# W2D3 · 黄金链路逐行注释阅读指引

按顺序读这四份，每份最上面标了「只看哪些方法、跳过什么、多少分钟」：

| 顺序 | 文件 | 目标 | 时间 |
|---|---|---|---|
| **第一份** | [IVehicle-annotated.md](./IVehicle-annotated.md) | HAL 接口契约：三个异步方法 | 10 min |
| **第二份** | [VehicleHal-annotated.md](./VehicleHal-annotated.md) | CarService 唯一跨进程出口 + 事件路由 | 20 min |
| **第三份** | [PropertyHalService-annotated.md](./PropertyHalService-annotated.md) | ID 映射 + HalPropValue→CarPropertyEvent | 20 min |
| **第四份** | [CarPropertyService-annotated.md](./CarPropertyService-annotated.md) | 权限检查 + 按订阅者分发 | 25 min |

> 对照源码：`packages/services/Car/service/src/com/android/car/`（android13-release）。
> 原始文件已存档在 [src/](./src/)（AOSP Apache 2.0），可直接对照行号。
> 建议先读 stepper 的「三条路径全景」建立坐标系，再按顺序读四份。

## 读完四份后的自检

不看代码，用一段话讲清楚：

> 一个 App 调 `getProperty(PERF_VEHICLE_SPEED)` →
> CarPropertyService 查配置和读权限 →
> PropertyHalService 把 manager id 转成 HAL id，确认 VHAL 支持 →
> VehicleHal 调 HalClient.getValue → 过 binder 到 IVehicle.getValues →
> 拿到 HalPropValue 按 float 解包 → 逐层转成 CarPropertyValue 返回。

再用一段话说反向：

> VHAL 有变化 → IVehicleCallback.onPropertyEvent →
> VehicleHal 按 propId 路由到 PropertyHalService →
> PropertyHalService 转成 CarPropertyEvent →
> CarPropertyService 按订阅者分组、锁外回调 →
> App 收到 onEvent。

**两段都能说顺，W2D3 就完成了。**