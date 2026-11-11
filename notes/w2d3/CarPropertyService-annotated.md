# CarPropertyService.java 注释版（权限 + 分发给 App）

> **只看 5 个位置**：`getProperty`、`getPropertySafe`、`setProperty`、`checkPropertyAccessibility`、`onPropertyChange`。
> 跳过：Client 生命周期管理细节、`dump`、`getPropertyList`。
> 预计 **25 分钟**。源码：`packages/services/Car/service/src/com/android/car/CarPropertyService.java`（696 行）

## 这个类是什么

`ICarProperty.Stub` 的实现，**App 通过 `CarPropertyManager` 跨进程调到的就是它**。
它是整条链路的**最后一站（往下）和第一站（往上）**：
- 往下：做**权限检查**，然后转给 PropertyHalService
- 往上：把事件**按订阅者分发**

```java
public class CarPropertyService extends ICarProperty.Stub {
```

## ① getProperty：先查配置，再查权限，最后才碰 HAL

```java
public CarPropertyValue getProperty(int prop, int zone) {
    synchronized (mLock) {
        if (mConfigs.get(prop) == null) {
            return null;   // ← 属性根本不存在，直接返回，不碰 HAL
        }
    }
    // Checks if android has permission to read property.
    String permission = mHal.getReadPermission(prop);      // ← 查这个属性的读权限名
    if (permission == null) {
        throw new SecurityException("Platform does not have permission to read value ...");
    }
    CarServiceUtils.assertPermission(mContext, permission); // ★ 真正做权限断言
    return mHal.getProperty(prop, zone);                    // ← 转给 PropertyHalService
}
// ← 权限检查在"服务层"，不在 HAL 层。CarService 进程以 system 身份跑，
//    但它会 assert 调用方（App）有没有对应权限 —— 这是 Android 权限模型的典型做法。
```

## ② setProperty：写比读多两道坎

```java
public void setProperty(CarPropertyValue prop, ICarPropertyEventListener listener) {
    int propId = prop.getPropertyId();
    checkPropertyAccessibility(propId);        // ★ 坎 1：属性存在 + 有写权限
    // need an extra permission for writing display units properties.
    if (mHal.isDisplayUnitsProperty(propId)) {
        CarServiceUtils.assertPermission(mContext, Car.PERMISSION_VENDOR_EXTENSION);
        // ★ 坎 2：改"显示单位"这类属性，额外要 VENDOR_EXTENSION 权限
    }
    mHal.setProperty(prop);                    // ← 转给 PropertyHalService
    // 记住"谁设的"，用于 set 失败的异步回调
    updateSetOperationRecorderLocked(propId, prop.getAreaId(), client);
}
```

```java
private void checkPropertyAccessibility(int propId) {
    if (mConfigs.get(propId) == null) {
        throw new IllegalArgumentException("Property Id: 0x... does not exist in the vehicle");
        // ← 对应 W2D2 的"属性不存在"
    }
    String propertyWritePermission = mHal.getWritePermission(propId);
    if (propertyWritePermission == null) {
        throw new SecurityException("Platform does not have permission to change value ...");
        // ← 对应 W2D2 的"只读属性"：写权限为 null → 这里就拒了
    }
}
```

> **和 W2D2 的对照**：我们当时对 `GEAR_SELECTION`（access:0x1）调 `set-property-value`，收到的是 **VHAL 的 `code 4 = ACCESS_DENIED`**，而不是这里的 `SecurityException`。
> 说明：`GEAR_SELECTION` 在 CarService 层**有**写权限字符串（所以 checkPropertyAccessibility 放行），但 VHAL 内部仍拒绝——**两层权限，缺一不可**。

## ③ onPropertyChange：按订阅者分发（锁外回调）

```java
@Override
public void onPropertyChange(List<CarPropertyEvent> events) {
    Map<Client, List<CarPropertyEvent>> eventsToDispatch = new ArrayMap<>();
    synchronized (mLock) {
        for (CarPropertyEvent event : events) {
            int propId = event.getCarPropertyValue().getPropertyId();
            List<Client> clients = mPropIdClientMap.get(propId);   // ← 谁订阅了这个属性
            if (clients == null) {
                Slogf.e(TAG, "onPropertyChange: no listener registered ...");
                continue;
            }
            for (Client c : clients) {
                eventsToDispatch.computeIfAbsent(c, k -> new ArrayList<>()).add(event);
                // ← 按"订阅者"分组：每个 App 只收自己订阅的属性
            }
        }
    }
    // Parse the dispatch list to send events. We must call the callback outside the
    // scoped lock since the callback might call some function in CarPropertyService
    // which might cause dead-lock.
    for (Client client : eventsToDispatch.keySet()) {
        try {
            client.onEvent(eventsToDispatch.get(client));   // ★ 跨 binder 异步回调给 App
        } catch (RemoteException ex) { ... }                // ← App 挂了就忽略，靠 DeathRecipient 清理
    }
}
// ← 三个设计点：
//   1) 锁内只做分组，锁外才回调 —— 防止 App 回调里再调 CarPropertyService 造成死锁
//   2) 按 Client 分组 —— 每个 App 只收自己订阅的属性，不广播
//   3) onEvent 是 oneway 异步 —— 发出去就算完成，不阻塞 CarService
```

## ④ 整条链路的"权限三段"

| 段 | 位置 | 检查什么 |
|---|---|---|
| 服务层 | `CarPropertyService.checkPropertyAccessibility` | 属性存在 + 写权限字符串非空 |
| HAL 层 | `PropertyHalService` | 属性在 VHAL 支持列表内 |
| VHAL 层 | vendor 实现 | 属性 access 位（只读就返回 `ACCESS_DENIED`） |

**这就是为什么 W2D2 的 `(code 4)` 来自 VHAL**——服务层放行了，最后被 VHAL 拒。

---

*读完三份，你已经走完 `App → CarPropertyService → PropertyHalService → VehicleHal → IVehicle` 的完整读/写链，和反向的事件链。*