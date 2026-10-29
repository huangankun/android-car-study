# ServiceStarter.java 逐行注释

> **导读位置**：第二轮（20 分钟）。只追 `main()` 和 `sendBinder()` 两个方法，目标是看懂「binder 怎么出生、怎么被扔出去」。
> **对照文件**：`~/projects/Shizuku-shallow/starter/src/main/java/moe/shizuku/starter/ServiceStarter.java`

---

## 阅读指引

只读这两个方法，跳过其余：

| 方法 | 做什么 | 时间 |
|---|---|---|
| `main()`（第 61-88 行） | 创建 ShizukuService binder → 调 sendBinder 投递给 Manager App | 5 min |
| `sendBinder()`（第 94-161 行） | 通过 ContentProvider.call() 跨进程传 binder 的核心逻辑 | 15 min |

---

## main()：binder 的诞生地

```java
public static void main(String[] args) {
    // ← main() 被 app_process 调用，不是普通 JVM。
    //   这个进程跑在 shell(uid=2000) 身份下，有系统级权限。

    if (Looper.getMainLooper() == null) {
        Looper.prepareMainLooper();
        // ← Android 的 Looper 机制：每个线程需要一个消息循环才能收 IPC 回调。
        //   C++ 背景对照：这相当于你熟悉的 EventLoop / RunLoop。
    }

    IBinder service;
    String token;

    UserService.setTag(TAG);
    Pair<IBinder, String> result = UserService.create(args);
    // ← ★★★ 第 一 个 关 键 点 ★★★
    //   UserService.create() 内部创建了 ShizukuService 的 binder 对象。
    //   service = 指向 ShizukuService 的 IBinder 代理。
    //   token   = 后续用于验证身份的一次性口令。
    //
    //   C++ 对照：相当于拿到了 BpShizukuService 的 sp<IShizukuService>。
    //   区别是你不需要手写 BpXXX/BnXXX——Java 层的 AIDL 自动生成。

    if (result == null) {
        System.exit(1);
        return;
    }

    service = result.first;
    token = result.second;

    if (!sendBinder(service, token)) {
        // ← ★★★ 第 二 个 关 键 点 ★★★
        //   把刚刚出生的 binder 投递给 Manager App。
        //   投递成功 → 进入 Looper.loop() 等消息。
        //   投递失败 → System.exit(1) 自尽。
        System.exit(1);
    }

    Looper.loop();   // ← 进入消息循环，线程不再退出
    System.exit(0);

    Log.i(TAG, "service exited");
}
```

---

## sendBinder()：binder 如何跨进程旅行（15 分钟，全部含金量）

```java
private static boolean sendBinder(IBinder binder, String token, boolean retry) {
    // ← binder 参数：就是 main() 里通过 UserService.create() 拿到的
    //   ShizukuService 的 IBinder 代理。

    String packageName = "moe.shizuku.privileged.api";
    // ← Manager App 的包名。Shizuku 的设计里，Manager App 是 binder
    //   的"第一站接收者"——ServiceStarter 先把 binder 给它，它再分发给其他 App。

    String name = packageName + ".shizuku";
    // ← ContentProvider 的 authority 名字。
    //   Manager App 在 manifest 里注册了一个 authority 为
    //   "moe.shizuku.privileged.api.shizuku" 的 ContentProvider。
    //
    //   C++ 对照：authority 相当于你在 HIDL service 里注册的
    //   "vendor.xxx.IXxxService/default" 这种实例名。

    int userId = 0;
    IContentProvider provider = null;

    try {
        // --- 第 1 步：找到 Manager App 的 ContentProvider ---
        provider = ActivityManagerApis.getContentProviderExternal(name, userId, null, name);
        // ← ★★★ 核心 API ★★★
        //   getContentProviderExternal() 是 @hide 的 AMS 方法。
        //   作用：告诉 ActivityManagerService "我要连这个 authority 的 ContentProvider"，
        //   AMS 找到 Manager App 进程里的那个 Provider，返回一个 IContentProvider 代理给你。
        //
        //   此刻 provider 是 Manager App 进程里那个 Provider 的 binder 代理。
        //   你（shell 进程）通过这个代理可以直接调 Manager App 的 Provider 方法。
        //
        //   面试点："ContentProvider 跨进程是怎么连上的？"
        //   答案：调用方通过 AMS.getContentProvider → AMS 找到目标进程的 Provider
        //   → 返回 IContentProvider 的 binder 代理。

        if (provider == null) {
            Log.e(TAG, String.format("provider is null %s %d", name, userId));
            return false;
        }
        if (!provider.asBinder().pingBinder()) {
            // ← pingBinder() 是 IBinder 的探活方法。
            //   如果对方进程已经死了，ping 返回 false。
            Log.e(TAG, String.format("provider is dead %s %d", name, userId));
            // ... retry logic (kill & restart Manager App) ...
            return false;
        }

        // --- 第 2 步：把 binder 打包进 Bundle ---
        Bundle extra = new Bundle();
        extra.putParcelable(EXTRA_BINDER, new BinderContainer(binder));
        // ← ★★★ 核心 trick ★★★
        //   BinderContainer 是一个实现 Parcelable 的包装类。
        //   putParcelable() 会调用 BinderContainer.writeToParcel(parcel, flags)，
        //   其中 parcel.writeStrongBinder(binder) 把 IBinder 序列化进 Parcel。
        //
        //   writeStrongBinder() 是 binder 跨进程传递的核心：
        //   → kernel binder 驱动在接收端创建新的 BinderProxy 对象
        //   → 指向同一个 binder 实体（ShizukuService 自己）
        //   → 跨进程传参完成
        //
        //   C++ 对照：IPCThreadState::writeStrongBinder()，完全同一个内核机制。

        extra.putString(ShizukuApiConstants.USER_SERVICE_ARG_TOKEN, token);
        // ← token 跟在后面，Manager App 收到后用 token 验证这次投递是否合法。

        // --- 第 3 步：调 ContentProvider.call()，完成跨进程投递 ---
        Bundle reply = IContentProviderCompat.call(provider, null, null, name, "sendUserService", null, extra);
        // ← ★★★ 投递动作本身 ★★★
        //   provider.call(method="sendUserService", arg=null, extras={binder,token})
        //
        //   这一行执行后：
        //   → Manager App 进程里的 ShizukuApiProvider.call() 被触发
        //   → 从 extras 里解出 BinderContainer → 取出 binder → 存下来
        //   → Manager App 现在持有 ShizukuService 的 binder 代理
        //
        //   为什么用 ContentProvider.call() 而不是 bindService？
        //   → bindService 需要 App 侧主动 bind（要写 ServiceConnection 回调）
        //   → call() 是单向推送：server 随时可以往 App 塞东西
        //   → call() 传的是 Bundle，可以携带任意 Parcelable（包括 IBinder）

        if (reply != null) {
            reply.setClassLoader(BinderContainer.class.getClassLoader());

            Log.i(TAG, String.format("send binder to %s in user %d", packageName, userId));
            BinderContainer container = reply.getParcelable(EXTRA_BINDER);
            // ← Manager App 的回执：它把 ShizukuService 的 binder 又传回来了
            //   （这是为了确认投递成功 + 拿到最终版的 binder 引用）

            if (container != null && container.binder != null && container.binder.pingBinder()) {
                shizukuBinder = container.binder;
                // ← ServiceStarter 自己也持有一份 ShizukuService 的 binder 引用。
                //   这行保存引用，防止被 GC 回收后 DeathRecipient 失效。

                shizukuBinder.linkToDeath(() -> {
                    // ← DeathRecipient：server 死了这里会收到通知。
                    //   C++ 对照：BpBinder::linkToDeath()，完全同一个内核机制。
                    Log.i(TAG, "exiting...");
                    System.exit(0);
                }, 0);
                return true;  // ← 投递成功！
            } else {
                Log.w(TAG, "server binder not received");
            }
        }

        return false;
    } catch (Throwable tr) {
        Log.e(TAG, ...);
        return false;
    } finally {
        if (provider != null) {
            // --- 第 4 步：断开 ContentProvider 连接 ---
            ActivityManagerApis.removeContentProviderExternal(name, null);
            // ← 用完就断开。这是 AMS 管理 ContentProvider 连接的标准做法。
            //   不清理的话 AMS 会一直维持这个连接。
        }
    }
}
```

---

## 这个文件的位置：在整条链路的最前端

```
adb shell start.sh
  → app_process ServiceStarter  ← 你在这里
      → main() 创建 ShizukuService binder
      → sendBinder() 把 binder 扔给 Manager App
      → Looper.loop() 进入等待（等 ShizukuService 被 kill）
```

**学会标志**：能讲清 `sendBinder()` 里四个步骤：getContentProvider → putParcelable → call → removeContentProvider，每一步在做什么、为什么必不可少。