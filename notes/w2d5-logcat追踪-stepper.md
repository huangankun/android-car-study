# W2D5 · logcat 追踪属性请求（✅ 完成）

> 任务：在 AAOS 模拟器上用 logcat 真跑一次读/写/注入，把 W2D3+W2D4 读的静态代码和运行时对上。
> 执行人：Hermes（导师）｜学习者：先生
> 证据：`experiments/w2d5/`（logcat-property-chain.txt 175 行 + inject-timeline.txt）

## 任务卡

- **目标**：用 logcat 证明：① 写操作确实经过 CarPropertyService；② `inject-vhal-event` 不改存储值（时间戳不变）；③ CarShellCommand 是所有 `cmd car_service` 操作的统一入口。
- **为什么这一步重要**：读了四天静态代码，第一次让它在模拟器上真跑——代码和运行时的对应关系是面试的"底气"。
- **知识点清单**：
  1. `CarShellCommand` 是 `cmd car_service` 的唯一入口类
  2. `CarPropertyService.mSyncGetSetPropertyOpCount` 是并发 get/set 的计数器
  3. `VehicleHal`/`PropertyHalService` 的 `DBG` 是编译期常量，userdebug 上不打 DEBUG 日志
  4. inject 前后时间戳对比 = W2D2 结论的运行时验证

## 执行步骤

### S1 · 准备：清 logcat + 开启 verbose ✅
```bash
adb logcat -c
adb shell setprop log.tag.CarPropertyService VERBOSE
adb shell setprop log.tag.PropertyHalService VERBOSE
adb shell setprop log.tag.VehicleHal VERBOSE
```
**讲解**：`setprop log.tag.XXX VERBOSE` 是 Android 标准的 logcat 等级控制。但 VehicleHal/PropertyHalService 的日志开关不是 `Slogf.d()` 直接打，而是 `DBG` 常量控制（编译期决定）。

### S2 · 操作 ①：读 PERF_VEHICLE_SPEED ✅
```bash
adb shell cmd car_service get-property-value 0x11600207
```
真实输出：
```text
Property:0x11600207, status: 0, timestamp: 26000546095, zone: 0x0,
floatValues: [0.0], int32Values: [], int64Values: [], bytes: [], string:
```
**logcat 段**：`mSyncGetSetPropertyOpCount` 同样 `1 → 0`——`get` 也是同步操作，也走 `runSyncOperationCheckLimit` 计数（2026-11-18 真机复验确认）。

### S3 · 操作 ②：写 HVAC_TEMPERATURE_DISPLAY_UNITS 48→49 ✅
```bash
adb shell cmd car_service set-property-value 0x1140050e 0 48
adb shell cmd car_service get-property-value 0x1140050e   # 读回 48
adb shell cmd car_service set-property-value 0x1140050e 0 49  # 恢复
```
真实 logcat（节选）：
```text
11-16 12:09:22.442  I CarShellCommand: Setting vehicle property: id=0x1140050e, areaId=0, value=48
11-16 12:09:22.625  D CarPropertyService: mSyncGetSetPropertyOpCount: 1
11-16 12:09:22.625  D CarPropertyService: mSyncGetSetPropertyOpCount: 0
11-16 12:09:23.499  I CarShellCommand: Setting vehicle property: id=0x1140050e, areaId=0, value=49
11-16 12:09:23.624  D CarPropertyService: mSyncGetSetPropertyOpCount: 1
11-16 12:09:23.624  D CarPropertyService: mSyncGetSetPropertyOpCount: 0
```
**解读**：
- `CarShellCommand` 在 INFO 级记录**每一次 cmd car_service 操作**——它是统一入口，所有 `cmd car_service` 命令都从这里进。
- `mSyncGetSetPropertyOpCount` 从 0→1→0，说明 CarPropertyService **确实收到了 set 请求**并处理了。
- **修正**：`get` 和 `set` 都经过 `runSyncOperationCheckLimit`，都会让计数器 +1/-1。它是**并发同步 get/set 上限保护**（并发数 ≥ `SYNC_GET_SET_PROPERTY_OP_LIMIT` 时抛 `SYNC_OP_LIMIT_TRY_AGAIN`），不是「set 等、get 不等」。原文错误，2026-11-18 真机复验后已改。

### S4 · 操作 ③：inject-vhal-event 车速=22.5 ✅
```bash
adb shell cmd car_service inject-vhal-event 0x11600207 0 22.5
```
真实 logcat：
```text
11-16 12:09:23.519  I CarShellCommand: Injecting VHAL event: prop=0x11600207, zone=0, value=22.5, isError=false, delayTime=0
```
**但注入前后 `get-property-value` 时间戳对比**：
```text
=== 注入前 ===
Property:0x11600207, timestamp: 26000546095, floatValues: [0.0]
=== 注入后 ===
Property:0x11600207, timestamp: 26000546095, floatValues: [0.0]
```
**时间戳一字不差 → 再次证实 W2D2 结论：inject-vhal-event 只伪造 onPropertyEvent，不写存储值。**

### S5 · 为什么 VehicleHal/PropertyHalService 没日志 ⚠️
`adb shell setprop log.tag.VehicleHal VERBOSE` 不起作用——因为这两个类的日志不是靠 `Slogf.d()` 直接打的，而是靠 `DBG` 常量（编译期 `static final boolean DBG = ...`）控制，运行时改 `log.tag` 没用。

**要拿到完整链路 trace，只有两条路**：
1. **Android Studio 断点**：在 `VehicleHal.get()` / `VehicleHal.onPropertyEvent()` 下断点，一步步跟。
2. **改源码加日志**（W1D5 那套）：在 `PropertyHalService.getProperty` 开头加一行 `Slogf.i(TAG, "getProperty called")`，重新构建安装。

## 问题日志

| # | 现象 | 原因 | 结论 |
|---|---|---|---|
| P1 | `setprop log.tag.VehicleHal VERBOSE` 无效 | VehicleHal 的日志由 `DBG` 编译期常量控制，不是运行时 log tag | 要 DEBUG 日志只能改源码重编，或 Android Studio 断点 |
| P2（已推翻） | 原以为 `get-property-value` 不触发 `mSyncGetSetPropertyOpCount` | **错**。android14-release 源码 + 真机复验：`getProperty` 也走 `runSyncOperationCheckLimit`，同样 +1/-1 | 计数器是**并发同步 get/set 限流**（超 `SYNC_GET_SET_PROPERTY_OP_LIMIT` 抛 `SYNC_OP_LIMIT_TRY_AGAIN`），不是「set 才计数」 |

## 面试高频

```bash
# 看属性读写是否经过 CarPropertyService
adb logcat | grep "CarPropertyService"
# 看 cmd car_service 操作入口
adb logcat | grep "CarShellCommand"
```

## 自测（3 题，做完喊我）

1. `mSyncGetSetPropertyOpCount` 是什么？它包住了哪些操作？并发超过上限会发生什么？
2. `inject-vhal-event` 的 logcat 有记录，但 `get-property-value` 时间戳不变——这证明了什么？用 W2D2/W2D3 的源码解释。
3. 如果你面试时被问「你怎么验证一个属性读写请求确实到达了 VHAL」，除了 `cmd car_service`，还有什么手段？

---

*本篇是 W2 黄金链路代码精读后的运行时验证。*