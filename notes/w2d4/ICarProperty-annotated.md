# ICarProperty.aidl 注释版（App ↔ CarService 的 binder 契约）

> **10 分钟**。源码：`car-lib/src/android/car/hardware/property/ICarProperty.aidl`（43 行）

## 这个文件是什么

W2D3 读的 `CarPropertyService extends ICarProperty.Stub`，就是**这个接口的服务端**。
这里看到的 `ICarProperty`，是 App 侧 `CarPropertyManager` 拿到的**代理（proxy）**。

**事务码 0~7，就是 W2D3 服务端那几个方法的编号。**

```aidl
interface ICarProperty {
    // 订阅：注册一个回调（App 把自己的 binder 递给 CarService）
    void registerListener(int propId, float rate, in ICarPropertyEventListener callback) = 0;
    void unregisterListener(int propId, in ICarPropertyEventListener callback) = 1;

    List<CarPropertyConfig> getPropertyList() = 2;
    CarPropertyValue getProperty(int prop, int zone) = 3;                 // 读
    void setProperty(in CarPropertyValue prop, in ICarPropertyEventListener callback) = 4;  // 写
    String getReadPermission(int propId) = 5;
    String getWritePermission(int propId) = 6;
    List<CarPropertyConfig> getPropertyConfigList(in int[] propIds) = 7;
}
```

## 关键：这是"单向"契约，回调靠另一个 AIDL

注意 `registerListener` 的第三个参数 `ICarPropertyEventListener callback`——App 不是传一个函数指针，而是**把自己的 binder 对象（`ICarPropertyEventListener.Stub`）递给 CarService**。

于是有了**两个方向的 binder**：

```
App ──(正向) ICarProperty.getProperty/setProperty/registerListener ──▶ CarService
App ◀──(反向) ICarPropertyEventListener.onEvent ─────────────────────── CarService
```

这就是为什么 W2D3 里 `CarPropertyService.onPropertyChange` 能 `client.onEvent(...)` 把事件推回来——**那个 `client` 就是 App 传进来的反向 binder**。

## 和 W2D3 的对照（链路拼上了）

| 契约方法 | W2D3 服务端实现 | 本文件事务码 |
|---|---|---|
| `registerListener` | `CarPropertyService.registerListener` | 0 |
| `getProperty` | `CarPropertyService.getProperty` | 3 |
| `setProperty` | `CarPropertyService.setProperty` | 4 |
| `getReadPermission` | `CarPropertyService.getReadPermission` | 5 |

---

*下一步：`CarPropertyManager-annotated.md`（App 怎么用这个代理）*