# ShizukuService.java 逐行注释

> **导读位置**：第三轮（20 分钟）。只看构造方法和 `sendBinderToUserApp()`，目标是看懂「server 怎么启动 + binder 怎么批量分发」。
> **对照文件**：`~/projects/Shizuku-shallow/server/src/main/java/rikka/shizuku/server/ShizukuService.java`

---

## 阅读指引

| 方法 | 做什么 | 时间 |
|---|---|---|
| `main()`（第 61-68 行） | 进程入口，起 Looper，new ShizukuService | 2 min |
| 构造方法（第 92-128 行） | 等系统服务 ready → 注册 BinderSender → 批量发 binder | 10 min |
| `sendBinderToUserApp()`（第 511-579 行） | **和 ServiceStarter.sendBinder() 完全对称**的投递逻辑 | 8 min |

---

## main()：shizuku_server 进程的入口

```java
public static void main(String[] args) {
    DdmHandleAppName.setAppName("shizuku_server", 0);
    // ← 设进程名。在 `adb shell ps -A` 里你会看到 "shizuku_server" 这个名字。

    RishConfig.setLibraryPath(System.getProperty("shizuku.library.path"));

    Looper.prepareMainLooper();
    new ShizukuService();  // ← 构造方法里做所有的事（见下节）
    Looper.loop();         // ← 进入消息循环
}
```

---

## 构造方法：server 启动四件事

```java
public ShizukuService() {
    super();

    HandlerUtil.setMainHandler(mainHandler);

    LOGGER.i("starting server...");

    // === 第 1 件事：等系统服务 ready ===
    waitSystemService("package");
    waitSystemService(Context.ACTIVITY_SERVICE);
    waitSystemService(Context.USER_SERVICE);
    waitSystemService(Context.APP_OPS_SERVICE);
    // ← ShizukuService 需要调 PackageManager / ActivityManager / UserManager /
    //   AppOpsManager 这些系统服务，但它们可能在 system_server 还没启动完成。
    //   waitSystemService() 内部轮询 ServiceManager.getService(name)，
    //   返回 null 就 sleep(1000) 再试——简单粗暴但有效。
    //
    //   C++ 对照：相当于你等 hwservicemanager 里的 HAL service ready。

    // === 第 2 件事：确认 Manager App 已安装 ===
    ApplicationInfo ai = getManagerApplicationInfo();
    if (ai == null) {
        System.exit(ServerConstants.MANAGER_APP_NOT_FOUND);
        // ← Manager App 不存在 → 直接退出。Shizuku server 依赖 Manager App
        //   来接收和分发 binder，没有它整个架构就断了。
    }

    assert ai != null;
    managerAppId = ai.uid;
    // ← 记住 Manager App 的 uid。后续权限检查用这个 uid 判断调用方是不是 Manager。

    configManager = getConfigManager();
    clientManager = getClientManager();

    // === 第 3 件事：注册 BinderSender（核心！） ===
    ApkChangedObservers.start(ai.sourceDir, () -> { ... });

    BinderSender.register(this);
    // ← ★★★ 把 this（ShizukuService 自己）传给 BinderSender ★★★
    //   register() 做了两件事（详见 BinderSender-annotated.md）：
    //   1. 保存 shizukuService 引用
    //   2. 向 AMS 注册 ProcessObserver 和 UidObserver
    //       → 此后每当有 App 进程启动 / UID 状态变化
    //       → BinderSender 的 callback 被触发
    //       → BinderSender 自动调用 ShizukuService.sendBinderToUserApp()

    // === 第 4 件事：向现有 App 批量投递 binder ===
    mainHandler.post(() -> {
        sendBinderToClient();
        sendBinderToManager();
        // ← post() 把投递操作放到消息队列里，等当前构造方法执行完再跑。
        //   这样确保 BinderSender 的 Observer 已经注册好了再去发。
        //
        //   sendBinderToClient(): 遍历所有已安装的 App，
        //     找出声明了 PERMISSION 的那些，逐个调 sendBinderToUserApp()
        //   sendBinderToManager(): 发一份给 Manager App
    });
}
```

---

## sendBinderToUserApp()：和 ServiceStarter.sendBinder() 完全对称

```java
static void sendBinderToUserApp(Binder binder, String packageName, int userId, boolean retry) {
    // ← binder 参数：在这里就是 this（ShizukuService 自己，extends Binder）。
    //   packageName：目标 App 的包名。
    //   userId：目标 App 所在的用户（Android 多用户支持）。

    // --- 临时加到省电白名单 ---
    DeviceIdleControllerApis.addPowerSaveTempWhitelistApp(packageName, 30 * 1000, userId, ...);
    // ← 如果目标 App 在 Doze 模式，ContentProvider 调用可能被延迟。
    //   先加到省电白名单 30 秒，保证投递不会因为 Doze 被挡。

    String name = packageName + ".shizuku";
    // ← ContentProvider authority 名字。
    //   每个 Shizuku 授权的 App 都在 manifest 里注册了一个 ContentProvider，
    //   authority = "com.example.app.shizuku"。
    //
    //   注意：这和 ServiceStarter 那边的 authority 是同一个命名规则，
    //   但 target 不同——ServiceStarter 连的是 Manager App 的 provider，
    //   这里连的是目标 App 的 provider。

    IContentProvider provider = null;
    IBinder token = null;
    // ← 注意注释里的解释：不能用 this 当 token。
    //   因为 getContentProviderExternal 内部用 IBinder 做 HashMap 的 key，
    //   跨进程后 BinderProxy 的 hashCode() 默认走 Object.hashCode()（地址），
    //   导致 removeContentProviderExternal 永远对不上——这是个已知的 binder 跨进程坑。

    try {
        // --- 第 1 步：找到目标 App 的 ContentProvider ---
        provider = ActivityManagerApis.getContentProviderExternal(name, userId, token, name);
        // ← ★★★ 完全一样的 API ★★★
        //   ServiceStarter 用的也是 getContentProviderExternal，连参数都一样。
        //   区别只在于 authority 名字由 packageName 决定。
        //
        //   此时 provider 是目标 App 进程里的 ContentProvider 的 binder 代理。
        //   站在 ShizukuService（shell 进程）的角度，
        //   provider 指向目标 App 进程（uid 10xxx）。

        if (provider == null) {
            LOGGER.e("provider is null %s %d", name, userId);
            return;
        }
        if (!provider.asBinder().pingBinder()) {
            // ... retry logic (same pattern as ServiceStarter) ...
            return;
        }

        // --- 第 2 步：把 self 打包进 Bundle ---
        Bundle extra = new Bundle();
        extra.putParcelable("moe.shizuku.privileged.api.intent.extra.BINDER",
            new BinderContainer(binder));
        // ← 和 ServiceStarter 的打包方式完全一样。
        //   区别：ServiceStarter 包装的 binder 是 UserService.create() 返回的，
        //   这里包装的 binder 是 this（ShizukuService 自己）。
        //   但都是同一个对象——ShizukuService 的 IBinder 代理。
        //
        //   putParcelable → writeToParcel → writeStrongBinder(this)
        //   → kernel binder 驱动在目标进程创建 BinderProxy → 投递完成

        // --- 第 3 步：调 ContentProvider.call() 投递 ---
        Bundle reply = IContentProviderUtils.callCompat(provider, null, name, "sendBinder", null, extra);
        // ← ★★★ 对称性：注意 method 参数是 "sendBinder" ★★★
        //   ServiceStarter 那边传的是 "sendUserService"。
        //   不同 method → ContentProvider 收到后走不同的分支处理。
        //   但底层机制完全一样：Bundle 跨进程传 IBinder。
        //
        //   目标 App 的 ContentProvider.call("sendBinder", extras) 被触发 →
        //   从 extras 里取出 BinderContainer → 取出 binder → 存到全局变量里。
        //   至此 App 手里有了 ShizukuService 的 binder 代理。

        if (reply != null) {
            LOGGER.i("send binder to user app %s in user %d", packageName, userId);
        } else {
            LOGGER.w("failed to send binder to user app %s in user %d", packageName, userId);
        }
    } catch (Throwable tr) {
        LOGGER.e(tr, "failed send binder to user app %s in user %d", packageName, userId);
    } finally {
        // --- 第 4 步：断开 ContentProvider 连接 ---
        if (provider != null) {
            ActivityManagerApis.removeContentProviderExternal(name, token);
            // ← 对称性：ServiceStarter 最后也调了这个。
            //   用完就断，不保持长连接——binder 已经投出去了，不需要再占着 provider。
        }
    }
}
```

---

## 和 ServiceStarter 的对照表（记住这一张就够）

| | ServiceStarter.sendBinder() | ShizukuService.sendBinderToUserApp() |
|---|---|---|
| 谁在发 | ServiceStarter（shell 进程） | ShizukuService（也是 shell 进程，同一个） |
| 发给谁 | Manager App | 任意授权 App |
| 传的 binder | `UserService.create()` 新建的 binder | `this`（ShizukuService 自己） |
| CP authority | `moe.shizuku.privileged.api.shizuku` | `{目标包名}.shizuku` |
| CP method | `"sendUserService"` | `"sendBinder"` |
| 打包方式 | `BinderContainer` via `putParcelable` | **完全相同** |
| 清理 | `removeContentProviderExternal` | **完全相同** |

**学会标志**：能画一条线从 ServiceStarter.sendBinder() 连到 ShizukuService.sendBinderToUserApp()，说出三个「相同」和一个「不同」。