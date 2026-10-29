# W1D3 第二轮~第四轮 · 阅读指引

按顺序打开这三个文件，每个文件最上面标了「只看哪些方法、跳过什么」：

| 轮次 | 文件 | 目标 | 时间 |
|---|---|---|---|
| **第二轮** | [ServiceStarter-annotated.md](./ServiceStarter-annotated.md) | binder 的出生和第一次投递 | 20 min |
| **第三轮** | [ShizukuService-annotated.md](./ShizukuService-annotated.md) | server 启动与 binder 批量分发 | 20 min |
| **第四轮** | [BinderSender-annotated.md](./BinderSender-annotated.md) | 「时机探测器」——App 一启动 binder 自动到 | 15 min |

> 第一轮（架构图概览）已在 stepper 文档里完成，不需要再看文件。
> 对照源码：`~/projects/Shizuku-shallow/` 下的对应 .java 文件。

## 读完三份后的自检

你能不能用一段话讲清楚下面这件事（不看代码）：

> 一个 App 被用户点开 → App 进程被 AMS 创建 → 
> `BinderSender` 的 Observer 被回调 →
> 查权限通过 → `ShizukuService.sendBinderToUserApp()` →
> 找到 App 的 ContentProvider → 把 ShizukuService 的 binder 包装进 Bundle →
> `ContentProvider.call("sendBinder")` → App 收到 binder。

如果你能用 `→` 箭头把这串事件说出来，而不需要看代码——W1D3 就学完了。