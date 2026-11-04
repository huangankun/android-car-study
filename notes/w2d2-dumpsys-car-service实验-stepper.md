# W2D2 · dumpsys car_service 玩熟 + service call 实验（✅ 完成）

> 任务：把 `dumpsys car_service` 的各个切面玩熟，并亲手做一次「读属性 → 写属性 → 读回」闭环和一次裸 `service call`。
> 执行人：Hermes（导师）｜学习者：先生
> 证据：`experiments/w2d2/`（398 条属性配置 + 33 服务 + service call 原始输出 + 注入测试）

## 任务卡

- **目标**：从「能 dump 出来」升级到「会用 dump 干活」——知道怎么按服务切、怎么把 propId 翻成名字、怎么读写属性、怎么直接打 binder。
- **为什么这一步重要**：W2D3 要读 `CarPropertyService` 源码，如果连「属性长什么样、怎么读写」都没摸过，读源码就是背代码。今天先把手弄脏。
- **知识点清单**（自测出题源）：
  1. `dumpsys car_service` 的 5 个切面：`--list` / `--list-hals` / `--services` / `--hal` / `--version`
  2. `cmd car_service` 与 `dumpsys` 的区别：一个是**命令接口**（能写），一个是**状态 dump**（只读）
  3. propId 三段位布局（组/区/类型）+ `get-carpropertyconfig` 是破译钥匙
  4. `access`（0x1=读, 0x2=写, 0x3=读写）与 `changeMode`（0x1=ON_CHANGE, 0x2=CONTINUOUS）
  5. `service call` 需要 AIDL 事务码，且返回是原始 Parcel（不可读）

## 执行步骤

### S1 · 摸清 6 个切面 ✅
```bash
adb shell dumpsys car_service --list          # 33 个服务名
adb shell dumpsys car_service --list-hals     # 9 个 HAL 名
adb shell dumpsys car_service --services CarPropertyService   # 只 dump 一个服务
adb shell dumpsys car_service --hal PropertyHalService        # 只 dump 一个 HAL
adb shell dumpsys car_service --version       # 版本
adb shell dumpsys car_service --help          # 全部选项
```
**讲解**：`--services` 和 `--hal` 是排查神器——1733 行的全量 dump 里眼睛会瞎，按名字切一刀就只剩几十行。

### S2 · 把 propId 翻成名字（398 条属性表）✅
```bash
adb shell cmd car_service get-carpropertyconfig            # 全部 398 条
adb shell cmd car_service get-carpropertyconfig 0x11400400 # 单条
```
真实输出（节选）：
```text
Property:0x11100100, Property name:INFO_VIN, access:0x1, changeMode:0x0
Property:0x11200407, Property name:NIGHT_MODE, access:0x1, changeMode:0x1
Property:0x11400400, Property name:GEAR_SELECTION, access:0x1, changeMode:0x1, config:[4,1,2,8,16,32,64,128,256]
Property:0x11600207, Property name:PERF_VEHICLE_SPEED, access:0x1, changeMode:0x2, fs min:1.0, fs max:10.0
Property:0x1140050e, Property name:HVAC_TEMPERATURE_DISPLAY_UNITS, access:0x3, changeMode:0x1, config:[49,48]
```
**统计**：398 条属性，其中 **92 条可读写（access:0x3）**。

**propId 位布局**（对照 `0x11400400`）：
```text
 0x 11 4 0 0400
 │  │  │   └── id  = 0400（GEAR 组）
 │  │  └────── 类型 = 0x10?（4 = INT32 的高位，低半字节）
 │  └───────── 区  = 0x1（GLOBAL）
 └──────────── 组  = 0x1（SYSTEM）
```

### S3 · 读属性 ✅
```bash
adb shell cmd car_service get-property-value 0x11400400   # GEAR_SELECTION
adb shell cmd car_service get-property-value 0x11600207   # PERF_VEHICLE_SPEED
adb shell cmd car_service get-property-value 0x11200407   # NIGHT_MODE
```
真实输出：
```text
Property:0x11400400, status: 0, timestamp: 1375801667, zone: 0x0, floatValues: [], int32Values: [4], ...
Property:0x11600207, status: 0, timestamp: 75200411577, zone: 0x0, floatValues: [0.0], int32Values: [], ...
Property:0x11200407, status: 0, timestamp: 1375801417, zone: 0x0, floatValues: [], int32Values: [0], ...
```
**读法**：`int32Values:[4]` = GEAR_SELECTION=4（PARK 档）；`floatValues:[0.0]` = 车速 0（静止）；`int32Values:[0]` = 白天模式。

### S4 · 写属性 + 读回闭环（核心）✅
选一个**全局可读写**属性：`HVAC_TEMPERATURE_DISPLAY_UNITS`（0x1140050e，48=华氏 / 49=摄氏）。
```bash
adb shell cmd car_service set-property-value 0x1140050e 0 48   # 写成华氏
adb shell cmd car_service get-property-value 0x1140050e         # 读回 48 ✔
adb shell cmd car_service set-property-value 0x1140050e 0 49   # 恢复摄氏
```
真实输出：
```text
Property(0x1140050e) is set to 48 successfully
Property:0x1140050e, ..., int32Values: [48], ...
Property(0x1140050e) is set to 49 successfully
Property:0x1140050e, ..., int32Values: [49], ...
```
**这就是完整闭环**：写成功 → 读回新值 → 恢复。比「dump 出来看看」深一层。

### S5 · VHAL 注入（失败，但很有价值）⚠️
```bash
adb shell cmd car_service inject-vhal-event 0x11400400 0 8   # 注入 GEAR_SELECTION=8(DRIVE)
adb shell cmd car_service get-property-value 0x11400400       # 读回仍是 4，没变
```
logcat 显示命令确实执行了：
```text
CarShellCommand: Injecting VHAL event: prop=0x11400400, zone=0, value=8, isError=false, delayTime=0
```
但属性值和时间戳都没变 → **注入被模拟器的 VHAL 丢弃**。见问题日志 P1。

### S6 · 裸 `service call`（能打，但不可读）⚠️
先查 ICar 的 AIDL 事务码（不是 1~10）：
```text
getCarService(String)            = 11
getCarConnectionType()           = 12
isFeatureEnabled(String)         = 13
enableFeature / disableFeature   = 14 / 15
getAllEnabledFeatures()          = 16
```
```bash
adb shell service call car_service 12          # getCarConnectionType
adb shell service call car_service 13 s16 hvac # isFeatureEnabled("hvac")
adb shell service call car_service 16          # getAllEnabledFeatures
```
真实输出：
```text
Result: Parcel(
  0x00000000: 00000000 73622a85 00000013 00000000 '.....*bs........')
Result: Parcel(00000000 00000005   '........')
Result: Parcel(
  0x00000000: ffffffff 00000034 00650072 ... 'requires android.car.permission.CONT...')
```
**三个结论**：① 事务码要查 AIDL（`= N`）；② 返回是原始 Parcel，花屏、读不出真实值；③ code 16 因缺权限抛 `SecurityException`。**这就是为什么工程上用 `cmd car_service`——同样的 binder 调用，人家帮你解析成人话。**

## 问题日志（本课 4 个真坑）

| # | 症状 | 原因 | 结论/解法 |
|---|---|---|---|
| P1 | `inject-vhal-event` 执行了（logcat 有记录），但属性值不变 | 模拟器的 VHAL 实现不应用注入（fake VHAL 的注入存储没被读路径用上） | 模拟器上别指望注入；用 `set-property-value`（可写属性）或改源码验证 |
| P2 | `service call car_service 1/2` 报 `Not a data message` / 花屏 | 事务码不是从 1 开始；ICar 的码是 11~19 | 查 AIDL 的 `= N`；先 `--help` 看有没有更友好的 `cmd` |
| P3 | `service call car_service 16` 返回 `SecurityException: requires android.car.permission.CONTROL_CAR_...` | shell UID 没有该权限 | 换不需要权限的方法，或 `adb root` 后再试 |
| P4 | `get-carpropertyconfig` 输出 398 行，找不到目标属性 | 全量太大 | `grep -iE "KEYWORD|access:0x3"` 过滤；或直接 `get-carpropertyconfig <propId>` |

## 面试高频命令

```bash
# 1. 定位属性
adb shell cmd car_service get-carpropertyconfig | grep -iE "SPEED|GEAR"
# 2. 读值
adb shell cmd car_service get-property-value 0x11600207
# 3. 写值（仅 access:0x3）
adb shell cmd car_service set-property-value <propId> <areaId> <data>
# 4. 只 dump 一个服务（排查专用）
adb shell dumpsys car_service --services CarPropertyService
```

## 自测（3 题，做完喊我）

1. `access:0x1` 和 `access:0x3` 分别是什么？为什么 `GEAR_SELECTION` 用 `set-property-value` 写不进去，但 `HVAC_TEMPERATURE_DISPLAY_UNITS` 可以？
2. `service call car_service 1` 为什么报 `Not a data message`？正确的做法是什么？（提示：事务码从哪来）
3. `inject-vhal-event` 和 `set-property-value` 都改属性，它们的区别是什么？为什么一个在模拟器上不生效？

---

*本文件由导师会话生成；证据在 `experiments/w2d2/`。*