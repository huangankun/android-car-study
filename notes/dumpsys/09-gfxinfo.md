# dumpsys 存档：09-gfxinfo.md（讲解版 · 图形栈强项）

命令：`adb shell dumpsys gfxinfo`

**这个服务是什么**：图形渲染的帧统计（GraphicsInfo），回答「每个进程渲染了多少帧、多少帧卡顿（jank）、帧耗时分布、GPU 缓存」。

**这段输出在讲什么**：刚 boot 完，两个前台相关进程的帧统计全是「冷启动式卡顿」——Google 搜索 11 帧里 8 帧 jank（72.73%），Launcher 4 帧里 3 帧 jank。这是冷启动的典型画像，不代表常态。

## 逐段讲解

### 1. 每进程帧统计头：jank 定义就在这

```text
** Graphics info for pid 1632 [com.google.android.googlequicksearchbox:search] **

Stats since: 13284385797ns
Total frames rendered: 11
Janky frames: 8 (72.73%)
50th percentile: 17ms
90th percentile: 200ms
95th percentile: 300ms
99th percentile: 300ms
```

**讲解**：`Janky frames` 是核心——**一帧超过 16.67ms（60fps 的帧预算）就算 jank**。11 帧里 8 帧超时，是因为进程刚启动、第一帧要加载整个 UI。`50th percentile: 17ms` 表示一半的帧 17ms 内完成（刚好卡在预算线上），`99th: 300ms` 表示最慢的那 1% 帧要 300ms（冷启动那几帧）。**面试问「怎么判断卡顿」，答案：gfxinfo 里的 Janky frames 比例 + percentile。**

### 2. 卡顿归因：这几行告诉你「为什么慢」

```text
Number Missed Vsync: 5       # 错过垂直同步信号 5 次
Number High input latency: 2 # 输入到响应延迟高 2 次
Number Slow UI thread: 4     # 主线程慢 4 次（UI 线程被阻塞）
Number Slow bitmap uploads: 1# 位图上传慢 1 次
Number Slow issue draw commands: 6  # 绘制指令下发慢 6 次
Number Frame deadline missed: 8     # 超过帧截止 8 次
```

**讲解**：这是 jank 的**归因分解**，比一个笼统的「卡」有用得多：
- `Slow UI thread` → 主线程做了重活（布局/测量/GC），该优化主线程。
- `Slow bitmap uploads` → 大图上传 GPU 慢，该缩图。
- `Missed Vsync` → 渲染没赶上垂直同步，画面撕裂/掉帧。

**做性能分析时，先看这六行定位瓶颈在哪一层，再对症下药。**

### 3. HISTOGRAM：帧耗时的完整分布

```text
HISTOGRAM: 5ms=0 6ms=0 7ms=1 8ms=0 ... 16ms=2 17ms=1 ... 300ms=1 ...
```

**讲解**：这是一张**帧耗时的直方图**——`7ms=1` 表示有 1 帧花了 7ms，`300ms=1` 表示有 1 帧花了 300ms。看分布比看平均值准：大部分帧挤在 16ms 附近说明基本流畅，尾巴拖到几百 ms 说明有偶发卡顿（通常是冷启动或 GC）。

### 4. 渲染管线与缓存

```text
Pipeline=Skia (OpenGL)
Memory policy:
  Max resource usage: 124.42MB (x48)
  Background retention: 50%
CPU Caches:
  Glyph Cache: 416.00 bytes (1 entry)
Total GPU memory usage:
  0 bytes, 0.00 bytes (0.00 bytes is purgeable)
```

**讲解**：`Pipeline=Skia (OpenGL)` 说明这台模拟器用 **Skia 渲染引擎 + OpenGL 后端**（真机高端 GPU 可能是 Vulkan）。`Max resource usage` 是 GPU 资源预算。**你的图形栈背景在这里能直接展开：Skia 是 Android 2D 渲染引擎，UI 的 draw 调用最终都进 Skia 再交给 GPU。**

### 5. Per-window 统计（第 53 行起）

文件后面还有按窗口（ViewRootImpl）拆分的帧统计，格式和上面一样，只是粒度到了单个窗口。查「哪个页面卡」就用这个。

**一句话结论**：`dumpsys gfxinfo` 是「渲染卡顿的体检单」——Janky frames 看卡不卡，六行归因看卡在哪，HISTOGRAM 看分布。配合 `adb shell dumpsys gfxinfo <包名> reset` 可以清零后复测。

## 完整原始输出


```text
Applications Graphics Acceleration Info:
Uptime: 37467 Realtime: 37467

** Graphics info for pid 1632 [com.google.android.googlequicksearchbox:search] **

Stats since: 13284385797ns
Total frames rendered: 11
Janky frames: 8 (72.73%)
Janky frames (legacy): 5 (45.45%)
50th percentile: 17ms
90th percentile: 200ms
95th percentile: 300ms
99th percentile: 300ms
Number Missed Vsync: 5
Number High input latency: 2
Number Slow UI thread: 4
Number Slow bitmap uploads: 1
Number Slow issue draw commands: 6
Number Frame deadline missed: 8
Number Frame deadline missed (legacy): 5
HISTOGRAM: 5ms=0 6ms=0 7ms=1 8ms=0 9ms=0 10ms=0 11ms=1 12ms=0 13ms=0 14ms=1 15ms=0 16ms=2 17ms=1 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=1 53ms=0 57ms=0 61ms=0 65ms=1 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=1 125ms=0 129ms=0 133ms=0 150ms=0 200ms=1 250ms=0 300ms=1 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 11ms
90th gpu percentile: 18ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=1 3ms=2 4ms=0 5ms=0 6ms=0 7ms=1 8ms=1 9ms=0 10ms=0 11ms=1 12ms=0 13ms=0 14ms=0 15ms=0 16ms=1 17ms=2 18ms=1 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=1

Pipeline=Skia (OpenGL)
Memory policy:
  Max surface area: 2592000
  Max resource usage: 124.42MB (x48)
  Background retention: 50% (altUiHidden = true)
  GPU Context timeout: 10
Contexts: 1 (stopped = 0)
CPU Caches:
  Glyph Cache: 416.00 bytes (1 entry)
  Glyph Count: 1 
Total CPU memory usage:
  416 bytes, 416.00 bytes (0.00 bytes is purgeable)
GPU Caches:
  Other:
    Other: 0.00 bytes (1 entry)
Total GPU memory usage:
  0 bytes, 0.00 bytes (0.00 bytes is purgeable)

Profile data in ms:

	com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity/android.view.ViewRootImpl@4b655d7 (visibility=0)
Window: com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity
Stats since: 16071229673ns
Total frames rendered: 4
Janky frames: 3 (75.00%)
Janky frames (legacy): 2 (50.00%)
50th percentile: 48ms
90th percentile: 121ms
95th percentile: 121ms
99th percentile: 121ms
Number Missed Vsync: 2
Number High input latency: 2
Number Slow UI thread: 1
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 2
Number Frame deadline missed: 3
Number Frame deadline missed (legacy): 2
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=1 15ms=0 16ms=1 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=1 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=1 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 16ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=1 9ms=0 10ms=0 11ms=1 12ms=0 13ms=0 14ms=0 15ms=0 16ms=1 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=1



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
1,4935,16079756933,16163090263,0,16174441132,16174441424,16174441549,16195267507,16096423599,16174427132,16666666,16195575340,16195706424,16195745049,16195824090,16203425674,2083,70250,16203425674,16197653715,0,16195824090,
0,5009,16179756929,16196423595,0,16201415257,16201415507,16201465215,16201863424,16229756927,16201411507,16666666,16202250132,16202421674,16202451382,16202516549,16230092882,2083,83125,16230092882,16203447424,0,16202516549,
0,5068,16229756927,16229756927,0,16231878299,16231878549,16231946424,16233111465,16263090259,16231876424,16666666,16233207174,16235757965,16235784049,16235838132,16246729632,1250,67542,16246729632,16239450924,0,16235838132,
0,5306,16413090253,16413090253,0,16413602090,16413602174,16413602299,16413926924,16429756919,16413600299,16666666,16413974174,16414091965,16414125424,16414180049,16430040924,1708,147500,16430040924,16414849340,0,16414180049,
---PROFILEDATA---


View hierarchy:

  com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity/android.view.ViewRootImpl@4b655d7
  56 views, 91.07 kB of render nodes


Total ViewRootImpl   : 1
Total attached Views : 56
Total RenderNode     : 91.07 kB (used) / 227.21 kB (capacity)


** Graphics info for pid 1054 [com.google.android.apps.nexuslauncher] **

Stats since: 12390557672ns
Total frames rendered: 44
Janky frames: 10 (22.73%)
Janky frames (legacy): 5 (11.36%)
50th percentile: 16ms
90th percentile: 31ms
95th percentile: 117ms
99th percentile: 250ms
Number Missed Vsync: 3
Number High input latency: 45
Number Slow UI thread: 2
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 7
Number Frame deadline missed: 10
Number Frame deadline missed (legacy): 3
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=1 13ms=0 14ms=2 15ms=0 16ms=22 17ms=11 18ms=0 19ms=1 20ms=1 21ms=0 22ms=0 23ms=1 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=1 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=1 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=1 121ms=0 125ms=0 129ms=0 133ms=0 150ms=1 200ms=0 250ms=1 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 15ms
90th gpu percentile: 17ms
95th gpu percentile: 17ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=2 4ms=0 5ms=1 6ms=0 7ms=0 8ms=1 9ms=0 10ms=0 11ms=1 12ms=1 13ms=2 14ms=4 15ms=10 16ms=14 17ms=3 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=1 24ms=0 25ms=0 4950ms=1

Pipeline=Skia (OpenGL)
Memory policy:
  Max surface area: 2592000
  Max resource usage: 124.42MB (x48)
  Background retention: 50% (altUiHidden = true)
  GPU Context timeout: 10
Contexts: 1 (stopped = 0)
CPU Caches:
  Glyph Cache: 77.64 KB (1 entry)
  Glyph Count: 10 
Total CPU memory usage:
  79505 bytes, 77.64 KB (0.00 bytes is purgeable)
GPU Caches:
  Other:
    Other: 8.31 KB (1 entry)
  Image:
    Texture: 189.46 KB (13 entries)
  Scratch:
    RenderTarget: 192.00 KB (3 entries)
    Buffer Object: 142.00 KB (4 entries)
    Texture: 2.16 MB (6 entries)
Total GPU memory usage:
  2807656 bytes, 2.68 MB (298.13 KB is purgeable)

Profile data in ms:

	com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity/android.view.ViewRootImpl@60caa61 (visibility=0)
Window: com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity
Stats since: 16039828423ns
Total frames rendered: 16
Janky frames: 6 (37.50%)
Janky frames (legacy): 4 (25.00%)
50th percentile: 17ms
90th percentile: 150ms
95th percentile: 250ms
99th percentile: 250ms
Number Missed Vsync: 2
Number High input latency: 15
Number Slow UI thread: 2
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 4
Number Frame deadline missed: 6
Number Frame deadline missed (legacy): 2
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=1 13ms=0 14ms=0 15ms=0 16ms=7 17ms=2 18ms=0 19ms=1 20ms=1 21ms=0 22ms=0 23ms=1 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=1 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=1 200ms=0 250ms=1 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 16ms
90th gpu percentile: 23ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=2 4ms=0 5ms=1 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=1 14ms=1 15ms=2 16ms=5 17ms=2 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=1 24ms=0 25ms=0 4950ms=1



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
1,4796,15929756939,16029756935,0,16046046632,16046047215,16046107423,16178627632,15946423605,16044581757,16666666,16179115882,16180756715,16180806632,16183028715,16185832340,1542,215125,16185812174,16185832340,0,16183028715,
0,4913,16063090267,16229756927,0,16241238757,16241239090,16241347174,16241400882,16213090261,16239249590,16666666,16241450299,16241460257,16241486507,16241937882,16246727715,2083,98625,16246727715,16242965257,0,16241937882,
0,5097,16246423593,16246423593,0,16261476549,16261476882,16263900882,16263949840,16279756925,16261473632,16666666,16264188590,16264198799,16264233590,16264856132,16267019465,1708,107125,16267019465,16265778257,0,16264856132,
0,5126,16263090259,16263090259,0,16266131132,16266131215,16266162507,16266177049,16296423591,16266129757,16666666,16266196090,16266201715,16266212924,16266603007,16282853132,14804958,47541,16282853132,16281855590,0,16266603007,
0,5148,16279756925,16279756925,0,16280470090,16280470215,16280521257,16280551590,16313090257,16280468174,16666666,16280596257,16281862215,16281890424,16282362340,16304935924,15484250,60458,16304935924,16298377215,0,16282362340,
0,5177,16296423591,16296423591,0,16296812049,16296812507,16296880965,16296913215,16329756923,16296809132,16666666,16296954674,16304094632,16304125965,16304467174,16316469424,10374291,123625,16316469424,16315370424,0,16304467174,
0,5199,16313090257,16313090257,0,16313539924,16313540007,16313590257,16313618465,16346423589,16313538007,16666666,16313659382,16315383799,16315408215,16315792215,16346636174,15896959,86459,16346636174,16332396590,0,16315792215,
0,5495,16679756909,16679756909,0,16682079924,16682080174,16682080257,16682126465,16696423575,16682074799,16666666,16682239965,16682250965,16682284382,16682798840,16696589465,1667,66792,16696589465,16683255507,0,16682798840,
0,5531,16696423575,16696423575,0,16696662090,16696662507,16696704174,16696731215,16729756907,16696659840,16666666,16696770424,16696782757,16696805674,16697226132,16713657215,467542,139875,16713657215,16698272757,0,16697226132,
0,5560,16713090241,16713090241,0,16713894215,16713894382,16713941049,16713971049,16746423573,16713892507,16666666,16714014049,16714029840,16714054340,16714479840,16729927799,36833,109208,16729927799,16715346174,0,16714479840,
0,5582,16729756907,16729756907,0,16730074507,16730075007,16730126674,16730157507,16763090239,16730072007,16666666,16730201840,16730210382,16730232465,16730737340,16746595382,26875,103333,16746595382,16731380007,0,16730737340,
0,5611,16746423573,16746423573,0,16746665007,16746665132,16746717215,16746744674,16779756905,16746663090,16666666,16746788007,16746800715,16746826549,16747468382,16763246465,320125,72959,16763246465,16748529715,0,16747468382,
0,5633,16763090239,16763090239,0,16763382424,16763382882,16763442632,16763472757,16796423571,16763379715,16666666,16763515382,16763524757,16763555174,16764110132,16779897632,166125,135750,16779897632,16765200299,-1,16764110132,
0,5655,16779756905,16779756905,0,16780296965,16780297174,16780366840,16780397965,16813090237,16780294965,16666666,16780443090,16780494757,16780604507,16781046132,16796701799,109291,219250,16796701799,16781906799,22,16781046132,
0,8945,24229761982,24229761982,0,24230114594,24230114719,24231449844,24231467844,24246428648,24230113219,16666665,24231510261,24231634677,24231909552,24232642052,24246820802,1708,110083,24246820802,24237715886,0,24232642052,
0,8973,24279756605,24279756605,0,24280665511,24280665677,24281520052,24281538969,24296423271,24280616761,16666666,24281578552,24281649886,24281684136,24282126094,24297027219,1875,134000,24297027219,24282933344,-1,24282126094,
---PROFILEDATA---


View hierarchy:

  com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity/android.view.ViewRootImpl@60caa61
  106 views, 156.13 kB of render nodes


Total ViewRootImpl   : 1
Total attached Views : 106
Total RenderNode     : 156.13 kB (used) / 284.40 kB (capacity)


** Graphics info for pid 1344 [com.google.android.gms.persistent] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2358 [com.google.android.apps.messaging] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2374 [com.google.android.gms.unstable] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1659 [com.google.android.gms] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2753 [com.google.android.apps.messaging:rcs] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1495 [com.google.process.gservices] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1318 [com.google.android.permissioncontroller] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1758 [android.process.acore] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3297 [com.google.android.contacts] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3665 [com.google.android.gms.ui] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1917 [com.google.process.gapps] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1503 [com.google.android.as] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2223 [com.google.android.as.oss] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1405 [com.google.android.apps.wellbeing] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 897 [com.google.android.bluetooth] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1837 [android.process.media] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 939 [com.android.settings] **

Stats since: 10750336254ns
Total frames rendered: 8
Janky frames: 5 (62.50%)
Janky frames (legacy): 2 (25.00%)
50th percentile: 17ms
90th percentile: 97ms
95th percentile: 97ms
99th percentile: 97ms
Number Missed Vsync: 0
Number High input latency: 6
Number Slow UI thread: 2
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 3
Number Frame deadline missed: 5
Number Frame deadline missed (legacy): 2
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=4 17ms=2 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=1 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=1 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 15ms
90th gpu percentile: 19ms
95th gpu percentile: 19ms
99th gpu percentile: 19ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=2 12ms=0 13ms=1 14ms=0 15ms=2 16ms=1 17ms=1 18ms=0 19ms=1 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0

Pipeline=Skia (OpenGL)
Memory policy:
  Max surface area: 2592000
  Max resource usage: 124.42MB (x48)
  Background retention: 50% (altUiHidden = true)
  GPU Context timeout: 10
Contexts: 0 (stopped = 0)
No GrContext; however 1 remaining Vulkan refs
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2993 [com.android.providers.calendar] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3570 [com.google.android.settings.intelligence] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3723 [com.google.android.marvin.talkback] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1397 [com.google.android.inputmethod.latin] **

Stats since: 12765819839ns
Total frames rendered: 0
Janky frames: 0 (0.00%)
Janky frames (legacy): 0 (0.00%)
50th percentile: 4950ms
90th percentile: 4950ms
95th percentile: 4950ms
99th percentile: 4950ms
Number Missed Vsync: 0
Number High input latency: 0
Number Slow UI thread: 0
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 0
Number Frame deadline missed: 0
Number Frame deadline missed (legacy): 0
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 4950ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0

Pipeline=Skia (OpenGL)
Memory policy:
  Max surface area: 2592000
  Max resource usage: 124.42MB (x48)
  Background retention: 50% (altUiHidden = true)
  GPU Context timeout: 10
Contexts: 1 (stopped = 1)
No GrContext; however 1 remaining Vulkan refs
Profile data in ms:

	InputMethod/android.view.ViewRootImpl@5a0c333 (visibility=8)
Window: InputMethod
Stats since: 12769749630ns
Total frames rendered: 0
Janky frames: 0 (0.00%)
Janky frames (legacy): 0 (0.00%)
50th percentile: 4950ms
90th percentile: 4950ms
95th percentile: 4950ms
99th percentile: 4950ms
Number Missed Vsync: 0
Number High input latency: 0
Number Slow UI thread: 0
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 0
Number Frame deadline missed: 0
Number Frame deadline missed (legacy): 0
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 4950ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
---PROFILEDATA---


View hierarchy:

  InputMethod/android.view.ViewRootImpl@5a0c333
  23 views, 28.75 kB of render nodes


Total ViewRootImpl   : 1
Total attached Views : 23
Total RenderNode     : 28.75 kB (used) / 28.75 kB (capacity)


** Graphics info for pid 3686 [com.google.android.healthconnect.controller] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1138 [com.google.android.cellbroadcastreceiver] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3655 [com.android.traceur] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3653 [com.android.emergency] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1594 [com.android.printspooler] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1478 [com.google.android.providers.media.module] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1515 [com.google.android.googlequicksearchbox:interactor] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2647 [com.google.android.tts] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3483 [com.google.android.partnersetup] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3550 [com.google.android.rkpdapp] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3356 [com.google.android.gm] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3511 [com.google.android.projection.gearhead:shared] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3409 [com.google.android.packageinstaller] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3181 [com.android.chrome] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1591 [com.google.android.apps.youtube.music] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1647 [com.google.android.youtube] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3195 [com.google.android.configupdater] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 3066 [com.android.shell] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2998 [com.android.localtransport] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1939 [com.google.android.devicelockcontroller] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2052 [com.google.android.apps.wallpaper] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2912 [com.android.dynsystem:dynsystem] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2926 [com.android.managedprovisioning] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2226 [com.android.imsserviceentitlement] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2693 [com.google.android.dialer] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2884 [com.android.dynsystem] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2869 [com.android.camera2] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2636 [com.android.externalstorage] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2577 [com.google.android.onetimeinitializer] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 2439 [com.google.android.webview:webview_service] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 1551 [com.android.emulator.multidisplay] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 974 [com.google.android.ext.services] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 937 [com.android.phone] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 905 [com.android.se] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 847 [com.android.networkstack.process] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)


** Graphics info for pid 765 [com.android.systemui] **

Stats since: 10495054171ns
Total frames rendered: 182
Janky frames: 35 (19.23%)
Janky frames (legacy): 92 (50.55%)
50th percentile: 19ms
90th percentile: 73ms
95th percentile: 200ms
99th percentile: 500ms
Number Missed Vsync: 17
Number High input latency: 251
Number Slow UI thread: 25
Number Slow bitmap uploads: 1
Number Slow issue draw commands: 17
Number Frame deadline missed: 35
Number Frame deadline missed (legacy): 32
HISTOGRAM: 5ms=21 6ms=3 7ms=3 8ms=2 9ms=2 10ms=3 11ms=1 12ms=0 13ms=2 14ms=1 15ms=4 16ms=15 17ms=16 18ms=10 19ms=20 20ms=14 21ms=13 22ms=1 23ms=3 24ms=3 25ms=3 26ms=1 27ms=1 28ms=0 29ms=2 30ms=0 31ms=3 32ms=7 34ms=2 36ms=1 38ms=0 40ms=1 42ms=1 44ms=1 46ms=0 48ms=1 53ms=1 57ms=0 61ms=0 65ms=1 69ms=0 73ms=1 77ms=0 81ms=2 85ms=1 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=1 121ms=0 125ms=0 129ms=0 133ms=1 150ms=3 200ms=2 250ms=3 300ms=2 350ms=1 400ms=0 450ms=0 500ms=1 550ms=0 600ms=1 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 13ms
90th gpu percentile: 19ms
95th gpu percentile: 25ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=34 2ms=14 3ms=4 4ms=4 5ms=2 6ms=4 7ms=4 8ms=4 9ms=2 10ms=9 11ms=2 12ms=4 13ms=6 14ms=8 15ms=20 16ms=9 17ms=9 18ms=15 19ms=6 20ms=5 21ms=1 22ms=0 23ms=1 24ms=0 25ms=2 4950ms=7

Pipeline=Skia (OpenGL)
Memory policy:
  Max surface area: 2592000
  Max resource usage: 124.42MB (x48)
  Background retention: 50% (altUiHidden = true)
  IsSystemOrPersistent
  GPU Context timeout: 10
Contexts: 8 (stopped = 4)
CPU Caches:
  Glyph Cache: 18.10 KB (1 entry)
  Glyph Count: 11 
Total CPU memory usage:
  18538 bytes, 18.10 KB (0.00 bytes is purgeable)
GPU Caches:
  Other:
    Other: 512.00 bytes (1 entry)
    Buffer Object: 2.50 KB (4 entries)
    StencilAttachment: 74.00 KB (3 entries)
  Image:
    Texture: 24.05 KB (5 entries)
  Scratch:
    RenderTarget: 1.27 MB (14 entries)
    Texture: 7.64 MB (9 entries)
    Buffer Object: 142.00 KB (4 entries)
Total GPU memory usage:
  9587820 bytes, 9.14 MB (4.99 MB is purgeable)

Profile data in ms:

	ShellDropTarget/android.view.ViewRootImpl@462592e (visibility=4)
Window: ShellDropTarget
Stats since: 10503158129ns
Total frames rendered: 0
Janky frames: 0 (0.00%)
Janky frames (legacy): 0 (0.00%)
50th percentile: 4950ms
90th percentile: 4950ms
95th percentile: 4950ms
99th percentile: 4950ms
Number Missed Vsync: 0
Number High input latency: 0
Number Slow UI thread: 0
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 0
Number Frame deadline missed: 0
Number Frame deadline missed (legacy): 0
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 4950ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
---PROFILEDATA---


	ScreenDecorOverlay/android.view.ViewRootImpl@ca02ccf (visibility=0)
Window: ScreenDecorOverlay
Stats since: 10785842338ns
Total frames rendered: 61
Janky frames: 6 (9.84%)
Janky frames (legacy): 45 (73.77%)
50th percentile: 20ms
90th percentile: 32ms
95th percentile: 44ms
99th percentile: 150ms
Number Missed Vsync: 2
Number High input latency: 108
Number Slow UI thread: 5
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 3
Number Frame deadline missed: 6
Number Frame deadline missed (legacy): 6
HISTOGRAM: 5ms=4 6ms=0 7ms=0 8ms=1 9ms=0 10ms=1 11ms=0 12ms=0 13ms=0 14ms=0 15ms=4 16ms=2 17ms=3 18ms=3 19ms=8 20ms=10 21ms=9 22ms=0 23ms=2 24ms=2 25ms=1 26ms=0 27ms=0 28ms=0 29ms=2 30ms=0 31ms=1 32ms=2 34ms=1 36ms=1 38ms=0 40ms=0 42ms=0 44ms=1 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=1 121ms=0 125ms=0 129ms=0 133ms=1 150ms=1 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 15ms
90th gpu percentile: 19ms
95th gpu percentile: 20ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=14 2ms=3 3ms=0 4ms=0 5ms=1 6ms=0 7ms=1 8ms=0 9ms=1 10ms=3 11ms=0 12ms=0 13ms=2 14ms=2 15ms=7 16ms=2 17ms=5 18ms=8 19ms=6 20ms=3 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=3



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
1,194,10796423811,10846423809,0,10852716088,10852716379,10852716463,10925975796,10813090477,10852711671,16666666,10926825213,10927154046,10927517754,10929254463,10946660796,2500,205250,10946660796,10932441546,0,10929254463,
0,240,10863090475,10963090471,0,10975374713,10975375004,10975402004,10975458088,10979757137,10975345088,16666666,10975461004,10975610629,10975640713,10975768296,10980160504,1041,103000,10980160504,10976650963,0,10975768296,
0,310,10979757137,10979757137,0,10983313546,10983313713,10983338296,10993448338,11013090469,10983312088,16666666,10994304213,10999171629,10999233129,10999272379,11000381171,416292,112250,10999951879,11000381171,0,10999272379,
0,325,10996423803,10996423803,0,11000133379,11000133463,11000159338,11001174588,11029757135,11000132504,16666666,11001176129,11012734088,11012761171,11014549338,11016092046,782166,127417,11015292504,11016092046,0,11014549338,
0,333,11013090469,11013090469,0,11013808796,11013809171,11013842379,11013883879,11046423801,11013806838,16666666,11013885713,11016101713,11016140921,11021779546,11036262213,10014709,79625,11036262213,11032773671,0,11021779546,
0,348,11029757135,11029757135,0,11033690879,11033690963,11033720338,11033962921,11063090467,11033689504,16666666,11033965671,11034230796,11034236379,11035696671,11050254296,11677208,61333,11050254296,11047971546,0,11035696671,
0,356,11046423801,11046423801,0,11049377921,11049378004,11049413879,11049463629,11079757133,11049376588,16666666,11049465671,11049520588,11049524379,11049602879,11065949296,14460208,65417,11065949296,11064760879,0,11049602879,
0,364,11063090467,11063090467,0,11064894463,11064894546,11064917213,11064954088,11096423799,11064893296,16666666,11064955796,11065431671,11065438879,11065555588,11083333129,15748916,34750,11083333129,11081726379,0,11065555588,
0,372,11079757133,11079757133,0,11082268379,11082268463,11082397754,11082442213,11113090465,11082267254,16666666,11082444379,11082869588,11082874629,11082953671,11098161171,14798084,99958,11083336546,11098161171,0,11082953671,
0,380,11096423799,11096423799,0,11098964713,11098964796,11098991963,11099033129,11129757131,11098963379,16666666,11099035129,11099279379,11099294379,11099461879,11116680504,15276750,37292,11116680504,11115100463,0,11099461879,
0,388,11113090465,11113090465,0,11115293838,11115293921,11115322213,11115362754,11146423797,11115292588,16666666,11115364879,11116187879,11116194171,11116323171,11135501504,15197667,44416,11135501504,11131909213,0,11116323171,
0,396,11129757131,11129757131,0,11134700338,11134700421,11134763504,11134814921,11163090463,11134699088,16666666,11134816963,11134933254,11134939421,11135082171,11151032713,12813458,92333,11151032713,11148350213,0,11135082171,
0,404,11146423797,11146423797,0,11149424504,11149424588,11149448338,11149494838,11179757129,11149423463,16666666,11149497088,11149838463,11149847004,11149995004,11170861838,19797209,775416,11151036754,11170861838,0,11149995004,
0,412,11163090463,11163090463,0,11171372963,11171373046,11171398004,11171958213,11196423795,11171371754,16666666,11171961296,11174574463,11174587546,11174830379,11187094546,10001917,55042,11187094546,11185351254,0,11174830379,
0,420,11179757129,11179757129,0,11186153379,11186153463,11186180546,11186337671,11213090461,11186152004,16666666,11186339963,11186452588,11186464921,11186671963,11199933963,11284083,73708,11199933963,11198429754,0,11186671963,
0,428,11196423795,11196423795,0,11199161546,11199161629,11199191046,11199289213,11229757127,11199160129,16666666,11199291796,11199376129,11199382379,11199479213,11215016213,15054000,71917,11199937921,11215016213,0,11199479213,
0,436,11213090461,11213090461,0,11215160546,11215160588,11215393963,11215627796,11246423793,11215159421,16666666,11215630546,11215836671,11215839796,11215915671,11233308838,15497500,49583,11233308838,11231891421,0,11215915671,
0,444,11229757127,11229757127,0,11232101630,11232101713,11232127546,11232163421,11263090459,11232100505,16666666,11232165713,11232713630,11232720046,11232828296,11250944505,15931459,103625,11250944505,11249276963,0,11232828296,
0,452,11246423793,11246423793,0,11249520880,11249520963,11249575463,11249832713,11279757125,11249519338,16666666,11249836130,11250364463,11250382963,11250498088,11266694130,13963750,74084,11266694130,11264951713,0,11250498088,
0,460,11263090459,11263090459,0,11265679046,11265679088,11265698713,11265727796,11296423791,11265678005,16666666,11265729213,11265960838,11265964505,11266182671,11285320130,16602750,80833,11285320130,11283357046,0,11266182671,
0,468,11279757125,11279757125,0,11283638713,11283638796,11283671755,11283722046,11313090457,11283637505,16666666,11283724255,11284692713,11284701671,11284850671,11300238130,13246125,59167,11300238130,11298634921,0,11284850671,
0,476,11296423791,11296423791,0,11298888630,11298888713,11298917963,11298964630,11329757123,11298887463,16666666,11298966963,11299503963,11299513588,11299713838,11318520380,18172625,105625,11300242796,11318520380,0,11299713838,
0,512,11313090457,11313090457,0,11319845213,11319845338,11319868546,11336192421,11346423789,11319843546,16666666,11336225880,11336552713,11336588546,11337213796,11346815296,1167,39084,11346815296,11337697880,0,11337213796,
0,534,11329757123,11329757123,0,11338489588,11338489963,11338507671,11339269213,11379757121,11338488338,16666666,11339270713,11349003838,11349032421,11349153671,11350247380,1541,78000,11350247380,11349532755,0,11349153671,
0,556,11346423789,11346423789,0,11349173088,11349173130,11349213921,11349234255,11396423787,11349172255,16666666,11349236213,11349569463,11349612505,11349740880,11368713880,16376250,54625,11368713880,11366703671,0,11349740880,
0,571,11363090455,11363090455,0,11367000630,11367000713,11367038463,11367071338,11413090453,11366999921,16666666,11367074213,11368214755,11368245338,11368381005,11385504005,14046333,34209,11385504005,11382796380,0,11368381005,
0,579,11379757121,11379757121,0,11383773880,11383773963,11383821130,11383886880,11429757119,11383772463,16666666,11383892880,11384561171,11384568005,11384958671,11398359380,12812709,104083,11385511380,11398359380,0,11384958671,
0,594,11396423787,11396423787,0,11398630463,11398630588,11398720255,11398753671,11446423785,11398629380,16666666,11398755588,11399254380,11399282671,11399446963,11432902713,33125750,41625,11432540296,11432902713,0,11399446963,
0,609,11413090453,11429757119,0,11434402421,11434402713,11434473880,11434533838,11463090451,11434393213,16666666,11434537005,11436906838,11436918296,11437082630,11446672046,1042,112792,11446672046,11437574713,0,11437082630,
0,632,11446423785,11446423785,0,11446860921,11446861046,11446890005,11491191463,11479757117,11446859630,16666666,11491194380,11491639005,11491645713,11491859338,11492608546,1250,278375,11492592713,11492608546,0,11491859338,
0,647,11463090451,11479757117,0,11492746005,11492746171,11492778963,11492813213,11513090449,11492743130,16666666,11492814213,11493371713,11493375338,11493649963,11499918630,4436875,32500,11499918630,11498485838,0,11493649963,
0,655,11496423783,11496423783,0,11498648671,11498648713,11498673463,11498702588,11529757115,11498647671,16666666,11498704755,11499460505,11499466546,11499550171,11517751380,15666042,58500,11517751380,11515614963,0,11499550171,
0,663,11513090449,11513090449,0,11516749213,11516749296,11516821005,11516856963,11546423781,11516747838,16666666,11516858671,11517025838,11517031546,11517239755,11534614255,14230375,35541,11534614255,11532087421,0,11517239755,
0,671,11529757115,11529757115,0,11533630546,11533630630,11533655546,11533692046,11563090447,11533628963,16666666,11533709713,11533882755,11533894338,11534302463,11550599421,13958583,46833,11550599421,11548634046,0,11534302463,
0,679,11546423781,11546423781,0,11549674755,11549674796,11549711171,11549748546,11579757113,11549673421,16666666,11549750713,11549817380,11549833505,11550099255,11566682296,14598625,62208,11566682296,11565238088,0,11550099255,
0,687,11563090447,11563090447,0,11565463005,11565463088,11565509255,11565550880,11596423779,11565461671,16666666,11565553255,11566263463,11566270213,11566377005,11583829421,15195833,67250,11583829421,11581969546,0,11566377005,
0,709,11579757113,11579757113,0,11582977046,11582977130,11583005796,11583049171,11613090445,11582975671,16666666,11583051338,11583159338,11583164046,11583402796,11599614963,14398250,121166,11599614963,11598261630,0,11583402796,
0,717,11596423779,11596423779,0,11598463213,11598463296,11598523921,11598557255,11629757111,11598462088,16666666,11598559421,11599133796,11599148171,11599300838,11630643088,15393792,33792,11630643088,11615040671,0,11599300838,
0,739,11613090445,11613090445,0,11615343546,11615343630,11615363421,11616978880,11663090443,11615342713,16666666,11616980796,11632618463,11632703130,11633081005,11633953588,1584,263750,11633778713,11633953588,0,11633081005,
0,761,11629757111,11629757111,0,11632801255,11632801338,11632835463,11632865963,11679757109,11632800755,16666666,11632868088,11636757713,11636768421,11637271046,11656896338,10065125,100250,11656896338,11648334046,0,11637271046,
0,776,11646423777,11646423777,0,11652787838,11652787921,11652813213,11652845755,11696423775,11652787130,16666666,11652847630,11656280338,11656297630,11656447463,11675432713,16137667,65500,11675432713,11673070671,0,11656447463,
0,805,11663090443,11663090443,0,11673265046,11673265171,11673329380,11673365296,11713090441,11673263880,16666666,11673367505,11674781046,11674798130,11675007755,11684396046,6298750,74042,11684396046,11681773546,0,11675007755,
0,827,11679757109,11679757109,0,11683146630,11683146755,11683179838,11683208463,11729757107,11683145755,16666666,11683209838,11683388213,11683395296,11683568296,11698332505,13899584,409416,11684400088,11698332505,0,11683568296,
0,842,11696423775,11696423775,0,11698760546,11698760630,11698796255,11698833005,11746423773,11698759713,16666666,11698834963,11699445963,11699452755,11699549546,11715145255,14891208,58292,11700189546,11715145255,0,11699549546,
0,857,11713090441,11713090441,0,11715303546,11715303671,11715327963,11715374505,11763090439,11715302505,16666666,11715376380,11715818046,11715823796,11715900046,11733471921,15954042,53084,11733471921,11732151921,0,11715900046,
0,879,11729757107,11729757107,0,11732386588,11732386671,11732418963,11732464713,11779757105,11732385713,16666666,11732467421,11732838796,11732852963,11732954921,11751246046,15747209,108083,11751246046,11749259130,0,11732954921,
0,901,11746423773,11746423773,0,11749472838,11749472921,11749501338,11749540796,11796423771,11749471963,16666666,11749542880,11750575880,11750582921,11750768671,11765079671,13790291,84875,11751252421,11765079671,0,11750768671,
0,916,11763090439,11763090439,0,11766586255,11766586338,11766621588,11766658838,11813090437,11766585005,16666666,11766661005,11766900838,11766908005,11767258921,11782431671,14605625,120834,11767752255,11782431671,0,11767258921,
0,945,11779757105,11779757105,0,11788475588,11788475796,11788502796,11788603755,11829757103,11788473046,16666666,11788620505,11788735755,11788751171,11789709380,11802953171,9133584,108333,11802953171,11799538838,0,11789709380,
0,967,11796423771,11796423771,0,11801601755,11801601838,11801621796,11801652588,11846423769,11801600588,16666666,11801654421,11802111963,11802122005,11802428255,11821230171,12526833,79334,11821230171,11815519338,0,11802428255,
0,989,11813090437,11813090437,0,11815833255,11815833463,11815850921,11815879713,11863090435,11815832588,16666666,11815880421,11820402255,11820409880,11820892588,11846680463,10606083,50000,11846680463,11831872255,0,11820892588,
0,1011,11829757103,11846423769,0,11851116505,11851116588,11851143588,11851181380,11879757101,11851114921,16666666,11851183338,11854989546,11855026421,11855182963,11863425838,2000,83333,11863425838,11856452963,0,11855182963,
0,1048,11863090435,11863090435,0,11864184130,11864184505,11864209130,11865651171,11896423767,11864181838,16666666,11865682130,11868302130,11868863463,11870554380,11871572713,395750,137333,11871161713,11871572713,0,11870554380,
0,1070,11879757101,11879757101,0,11880572171,11880572296,11880589463,11880662130,11913090433,11880570880,16666666,11880666213,11882056671,11882077046,11882415088,11896662546,429667,67000,11896662546,11883382130,0,11882415088,
0,1092,11896423767,11896423767,0,11898191588,11898191921,11898212880,11898253963,11929757099,11898190255,16666666,11898255880,11898426380,11898444213,11898569171,11913462005,1333,68125,11913462005,11899276838,0,11898569171,
0,1114,11913090433,11913090433,0,11913572130,11913572255,11913606130,11913653880,11946423765,11913570838,16666666,11913656171,11917968213,11917976588,11918275588,11919571047,2000,733333,11919542422,11919571047,0,11918275588,
0,1150,11929757099,11929757099,0,11930236088,11930236130,11930260547,11930305255,11963090431,11930235047,16666666,11930307005,11932091255,11932100755,11932578463,11946637505,1583,66250,11946637505,11933744630,0,11932578463,
0,1172,11946423765,11946423765,0,11947736005,11947736047,11947782213,11947829297,11979757097,11947734838,16666666,11947831713,11948247130,11948275297,11948581505,11963482630,2625,74125,11963482630,11950000422,0,11948581505,
0,1195,11963090431,11963090431,0,11963858213,11963858338,11963884213,11963917713,11996423763,11963857005,16666666,11963919505,11965768630,11965778213,11966075422,11980203880,2833,95500,11980203880,11966917922,0,11966075422,
0,1277,12113090425,12113090425,0,12113954380,12113954797,12113954963,12115954213,12129757091,12113949922,16666666,12115972630,12116148797,12116157547,12117361922,12118385755,2375,433291,12118357963,12118385755,0,12117361922,
0,4693,15829756943,15829756943,0,15830556215,15830556507,15830556632,15917785798,15846423609,15830553923,16666666,15917868132,15918501132,15918542798,15951597965,15963612340,1334,89708,15963612340,15952568965,0,15951597965,
---PROFILEDATA---


	ScreenDecorOverlayBottom/android.view.ViewRootImpl@4f4565c (visibility=0)
Window: ScreenDecorOverlayBottom
Stats since: 10793243796ns
Total frames rendered: 58
Janky frames: 6 (10.34%)
Janky frames (legacy): 13 (22.41%)
50th percentile: 17ms
90th percentile: 32ms
95th percentile: 40ms
99th percentile: 150ms
Number Missed Vsync: 1
Number High input latency: 83
Number Slow UI thread: 3
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 5
Number Frame deadline missed: 6
Number Frame deadline missed (legacy): 5
HISTOGRAM: 5ms=12 6ms=3 7ms=1 8ms=1 9ms=0 10ms=0 11ms=1 12ms=0 13ms=2 14ms=1 15ms=0 16ms=2 17ms=8 18ms=4 19ms=8 20ms=3 21ms=0 22ms=1 23ms=1 24ms=1 25ms=1 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=1 32ms=3 34ms=1 36ms=0 38ms=0 40ms=1 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=1 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=1 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 13ms
90th gpu percentile: 18ms
95th gpu percentile: 25ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=14 2ms=6 3ms=2 4ms=0 5ms=0 6ms=1 7ms=1 8ms=0 9ms=1 10ms=1 11ms=0 12ms=1 13ms=3 14ms=3 15ms=12 16ms=3 17ms=3 18ms=2 19ms=0 20ms=0 21ms=1 22ms=0 23ms=1 24ms=0 25ms=1 4950ms=2



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
1,194,10796423811,10846423809,0,10852716088,10852716379,10852716463,10941799879,10813090477,10852711671,16666666,10941828338,10947143046,10947189004,10947237838,10978183213,1584,78083,10978183213,10964462546,0,10947237838,
0,240,10863090475,10963090471,0,10975374713,10975375004,10975402004,10975777213,10879757141,10975345088,16666666,10975779588,10976767421,10976779171,10977702004,0,1916,64208,0,10978261213,0,10977702004,
0,310,10979757137,10979757137,0,10983313546,10983313713,10983338296,10991302671,10996423803,10983312088,16666666,10991323171,10991473588,10991494088,10991584129,11012216171,468875,62625,11012216171,10992812129,0,10991584129,
0,325,10996423803,10996423803,0,11000133379,11000133463,11000159338,11000207754,11029757135,11000132504,16666666,11000211171,11000424296,11000438963,11010650046,11012676004,439417,226541,11012221254,11012676004,0,11010650046,
0,333,11013090469,11013090469,0,11013808796,11013809171,11013842379,11016137629,11046423801,11013806838,16666666,11016138838,11032891838,11032905463,11033033629,11034117296,1542,565375,11034099879,11034117296,0,11033033629,
0,348,11029757135,11029757135,0,11033690879,11033690963,11033720338,11034829588,11063090467,11033689504,16666666,11034831213,11048399254,11048408754,11048540046,11063233796,1500,92208,11063233796,11049328713,0,11048540046,
0,356,11046423801,11046423801,0,11049377921,11049378004,11049413879,11050304796,11096423799,11049376588,16666666,11050305754,11064831879,11064840129,11064950796,11080070879,1584,82416,11080070879,11065366879,0,11064950796,
0,364,11063090467,11063090467,0,11064894463,11064894546,11064917213,11065607088,11113090465,11064893296,16666666,11065608129,11081804004,11081812921,11081994171,11082819629,1125,219584,11082788796,11082819629,0,11081994171,
0,372,11079757133,11079757133,0,11082268379,11082268463,11082397754,11083357713,11129757131,11082267254,16666666,11083358504,11098244546,11098326338,11098453004,11099231796,1208,51209,11099200963,11099231796,0,11098453004,
0,380,11096423799,11096423799,0,11098964713,11098964796,11098991963,11099335004,11146423797,11098963379,16666666,11099335588,11115190463,11115209004,11115511963,11130161421,1958,98917,11130161421,11115996504,0,11115511963,
0,388,11113090465,11113090465,0,11115293838,11115293921,11115322213,11116231963,11163090463,11115292588,16666666,11116232921,11132213838,11132222421,11132352046,11146694921,1584,89500,11146694921,11132776921,0,11132352046,
0,396,11129757131,11129757131,0,11134700338,11134700421,11134763504,11135143254,11179757129,11134699088,16666666,11135144171,11148497796,11148506671,11148810421,11149676463,1250,305500,11149604963,11149676463,0,11148810421,
0,404,11146423797,11146423797,0,11149424504,11149424588,11149448338,11150399421,11196423795,11149423463,16666666,11150400379,11171062379,11171070754,11171494504,11180099838,959,64750,11180099838,11172221713,0,11171494504,
0,412,11163090463,11163090463,0,11171372963,11171373046,11171398004,11175437463,11213090461,11171371754,16666666,11175439671,11185419421,11185445421,11185635754,11196717254,1250,94250,11196717254,11186084254,0,11185635754,
0,420,11179757129,11179757129,0,11186153379,11186153463,11186180546,11187164129,11229757127,11186152004,16666666,11187165879,11198530338,11198537921,11198747671,11199330421,1292,267209,11199314004,11199330421,0,11198747671,
0,428,11196423795,11196423795,0,11199161546,11199161629,11199191046,11199926088,11246423793,11199160129,16666666,11199926963,11215080380,11215087130,11215319421,11215792338,875,82125,11215777463,11215792338,0,11215319421,
0,436,11213090461,11213090461,0,11215160546,11215160588,11215393963,11215953463,11263090459,11215159421,16666666,11215954338,11231965546,11231980921,11232177296,11247726005,1333,57125,11247726005,11232634838,0,11232177296,
0,444,11229757127,11229757127,0,11232101630,11232101713,11232127546,11233377421,11279757125,11232100505,16666666,11233378630,11249423838,11249448380,11249688421,11263466505,2500,92666,11263466505,11250279755,0,11249688421,
0,452,11246423793,11246423793,0,11249520880,11249520963,11249575463,11250454713,11296423791,11249519338,16666666,11250456713,11265026838,11265036421,11265225213,11265891838,1125,217875,11265795296,11265891838,0,11265225213,
0,460,11263090459,11263090459,0,11265679046,11265679088,11265698713,11266544130,11313090457,11265678005,16666666,11266544921,11283482755,11283518296,11283772963,11296671671,2041,105208,11296671671,11284304380,0,11283772963,
0,468,11279757125,11279757125,0,11283638713,11283638796,11283671755,11285074296,11329757123,11283637505,16666666,11285075505,11298749213,11298769130,11298911213,11313332963,1250,62542,11313332963,11299410838,0,11298911213,
0,476,11296423791,11296423791,0,11298888630,11298888713,11298917963,11300293630,11346423789,11298887463,16666666,11300296505,11318587421,11318596671,11318805046,11319501046,1209,257834,11319485296,11319501046,0,11318805046,
0,512,11313090457,11313090457,0,11319845213,11319845338,11319868546,11326538463,11363090455,11319843546,16666666,11326580880,11334101255,11334265088,11334870421,11340794338,1500,86083,11340794338,11335428963,0,11334870421,
0,534,11329757123,11329757123,0,11338489588,11338489963,11338507671,11338546421,11379757121,11338488338,16666666,11338549380,11339236588,11339286921,11340190421,11365146463,8100667,119250,11365146463,11348925546,0,11340190421,
0,556,11346423789,11346423789,0,11349173088,11349173130,11349213921,11349609880,11396423787,11349172255,16666666,11349610796,11366874963,11367354296,11367485046,11380897880,1292,71125,11380897880,11367983713,0,11367485046,
0,571,11363090455,11363090455,0,11367000630,11367000713,11367038463,11368241171,11413090453,11366999921,16666666,11368242296,11382968088,11382980588,11383221463,11384450671,209458,689250,11384196130,11384450671,0,11383221463,
0,579,11379757121,11379757121,0,11383773880,11383773963,11383821130,11384897213,11429757119,11383772463,16666666,11384898755,11398486671,11398507921,11398720588,11415564880,2250,79708,11415564880,11399119505,0,11398720588,
0,594,11396423787,11396423787,0,11398630463,11398630588,11398720255,11399367588,11446423785,11398629380,16666666,11399368213,11433959171,11433982088,11434402046,11436803130,2083,514500,11436750046,11436803130,0,11434402046,
0,609,11413090453,11429757119,0,11434402421,11434402713,11434473880,11437430421,11429757119,11434393213,16666666,11437432838,11437630755,11437637713,11437713213,0,52683958,72792,0,11490779005,0,11437713213,
0,632,11446423785,11446423785,0,11446860921,11446861046,11446890005,11446982380,11463090451,11446859630,16666666,11446986171,11490824505,11490849838,11491041171,11491500046,1000,95417,11491479421,11491500046,0,11491041171,
0,647,11463090451,11479757117,0,11492746005,11492746171,11492778963,11493595546,11513090449,11492743130,16666666,11493596255,11498598796,11498610380,11498764380,11499358380,1250,168125,11499340630,11499358380,0,11498764380,
0,655,11496423783,11496423783,0,11498648671,11498648713,11498673463,11499521463,11529757115,11498647671,16666666,11499522630,11515785713,11515795421,11516233463,11530273046,1375,238916,11530273046,11516955755,0,11516233463,
0,663,11513090449,11513090449,0,11516749213,11516749296,11516821005,11517776963,11563090447,11516747838,16666666,11517777713,11532275130,11532285130,11532929796,11546802671,792,78250,11546802671,11533504505,0,11532929796,
0,671,11529757115,11529757115,0,11533630546,11533630630,11533655546,11534663213,11579757113,11533628963,16666666,11534675880,11548722296,11548735963,11549094463,11563434880,1166,70500,11563434880,11549621921,0,11549094463,
0,679,11546423781,11546423781,0,11549674755,11549674796,11549711171,11549897380,11596423779,11549673421,16666666,11549898921,11565362463,11565380380,11565590588,11580373713,1000,71875,11580373713,11566061796,0,11565590588,
0,687,11563090447,11563090447,0,11565463005,11565463088,11565509255,11566415130,11613090445,11565461671,16666666,11566417005,11582196713,11582207171,11582449796,11596600963,1083,209500,11596600963,11583089005,0,11582449796,
0,709,11579757113,11579757113,0,11582977046,11582977130,11583005796,11583863296,11629757111,11582975671,16666666,11583864546,11598398713,11598409046,11598529963,11613528213,1166,91417,11613528213,11599087296,0,11598529963,
0,717,11596423779,11596423779,0,11598463213,11598463296,11598523921,11599180588,11646423777,11598462088,16666666,11599181213,11615170380,11615204171,11615391505,11616913755,708,36250,11616913755,11616310838,0,11615391505,
0,739,11613090445,11613090445,0,11615343546,11615343630,11615363421,11615394005,11663090443,11615342713,16666666,11615394838,11616323546,11616327171,11616521546,11646861463,15550041,80333,11646861463,11632496213,0,11616521546,
0,761,11629757111,11629757111,0,11632801255,11632801338,11632835463,11637048671,11679757109,11632800755,16666666,11637049171,11652744213,11652752338,11652908505,11670643005,1042,56791,11670643005,11653422630,0,11652908505,
0,776,11646423777,11646423777,0,11652787838,11652787921,11652813213,11656391255,11696423775,11652787130,16666666,11656393921,11673185255,11673204505,11673392630,11674673546,667,132833,11674654880,11674673546,0,11673392630,
0,805,11663090443,11663090443,0,11673265046,11673265171,11673329380,11674846255,11713090441,11673263880,16666666,11674847463,11681858171,11681866630,11682015255,11683336255,2291,88875,11683313630,11683336255,0,11682015255,
0,827,11679757109,11679757109,0,11683146630,11683146755,11683179838,11684257421,11729757107,11683145755,16666666,11684259046,11698456838,11698467880,11698695713,11699399088,1584,112334,11699379713,11699399088,0,11698695713,
0,842,11696423775,11696423775,0,11698760546,11698760630,11698796255,11699483130,11746423773,11698759713,16666666,11699484005,11715226088,11715244088,11715391963,11715781005,833,57000,11715761796,11715781005,0,11715391963,
0,857,11713090441,11713090441,0,11715303546,11715303671,11715327963,11715847713,11763090439,11715302505,16666666,11715848630,11732232255,11732268421,11732403255,11747576671,1000,66292,11747576671,11732760046,0,11732403255,
0,879,11729757107,11729757107,0,11732386588,11732386671,11732418963,11732948630,11779757105,11732385713,16666666,11732950296,11749380505,11749401546,11749769046,11750491671,1417,363292,11750475588,11750491671,0,11749769046,
0,901,11746423773,11746423773,0,11749472838,11749472921,11749501338,11751122546,11796423771,11749471963,16666666,11751123963,11765254171,11765267380,11765624880,11766768255,1542,562542,11766741671,11766768255,0,11765624880,
0,916,11763090439,11763090439,0,11766586255,11766586338,11766621588,11767717421,11813090437,11766585005,16666666,11767718630,11782542505,11782552963,11782831338,11785124130,2833,1561167,11784997463,11785124130,0,11782831338,
0,945,11779757105,11779757105,0,11788475588,11788475796,11788502796,11799761505,11829757103,11788473046,16666666,11799778421,11800223546,11800239213,11800888588,11813776713,1750,73709,11813776713,11801524755,0,11800888588,
0,967,11796423771,11796423771,0,11801601755,11801601838,11801621796,11802424046,11846423769,11801600588,16666666,11802424963,11815660005,11815673213,11815888588,11830012880,875,47583,11830012880,11816296296,0,11815888588,
0,989,11813090437,11813090437,0,11815833255,11815833463,11815850921,11820515005,11863090435,11815832588,16666666,11820515880,11851069296,11851186921,11851321755,11857756713,1250,72375,11857756713,11851772463,0,11851321755,
0,1011,11829757103,11846423769,0,11851116505,11851116588,11851143588,11855022505,11879757101,11851114921,16666666,11855023963,11857292796,11857395213,11857497296,11872377838,7693500,43250,11872377838,11865526838,0,11857497296,
0,1048,11863090435,11863090435,0,11864184130,11864184505,11864209130,11868428671,11896423767,11864181838,16666666,11868470255,11871643005,11871680671,11871895505,11884228005,9537458,74292,11884228005,11881961421,0,11871895505,
0,1070,11879757101,11879757101,0,11880572171,11880572296,11880589463,11882093713,11913090433,11880570880,16666666,11882095255,11883455421,11883487921,11883670213,11899931588,14099208,41458,11899931588,11898359838,0,11883670213,
0,1092,11896423767,11896423767,0,11898191588,11898191921,11898212880,11898496880,11929757099,11898190255,16666666,11898498713,11899388546,11899397630,11899535463,11921693630,17874542,66250,11921693630,11917836797,0,11899535463,
0,1114,11913090433,11913090433,0,11913572130,11913572255,11913606130,11919124797,11946423765,11913570838,16666666,11919125922,11920992172,11920998880,11921199547,11935348505,10134167,80375,11935348505,11931873130,0,11921199547,
0,1150,11929757099,11929757099,0,11930236088,11930236130,11930260547,11932517630,11963090431,11930235047,16666666,11932519422,11933893672,11933900422,11934281047,11950704963,12621458,61291,11950704963,11948182797,0,11934281047,
0,1172,11946423765,11946423765,0,11947736005,11947736047,11947782213,11948310380,11979757097,11947734838,16666666,11948311005,11950134547,11950159005,11950309213,11967625547,14912125,76167,11967625547,11965651547,0,11950309213,
0,1195,11963090431,11963090431,0,11963858213,11963858338,11963884213,11965971255,11996423763,11963857005,16666666,11965973630,11967000672,11967008255,11967127755,11982017172,14343875,112667,11967630047,11982017172,0,11967127755,
0,4693,15829756943,15829756943,0,15830556215,15830556507,15830556632,15896406423,15846423609,15830553923,16666666,15896455090,15896597382,15896619548,15903657048,15913466590,2250,115417,15913466590,15904810840,0,15903657048,
---PROFILEDATA---


	NavigationBar0/android.view.ViewRootImpl@580fd65 (visibility=0)
Window: NavigationBar0
Stats since: 11284314463ns
Total frames rendered: 5
Janky frames: 5 (100.00%)
Janky frames (legacy): 5 (100.00%)
50th percentile: 300ms
90th percentile: 600ms
95th percentile: 600ms
99th percentile: 600ms
Number Missed Vsync: 5
Number High input latency: 0
Number Slow UI thread: 4
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 4
Number Frame deadline missed: 5
Number Frame deadline missed (legacy): 5
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=1 250ms=1 300ms=2 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=1 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 16ms
90th gpu percentile: 20ms
95th gpu percentile: 20ms
99th gpu percentile: 20ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=1 8ms=0 9ms=0 10ms=0 11ms=1 12ms=0 13ms=0 14ms=0 15ms=0 16ms=1 17ms=1 18ms=0 19ms=0 20ms=1 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
1,498,11313090457,11563090447,0,11573715671,11573715796,11574255255,11636849338,11329757123,11573538005,16666666,11636995463,11648523005,11648574588,11651623213,11670645796,1333,137666,11670645796,11652645546,0,11651623213,
0,702,11579757113,11913090433,0,11914397713,11914397880,11917359130,11917854088,11696423775,11914253005,16666666,11917894713,11919675630,11919700380,11919979422,11930019672,1667,110417,11930019672,11920640297,0,11919979422,
0,1136,11929757099,12163090423,0,12179393963,12179394297,12179987088,12180709672,11963090431,12179283880,16666666,12180803797,12180927130,12180946172,12181296505,12196616463,2291,96417,12196616463,12181975505,0,12181296505,
0,4670,15796423611,16396423587,0,16409634840,16409635215,16409635340,16422504424,15813090277,16408444715,16666666,16422539049,16422932090,16422980215,16423400715,16441034674,3250,16015042,16430033465,16441034674,0,16423400715,
0,5328,16429756919,16596423579,0,16602347257,16602347590,16602381674,16629644257,16463090251,16601990007,16666666,16629722299,16629779424,16629808340,16630606757,16646696299,1750,73792,16646696299,16631255799,0,16630606757,
---PROFILEDATA---


	EdgeBackGestureHandler0/android.view.ViewRootImpl@63eda3a (visibility=8)
Window: EdgeBackGestureHandler0
Stats since: 11325716921ns
Total frames rendered: 0
Janky frames: 0 (0.00%)
Janky frames (legacy): 0 (0.00%)
50th percentile: 4950ms
90th percentile: 4950ms
95th percentile: 4950ms
99th percentile: 4950ms
Number Missed Vsync: 0
Number High input latency: 0
Number Slow UI thread: 0
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 0
Number Frame deadline missed: 0
Number Frame deadline missed (legacy): 0
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 4950ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
---PROFILEDATA---


	NotificationShade/android.view.ViewRootImpl@21cc6eb (visibility=4)
Window: NotificationShade
Stats since: 11382834463ns
Total frames rendered: 0
Janky frames: 0 (0.00%)
Janky frames (legacy): 0 (0.00%)
50th percentile: 4950ms
90th percentile: 4950ms
95th percentile: 4950ms
99th percentile: 4950ms
Number Missed Vsync: 0
Number High input latency: 0
Number Slow UI thread: 0
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 0
Number Frame deadline missed: 0
Number Frame deadline missed (legacy): 0
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 4950ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
---PROFILEDATA---


	StatusBar/android.view.ViewRootImpl@f9e7c48 (visibility=0)
Window: StatusBar
Stats since: 11399137588ns
Total frames rendered: 52
Janky frames: 18 (34.62%)
Janky frames (legacy): 29 (55.77%)
50th percentile: 19ms
90th percentile: 150ms
95th percentile: 250ms
99th percentile: 500ms
Number Missed Vsync: 9
Number High input latency: 60
Number Slow UI thread: 13
Number Slow bitmap uploads: 1
Number Slow issue draw commands: 5
Number Frame deadline missed: 18
Number Frame deadline missed (legacy): 16
HISTOGRAM: 5ms=1 6ms=0 7ms=1 8ms=0 9ms=1 10ms=2 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=11 17ms=5 18ms=3 19ms=4 20ms=1 21ms=4 22ms=0 23ms=0 24ms=0 25ms=1 26ms=1 27ms=1 28ms=0 29ms=0 30ms=0 31ms=1 32ms=2 34ms=0 36ms=0 38ms=0 40ms=0 42ms=1 44ms=0 46ms=0 48ms=1 53ms=1 57ms=0 61ms=0 65ms=1 69ms=0 73ms=1 77ms=0 81ms=1 85ms=1 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=1 200ms=1 250ms=2 300ms=0 350ms=1 400ms=0 450ms=0 500ms=1 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 10ms
90th gpu percentile: 18ms
95th gpu percentile: 25ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=6 2ms=5 3ms=2 4ms=4 5ms=1 6ms=3 7ms=1 8ms=4 9ms=0 10ms=5 11ms=1 12ms=3 13ms=1 14ms=3 15ms=1 16ms=3 17ms=0 18ms=5 19ms=0 20ms=1 21ms=0 22ms=0 23ms=0 24ms=0 25ms=1 4950ms=2



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
1,498,11313090457,11563090447,0,11573715671,11573715796,11574255255,11820154546,11329757123,11573538005,16666666,11820472463,11831972213,11831993796,11849730421,11863431046,1833,74500,11863431046,11850868671,0,11849730421,
0,702,11579757113,11913090433,0,11914397713,11914397880,11917359130,11967097797,11896423767,11914253005,16666666,11967862213,11982142130,11982178755,11982679630,11985589255,1791,605375,11985542130,11985589255,0,11982679630,
0,1136,11929757099,12163090423,0,12179393963,12179394297,12179987088,12210110922,12013090429,12179283880,16666666,12210285713,12210426797,12210461172,12211299047,12212716713,2000,425791,12212693005,12212716713,0,12211299047,
0,1306,12179757089,12429757079,0,12442297630,12442298130,12442416463,12445910047,12229757087,12441413838,16666666,12445958672,12451265672,12451515047,12451886213,12463308297,2083,102833,12463308297,12452962172,0,12451886213,
0,1400,12563090407,12729757067,0,12737973214,12737973630,12738285255,12742606297,12579757073,12737834589,16666666,12742638547,12742702880,12742731839,12743012089,12746913214,1459,70708,12746913214,12743853797,0,12743012089,
0,1437,12763090399,12829757063,0,12832397255,12832397464,12832469214,12838205630,12779757065,12832392797,16666666,12838233714,12838462339,12838497547,12841771589,12847680255,2667,5034917,12846836464,12847680255,0,12841771589,
0,1512,12846423729,12846423729,0,12847125089,12847125255,12847158130,12852974839,12879757061,12847123589,16666666,12853061589,12853102547,12853134214,12853903380,12863318047,1542,57708,12863318047,12855284630,0,12853903380,
0,1534,12863090395,12863090395,0,12865081964,12865082255,12865121422,12866819672,12896423727,12865079714,16666666,12866825922,12866918380,12866937505,12867713005,12879943422,1333,59541,12879943422,12868452380,0,12867713005,
0,1556,12879757061,12879757061,0,12880319005,12880319422,12880366505,12882897130,12913090393,12880316005,16666666,12882904630,12883042505,12883059839,12883334547,12896800089,510833,280833,12896800089,12884717755,0,12883334547,
0,1571,12896423727,12896423727,0,12898663505,12898663922,12898754630,12903212464,12929757059,12898660589,16666666,12903224297,12903346964,12903367339,12903742047,12913518089,1583,103209,12913518089,12904534172,0,12903742047,
0,1593,12913090393,12913090393,0,12916648630,12916648880,12916687672,12919480464,12946423725,12916646130,16666666,12919512880,12919529255,12919556297,12919832422,12929917880,1916,120000,12929917880,12920925089,0,12919832422,
0,1615,12929757059,12929757059,0,12933283672,12933283922,12933332047,12935520339,12963090391,12933281255,16666666,12935528089,12935553255,12935573630,12936226880,12936811047,1334,134000,12936790464,12936811047,0,12936226880,
0,1637,12946423725,12946423725,0,12954390547,12954391005,12954471755,12959397839,12979757057,12954387714,16666666,12959522255,12959533214,12959554130,12959950714,12963226339,1834,169333,12963226339,12960907089,0,12959950714,
0,1659,12963090391,12963090391,0,12967946505,12967946964,12968167880,12969992755,12996423723,12967943380,16666666,12969998297,12970058130,12970077089,12970424755,12980150547,2000,94625,12980150547,12971131380,0,12970424755,
0,1681,12979757057,12979757057,0,12981722339,12981722505,12981863630,12986570547,13013090389,12981719880,16666666,12986578297,12986660547,12986680464,12987258089,12996633130,2500,481000,12996633130,12988355672,0,12987258089,
0,1703,12996423723,12996423723,0,12997274505,12997274547,12997341297,12999647047,13029757055,12997272547,16666666,12999666589,12999727380,12999765339,13000158797,13013326380,1750,230375,13013326380,13001051672,0,13000158797,
0,1858,13146423717,13146423717,0,13160132547,13160132880,13162358922,13172550464,13163090383,13160130130,16666666,13172576672,13176413797,13176471172,13176746005,13181272797,2459,2608291,13179996089,13181272797,0,13176746005,
0,1981,13246423713,13246423713,0,13260676672,13260676797,13260741839,13262395922,13263090379,13260674755,16666666,13262424380,13262686547,13262892172,13273280797,13274532630,2417,223959,13274488630,13274532630,0,13273280797,
0,2024,13263090379,13263090379,0,13266470005,13266470172,13266511380,13310422047,13296423711,13266468630,16666666,13310456297,13310468255,13310719464,13311791714,13312492589,1375,169958,13312474172,13312492589,0,13311791714,
0,2067,13279757045,13296423711,0,13312845339,13312845464,13313419214,13315719089,13329757043,13312842881,16666666,13315753631,13315763381,13316376797,13316867256,13323591339,1500,110625,13323591339,13317270506,0,13316867256,
0,2125,13313090377,13313090377,0,13317753339,13317753422,13317777881,13320183339,13346423709,13317751714,16666666,13320188839,13320200339,13322426339,13322999464,13332185381,8553500,139625,13323596839,13332185381,0,13322999464,
0,2154,13329757043,13329757043,0,13330633506,13330633756,13330666839,13332684839,13363090375,13330630964,16666666,13332691089,13332797506,13332961797,13333258381,13351138881,16289417,119417,13351138881,13350220089,0,13333258381,
0,2204,13346423709,13346423709,0,13346900006,13346900506,13346936547,13349460756,13379757041,13346897172,16666666,13349466547,13350232881,13350264589,13350523964,13368377297,15930125,56667,13368377297,13367120131,0,13350523964,
0,2233,13363090375,13363090375,0,13364128047,13364128131,13364223547,13364232214,13379757041,13364126631,16666666,13364328964,13367132339,13367165672,13367644089,0,37913459,78166,0,13406337256,0,13367644089,
0,2269,13379757041,13379757041,0,13380688839,13380688922,13380849922,13383414172,13396423707,13380686922,16666666,13383536756,13406352672,13406383672,13407838839,13413281631,2041,53625,13413281631,13408457422,0,13407838839,
0,2305,13396423707,13396423707,0,13410122964,13410123172,13410262297,13410281047,13446423705,13410120547,16666666,13410427839,13410485256,13410504089,13461144089,13462314464,2208,336292,13462288381,13462314464,0,13461144089,
0,2341,13413090373,13446423705,0,13457595964,13457596131,13457724006,13457734922,13479757037,13457593464,16666666,13457856006,13462339214,13462390047,13464833714,13472184422,1334,53209,13472184422,13465572172,0,13464833714,
0,2414,13463090371,13463090371,0,13463823172,13463823256,13464368339,13467009631,13496423703,13463822256,16666666,13467124797,13467366131,13467389339,13471036964,13482250256,9995625,430459,13472190756,13482250256,0,13471036964,
0,2443,13479757037,13479757037,0,13480586089,13480586172,13480730756,13480740672,13513090369,13480585006,16666666,13480849881,13482268922,13482297714,13485064214,13498649881,12863666,115584,13485753797,13498649881,0,13485064214,
0,2472,13496423703,13496423703,0,13497136131,13497136714,13497305881,13497321464,13529757035,13497132589,16666666,13497476006,13498664464,13498686797,13499111089,13517087589,13541875,119625,13503520297,13517087589,0,13499111089,
0,2501,13513090369,13513090369,0,13520732256,13520732589,13520732672,13520751797,13546423701,13520729714,16666666,13520807047,13521145131,13521168589,13521764256,13547111256,12754875,78166,13547111256,13535337714,0,13521764256,
0,2817,13763090359,13763090359,0,13767751089,13767751339,13767919214,13767936839,13779757025,13767748339,16666666,13768135131,13768146422,13768168881,13768557256,13780149714,1458,69375,13780149714,13769166714,0,13768557256,
0,2832,13779757025,13779757025,0,13780860672,13780860839,13781502089,13784706547,13813090357,13780858422,16666666,13784812422,13784822631,13784870464,13785168172,13796645714,1417,119750,13796645714,13785964006,0,13785168172,
0,2854,13796423691,13796423691,0,13796842714,13796842839,13797009756,13797018422,13829757023,13796840422,16666666,13797145922,13797155297,13797184589,13797567672,13813302006,709,62875,13813302006,13801118297,0,13797567672,
0,2883,13813090357,13813090357,0,13813447339,13813447797,13813625214,13813638047,13846423689,13813444214,16666666,13813760506,13813773922,13813792714,13814180381,13830113464,1916,132958,13830113464,13816980672,0,13814180381,
0,2905,13829757023,13829757023,0,13830314797,13830315297,13830470631,13830479214,13863090355,13830311672,16666666,13830603589,13830619089,13830636589,13831176214,13833980214,1750,93792,13833954881,13833980214,0,13831176214,
0,2927,13846423689,13846423689,0,13848644547,13848644672,13848835464,13848855256,13879757021,13848642464,16666666,13848988256,13849191714,13849207214,13849678006,13856714089,1834,779750,13856684089,13856714089,0,13849678006,
0,2949,13863090355,13863090355,0,13863867172,13863867506,13864065589,13864088381,13896423687,13863864422,16666666,13864239464,13864269381,13864289506,13864676464,13880138964,1792,85833,13880138964,13867216089,0,13864676464,
0,2971,13879757021,13879757021,0,13880770589,13880770756,13881040506,13881062714,13913090353,13880768256,16666666,13881231089,13881354714,13881378047,13882581422,13896789672,1416,64083,13896789672,13883175131,0,13882581422,
0,2993,13896423687,13896423687,0,13897049214,13897049297,13897545214,13897562756,13929757019,13897047506,16666666,13897666381,13898186797,13898209756,13898597922,13906257381,133750,6943333,13906082672,13906257381,0,13898597922,
0,3106,13996423683,13996423683,0,13998650131,13998650339,13998650422,14000929006,14013090349,13998648339,16666666,14000989881,14001000256,14001019422,14005842547,14021655631,3083,15010501,14013243173,14021655631,0,14005842547,
0,5328,16429756919,16596423579,0,16602347257,16602347590,16602381674,16633776382,16446423585,16601990007,16666666,16634064215,16634184590,16638561049,16641472049,16650991507,2459,84125,16650528882,16650991507,0,16641472049,
0,5435,16613090245,16679756909,0,16691472340,16691472549,16691521882,16691823215,16679756909,16691469215,16666666,16691895424,16691934424,16691973090,16692767090,16696587299,1834,74084,16696587299,16693224715,0,16692767090,
0,5604,16746423573,16796423571,0,16808858299,16808858799,16809170091,16811679424,16763090239,16808854591,16666666,16811746966,16811805091,16811841966,16816152716,16821235132,1291,65250,16821235132,16816499341,0,16816152716,
0,5699,16813090237,16813090237,0,16818965924,16818966341,16819012257,16819969841,16846423569,16818963674,16666666,16819986591,16819996674,16820220299,16820466216,16833212716,11803459,59042,16821383216,16833212716,0,16820466216,
0,5714,16829756903,16829756903,0,16829982216,16829982674,16830345757,16832656382,16863090235,16829980091,16666666,16832677632,16833226466,16833282174,16833633924,16848561049,13611000,797417,16834920799,16848561049,0,16833633924,
0,5729,16846423569,16846423569,0,16846779299,16846779799,16846869424,16847933466,16879756901,16846776841,16666666,16847951924,16848577966,16848604632,16849221091,16873711966,15865666,112417,16873711966,16865548132,0,16849221091,
0,5744,16863090235,16863090235,0,16868521091,16868521591,16868754382,16872238716,16896423567,16868518841,16666666,16872258966,16872308132,16872337549,16872785716,16881700716,7935833,252084,16873737591,16881700716,0,16872785716,
0,5759,16879756901,16879756901,0,16880307132,16880307549,16880363049,16881492799,16913090233,16880304591,16666666,16881511216,16881712507,16881732632,16881959549,16899074632,15680000,133667,16899074632,16898286507,0,16881959549,
0,5774,16896423567,16896423567,0,16896940341,16896940466,16896993466,16898260007,16929756899,16896938632,16666666,16898276507,16898300174,16898331591,16898564549,16915868716,15633500,59500,16915868716,16914740549,0,16898564549,
0,5789,16913090233,16913090233,0,16913422007,16913422341,16913478632,16914387257,16946423565,16913420424,16666666,16914404257,16914755049,16914778466,16915145257,16934591591,17298583,99667,16934591591,16933200966,0,16915145257,
0,5804,16929756899,16929756899,0,16930139882,16930140049,16930227007,16933646924,16963090231,16930136966,16666666,16933668757,16933675091,16933703049,16933941257,16950968424,13569208,107083,16950968424,16948192424,0,16933941257,
0,5819,16946423565,16946423565,0,16946727049,16946727632,16946813507,16949233632,16979756897,16946725007,16666666,16949260549,16949267507,16949911632,16950203757,16980156882,13885333,67958,16980156882,16964882799,0,16950203757,
8,6017,17179756889,17179756889,0,17180052674,17180053591,17180154007,17181178507,17196423555,17179997424,16666666,17181181591,17181289216,0,0,0,0,0,0,0,0,0,
---PROFILEDATA---


	SecondaryHomeHandle0/android.view.ViewRootImpl@8090ae1 (visibility=8)
Window: SecondaryHomeHandle0
Stats since: 11583101546ns
Total frames rendered: 0
Janky frames: 0 (0.00%)
Janky frames (legacy): 0 (0.00%)
50th percentile: 4950ms
90th percentile: 4950ms
95th percentile: 4950ms
99th percentile: 4950ms
Number Missed Vsync: 0
Number High input latency: 0
Number Slow UI thread: 0
Number Slow bitmap uploads: 0
Number Slow issue draw commands: 0
Number Frame deadline missed: 0
Number Frame deadline missed (legacy): 0
HISTOGRAM: 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 26ms=0 27ms=0 28ms=0 29ms=0 30ms=0 31ms=0 32ms=0 34ms=0 36ms=0 38ms=0 40ms=0 42ms=0 44ms=0 46ms=0 48ms=0 53ms=0 57ms=0 61ms=0 65ms=0 69ms=0 73ms=0 77ms=0 81ms=0 85ms=0 89ms=0 93ms=0 97ms=0 101ms=0 105ms=0 109ms=0 113ms=0 117ms=0 121ms=0 125ms=0 129ms=0 133ms=0 150ms=0 200ms=0 250ms=0 300ms=0 350ms=0 400ms=0 450ms=0 500ms=0 550ms=0 600ms=0 650ms=0 700ms=0 750ms=0 800ms=0 850ms=0 900ms=0 950ms=0 1000ms=0 1050ms=0 1100ms=0 1150ms=0 1200ms=0 1250ms=0 1300ms=0 1350ms=0 1400ms=0 1450ms=0 1500ms=0 1550ms=0 1600ms=0 1650ms=0 1700ms=0 1750ms=0 1800ms=0 1850ms=0 1900ms=0 1950ms=0 2000ms=0 2050ms=0 2100ms=0 2150ms=0 2200ms=0 2250ms=0 2300ms=0 2350ms=0 2400ms=0 2450ms=0 2500ms=0 2550ms=0 2600ms=0 2650ms=0 2700ms=0 2750ms=0 2800ms=0 2850ms=0 2900ms=0 2950ms=0 3000ms=0 3050ms=0 3100ms=0 3150ms=0 3200ms=0 3250ms=0 3300ms=0 3350ms=0 3400ms=0 3450ms=0 3500ms=0 3550ms=0 3600ms=0 3650ms=0 3700ms=0 3750ms=0 3800ms=0 3850ms=0 3900ms=0 3950ms=0 4000ms=0 4050ms=0 4100ms=0 4150ms=0 4200ms=0 4250ms=0 4300ms=0 4350ms=0 4400ms=0 4450ms=0 4500ms=0 4550ms=0 4600ms=0 4650ms=0 4700ms=0 4750ms=0 4800ms=0 4850ms=0 4900ms=0 4950ms=0
50th gpu percentile: 4950ms
90th gpu percentile: 4950ms
95th gpu percentile: 4950ms
99th gpu percentile: 4950ms
GPU HISTOGRAM: 1ms=0 2ms=0 3ms=0 4ms=0 5ms=0 6ms=0 7ms=0 8ms=0 9ms=0 10ms=0 11ms=0 12ms=0 13ms=0 14ms=0 15ms=0 16ms=0 17ms=0 18ms=0 19ms=0 20ms=0 21ms=0 22ms=0 23ms=0 24ms=0 25ms=0 4950ms=0



---PROFILEDATA---
Flags,FrameTimelineVsyncId,IntendedVsync,Vsync,InputEventId,HandleInputStart,AnimationStart,PerformTraversalsStart,DrawStart,FrameDeadline,FrameInterval,FrameStartTime,SyncQueued,SyncStart,IssueDrawCommandsStart,SwapBuffers,FrameCompleted,DequeueBufferDuration,QueueBufferDuration,GpuCompleted,SwapBuffersCompleted,DisplayPresentTime,CommandSubmissionCompleted,
---PROFILEDATA---


View hierarchy:

  ShellDropTarget/android.view.ViewRootImpl@462592e
  8 views, 10.00 kB of render nodes

  ScreenDecorOverlay/android.view.ViewRootImpl@ca02ccf
  8 views, 11.07 kB of render nodes

  ScreenDecorOverlayBottom/android.view.ViewRootImpl@4f4565c
  7 views, 9.66 kB of render nodes

  NavigationBar0/android.view.ViewRootImpl@580fd65
  23 views, 34.13 kB of render nodes

  EdgeBackGestureHandler0/android.view.ViewRootImpl@63eda3a
  1 views, 1.25 kB of render nodes

  NotificationShade/android.view.ViewRootImpl@21cc6eb
  554 views, 692.50 kB of render nodes

  StatusBar/android.view.ViewRootImpl@f9e7c48
  56 views, 81.44 kB of render nodes

  SecondaryHomeHandle0/android.view.ViewRootImpl@8090ae1
  1 views, 1.25 kB of render nodes


Total ViewRootImpl   : 8
Total attached Views : 658
Total RenderNode     : 841.30 kB (used) / 999.73 kB (capacity)


** Graphics info for pid 554 [system] **
Profile data in ms:

View hierarchy:


Total ViewRootImpl   : 0
Total attached Views : 0
Total RenderNode     : 0.00 kB (used) / 0.00 kB (capacity)

```
