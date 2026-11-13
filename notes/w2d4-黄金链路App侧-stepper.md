# W2D4 · 黄金链路精读：CarPropertyManager → 示例 App（✅ 完成）

> 任务：读通客户端（App 侧），把 W2D3 的 HAL 侧和今天的 App 侧拼成**一条完整的黄金链路**。
> 执行人：Hermes（导师）｜学习者：先生
> 源码：android13-release；逐行注释在 `notes/w2d4/`

## 任务卡

- **目标**：能不看代码，把「App 调 `getProperty(车速)` 到 VHAL 再回来」的完整旅程讲出来，包括**双向 binder**和**错误码翻译**。
- **为什么这步收口**：W2D3 从 HAL 读到 CarService；今天从 CarService 读到 App。读完这步，黄金链路才算「从头到尾」打通，W2D6 的旗舰文就有完整素材。
- **知识点清单**（自测出题源）：
  1. `ICarProperty.aidl` 的事务码 0~7（和 W2D3 服务端一一对应）
  2. **双向 binder**：`ICarProperty`（正向）+ `ICarPropertyEventListener`（反向）
  3. `registerCallback` 本质是「把 App 的 binder 递给 CarService」
  4. 错误码翻译：VHAL `code 4` → `PropertyAccessDeniedSecurityException`
  5. `SENSOR_RATE_*` 和 `changeMode` 的关系

## 完整黄金链路（HAL → App，收口版）

```
【App 进程】
  SpeedActivity
   └─ mCarPropertyManager.getProperty(Float.class, PERF_VEHICLE_SPEED, GLOBAL)
       └─ mService.getProperty(...)                        ══ ICarProperty:3 ══▶
【CarService 进程】                                          （正向 binder）
  CarPropertyService.getProperty        [查配置 + 读权限 assertPermission]
   └─ PropertyHalService.getProperty    [managerToHalPropId + 支持检查]
       └─ VehicleHal.get                [按 clazz 解包]
           └─ HalClient.getValue        ══ IVehicle:getValues ══▶
【vendor 进程】
  VHAL（读 CAN / 缓存）→ 返回 HalPropValue
        ◀══ 逐层转成 CarPropertyValue<Float> ══  逐层返回  ══▶ App 拿到 22.5

【反向：事件】
  VHAL 车速变化 → VehicleHal.onPropertyEvent → PropertyHalService.onHalEvents
   → CarPropertyService.onPropertyChange → client.onEvent ══ 反向 binder ══▶
  CarPropertyEventListenerToService.onEvent → handleEvent → 主线程
   → mSpeedCallback.onChangeEvent(22.5)
```

## 执行步骤

### S1 · 读 binder 契约 ✅（10 min）
`notes/w2d4/ICarProperty-annotated.md`
**记住**：事务码 0~7；`registerListener` 把 `ICarPropertyEventListener`（反向 binder）递过去。

### S2 · 读 App 侧 API ✅（25 min）
`notes/w2d4/CarPropertyManager-annotated.md`
**记住**：`registerCallback` = 递反向 binder；`handleCarServiceSpecificException` 是错误码翻译点。

### S3 · 看示例 App ✅（10 min）
`notes/w2d4/示例App-读车速.md`
**记住**：`Car.createCar` 异步、`getCarManager(Car.PROPERTY_SERVICE)`、`registerCallback` 订阅、`getProperty` 读一次。

## 问题日志（读客户端踩到的 2 个坑）

| # | 困惑 | 真相 | 依据 |
|---|---|---|---|
| P1 | `setProperty` 为什么也要传回调 binder？ | 写是异步的，VHAL 可能事后回报"写失败"，得靠 `onPropertySetError` 推回来 | `setProperty` 传 `mCarPropertyEventToService` |
| P2 | App 怎么拿到 `code 4`？ | App 拿不到原始码——`handleCarServiceSpecificException` 把 `STATUS_ACCESS_DENIED` 翻成 `PropertyAccessDeniedSecurityException` | 该方法的 switch |

## 面试高频

```text
Q: App 读一个车控属性，跨了几个进程？
A: 三个。App → CarService（ICarProperty binder）→ VHAL（IVehicle binder）。
   回调反向：VHAL → CarService → App（ICarPropertyEventListener binder）。
```

## 自测（3 题，做完喊我）

1. `registerCallback` 为什么能收到"推送"？binder 世界里"推送"是怎么实现的？
2. App 侧写一个只读属性，最终拿到的是什么异常？它对应的 VHAL 错误码是多少？（用链路说清翻译过程）
3. `getProperty(Float.class, ...)` 如果属性实际是 int 类型，会在哪一层、抛什么错？

---

*黄金链路读完。W2D5 用 logcat 真跑一次属性请求。*