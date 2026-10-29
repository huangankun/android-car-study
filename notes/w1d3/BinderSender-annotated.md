# BinderSender.java 逐行注释

> **导读位置**：第四轮（15 分钟）。只看 `register()` 和 `sendBinder(uid,pid)`，目标是看懂「App 一启动，binder 怎么自动送上门」。
> **对照文件**：`~/projects/Shizuku-shallow/server/src/main/java/rikka/shizuku/server/BinderSender.java`

---

## 阅读指引

| 方法 | 做什么 | 时间 |
|---|---|---|
| `register()`（第 172-194 行） | 注册两个 Observer，绑定触发源头 | 5 min |
| `ProcessObserver` callbacks（第 42-79 行） | 监听"App 进程的前台/状态变化" | 3 min |
| `UidObserver` callbacks（第 83-139 行） | 监听"UID 从缓存态变活跃" | 3 min |
| `sendBinder(uid,pid)`（第 141-170 行） | 两个 Observer 的汇合点：查权限 → 投递 | 4 min |

---

## 总览：BinderSender 在整条链路里的位置

```
BinderSender.register(this)  ← ShizukuService 构造方法里调

     ├──→ registerProcessObserver( new ProcessObserver() )
     │      └── AMS 会在每个 App 进程状态变化时回调
     │          onForegroundActivitiesChanged() → sendBinder(uid,pid)
     │          onProcessStateChanged()          → sendBinder(uid,pid)
     │
     └──→ registerUidObserver( new UidObserver() )
            └── AMS 会在每个 UID 状态变化时回调
                onUidActive()                 → sendBinder(uid,-1)
                onUidCachedChanged(cached=false) → sendBinder(uid,-1)

所有 callback 都落地到同一个方法：
                    ↓
         sendBinder(uid, pid)
            ├── getPackagesForUidNoThrow(uid)
            ├── 检查每个包的权限
            └── ShizukuService.sendBinderToUserApp()  或  sendBinderToManger()
```

**一句话**：BinderSender 是一个「时机探测器」——它不持有 binder，不传 binder，只负责判断「什么时候该触发投递」。真正的投递动作委托给 ShizukuService。

---

## register()：绑定两个触发器

```java
public static void register(ShizukuService shizukuService) {
    sShizukuService = shizukuService;
    // ← 保存 ShizukuService 的引用。
    //   后面 sendBinder() 会通过 sShizukuService 调用它的投递方法。

    // === 触发器 1：ProcessObserver ===
    try {
        ActivityManagerApis.registerProcessObserver(new ProcessObserver());
        // ← 向 AMS（系统进程）注册一个进程观察者。
        //   参数是 ProcessObserverAdapter 的实例——它实现了
        //   android.app.IProcessObserver 这个 AIDL 接口。
        //
        //   注册后，AMS 会在以下时机回调你的方法：
        //   - 任何 App 进程进入/退出前台
        //   - 任何 App 进程状态变化（活跃→缓存→死亡）
        //
        //   C++ 对照：相当于你注册了一个 CarWatchdog 的 callback，
        //   但这里的 observer 是跨进程 binder 回调。
    } catch (Throwable tr) {
        LOGGER.e(tr, "registerProcessObserver");
    }

    // === 触发器 2：UidObserver（Android 8.0+ 可用） ===
    if (Build.VERSION.SDK_INT >= 26) {
        int flags = UID_OBSERVER_GONE    // uid 消失
                  | UID_OBSERVER_IDLE    // uid 进入空闲
                  | UID_OBSERVER_ACTIVE; // uid 变为活跃
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            flags |= UID_OBSERVER_CACHED; // uid 进入/离开缓存态
        }
        try {
            ActivityManagerApis.registerUidObserver(
                new UidObserver(), flags,
                ActivityManagerHidden.PROCESS_STATE_UNKNOWN,
                null);
            // ← UidObserver 比 ProcessObserver 更低级别。
            //   ProcessObserver 关心"进程"，UidObserver 关心"UID"。
            //
            //   一个 UID 可能对应多个进程（同一 App 的多进程），
            //   或者 UID 处于活跃状态但进程还没完全启动。
            //   UidObserver 的粒度更粗，但覆盖更全——保证 binder 不会漏投。
        } catch (Throwable tr) {
            LOGGER.e(tr, "registerUidObserver");
        }
    }
}
```

---

## 触发器 1：ProcessObserver ——「App 进程状态变了」

```java
private static class ProcessObserver extends ProcessObserverAdapter {

    private static final List<Integer> PID_LIST = new ArrayList<>();
    // ← 记录「已经发过 binder 的 PID」。
    //   同一个 PID 只发一次，避免重复投递。

    @Override
    public void onForegroundActivitiesChanged(int pid, int uid, boolean foreground) {
        // ← App 进入或退出前台时触发。
        //   比如：用户点了 Launcher 上的图标 → App 启动 → 这一行被回调。

        synchronized (PID_LIST) {
            if (PID_LIST.contains(pid) || !foreground) {
                return;
                // ← 已经发过的跳过；退到后台也跳过（只在进前台时发）。
            }
            PID_LIST.add(pid);
        }

        sendBinder(uid, pid);
        // ← ★★★ 触发器生效：App 进前台 → 自动发 binder ★★★
    }

    @Override
    public void onProcessStateChanged(int pid, int uid, int procState) {
        // ← App 进程状态变化时触发（比 onForegroundActivitiesChanged 更宽）。
        //   例如：从 IMPORTANT_FOREGROUND 变成 IMPORTANT_BACKGROUND。

        synchronized (PID_LIST) {
            if (PID_LIST.contains(pid)) {
                return;
            }
            PID_LIST.add(pid);
        }

        sendBinder(uid, pid);
        // ← ★★★ 触发：进程状态变化 → 自动发 binder ★★★
    }

    @Override
    public void onProcessDied(int pid, int uid) {
        // ← App 进程死了。从 PID_LIST 里移除以释放内存。
        synchronized (PID_LIST) {
            int index = PID_LIST.indexOf(pid);
            if (index != -1) {
                PID_LIST.remove(index);
            }
        }
    }
}
```

---

## 触发器 2：UidObserver ——「UID 状态变了」

```java
private static class UidObserver extends UidObserverAdapter {

    private static final List<Integer> UID_LIST = new ArrayList<>();
    // ← 记录「已经发过 binder 的 UID」。
    //   同一 UID 只发一次。

    @Override
    public void onUidActive(int uid) {
        // ← UID 变为活跃状态。
        //   触发时机：App 进程从 cached/idle 变成 active。
        LOGGER.d("onUidCachedChanged: uid=%d", uid);
        uidStarts(uid);
    }

    @Override
    public void onUidCachedChanged(int uid, boolean cached) {
        // ← UID 进入/离开缓存态。
        LOGGER.d("onUidCachedChanged: uid=%d, cached=%s", uid, ...);
        if (!cached) {
            uidStarts(uid);
            // ← 离开缓存态 = App 又活过来了 → 发 binder
        }
    }

    @Override
    public void onUidIdle(int uid, boolean disabled) {
        uidStarts(uid);
        // ← UID 从 idle 变成 active（也可能是 disabled）→ 发 binder
    }

    @Override
    public void onUidGone(int uid, boolean disabled) {
        uidGone(uid);
        // ← UID 彻底消失了 → 从 UID_LIST 清理
    }

    private void uidStarts(int uid) {
        synchronized (UID_LIST) {
            if (UID_LIST.contains(uid)) {
                return;  // ← 已经发过了，跳过
            }
            UID_LIST.add(uid);
        }

        try {
            sendBinder(uid, -1);
            // ← ★★★ pid = -1 表示"不确定具体进程，只知道 UID 活了" ★★★
            //   sendBinder() 内部会通过 getPackagesForUidNoThrow(uid)
            //   查到该 UID 对应的所有包，遍历投递。
        } catch (RemoteException e) { ... }
    }

    private void uidGone(int uid) {
        synchronized (UID_LIST) {
            UID_LIST.remove(Integer.valueOf(uid));
        }
    }
}
```

---

## sendBinder(uid,pid)：两个触发器的汇合点

```java
private static void sendBinder(int uid, int pid) throws RemoteException {
    // ← 此方法被 ProcessObserver 和 UidObserver 的所有 callback 调用。
    //   pid = 具体进程 PID（从 ProcessObserver 来）
    //   pid = -1（从 UidObserver 来，不确定具体进程）

    // --- 第 1 步：查这个 UID 对应哪（几）个包 ---
    List<String> packages = PackageManagerApis.getPackagesForUidNoThrow(uid);
    if (packages.isEmpty())
        return;

    LOGGER.d("sendBinder to uid %d: packages=%s", uid, TextUtils.join(", ", packages));

    int userId = uid / 100000;
    // ← Android 的 userId 计算方式：userId = uid / 100000。
    //   uid = 0 → userId 0（root）
    //   uid = 1000 → userId 0（system）
    //   uid = 2000 → userId 0（shell）
    //   uid = 10128 → userId 0（app, userId=0 表示机主用户）
    //   uid = 10xxx → userId 1（工作资料用户）

    // --- 第 2 步：遍历每个包，检查权限 ---
    for (String packageName : packages) {
        PackageInfo pi = PackageManagerApis.getPackageInfoNoThrow(
            packageName, PackageManager.GET_PERMISSIONS, userId);
        if (pi == null || pi.requestedPermissions == null)
            continue;

        if (ArraysKt.contains(pi.requestedPermissions, PERMISSION_MANAGER)) {
            // ← 这个包声明了 PERMISSION_MANAGER = "moe.shizuku.manager.permission.MANAGER"
            //   说明它是 Manager App 本身。给 Manager 发 binder。

            boolean granted;
            if (pid == -1)
                granted = PermissionManagerApis.checkPermission(
                    PERMISSION_MANAGER, uid) == PERMISSION_GRANTED;
            else
                granted = ActivityManagerApis.checkPermission(
                    PERMISSION_MANAGER, pid, uid) == PERMISSION_GRANTED;
            // ← 权限检查：Manager App 必须先有 PERMISSION_MANAGER 权限。
            //   pid == -1 时用 checkPermission(uid)（查 UID 级别的权限），
            //   pid 已知时用 checkPermission(pid,uid)（查 PID 级别的权限，更精确）。

            if (granted) {
                ShizukuService.sendBinderToManger(sShizukuService, userId);
                // ← ★★★ 调 ShizukuService 的静态方法投递 ★★★
                //   走到 ShizukuService.sendBinderToUserApp() 同一套逻辑。
                return;
            }

        } else if (ArraysKt.contains(pi.requestedPermissions, PERMISSION)) {
            // ← 这个包声明了 PERMISSION = "moe.shizuku.manager.permission.API_V23"
            //   说明它是一个授权使用 Shizuku 的普通 App。

            ShizukuService.sendBinderToUserApp(sShizukuService, packageName, userId);
            // ← ★★★ 调同一个投递方法 ★★★
            //   ShizukuService.sendBinderToUserApp() 就是刚才第三轮读的那个方法。
            return;
        }
        // ← 如果包既不声明 PERMISSION_MANAGER 也不声明 PERMISSION，
        //   说明它跟 Shizuku 没关系——跳过，不发 binder。
    }
}
```

---

## 汇总：BinderSender 不做的事

BinderSender **不**做这些：
- ❌ 创建 binder
- ❌ 管理权限（只管检查）
- ❌ 建立长连接
- ❌ 存 binder 引用

BinderSender **只**做一件事：**检测「目标 App 现在活着/刚活过来」→ 触发投递**。

真正的投递逻辑全在 `ShizukuService.sendBinderToUserApp()` 里。BinderSender 是「触发器」，ShizukuService 是「执行器」。

**学会标志**：能画出从「App 启动」到「拿到 binder」的完整时序——AMS 回调 Observer → sendBinder(uid,pid) → 查权限 → ShizukuService.sendBinderToUserApp() → ContentProvider.call() → App 收到。