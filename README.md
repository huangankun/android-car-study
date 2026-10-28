# Android 车载系统服务学习记录

> Android Car / System Services Study Notes —— 记录我从「跑 → 读 → 改 → 写」四个动作出发，系统性学习座舱 Android 系统服务的过程。每一条命令、每一份 dump、每一个踩过的坑都是真实发生过的。

## 这是什么

一个公开的学习仓库。目标是建立 Android 系统服务（WMS / AMS / binder 应用侧 / CarService）与调试手段（dumpsys / perfetto / logcat）的实战经验，并把每一步的源码解读、实验、踩坑记录下来。

背景：作者有 10 年 C++ 车载多媒体 Framework 开发经验（智能座舱、高通 8295/8155 平台），强项在 HAL、多媒体栈、图形层，短板是 Android 系统服务这一环。这个仓库就是补齐这一环的过程——不是教程合集，而是带**真实命令、真实输出、真实踩坑**的学习日志。

## 方法论：跑 → 读 → 改 → 写

1. **跑**：先在模拟器上把系统服务「跑起来、看输出」（dumpsys / logcat / service call）
2. **读**：定向精读源码（Shizuku → AOSP CarService），只读一条链，不横读失控
3. **改**：改一处代码，用 dumpsys / 日志验证自己的修改
4. **写**：每个阶段沉淀一篇「问题 → 机制 → 验证」的文章

## 学习路线（4 周）

| 周 | 主题 | 内容 |
|---|---|---|
| W1 | 环境 + Shizuku | dumpsys 十连、Shizuku 源码精读与修改 |
| W2 | AAOS 黄金链路 | Vehicle HAL → CarService → CarPropertyManager → App |
| W3 | 改代码 + perfetto | CarService 加 dump 字段、perfetto 抓车控 trace |
| W4 | CarLauncher + 收尾 | dumpsys window、仓库收尾、面试 10 题 |

## 目录结构

```
.
├── notes/          # 每个任务的 stepper 文档（任务卡 / 执行步骤 / 问题日志 / 自测）
│   └── dumpsys/    # 10 条系统服务 dump：逐段讲解 + 完整原始输出
├── articles/       # 每篇解读文章（问题 → 机制 → 验证）
├── experiments/    # 代码修改补丁、logcat 日志、截图
└── traces/         # perfetto trace 文件
```

## 当前进度

- [x] W1D1 环境搭建（cmdline-tools + arm64 模拟器镜像 + AVD boot）
- [x] W1D2 dumpsys 十连（10 条系统服务 dump，含逐段讲解）
- [ ] W1D3 Shizuku 导读（starter → service → BinderSender）
- [ ] 后续任务（共 28 个，随进度更新）

## 环境要求

- macOS（Apple Silicon）+ Android SDK（cmdline-tools / platform-tools / emulator）
- Android 14（API 34）`google_apis;arm64-v8a` 模拟器镜像
- `adb` / `sdkmanager` / `emulator` 已加入 PATH

## 文章索引

文章发布后在此登记（掘金 + 本仓库 `articles/` 同步）。

## License

[MIT](./LICENSE)
