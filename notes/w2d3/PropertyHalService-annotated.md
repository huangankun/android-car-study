# PropertyHalService.java 注释版（业务层 + ID 映射）

> **只看 5 个位置**：ID 映射、`getProperty`、`setProperty`、`subscribeProperty`、`onHalEvents`。
> 跳过：权限字符串表、`dump`、`mPropValueBuilder` 细节。
> 预计 **20 分钟**。源码：`packages/services/Car/service/src/com/android/car/hal/PropertyHalService.java`（470 行）

## 这个类是什么

夹在 `CarPropertyService`（给 App 用）和 `VehicleHal`（贴 HAL）之间的**业务层**：
- 负责 **Manager propId ↔ HAL propId 的双向映射**
- 负责把 `HalPropValue`（弱类型）转成 `CarPropertyValue`（强类型）
- 负责订阅的建立/撤销
- 负责把 VHAL 事件转成 `CarPropertyEvent` 往上抛

```java
public class PropertyHalService extends HalServiceBase {
```

## ① 两级 ID 映射（很多人不知道的点）

```java
// Only contains propId if the property Id is different in HAL and manager
private static final Map<Integer, Integer> PROPERTY_ID_HAL_TO_MANAGER = Map.of(
        VehicleProperty.VEHICLE_SPEED_DISPLAY_UNITS,
        VehiclePropertyIds.VEHICLE_SPEED_DISPLAY_UNITS);
// ← 只有 VEHICLE_SPEED_DISPLAY_UNITS 这一个属性的 HAL id 和 manager id 不同，
//    其余属性的 id 完全一样。所以映射表是"特例表"，不是全量表。

private static int managerToHalPropId(int mgrPropId) {
    return PROPERTY_ID_MANAGER_TO_HAL.getOrDefault(mgrPropId, mgrPropId);  // ← 查不到就用原值
}

private static int halToManagerPropId(int halPropId) {
    return PROPERTY_ID_HAL_TO_MANAGER.getOrDefault(halPropId, halPropId);
}
```

## ② getProperty：App 读 → 落到 VHAL

```java
public CarPropertyValue getProperty(int mgrPropId, int areaId) {
    int halPropId = managerToHalPropId(mgrPropId);           // ← manager → HAL id
    if (!isPropertySupportedInVehicle(halPropId)) {
        throw new IllegalArgumentException("Invalid property Id : 0x" + ...);
        // ← VHAL 不支持，直接抛，不会白跑一趟
    }
    HalPropValue value = mVehicleHal.get(halPropId, areaId); // ★ 交给 VehicleHal → IVehicle
    if (value == null) return null;
    HalPropConfig propConfig = mHalPropIdToPropConfig.get(halPropId);
    return value.toCarPropertyValue(mgrPropId, propConfig);  // ← 弱类型 → 强类型（带单位/范围）
}
```

## ③ setProperty：App 写 → 打包 → VHAL

```java
public void setProperty(CarPropertyValue prop) {
    int halPropId = managerToHalPropId(prop.getPropertyId());
    if (!isPropertySupportedInVehicle(halPropId)) {
        throw new IllegalArgumentException("Invalid property Id : 0x" + ...);
    }
    HalPropConfig propConfig = mHalPropIdToPropConfig.get(halPropId);
    HalPropValue halPropValue = mPropValueBuilder.build(prop, halPropId, propConfig);
    // ← 把 CarPropertyValue（带 Java 类型）打包成 HalPropValue（int32[]/float[] 等）
    mVehicleHal.set(halPropValue);   // ★ 交给 VehicleHal → IVehicle.setValues()
}
```

## ④ subscribeProperty：订阅 = 告诉 VHAL "有变化推给我"

```java
public void subscribeProperty(int mgrPropId, float rate) {
    int halPropId = managerToHalPropId(mgrPropId);
    ...
    mVehicleHal.subscribeProperty(this, halPropId, rate);
    // ← this 是 PropertyHalService，它实现了 HalClientCallback 的 onPropertyEvent
    //    意思是："VHAL 以后有变化，回调我这个对象"
}
```

## ⑤ onHalEvents：VHAL 事件 → CarPropertyEvent（核心转换）

```java
@Override
public void onHalEvents(List<HalPropValue> values) {
    PropertyHalListener listener = mListener;      // ← CarPropertyService（下一层）
    if (listener == null) return;                  // ← 没人听，事件直接丢
    for (HalPropValue v : values) {
        int propId = v.getPropId();
        if (!isPropertySupportedInVehicle(propId)) continue;
        // userdebug 上额外校验 payload，防止脏数据
        if (BuildHelper.isDebuggableBuild() && !mPropIds.checkPayload(v)) continue;

        int mgrPropId = halToManagerPropId(propId);            // ← HAL → manager id
        HalPropConfig propConfig = mHalPropIdToPropConfig.get(propId);
        CarPropertyValue<?> propVal = v.toCarPropertyValue(mgrPropId, propConfig);  // ← 类型转换
        CarPropertyEvent event = new CarPropertyEvent(
                CarPropertyEvent.PROPERTY_EVENT_PROPERTY_CHANGE, propVal);         // ← 包装成事件
        mEventsToDispatch.add(event);
    }
    listener.onPropertyChange(mEventsToDispatch);   // ★ 交给 CarPropertyService
    mEventsToDispatch.clear();
}
// ← 注意：这一层是"批量"处理的——一次 VHAL 回调可能带多个属性，攒成 List 一次性往上抛
```

## 这条链上的设计点

| 设计 | 为什么 |
|---|---|
| ID 映射是"特例表" | 绝大多数属性 HAL/manager id 一致，只有 `VEHICLE_SPEED_DISPLAY_UNITS` 不一致 |
| `isPropertySupportedInVehicle` 前置检查 | 避免对不存在的属性白调 binder |
| `checkPayload` 只在 userdebug | 生产版不校验（性能），调试版校验（防脏数据） |
| 批量派发 `mEventsToDispatch` | 一次 VHAL 回调多属性，减少跨层调用次数 |

---

*下一步：`CarPropertyService-annotated.md`（权限 + 分发给 App）*