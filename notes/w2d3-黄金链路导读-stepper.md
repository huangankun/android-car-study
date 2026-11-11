# W2D3 · 黄金链路精读：Vehicle HAL → CarService（✅ 完成）

> 任务：把车控属性从 HAL 到 CarService 的**读、写、事件**三条路径读通，为 W2D4（CarPropertyManager → App）和 W2D6（旗舰文）打底。
> 执行人：Hermes（导师）｜学习者：先生
> 源码：android13-release（googlesource，经 Clash 代理拉取）；逐行注释在 `notes/w2d3/`
> 阅读范围：**只读这条链，禁止横读**（CarService 的 33 个子服务里，只碰属性这一条）

## 任务卡

- **目标**：能不看代码，把「一个车控属性从 HAL 到 App」的读/写/事件三条路径讲出来。
- **为什么先读 HAL 侧**：W2D3 是"从下往上"——先搞清底层契约（IVehicle）和 CarService 的 HAL 包装（VehicleHal/PropertyHalService），W2D4 再往上读 App 侧（CarPropertyManager）。
- **知识点清单**（自测出题源）：
  1. `IVehicle` 的三个异步方法（getValues/setValues/subscribe）
  2. `VehicleHal` 的两个职责：跨进程唯一出口 + VHAL 事件路由
  3. `PropertyHalService` 的 ID 双向映射（特例表）
  4. **权限三段**：服务层 → HAL 层 → VHAL 层
  5. 事件链为什么"锁内分组、锁外回调"

## 三条路径全景（先记这张图）

### 路径 A · 读（App → VHAL）

```
App
 └─ CarPropertyManager.getProperty()
     ═══ binder ═══▶
       CarPropertyService.getProperty(prop, zone)          ← 服务层
         ├─ mConfigs 里有这个属性吗？                        （不存在→null）
         ├─ mHal.getReadPermission(prop)                    （读权限字符串）
         ├─ CarServiceUtils.assertPermission(...)           ★ 权限断言
         └─ PropertyHalService.getProperty(mgrPropId, areaId)
              ├─ managerToHalPropId()                       ← ID 映射
              ├─ isPropertySupportedInVehicle()             ← VHAL 支持吗
              └─ VehicleHal.get(halPropId, areaId)
                   ├─ mHalClient.getValue(...)              ★ 唯一跨进程点
                   │    ═══ binder ═══▶ IVehicle.getValues()
                   └─ 按 clazz 解包（float/int/bool...）
```

### 路径 B · 写（App → VHAL）

```
App
 └─ CarPropertyManager.setProperty()
     ═══ binder ═══▶
       CarPropertyService.setProperty(prop, listener)       ← 服务层
         ├─ checkPropertyAccessibility(propId)              ★ 属性存在 + 写权限
         ├─ 若是 display units 属性 → 额外要 VENDOR_EXTENSION ← 坎 2
         ├─ PropertyHalService.setProperty(prop)
         │    ├─ mPropValueBuilder.build(...)               ← 打包成 HalPropValue
         │    └─ VehicleHal.set(halPropValue)
         │         └─ mHalClient.setValue(...)               ★ 跨进程
         │              ═══ binder ═══▶ IVehicle.setValues()
         └─ updateSetOperationRecorderLocked(...)            ← 记住谁设的（失败回调用）
```

### 路径 C · 事件（VHAL → App）

```
VHAL（vendor，主动上报）
 └─ IVehicleCallback.onPropertyEvent()
     ═══ binder ═══▶
       VehicleHal.onPropertyEvent(List<HalPropValue>)       ← 路由层
         ├─ mPropertyHandlers.get(propId)                    ← 属性归属哪个 HAL service
         └─ service.onHalEvents(dispatchList)                ← 交给 PropertyHalService
              └─ PropertyHalService.onHalEvents(...)
                   ├─ checkPayload（userdebug）
                   ├─ halToManagerPropId()                    ← ID 反向映射
                   ├─ v.toCarPropertyValue()                  ← 弱类型→强类型
                   └─ listener.onPropertyChange(events)       ← 交给 CarPropertyService
                        └─ CarPropertyService.onPropertyChange(events)
                             ├─ 按 propId 找订阅者（mPropIdClientMap）
                             ├─ 按 Client 分组
                             └─ （锁外）client.onEvent(events)  ★ 跨 binder 回 App
```

## 执行步骤

### S1 · 读接口契约 ✅（10 min）
`notes/w2d3/IVehicle-annotated.md`
**记住**：`getValues` / `setValues` / `subscribe` 全部异步、全部带 callback；`subscribe` 的 sampleRate 是"建议值"。

### S2 · 读 CarService 的 HAL 包装 ✅（20 min）
`notes/w2d3/VehicleHal-annotated.md`
**记住**：`VehicleHal` 是**唯一**持有 `IVehicle` 的地方；`onPropertyEvent` 只做路由，不做业务。

### S3 · 读业务层与 ID 映射 ✅（20 min）
`notes/w2d3/PropertyHalService-annotated.md`
**记住**：ID 映射是**特例表**（只有 `VEHICLE_SPEED_DISPLAY_UNITS` 不同）；事件在这里从 `HalPropValue` 转成 `CarPropertyEvent`。

### S4 · 读服务层与权限 ✅（25 min）
`notes/w2d3/CarPropertyService-annotated.md`
**记住**：权限检查在服务层；写比读多一道"display units 额外权限"；事件分发"锁内分组、锁外回调"。

## 问题日志（读源码时踩到的 3 个坑）

| # | 困惑 | 真相 | 依据 |
|---|---|---|---|
| P1 | `getProperty` 明明是同步返回，为什么说 IVehicle 是异步？ | `HalClient.getValue()` 内部用 latch 把"异步 getValues + 等 onGetValues 回调"包成了同步 | `VehicleHal.get()` → `mHalClient.getValue()` |
| P2 | 属性 ID 在 HAL 和 App 层不一样？ | 绝大多数一样；只有 `VEHICLE_SPEED_DISPLAY_UNITS` 不同，用特例表映射 | `PROPERTY_ID_HAL_TO_MANAGER`（Map.of 只有 1 项） |
| P3 | W2D2 的 `code 4` 是谁拒的？ | 服务层有写权限字符串（放行），**VHAL 层**按 access 位拒 | `checkPropertyAccessibility` 只查权限字符串非空 |

## 面试高频

```text
Q: 一个车控属性从 HAL 到 App 怎么走？
A: 读路径 App→CarPropertyManager→(binder)CarPropertyService(权限)→PropertyHalService(ID映射)
   →VehicleHal→(binder)IVehicle.getValues→VHAL。
   事件反向：VHAL→VehicleHal.onPropertyEvent(路由)→PropertyHalService.onHalEvents(转换)
   →CarPropertyService.onPropertyChange(按订阅者分组)→(binder)App。
```

## 自测（3 题，做完喊我）

1. 读、写、事件三条路径里，**哪一行是唯一真正跨进程（binder）的地方**？分别在哪个类？
2. 为什么 `inject-vhal-event` 改了值，`get` 却读不到？（用 W2D3 的链路解释，不要再说"模拟器 bug"）
3. 权限检查有三段，分别在哪一层？W2D2 的 `code 4 = ACCESS_DENIED` 是哪一段拒的？

---

*证据与源码摘录见 `notes/w2d3/`；原始源码为 AOSP android13-release（Apache 2.0）。*