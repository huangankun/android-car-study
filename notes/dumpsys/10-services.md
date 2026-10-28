# dumpsys 存档：10-services.md（讲解版）

命令：`adb shell dumpsys activity services`

**这个服务是什么**：AMS 的 services 子系统，回答「系统里现在**正在运行**的 App 层 Service 有哪些、谁绑定了它」。

**这段输出在讲什么**：3142 行全是「活着的」Service 记录——GMS 的广告 ID 服务、蓝牙 HID 服务、短信 RCS 服务……每个都记着它的进程、谁绑定了它、能不能转前台。

## 逐段讲解

### 1. 先澄清一个关键概念（面试高频陷阱）

这里 `activity services` 里的 **Service 是 App 层的 `Service` 组件**（`startService`/`bindService` 那个），**不是** `service list` 里看到的 binder 系统服务（AMS/WMS/PMS 那种，那是注册在 ServiceManager 上的 C++ 服务）。**两个「service」完全不是一回事**——前者是 App 组件，后者是系统服务的 binder 对象。名字一样，层次差两层。

### 2. 一个 ServiceRecord 的完整档案（拿第一个拆）

```text
  * ServiceRecord{584a5ef u0 com.google.android.gms/.ads.identifier.service.AdvertisingIdService}
    intent={act=com.google.android.gms.ads.identifier.service.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    allowStartForeground=ACTIVITY_STARTER
    createTime=-24s60ms startingBgTimeout=--
```

**讲解**：`ServiceRecord` 是每个运行中 Service 的档案：
- `packageName` / `processName` —— 服务在哪个包、跑在哪个进程。
- `baseDir` —— 服务所属 APK 的位置（`/product/priv-app` = 预装特权应用）。
- `app=ProcessRecord{... 1659:...}` —— 它所在进程的记录（1659 是 PID）。
- `allowStartForeground=ACTIVITY_STARTER` —— **Android 14 的前台服务（FGS）限制**：什么理由允许它转前台（这里是「因为是从 Activity 启动的」）。

### 3. Bindings：谁绑定了这个服务

```text
    Bindings:
    * IntentBindRecord{2bb124f CREATE}:
      intent={act=com.google.android.gms.ads.identifier.service.START ...}
      binder=android.os.BinderProxy@1550ddc
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{... ProcessRecord{... youtube.music ...}}
```

**讲解**：这段回答「谁在用这个服务」。`Client AppBindRecord` 里是客户端进程——这个广告 ID 服务被 **youtube.music** 绑定了。`hasBound=true` 表示绑定已完成。**查「某个服务卡住/谁连不上谁」，就看 Bindings 段里的连接状态。**

### 4. 前台服务（FGS）——座舱里最相关的部分

```text
    infoAllowStartForeground=[... uidState: BTOP; code:ACTIVITY_STARTER; targetSdkVersion:33; ...]
```

**讲解**：Android 14 对 FGS（前台服务）限制极严——**App 不能随便 `startForeground`，必须满足特定条件**（有可见 Activity、收到特定广播、系统白名单等），否则直接 `ForegroundServiceStartNotAllowedException`。座舱里导航、语音、媒体播放大量依赖 FGS，这套限制是车机 App 适配 Android 14 的必修课。**`dumpsys activity services` 里 `allowStartForeground` 和 `infoAllowStartForeground` 就是判断「这个服务为什么能/不能转前台」的现场证据。**

**一句话结论**：`dumpsys activity services` 是「运行中 App 服务的花名册」——谁在跑、跑在哪个进程、谁绑定、能否转前台。查「服务莫名被杀/前台服务启动失败/绑定异常」从这里开始。

## 完整原始输出


```text
ACTIVITY MANAGER SERVICES (dumpsys activity services)
  User 0 active services:
  * ServiceRecord{584a5ef u0 com.google.android.gms/.ads.identifier.service.AdvertisingIdService}
    intent={act=com.google.android.gms.ads.identifier.service.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.ads.identifier.service.START pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s60ms startingBgTimeout=--
    lastActivity=-21s443ms restartTime=-24s60ms createdFromFg=false
    Bindings:
    * IntentBindRecord{2bb124f CREATE}:
      intent={act=com.google.android.gms.ads.identifier.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@1550ddc
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{f981ee5 ProcessRecord{f277914 1591:com.google.android.apps.youtube.music/u0a155}}
        Per-process Connections:
          ConnectionRecord{9d682ce u0 CR com.google.android.gms/.ads.identifier.service.AdvertisingIdService:@30a5bc9 flags=0x1}
    All Connections:
      ConnectionRecord{9d682ce u0 CR com.google.android.gms/.ads.identifier.service.AdvertisingIdService:@30a5bc9 flags=0x1}

  * ServiceRecord{4724240 u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s522ms startingBgTimeout=--
    lastActivity=-26s522ms restartTime=-26s522ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{74d1dba}:
      intent={act=android.bluetooth.IBluetoothHidDevice cmp=com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService}
      binder=android.os.BinderProxy@2c0846b
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{a132bc8 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{de257ee u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService:@c79d169 flags=0x0}
    All Connections:
      ConnectionRecord{de257ee u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService:@c79d169 flags=0x0}

  * ServiceRecord{3ac861b u0 com.google.android.apps.messaging/com.google.android.ims.service.JibeService}
    intent={act=com.google.android.ims.rcs.singleregistration.ISingleRegistrationVendorImsController cmp=com.google.android.apps.messaging/com.google.android.ims.service.JibeService}
    packageName=com.google.android.apps.messaging
    processName=com.google.android.apps.messaging:rcs
    baseDir=/product/priv-app/PrebuiltBugle/PrebuiltBugle.apk
    dataDir=/data/user/0/com.google.android.apps.messaging
    app=ProcessRecord{8ddbe7d 2753:com.google.android.apps.messaging:rcs/u0a130}
    mAllowWhileInUsePermissionInFgsReason=DENIED
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.apps.messaging
    recentCallingUid=10130
    allowStartForeground=BACKGROUND_FGS_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.apps.messaging; callingUid: 10130; uidState: TRNB; uidBFSL: n/a; intent: Intent { act=com.google.android.ims.rcs.singleregistration.ISingleRegistrationVendorImsController cmp=com.google.android.apps.messaging/com.google.android.ims.service.JibeService (has extras) }; code:BACKGROUND_FGS_PERMISSION; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-23s88ms startingBgTimeout=--
    lastActivity=-8s276ms restartTime=-23s20ms createdFromFg=false
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1
    Bindings:
    * IntentBindRecord{630c461 CREATE}:
      intent={act=com.google.android.ims.rcs.singleregistration.ISingleRegistrationVendorImsController cmp=com.google.android.apps.messaging/com.google.android.ims.service.JibeService}
      binder=android.os.BinderProxy@29f5b86
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{b60fc47 ProcessRecord{6e4bf43 2358:com.google.android.apps.messaging/u0a130}}
        Per-process Connections:
          ConnectionRecord{3678c83 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@6f95732 flags=0x1}
          ConnectionRecord{8258cd4 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@8c2d227 flags=0x1}
          ConnectionRecord{dd94073 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@e72a4e2 flags=0x1}
    * IntentBindRecord{b133c74}:
      intent={act=com.google.android.ims.rcs.engine.IRcsEngineTemporaryController cmp=com.google.android.apps.messaging/com.google.android.ims.service.JibeService}
      binder=android.os.BinderProxy@954459d
      requested=true received=true hasBound=false doRebind=false
    All Connections:
      ConnectionRecord{3678c83 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@6f95732 flags=0x1}
      ConnectionRecord{8258cd4 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@8c2d227 flags=0x1}
      ConnectionRecord{dd94073 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@e72a4e2 flags=0x1}

  * ServiceRecord{18bc0a7 u0 com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService}
    intent={act=android.net.ITetheringConnector cmp=com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService}
    packageName=com.google.android.networkstack.tethering
    processName=com.android.networkstack.process
    permission=android.permission.MAINLINE_NETWORK_STACK
    baseDir=/apex/com.android.tethering/priv-app/TetheringGoogle@340818080/TetheringGoogle.apk
    dataDir=/data/user_de/0/com.google.android.networkstack.tethering
    app=ProcessRecord{d826121 847:com.android.networkstack.process/1073}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.net.ITetheringConnector cmp=com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-27s153ms startingBgTimeout=--
    lastActivity=-27s118ms restartTime=-27s118ms createdFromFg=true
    Bindings:
    * IntentBindRecord{a85aa12 CREATE}:
      intent={act=android.net.ITetheringConnector cmp=com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService}
      binder=android.os.BinderProxy@a715e3
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{61abe0 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{b8484c9 u0 CR IMP com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService:@e58cd0 flags=0x41}
    All Connections:
      ConnectionRecord{b8484c9 u0 CR IMP com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService:@e58cd0 flags=0x41}

  * ServiceRecord{1b73b7d u0 com.google.android.gms/.nearby.sharing.ReceiveSurfaceService}
    intent={cmp=com.google.android.gms/.nearby.sharing.ReceiveSurfaceService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/.nearby.sharing.ReceiveSurfaceService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-18s860ms startingBgTimeout=--
    lastActivity=-18s860ms restartTime=-18s860ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{7a57b3f u0 com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService}
    intent={act=grpc.io.action.BIND cmp=com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService}
    packageName=com.google.android.as.oss
    processName=com.google.android.as.oss
    baseDir=/product/priv-app/DeviceIntelligenceNetworkPrebuilt/DeviceIntelligenceNetworkPrebuilt.apk
    dataDir=/data/user/0/com.google.android.as.oss
    app=ProcessRecord{a0563d2 2223:com.google.android.as.oss/u0a126}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.as
    recentCallingUid=10131
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.as; callingUid: 10131; uidState: BFGS; uidBFSL: [BFSL]; intent: Intent { act=grpc.io.action.BIND cmp=com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s271ms startingBgTimeout=--
    lastActivity=-24s171ms restartTime=-24s171ms createdFromFg=true
    Bindings:
    * IntentBindRecord{b349e99 CREATE}:
      intent={act=grpc.io.action.BIND cmp=com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService}
      binder=android.os.BinderProxy@110555e
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{2ab2d3f ProcessRecord{731422c 1503:com.google.android.as/u0a131}}
        Per-process Connections:
          ConnectionRecord{1fbce5d u0 CR com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService:@2747034 flags=0x1}
    All Connections:
      ConnectionRecord{1fbce5d u0 CR com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService:@2747034 flags=0x1}

  * ServiceRecord{7fff5b6 u0 com.google.android.gms/.icing.service.AppIndexingService}
    intent={act=com.google.android.gms.icing.APP_INDEXING_SERVICE pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.icing.APP_INDEXING_SERVICE pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-22s574ms startingBgTimeout=--
    lastActivity=-22s287ms restartTime=-22s574ms createdFromFg=true
    Bindings:
    * IntentBindRecord{865a60c CREATE}:
      intent={act=com.google.android.gms.icing.APP_INDEXING_SERVICE pkg=com.google.android.gms}
      binder=android.os.BinderProxy@5278b55
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{708696a ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{f87a951 u0 CR WACT CAPS com.google.android.gms/.icing.service.AppIndexingService:@ef3ce78 flags=0x1081}
    All Connections:
      ConnectionRecord{f87a951 u0 CR WACT CAPS com.google.android.gms/.icing.service.AppIndexingService:@ef3ce78 flags=0x1081}

  * ServiceRecord{ccbdec6 u0 com.google.android.gms/.deviceconnection.service.DeviceConnectionWatcherService}
    intent={cmp=com.google.android.gms/.deviceconnection.service.DeviceConnectionWatcherService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/.deviceconnection.service.DeviceConnectionWatcherService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-19s52ms startingBgTimeout=--
    lastActivity=-19s52ms restartTime=-19s52ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{af5e5b u0 com.google.android.apps.messaging/com.google.apps.tiktok.concurrent.AndroidFuturesService}
    intent={cmp=com.google.android.apps.messaging/com.google.apps.tiktok.concurrent.AndroidFuturesService}
    packageName=com.google.android.apps.messaging
    processName=com.google.android.apps.messaging
    baseDir=/product/priv-app/PrebuiltBugle/PrebuiltBugle.apk
    dataDir=/data/user/0/com.google.android.apps.messaging
    app=null
    mAllowWhileInUsePermissionInFgsReason=DENIED
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.apps.messaging
    recentCallingUid=10130
    allowStartForeground=BACKGROUND_FGS_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.apps.messaging; callingUid: 10130; uidState: CEM ; uidBFSL: n/a; intent: Intent { cmp=com.google.android.apps.messaging/com.google.apps.tiktok.concurrent.AndroidFuturesService (has extras) }; code:BACKGROUND_FGS_PERMISSION; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-23s191ms startingBgTimeout=--
    lastActivity=-23s191ms restartTime=-- createdFromFg=false

  * ServiceRecord{20d1fad u0 com.android.systemui/.keyguard.KeyguardService}
    intent={cmp=com.android.systemui/.keyguard.KeyguardService}
    packageName=com.android.systemui
    processName=com.android.systemui
    baseDir=/system_ext/priv-app/SystemUIGoogle/SystemUIGoogle.apk
    dataDir=/data/user_de/0/com.android.systemui
    app=ProcessRecord{6218346 765:com.android.systemui/u0a169}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { flg=0x100 cmp=com.android.systemui/.keyguard.KeyguardService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s933ms startingBgTimeout=--
    lastActivity=-26s932ms restartTime=-26s932ms createdFromFg=true
    Bindings:
    * IntentBindRecord{ecd16f8 CREATE}:
      intent={flg=0x100 cmp=com.android.systemui/.keyguard.KeyguardService}
      binder=android.os.BinderProxy@62287d1
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{ebbb236 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{1bdf4c4 u0 CR com.android.systemui/.keyguard.KeyguardService:@5bd23d7 flags=0x1}
    All Connections:
      ConnectionRecord{1bdf4c4 u0 CR com.android.systemui/.keyguard.KeyguardService:@5bd23d7 flags=0x1}

  * ServiceRecord{3761282 u0 com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService}
    intent={cmp=com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService}
    packageName=com.google.android.googlequicksearchbox
    processName=com.google.android.googlequicksearchbox:search
    permission=android.permission.BIND_JOB_SERVICE
    baseDir=/product/priv-app/Velvet/Velvet.apk
    dataDir=/data/user/0/com.google.android.googlequicksearchbox
    app=ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { flg=0x4 cmp=com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s190ms startingBgTimeout=--
    lastActivity=-20s979ms restartTime=-25s47ms createdFromFg=true
    Bindings:
    * IntentBindRecord{1fb8537 CREATE}:
      intent={flg=0x4 cmp=com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService}
      binder=android.os.BinderProxy@a38aaa4
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{cf6d00d ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{d5a01d u0 CR !FG !PRCP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService:@5af70f4 flags=0x8105}
    All Connections:
      ConnectionRecord{d5a01d u0 CR !FG !PRCP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService:@5af70f4 flags=0x8105}

  * ServiceRecord{f369568 u0 com.google.android.gms/.droidguard.DroidGuardService}
    intent={act=com.google.android.gms.droidguard.service.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms.unstable
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{9597961 2374:com.google.android.gms.unstable/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.droidguard.service.START pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-23s924ms startingBgTimeout=--
    lastActivity=-23s456ms restartTime=-23s723ms createdFromFg=true
    Bindings:
    * IntentBindRecord{f88bbc2 CREATE}:
      intent={act=com.google.android.gms.droidguard.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@793dd3
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{8a7cd10 ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{44994c8 u0 CR WACT CAPS com.google.android.gms/.droidguard.DroidGuardService:@d9af16b flags=0x1081}
      * Client AppBindRecord{a4d6009 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{fc63bf0 u0 CR WACT CAPS com.google.android.gms/.droidguard.DroidGuardService:@f229c33 flags=0x1081}
    All Connections:
      ConnectionRecord{44994c8 u0 CR WACT CAPS com.google.android.gms/.droidguard.DroidGuardService:@d9af16b flags=0x1081}
      ConnectionRecord{fc63bf0 u0 CR WACT CAPS com.google.android.gms/.droidguard.DroidGuardService:@f229c33 flags=0x1081}

  * ServiceRecord{95cf227 u0 com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s523ms startingBgTimeout=--
    lastActivity=-26s523ms restartTime=-26s523ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{62ad20e}:
      intent={act=android.bluetooth.IBluetoothHeadset cmp=com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService}
      binder=android.os.BinderProxy@10fe42f
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{6a4aa3c ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{9471df u0 com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService:@7b7487e flags=0x0}
    All Connections:
      ConnectionRecord{9471df u0 com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService:@7b7487e flags=0x0}

  * ServiceRecord{20f760 u0 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService}
    intent={act=android.service.autofill.augmented.AugmentedAutofillService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.BIND_AUGMENTED_AUTOFILL_SERVICE
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.autofill.augmented.AugmentedAutofillService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s354ms startingBgTimeout=--
    lastActivity=-25s281ms restartTime=-25s281ms createdFromFg=true
    Bindings:
    * IntentBindRecord{662f3c5 CREATE}:
      intent={act=android.service.autofill.augmented.AugmentedAutofillService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService}
      binder=android.os.BinderProxy@dc6011a
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{5c0944b ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{9e48662 u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService:@3cea12d flags=0x1}
    All Connections:
      ConnectionRecord{9e48662 u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService:@3cea12d flags=0x1}

  * ServiceRecord{589131d u0 com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService}
    intent={act=android.service.systemcaptions.SystemCaptionsManagerService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService}
    packageName=com.google.android.as
    processName=com.google.android.as
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.systemcaptions.SystemCaptionsManagerService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s387ms startingBgTimeout=--
    lastActivity=-25s281ms restartTime=-25s281ms createdFromFg=true
    Bindings:
    * IntentBindRecord{d302e28 CREATE}:
      intent={act=android.service.systemcaptions.SystemCaptionsManagerService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService}
      binder=null
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{6840741 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{2cc7e8e u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService:@7efee89 flags=0x4001001}
    All Connections:
      ConnectionRecord{2cc7e8e u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService:@7efee89 flags=0x4001001}

  * ServiceRecord{f4beeac u0 com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService}
    intent={cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService}
    packageName=com.google.android.as
    processName=com.google.android.as
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.as
    recentCallingUid=10131
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.as; callingUid: 10131; uidState: BFGS; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s387ms startingBgTimeout=--
    lastActivity=-23s300ms restartTime=-24s387ms createdFromFg=true
    Bindings:
    * IntentBindRecord{db314e6 CREATE}:
      intent={cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService}
      binder=android.os.BinderProxy@5822a27
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{26e04d4 ProcessRecord{731422c 1503:com.google.android.as/u0a131}}
        Per-process Connections:
          ConnectionRecord{5fd88f2 u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:@916d3fd flags=0x1}
          ConnectionRecord{bd0b45f u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:@60904fe flags=0x1}
    All Connections:
      ConnectionRecord{bd0b45f u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:@60904fe flags=0x1}
      ConnectionRecord{5fd88f2 u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:@916d3fd flags=0x1}

  * ServiceRecord{f7ea17 u0 com.google.android.gms/.auth.setup.devicesignals.LockScreenService}
    intent={cmp=com.google.android.gms/.auth.setup.devicesignals.LockScreenService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/.auth.setup.devicesignals.LockScreenService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-19s198ms startingBgTimeout=--
    lastActivity=-19s198ms restartTime=-19s198ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{6168190 u0 com.google.android.gms/.gcm.GcmService}
    intent={pkg=com.google.android.gms cmp=com.google.android.gms/.gcm.GcmService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    permission=com.google.android.gtalkservice.permission.GTALK_SERVICE
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { flg=0x89000010 pkg=com.google.android.gms cmp=com.google.android.gms/.gcm.GcmService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-22s841ms startingBgTimeout=--
    lastActivity=-19s21ms restartTime=-22s840ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=3
 startCommandResult=1

  * ServiceRecord{684757a u0 com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps}
    intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.nearby.sharing.START_SERVICE cmp=com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.chimera.BoundService.START dat=chimera-action: cmp=com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-18s852ms startingBgTimeout=--
    lastActivity=-18s808ms restartTime=-18s852ms createdFromFg=true
    Bindings:
    * IntentBindRecord{e48d67d CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.nearby.sharing.START_SERVICE cmp=com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps}
      binder=android.os.BinderProxy@80b9972
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{5dd41c3 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{7bafda5 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps:@2512f9c flags=0x1081}
    All Connections:
      ConnectionRecord{7bafda5 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps:@2512f9c flags=0x1081}

  * ServiceRecord{a8af784 u0 com.google.android.gms/.clearcut.debug.ClearcutDebugDumpService}
    intent={cmp=com.google.android.gms/.clearcut.debug.ClearcutDebugDumpService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/.clearcut.debug.ClearcutDebugDumpService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-22s806ms startingBgTimeout=--
    lastActivity=-19s71ms restartTime=-22s806ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=2
 startCommandResult=1

  * ServiceRecord{152ff3e u0 com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService}
    intent={cmp=com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService}
    packageName=com.google.android.devicelockcontroller
    processName=com.google.android.devicelockcontroller
    baseDir=/apex/com.android.devicelock/priv-app/DeviceLockControllerGoogle@UE1A.230829.050/DeviceLockControllerGoogle.apk
    dataDir=/data/user/0/com.google.android.devicelockcontroller
    app=ProcessRecord{89fc5ac 1939:com.google.android.devicelockcontroller/u0a191}
    mAllowWhileInUsePermissionInFgsReason=DENIED
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.devicelockcontroller
    recentCallingUid=10191
    allowStartForeground=LOCKED_BOOT_COMPLETED
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.devicelockcontroller; callingUid: 10191; uidState: SVC ; uidBFSL: n/a; intent: Intent { cmp=com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService }; code:LOCKED_BOOT_COMPLETED; tempAllowListReason:<e0125f0 android.intent.action.LOCKED_BOOT_COMPLETED/u0,reasonCode:LOCKED_BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s451ms startingBgTimeout=--
    lastActivity=-24s450ms restartTime=-24s450ms createdFromFg=false
    Bindings:
    * IntentBindRecord{9109a40 CREATE}:
      intent={cmp=com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService}
      binder=android.os.BinderProxy@8915d79
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{4f5dabe ProcessRecord{89fc5ac 1939:com.google.android.devicelockcontroller/u0a191}}
        Per-process Connections:
          ConnectionRecord{a5243f9 u0 CR com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService:@430ac0 flags=0x1}
    All Connections:
      ConnectionRecord{a5243f9 u0 CR com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService:@430ac0 flags=0x1}

  * ServiceRecord{14db15c u0 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService}
    intent={act=android.service.smartspace.SmartspaceService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.MANAGE_SMARTSPACE
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.smartspace.SmartspaceService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s390ms startingBgTimeout=--
    lastActivity=-25s283ms restartTime=-25s283ms createdFromFg=true
    Bindings:
    * IntentBindRecord{248371f CREATE}:
      intent={act=android.service.smartspace.SmartspaceService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService}
      binder=android.os.BinderProxy@a851a6c
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{4415835 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{47125df u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService:@b064c7e flags=0x4001001}
    All Connections:
      ConnectionRecord{47125df u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService:@b064c7e flags=0x4001001}

  * ServiceRecord{8b546a3 u0 com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService}
    intent={cmp=com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService}
    packageName=com.google.android.apps.messaging
    processName=com.google.android.apps.messaging:rcs
    permission=android.permission.BIND_CARRIER_MESSAGING_CLIENT_SERVICE
    baseDir=/product/priv-app/PrebuiltBugle/PrebuiltBugle.apk
    dataDir=/data/user/0/com.google.android.apps.messaging
    app=ProcessRecord{8ddbe7d 2753:com.google.android.apps.messaging:rcs/u0a130}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-13s409ms startingBgTimeout=--
    lastActivity=-13s409ms restartTime=-13s409ms createdFromFg=true
    Bindings:
    * IntentBindRecord{6b0e4ca CREATE}:
      intent={cmp=com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService}
      binder=android.os.BinderProxy@d43263b
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{7df7158 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{99f25d2 u0 CR FGS !VIS com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService:@bb585d flags=0x44000001}
    All Connections:
      ConnectionRecord{99f25d2 u0 CR FGS !VIS com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService:@bb585d flags=0x44000001}

  * ServiceRecord{70c483 u0 com.google.android.gms/.chimera.PersistentApiService}
    intent={act=com.google.android.gms.phenotype.service.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.apps.wellbeing; callingUid: 10121; uidState: BFGS; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.phenotype.service.START pkg=com.google.android.gms }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s391ms startingBgTimeout=--
    lastActivity=-19s192ms restartTime=-25s391ms createdFromFg=true
    Bindings:
    * IntentBindRecord{bc42b1 CREATE}:
      intent={act=com.google.android.gms.phenotype.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@2608396
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{733eb17 ProcessRecord{6e4bf43 2358:com.google.android.apps.messaging/u0a130}}
        Per-process Connections:
          ConnectionRecord{76b3c49 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@8de7250 flags=0x1081}
      * Client AppBindRecord{d864b04 ProcessRecord{8926215 3483:com.google.android.partnersetup/u0a120}}
        Per-process Connections:
          ConnectionRecord{86ac434 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@246cb07 flags=0x1081}
      * Client AppBindRecord{62158ed ProcessRecord{8e26d8d 2647:com.google.android.tts/u0a149}}
        Per-process Connections:
          ConnectionRecord{13c5585 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@ee37afc flags=0x1081}
      * Client AppBindRecord{9994322 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{40c397b u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@1f13d0a flags=0x1081}
      * Client AppBindRecord{70221b3 ProcessRecord{9bc13d7 1397:com.google.android.inputmethod.latin/u0a151}}
        Per-process Connections:
          ConnectionRecord{6571060 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@e393c63 flags=0x1081}
      * Client AppBindRecord{59f1370 ProcessRecord{ce59738 3356:com.google.android.gm/u0a145}}
        Per-process Connections:
          ConnectionRecord{ab3c705 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@5b3c27c flags=0x1081}
      * Client AppBindRecord{54796e9 ProcessRecord{e02117f 2693:com.google.android.dialer/u0a123}}
        Per-process Connections:
          ConnectionRecord{c4eaa6 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@3849c01 flags=0x1081}
    * IntentBindRecord{ac6f6e CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.scheduler.ACTION_PROXY_SCHEDULE cmp=com.google.android.gms/.chimera.PersistentApiService}
      binder=android.os.BinderProxy@73260f
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{539f69c ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{dcd1163 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@7e06392 flags=0x1081}
    * IntentBindRecord{b79b8a5}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.tapandpay.service.BIND cmp=com.google.android.gms/.chimera.PersistentApiService}
      binder=android.os.BinderProxy@db4147a
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{446142b}:
      intent={act=com.google.android.contextmanager.service.ContextManagerService.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@3de088
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{5f23a21 CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.phenotype.service.START cmp=com.google.android.gms/.chimera.PersistentApiService}
      binder=android.os.BinderProxy@c5efe46
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{60fc807 ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{c68b169 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@f8207f0 flags=0x1081}
      * Client AppBindRecord{147d34 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{7c8bde2 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@94b06ad flags=0x1081}
    * IntentBindRecord{117575d}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.auth.account.workaccount.START cmp=com.google.android.gms/.chimera.PersistentApiService}
      binder=android.os.BinderProxy@27cb8d2
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{3d6dda3}:
      intent={act=com.google.android.gms.pseudonymous.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@91638a0
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{f770c59}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.icing.LIGHTWEIGHT_INDEX_SERVICE cmp=com.google.android.gms/.chimera.PersistentApiService}
      binder=android.os.BinderProxy@149901e
      requested=true received=true hasBound=false doRebind=false
    All Connections:
      ConnectionRecord{40c397b u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@1f13d0a flags=0x1081}
      ConnectionRecord{86ac434 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@246cb07 flags=0x1081}
      ConnectionRecord{c4eaa6 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@3849c01 flags=0x1081}
      ConnectionRecord{ab3c705 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@5b3c27c flags=0x1081}
      ConnectionRecord{dcd1163 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@7e06392 flags=0x1081}
      ConnectionRecord{76b3c49 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@8de7250 flags=0x1081}
      ConnectionRecord{7c8bde2 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@94b06ad flags=0x1081}
      ConnectionRecord{6571060 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@e393c63 flags=0x1081}
      ConnectionRecord{13c5585 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@ee37afc flags=0x1081}
      ConnectionRecord{c68b169 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@f8207f0 flags=0x1081}

  * ServiceRecord{5e6cd02 u0 com.android.systemui/.wallpapers.ImageWallpaper}
    intent={act=android.service.wallpaper.WallpaperService cmp=com.android.systemui/.wallpapers.ImageWallpaper}
    packageName=com.android.systemui
    processName=com.android.systemui
    permission=android.permission.BIND_WALLPAPER
    baseDir=/system_ext/priv-app/SystemUIGoogle/SystemUIGoogle.apk
    dataDir=/data/user_de/0/com.android.systemui
    app=ProcessRecord{6218346 765:com.android.systemui/u0a169}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.wallpaper.WallpaperService cmp=com.android.systemui/.wallpapers.ImageWallpaper }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-27s297ms startingBgTimeout=--
    lastActivity=-27s188ms restartTime=-27s233ms createdFromFg=true
    Bindings:
    * IntentBindRecord{b6fb0ff CREATE}:
      intent={act=android.service.wallpaper.WallpaperService cmp=com.android.systemui/.wallpapers.ImageWallpaper}
      binder=android.os.BinderProxy@ab63ecc
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{4831515 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{57e424a u0 CR FGSA UI CAPS com.android.systemui/.wallpapers.ImageWallpaper:@19bbbb5 flags=0x22001001}
          ConnectionRecord{cc7b321 u0 CR FGSA UI CAPS com.android.systemui/.wallpapers.ImageWallpaper:@9899d88 flags=0x22001001}
    All Connections:
      ConnectionRecord{57e424a u0 CR FGSA UI CAPS com.android.systemui/.wallpapers.ImageWallpaper:@19bbbb5 flags=0x22001001}
      ConnectionRecord{cc7b321 u0 CR FGSA UI CAPS com.android.systemui/.wallpapers.ImageWallpaper:@9899d88 flags=0x22001001}

  * ServiceRecord{10a86a7 u0 com.google.android.gms/.location.geocode.GeocodeService}
    intent={act=com.android.location.service.GeocodeProvider cmp=com.google.android.gms/.location.geocode.GeocodeService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=com.android.location.service.GeocodeProvider cmp=com.google.android.gms/.location.geocode.GeocodeService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s708ms startingBgTimeout=--
    lastActivity=-24s708ms restartTime=-24s708ms createdFromFg=true
    Bindings:
    * IntentBindRecord{f7a902a CREATE}:
      intent={act=com.android.location.service.GeocodeProvider cmp=com.google.android.gms/.location.geocode.GeocodeService}
      binder=android.os.BinderProxy@9985e1b
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{66e7bb8 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{fe91366 u0 CR !FG !VIS com.google.android.gms/.location.geocode.GeocodeService:@f0efc1 flags=0x40000005}
    All Connections:
      ConnectionRecord{fe91366 u0 CR !FG !VIS com.google.android.gms/.location.geocode.GeocodeService:@f0efc1 flags=0x40000005}

  * ServiceRecord{be82190 u0 com.android.phone/com.android.internal.telephony.CellularNetworkService}
    intent={act=android.telephony.NetworkService pkg=com.android.phone}
    packageName=com.android.phone
    processName=com.android.phone
    permission=android.permission.BIND_TELEPHONY_NETWORK_SERVICE
    baseDir=/system/priv-app/TeleService/TeleService.apk
    dataDir=/data/user_de/0/com.android.phone
    app=ProcessRecord{1598066 937:com.android.phone/1001}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.phone
    recentCallingUid=1001
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.phone; callingUid: 1001; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.telephony.NetworkService pkg=com.android.phone }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s392ms startingBgTimeout=--
    lastActivity=-26s392ms restartTime=-26s392ms createdFromFg=true
    Bindings:
    * IntentBindRecord{f0ced91 CREATE}:
      intent={act=android.telephony.NetworkService pkg=com.android.phone}
      binder=android.os.BinderProxy@80984f6
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{ed4c0f7 ProcessRecord{1598066 937:com.android.phone/1001}}
        Per-process Connections:
          ConnectionRecord{6ec1453 u0 CR com.android.phone/com.android.internal.telephony.CellularNetworkService:@83edc42 flags=0x1}
    All Connections:
      ConnectionRecord{6ec1453 u0 CR com.android.phone/com.android.internal.telephony.CellularNetworkService:@83edc42 flags=0x1}

  * ServiceRecord{a2e2324 u0 com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService}
    intent={cmp=com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-22s334ms startingBgTimeout=--
    lastActivity=-22s295ms restartTime=-22s334ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{96b9b64 CREATE}:
      intent={cmp=com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService}
      binder=android.os.BinderProxy@f81d1cd
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{9c0fa82 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{7f18fb7 u0 CR com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService:@af156b6 flags=0x1}
    All Connections:
      ConnectionRecord{7f18fb7 u0 CR com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService:@af156b6 flags=0x1}

  * ServiceRecord{24c21e6 u0 com.google.android.gms/.chimera.PersistentBoundBrokerService}
    intent={act=android.net.action.RECOMMEND_NETWORKS cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.net.action.RECOMMEND_NETWORKS cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s208ms startingBgTimeout=--
    lastActivity=-19s150ms restartTime=-25s208ms createdFromFg=true
    Bindings:
    * IntentBindRecord{60a7593 CREATE}:
      intent={act=android.net.action.RECOMMEND_NETWORKS cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
      binder=android.os.BinderProxy@4f909d0
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{5e6bdc9 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{ad52841 u0 CR FGS com.google.android.gms/.chimera.PersistentBoundBrokerService:@37d3328 flags=0x4000001}
    * IntentBindRecord{3883cce CREATE}:
      intent={act=com.google.android.gms.clearcut.bootcount.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@8dcd7ef
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{1acf2fc ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{1d44de8 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@5665b0b flags=0x1081}
    * IntentBindRecord{3946d85 CREATE}:
      intent={act=com.google.android.gms.semanticlocation.service.START_ODLH pkg=com.google.android.gms}
      binder=android.os.BinderProxy@96f57da
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{dc9040b ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{f56906a u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@8c9ee55 flags=0x1081}
    * IntentBindRecord{95442e8 CREATE}:
      intent={act=android.intent.action.RESOLVE_INSTANT_APP_PACKAGE cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
      binder=android.os.BinderProxy@cb35d01
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{e7b17a6 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{4d48781 u0 CR FGS com.google.android.gms/.chimera.PersistentBoundBrokerService:@6ed8768 flags=0x4000001}
    * IntentBindRecord{c01d5e7 CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.gmscompliance.service.START cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
      binder=android.os.BinderProxy@39ea594
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{577c83d ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{ead32d9 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@14ae920 flags=0x1081}
      * Client AppBindRecord{f310832 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{afd4222 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@4a9f3ed flags=0x1081}
      * Client AppBindRecord{10be983 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{297eb9 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@82bb103 flags=0x1081}
    * IntentBindRecord{18a8700}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.auth.proximity.devicesyncservice.START cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
      binder=android.os.BinderProxy@71dab39
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{8e3757e}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.auth.proximity.START cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
      binder=android.os.BinderProxy@4199adf
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{391132c CREATE}:
      intent={act=com.google.android.gms.auth.account.data.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@8a4c1f5
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{9bd6b8a ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{a4694c6 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@bf81aa1 flags=0x1081}
    * IntentBindRecord{32705fb}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.clearcut.bootcount.service.START cmp=com.google.android.gms/.chimera.PersistentBoundBrokerService}
      binder=android.os.BinderProxy@6923618
      requested=true received=true hasBound=false doRebind=true
    All Connections:
      ConnectionRecord{ead32d9 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@14ae920 flags=0x1081}
      ConnectionRecord{ad52841 u0 CR FGS com.google.android.gms/.chimera.PersistentBoundBrokerService:@37d3328 flags=0x4000001}
      ConnectionRecord{afd4222 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@4a9f3ed flags=0x1081}
      ConnectionRecord{1d44de8 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@5665b0b flags=0x1081}
      ConnectionRecord{4d48781 u0 CR FGS com.google.android.gms/.chimera.PersistentBoundBrokerService:@6ed8768 flags=0x4000001}
      ConnectionRecord{297eb9 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@82bb103 flags=0x1081}
      ConnectionRecord{f56906a u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@8c9ee55 flags=0x1081}
      ConnectionRecord{a4694c6 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@bf81aa1 flags=0x1081}

  * ServiceRecord{fc38fef u0 com.google.android.gms/.chimera.GmsBoundBrokerService}
    intent={act=com.google.android.gms.gservices.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.apps.messaging
    recentCallingUid=10130
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gsf; callingUid: 10128; uidState: BFGS; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.gservices.START pkg=com.google.android.gms }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s50ms startingBgTimeout=--
    lastActivity=-8s265ms restartTime=-25s46ms createdFromFg=true
    startRequested=false delayedStop=false stopIfKilled=true callStart=false lastStartId=5
 startCommandResult=2
    Bindings:
    * IntentBindRecord{74c8871}:
      intent={act=com.google.android.gms.gservices.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@58eb656
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{5d606d7}:
      intent={act=com.google.android.gms.feedback.internal.IFeedbackService pkg=com.google.android.gms}
      binder=android.os.BinderProxy@3809bc4
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{ad03aad}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.mdh.service.listener.START cmp=com.google.android.gms/.chimera.GmsBoundBrokerService}
      binder=android.os.BinderProxy@b57e1e2
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{20a3973}:
      intent={act=com.google.android.gms.people.contactssync.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@dcdb030
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{162d4a9}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.auth.cryptauth.cryptauthservice.START cmp=com.google.android.gms/.chimera.GmsBoundBrokerService}
      binder=android.os.BinderProxy@7963a2e
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{e44f9cf}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.feedback.internal.IFeedbackService cmp=com.google.android.gms/.chimera.GmsBoundBrokerService}
      binder=android.os.BinderProxy@c959f5c
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{f6b1265}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.mdd.service.START cmp=com.google.android.gms/.chimera.GmsBoundBrokerService}
      binder=android.os.BinderProxy@f4fcb3a
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{dc163eb CREATE}:
      intent={act=com.google.android.gms.constellation.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@a8b5548
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{eff6fe1 ProcessRecord{6e4bf43 2358:com.google.android.apps.messaging/u0a130}}
        Per-process Connections:
          ConnectionRecord{edcd6bf u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@4c0b4de flags=0x1081}
    * IntentBindRecord{fdf6106}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.mdh.service.START cmp=com.google.android.gms/.chimera.GmsBoundBrokerService}
      binder=android.os.BinderProxy@25053c7
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{8a47df4 CREATE}:
      intent={act=com.google.android.mobstore.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@b22291d
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{f808792 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{3ff0d65 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@560a65c flags=0x1081}
    * IntentBindRecord{ff46563 CREATE}:
      intent={act=com.google.android.gms.languageprofile.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@f858560
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{2bd3a19 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{13c619 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@12ec160 flags=0x1081}
    All Connections:
      ConnectionRecord{13c619 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@12ec160 flags=0x1081}
      ConnectionRecord{edcd6bf u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@4c0b4de flags=0x1081}
      ConnectionRecord{3ff0d65 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@560a65c flags=0x1081}

  * ServiceRecord{ceb5819 u0 com.google.android.gms/.chimera.GmsApiService}
    intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.chimera.container.moduleinstall.ModuleInstallService.START cmp=com.google.android.gms/.chimera.GmsApiService}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.googlequicksearchbox
    recentCallingUid=10132
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.googlequicksearchbox; callingUid: 10132; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.chimera.BoundService.START dat=chimera-action: cmp=com.google.android.gms/.chimera.GmsApiService }; code:ACTIVITY_STARTER; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s14ms startingBgTimeout=--
    lastActivity=-21s365ms restartTime=-24s14ms createdFromFg=true
    Bindings:
    * IntentBindRecord{a9b8ade CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.credential.manager.service.firstparty.START cmp=com.google.android.gms/.chimera.GmsApiService}
      binder=android.os.BinderProxy@e3df4bf
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{bad978c ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{4f108b u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@e4bc65a flags=0x1081}
    * IntentBindRecord{f5e5ed5}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.findmydevice.spot.service.locationreport.START cmp=com.google.android.gms/.chimera.GmsApiService}
      binder=android.os.BinderProxy@9d176ea
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{3671ddb}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.findmydevice.spot.service.management.START cmp=com.google.android.gms/.chimera.GmsApiService}
      binder=android.os.BinderProxy@62a078
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{bb31351 CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.pay.service.BIND cmp=com.google.android.gms/.chimera.GmsApiService}
      binder=android.os.BinderProxy@cc817b6
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{52fbcb7 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{813f26 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@ae37281 flags=0x1081}
    * IntentBindRecord{d5d4c24 CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.chimera.container.moduleinstall.ModuleInstallService.START cmp=com.google.android.gms/.chimera.GmsApiService}
      binder=android.os.BinderProxy@5c4938d
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{5b5f942 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{7415b60 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@81d363 flags=0x1081}
    * IntentBindRecord{b796d53}:
      intent={act=com.google.android.gms.asterism.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@3350690
      requested=true received=true hasBound=false doRebind=false
    All Connections:
      ConnectionRecord{7415b60 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@81d363 flags=0x1081}
      ConnectionRecord{813f26 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@ae37281 flags=0x1081}
      ConnectionRecord{4f108b u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@e4bc65a flags=0x1081}

  * ServiceRecord{1a36454 u0 com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService}
    intent={act=com.android.launcher3.WINDOW_OVERLAY dat=app://com.google.android.apps.nexuslauncher:10162?v=11&cv=20 pkg=com.google.android.googlequicksearchbox}
    packageName=com.google.android.googlequicksearchbox
    processName=com.google.android.googlequicksearchbox:search
    baseDir=/product/priv-app/Velvet/Velvet.apk
    dataDir=/data/user/0/com.google.android.googlequicksearchbox
    app=ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_TOP
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.apps.nexuslauncher
    recentCallingUid=10162
    allowStartForeground=PROC_STATE_TOP
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.apps.nexuslauncher; callingUid: 10162; uidState: TOP ; uidBFSL: [BFSL]; intent: Intent { act=com.android.launcher3.WINDOW_OVERLAY dat=app://com.google.android.apps.nexuslauncher:10162/... pkg=com.google.android.googlequicksearchbox }; code:PROC_STATE_TOP; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s827ms startingBgTimeout=--
    lastActivity=-21s525ms restartTime=-24s826ms createdFromFg=true
    Bindings:
    * IntentBindRecord{8f3db89 CREATE}:
      intent={act=com.android.launcher3.WINDOW_OVERLAY dat=app://com.google.android.apps.nexuslauncher:10162?v=11&cv=20 pkg=com.google.android.googlequicksearchbox}
      binder=android.os.BinderProxy@1ae678e
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{a38baf ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}}
        Per-process Connections:
          ConnectionRecord{4cb207b u0 CR IMP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@a4f600a flags=0x41}
          ConnectionRecord{7bb57a7 u0 CR WPRI com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@c868866 flags=0x21}
    All Connections:
      ConnectionRecord{4cb207b u0 CR IMP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@a4f600a flags=0x41}
      ConnectionRecord{7bb57a7 u0 CR WPRI com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@c868866 flags=0x21}

  * ServiceRecord{8ce1958 u0 com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s522ms startingBgTimeout=--
    lastActivity=-26s522ms restartTime=-26s522ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{28bfbbc}:
      intent={act=android.bluetooth.IBluetoothMap cmp=com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService}
      binder=android.os.BinderProxy@bb5a745
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{9ad6e9a ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{1a8a33e u0 com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService:@da7f7f9 flags=0x0}
    All Connections:
      ConnectionRecord{1a8a33e u0 com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService:@da7f7f9 flags=0x0}

  * ServiceRecord{14212b8 u0 com.google.android.gms/.chimera.container.ConfigService}
    intent={act=com.google.android.gms.gcm.ACTION_TASK_READY cmp=com.google.android.gms/.chimera.container.ConfigService}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    permission=com.google.android.gms.permission.BIND_NETWORK_TASK_SERVICE
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.gcm.ACTION_TASK_READY cmp=com.google.android.gms/.chimera.container.ConfigService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-20s575ms startingBgTimeout=--
    lastActivity=-20s575ms restartTime=-20s575ms createdFromFg=true
    Bindings:
    * IntentBindRecord{ba733cb CREATE}:
      intent={act=com.google.android.gms.gcm.ACTION_TASK_READY cmp=com.google.android.gms/.chimera.container.ConfigService}
      binder=android.os.BinderProxy@1fb17a8
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{d0e72c1 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{9aff11b u0 CR !FG !PRCP com.google.android.gms/.chimera.container.ConfigService:@7b88f2a flags=0x105}
    All Connections:
      ConnectionRecord{9aff11b u0 CR !FG !PRCP com.google.android.gms/.chimera.container.ConfigService:@7b88f2a flags=0x105}

  * ServiceRecord{de641ff u0 com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService}
    intent={cmp=com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService}
    packageName=com.google.android.devicelockcontroller
    processName=com.google.android.devicelockcontroller
    baseDir=/apex/com.android.devicelock/priv-app/DeviceLockControllerGoogle@UE1A.230829.050/DeviceLockControllerGoogle.apk
    dataDir=/data/user/0/com.google.android.devicelockcontroller
    app=ProcessRecord{89fc5ac 1939:com.google.android.devicelockcontroller/u0a191}
    mAllowWhileInUsePermissionInFgsReason=DENIED
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.devicelockcontroller
    recentCallingUid=10191
    allowStartForeground=BOOT_COMPLETED
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.devicelockcontroller; callingUid: 10191; uidState: RCVR; uidBFSL: n/a; intent: Intent { cmp=com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService }; code:BOOT_COMPLETED; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-22s239ms startingBgTimeout=--
    lastActivity=-22s239ms restartTime=-22s239ms createdFromFg=false
    Bindings:
    * IntentBindRecord{863da66 CREATE}:
      intent={cmp=com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService}
      binder=android.os.BinderProxy@ff341a7
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{6be0654 ProcessRecord{89fc5ac 1939:com.google.android.devicelockcontroller/u0a191}}
        Per-process Connections:
          ConnectionRecord{a2bc51e u0 CR com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService:@45cf559 flags=0x1}
    All Connections:
      ConnectionRecord{a2bc51e u0 CR com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService:@45cf559 flags=0x1}

  * ServiceRecord{db3ff1f u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s522ms startingBgTimeout=--
    lastActivity=-26s522ms restartTime=-26s522ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{dce79fd}:
      intent={act=android.bluetooth.IBluetoothHidHost cmp=com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService}
      binder=android.os.BinderProxy@c336f2
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{f085143 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{307b54a u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService:@671ab5 flags=0x0}
    All Connections:
      ConnectionRecord{307b54a u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService:@671ab5 flags=0x0}

  * ServiceRecord{56428cb u0 com.google.android.gms/com.google.android.location.fused.FusedLocationService}
    intent={act=com.android.location.service.FusedLocationProvider cmp=com.google.android.gms/com.google.android.location.fused.FusedLocationService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=com.android.location.service.FusedLocationProvider cmp=com.google.android.gms/com.google.android.location.fused.FusedLocationService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s710ms startingBgTimeout=--
    lastActivity=-24s710ms restartTime=-24s710ms createdFromFg=true
    Bindings:
    * IntentBindRecord{c1f33c0 CREATE}:
      intent={act=com.android.location.service.FusedLocationProvider cmp=com.google.android.gms/com.google.android.location.fused.FusedLocationService}
      binder=android.os.BinderProxy@18db8f9
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{149d03e ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{321179a u0 CR !FG !VIS com.google.android.gms/com.google.android.location.fused.FusedLocationService:@37a5445 flags=0x40000005}
    All Connections:
      ConnectionRecord{321179a u0 CR !FG !VIS com.google.android.gms/com.google.android.location.fused.FusedLocationService:@37a5445 flags=0x40000005}

  * ServiceRecord{a48bd27 u0 com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator}
    intent={act=com.google.android.gms.gcm.ACTION_TASK_READY cmp=com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    permission=com.google.android.gms.permission.BIND_NETWORK_TASK_SERVICE
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.gcm.ACTION_TASK_READY cmp=com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-22s420ms startingBgTimeout=--
    lastActivity=-22s420ms restartTime=-22s420ms createdFromFg=true
    Bindings:
    * IntentBindRecord{7d4be9f CREATE}:
      intent={act=com.google.android.gms.gcm.ACTION_TASK_READY cmp=com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator}
      binder=android.os.BinderProxy@5a3cbec
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{367ebb5 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{3fc13e6 u0 CR !FG !PRCP com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator:@a65a241 flags=0x105}
    All Connections:
      ConnectionRecord{3fc13e6 u0 CR !FG !PRCP com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator:@a65a241 flags=0x105}

  * ServiceRecord{2b77304 u0 com.google.android.bluetooth/com.android.bluetooth.opp.BluetoothOppService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.opp.BluetoothOppService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    permission=android.permission.ACCESS_BLUETOOTH_SHARE
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.bluetooth
    recentCallingUid=1002
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.opp.BluetoothOppService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s522ms startingBgTimeout=--
    lastActivity=-26s522ms restartTime=-26s522ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2

  * ServiceRecord{cd2ab22 u0 com.google.android.bluetooth/com.android.bluetooth.pan.PanService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.pan.PanService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.pan.PanService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s521ms startingBgTimeout=--
    lastActivity=-26s521ms restartTime=-26s521ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{eb24a}:
      intent={act=android.bluetooth.IBluetoothPan cmp=com.google.android.bluetooth/com.android.bluetooth.pan.PanService}
      binder=android.os.BinderProxy@fd0a5bb
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{7f7bad8 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{fd51b25 u0 com.google.android.bluetooth/com.android.bluetooth.pan.PanService:@f33531c flags=0x0}
    All Connections:
      ConnectionRecord{fd51b25 u0 com.google.android.bluetooth/com.android.bluetooth.pan.PanService:@f33531c flags=0x0}

  * ServiceRecord{15f8f41 u0 com.google.android.bluetooth/com.android.bluetooth.avrcp.AvrcpTargetService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.avrcp.AvrcpTargetService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.bluetooth
    recentCallingUid=1002
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.avrcp.AvrcpTargetService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s524ms startingBgTimeout=--
    lastActivity=-26s524ms restartTime=-26s524ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2

  * ServiceRecord{86033e u0 com.google.android.gms/.gcm.nts.SchedulerService}
    intent={pkg=com.google.android.gms cmp=com.google.android.gms/.gcm.nts.SchedulerService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { flg=0x89000010 pkg=com.google.android.gms cmp=com.google.android.gms/.gcm.nts.SchedulerService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-22s821ms startingBgTimeout=--
    lastActivity=-18s710ms restartTime=-22s821ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=2
 startCommandResult=1

  * ServiceRecord{e2d14a0 u0 com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl}
    intent={act=android.service.autofill.InlineSuggestionRenderService cmp=com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl}
    packageName=com.google.android.ext.services
    processName=com.google.android.ext.services
    permission=android.permission.BIND_INLINE_SUGGESTION_RENDER_SERVICE
    baseDir=/apex/com.android.extservices/priv-app/GoogleExtServices@340818080/GoogleExtServices.apk
    dataDir=/data/user/0/com.google.android.ext.services
    app=ProcessRecord{55a6a9b 974:com.google.android.ext.services/u0a187}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.autofill.InlineSuggestionRenderService cmp=com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s887ms startingBgTimeout=--
    lastActivity=-26s856ms restartTime=-26s856ms createdFromFg=true
    Bindings:
    * IntentBindRecord{a788e31 CREATE}:
      intent={act=android.service.autofill.InlineSuggestionRenderService cmp=com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl}
      binder=android.os.BinderProxy@b8da916
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{1d9e297 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{3462d95 u0 CR FGS CAPS com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl:@9ac694c flags=0x4001001}
    All Connections:
      ConnectionRecord{3462d95 u0 CR FGS CAPS com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl:@9ac694c flags=0x4001001}

  * ServiceRecord{f46d875 u0 com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl}
    intent={cmp=com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl}
    packageName=com.google.android.providers.media.module
    processName=com.google.android.providers.media.module
    permission=android.permission.BIND_EXTERNAL_STORAGE_SERVICE
    baseDir=/apex/com.android.mediaprovider/priv-app/MediaProviderGoogle@340818080/MediaProviderGoogle.apk
    dataDir=/data/user/0/com.google.android.providers.media.module
    app=ProcessRecord{ded5f59 1478:com.google.android.providers.media.module/u0a186}
    mAllowWhileInUsePermissionInFgsReason=SYSTEM_UID
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=0
    allowStartForeground=SYSTEM_UID
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 0; uidState: NONE; uidBFSL: n/a; intent: Intent { cmp=com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl }; code:SYSTEM_UID; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s408ms startingBgTimeout=--
    lastActivity=-25s357ms restartTime=-25s357ms createdFromFg=true
    Bindings:
    * IntentBindRecord{499ac84 CREATE}:
      intent={cmp=com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl}
      binder=android.os.BinderProxy@a16dc6d
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{c3340a2 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{6f5f7a0 u0 CR IMP com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl:@87238a3 flags=0x41}
    All Connections:
      ConnectionRecord{6f5f7a0 u0 CR IMP com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl:@87238a3 flags=0x41}

  * ServiceRecord{c8d16a u0 com.android.phone/com.android.internal.telephony.data.CellularDataService}
    intent={act=android.telephony.data.DataService pkg=com.android.phone}
    packageName=com.android.phone
    processName=com.android.phone
    permission=android.permission.BIND_TELEPHONY_DATA_SERVICE
    baseDir=/system/priv-app/TeleService/TeleService.apk
    dataDir=/data/user_de/0/com.android.phone
    app=ProcessRecord{1598066 937:com.android.phone/1001}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.phone
    recentCallingUid=1001
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.phone; callingUid: 1001; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.telephony.data.DataService pkg=com.android.phone }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s538ms startingBgTimeout=--
    lastActivity=-26s538ms restartTime=-26s538ms createdFromFg=true
    Bindings:
    * IntentBindRecord{ed01133 CREATE}:
      intent={act=android.telephony.data.DataService pkg=com.android.phone}
      binder=android.os.BinderProxy@4470cf0
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{9d1d269 ProcessRecord{1598066 937:com.android.phone/1001}}
        Per-process Connections:
          ConnectionRecord{5889355 u0 CR com.android.phone/com.android.internal.telephony.data.CellularDataService:@905ce0c flags=0x1}
    All Connections:
      ConnectionRecord{5889355 u0 CR com.android.phone/com.android.internal.telephony.data.CellularDataService:@905ce0c flags=0x1}

  * ServiceRecord{ac3ea8c u0 com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService}
    intent={pkg=com.google.android.googlequicksearchbox cmp=com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService}
    packageName=com.google.android.googlequicksearchbox
    processName=com.google.android.googlequicksearchbox:interactor
    baseDir=/product/priv-app/Velvet/Velvet.apk
    dataDir=/data/user/0/com.google.android.googlequicksearchbox
    app=ProcessRecord{c365f4c 1515:com.google.android.googlequicksearchbox:interactor/u0a132}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.googlequicksearchbox
    recentCallingUid=10132
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.googlequicksearchbox; callingUid: 10132; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { pkg=com.google.android.googlequicksearchbox cmp=com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService }; code:ACTIVITY_STARTER; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s247ms startingBgTimeout=--
    lastActivity=-24s247ms restartTime=-24s247ms createdFromFg=true
    Bindings:
    * IntentBindRecord{2a8c4ee CREATE}:
      intent={pkg=com.google.android.googlequicksearchbox cmp=com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService}
      binder=android.os.BinderProxy@bf08d8f
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{c28081c ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{b3db3bf u0 CR com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService:@6d6e5de flags=0x1}
    All Connections:
      ConnectionRecord{b3db3bf u0 CR com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService:@6d6e5de flags=0x1}

  * ServiceRecord{70e5d81 u0 com.google.android.gms/.thunderbird.EmergencyPersistentService}
    intent={cmp=com.google.android.gms/.thunderbird.EmergencyPersistentService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/.thunderbird.EmergencyPersistentService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-18s658ms startingBgTimeout=--
    lastActivity=-18s658ms restartTime=-18s658ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{90b6ed0 u0 com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener}
    intent={act=android.service.notification.NotificationListenerService cmp=com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener}
    packageName=com.google.android.apps.nexuslauncher
    processName=com.google.android.apps.nexuslauncher
    permission=android.permission.BIND_NOTIFICATION_LISTENER_SERVICE
    baseDir=/system_ext/priv-app/NexusLauncherRelease/NexusLauncherRelease.apk
    dataDir=/data/user/0/com.google.android.apps.nexuslauncher
    app=ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}
    allowlistManager=true
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.notification.NotificationListenerService cmp=com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s196ms startingBgTimeout=--
    lastActivity=-25s196ms restartTime=-25s196ms createdFromFg=true
    Bindings:
    * IntentBindRecord{12c2c25 CREATE}:
      intent={act=android.service.notification.NotificationListenerService cmp=com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener}
      binder=android.os.BinderProxy@ee041fa
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{af273ab ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{1034e93 u0 CR FGS !PRCP com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener:@e219782 flags=0x5000101}
    All Connections:
      ConnectionRecord{1034e93 u0 CR FGS !PRCP com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener:@e219782 flags=0x5000101}

  * ServiceRecord{d5e7e85 u0 com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService}
    intent={act=android.service.notification.NotificationListenerService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.BIND_NOTIFICATION_LISTENER_SERVICE
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    allowlistManager=true
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.notification.NotificationListenerService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s195ms startingBgTimeout=--
    lastActivity=-25s195ms restartTime=-25s195ms createdFromFg=true
    Bindings:
    * IntentBindRecord{9bb8a08 CREATE}:
      intent={act=android.service.notification.NotificationListenerService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService}
      binder=android.os.BinderProxy@31865a1
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{be083c6 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{500a7fc u0 CR FGS !PRCP com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService:@d0a40ef flags=0x5000101}
    All Connections:
      ConnectionRecord{500a7fc u0 CR FGS !PRCP com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService:@d0a40ef flags=0x5000101}

  * ServiceRecord{2151d71 u0 com.android.systemui/.SystemUIService}
    intent={cmp=com.android.systemui/.SystemUIService}
    packageName=com.android.systemui
    processName=com.android.systemui
    baseDir=/system_ext/priv-app/SystemUIGoogle/SystemUIGoogle.apk
    dataDir=/data/user_de/0/com.android.systemui
    app=ProcessRecord{6218346 765:com.android.systemui/u0a169}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { flg=0x100 cmp=com.android.systemui/.SystemUIService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s935ms startingBgTimeout=--
    lastActivity=-26s934ms restartTime=-26s934ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{5661c41 u0 com.google.android.gms/.nearby.exposurenotification.service.ExposureMatchingService}
    intent={act=com.google.android.gms.nearby.exposurenotification.service.EXPOSURE_MATCHING_START cmp=com.google.android.gms/.nearby.exposurenotification.service.ExposureMatchingService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.nearby.exposurenotification.service.EXPOSURE_MATCHING_START cmp=com.google.android.gms/.nearby.exposurenotification.service.ExposureMatchingService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-18s870ms startingBgTimeout=--
    lastActivity=-18s867ms restartTime=-18s867ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{dfb20b1 u0 com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService}
    intent={act=grpc.io.action.BIND cmp=com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService}
    packageName=com.google.android.googlequicksearchbox
    processName=com.google.android.googlequicksearchbox:interactor
    baseDir=/product/priv-app/Velvet/Velvet.apk
    dataDir=/data/user/0/com.google.android.googlequicksearchbox
    app=ProcessRecord{c365f4c 1515:com.google.android.googlequicksearchbox:interactor/u0a132}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.googlequicksearchbox
    recentCallingUid=10132
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.googlequicksearchbox; callingUid: 10132; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=grpc.io.action.BIND cmp=com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService }; code:ACTIVITY_STARTER; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s102ms startingBgTimeout=--
    lastActivity=-24s102ms restartTime=-24s102ms createdFromFg=true
    Bindings:
    * IntentBindRecord{7e29f87 CREATE}:
      intent={act=grpc.io.action.BIND cmp=com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService}
      binder=android.os.BinderProxy@1833eb4
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{534badd ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{5770758 u0 CR com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService:@6c3543b flags=0x1}
    All Connections:
      ConnectionRecord{5770758 u0 CR com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService:@6c3543b flags=0x1}

  * ServiceRecord{78f43c0 u0 android/.hardware.location.GeofenceHardwareService}
    intent={cmp=android/.hardware.location.GeofenceHardwareService}
    packageName=android
    processName=system
    permission=android.permission.LOCATION_HARDWARE
    baseDir=/system/framework/framework-res.apk
    dataDir=/data/system
    app=ProcessRecord{9870635 554:system/1000}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=android/.hardware.location.GeofenceHardwareService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-27s190ms startingBgTimeout=--
    lastActivity=-27s190ms restartTime=-27s190ms createdFromFg=true
    Bindings:
    * IntentBindRecord{c511652 CREATE}:
      intent={cmp=android/.hardware.location.GeofenceHardwareService}
      binder=android.hardware.location.GeofenceHardwareService$1@8bfad23
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{c6f9220 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{eea143 u0 CR android/.hardware.location.GeofenceHardwareService:@c10c6f2 flags=0x1}
    All Connections:
      ConnectionRecord{eea143 u0 CR android/.hardware.location.GeofenceHardwareService:@c10c6f2 flags=0x1}

  * ServiceRecord{602e8f1 u0 com.android.se/.SecureElementService}
    intent={cmp=com.android.se/.SecureElementService}
    packageName=com.android.se
    processName=com.android.se
    baseDir=/system/app/SecureElement/SecureElement.apk
    dataDir=/data/user/0/com.android.se
    app=ProcessRecord{2683db6 905:com.android.se/1068}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.se
    recentCallingUid=1068
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.se; callingUid: 1068; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.android.se/.SecureElementService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s880ms startingBgTimeout=--
    lastActivity=-26s880ms restartTime=-26s880ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{49b0172 u0 com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s524ms startingBgTimeout=--
    lastActivity=-26s524ms restartTime=-26s524ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{ec727d9}:
      intent={act=android.bluetooth.IBluetoothHearingAid cmp=com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService}
      binder=android.os.BinderProxy@3c6459e
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{ad5f87f ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{e76200 u0 com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService:@b75083 flags=0x0}
    All Connections:
      ConnectionRecord{e76200 u0 com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService:@b75083 flags=0x0}

  * ServiceRecord{f6682bc u0 com.google.android.gms/.chimera.GmsIntentOperationService}
    intent={act=com.google.android.gms.chimera.debug.WRITE_JOURNAL_UPDATE_ACTION cat=[targeted_intent_op_prefix:.chimera.debug.ModuleSetJournalUpdate$ModuleSetJournalIntentOperation] cmp=com.google.android.gms/.chimera.GmsIntentOperationService}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.chimera.debug.WRITE_JOURNAL_UPDATE_ACTION cat=[targeted_intent_op_prefix:.chimera.debug.ModuleSetJournalUpdate$ModuleSetJournalIntentOperation] cmp=com.google.android.gms/.chimera.GmsIntentOperationService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-24s454ms startingBgTimeout=--
    lastActivity=-5s732ms restartTime=-24s454ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=66
 startCommandResult=1

  * ServiceRecord{45f789 u0 com.google.android.gms/.chimera.PersistentDirectBootAwareApiService}
    intent={act=com.google.android.gms.clearcut.service.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.settings.intelligence
    recentCallingUid=10127
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.apps.wellbeing; callingUid: 10121; uidState: BFGS; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.clearcut.service.START pkg=com.google.android.gms }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s449ms startingBgTimeout=--
    lastActivity=-20s527ms restartTime=-25s440ms createdFromFg=true
    Bindings:
    * IntentBindRecord{bb04c CREATE}:
      intent={act=com.google.android.gms.clearcut.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@b796895
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{8cd1daa ProcessRecord{6e4bf43 2358:com.google.android.apps.messaging/u0a130}}
        Per-process Connections:
          ConnectionRecord{96d3eb0 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@a4cf1f3 flags=0x1081}
      * Client AppBindRecord{9db9d9b ProcessRecord{8fd97d3 3297:com.google.android.contacts/u0a153}}
        Per-process Connections:
          ConnectionRecord{742ba1d u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@f98b2f4 flags=0x1081}
      * Client AppBindRecord{d698538 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{d08aa70 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@47b4b3 flags=0x1081}
      * Client AppBindRecord{dd4f911 ProcessRecord{ce59738 3356:com.google.android.gm/u0a145}}
        Per-process Connections:
          ConnectionRecord{c2ece81 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@bb88a68 flags=0x1081}
    * IntentBindRecord{bb76a76}:
      intent={act=com.google.android.gms.usagereporting.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@ccc7877
      requested=true received=true hasBound=false doRebind=false
    * IntentBindRecord{2cdbce4 CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.clearcut.service.START cmp=com.google.android.gms/.chimera.PersistentDirectBootAwareApiService}
      binder=android.os.BinderProxy@d7f154d
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{e27b802 ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{bafa55f u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@93919fe flags=0x1081}
      * Client AppBindRecord{4862513 ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{87369d7 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@287c556 flags=0x1081}
    * IntentBindRecord{c1bc350 CREATE}:
      intent={act=com.google.android.chimera.BoundService.START dat=chimera-action:com.google.android.gms.usagereporting.service.START cmp=com.google.android.gms/.chimera.PersistentDirectBootAwareApiService}
      binder=android.os.BinderProxy@d34b949
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{75d524e ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{deaba15 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@21157cc flags=0x1081}
      * Client AppBindRecord{823ff6f ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{8a53702 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@b97304d flags=0x1081}
    All Connections:
      ConnectionRecord{d08aa70 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@47b4b3 flags=0x1081}
      ConnectionRecord{deaba15 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@21157cc flags=0x1081}
      ConnectionRecord{87369d7 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@287c556 flags=0x1081}
      ConnectionRecord{bafa55f u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@93919fe flags=0x1081}
      ConnectionRecord{96d3eb0 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@a4cf1f3 flags=0x1081}
      ConnectionRecord{8a53702 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@b97304d flags=0x1081}
      ConnectionRecord{c2ece81 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@bb88a68 flags=0x1081}
      ConnectionRecord{742ba1d u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@f98b2f4 flags=0x1081}

  * ServiceRecord{f861978 u0 com.google.android.gms/.chimera.PersistentIntentOperationService}
    intent={act=com.google.android.gms.common.broadcast.DELIVER_BROADCAST cat=[targeted_intent_op_prefix:.common.broadcast.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation] cmp=com.google.android.gms/.chimera.PersistentIntentOperationService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: CEM ; uidBFSL: n/a; intent: Intent { act=com.google.android.gms.common.broadcast.DELIVER_BROADCAST cat=[targeted_intent_op_prefix:.common.broadcast.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation] cmp=com.google.android.gms/.chimera.PersistentIntentOperationService (has extras) }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-25s607ms startingBgTimeout=-10s605ms
    lastActivity=-12s983ms restartTime=-25s606ms createdFromFg=false
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=79
 startCommandResult=1

  * ServiceRecord{9bdd595 u0 com.google.android.gms/.geotimezone.GeoTimeZoneService}
    intent={act=android.service.timezone.PrimaryLocationTimeZoneProviderService cmp=com.google.android.gms/.geotimezone.GeoTimeZoneService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    permission=android.permission.BIND_TIME_ZONE_PROVIDER_SERVICE
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.timezone.PrimaryLocationTimeZoneProviderService cmp=com.google.android.gms/.geotimezone.GeoTimeZoneService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s681ms startingBgTimeout=--
    lastActivity=-24s681ms restartTime=-24s681ms createdFromFg=true
    Bindings:
    * IntentBindRecord{e01c47c CREATE}:
      intent={act=android.service.timezone.PrimaryLocationTimeZoneProviderService cmp=com.google.android.gms/.geotimezone.GeoTimeZoneService}
      binder=android.os.BinderProxy@486a105
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{140455a ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{619b14c u0 CR !FG !VIS com.google.android.gms/.geotimezone.GeoTimeZoneService:@2475d7f flags=0x40000005}
    All Connections:
      ConnectionRecord{619b14c u0 CR !FG !VIS com.google.android.gms/.geotimezone.GeoTimeZoneService:@2475d7f flags=0x40000005}

  * ServiceRecord{81c4307 u0 com.google.android.gms/.location.persistent.LocationPersistentService}
    intent={cmp=com.google.android.gms/.location.persistent.LocationPersistentService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/.location.persistent.LocationPersistentService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-17s68ms startingBgTimeout=--
    lastActivity=-17s67ms restartTime=-17s67ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{70674f2 u0 com.google.android.gms/.nearby.discovery.service.DiscoveryService}
    intent={act=com.google.android.gms.nearby.discovery:ACTION_PERMISSION_CHANGE cmp=com.google.android.gms/.nearby.discovery.service.DiscoveryService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    permission=com.google.android.gms.permission.NEARBY_START_DISCOVERER
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.nearby.discovery:ACTION_PERMISSION_CHANGE cmp=com.google.android.gms/.nearby.discovery.service.DiscoveryService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-22s558ms startingBgTimeout=--
    lastActivity=-18s879ms restartTime=-22s558ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=4
 startCommandResult=2

  * ServiceRecord{3292f7f u0 com.google.android.gms/com.google.android.location.internal.PendingIntentCallbackService}
    intent={act=com.google.android.location.internal.action.FLP_LOW_POWER_LOCATION_RESULT pkg=com.google.android.gms cmp=com.google.android.gms/com.google.android.location.internal.PendingIntentCallbackService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.location.internal.action.FLP_LOW_POWER_LOCATION_RESULT pkg=com.google.android.gms cmp=com.google.android.gms/com.google.android.location.internal.PendingIntentCallbackService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-22s770ms startingBgTimeout=--
    lastActivity=-22s440ms restartTime=-22s770ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=4
 startCommandResult=2

  * ServiceRecord{7e00910 u0 com.google.android.gms/com.google.android.location.reporting.service.ReportingAndroidService}
    intent={act=com.google.android.gms.location.reporting.service.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.googlequicksearchbox; callingUid: 10132; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.location.reporting.service.START pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-23s706ms startingBgTimeout=--
    lastActivity=-18s682ms restartTime=-23s706ms createdFromFg=true
    Bindings:
    * IntentBindRecord{b1b238b CREATE}:
      intent={act=com.google.android.gms.location.reporting.service.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@7e4ac68
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{9554881 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{cbce9d3 u0 CR WACT CAPS com.google.android.gms/com.google.android.location.reporting.service.ReportingAndroidService:@11f97c2 flags=0x1081}
    All Connections:
      ConnectionRecord{cbce9d3 u0 CR WACT CAPS com.google.android.gms/com.google.android.location.reporting.service.ReportingAndroidService:@11f97c2 flags=0x1081}

  * ServiceRecord{d0d3a1f u0 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService}
    intent={act=android.service.appprediction.AppPredictionService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.MANAGE_APP_PREDICTIONS
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.appprediction.AppPredictionService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s527ms startingBgTimeout=--
    lastActivity=-24s527ms restartTime=-24s527ms createdFromFg=true
    Bindings:
    * IntentBindRecord{a2d5d26 CREATE}:
      intent={act=android.service.appprediction.AppPredictionService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService}
      binder=android.os.BinderProxy@9166d67
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{88c2714 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{97109be u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService:@84fe879 flags=0x4001001}
    All Connections:
      ConnectionRecord{97109be u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService:@84fe879 flags=0x4001001}

  * ServiceRecord{25e5b0d u0 com.google.android.gms/.nearby.messages.service.NearbyMessagesService}
    intent={act=com.google.android.gms.nearby.messages.service.NearbyMessagesService.START pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.nearby.messages.service.NearbyMessagesService.START pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-22s430ms startingBgTimeout=--
    lastActivity=-18s855ms restartTime=-22s430ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=9
 startCommandResult=1
    Bindings:
    * IntentBindRecord{50cebbd}:
      intent={act=com.google.android.gms.nearby.messages.service.NearbyMessagesService.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@78225b2
      requested=true received=true hasBound=false doRebind=true

  * ServiceRecord{41eeec3 u0 com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService}
    intent={act=android.bluetooth.IBluetooth cmp=com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    permission=android.permission.ACCESS_BLUETOOTH_SHARE
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.bluetooth.IBluetooth cmp=com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-27s69ms startingBgTimeout=--
    lastActivity=-26s944ms restartTime=-26s944ms createdFromFg=true
    Bindings:
    * IntentBindRecord{3927903 CREATE}:
      intent={act=android.bluetooth.IBluetooth cmp=com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService}
      binder=android.os.BinderProxy@18ea080
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{1a186b9 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{82a5a7a u0 CR IMP com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService:@46556a5 flags=0x41}
    All Connections:
      ConnectionRecord{82a5a7a u0 CR IMP com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService:@46556a5 flags=0x41}

  * ServiceRecord{25b3ff0 u0 com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService}
    intent={act=android.service.quicksettings.action.QS_TILE cmp=com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService}
    packageName=com.google.android.permissioncontroller
    processName=com.google.android.permissioncontroller
    permission=android.permission.BIND_QUICK_SETTINGS_TILE
    baseDir=/apex/com.android.permission/priv-app/GooglePermissionController@340818080/GooglePermissionController.apk
    dataDir=/data/user_de/0/com.google.android.permissioncontroller
    app=ProcessRecord{39b6a51 1318:com.google.android.permissioncontroller/u0a182}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.systemui
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.systemui; callingUid: 10169; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.quicksettings.action.QS_TILE cmp=com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<4f5f3b7 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s3ms startingBgTimeout=--
    lastActivity=-25s958ms restartTime=-25s958ms createdFromFg=true
    Bindings:
    * IntentBindRecord{4e8eafe CREATE}:
      intent={act=android.service.quicksettings.action.QS_TILE cmp=com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService}
      binder=android.os.BinderProxy@d39a25f
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{57d44ac ProcessRecord{6218346 765:com.android.systemui/u0a169}}
        Per-process Connections:
          ConnectionRecord{5e9f378 u0 CR WPRI FGSA com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService:@5fbdcdb flags=0x2000021}
    All Connections:
      ConnectionRecord{5e9f378 u0 CR WPRI FGSA com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService:@5fbdcdb flags=0x2000021}

  * ServiceRecord{60ccff4 u0 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService}
    intent={act=android.service.contentcapture.ContentCaptureService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.BIND_CONTENT_CAPTURE_SERVICE
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.contentcapture.ContentCaptureService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s388ms startingBgTimeout=--
    lastActivity=-25s282ms restartTime=-25s282ms createdFromFg=true
    Bindings:
    * IntentBindRecord{a4ad575 CREATE}:
      intent={act=android.service.contentcapture.ContentCaptureService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService}
      binder=android.os.BinderProxy@c64b90a
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{f00057b ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{a348853 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService:@a50a042 flags=0x4001001}
    All Connections:
      ConnectionRecord{a348853 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService:@a50a042 flags=0x4001001}

  * ServiceRecord{9aec4d9 u0 com.google.android.gms/com.google.android.location.internal.server.GoogleLocationService}
    intent={act=com.google.android.location.internal.GMS_NLP pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    permission=android.permission.ACCESS_COARSE_LOCATION
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=BACKGROUND_ACTIVITY_PERMISSION
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=BACKGROUND_ACTIVITY_PERMISSION
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BFGS; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.location.internal.GMS_NLP pkg=com.google.android.gms (has extras) }; code:BACKGROUND_ACTIVITY_PERMISSION; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-24s681ms startingBgTimeout=--
    lastActivity=-17s36ms restartTime=-24s681ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=59
 startCommandResult=1

  * ServiceRecord{abe60a9 u0 com.google.android.gms/com.google.android.contextmanager.service.ContextManagerService}
    intent={cmp=com.google.android.gms/com.google.android.contextmanager.service.ContextManagerService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.gms/com.google.android.contextmanager.service.ContextManagerService (has extras) }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-23s572ms startingBgTimeout=--
    lastActivity=-23s570ms restartTime=-23s570ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{30b6714 u0 com.android.systemui/.dump.SystemUIAuxiliaryDumpService}
    intent={cmp=com.android.systemui/.dump.SystemUIAuxiliaryDumpService}
    packageName=com.android.systemui
    processName=com.android.systemui
    permission=com.android.systemui.permission.SELF
    baseDir=/system_ext/priv-app/SystemUIGoogle/SystemUIGoogle.apk
    dataDir=/data/user_de/0/com.android.systemui
    app=ProcessRecord{6218346 765:com.android.systemui/u0a169}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.systemui
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.systemui; callingUid: 10169; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.android.systemui/.dump.SystemUIAuxiliaryDumpService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<4f5f3b7 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s66ms startingBgTimeout=--
    lastActivity=-26s66ms restartTime=-26s66ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{49d10b6 u0 com.google.android.gms/com.google.android.location.network.NetworkLocationService}
    intent={act=com.android.location.service.v3.NetworkLocationProvider cmp=com.google.android.gms/com.google.android.location.network.NetworkLocationService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    permission=android.permission.WRITE_SECURE_SETTINGS
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=com.android.location.service.v3.NetworkLocationProvider cmp=com.google.android.gms/com.google.android.location.network.NetworkLocationService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s715ms startingBgTimeout=--
    lastActivity=-22s426ms restartTime=-24s715ms createdFromFg=true
    startRequested=false delayedStop=false stopIfKilled=true callStart=false lastStartId=2
 startCommandResult=2
    Bindings:
    * IntentBindRecord{ccfff98 CREATE}:
      intent={act=com.android.location.service.v3.NetworkLocationProvider cmp=com.google.android.gms/com.google.android.location.network.NetworkLocationService}
      binder=android.os.BinderProxy@c0053f1
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{31d5bd6 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{44c5051 u0 CR !FG !VIS com.google.android.gms/com.google.android.location.network.NetworkLocationService:@4d6b178 flags=0x40000005}
    All Connections:
      ConnectionRecord{44c5051 u0 CR !FG !VIS com.google.android.gms/com.google.android.location.network.NetworkLocationService:@4d6b178 flags=0x40000005}

  * ServiceRecord{bb6d029 u0 com.android.stk/.StkAppService}
    intent={cmp=com.android.stk/.StkAppService}
    packageName=com.android.stk
    processName=com.android.phone
    baseDir=/system/app/Stk/Stk.apk
    dataDir=/data/user_de/0/com.android.stk
    app=ProcessRecord{1598066 937:com.android.phone/1001}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.stk
    recentCallingUid=1001
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.stk; callingUid: 1001; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.android.stk/.StkAppService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s48ms startingBgTimeout=--
    lastActivity=-22s711ms restartTime=-26s48ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=3
 startCommandResult=1

  * ServiceRecord{1efa39f u0 com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService}
    intent={act=com.android.location.service.GeofenceProvider cmp=com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=com.android.location.service.GeofenceProvider cmp=com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s709ms startingBgTimeout=--
    lastActivity=-17s67ms restartTime=-24s709ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=10
 startCommandResult=1
    Bindings:
    * IntentBindRecord{2ff7e57 CREATE}:
      intent={act=com.google.android.location.internal.GoogleLocationManagerService.START pkg=com.google.android.gms}
      binder=android.os.BinderProxy@d917d44
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{1b53e2d ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}}
        Per-process Connections:
          ConnectionRecord{80d5c3d u0 CR WACT CAPS com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:@b7e0994 flags=0x1081}
    * IntentBindRecord{6eb5f62 CREATE}:
      intent={act=com.android.location.service.GeofenceProvider cmp=com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService}
      binder=android.os.BinderProxy@113a8f3
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{1cb29b0 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{b1d293e u0 CR !FG !VIS com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:@5a2d5f9 flags=0x40000005}
    All Connections:
      ConnectionRecord{b1d293e u0 CR !FG !VIS com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:@5a2d5f9 flags=0x40000005}
      ConnectionRecord{80d5c3d u0 CR WACT CAPS com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:@b7e0994 flags=0x1081}

  * ServiceRecord{c85a341 u0 com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME}
    intent={act=android.view.InputMethod cmp=com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME}
    packageName=com.google.android.inputmethod.latin
    processName=com.google.android.inputmethod.latin
    permission=android.permission.BIND_INPUT_METHOD
    baseDir=/product/app/LatinIMEGooglePrebuilt/LatinIMEGooglePrebuilt.apk
    dataDir=/data/user/0/com.google.android.inputmethod.latin
    app=ProcessRecord{9bc13d7 1397:com.google.android.inputmethod.latin/u0a151}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.view.InputMethod cmp=com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s629ms startingBgTimeout=--
    lastActivity=-25s545ms restartTime=-25s545ms createdFromFg=true
    Bindings:
    * IntentBindRecord{8549029 CREATE}:
      intent={act=android.view.InputMethod cmp=com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME}
      binder=android.os.BinderProxy@8a40fae
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{935e14f ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{6d327cc u0 CR !FG IMPB SLTA !VIS com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME:@dba9dff flags=0x40880005}
    All Connections:
      ConnectionRecord{6d327cc u0 CR !FG IMPB SLTA !VIS com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME:@dba9dff flags=0x40880005}

  * ServiceRecord{bd6d1ef u0 com.google.android.gms/.wallet.service.PaymentService}
    intent={act=com.google.android.gms.wallet.service.BIND pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.googlequicksearchbox
    recentCallingUid=10132
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.googlequicksearchbox; callingUid: 10132; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.wallet.service.BIND pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-21s465ms startingBgTimeout=--
    lastActivity=-21s465ms restartTime=-21s465ms createdFromFg=true
    Bindings:
    * IntentBindRecord{8b130dc CREATE}:
      intent={act=com.google.android.gms.wallet.service.BIND pkg=com.google.android.gms}
      binder=android.os.BinderProxy@67d05e5
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{f2578ba ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{2a5dece u0 CR WACT CAPS com.google.android.gms/.wallet.service.PaymentService:@24da7c9 flags=0x1081}
    All Connections:
      ConnectionRecord{2a5dece u0 CR WACT CAPS com.google.android.gms/.wallet.service.PaymentService:@24da7c9 flags=0x1081}

  * ServiceRecord{a4305cb u0 com.android.server.telecom/.components.TelecomService}
    intent={act=com.android.ITelecomService cmp=com.android.server.telecom/.components.TelecomService}
    packageName=com.android.server.telecom
    processName=system
    baseDir=/system/priv-app/Telecom/Telecom.apk
    dataDir=/data/user_de/0/com.android.server.telecom
    app=ProcessRecord{9870635 554:system/1000}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=com.android.ITelecomService cmp=com.android.server.telecom/.components.TelecomService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-27s373ms startingBgTimeout=--
    lastActivity=-27s373ms restartTime=-27s373ms createdFromFg=true
    Bindings:
    * IntentBindRecord{799436b CREATE}:
      intent={act=com.android.ITelecomService cmp=com.android.server.telecom/.components.TelecomService}
      binder=com.android.server.telecom.components.TelecomService$1@e8e7ec8
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{3fd1b61 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{704a945 u0 CR IMP FGS com.android.server.telecom/.components.TelecomService:@18dc5bc flags=0x4000041}
    All Connections:
      ConnectionRecord{704a945 u0 CR IMP FGS com.android.server.telecom/.components.TelecomService:@18dc5bc flags=0x4000041}

  * ServiceRecord{41c043d u0 com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabsConnectionService}
    intent={act=android.support.customtabs.action.CustomTabsService pkg=com.android.chrome}
    packageName=com.android.chrome
    processName=com.android.chrome
    baseDir=/data/app/~~fITDvPUiJ40Uy9KOG4oUlA==/com.android.chrome-0spYTzcLfXv3ncv16vvhcw==/Chrome.apk
    dataDir=/data/user/0/com.android.chrome
    app=ProcessRecord{71f60fe 3181:com.android.chrome/u0a147}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.googlequicksearchbox
    recentCallingUid=10132
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.googlequicksearchbox; callingUid: 10132; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=android.support.customtabs.action.CustomTabsService pkg=com.android.chrome }; code:ACTIVITY_STARTER; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-21s945ms startingBgTimeout=--
    lastActivity=-21s24ms restartTime=-21s866ms createdFromFg=false
    Bindings:
    * IntentBindRecord{f226686 CREATE}:
      intent={act=android.support.customtabs.action.CustomTabsService pkg=com.android.chrome}
      binder=android.os.BinderProxy@e86ab47
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{770bf74 ProcessRecord{e90ab97 1647:com.google.android.youtube/u0a156}}
        Per-process Connections:
          ConnectionRecord{57014b9 u0 CR WPRI com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabsConnectionService:@c66a680 flags=0x21}
    All Connections:
      ConnectionRecord{57014b9 u0 CR WPRI com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabsConnectionService:@c66a680 flags=0x21}

  * ServiceRecord{6affaa8 u0 com.google.android.networkstack/com.android.server.NetworkStackService}
    intent={act=android.net.INetworkStackConnector cmp=com.google.android.networkstack/com.android.server.NetworkStackService}
    packageName=com.google.android.networkstack
    processName=com.android.networkstack.process
    permission=android.permission.MAINLINE_NETWORK_STACK
    baseDir=/system/priv-app/NetworkStackGoogle/NetworkStackGoogle.apk
    dataDir=/data/user_de/0/com.google.android.networkstack
    app=ProcessRecord{d826121 847:com.android.networkstack.process/1073}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.net.INetworkStackConnector cmp=com.google.android.networkstack/com.android.server.NetworkStackService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-27s166ms startingBgTimeout=--
    lastActivity=-27s122ms restartTime=-27s122ms createdFromFg=true
    Bindings:
    * IntentBindRecord{d0f0c9d CREATE}:
      intent={act=android.net.INetworkStackConnector cmp=com.google.android.networkstack/com.android.server.NetworkStackService}
      binder=android.os.BinderProxy@3ae6512
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{1f8b4e3 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{eea4388 u0 CR IMP com.google.android.networkstack/com.android.server.NetworkStackService:@82a232b flags=0x41}
    All Connections:
      ConnectionRecord{eea4388 u0 CR IMP com.google.android.networkstack/com.android.server.NetworkStackService:@82a232b flags=0x41}

  * ServiceRecord{1aea4ff u0 com.google.android.gms/.nearby.sharing.SharingTileService}
    intent={act=android.service.quicksettings.action.QS_TILE cmp=com.google.android.gms/.nearby.sharing.SharingTileService}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    permission=android.permission.BIND_QUICK_SETTINGS_TILE
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mIsAllowedBgActivityStartsByBinding=true
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.systemui
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.systemui; callingUid: 10169; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.quicksettings.action.QS_TILE cmp=com.google.android.gms/.nearby.sharing.SharingTileService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s640ms startingBgTimeout=--
    lastActivity=-24s640ms restartTime=-24s640ms createdFromFg=true
    Bindings:
    * IntentBindRecord{8945ee0 CREATE}:
      intent={act=android.service.quicksettings.action.QS_TILE cmp=com.google.android.gms/.nearby.sharing.SharingTileService}
      binder=android.os.BinderProxy@d54d599
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{389c05e ProcessRecord{6218346 765:com.android.systemui/u0a169}}
        Per-process Connections:
          ConnectionRecord{61bd41e u0 CR WPRI FGSA com.google.android.gms/.nearby.sharing.SharingTileService:@ed7e059 flags=0x2100021}
    All Connections:
      ConnectionRecord{61bd41e u0 CR WPRI FGSA com.google.android.gms/.nearby.sharing.SharingTileService:@ed7e059 flags=0x2100021}

  * ServiceRecord{7269417 u0 com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService}
    intent={act=grpc.io.action.BIND cmp=com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService}
    packageName=com.google.android.googlequicksearchbox
    processName=com.google.android.googlequicksearchbox:search
    permission=com.google.android.apps.nexuslauncher.permission.QSB
    baseDir=/product/priv-app/Velvet/Velvet.apk
    dataDir=/data/user/0/com.google.android.googlequicksearchbox
    app=ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_TOP
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.apps.nexuslauncher
    recentCallingUid=10162
    allowStartForeground=PROC_STATE_TOP
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.apps.nexuslauncher; callingUid: 10162; uidState: TOP ; uidBFSL: [BFSL]; intent: Intent { act=grpc.io.action.BIND cmp=com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService }; code:PROC_STATE_TOP; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-21s323ms startingBgTimeout=--
    lastActivity=-21s323ms restartTime=-21s323ms createdFromFg=true
    Bindings:
    * IntentBindRecord{f7bc3f CREATE}:
      intent={act=grpc.io.action.BIND cmp=com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService}
      binder=android.os.BinderProxy@c90890c
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{e943255 ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}}
        Per-process Connections:
          ConnectionRecord{f403096 u0 CR com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService:@dca83b1 flags=0x1}
    All Connections:
      ConnectionRecord{f403096 u0 CR com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService:@dca83b1 flags=0x1}

  * ServiceRecord{fa8e818 u0 com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService}
    intent={act=android.service.voice.VoiceInteractionService cmp=com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService}
    packageName=com.google.android.googlequicksearchbox
    processName=com.google.android.googlequicksearchbox:interactor
    permission=android.permission.BIND_VOICE_INTERACTION
    baseDir=/product/priv-app/Velvet/Velvet.apk
    dataDir=/data/user/0/com.google.android.googlequicksearchbox
    app=ProcessRecord{c365f4c 1515:com.google.android.googlequicksearchbox:interactor/u0a132}
    mIsAllowedBgActivityStartsByBinding=true
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.voice.VoiceInteractionService cmp=com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s375ms startingBgTimeout=--
    lastActivity=-25s295ms restartTime=-25s295ms createdFromFg=true
    Bindings:
    * IntentBindRecord{f2d846a CREATE}:
      intent={act=android.service.voice.VoiceInteractionService cmp=com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService}
      binder=android.os.BinderProxy@8b5dd5b
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{e4329f8 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{9010823 u0 CR FGS CAPS com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService:@7a2fd52 flags=0x4101001}
    All Connections:
      ConnectionRecord{9010823 u0 CR FGS CAPS com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService:@7a2fd52 flags=0x4101001}

  * ServiceRecord{a9a5d52 u0 com.android.emulator.multidisplay/.MultiDisplayService}
    intent={cmp=com.android.emulator.multidisplay/.MultiDisplayService}
    packageName=com.android.emulator.multidisplay
    processName=com.android.emulator.multidisplay
    baseDir=/system_ext/priv-app/MultiDisplayProvider/MultiDisplayProvider.apk
    dataDir=/data/user/0/com.android.emulator.multidisplay
    app=ProcessRecord{e903e2 1551:com.android.emulator.multidisplay/1000}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.emulator.multidisplay
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.emulator.multidisplay; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.android.emulator.multidisplay/.MultiDisplayService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-21s545ms startingBgTimeout=--
    lastActivity=-21s544ms restartTime=-21s544ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{b362e4b u0 com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl}
    intent={act=android.app.role.RoleControllerService cmp=com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl}
    packageName=com.google.android.permissioncontroller
    processName=com.google.android.permissioncontroller
    baseDir=/apex/com.android.permission/priv-app/GooglePermissionController@340818080/GooglePermissionController.apk
    dataDir=/data/user_de/0/com.google.android.permissioncontroller
    app=ProcessRecord{39b6a51 1318:com.google.android.permissioncontroller/u0a182}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.app.role.RoleControllerService cmp=com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-21s492ms startingBgTimeout=--
    lastActivity=-21s492ms restartTime=-21s492ms createdFromFg=true
    Bindings:
    * IntentBindRecord{7329ed1 CREATE}:
      intent={act=android.app.role.RoleControllerService cmp=com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl}
      binder=android.os.BinderProxy@3977d36
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{d6af437 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{389c31a u0 CR com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl:@1b47dc5 flags=0x1}
    All Connections:
      ConnectionRecord{389c31a u0 CR com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl:@1b47dc5 flags=0x1}

  * ServiceRecord{f0d60c6 u0 com.google.android.bluetooth/com.android.bluetooth.gatt.GattService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.gatt.GattService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    permission=android.permission.ACCESS_BLUETOOTH_SHARE
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.gatt.GattService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s572ms startingBgTimeout=--
    lastActivity=-26s530ms restartTime=-26s572ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{67ceda4 CREATE}:
      intent={act=android.bluetooth.IBluetoothGatt cmp=com.google.android.bluetooth/com.android.bluetooth.gatt.GattService}
      binder=android.os.BinderProxy@471570d
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{dd636c2 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{65fe809 u0 CR IMP com.google.android.bluetooth/com.android.bluetooth.gatt.GattService:@46556a5 flags=0x41}
    All Connections:
      ConnectionRecord{65fe809 u0 CR IMP com.google.android.bluetooth/com.android.bluetooth.gatt.GattService:@46556a5 flags=0x41}

  * ServiceRecord{651c9ed u0 com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService}
    intent={act=android.service.notification.NotificationAssistantService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.BIND_NOTIFICATION_ASSISTANT_SERVICE
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    allowlistManager=true
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.notification.NotificationAssistantService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<770d80d android.bluetooth.adapter.action.BLUETOOTH_ADDRESS_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:20000,callingUid:1002>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-25s204ms startingBgTimeout=--
    lastActivity=-25s204ms restartTime=-25s204ms createdFromFg=true
    Bindings:
    * IntentBindRecord{4f09cd3 CREATE}:
      intent={act=android.service.notification.NotificationAssistantService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService}
      binder=android.os.BinderProxy@86d4010
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{c695709 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{15de004 u0 CR FGS com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService:@e08b417 flags=0x5000001}
    All Connections:
      ConnectionRecord{15de004 u0 CR FGS com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService:@e08b417 flags=0x5000001}

  * ServiceRecord{5536b96 u0 com.google.android.bluetooth/com.android.bluetooth.mcp.McpService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.mcp.McpService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.bluetooth
    recentCallingUid=1002
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.mcp.McpService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s523ms startingBgTimeout=--
    lastActivity=-26s523ms restartTime=-26s523ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2

  * ServiceRecord{1d96208 u0 com.android.ons/.OpportunisticNetworkService}
    intent={cmp=com.android.ons/.OpportunisticNetworkService}
    packageName=com.android.ons
    processName=com.android.phone
    baseDir=/system/priv-app/ONS/ONS.apk
    dataDir=/data/user/0/com.android.ons
    app=ProcessRecord{1598066 937:com.android.phone/1001}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.ons
    recentCallingUid=1001
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.ons; callingUid: 1001; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.android.ons/.OpportunisticNetworkService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<e0125f0 android.intent.action.LOCKED_BOOT_COMPLETED/u0,reasonCode:LOCKED_BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-24s952ms startingBgTimeout=--
    lastActivity=-22s540ms restartTime=-24s951ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=3
 startCommandResult=1

  * ServiceRecord{d32d9c1 u0 com.google.android.gms/.common.stats.GmsCoreStatsService}
    intent={act=com.google.android.gms.common.stats.START cmp=com.google.android.gms/.common.stats.GmsCoreStatsService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.gms
    recentCallingUid=10128
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.common.stats.START cmp=com.google.android.gms/.common.stats.GmsCoreStatsService }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-19s69ms startingBgTimeout=--
    lastActivity=-19s69ms restartTime=-19s69ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{acee643 u0 com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService}
    intent={act=com.android.location.service.ActivityRecognitionProvider cmp=com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService}
    packageName=com.google.android.gms
    processName=com.google.android.gms.persistent
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{ec75c9b 1344:com.google.android.gms.persistent/u0a128}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=com.android.location.service.ActivityRecognitionProvider cmp=com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s710ms startingBgTimeout=--
    lastActivity=-24s710ms restartTime=-24s710ms createdFromFg=true
    Bindings:
    * IntentBindRecord{b54fd0e CREATE}:
      intent={act=com.android.location.service.ActivityRecognitionProvider cmp=com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService}
      binder=android.os.BinderProxy@f1e332f
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{8ce4d3c ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{de2fff2 u0 CR !FG !VIS com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService:@9dbc6fd flags=0x40000005}
    All Connections:
      ConnectionRecord{de2fff2 u0 CR !FG !VIS com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService:@9dbc6fd flags=0x40000005}

  * ServiceRecord{babb70 u0 com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    permission=android.permission.BLUETOOTH_PRIVILEGED
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=10169
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s522ms startingBgTimeout=--
    lastActivity=-26s522ms restartTime=-26s522ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{3c75ac5}:
      intent={act=android.bluetooth.IBluetoothPbap cmp=com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService}
      binder=android.os.BinderProxy@2e7dc1a
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{7e4d34b ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{c5976c6 u0 com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService:@4e144a1 flags=0x0}
    All Connections:
      ConnectionRecord{c5976c6 u0 com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService:@4e144a1 flags=0x0}

  * ServiceRecord{4590c79 u0 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService}
    intent={act=android.service.contentsuggestions.ContentSuggestionsService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.BIND_CONTENT_SUGGESTIONS_SERVICE
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.contentsuggestions.ContentSuggestionsService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s896ms startingBgTimeout=--
    lastActivity=-24s896ms restartTime=-24s896ms createdFromFg=true
    Bindings:
    * IntentBindRecord{bd10128 CREATE}:
      intent={act=android.service.contentsuggestions.ContentSuggestionsService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService}
      binder=android.os.BinderProxy@347de41
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{2979fe6 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{37da540 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService:@efb98c3 flags=0x4001001}
    All Connections:
      ConnectionRecord{37da540 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService:@efb98c3 flags=0x4001001}

  * ServiceRecord{1098db2 u0 com.android.phone/.TelephonyDebugService}
    intent={cmp=com.android.phone/.TelephonyDebugService}
    packageName=com.android.phone
    processName=com.android.phone
    permission=android.permission.DUMP
    baseDir=/system/priv-app/TeleService/TeleService.apk
    dataDir=/data/user_de/0/com.android.phone
    app=ProcessRecord{1598066 937:com.android.phone/1001}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.phone
    recentCallingUid=1001
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.phone; callingUid: 1001; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.android.phone/.TelephonyDebugService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s467ms startingBgTimeout=--
    lastActivity=-26s467ms restartTime=-26s467ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=false callStart=true lastStartId=1
 startCommandResult=1

  * ServiceRecord{ffedc4b u0 com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService}
    intent={cmp=com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService}
    packageName=com.google.android.bluetooth
    processName=com.google.android.bluetooth
    baseDir=/apex/com.android.btservices/app/BluetoothGoogle@340815010/BluetoothGoogle.apk
    dataDir=/data/user_de/0/com.google.android.bluetooth
    app=ProcessRecord{cdc9688 897:com.google.android.bluetooth/1002}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.bluetooth; callingUid: 1002; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { cmp=com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService (has extras) }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<515fbc5 android.bluetooth.adapter.action.STATE_CHANGED/u-1,reasonCode:BLUETOOTH_BROADCAST,duration:10000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:false]
    createTime=-26s526ms startingBgTimeout=--
    lastActivity=-26s526ms restartTime=-26s526ms createdFromFg=true
    startRequested=true delayedStop=false stopIfKilled=true callStart=true lastStartId=1
 startCommandResult=2
    Bindings:
    * IntentBindRecord{f2b5927}:
      intent={act=android.bluetooth.IBluetoothA2dp cmp=com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService}
      binder=android.os.BinderProxy@5c907d4
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{8f31d7d ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{d7b6e8a u0 com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService:@a5cf0f5 flags=0x0}
    All Connections:
      ConnectionRecord{d7b6e8a u0 com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService:@a5cf0f5 flags=0x0}

  * ServiceRecord{e285e1 u0 com.google.android.gms/.icing.service.IndexService}
    intent={act=com.google.android.gms.icing.INDEX_SERVICE pkg=com.google.android.gms}
    packageName=com.google.android.gms
    processName=com.google.android.gms
    baseDir=/product/priv-app/PrebuiltGmsCore/PrebuiltGmsCore.apk
    dataDir=/data/user/0/com.google.android.gms
    app=ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}
    mAllowWhileInUsePermissionInFgsReason=ACTIVITY_STARTER
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.googlequicksearchbox
    recentCallingUid=10132
    allowStartForeground=ACTIVITY_STARTER
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.google.android.gms; callingUid: 10128; uidState: BTOP; uidBFSL: [BFSL]; intent: Intent { act=com.google.android.gms.icing.INDEX_SERVICE pkg=com.google.android.gms }; code:ACTIVITY_STARTER; tempAllowListReason:<,reasonCode:SYSTEM_ALLOW_LISTED,duration:9223372036854775807,callingUid:-1>; targetSdkVersion:33; callerTargetSdkVersion:33; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-22s589ms startingBgTimeout=--
    lastActivity=-21s348ms restartTime=-22s589ms createdFromFg=true
    Bindings:
    * IntentBindRecord{e2dd472 CREATE}:
      intent={act=com.google.android.gms.icing.INDEX_SERVICE pkg=com.google.android.gms}
      binder=android.os.BinderProxy@26a60c3
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{a98cd40 ProcessRecord{8c56a26 1659:com.google.android.gms/u0a128}}
        Per-process Connections:
          ConnectionRecord{4550348 u0 CR WACT CAPS com.google.android.gms/.icing.service.IndexService:@b0d09eb flags=0x1081}
      * Client AppBindRecord{1191479 ProcessRecord{959abad 1632:com.google.android.googlequicksearchbox:search/u0a132}}
        Per-process Connections:
          ConnectionRecord{8be4109 u0 CR WACT CAPS com.google.android.gms/.icing.service.IndexService:@2bb9210 flags=0x1081}
    All Connections:
      ConnectionRecord{8be4109 u0 CR WACT CAPS com.google.android.gms/.icing.service.IndexService:@2bb9210 flags=0x1081}
      ConnectionRecord{4550348 u0 CR WACT CAPS com.google.android.gms/.icing.service.IndexService:@b0d09eb flags=0x1081}

  * ServiceRecord{1012dc5 u0 com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService}
    intent={act=android.intent.action.QUICKSTEP_SERVICE pkg=com.google.android.apps.nexuslauncher}
    packageName=com.google.android.apps.nexuslauncher
    processName=com.google.android.apps.nexuslauncher
    permission=android.permission.STATUS_BAR_SERVICE
    baseDir=/system_ext/priv-app/NexusLauncherRelease/NexusLauncherRelease.apk
    dataDir=/data/user/0/com.google.android.apps.nexuslauncher
    app=ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.google.android.apps.nexuslauncher
    recentCallingUid=10162
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.systemui; callingUid: 10169; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.intent.action.QUICKSTEP_SERVICE pkg=com.google.android.apps.nexuslauncher }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s787ms startingBgTimeout=--
    lastActivity=-26s719ms restartTime=-26s719ms createdFromFg=true
    Bindings:
    * IntentBindRecord{a80c5be CREATE}:
      intent={act=android.intent.action.QUICKSTEP_SERVICE pkg=com.google.android.apps.nexuslauncher}
      binder=android.os.BinderProxy@408461f
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{7dd7d6c ProcessRecord{6218346 765:com.android.systemui/u0a169}}
        Per-process Connections:
          ConnectionRecord{75bf569 u0 CR FGSA com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@4e7dbf0 flags=0x2000001}
    * IntentBindRecord{30d7f35}:
      intent={cmp=com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService}
      binder=android.os.BinderProxy@408461f
      requested=true received=true hasBound=false doRebind=false
      * Client AppBindRecord{17f7fca ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}}
        Per-process Connections:
          ConnectionRecord{90fc94e u0 com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@adaac49 flags=0x0}
    All Connections:
      ConnectionRecord{75bf569 u0 CR FGSA com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@4e7dbf0 flags=0x2000001}
      ConnectionRecord{90fc94e u0 com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@adaac49 flags=0x0}

  * ServiceRecord{5ac8398 u0 com.google.android.partnersetup/.PhenotypeJobService}
    intent={cmp=com.google.android.partnersetup/.PhenotypeJobService}
    packageName=com.google.android.partnersetup
    processName=com.google.android.partnersetup
    permission=android.permission.BIND_JOB_SERVICE
    baseDir=/product/priv-app/PartnerSetupPrebuilt/PartnerSetupPrebuilt.apk
    dataDir=/data/user/0/com.google.android.partnersetup
    app=ProcessRecord{8926215 3483:com.google.android.partnersetup/u0a120}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { flg=0x4 cmp=com.google.android.partnersetup/.PhenotypeJobService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:33; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-20s659ms startingBgTimeout=--
    lastActivity=-20s659ms restartTime=-20s659ms createdFromFg=true
    Bindings:
    * IntentBindRecord{c75253b CREATE}:
      intent={flg=0x4 cmp=com.google.android.partnersetup/.PhenotypeJobService}
      binder=android.os.BinderProxy@5db0458
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{da3d9b1 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{f2c197b u0 CR !FG !PRCP com.google.android.partnersetup/.PhenotypeJobService:@8249d0a flags=0x8105}
    All Connections:
      ConnectionRecord{f2c197b u0 CR !FG !PRCP com.google.android.partnersetup/.PhenotypeJobService:@8249d0a flags=0x8105}

  * ServiceRecord{a693bad u0 com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService}
    intent={act=android.telephony.CellBroadcastService pkg=com.google.android.cellbroadcastservice}
    packageName=com.google.android.cellbroadcastservice
    processName=com.android.networkstack.process
    permission=android.permission.BIND_CELL_BROADCAST_SERVICE
    baseDir=/apex/com.android.cellbroadcast/priv-app/GoogleCellBroadcastServiceModule@340818080/GoogleCellBroadcastServiceModule.apk
    dataDir=/data/user_de/0/com.google.android.cellbroadcastservice
    app=ProcessRecord{d826121 847:com.android.networkstack.process/1073}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=com.android.phone
    recentCallingUid=1001
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: com.android.phone; callingUid: 1001; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.telephony.CellBroadcastService pkg=com.google.android.cellbroadcastservice }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<null>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-26s587ms startingBgTimeout=--
    lastActivity=-26s586ms restartTime=-26s586ms createdFromFg=true
    Bindings:
    * IntentBindRecord{afdce96 CREATE}:
      intent={act=android.telephony.CellBroadcastService pkg=com.google.android.cellbroadcastservice}
      binder=android.os.BinderProxy@106da17
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{b280e04 ProcessRecord{1598066 937:com.android.phone/1001}}
        Per-process Connections:
          ConnectionRecord{7c900c4 u0 CR com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:@81cdfd7 flags=0x1}
          ConnectionRecord{80ae5a9 u0 CR com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:@81cdfd7 flags=0x1}
    All Connections:
      ConnectionRecord{7c900c4 u0 CR com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:@81cdfd7 flags=0x1}
      ConnectionRecord{80ae5a9 u0 CR com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:@81cdfd7 flags=0x1}

  * ServiceRecord{49a4873 u0 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService}
    intent={act=android.service.search.SearchUiService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService}
    packageName=com.google.android.as
    processName=com.google.android.as
    permission=android.permission.MANAGE_SEARCH_UI
    baseDir=/product/priv-app/DevicePersonalizationPrebuiltPixel2021/DevicePersonalizationPrebuiltPixel2021.apk
    dataDir=/data/user/0/com.google.android.as
    app=ProcessRecord{731422c 1503:com.google.android.as/u0a131}
    mAllowWhileInUsePermissionInFgsReason=PROC_STATE_PERSISTENT
    allowUiJobScheduling=false
    recentCallingPackage=android
    recentCallingUid=1000
    allowStartForeground=PROC_STATE_PERSISTENT
    startForegroundCount=0
    infoAllowStartForeground=[callingPackage: android; callingUid: 1000; uidState: PER ; uidBFSL: [BFSL]; intent: Intent { act=android.service.search.SearchUiService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService }; code:PROC_STATE_PERSISTENT; tempAllowListReason:<d156bdd android.intent.action.BOOT_COMPLETED/u0,reasonCode:BOOT_COMPLETED,duration:20000,callingUid:1000>; targetSdkVersion:34; callerTargetSdkVersion:34; startForegroundCount:0; bindFromPackage:null: isBindService:true]
    createTime=-24s264ms startingBgTimeout=--
    lastActivity=-24s264ms restartTime=-24s264ms createdFromFg=true
    Bindings:
    * IntentBindRecord{f6b5fed CREATE}:
      intent={act=android.service.search.SearchUiService cmp=com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService}
      binder=android.os.BinderProxy@6403e22
      requested=true received=true hasBound=true doRebind=false
      * Client AppBindRecord{c9500b3 ProcessRecord{9870635 554:system/1000}}
        Per-process Connections:
          ConnectionRecord{2f2cce2 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService:@3a7f1ad flags=0x4001001}
    All Connections:
      ConnectionRecord{2f2cce2 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService:@3a7f1ad flags=0x4001001}

  Connection bindings to services:
  * ConnectionRecord{a5243f9 u0 CR com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService:@430ac0 flags=0x1}
    binding=AppBindRecord{4f5dabe com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.SetupParametersService:com.google.android.devicelockcontroller}
    conn=android.os.BinderProxy@430ac0 flags=0x1
  * ConnectionRecord{d08aa70 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@47b4b3 flags=0x1081}
    binding=AppBindRecord{d698538 com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@47b4b3 flags=0x1081
  * ConnectionRecord{307b54a u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService:@671ab5 flags=0x0}
    binding=AppBindRecord{f085143 com.google.android.bluetooth/com.android.bluetooth.hid.HidHostService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@671ab5 flags=0x0
  * ConnectionRecord{7415b60 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@81d363 flags=0x1081}
    binding=AppBindRecord{5b5f942 com.google.android.gms/.chimera.GmsApiService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@81d363 flags=0x1081
  * ConnectionRecord{e76200 u0 com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService:@b75083 flags=0x0}
    binding=AppBindRecord{ad5f87f com.google.android.bluetooth/com.android.bluetooth.hearingaid.HearingAidService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@b75083 flags=0x0
  * ConnectionRecord{99f25d2 u0 CR FGS !VIS com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService:@bb585d flags=0x44000001}
    binding=AppBindRecord{7df7158 com.google.android.apps.messaging/com.google.android.ims.binding.SystemBindingService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@bb585d flags=0x44000001
  * ConnectionRecord{b8484c9 u0 CR IMP com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService:@e58cd0 flags=0x41}
    binding=AppBindRecord{61abe0 com.google.android.networkstack.tethering/com.android.networkstack.tethering.TetheringService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@e58cd0 flags=0x41
  * ConnectionRecord{fe91366 u0 CR !FG !VIS com.google.android.gms/.location.geocode.GeocodeService:@f0efc1 flags=0x40000005}
    binding=AppBindRecord{66e7bb8 com.google.android.gms/.location.geocode.GeocodeService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@f0efc1 flags=0x40000005
  * ConnectionRecord{cbce9d3 u0 CR WACT CAPS com.google.android.gms/com.google.android.location.reporting.service.ReportingAndroidService:@11f97c2 flags=0x1081}
    binding=AppBindRecord{9554881 com.google.android.gms/com.google.android.location.reporting.service.ReportingAndroidService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@11f97c2 flags=0x1081
  * ConnectionRecord{13c619 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@12ec160 flags=0x1081}
    binding=AppBindRecord{2bd3a19 com.google.android.gms/.chimera.GmsBoundBrokerService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@12ec160 flags=0x1081
  * ConnectionRecord{ead32d9 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@14ae920 flags=0x1081}
    binding=AppBindRecord{577c83d com.google.android.gms/.chimera.PersistentBoundBrokerService:com.google.android.gms}
    conn=android.os.BinderProxy@14ae920 flags=0x1081
  * ConnectionRecord{704a945 u0 CR IMP FGS com.android.server.telecom/.components.TelecomService:@18dc5bc flags=0x4000041}
    binding=AppBindRecord{3fd1b61 com.android.server.telecom/.components.TelecomService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@18dc5bc flags=0x4000041
  * ConnectionRecord{57e424a u0 CR FGSA UI CAPS com.android.systemui/.wallpapers.ImageWallpaper:@19bbbb5 flags=0x22001001}
    binding=AppBindRecord{4831515 com.android.systemui/.wallpapers.ImageWallpaper:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@19bbbb5 flags=0x22001001
  * ConnectionRecord{389c31a u0 CR com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl:@1b47dc5 flags=0x1}
    binding=AppBindRecord{d6af437 com.google.android.permissioncontroller/com.android.permissioncontroller.role.service.RoleControllerServiceImpl:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@1b47dc5 flags=0x1
  * ConnectionRecord{40c397b u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@1f13d0a flags=0x1081}
    binding=AppBindRecord{9994322 com.google.android.gms/.chimera.PersistentApiService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@1f13d0a flags=0x1081
  * ConnectionRecord{deaba15 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@21157cc flags=0x1081}
    binding=AppBindRecord{75d524e com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.gms}
    conn=android.os.BinderProxy@21157cc flags=0x1081
  * ConnectionRecord{86ac434 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@246cb07 flags=0x1081}
    binding=AppBindRecord{d864b04 com.google.android.gms/.chimera.PersistentApiService:com.google.android.partnersetup}
    conn=android.os.BinderProxy@246cb07 flags=0x1081
  * ConnectionRecord{619b14c u0 CR !FG !VIS com.google.android.gms/.geotimezone.GeoTimeZoneService:@2475d7f flags=0x40000005}
    binding=AppBindRecord{140455a com.google.android.gms/.geotimezone.GeoTimeZoneService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@2475d7f flags=0x40000005
  * ConnectionRecord{2a5dece u0 CR WACT CAPS com.google.android.gms/.wallet.service.PaymentService:@24da7c9 flags=0x1081}
    binding=AppBindRecord{f2578ba com.google.android.gms/.wallet.service.PaymentService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@24da7c9 flags=0x1081
  * ConnectionRecord{7bafda5 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps:@2512f9c flags=0x1081}
    binding=AppBindRecord{5dd41c3 com.google.android.gms/.chimera.PersistentApiServiceNoInstantApps:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@2512f9c flags=0x1081
  * ConnectionRecord{1fbce5d u0 CR com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService:@2747034 flags=0x1}
    binding=AppBindRecord{2ab2d3f com.google.android.as.oss/com.google.android.apps.miphone.astrea.grpc.AstreaGrpcService:com.google.android.as}
    conn=android.os.BinderProxy@2747034 flags=0x1
  * ConnectionRecord{87369d7 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@287c556 flags=0x1081}
    binding=AppBindRecord{4862513 com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@287c556 flags=0x1081
  * ConnectionRecord{8be4109 u0 CR WACT CAPS com.google.android.gms/.icing.service.IndexService:@2bb9210 flags=0x1081}
    binding=AppBindRecord{1191479 com.google.android.gms/.icing.service.IndexService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@2bb9210 flags=0x1081
  * ConnectionRecord{9d682ce u0 CR com.google.android.gms/.ads.identifier.service.AdvertisingIdService:@30a5bc9 flags=0x1}
    binding=AppBindRecord{f981ee5 com.google.android.gms/.ads.identifier.service.AdvertisingIdService:com.google.android.apps.youtube.music}
    conn=android.os.BinderProxy@30a5bc9 flags=0x1
  * ConnectionRecord{321179a u0 CR !FG !VIS com.google.android.gms/com.google.android.location.fused.FusedLocationService:@37a5445 flags=0x40000005}
    binding=AppBindRecord{149d03e com.google.android.gms/com.google.android.location.fused.FusedLocationService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@37a5445 flags=0x40000005
  * ConnectionRecord{ad52841 u0 CR FGS com.google.android.gms/.chimera.PersistentBoundBrokerService:@37d3328 flags=0x4000001}
    binding=AppBindRecord{5e6bdc9 com.google.android.gms/.chimera.PersistentBoundBrokerService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@37d3328 flags=0x4000001
  * ConnectionRecord{c4eaa6 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@3849c01 flags=0x1081}
    binding=AppBindRecord{54796e9 com.google.android.gms/.chimera.PersistentApiService:com.google.android.dialer}
    conn=android.os.BinderProxy@3849c01 flags=0x1081
  * ConnectionRecord{2f2cce2 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService:@3a7f1ad flags=0x4001001}
    binding=AppBindRecord{c9500b3 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSearchUiService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@3a7f1ad flags=0x4001001
  * ConnectionRecord{9e48662 u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService:@3cea12d flags=0x1}
    binding=AppBindRecord{5c0944b com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiAugmentedAutofillService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@3cea12d flags=0x1
  * ConnectionRecord{a2bc51e u0 CR com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService:@45cf559 flags=0x1}
    binding=AppBindRecord{6be0654 com.google.android.devicelockcontroller/com.android.devicelockcontroller.storage.GlobalParametersService:com.google.android.devicelockcontroller}
    conn=android.os.BinderProxy@45cf559 flags=0x1
  * ConnectionRecord{82a5a7a u0 CR IMP com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService:@46556a5 flags=0x41}
    binding=AppBindRecord{1a186b9 com.google.android.bluetooth/com.android.bluetooth.btservice.AdapterService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@46556a5 flags=0x41
  * ConnectionRecord{65fe809 u0 CR IMP com.google.android.bluetooth/com.android.bluetooth.gatt.GattService:@46556a5 flags=0x41}
    binding=AppBindRecord{dd636c2 com.google.android.bluetooth/com.android.bluetooth.gatt.GattService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@46556a5 flags=0x41
  * ConnectionRecord{afd4222 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@4a9f3ed flags=0x1081}
    binding=AppBindRecord{f310832 com.google.android.gms/.chimera.PersistentBoundBrokerService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@4a9f3ed flags=0x1081
  * ConnectionRecord{edcd6bf u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@4c0b4de flags=0x1081}
    binding=AppBindRecord{eff6fe1 com.google.android.gms/.chimera.GmsBoundBrokerService:com.google.android.apps.messaging}
    conn=android.os.BinderProxy@4c0b4de flags=0x1081
  * ConnectionRecord{44c5051 u0 CR !FG !VIS com.google.android.gms/com.google.android.location.network.NetworkLocationService:@4d6b178 flags=0x40000005}
    binding=AppBindRecord{31d5bd6 com.google.android.gms/com.google.android.location.network.NetworkLocationService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@4d6b178 flags=0x40000005
  * ConnectionRecord{c5976c6 u0 com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService:@4e144a1 flags=0x0}
    binding=AppBindRecord{7e4d34b com.google.android.bluetooth/com.android.bluetooth.pbap.BluetoothPbapService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@4e144a1 flags=0x0
  * ConnectionRecord{75bf569 u0 CR FGSA com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@4e7dbf0 flags=0x2000001}
    binding=AppBindRecord{7dd7d6c com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:com.android.systemui}
    conn=android.os.BinderProxy@4e7dbf0 flags=0x2000001
  * ConnectionRecord{3ff0d65 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsBoundBrokerService:@560a65c flags=0x1081}
    binding=AppBindRecord{f808792 com.google.android.gms/.chimera.GmsBoundBrokerService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@560a65c flags=0x1081
  * ConnectionRecord{1d44de8 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@5665b0b flags=0x1081}
    binding=AppBindRecord{1acf2fc com.google.android.gms/.chimera.PersistentBoundBrokerService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@5665b0b flags=0x1081
  * ConnectionRecord{b1d293e u0 CR !FG !VIS com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:@5a2d5f9 flags=0x40000005}
    binding=AppBindRecord{1cb29b0 com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@5a2d5f9 flags=0x40000005
  * ConnectionRecord{d5a01d u0 CR !FG !PRCP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService:@5af70f4 flags=0x8105}
    binding=AppBindRecord{cf6d00d com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@5af70f4 flags=0x8105
  * ConnectionRecord{ab3c705 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@5b3c27c flags=0x1081}
    binding=AppBindRecord{59f1370 com.google.android.gms/.chimera.PersistentApiService:com.google.android.gm}
    conn=android.os.BinderProxy@5b3c27c flags=0x1081
  * ConnectionRecord{1bdf4c4 u0 CR com.android.systemui/.keyguard.KeyguardService:@5bd23d7 flags=0x1}
    binding=AppBindRecord{ebbb236 com.android.systemui/.keyguard.KeyguardService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@5bd23d7 flags=0x1
  * ConnectionRecord{5e9f378 u0 CR WPRI FGSA com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService:@5fbdcdb flags=0x2000021}
    binding=AppBindRecord{57d44ac com.google.android.permissioncontroller/com.android.permissioncontroller.permission.service.v33.SafetyCenterQsTileService:com.android.systemui}
    conn=android.os.BinderProxy@5fbdcdb flags=0x2000021
  * ConnectionRecord{bd0b45f u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:@60904fe flags=0x1}
    binding=AppBindRecord{26e04d4 com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:com.google.android.as}
    conn=android.os.BinderProxy@60904fe flags=0x1
  * ConnectionRecord{5770758 u0 CR com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService:@6c3543b flags=0x1}
    binding=AppBindRecord{534badd com.google.android.googlequicksearchbox/com.google.frameworks.client.data.android.server.tiktok.InteractorProcessEndpointService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@6c3543b flags=0x1
  * ConnectionRecord{b3db3bf u0 CR com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService:@6d6e5de flags=0x1}
    binding=AppBindRecord{c28081c com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nga.engine.viss.NgaService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@6d6e5de flags=0x1
  * ConnectionRecord{4d48781 u0 CR FGS com.google.android.gms/.chimera.PersistentBoundBrokerService:@6ed8768 flags=0x4000001}
    binding=AppBindRecord{e7b17a6 com.google.android.gms/.chimera.PersistentBoundBrokerService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@6ed8768 flags=0x4000001
  * ConnectionRecord{3678c83 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@6f95732 flags=0x1}
    binding=AppBindRecord{b60fc47 com.google.android.apps.messaging/com.google.android.ims.service.JibeService:com.google.android.apps.messaging}
    conn=android.os.BinderProxy@6f95732 flags=0x1
  * ConnectionRecord{9010823 u0 CR FGS CAPS com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService:@7a2fd52 flags=0x4101001}
    binding=AppBindRecord{e4329f8 com.google.android.googlequicksearchbox/com.google.android.voiceinteraction.GsaVoiceInteractionService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@7a2fd52 flags=0x4101001
  * ConnectionRecord{9471df u0 com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService:@7b7487e flags=0x0}
    binding=AppBindRecord{6a4aa3c com.google.android.bluetooth/com.android.bluetooth.hfp.HeadsetService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@7b7487e flags=0x0
  * ConnectionRecord{9aff11b u0 CR !FG !PRCP com.google.android.gms/.chimera.container.ConfigService:@7b88f2a flags=0x105}
    binding=AppBindRecord{d0e72c1 com.google.android.gms/.chimera.container.ConfigService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@7b88f2a flags=0x105
  * ConnectionRecord{dcd1163 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@7e06392 flags=0x1081}
    binding=AppBindRecord{539f69c com.google.android.gms/.chimera.PersistentApiService:com.google.android.gms}
    conn=android.os.BinderProxy@7e06392 flags=0x1081
  * ConnectionRecord{2cc7e8e u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService:@7efee89 flags=0x4001001}
    binding=AppBindRecord{6840741 com.google.android.as/com.google.android.apps.miphone.aiai.captions.SystemCaptionsManagerService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@7efee89 flags=0x4001001
  * ConnectionRecord{7c900c4 u0 CR com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:@81cdfd7 flags=0x1}
    binding=AppBindRecord{b280e04 com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:com.android.phone}
    conn=android.os.BinderProxy@81cdfd7 flags=0x1
  * ConnectionRecord{80ae5a9 u0 CR com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:@81cdfd7 flags=0x1}
    binding=AppBindRecord{b280e04 com.google.android.cellbroadcastservice/com.android.cellbroadcastservice.DefaultCellBroadcastService:com.android.phone}
    conn=android.os.BinderProxy@81cdfd7 flags=0x1
  * ConnectionRecord{f2c197b u0 CR !FG !PRCP com.google.android.partnersetup/.PhenotypeJobService:@8249d0a flags=0x8105}
    binding=AppBindRecord{da3d9b1 com.google.android.partnersetup/.PhenotypeJobService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@8249d0a flags=0x8105
  * ConnectionRecord{eea4388 u0 CR IMP com.google.android.networkstack/com.android.server.NetworkStackService:@82a232b flags=0x41}
    binding=AppBindRecord{1f8b4e3 com.google.android.networkstack/com.android.server.NetworkStackService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@82a232b flags=0x41
  * ConnectionRecord{297eb9 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@82bb103 flags=0x1081}
    binding=AppBindRecord{10be983 com.google.android.gms/.chimera.PersistentBoundBrokerService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@82bb103 flags=0x1081
  * ConnectionRecord{6ec1453 u0 CR com.android.phone/com.android.internal.telephony.CellularNetworkService:@83edc42 flags=0x1}
    binding=AppBindRecord{ed4c0f7 com.android.phone/com.android.internal.telephony.CellularNetworkService:com.android.phone}
    conn=android.os.BinderProxy@83edc42 flags=0x1
  * ConnectionRecord{97109be u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService:@84fe879 flags=0x4001001}
    binding=AppBindRecord{88c2714 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiPredictionService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@84fe879 flags=0x4001001
  * ConnectionRecord{6f5f7a0 u0 CR IMP com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl:@87238a3 flags=0x41}
    binding=AppBindRecord{c3340a2 com.google.android.providers.media.module/com.android.providers.media.fuse.ExternalStorageServiceImpl:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@87238a3 flags=0x41
  * ConnectionRecord{8258cd4 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@8c2d227 flags=0x1}
    binding=AppBindRecord{b60fc47 com.google.android.apps.messaging/com.google.android.ims.service.JibeService:com.google.android.apps.messaging}
    conn=android.os.BinderProxy@8c2d227 flags=0x1
  * ConnectionRecord{f56906a u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@8c9ee55 flags=0x1081}
    binding=AppBindRecord{dc9040b com.google.android.gms/.chimera.PersistentBoundBrokerService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@8c9ee55 flags=0x1081
  * ConnectionRecord{76b3c49 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@8de7250 flags=0x1081}
    binding=AppBindRecord{733eb17 com.google.android.gms/.chimera.PersistentApiService:com.google.android.apps.messaging}
    conn=android.os.BinderProxy@8de7250 flags=0x1081
  * ConnectionRecord{5889355 u0 CR com.android.phone/com.android.internal.telephony.data.CellularDataService:@905ce0c flags=0x1}
    binding=AppBindRecord{9d1d269 com.android.phone/com.android.internal.telephony.data.CellularDataService:com.android.phone}
    conn=android.os.BinderProxy@905ce0c flags=0x1
  * ConnectionRecord{5fd88f2 u0 CR com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:@916d3fd flags=0x1}
    binding=AppBindRecord{26e04d4 com.google.android.as/com.google.android.apps.miphone.aiai.common.superpacks.impl.AiAiSuperpacksService:com.google.android.as}
    conn=android.os.BinderProxy@916d3fd flags=0x1
  * ConnectionRecord{bafa55f u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@93919fe flags=0x1081}
    binding=AppBindRecord{e27b802 com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.gms}
    conn=android.os.BinderProxy@93919fe flags=0x1081
  * ConnectionRecord{7c8bde2 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@94b06ad flags=0x1081}
    binding=AppBindRecord{147d34 com.google.android.gms/.chimera.PersistentApiService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@94b06ad flags=0x1081
  * ConnectionRecord{cc7b321 u0 CR FGSA UI CAPS com.android.systemui/.wallpapers.ImageWallpaper:@9899d88 flags=0x22001001}
    binding=AppBindRecord{4831515 com.android.systemui/.wallpapers.ImageWallpaper:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@9899d88 flags=0x22001001
  * ConnectionRecord{3462d95 u0 CR FGS CAPS com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl:@9ac694c flags=0x4001001}
    binding=AppBindRecord{1d9e297 com.google.android.ext.services/android.ext.services.autofill.InlineSuggestionRenderServiceImpl:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@9ac694c flags=0x4001001
  * ConnectionRecord{de2fff2 u0 CR !FG !VIS com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService:@9dbc6fd flags=0x40000005}
    binding=AppBindRecord{8ce4d3c com.google.android.gms/com.google.android.location.internal.server.HardwareArProviderService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@9dbc6fd flags=0x40000005
  * ConnectionRecord{96d3eb0 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@a4cf1f3 flags=0x1081}
    binding=AppBindRecord{8cd1daa com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.apps.messaging}
    conn=android.os.BinderProxy@a4cf1f3 flags=0x1081
  * ConnectionRecord{4cb207b u0 CR IMP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@a4f600a flags=0x41}
    binding=AppBindRecord{a38baf com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:com.google.android.apps.nexuslauncher}
    activity=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
    conn=android.os.BinderProxy@a4f600a flags=0x41
  * ConnectionRecord{a348853 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService:@a50a042 flags=0x4001001}
    binding=AppBindRecord{f00057b com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentCaptureService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@a50a042 flags=0x4001001
  * ConnectionRecord{d7b6e8a u0 com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService:@a5cf0f5 flags=0x0}
    binding=AppBindRecord{8f31d7d com.google.android.bluetooth/com.android.bluetooth.a2dp.A2dpService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@a5cf0f5 flags=0x0
  * ConnectionRecord{3fc13e6 u0 CR !FG !PRCP com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator:@a65a241 flags=0x105}
    binding=AppBindRecord{367ebb5 com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@a65a241 flags=0x105
  * ConnectionRecord{90fc94e u0 com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@adaac49 flags=0x0}
    binding=AppBindRecord{17f7fca com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:com.google.android.apps.nexuslauncher}
    activity=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
    conn=android.os.BinderProxy@adaac49 flags=0x0
  * ConnectionRecord{813f26 u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@ae37281 flags=0x1081}
    binding=AppBindRecord{52fbcb7 com.google.android.gms/.chimera.GmsApiService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@ae37281 flags=0x1081
  * ConnectionRecord{7f18fb7 u0 CR com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService:@af156b6 flags=0x1}
    binding=AppBindRecord{9c0fa82 com.google.android.gms/com.google.location.nearby.direct.service.NearbyDirectService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@af156b6 flags=0x1
  * ConnectionRecord{47125df u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService:@b064c7e flags=0x4001001}
    binding=AppBindRecord{4415835 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiSmartspaceService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@b064c7e flags=0x4001001
  * ConnectionRecord{4550348 u0 CR WACT CAPS com.google.android.gms/.icing.service.IndexService:@b0d09eb flags=0x1081}
    binding=AppBindRecord{a98cd40 com.google.android.gms/.icing.service.IndexService:com.google.android.gms}
    conn=android.os.BinderProxy@b0d09eb flags=0x1081
  * ConnectionRecord{80d5c3d u0 CR WACT CAPS com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:@b7e0994 flags=0x1081}
    binding=AppBindRecord{1b53e2d com.google.android.gms/com.google.android.location.internal.GoogleLocationManagerService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@b7e0994 flags=0x1081
  * ConnectionRecord{8a53702 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@b97304d flags=0x1081}
    binding=AppBindRecord{823ff6f com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@b97304d flags=0x1081
  * ConnectionRecord{c2ece81 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@bb88a68 flags=0x1081}
    binding=AppBindRecord{dd4f911 com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.gm}
    conn=android.os.BinderProxy@bb88a68 flags=0x1081
  * ConnectionRecord{a4694c6 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentBoundBrokerService:@bf81aa1 flags=0x1081}
    binding=AppBindRecord{9bd6b8a com.google.android.gms/.chimera.PersistentBoundBrokerService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@bf81aa1 flags=0x1081
  * ConnectionRecord{eea143 u0 CR android/.hardware.location.GeofenceHardwareService:@c10c6f2 flags=0x1}
    binding=AppBindRecord{c6f9220 android/.hardware.location.GeofenceHardwareService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@c10c6f2 flags=0x1
  * ConnectionRecord{57014b9 u0 CR WPRI com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabsConnectionService:@c66a680 flags=0x21}
    binding=AppBindRecord{770bf74 com.android.chrome/org.chromium.chrome.browser.customtabs.CustomTabsConnectionService:com.google.android.youtube}
    conn=android.os.BinderProxy@c66a680 flags=0x21
  * ConnectionRecord{de257ee u0 com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService:@c79d169 flags=0x0}
    binding=AppBindRecord{a132bc8 com.google.android.bluetooth/com.android.bluetooth.hid.HidDeviceService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@c79d169 flags=0x0
  * ConnectionRecord{7bb57a7 u0 CR WPRI com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@c868866 flags=0x21}
    binding=AppBindRecord{a38baf com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:com.google.android.apps.nexuslauncher}
    conn=android.os.BinderProxy@c868866 flags=0x21
  * ConnectionRecord{500a7fc u0 CR FGS !PRCP com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService:@d0a40ef flags=0x5000101}
    binding=AppBindRecord{be083c6 com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationListenerService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@d0a40ef flags=0x5000101
  * ConnectionRecord{44994c8 u0 CR WACT CAPS com.google.android.gms/.droidguard.DroidGuardService:@d9af16b flags=0x1081}
    binding=AppBindRecord{8a7cd10 com.google.android.gms/.droidguard.DroidGuardService:com.google.android.gms}
    conn=android.os.BinderProxy@d9af16b flags=0x1081
  * ConnectionRecord{1a8a33e u0 com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService:@da7f7f9 flags=0x0}
    binding=AppBindRecord{9ad6e9a com.google.android.bluetooth/com.android.bluetooth.map.BluetoothMapService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@da7f7f9 flags=0x0
  * ConnectionRecord{6d327cc u0 CR !FG IMPB SLTA !VIS com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME:@dba9dff flags=0x40880005}
    binding=AppBindRecord{935e14f com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@dba9dff flags=0x40880005
  * ConnectionRecord{f403096 u0 CR com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService:@dca83b1 flags=0x1}
    binding=AppBindRecord{e943255 com.google.android.googlequicksearchbox/com.google.android.apps.search.googleapp.search.suggest.plugins.onesearch.server.OneSearchSuggestService:com.google.android.apps.nexuslauncher}
    conn=android.os.BinderProxy@dca83b1 flags=0x1
  * ConnectionRecord{15de004 u0 CR FGS com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService:@e08b417 flags=0x5000001}
    binding=AppBindRecord{c695709 com.google.android.as/com.google.android.apps.miphone.aiai.common.notification.service.AiAiNotificationAssistantService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@e08b417 flags=0x5000001
  * ConnectionRecord{1034e93 u0 CR FGS !PRCP com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener:@e219782 flags=0x5000101}
    binding=AppBindRecord{af273ab com.google.android.apps.nexuslauncher/com.android.launcher3.notification.NotificationListener:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@e219782 flags=0x5000101
  * ConnectionRecord{6571060 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@e393c63 flags=0x1081}
    binding=AppBindRecord{70221b3 com.google.android.gms/.chimera.PersistentApiService:com.google.android.inputmethod.latin}
    conn=android.os.BinderProxy@e393c63 flags=0x1081
  * ConnectionRecord{4f108b u0 CR WACT CAPS com.google.android.gms/.chimera.GmsApiService:@e4bc65a flags=0x1081}
    binding=AppBindRecord{bad978c com.google.android.gms/.chimera.GmsApiService:com.google.android.googlequicksearchbox:search}
    conn=android.os.BinderProxy@e4bc65a flags=0x1081
  * ConnectionRecord{dd94073 u0 CR com.google.android.apps.messaging/com.google.android.ims.service.JibeService:@e72a4e2 flags=0x1}
    binding=AppBindRecord{b60fc47 com.google.android.apps.messaging/com.google.android.ims.service.JibeService:com.google.android.apps.messaging}
    conn=android.os.BinderProxy@e72a4e2 flags=0x1
  * ConnectionRecord{61bd41e u0 CR WPRI FGSA com.google.android.gms/.nearby.sharing.SharingTileService:@ed7e059 flags=0x2100021}
    binding=AppBindRecord{389c05e com.google.android.gms/.nearby.sharing.SharingTileService:com.android.systemui}
    conn=android.os.BinderProxy@ed7e059 flags=0x2100021
  * ConnectionRecord{13c5585 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@ee37afc flags=0x1081}
    binding=AppBindRecord{62158ed com.google.android.gms/.chimera.PersistentApiService:com.google.android.tts}
    conn=android.os.BinderProxy@ee37afc flags=0x1081
  * ConnectionRecord{f87a951 u0 CR WACT CAPS com.google.android.gms/.icing.service.AppIndexingService:@ef3ce78 flags=0x1081}
    binding=AppBindRecord{708696a com.google.android.gms/.icing.service.AppIndexingService:com.google.android.gms}
    conn=android.os.BinderProxy@ef3ce78 flags=0x1081
  * ConnectionRecord{37da540 u0 CR FGS CAPS com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService:@efb98c3 flags=0x4001001}
    binding=AppBindRecord{2979fe6 com.google.android.as/com.google.android.apps.miphone.aiai.app.AiAiContentSuggestionsService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@efb98c3 flags=0x4001001
  * ConnectionRecord{fc63bf0 u0 CR WACT CAPS com.google.android.gms/.droidguard.DroidGuardService:@f229c33 flags=0x1081}
    binding=AppBindRecord{a4d6009 com.google.android.gms/.droidguard.DroidGuardService:com.google.android.gms.persistent}
    conn=android.os.BinderProxy@f229c33 flags=0x1081
  * ConnectionRecord{fd51b25 u0 com.google.android.bluetooth/com.android.bluetooth.pan.PanService:@f33531c flags=0x0}
    binding=AppBindRecord{7f7bad8 com.google.android.bluetooth/com.android.bluetooth.pan.PanService:system}
    conn=android.app.LoadedApk$ServiceDispatcher$InnerConnection@f33531c flags=0x0
  * ConnectionRecord{c68b169 u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentApiService:@f8207f0 flags=0x1081}
    binding=AppBindRecord{60fc807 com.google.android.gms/.chimera.PersistentApiService:com.google.android.gms}
    conn=android.os.BinderProxy@f8207f0 flags=0x1081
  * ConnectionRecord{742ba1d u0 CR WACT CAPS com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:@f98b2f4 flags=0x1081}
    binding=AppBindRecord{9db9d9b com.google.android.gms/.chimera.PersistentDirectBootAwareApiService:com.google.android.contacts}
    conn=android.os.BinderProxy@f98b2f4 flags=0x1081
```
