# W1D2 · dumpsys 十连 Stepper 文档（✅ 完成）

> 任务：用 10 条 `dumpsys` 命令给模拟器做一次「系统体检」，每条输出存档 + 一句话说明它讲了什么。
> 执行人：Hermes（导师）｜学习者：先生（文档 + 自测）
> 最终状态：✅ 10 条命令全部执行，10 个存档落盘 `notes/dumpsys/01~10`；其中 `dumpsys permission` 被证实是死命令，已用 `pm list permissions -g` 替换存档（详见 P2）。

## 任务卡

- **目标**：dumpsys 是系统服务调试的**第一入口**——任何一个服务都能被 `dumpsys <服务名>` 拉出实时状态。今天把 10 个高频服务的 dump 跑一遍、读一遍关键字段，为 W1D3-5（Shizuku）和 W2（AAOS 车控诊断）打底。座舱里排查「车机卡顿/窗口异常/权限不通」，第一步永远是先 dumpsys。
- **知识点清单**（自测从这里出题）：
  1. `dumpsys` 的底层机制：ServiceManager 按名找服务 → binder 调服务的 `dump(fd, pw, args)` → 打印到文件描述符
  2. `dumpsys -l`（列可 dump 服务）和 `service list`（列 binder 接口真名）的区别
  3. AMS 的活动栈 / task / ResumedActivity 概念（ActivityManagerService）
  4. WMS 的窗口列表、z-order、token、焦点窗（WindowManagerService）
  5. PackageManager 的包元信息 / 权限 / 组件
  6. PowerManager 的状态机字段：`mWakefulness`、wakelock、SuspendBlocker
  7. BatteryService 的状态码：`status` / `health` / `level` / `scale` 各是几、什么含义
  8. `meminfo` 的 PSS 内存模型（Total/Free/Used RAM、cached pss、kernel）
  9. `cpuinfo` 的 Load 三段值 + per-process 耗时
  10. `gfxinfo` 的帧渲染统计（Total/Janky frames）——图形栈强项
  11. `dumpsys activity services`：系统里当前「活着的」服务全景

## 执行步骤

### S1 · 环境探底 ❌→✅（发现模拟器没在跑）
```bash
adb devices -l        # 空 —— 没有设备！
pgrep -fl qemu        # 空 —— 模拟器进程不存在
```
**讲解**：你印象里「study 在跑着」是过时状态（可能崩了或被关了）。`adb devices` 是唯一真相源——**任何 `adb shell` 操作前先 `adb devices`**。这是今天的第一个真实坑（P1）。

### S2 · 重启模拟器 + 等 boot ✅
```bash
emulator -avd study -no-snapshot -gpu auto -no-audio -no-boot-anim   # 后台跑
adb wait-for-device shell getprop sys.boot_completed                  # 轮询直到返回 1
adb devices      # emulator-5554  device（Android 14 · arm64-v8a）
```
**讲解**：`getprop sys.boot_completed == 1` 是「系统真起完了」的官方信号（adb 连上 ≠ 系统就绪）。今天 3 次轮询就 ready，比昨天 12 秒还快。

### S3 · 建目录 + 十连归档 ✅
```bash
mkdir -p ~/projects/android-car-study/notes/dumpsys
# 每条：{ 命令头 + 生成时间 + adb shell <cmd> 全量输出 } > 存档文件
```
**讲解**：每条存档顶部记了「命令 + 时间」，以后回溯知道这份 dump 是哪天、哪个状态抓的。真实行数：activity 364 / window 458 / package 2808 / permission 8→1373 / power 997 / battery 24 / meminfo 645 / cpuinfo 105 / gfxinfo 1444 / services 3142。

### S4 · 十连结果一句话笔记 ✅
见下方「十连笔记」表——每条都从真实输出里抓了关键字段，不是空谈。

### S5 · 两个「异常」排查 ✅
`04-permission.md` 只有 8 行、`06-battery.md` 只有 428 字节，都先读内容再下结论（P2、P3）。

## 十连笔记（每条 dump 在说什么 + 真实关键字段）

| # | 命令 | 这段输出说明什么 | 本次真实关键字段 |
|---|---|---|---|
| 01 | `dumpsys activity activities` | **任务栈全景**：所有 Activity 栈、task、谁在前台 RESUMED | `topResumedActivity = com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6`（Launcher 在前台，taskId=6） |
| 02 | `dumpsys window windows` | **窗口列表 + z-order**：从上到下每个 Window、token、焦点 | `Window #0 ScreenDecorOverlayBottom` … `Window #3 EdgeBackGestureHandler0`（z-order 越小越靠上） |
| 03 | `dumpsys package com.android.settings` | **单个包的档案**：版本、sdk、权限、组件、安装信息 | `versionName=14 versionCode=34 minSdk=34 targetSdk=34`，含 464 处 `android.permission` 引用 |
| 04 | `dumpsys permission` → **空** | 本该是运行时权限状态，实际是死命令 | 见 P2，已用 `pm list permissions -g` 替代 |
| 05 | `dumpsys power` | **电源状态机**：屏亮灭、wakelock、SuspendBlocker | `mWakefulness=Awake`、`mHoldingWakeLockSuspendBlocker=true`（有 wakelock 阻止系统休眠） |
| 06 | `dumpsys battery` | **电池状态**：供电方式、电量、温度、电压 | `level=100 scale=100 status=4(NOT_CHARGING) health=2(GOOD) voltage=5000mV temperature=250(25.0℃)` |
| 07 | `dumpsys meminfo` | **全局内存**：Total/Free/Used RAM、PSS 明细 | `Total RAM 2,537,912K · Free 1,135,253K · Used 1,553,467K`（模拟器默认 2.4GB） |
| 08 | `dumpsys cpuinfo` | **CPU 负载 + 每进程耗时** | `Load: 3.06 / 0.81 / 0.27`（1/5/15 分钟负载），`27% TOTAL` |
| 09 | `dumpsys gfxinfo` | **渲染帧统计**：总帧数、janky 帧、各 app 帧耗时 | `Total frames rendered: 11 · Janky frames: 8 (72.73%)`（刚 boot，Launcher 冷启动全是 jank） |
| 10 | `dumpsys activity services` | **系统服务全景**：每个 user 下当前活着的服务清单 | `User 0 active services:` 列表（AMS 自己打的服务清单，W1D3 读 Shizuku 服务时要用） |

## 问题日志（这节课的全部含金量）

| # | 症状 | 原因 | 解法 |
|---|---|---|---|
| P1 | `adb devices` 空、`pgrep qemu` 空 | 模拟器早就不在跑了（用户印象里的「在跑」是过时状态），任何 adb 操作都会「无设备」 | 操作前先 `adb devices` 探活；不在就 `emulator -avd study ...` 重启 + `getprop sys.boot_completed` 等 boot |
| P2 | `dumpsys permission` 输出为空：exit 0、无报错，**shell 和 root 都试过** | Android 10 起 PermissionController 独立成 App，`permission` 服务名退化成 `IPermissionController` 遗留桩，无 dump 实现（`service list` 可见 `permission: [android.os.IPermissionController]`；真身 `permissionmgr` 在此镜像上也无输出）。这是计划附录 B 里的**过时命令** | 用 `pm list permissions -g`（按组列全量权限）或 `dumpsys package <pkg>` 的 runtime permissions 段替代；计划附录 B 已同步更正 |
| P3 | 误以为 `06-battery` 428 字节是「异常小」 | battery dump 本来就紧凑，24 行已是完整输出（不像 package/gfxinfo 动辄上千行） | **先读内容再下「异常」结论**，别用文件大小猜状态 |
| P4 | 排查 permission 时发现镜像可 `adb root` | 这个 google_apis 镜像是 `userdebug`（`ro.build.type=userdebug`、`ro.debuggable=1`），不是 user build，adbd 能切 root | W1D5 改 Shizuku 代码 / 加日志时直接 `adb root` + `adb remount`，不用绕。排查完记得 `adb unroot` 恢复 |

## 面试高频命令（请亲手敲一遍）

```bash
adb shell dumpsys activity activities      # 任务栈：谁在前台、几个 task（面试必问）
adb shell dumpsys window windows           # 窗口 z-order 与 token（WMS 入口，座舱高频）
adb shell dumpsys meminfo <包名>           # 单进程 PSS 内存（你最该讲深的一条）
adb shell dumpsys gfxinfo <包名>           # 该 app 的帧渲染统计（图形栈强项）
```

## 自测（3 题，做完喊我，我们对答案）

1. `adb shell dumpsys activity` 这条命令，从你敲下回车到看到输出，底层走了哪几步？（提示：ServiceManager / binder / dump 方法。答案线索在「任务卡·知识点清单 1」和 S3）
2. 打开 `notes/dumpsys/01-activity.md`，`topResumedActivity` 是哪个 App？为什么是它、`t6` 是什么？（答案线索在「十连笔记」01 行）
3. `dumpsys permission` 为什么是空的？给我两个能用的替代命令，并说出 `service list` 里 `permission` 服务对应的 binder 接口真名是什么。（答案线索在 P2）

---

*本文件由导师会话生成，归档至 `~/projects/android-car-study/notes/`；10 份原始 dump 在 `notes/dumpsys/`*
