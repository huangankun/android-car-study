# W1D3 · Shizuku 导读 Stepper 文档（✅ 完成）

> 任务：按附录 A 顺序读 Shizuku 源码四个文件，画出「shell 权限如何进入特权进程 → binder 如何递交给普通 App」的架构图。
> 执行人：Hermes（导师）｜学习者：先生（文档 + 自测）
> 最终状态：✅ 四文件精读完成、架构图锁定、源码层级关系理解了

## 任务卡

- **目标**：读懂 Shizuku 的完整架构链路——`adb shell → ServiceStarter → ShizukuService → BinderSender → 普通 App`。核心产出是一张能讲清的架构图。
- **为什么做**：Shizuku 是理解「非 root 环境下 App 获取系统级权限」的**最小可运行案例**。它的核心 trick（binder 跨进程传递）不是 Shizuku 独家——CarService 给 App 发 binder、SystemServer 的各种 Manager 都是同一个模式。吃透这条链路，W2 读 CarService 黄金链路时「binder 每一段角色」就全通了。
- **今天进度**：精读四个文件 + 架构图 + 自测 3 题。深读三处（ShizukuService / BinderSender / UserServiceManager）留给 W1D4。
- **知识点清单**（自测出题源）：
  1. Shizuku 架构链五个角色：`adb shell` → `start.sh` → `ServiceStarter` → `ShizukuService` → `BinderSender` + ContentProvider → App
  2. Android UID 权限模型：shell(2000) / system(1000) / app(10000+) 各自能做什么
  3. `ContentProvider.call()`：不是存数据，而是**传 binder 对象**——这是 Shizuku 选的路
  4. BinderSender 的两个 observer：`ProcessObserver`（等 app 进程启动）和 `UidObserver`（等 uid 状态变化），做同一件事——**时机一到就投递 binder**
  5. `sendBinderToUserApp()` 和 ServiceStarter 的 `sendBinder()` 是对称的：一个从 starter 投给 manager，一个从 server 投给所有授权 app

## 架构图：Binder 的两次跨进程投递

```
                    ① 第一次投递（starter → manager）
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                 │
   │  adb shell start.sh                                             │
   │     │  (uid=2000, shell 权限)                                    │
   │     │  app_process -cp Shizuku.apk ServiceStarter                │
   │     ▼                                                           │
   │  ┌─────────────────────────┐                                    │
   │  │    ServiceStarter       │ main() → UserService.create(args)  │
   │  │                         │              ↓                     │
   │  │  created binder for     │ sendBinder(service, token)         │
   │  │  ShizukuService         │   → getContentProviderExternal(    │
   │  │                         │       "moe.shizuku.privileged      │
   │  │                         │        .api.shizuku")              │
   │  │                         │   → provider.call("sendUserService"│
   │  │                         │       , extra={binder})            │
   │  └────────┬────────────────┘                                    │
   │           │  binder 包裹在 Bundle → PendingIntent 类似的模式     │
   │           ▼                                                     │
   │  ┌─────────────────────────┐                                    │
   │  │  Manager App            │ ← 拿到 binder，知道 server 活了     │
   │  │  (moe.shizuku.          │                                    │
   │  │   privileged.api)       │                                    │
   │  └────────┬────────────────┘                                    │
   │           │                                                     │
   └───────────┼─────────────────────────────────────────────────────┘
               │
               │  ② 第二次投递（server → 所有授权 app）
               │     由 BinderSender 驱动的自动投递
               ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                 │
   │  ┌──────────────────────────┐                                   │
   │  │  ShizukuService (server) │ main() → new ShizukuService()     │
   │  │                           │           ↓                      │
   │  │  uid = shell(2000)       │ waitSystemService("package") etc  │
   │  │  持有系统服务 binder      │ BinderSender.register(this)       │
   │  │  能调 hidden API         │   → registerProcessObserver()     │
   │  └──────────┬───────────────┘   → registerUidObserver()         │
   │             │                   sendBinderToClient()             │
   │             │                   遍历所有请求了 PERMISSION 的 app │
   │             │                   逐个 sendBinderToUserApp()       │
   │             │                                                   │
   │             │  ┌──────────────────┐                             │
   │             │  │   BinderSender   │                             │
   │             │  │                  │                             │
   │             │  │ ProcessObserver  │ ← 监到 app 进程启动          │
   │             │  │   onForeground-  │    onProcessStateChanged()  │
   │             │  │   Activities-    │    → sendBinder(uid, pid)   │
   │             │  │   Changed()      │                             │
   │             │  │                  │                             │
   │             │  │ UidObserver      │ ← 监到 uid 状态变化          │
   │             │  │   onUidActive()  │    uid 从 cached → active   │
   │             │  │   onUidCached-   │    → sendBinder(uid, -1)    │
   │             │  │   Changed(false) │                             │
   │             │  └──────────────────┘                             │
   │             │         │ 时机一到 → sendBinder(uid, pid)          │
   │             │         │   → ShizukuService.sendBinderToUserApp()│
   │             │         ▼                                         │
   │             │  ┌──────────────────────────────────────┐         │
   │             │  │  ContentProvider.call("sendBinder")  │         │
   │             │  │  extra = BinderContainer(binder)     │         │
   │             │  └──────────────────────────────────────┘         │
   │             │         │                                         │
   │             ▼         ▼                                         │
   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
   │  │   App A          │  │   App B          │  │   App C ...      │ │
   │  │ uid=10xxx        │  │ uid=10yyy        │  │                  │ │
   │  │ 拿到 binder 后： │  │                  │  │                  │ │
   │  │ 调 ShizukuService│  │                  │  │                  │ │
   │  │ .transactRemote()│  │                  │  │                  │ │
   │  │ → 系统 API 以更  │  │                  │  │                  │ │
   │  │   高权限执行      │  │                  │  │                  │ │
   │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
   └─────────────────────────────────────────────────────────────────┘
```

## 执行步骤

### S1 · 克隆 Shizuku 源码 ✅

```bash
git clone --depth 1 git@github.com:RikkaApps/Shizuku.git ~/projects/Shizuku-shallow
# commit: b844bc4 "Clarify license"
```

**讲解**：网络和你 W1D1 遇到的一样，SSH 连接偏慢但最终成功（使用 `--depth 1` 浅克隆减少传输量）。四个目标文件的位置：

| 文件 | 路径 |
|---|---|
| README | `./README.md` |
| ServiceStarter | `./starter/src/main/java/moe/shizuku/starter/ServiceStarter.java` |
| ShizukuService | `./server/src/main/java/rikka/shizuku/server/ShizukuService.java` |
| BinderSender | `./server/src/main/java/rikka/shizuku/server/BinderSender.java` |

### S2 · 读 README：架构顶层设计 ✅

Shizuku 解决的核心问题：**不让 App 直接拿 root，但让 App 能用系统级 API**。

传统做法：`Runtime.exec("su")` 起一个 root shell 发命令 → **慢、不可靠、只有命令行的权限**。
Shizuku 做法：起一个**独立进程（Shizuku server）**跑在 shell/root 权限下，持有系统服务 binder；然后在 App 启动时，把这个 server 的 binder **递送给 App**。App 拿到 binder 后，就像手里有一个系统服务的代理，可以直接调 `transactRemote()`。

**一句话**：Shizuku 是一个「binder 传递中间人」——server 有特权、App 有 server 的 binder、App 通过 server 间接调用系统 API。

### S3 · 读 ServiceStarter：入口 ——「shell 权限怎么进来」 ✅

这是起点。`ServiceStarter.main()` 被 `start.sh` 里的 `app_process` 启动（不是普通 dalvikvm，是 `app_process`——Android 官方进程启动器）。

核心逻辑（`main()` 方法）：

```java
// ① 创建 ShizukuService 的 binder
Pair<IBinder, String> result = UserService.create(args);

// ② 通过 ContentProvider 把 binder 传给 Manager App
if (!sendBinder(service, token)) {
    System.exit(1);
}
```

`sendBinder()` 做了什么（第 94-161 行）：

```java
// 找到 Manager App 注册的 ContentProvider
provider = ActivityManagerApis.getContentProviderExternal(
    "moe.shizuku.privileged.api.shizuku", userId, null, name);

// 把 binder 装进 Bundle
extra.putParcelable(EXTRA_BINDER, new BinderContainer(binder));

// 调 ContentProvider.call("sendUserService", extra)
// → 这一步完成跨进程：binder 从 shell 进程传到了 Manager App 进程
Bundle reply = IContentProviderCompat.call(provider, ..., "sendUserService", ..., extra);
```

**关键点**：`ContentProvider.call()` 是一个可以传任意 `Bundle` 的 IPC 通道。ServiceStarter 用它传了 `BinderContainer`（包裹了 ShizukuService 的 IBinder）。Manager App 的 ContentProvider 收到后，取出 binder，存下来——这就是「接收端」。

### S4 · 读 ShizukuService：特权服务本体 ✅

`ShizukuService.main()` 在 `shizuku_server` 进程中运行（和 ServiceStarter 是同一个进程，但 ServiceStarter 创建完 binder 就退出了，ShizukuService 接管）。

构造逻辑（第 92-128 行）：

```java
public ShizukuService() {
    // ① 等系统服务 ready
    waitSystemService("package");
    waitSystemService(Context.ACTIVITY_SERVICE);

    // ② 确认 Manager App 已安装
    ApplicationInfo ai = getManagerApplicationInfo();

    // ③ 注册 Observer —— 核心：让 binder 在 app 启动时自动投递
    BinderSender.register(this);

    // ④ 向已安装的所有授权 app 发送 binder
    mainHandler.post(() -> {
        sendBinderToClient();      // 遍历所有请求了 PERMISSION 的 app
        sendBinderToManager();     // 发给 Manager
    });
}
```

`sendBinderToUserApp()`（第 511-579 行）：

```java
// 找到目标 app 的 ContentProvider
provider = ActivityManagerApis.getContentProviderExternal(
    packageName + ".shizuku", userId, token, name);

// 把自身(this)的 binder 装进 BinderContainer，通过 Bundle 传给 app
extra.putParcelable("moe.shizuku.privileged.api.intent.extra.BINDER",
    new BinderContainer(binder));

// 调 ContentProvider.call("sendBinder")
IContentProviderUtils.callCompat(provider, ..., "sendBinder", null, extra);
```

**注意对称性**：ServiceStarter 的 `sendBinder()` 传的是 ShizukuService binder → Manager App。ShizukuService 的 `sendBinderToUserApp()` 传的是**自身 this** → 所有授权 App。两次投递都走 ContentProvider.call()，只是方向不同：「先给 manager、再从 manager 反推给全部 app」。

### S5 · 读 BinderSender：核心 trick ——「时机一到就投递」 ✅

这是 Shizuku 最精妙的地方。`BinderSender.register()` 挂了两个系统级的 Observer，监听 App 进程的启动和 UID 状态变化：

```java
public static void register(ShizukuService shizukuService) {
    sShizukuService = shizukuService;

    // ① ProcessObserver：监听到 app 进程启动
    ActivityManagerApis.registerProcessObserver(new ProcessObserver());

    // ② UidObserver：监听到 uid 从 cached → active 或 idle → active
    ActivityManagerApis.registerUidObserver(new UidObserver(), flags, ...);
}
```

**ProcessObserver**（第 37-80 行）：
- `onForegroundActivitiesChanged(pid, uid, foregroundActivities=true)` → `sendBinder(uid, pid)`
- `onProcessStateChanged(pid, uid, procState)` → `sendBinder(uid, pid)`
- 一旦 app 进程进入前台或状态变化，立刻投递 binder

**UidObserver**（第 83-139 行）：
- `onUidActive(uid)` → `sendBinder(uid, -1)`
- `onUidCachedChanged(uid, cached=false)` → `sendBinder(uid, -1)`（uid 从缓存态出来）
- `onUidIdle(uid)` → `sendBinder(uid, -1)`
- `onUidGone(uid)` → 清理 uid 列表
- 比 ProcessObserver 更低级别：只要 UID 激活了，即使进程还没启动也投递

**sendBinder(uid, pid)**（第 141-170 行）——两个 observer 都落地到同一个方法：

```java
// ① 拿到 uid 对应的包名
packages = PackageManagerApis.getPackagesForUidNoThrow(uid);

// ② 检查每个包的权限
for (packageName : packages) {
    if (pi.requestedPermissions contains PERMISSION_MANAGER) {
        ShizukuService.sendBinderToManger(sShizukuService, userId);
    } else if (pi.requestedPermissions contains PERMISSION) {
        ShizukuService.sendBinderToUserApp(sShizukuService, packageName, userId);
    }
}
```

**这就是 Shizuku 的「自动化」**：你不需要手动启动什么——App 进程一启动，BinderSender 自动检测到，自动检查权限，自动投递 binder。整个过程对 App 几乎透明。

## 问题日志

| # | 症状 | 原因 | 解法 |
|---|---|---|---|
| P1 | SSH clone 超时 | SSH 连接 github.com:22 在当前网络下延迟高 | 换 `--depth 1` 浅克隆减少传输量，成功 |
| P2 | `gh repo clone` 也超时 | gh 底层也用 SSH（`git_protocol=ssh`），同一个瓶颈 | 同样走浅克隆；700KB 的源码不需要深度历史 |

## 面试高频命令（你今天不敲命令，但明天这些会用到）

```bash
# 查看正在运行的 Shizuku 进程
adb shell ps -A | grep shizuku
# 通过 ContentProvider 直接取 binder（等效于 ServiceStarter 干的事——W1D5 会用到）
adb shell content call --uri content://moe.shizuku.privileged.api.shizuku --method sendBinder
```

## 自测（3 题，做完喊我，我们对答案）

1. ServiceStarter 的 `sendBinder()` 把 binder 传到 Manager App 时，走了什么方法？binder 被包装在什么对象里？为什么这条路比 `bindService` 更适合 Shizuku？
2. BinderSender 挂了哪两个系统 Observer？各监听了什么事件？监听结果最终汇合到哪个方法？
3. `ShizukuService.sendBinderToUserApp()` 里调 `ContentProvider.call()` 的 method 参数叫什么？和 ServiceStarter 那边传的 method 参数是同一个值吗？如果不是，区别在哪？

---

*本文件由导师会话生成，归档至 `~/projects/android-car-study/notes/`；Shizuku 源码在 `~/projects/Shizuku-shallow/`*