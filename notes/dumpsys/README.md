# notes/dumpsys/

W1D2 的 10 条系统服务 dump，每条都是「讲解版」：**服务是什么 / 输出在讲什么 / 逐段讲解 / 关键字段 / 完整原文**。

| 文件 | 服务 | 一句话 |
|---|---|---|
| [01-activity.md](./01-activity.md) | ActivityManagerService | 任务栈、前台 Activity |
| [02-window.md](./02-window.md) | WindowManagerService | 窗口列表、z 顺序、焦点窗 |
| [03-package.md](./03-package.md) | PackageManagerService | 单包档案、Resolver Table、权限 |
| [04-permission.md](./04-permission.md) | （Android 14 死命令） | 替代：`pm list permissions -g` |
| [05-power.md](./05-power.md) | PowerManagerService | 唤醒状态、wakelock |
| [06-battery.md](./06-battery.md) | BatteryService | 供电/电量/健康 |
| [07-meminfo.md](./07-meminfo.md) | AMS 内存 | PSS/RSS、Total/Free/Used |
| [08-cpuinfo.md](./08-cpuinfo.md) | CPU | Load、每进程 CPU |
| [09-gfxinfo.md](./09-gfxinfo.md) | 图形渲染 | Janky frames、帧耗时 |
| [10-services.md](./10-services.md) | AMS services | 运行中的 App Service |

> 原始 dump 备份在 `~/.hermes/cache/scratch/dumpsys_raw_backup/`（不进仓库）。