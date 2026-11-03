# dumpsys car_service 全景地图（W2 学习索引）

> 目的：在读 W2 代码前，先用一份真实 dump 建立「车服务地图」——**这个 dump 里有哪些服务、各自干什么、和黄金链路在哪对接**。后续读 `Vehicle HAL → CarService → CarPropertyManager → App` 时，心里有张图，不会一头雾水。
> 数据来源：`experiments/w2d1-aaos/dumpsys-car_service.txt`（真实 dump，1733 行，Android 13 / `sdk_gcar_arm64` / userdebug）。
> 服务清单：`experiments/w2d1-aaos/car-service-list.txt`（`dumpsys car_service --list` 输出，33 个）。

---

## 一、这个 dump 到底是什么

`dumpsys car_service` 打印的是 **CarService 进程**的内部状态。三个关键事实：

1. **CarService 是独立进程**，不是 system_server。实测：
   ```
   system   570  ... system_server
   system   970  ... com.android.car      ← CarService 在这里
   ```
   从 Android 10 起，CarService 从 system_server 拆出来，以 `com.android.car` 独立进程运行（`car_service.rc` 拉起）。**这点很重要**：车服务挂了不会直接拖死整个系统，但也意味着它和 system_server 是跨进程协作。

2. **它是 33 个子服务的聚合体**。CarService 本身是个"壳"，真正的能力分散在 33 个 `CarXxxService` 里，每个都是独立模块。

3. **它还把 9 个 HAL 的转储一起带出来**。所以一份 dump 里同时看到「上层 Java 服务」和「底层 HAL 状态」——这正是它比普通 `dumpsys` 值钱的地方。

---

## 二、三层结构

```
┌─────────────────────────────────────────────────────────────┐
│ CarService 进程 (com.android.car, pid 970)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 33 个子服务（Java 层，各自独立模块）                    │   │
│  │   属性 / 用户 / 电源 / 音频 / 显示 / 输入 / 诊断 ...    │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │ Binder                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 9 个 HAL（HIDL/AIDL，跨进程到 vendor 侧）               │   │
│  │   Vehicle HAL / Power HAL / Input HAL / User HAL ...   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              │  App（CarPropertyManager 等）│
              └───────────────────────────┘
```

---

## 三、33 个子服务分组（核心表）

按「干什么」分成 9 组。**这张表就是后续学习的地图**——遇到哪个场景，就查哪一组。

| 分组 | 服务 | 一句话用途 |
|---|---|---|
| **属性/特性** | `CarPropertyService` | **车辆属性总入口**（车速、档位、空调、车门…）；W2 主战场 |
| | `CarFeatureController` | 特性开关总控（决定哪些车服务启用，见下方「已启用特性」） |
| | `CarExperimentalFeatureServiceController` | 实验特性控制（灰度/AB） |
| **用户/账号** | `CarUserService` | 多用户（Driver/Guest/乘客），用户切换生命周期 |
| | `CarUserNoticeService` | 用户通知（首次登录、切换提示） |
| | `PerUserCarServiceHelper` | 每用户的服务辅助（按用户起停子系统） |
| **电源/驾驶/驻车** | `CarPowerManagementService` | **电源状态机**（ON/SUSPEND/SHUTDOWN），电源策略、组件开关 |
| | `GarageModeService` | 驻车充电时的维护模式（后台升级/清理） |
| | `CarDrivingStateService` | 驾驶状态（Parked/Idling/Moving），很多限制的触发源 |
| **音频/媒体/夜** | `CarAudioService` | **音频**（音量、焦点、多 zone、音频路由） |
| | `CarMediaService` | 每用户媒体源管理（谁在播、播放器状态） |
| | `CarNightService` | 日夜模式（DAY NIGHT POLICY） |
| **显示/UX/仪表** | `CarUxRestrictionsManagerService` | **驾驶时 UX 限制**（禁止长列表、禁止输入…） |
| | `CarOccupantZoneService` | 乘员区（座位/显示/音频区的映射，多屏多人的基础） |
| | `ClusterHomeService` | 仪表盘 Home |
| | `ClusterNavigationService` | 仪表盘导航状态同步 |
| | `FixedActivityService` | 固定 Activity（倒车影像这类必须常驻的） |
| **输入/焦点** | `CarInputService` | 输入（物理按键、旋钮 Rotary、方向盘键） |
| | `AppFocusService` | 应用焦点（哪个 App 当前"拥有"用户注意力） |
| **包/活动/系统监控** | `CarPackageManagerService` | 车规包管理（驾驶时禁某些应用，`CarUxRestrictions` 的执行者） |
| | `CarActivityService` | 车规 Activity 管理（AMS 的车端扩展） |
| | `SystemActivityMonitoringService` | 前台活动监控（谁在前台，供电/音频用） |
| **诊断/监控/性能/遥测** | `CarDiagnosticService` | 诊断（OBD/DTC，车辆故障码） |
| | `CarStorageMonitoringService` | 存储监控（IO 过载、寿命预测） |
| | `CarWatchdogService` | 看门狗（进程卡死/ANR 检测） |
| | `CarPerformanceService` | 性能（渲染/CPU 性能参数调优） |
| | `CarTelemetryService` | 遥测（匿名上报车辆/系统指标） |
| | `CarBugreportManagerService` | bugreport 抓取管理 |
| **连接/位置/投屏/地图** | `CarBluetoothService` | 车机蓝牙（配对、免打扰、驾驶限制） |
| | `CarProjectionService` | 投屏（Android Auto / CarPlay） |
| | `CarLocationService` | 位置（GPS/定位，给导航/ADAS 用） |
| | `VmsBrokerService` | VMS 车辆地图服务（把车辆数据分发给订阅者） |
| **设备管理** | `CarDevicePolicyService` | 车规设备策略（DPM 的车端扩展，锁屏/禁用相机等） |

> **当前启用的特性**（dump 第 13 行 `mEnabledFeatures`）：
> `hvac, storage_monitoring, cabin, cluster_home_service, vehicle_map_service, uxrestriction, drivingstate, property, audio, power, projection, diagnostic, car_occupant_zone_service, info, car_bugreport, car_media, app_focus, package, car_watchdog, vendor_extension, car_bluetooth, car_performance, car_user_service, car_activity_service, android.car.input, car_telemetry_service, sensor ...`
> —— 这是一个"全功能"开发镜像，几乎全开。真车上 OEM 会关掉一部分。

---

## 四、HAL 层（dump 里 953 行之后）

| HAL | dump 里的内容 | 用途 |
|---|---|---|
| **Vehicle HAL** | `android.hardware.automotive.vehicle.IVehicle` | **车辆信号的唯一来源**；`VehiclePropConfig` 列表就在这 |
| Power HAL | `isPowerStateSupported` / `isDeepSleepAllowed` | 底层电源能力 |
| Input HAL | `mKeyInputSupported` / `mRotaryInputSupported` | 底层输入能力 |
| Diagnostic HAL | （本镜像为空） | 诊断能力 |
| VMS HAL | `VmsProperty: supported` / `VmsClient: connected` | 车辆地图服务 HAL |
| User HAL | 5 个 `VehiclePropConfig` | 用户切换的底层支持 |
| Cluster HAL | `mIsCoreSupported` / `mIsNavigationStateSupported` | 仪表盘 HAL |
| EVS HAL | `EVS_SERVICE_REQUEST` | 环视/倒车影像 |
| ExternalTime HAL | `mLastAndroidTimeReported` + **`CAR.PropertyHalService` 的完整属性列表** | 外部时间同步 + **属性 HAL 明细（736 行，占 dump 最大头）** |

> **重点**：`ExternalTime HAL` 那 736 行（987–1723）表面看是"外部时间"，实际里面是 **`CAR.PropertyHalService` 的 `Properties available`**——也就是 Vehicle HAL 向 CarService 暴露的**全部 `VehiclePropConfig`**。这是 W2 黄金链路的第一手证据。

---

## 五、和 W2 黄金链路的对接点（划重点）

W2 要读的链路：

```
Vehicle HAL (IVehicle, vendor)
        │  get/set VehiclePropValue
        ▼
CarPropertyService (Java, 本 dump 第 19 行)
        │  getProperty / setProperty / subscribe
        ▼
CarPropertyManager (App 侧)
        │
        ▼
App（空调/仪表/媒体…）
```

在这个 dump 里，三处对应：

1. **`*CarPropertyService*`（第 19–59 行）**：`14 clients` + 35 个 `propId` 注册记录。这是"当前谁在监听什么属性"的实时快照。
2. **`ExternalTime HAL → CAR.PropertyHalService → Properties available`（第 989 行起）**：`VehiclePropConfig` 全量列表（`access`/`changeMode`/`areaConfigs`/`configArray`）。这是"HAL 到底能提供哪些属性"的权威清单。
3. **`*CarFeatureController*` 的 `mEnabledFeatures`（第 13 行）**：`property` 在启用列表里 → 说明 CarPropertyService 是活的。

**读码入口建议**：下一课从 `CarPropertyService.getProperty()` / `subscribeProperty()` 入手，对着这里的 `propId` 和 HAL 的 `VehiclePropConfig` 对照，链路就通了。

---

## 六、排障索引（这份 dump 的实用价值）

| 现象 | 先看哪段 | 关键字段 |
|---|---|---|
| 某项车辆信号（车速/档位/空调）读不到 | `*CarPropertyService*` + `CAR.PropertyHalService` | `propId` 是否注册、HAL 是否支持该属性 |
| 屏幕莫名变暗/休眠 | `*PowerManagementService*` | `mCurrentState`、`mCurrentPowerPolicyId`、组件开关 |
| 用户切不过去/切了回不来 | `*CarUserService*` | `lifecycle listeners`、`InitialUser`、`User HAL` |
| 驾驶时界面被锁/应用被禁 | `*CarUxRestrictionsManagerService*` + `*CarDrivingStateService*` | UX 限制回调、`mCurrentState` |
| 声音串音/音量不对 | `*CarAudioService*` | 音频 zone、焦点持有者 |
| 夜间模式不生效 | `*DAY NIGHT POLICY*`（`CarNightService`） | 当前 policy |
| 某个服务没启动 | `*CarFeatureController*` | `mEnabledFeatures` 里有没有它 |
| 倒车影像不显示 | `*FixedActivityService*` | 固定 Activity 绑定 |
| 卡顿/ANR | `*CarWatchdogService*` + `*CarPerformanceService*` | 看门狗记录、性能参数 |

---

## 七、propId 怎么读（看懂 `0x11200402` 这类数字）

`VehicleProperty` 的 `propId` 是 32 位整数，按字节分区：

```
 0x11 2004 02
 ││  ││││ │
 ││  ││││ └── property id（具体的信号，如 HVAC_FAN_SPEED）
 ││  └────── 类型（0x0040=INT32, 0x0020=BOOLEAN, 0x0050=INT64...）
 └────────── 区域（0x01=GLOBAL, 0x05=SEAT, 0x06=DOOR...）
    └──────── 组（0x1=SYSTEM 系统属性, 0x2=VENDOR 厂商属性）
```

完整枚举在 AOSP 的 `hardware/interfaces/automotive/vehicle/aidl/.../VehicleProperty.aidl`。**读代码时对着这个位布局看，比死记名字有用。**

---

## 八、怎么用这份地图进入 W2

1. **先记住 9 个分组 + 每组 1 个"代表服务"**（属性=CarPropertyService、电源=CarPowerManagementService、用户=CarUserService、音频=CarAudioService、UX=CarUxRestrictionsManagerService）。
2. **再记住黄金链路的 4 段**：Vehicle HAL → CarPropertyService → CarPropertyManager → App。
3. **然后从 dump 里挑一条真实链路追**：比如 `0x11400400`（HVAC 组，3 个 client 在监听）→ 看 `CAR.PropertyHalService` 里它的 `VehiclePropConfig` → 再进代码看 `CarPropertyService.getProperty()`。
4. **最后才读源码**——这时你已经知道它"为什么存在、给谁用"，不会迷失。

---

*本文档由导师会话基于真实 dump 生成，归档至 `~/projects/android-car-study/notes/`；原始数据在 `experiments/w2d1-aaos/`。*