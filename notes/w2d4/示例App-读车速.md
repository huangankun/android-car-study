# 示例 App：读车速（PERF_VEHICLE_SPEED）

> 一个最简 App 片段，展示 App 侧怎么用 `CarPropertyManager` 订阅和读取车速。
> 这是整条黄金链路的「第 ⑤ 段（App）」的落点。

```java
public class SpeedActivity extends Activity {
    private CarPropertyManager mCarPropertyManager;
    private TextView tvSpeed;

    // 订阅回调：CarService 推事件时，最终会调到这里的 onChangeEvent
    private final CarPropertyEventCallback mSpeedCallback = new CarPropertyEventCallback() {
        @Override
        public void onChangeEvent(CarPropertyValue value) {
            float speed = (Float) value.getValue();          // ★ 拿到车速（float）
            runOnUiThread(() -> tvSpeed.setText(
                    String.format(Locale.US, "%.1f km/h", speed)));
        }
        @Override
        public void onErrorEvent(CarPropertyValue value, int errorCode) {
            // errorCode 4 = ACCESS_DENIED（写只读属性才会走到这）
            Log.e(TAG, "speed property error: " + errorCode);
        }
    };

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        // ① 连 Car 服务（异步），拿到 CarPropertyManager
        Car.createCar(this, /* handler= */ null, Car.CAR_WAIT_TIMEOUT_DO_NOT_WAIT,
                (car, ready) -> {
                    if (!ready) return;
                    mCarPropertyManager = (CarPropertyManager)
                            car.getCarManager(Car.PROPERTY_SERVICE);

                    // ② 订阅车速（continuous 属性，用 FAST 采样率）
                    mCarPropertyManager.registerCallback(
                            mSpeedCallback,
                            VehiclePropertyIds.PERF_VEHICLE_SPEED,
                            CarPropertyManager.SENSOR_RATE_FAST);

                    // ③ 或者一次性读当前值（get 是同步跨进程）
                    CarPropertyValue<Float> v = mCarPropertyManager.getProperty(
                            Float.class,
                            VehiclePropertyIds.PERF_VEHICLE_SPEED,
                            VehicleAreaSeat.SEAT_ROW_1_LEFT);
                    if (v != null) {
                        tvSpeed.setText(String.valueOf(v.getValue()));
                    }
                });
    }

    @Override
    protected void onDestroy() {
        mCarPropertyManager.unregisterCallback(mSpeedCallback);   // ★ 别忘了反注册
        super.onDestroy();
    }
}
```

## 逐段对照链路

| 代码 | 对应链路段 |
|---|---|
| `Car.createCar(...)` | 拿到 `Car` 对象（连 CarService 的门面） |
| `car.getCarManager(Car.PROPERTY_SERVICE)` | 拿到 `CarPropertyManager`（持有 ICarProperty 代理） |
| `registerCallback(...)` | `mService.registerListener`（ICarProperty code 0）→ W2D3 服务端 |
| `onChangeEvent(value)` | ← `client.onEvent`（反向 binder）→ `CarPropertyEventListenerToService` → 这里 |
| `getProperty(Float.class, ...)` | `mService.getProperty`（code 3）→ ... → IVehicle.getValues |
| `unregisterCallback(...)` | `mService.unregisterListener`（code 1） |

## 注意

- `PERF_VEHICLE_SPEED` 是 `changeMode:0x2`（continuous），`registerCallback` 才有效；`get` 拿的是瞬间值。
- `Car.createCar` 是异步的（要等 CarService binder 连上），不能同步拿 manager。
- 写只读属性（如档位）→ `onErrorEvent` 收到 `errorCode 4`，对应 `PropertyAccessDeniedSecurityException`。