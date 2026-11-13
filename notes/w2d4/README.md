# W2D4 · App 侧逐行注释阅读指引

按顺序读：

| 顺序 | 文件 | 目标 | 时间 |
|---|---|---|---|
| **第一份** | [ICarProperty-annotated.md](./ICarProperty-annotated.md) | binder 契约（事务码 0~7）+ 双向 binder | 10 min |
| **第二份** | [CarPropertyManager-annotated.md](./CarPropertyManager-annotated.md) | App 侧 API + 错误码翻译 | 25 min |
| **第三份** | [示例App-读车速.md](./示例App-读车速.md) | 一个最简 App 怎么读车速 | 10 min |
| **概念** | [概念辨析.md](./概念辨析.md) | Stub 与 Binder、强弱类型、Class&lt;E&gt; 为什么 | 15 min |

> 原始文件已存档在 [src/](./src/)（AOSP Apache 2.0）。

## 读完三份后的自检

不看代码，用一段话讲清楚：

> App 调 `CarPropertyManager.registerCallback(callback, PERF_VEHICLE_SPEED, FAST)` →
> 内部造一个 `ICarPropertyEventListener.Stub`（反向 binder）→
> `mService.registerListener(propId, rate, 这个binder)`（code 0）→
> CarService 记住这个 binder → 以后 VHAL 有车速变化 →
> `client.onEvent(events)` 跨进程回调这个 binder →
> App 主线程 `onChangeEvent(22.5)`。

**能说清「反向 binder 怎么让推送成立」，W2D4 就学完了。**