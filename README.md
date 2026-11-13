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
├── articles/                    # 解读文章（问题 → 机制 → 验证）
│   └── 01-shizuku源码解读.md
├── notes/                       # 每个任务的 stepper 文档（任务卡 / 步骤 / 问题日志 / 自测）
│   ├── w1d1-环境搭建-stepper.md
│   ├── w1d2-dumpsys十连-stepper.md
│   ├── w1d3-shizuku导读-stepper.md
│   ├── w1d4-深读与问题清单-stepper.md
│   ├── w1d5-第一次改代码-stepper.md
│   ├── dumpsys/                 # 10 条系统服务 dump：逐段讲解 + 完整原始输出
│   └── w1d3/                    # Shizuku 源码逐行注释 + 架构时序图（HTML）
├── experiments/                 # 代码修改 patch / logcat 证据 / 截图
│   ├── w1d5-first-modification/ # 第一次改代码：patch + logcat + 构建信息
│   └── w2d1-aaos/               # AAOS 镜像：dumpsys car_service + 服务清单 + 构建信息
├── traces/                      # perfetto trace（W3 预留）
├── README.md
└── LICENSE
```

## 当前进度（11/28）

- [x] **W1D1** 环境搭建（cmdline-tools + arm64 模拟器 + AVD boot）
- [x] **W1D2** dumpsys 十连（10 条系统服务 dump，含逐段讲解）
- [x] **W1D3** Shizuku 导读（starter → service → BinderSender 架构图 + 源码逐行注释）
- [x] **W1D4** 深读与问题清单（attachApplication / observer / 去重 / UserService vs CarService）
- [x] **W1D5** 第一次改代码（加标记日志 → 构建 → logcat 验证，证据在 `experiments/`）
- [x] **W1D6** 文章底稿定稿《Shizuku 源码解读》（掘金暂缓，发布并入多平台分发待办）
- [x] **W1D7** 周复盘（[`notes/w1d7-周复盘.md`](./notes/w1d7-周复盘.md)）
- [x] **W2D1** AAOS 镜像试跑（Android 13 automotive arm64 启动成功，`dumpsys car_service` 1733 行）｜[车服务地图](./notes/w2d1-car-service-map.md)
- [x] **W2D2** dumpsys car_service 玩熟 + 属性读写 + service call 实验｜[stepper](./notes/w2d2-dumpsys-car-service实验-stepper.md)
- [x] **W2D3** 黄金链路精读（Vehicle HAL → CarService：读/写/事件三条路径 + 4 份逐行注释）｜[stepper](./notes/w2d3-黄金链路导读-stepper.md)
- [x] **W2D4** 精读 CarPropertyManager → 示例 App（双向 binder + 错误码翻译，黄金链路打通）｜[stepper](./notes/w2d4-黄金链路App侧-stepper.md)
- [ ] **W2** AAOS 黄金链路：Vehicle HAL → CarService → CarPropertyManager → App（进行中）

## 文章索引

| # | 标题 | 状态 |
|---|---|---|
| 01 | [Shizuku 源码解读：不用 Root，如何让 App 调用系统级 API？](./articles/01-shizuku源码解读.md) | v1 定稿（底稿） |

## 环境要求

- macOS（Apple Silicon）+ Android SDK（cmdline-tools / platform-tools / emulator）
- Android 14（API 34）`google_apis;arm64-v8a` 模拟器镜像
- 构建 Shizuku 额外需要：**NDK 29** + **JDK 21**（JDK 17 会报「无效的源发行版：21」）

## 更新记录

- 2026-10-30：W1D1-W1D2（环境 + dumpsys 十连）
- 2026-10-31：W1D3-W1D4（Shizuku 导读 + 深读）+ W1D5 环境搭建（NDK/Java 21）
- 2026-11-01：W1D5 首次改代码验证通过 + W1D6 文章 v1
- 2026-11-02：W1D6 文章底稿定稿；W1D7 周复盘 → **W1 完成（7/28）**；掘金暂缓，发布并入「多平台分发」待办
- 2026-11-03：W2D1 AAOS 镜像试跑成功（复合 tag + QEMU 逗号坑已解，`dumpsys car_service` 1733 行）
- 2026-11-03：W2D2 属性读写闭环 + service call 实验（事务码 11~19；`inject-vhal-event` 在模拟器不生效）
- 2026-11-03：W2D3 黄金链路精读（读/写/事件三条路径 + 4 份逐行注释 + AOSP 源码存档）
- 2026-11-03：W2D4 精读 CarPropertyManager → 示例 App（双向 binder + 错误码翻译，黄金链路打通）

## License

[MIT](./LICENSE)