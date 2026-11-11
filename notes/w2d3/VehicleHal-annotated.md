# VehicleHal.java 注释版（CarService 侧的 HAL 包装）

> **只看 5 个位置**：构造（HAL 服务清单）、`get`、`set`、`onPropertyEvent`、`isPropertySubscribable`。
> 跳过：所有 `dump`、`getIfAvailable*` 泛型助手、`VehiclePropertyEventInfo` 等。
> 预计 **20 分钟**。源码：`packages/services/Car/service/src/com/android/car/hal/VehicleHal.java`（1139 行）

## 这个类是什么

CarService 里**唯一**直接持有 `IVehicle` binder 的地方。它负责：
1. 启动时把 VHAL 的属性配置拉下来，分给各个 `HalServiceBase` 子类（PropertyHalService / PowerHalService / ...）。
2. 提供 `get`/`set` 给上层。
3. 接收 VHAL 的上报，**按 propId 路由**给对应的 HAL service。

```java
public class VehicleHal implements HalClientCallback {    // ← 它是"回调的接收者"
```

## ① 构造：把 HAL 服务排好队（PropertyHalService 必须最后）

```java
mAllServices = List.of(
        mPowerHal, mInputHal, mDiagnosticHal, mVmsHal,
        mUserHal, mClusterHalService, mEvsHal, mTimeHalService,
        mPropertyHal);                          // ← PropertyHalService 放最后
// 注释原文：mPropertyHal must be the last so that on init/release
//          it can be used for all other HAL services properties.
// ← 为什么？其他 HAL service 在 init 时可能要读属性（比如电源服务要知道状态），
//    所以 PropertyHalService 得先"就绪"，才能给别人用。
```

```java
mHalClient = halClient != null ? halClient
        : new HalClient(vehicle, mHandlerThread.getLooper(), /* callback= */ this);
// ← vehicle 就是 IVehicle 的 binder 代理；this 是回调接收者
// ← 所有 VHAL 回调都投到 mHandlerThread 这个单独线程，不占 binder 线程
```

## ② init：把"属性归属"建起来（SparseArray<HalServiceBase>）

```java
configs = mHalClient.getAllPropConfigs();        // ← 调 IVehicle.getAllPropConfigs()
for (HalServiceBase service : mAllServices) {
    for (Integer propId : mAllProperties.keyAt(j)) {
        if (service.isSupportedProperty(propId)) {
            mPropertyHandlers.append(propId, service);   // ← propId → 唯一 HAL service
        }
    }
}
// ← 每个属性只归属一个 HAL service。绝大多数归 PropertyHalService，
//    少数（电源/输入/用户/仪表…）归专门的 service。
```

## ③ get：调 IVehicle + 按类型解包（重点看这一行跨进程）

```java
public <T> T get(Class clazz, HalPropValue requestedPropValue) {
    HalPropValue propValue;
    propValue = mHalClient.getValue(requestedPropValue);   // ★ 真正过 binder 到 VHAL
    // ← 这一行以下是纯解包：HalPropValue 里是 int32[]/float[] 等弱类型数组，
    //    按调用方要的 clazz 取出对应字段
    if (clazz == Float.class || clazz == float.class) {
        return (T) propValue.getFloatValue(0);
    } else if (clazz == Integer.class || clazz == int.class) {
        return (T) propValue.getInt32Value(0);
    } ...
}
// ← 注意：HalClient.getValue 对外是同步返回，内部其实是"发 getValues + 等 onGetValues 回调"
//    （用 latch/条件变量把异步包成同步），对上层隐藏了异步细节。
```

## ④ set：只有一行

```java
public void set(HalPropValue propValue) {
    mHalClient.setValue(propValue);   // ★ 过 binder 到 VHAL.setValues()
}
```

## ⑤ onPropertyEvent：VHAL 上报的入口（按 propId 路由）

```java
@Override
public void onPropertyEvent(ArrayList<HalPropValue> propValues) {
    synchronized (mLock) {
        for (HalPropValue v : propValues) {
            int propId = v.getPropId();
            HalServiceBase service = mPropertyHandlers.get(propId);   // ← 查归属
            if (service == null) { continue; }                        // ← 没人认领就丢
            service.getDispatchList().add(v);                         // ← 塞进该 service 的待派发队列
            mServicesToDispatch.add(service);
        }
    }
    for (HalServiceBase s : mServicesToDispatch) {
        s.onHalEvents(s.getDispatchList());   // ★ 交给 HAL service 处理
        s.getDispatchList().clear();
    }
}
// ← 关键：VehicleHal 不做业务判断，只做"路由"。真正的解析/映射/分发在 PropertyHalService.onHalEvents。
```

## ⑥ isPropertySubscribable：什么属性才能订阅

```java
static boolean isPropertySubscribable(HalPropConfig config) {
    if ((config.getAccess() & VehiclePropertyAccess.READ) == 0   // 必须可读
            || (config.getChangeMode() == STATIC)) {              // STATIC 属性不会变，不用订阅
        return false;
    }
    return true;
}
// ← 对应 W2D2 的 access/changeMode：只读(0x1)可订阅；只写(0x2)不能；
//    STATIC（如 VIN）订阅了也永远只有一次值。
```

## 这条链上的四个"卡点"（面试常问）

| 卡点 | 位置 | 回答要点 |
|---|---|---|
| 属性归属谁 | `mPropertyHandlers` | 每个 propId 唯一一个 HalServiceBase；PropertyHalService 兜底 |
| 谁真正跨进程 | `mHalClient.getValue/setValue` | 只有这一层调 IVehicle |
| 异步怎么变同步 | `HalClient` 内部 latch | get 对外同步，底层是 getValues + 等回调 |
| `inject` 为什么不生效 | 不在 IVehicle 上 | 它只调 `VehicleHal.onPropertyEvent` 伪造事件 |

---

*下一步：`PropertyHalService-annotated.md`（路由到业务层 + ID 映射）*