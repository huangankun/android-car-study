# CarPropertyManager.java 注释版（App 侧 API）

> **只看 6 个位置**：构造、`registerCallback`、`CarPropertyEventListenerToService`、`getProperty`、`setProperty`、`handleCarServiceSpecificException`。
> 跳过：`getPropertyList`、各类泛型助手、`dump`。
> 预计 **25 分钟**。源码：`car-lib/src/android/car/hardware/property/CarPropertyManager.java`（1048 行）

## 这个类是什么

App 拿到的**唯一入口**。它持有 `ICarProperty` 代理（`mService`），对 App 隐藏了 binder 细节，把「跨进程调用 + 回调 + 异常」包装成普通的 Java API。

```java
public CarPropertyManager(Car car, @NonNull ICarProperty service) {
    mService = service;   // ← ICarProperty 的 binder 代理
    // 用一个 handler 把 CarService 推来的事件投到 App 主线程
    mHandler = new SingleMessageHandler<CarPropertyEvent>(eventHandler.getLooper(), MSG_GENERIC_EVENT) {
        protected void handleEvent(CarPropertyEvent event) {
            // 按 propertyId 找监听者，分 PROPERTY_CHANGE / ERROR 两类
            listeners.onPropertyChanged(event);   // ← 最终回到 App 的回调
        }
    };
}
```

## ① registerCallback：订阅 = "我把我的 binder 递过去"

```java
public boolean registerCallback(CarPropertyEventCallback callback, int propertyId, float rate) {
    synchronized (mActivePropertyListener) {
        if (mCarPropertyEventToService == null) {
            mCarPropertyEventToService = new CarPropertyEventListenerToService(this);
            // ★ 造一个"反向 binder"，CarService 以后回调它
        }
        CarPropertyConfig config = getCarPropertyConfig(propertyId);
        if (config == null) return false;                 // ← 属性不存在

        if (config.getChangeMode() == VEHICLE_PROPERTY_CHANGE_MODE_ONCHANGE) {
            rate = SENSOR_RATE_ONCHANGE;                  // ← ONCHANGE 属性强制用 ONCHANGE rate
        }
        ...
        mService.registerListener(propertyId, rate, mCarPropertyEventToService);
        // ★ 跨进程（ICarProperty code 0）：把 propertyId、rate、反向 binder 一起发给 CarService
    }
    return true;
}
```

> **`rate` 的语义**（和 W2D2 的 `changeMode` 呼应）：
> `SENSOR_RATE_ONCHANGE`（0，变化才推）／`NORMAL`／`UI`／`FAST`／`FASTEST`。
> ONCHANGE 属性你给多高的 rate 都没用，强制回 ONCHANGE。

## ② CarPropertyEventListenerToService：反向 binder 的桩

```java
private static class CarPropertyEventListenerToService extends ICarPropertyEventListener.Stub {
    private final WeakReference<CarPropertyManager> mMgr;   // ← 弱引用，防泄漏
    @Override
    public void onEvent(List<CarPropertyEvent> events) {
        CarPropertyManager manager = mMgr.get();
        if (manager != null) manager.handleEvent(events);   // ← 转投到主线程 handler
    }
}
// ← 这就是 W2D3 服务端 `client.onEvent(events)` 的另一端！
//    CarService 跨进程调这个 onEvent，数据就到了 App 进程。
```

## ③ getProperty：跨进程读

```java
public <E> CarPropertyValue<E> getProperty(Class<E> clazz, int propId, int areaId) {
    checkSupportedProperty(propId);                       // ← 本地先查属性支持
    try {
        CarPropertyValue<E> propVal = mService.getProperty(propId, areaId);
        // ★ 跨进程（ICarProperty code 3）→ W2D3 的 CarPropertyService.getProperty → ... → IVehicle
        if (propVal.getValue().getClass() != clazz) {
            throw new IllegalArgumentException("Invalid property type...");
            // ← 类型对不上（比如把 float 属性当 int 读）直接抛
        }
        return propVal;
    } catch (ServiceSpecificException e) {
        return handleCarServiceSpecificException(e, propId, areaId, null);   // ★ 见 ⑤
    }
}
```

## ④ setProperty：跨进程写（还带上反向 binder 收错误）

```java
public <E> void setProperty(Class<E> clazz, int propId, int areaId, E val) {
    checkSupportedProperty(propId);
    if (mCarPropertyEventToService == null) {
        mCarPropertyEventToService = new CarPropertyEventListenerToService(this);
    }
    mService.setProperty(new CarPropertyValue<>(propId, areaId, val),
            mCarPropertyEventToService);
    // ★ 跨进程（code 4）。为什么 set 也要传反向 binder？
    //   因为写是异步的——VHAL 可能事后才回报"写失败"，得靠 onPropertySetError 推回来。
}
```

## ⑤ handleCarServiceSpecificException：VHAL 错误码 → App 异常（黄金链路的终点）

```java
private <T> T handleCarServiceSpecificException(ServiceSpecificException e, int propId, int areaId, T rv) {
    int errorCode = e.errorCode;
    switch (errorCode) {
        case VehicleHalStatusCode.STATUS_NOT_AVAILABLE:    // 3
            throw new PropertyNotAvailableException(propId, areaId);
        case VehicleHalStatusCode.STATUS_TRY_AGAIN:        // 1
            throw new PropertyNotAvailableAndRetryException(propId, areaId);
        case VehicleHalStatusCode.STATUS_ACCESS_DENIED:    // 4 ★
            throw new PropertyAccessDeniedSecurityException(propId, areaId);
        case VehicleHalStatusCode.STATUS_INTERNAL_ERROR:   // 5
            throw new CarInternalErrorException(propId, areaId);
    }
}
// ★★ W2D2 的 `code 4 = ACCESS_DENIED`，在 App 侧就是这个 PropertyAccessDeniedSecurityException！
//    整条链闭合了：VHAL 拒(4) → ServiceSpecificException → 这里 → App 看到类型化异常。
```

## 把整条黄金链路拼起来（含 App 侧）

```
App 代码
 └─ carPropertyManager.getProperty(Float.class, PERF_VEHICLE_SPEED, GLOBAL)
     └─ mService.getProperty(...)                    ═══ code 3 ═══▶ CarService
         └─ CarPropertyService.getProperty           [查配置+读权限]
             └─ PropertyHalService.getProperty       [ID映射+支持检查]
                 └─ VehicleHal.get                   [解包类型]
                     └─ HalClient.getValue           ═══ binder ═══▶ IVehicle.getValues
                         └─ vendor VHAL               [读 CAN/缓存]
                         ◀═══ 返回 HalPropValue ═══
                     ◀── 逐层转 CarPropertyValue ──
             ◀── CarPropertyValue ──
     ◀═══ code 3 返回 ═══
 └─ App 拿到 CarPropertyValue<Float>（车速 22.5）

反向（事件）：
VHAL 变化 → ... → CarPropertyService.client.onEvent ═══ code 0 的反向 ═══▶
  CarPropertyEventListenerToService.onEvent → handleEvent → 主线程 → App 的 onPropertyChanged
```

## 客户端三个"面试级"点

1. **双向 binder**：`registerListener`/`setProperty` 都把 `ICarPropertyEventListener.Stub` 递给 CarService，CarService 拿它做回调——这就是"推送"在 binder 世界的实现。
2. **弱引用**：反向 binder 桩持有 `WeakReference<CarPropertyManager>`，防止 App 忘 unregister 导致泄漏。
3. **错误码类型化**：App 不接触原始 `code 4`，而是拿到 `PropertyAccessDeniedSecurityException`——这就是"API 设计"：跨进程错误码在边界翻译成语义异常。

---

*黄金链路从 HAL 到 App 全部读完。下一步 W2D5 用 logcat/断点真跑一次。*