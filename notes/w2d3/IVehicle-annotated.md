# IVehicle.aidl 注释版（HAL 接口契约）

> **只看这 5 个方法**，跳过全部 Javadoc 长注释与 shared memory 细节。
> 预计 **10 分钟**。源码：`hardware/interfaces/automotive/vehicle/aidl/.../IVehicle.aidl`（android13-release，255 行）

## 这个文件是什么

Vendor 侧 VHAL 与 CarService 之间的 **AIDL 契约**。CarService 拿着 `IVehicle` 这个 binder 代理，就能跨进程调 vendor 的 VHAL。

**一句话记住：`getValues` / `setValues` / `subscribe` 三个方法，全部异步、全部带 callback。**

```aidl
@VintfStability
interface IVehicle {
    const long INVALID_MEMORY_ID = 0;
    const int MAX_SHARED_MEMORY_FILES_PER_CLIENT = 3;

    // ① 拿全部属性配置（CarService 启动时调一次，建立"车能提供什么"的地图）
    VehiclePropConfigs getAllPropConfigs();
    // ② 拿指定属性的配置
    VehiclePropConfigs getPropConfigs(in int[] props);

    // ③ 异步读：结果通过 callback.onGetValues 回来
    //    ← 注意：not "returns value"，而是"发请求 + 等回调"
    void getValues(IVehicleCallback callback, in GetValueRequests requests);

    // ④ 异步写：结果通过 callback.onSetValues 回来
    void setValues(IVehicleCallback callback, in SetValueRequests requests);

    // ⑤ 订阅：VHAL 有变化就通过 callback.onPropertyEvent 推上来
    //    callback：onPropertyEvent（值变）/ onPropertySetError（写失败）
    //    options：属性 id + areaId + 采样率（continuous 属性必须给）
    void subscribe(in IVehicleCallback callback, in SubscribeOptions[] options,
            int maxSharedMemoryFileCount);

    void unsubscribe(in IVehicleCallback callback, in int[] propIds);

    // 共享内存回收：onPropertyEvent 里拿到的 buffer 用完要还
    void returnSharedMemory(in IVehicleCallback callback, long sharedMemoryId);
}
```

## 三个"面试级"设计点

1. **为什么全异步？**
   VHAL 背后是 CAN/LIN 总线，取一个值可能要等总线响应（几十 ms）。如果同步等，CarService 的 binder 线程会被堵死。所以设计成「发请求，立刻返回，结果走 callback」。

2. **`subscribe` 的 sampleRate 是"建议值"**
   文档明确：实际推送频率受 VHAL 轮询率约束。你订阅 7Hz，VHAL 只有 5Hz/10Hz 轮询，那就给 5Hz。**这就是为什么车速这种 CONTINUOUS 属性能做到"按帧更新"，而 ON_CHANGE 属性只在变化时才推。**

3. **共享内存（`maxSharedMemoryFileCount`）**
   一次推几百个属性时，binder 一次拷贝扛不住，用共享内存传。**这是车机上"高频数据"的标准做法**，和多媒体传帧是同一类思路（你在 C++ 里应该很熟）。

## 和 W2D2 实验的对应

- W2D2 的 `get-property-value` → 最终落到 `IVehicle.getValues()`（经 HalClient 封装成同步等待）
- W2D2 的 `set-property-value` → `IVehicle.setValues()`
- W2D2 的 `inject-vhal-event` → **不走 IVehicle**！它只在 CarService 内部伪造 `onPropertyEvent`（这就是为什么 get 读不到）

---

*下一步：看 CarService 怎么用这个接口 → `VehicleHal-annotated.md`*