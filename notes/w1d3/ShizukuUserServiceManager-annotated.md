# ShizukuUserServiceManager.java 逐行注释

> **导读位置**：W1D4 第三处深读。目标是理解「UserService 机制」——Shizuku 怎么在 App 自己进程里跑一个带特权的服务。
> **对照文件**：`~/projects/Shizuku-shallow/server/src/main/java/rikka/shizuku/server/ShizukuUserServiceManager.java`

---

## UserService 是什么（先读这段，再看代码）

回顾 W1D3 的架构图：App 拿到 ShizukuService 的 binder 后，通过它间接调系统 API。这是「App → ShizukuService → 系统 API」的模式。

**UserService 是反过来的**：Shizuku 在 **App 自己的进程里** 起一个新服务，这个服务有 Shizuku 的 binder 权限，但它跑在 App 的进程空间里——App 可以直接访问它的内存和方法，同时又享有 Shizuku 的权限。

```
                 ┌──── App 进程 ─────┐
                 │                    │
                 │  App 自己的代码     │
                 │       ↕ 同进程调用  │
                 │  UserService       │ ← 拿着 Shizuku 的 binder
                 │       ↕              │    可以调 transactRemote()
                 │  ServiceStarter    │ ← 复用 W1D3 那条投递链
                 │                    │
                 └────┬───────────────┘
                      │ ContentProvider.call()
                      ↓
            ┌──────────────────┐
            │  ShizukuService  │  (shizuku_server 进程, shell uid)
            └──────────────────┘
```

**使用场景**：一个 App 想写一个后台 Service 来监听系统事件（比如 `IActivityManager.registerProcessObserver`），但这个监听需要系统级权限。App 自己没权限——但它可以让 Shizuku 在它的进程里起一个 UserService，这个 UserService 持有 Shizuku 的 binder，可以用它来调系统 API。

---

## 逐段讲解

### 1. 类结构与角色

```java
public class ShizukuUserServiceManager extends UserServiceManager {
    // ← UserServiceManager 是父类（在 shizuku-shared 或 api 模块中），
    //   定义了 UserService 的标准生命周期：创建 / 移除 / 启动命令。
    //   ShizukuUserServiceManager 是 Shizuku server 侧的实现。

    private final Map<UserServiceRecord, ApkChangedListener> apkChangedListeners = new ArrayMap<>();
    // ← 记录 → 监听器映射。每个 UserService 对应一个 APK 变更监听器。
    //   当 APK 被更新或卸载时，对应的 UserService 需要被清理或重新创建。

    private final Map<String, List<UserServiceRecord>> userServiceRecords = Collections.synchronizedMap(new ArrayMap<>());
    // ← 包名 → UserServiceRecord 列表。用于按包名查找该 App 创建了哪些 UserService。
```

### 2. getUserServiceStartCmd()：生成 ServiceStarter 的命令行

```java
@Override
public String getUserServiceStartCmd(
        UserServiceRecord record, String key, String token, String packageName,
        String classname, String processNameSuffix, int callingUid,
        boolean use32Bits, boolean debug) {
    // ← 当 Shizuku 决定启动一个 UserService 时，调用这个方法获取命令行。
    //
    //   record：UserService 的记录对象（含 uid/pid/token 等）
    //   classname：App 定义的 UserService 类全名（如 "com.example.MyUserService"）
    //   processNameSuffix：进程名后缀（如 ":shizuku"）——
    //     注意！！！UserService 跑在 App 的 processName + suffix 进程里，
    //     不是 shizuku_server 进程。它复用 app_process 创建新进程，
    //     cp 了 App 的 CLASSPATH。
    //   callingUid：发起请求的 App 的 UID

    String appProcess = "/system/bin/app_process";
    if (use32Bits && new File("/system/bin/app_process32").exists()) {
        appProcess = "/system/bin/app_process32";
        // ← 32 位兼容。某些老旧设备需要 app_process32。
    }

    return ServiceStarter.commandForUserService(
            appProcess,
            ShizukuService.getManagerApplicationInfo().sourceDir,
            token, packageName, classname, processNameSuffix, callingUid, debug);
    // ← ★★★ 回到 W1D3 的 ServiceStarter ★★★
    //   commandForUserService() 拼接如下命令：
    //
    //   CLASSPATH='/path/to/Shizuku.apk' /system/bin/app_process
    //       --nice-name='com.example:shizuku'
    //       moe.shizuku.starter.ServiceStarter
    //       --token='...' --package='com.example' --class='MyUserService' --uid=10xxx
    //
    //   解释：
    //   - CLASSPATH 设成 Shizuku 的 APK 路径（ServiceStarter 在里面）
    //   - app_process 在 App 的进程空间 fork 新进程（继承 App 的 uid/环境）
    //   - ServiceStarter.main() 被调用（和 W1D3 同一个入口！）
    //   - ServiceStarter 创建 UserService 的 binder → sendBinder() 传回 ShizukuService
    //
    //   所以 UserService 的启动流程和 ShizukuService 的启动流程
    //   **共用同一个 ServiceStarter**——区别在于传的参数不同：
    //   - ShizukuService 启动时传的是 server 类名
    //   - UserService 启动时传的是 App 自己定义的类名
    //
    //   面试点："UserService 和 ShizukuService 是同一个进程吗？"
    //   答案：不是。ShizukuService 在 shizuku_server 进程（shell uid），
    //   UserService 在 App 进程内（App uid），但通过 binder 连接到 ShizukuService。
}
```

### 3. onUserServiceRecordCreated()：UserService 创建后的生命周期管理

```java
@Override
public void onUserServiceRecordCreated(UserServiceRecord record, PackageInfo packageInfo) {
    super.onUserServiceRecordCreated(record, packageInfo);
    // ← 父类做基础记录（存到 userServiceRecords）和权限检查

    String packageName = packageInfo.packageName;

    // --- 监控 APK 更新 ---
    ApkChangedListener listener = new ApkChangedListener() {
        @Override
        public void onApkChanged() {
            // ← ★ 当 App 的 APK 被更新或卸载时触发 ★
            //   这是通过 ApkChangedObservers 实现的——它监听 APK 文件的修改时间。

            String newSourceDir = null;
            for (int userId : UserManagerApis.getUserIdsNoThrow()) {
                PackageInfo pi = PackageManagerApis.getPackageInfoNoThrow(packageName, 0, userId);
                if (pi != null && pi.applicationInfo != null && pi.applicationInfo.sourceDir != null) {
                    newSourceDir = pi.applicationInfo.sourceDir;
                    break;
                }
            }

            if (newSourceDir == null) {
                // App 被卸载了 → 移除这个 UserService
                LOGGER.v("remove record %s because package %s has been removed",
                    record.token, packageName);
                record.removeSelf();
            } else {
                // App 升级了 → APK 路径变了，重新注册监听（指向新 APK）
                LOGGER.v("update apk listener for record %s since package %s is upgrading",
                    record.token, packageName);
                ApkChangedObservers.stop(this);
                ApkChangedObservers.start(newSourceDir, this);
            }
        }
    };

    ApkChangedObservers.start(packageInfo.applicationInfo.sourceDir, listener);
    // ← sourceDir 是 APK 文件路径（如 /data/app/com.example-xxx/base.apk）。
    //   ApkChangedObservers 通过 FileObserver 监听这个文件的 IN_MODIFY 事件。
    //   一旦 APK 被覆盖（更新），listener.onApkChanged() 被回调。

    apkChangedListeners.put(record, listener);
    // ← 建立 record → listener 映射，后续移除时用于清理。
}
```

### 4. onUserServiceRecordRemoved()：清理

```java
@Override
public void onUserServiceRecordRemoved(UserServiceRecord record) {
    super.onUserServiceRecordRemoved(record);
    // ← 父类从 userServiceRecords 中移除

    ApkChangedListener listener = apkChangedListeners.get(record);
    if (listener != null) {
        ApkChangedObservers.stop(listener);
        // ← 停止监听 APK 变更
        apkChangedListeners.remove(record);
        // ← 解除映射
    }
}
```

---

## W1D4 帮助你生成问题的提示

对照你今天看到的三处深读内容，下面每个框都是一个可以追问的方向（答案自己先想想，想不通就放进问题清单问我）：

- **ShizukuService.attachApplication()**（W1D3 注释版里略过了）：App 向 ShizukuService「报到」时传了什么？`attachApplication` 和 `sendBinderToUserApp` 是什么关系？为什么 binder 已经通过 ContentProvider 发出去了，还需要 App 调一次 `attachApplication` 回来？

- **BinderSender 的去重逻辑**：`PID_LIST` 和 `UID_LIST` 分别存什么？为什么 ProcessObserver 和 UidObserver 各维护一套去重列表？如果 pid 和 uid 都命中——会不会重复投递？

- **UserService 的本质**：它不是普通的 Service 组件——`app_process` fork 出来的是什么？UserService 跑在 App 的 uid 下还是 shell uid？为什么 App 自己的进程里能跑 Shizuku 权限的代码？

- **ContentProvider.call() 的 method 参数**：W1D3 里 ServiceStarter 传 `"sendUserService"`，ShizukuService 传 `"sendBinder"`。发送端不同、接收端也不同——Manager App 的 ContentProvider 怎么区分这两者？它 call() 里做了什么？

≥3 条即可，不设上限。你现在去读，读完把问题发过来——我今天不主动讲，等你问。