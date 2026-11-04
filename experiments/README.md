# experiments/

每次「改代码 / 跑环境」的证据放在这里：补丁、logcat、截图、dump。

| 目录 | 内容 |
|---|---|
| [w1d5-first-modification/](./w1d5-first-modification/) | 第一次改 Shizuku 代码：patch + logcat 标记 + 构建信息 |
| [w2d1-aaos/](./w2d1-aaos/) | AAOS 镜像试跑：dumpsys car_service + 33 服务清单 + 构建信息 + 截图 |
| [w2d2/](./w2d2/) | 属性读写实验：398 条属性配置 + service call 原始输出 + VHAL 注入测试 |

约定：
- 每个实验一个子目录，命名 `<周次/日期>-<主题>/`
- 记录：改了什么、怎么验证、观察到了什么
- 新实验先在这里登记，再更新根 README 的「更新记录」