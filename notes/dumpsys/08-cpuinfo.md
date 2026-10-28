# dumpsys 存档：08-cpuinfo.md（讲解版）

命令：`adb shell dumpsys cpuinfo`

**这个服务是什么**：全局 CPU 负载统计，回答「过去 22 秒每个进程吃了多少 CPU、系统整体负载多少」。

**这段输出在讲什么**：刚 boot 完的模拟器在「热身」——system_server 和 SystemUI 各占 16% CPU，Google 后台服务在拼命初始化，整体负载 3.06（对刚启动的系统偏高，正常）。

## 逐段讲解

### 1. Load average：系统整体负载

```text
Load: 3.06 / 0.81 / 0.27
```

**讲解**：三个数是 **1 分钟 / 5 分钟 / 15 分钟** 的平均负载（Linux 概念）。3.06 表示过去 1 分钟平均有 3 个进程在等 CPU。刚 boot 完系统在密集初始化所以偏高，15 分钟值 0.27 说明已经降下来了。**面试问「负载 3 是什么意思」——不是 3% 占用，是「平均 3 个任务在可运行队列」。**

### 2. 每进程 CPU 占用（这才是排障重点）

```text
CPU usage from 22807ms to 501ms ago (...):
  16% 554/system_server: 9.6% user + 6.5% kernel / faults: 109772 minor 2061 major
  16% 765/com.android.systemui: 13% user + 2.5% kernel / faults: 128186 minor 1431 major
  10% 1344/com.google.android.gms.persistent: 6.5% user + 3.6% kernel / faults: 161010 minor 1026 major
   3.6% 51/kswapd0: 0% user + 3.6% kernel
   1% 395/surfaceflinger: 0.3% user + 0.6% kernel / faults: 3373 minor 339 major
```

**讲解**：每行一个进程（或内核线程）：
- `16%` 是总 CPU 占比，拆成 `user`（用户态）+ `kernel`（内核态）。SystemUI 的 13% user 说明它在做应用层工作（画 UI），system_server 的 6.5% kernel 偏高说明它在频繁系统调用。
- `faults: 109772 minor 2061 major` 是**缺页次数**：minor fault 是内存里已有的页（软缺页，快），major fault 是要从磁盘读的页（硬缺页，慢）。**major fault 多 = 进程在频繁换页，往往是内存不够的信号。**
- `kswapd0` 是内核的**换页守护线程**——它占 3.6% CPU 说明内核正在做内存回收，和 07-meminfo 里看到的 ZRAM 换页对上了。

### 3. 末尾 TOTAL：系统总 CPU 占用

```text
27% TOTAL: 11% user + 8.7% kernel + 1.5% iowait + 5% irq + 0.3% softirq
```

**讲解**：27% 是统计窗口内的总 CPU 占用。分解里有两个值得注意的：
- `iowait 1.5%`：CPU 在等 IO（磁盘/网络）。持续高 iowait = IO 瓶颈。
- `irq 5% + softirq 0.3%`：硬件/软件中断开销。**你在多媒体/图形栈调性能时，irq 高往往意味着外设中断频繁（触摸、GPU、网络）。**

**一句话结论**：`dumpsys cpuinfo` 是「谁在吃 CPU」的快速清单——第一看 load 三兄弟判断整体，第二扫 per-process 找占比高的进程，第三盯 major fault 和 iowait 判断是不是内存/IO 拖累。

## 完整原始输出


```text
Load: 3.06 / 0.81 / 0.27
CPU usage from 22807ms to 501ms ago (2026-10-28 11:02:29.105 to 2026-10-28 11:02:51.411):
  16% 554/system_server: 9.6% user + 6.5% kernel / faults: 109772 minor 2061 major
  16% 765/com.android.systemui: 13% user + 2.5% kernel / faults: 128186 minor 1431 major
  10% 1344/com.google.android.gms.persistent: 6.5% user + 3.6% kernel / faults: 161010 minor 1026 major
  3.9% 1659/com.google.android.gms: 2.4% user + 1.5% kernel / faults: 60224 minor 862 major
  3.6% 51/kswapd0: 0% user + 3.6% kernel
  2.4% 2647/com.google.android.tts: 2.1% user + 0.3% kernel / faults: 33949 minor 279 major
  1.8% 1632/com.google.android.googlequicksearchbox:search: 1.2% user + 0.6% kernel / faults: 56567 minor 2107 major
  1.4% 2358/com.google.android.apps.messaging: 1% user + 0.4% kernel / faults: 30141 minor 363 major
  1.3% 1405/com.google.android.apps.wellbeing: 0.7% user + 0.5% kernel / faults: 29679 minor 1243 major
  1% 395/surfaceflinger: 0.3% user + 0.6% kernel / faults: 3373 minor 339 major
  1% 1478/com.google.android.providers.media.module: 0.7% user + 0.3% kernel / faults: 20401 minor 257 major
  0.9% 433/logcat: 0% user + 0.9% kernel / faults: 50 minor
  0.9% 1054/com.google.android.apps.nexuslauncher: 0.4% user + 0.4% kernel / faults: 35133 minor 1544 major
  0.8% 1647/com.google.android.youtube: 0.4% user + 0.4% kernel / faults: 25769 minor 1112 major
  0.7% 1503/com.google.android.as: 0.4% user + 0.3% kernel / faults: 17047 minor 1611 major
  0.7% 939/com.android.settings: 0.3% user + 0.3% kernel / faults: 23620 minor 1007 major
  0.6% 937/com.android.phone: 0.4% user + 0.2% kernel / faults: 18706 minor 1204 major
  0.5% 448/media.extractor: 0.4% user + 0.1% kernel / faults: 1440 minor 17 major
  0.5% 1495/com.google.process.gservices: 0.3% user + 0.1% kernel / faults: 7060 minor 40 major
  0.3% 41/kcompactd0: 0% user + 0.3% kernel
  0.4% 2693/com.google.android.dialer: 0.3% user + 0.1% kernel / faults: 10790 minor 90 major
  0.4% 450/mediaserver: 0.1% user + 0.2% kernel / faults: 2043 minor 85 major
  0.4% 1318/com.google.android.permissioncontroller: 0.2% user + 0.1% kernel / faults: 14958 minor 1022 major
  0.4% 2753/com.google.android.apps.messaging:rcs: 0.2% user + 0.2% kernel / faults: 15945 minor 15 major
  0.4% 356/statsd: 0% user + 0.3% kernel / faults: 307 minor 7 major
  0.4% 384/android.hardware.graphics.composer3-service.ranchu: 0% user + 0.3% kernel / faults: 416 minor 134 major
  0.3% 151/logd: 0% user + 0.2% kernel / faults: 734 minor 44 major
  0.3% 1591/com.google.android.apps.youtube.music: 0.1% user + 0.1% kernel / faults: 15188 minor 2472 major
  0.3% 196/jbd2/dm-39-8: 0% user + 0.3% kernel
  0.3% 358/zygote64: 0% user + 0.3% kernel / faults: 1035 minor
  0.3% 1397/com.google.android.inputmethod.latin: 0.2% user + 0% kernel / faults: 16710 minor 728 major
  0.2% 7/kworker/0:0H-kblockd: 0% user + 0.2% kernel
  0.2% 897/com.google.android.bluetooth: 0.1% user + 0% kernel / faults: 10225 minor 371 major
  0.2% 1758/android.process.acore: 0% user + 0.1% kernel / faults: 8312 minor 228 major
  0.1% 1/init: 0% user + 0.1% kernel / faults: 418 minor 78 major
  0.1% 52/kworker/u9:0-fscrypt_read_queue: 0% user + 0.1% kernel
  0.1% 158/lmkd: 0% user + 0.1% kernel / faults: 4 minor
  0.1% 159/servicemanager: 0% user + 0% kernel / faults: 321 minor 22 major
  0.1% 195/kworker/u9:3-fscrypt_read_queue: 0% user + 0.1% kernel
  0.1% 2374/com.google.android.gms.unstable: 0.1% user + 0% kernel / faults: 6324 minor 125 major
  0.1% 190/kworker/u9:1-blk_crypto_wq: 0% user + 0.1% kernel
  0.1% 277/kworker/u8:7-loop27: 0% user + 0.1% kernel
  0.1% 292/kworker/u8:9-ext4-rsv-conversion: 0% user + 0.1% kernel
  0.1% 374/android.hardware.sensors-service.multihal: 0% user + 0% kernel / faults: 140 minor 34 major
  0.1% 410/adbd: 0% user + 0% kernel / faults: 10541 minor 3 major
  0.1% 847/com.android.networkstack.process: 0% user + 0% kernel / faults: 8908 minor 322 major
  0.1% 1174/kworker/1:6H-kblockd: 0% user + 0.1% kernel
  0% 14/rcu_preempt: 0% user + 0% kernel
  0% 49/kworker/u8:2-loop37: 0% user + 0% kernel
  0% 276/kworker/3:6H-kblockd: 0% user + 0% kernel
  0% 294/kworker/2:2H-kblockd: 0% user + 0% kernel
  0% 357/netd: 0% user + 0% kernel / faults: 896 minor 17 major
  0% 405/kworker/0:2-rcu_gp: 0% user + 0% kernel
  0% 421/drmserver: 0% user + 0% kernel / faults: 307 minor 23 major
  0% 1515/com.google.android.googlequicksearchbox:interactor: 0% user + 0% kernel / faults: 9541 minor 1292 major
  0% 1917/com.google.process.gapps: 0% user + 0% kernel / faults: 6485 minor 269 major
  0% 1939/com.google.android.devicelockcontroller: 0% user + 0% kernel / faults: 7048 minor 93 major
  0% 13/ksoftirqd/0: 0% user + 0% kernel
  0% 18/migration/0: 0% user + 0% kernel
  0% 176/keystore2: 0% user + 0% kernel / faults: 124 minor 62 major
  0% 368/android.hardware.graphics.allocator@3.0-service.ranchu: 0% user + 0% kernel / faults: 234 minor 127 major
  0% 392/audioserver: 0% user + 0% kernel / faults: 298 minor 35 major
  0% 449/media.metrics: 0% user + 0% kernel / faults: 618 minor 5 major
  0% 1138/com.google.android.cellbroadcastreceiver: 0% user + 0% kernel / faults: 5296 minor 98 major
  0% 1551/com.android.emulator.multidisplay: 0% user + 0% kernel / faults: 5475 minor 176 major
  0% 1594/com.android.printspooler: 0% user + 0% kernel / faults: 4279 minor 452 major
  0% 2052/com.google.android.apps.wallpaper: 0% user + 0% kernel / faults: 6525 minor 169 major
  0% 2223/com.google.android.as.oss: 0% user + 0% kernel / faults: 3170 minor 210 major
  0% 2226/com.android.imsserviceentitlement: 0% user + 0% kernel / faults: 4281 minor 81 major
  0% 2439/com.google.android.webview:webview_service: 0% user + 0% kernel / faults: 3355 minor 472 major
  0% 2636/com.android.externalstorage: 0% user + 0% kernel / faults: 2006 minor 95 major
 +0% 2869/com.android.camera2: 0% user + 0% kernel
 +0% 2884/com.android.dynsystem: 0% user + 0% kernel
 +0% 2912/com.android.dynsystem:dynsystem: 0% user + 0% kernel
 +0% 2926/com.android.managedprovisioning: 0% user + 0% kernel
 +0% 2993/com.android.providers.calendar: 0% user + 0% kernel
 +0% 2998/com.android.localtransport: 0% user + 0% kernel
 +0% 3066/com.android.shell: 0% user + 0% kernel
 +0% 3181/com.android.chrome: 0% user + 0% kernel
 +0% 3195/com.google.android.configupdater: 0% user + 0% kernel
 +0% 3297/com.google.android.contacts: 0% user + 0% kernel
 +0% 3356/com.google.android.gm: 0% user + 0% kernel
 +0% 3409/com.google.android.packageinstaller: 0% user + 0% kernel
 +0% 3483/com.google.android.partnersetup: 0% user + 0% kernel
 +0% 3511/com.google.android.projection.gearhead:shared: 0% user + 0% kernel
 +0% 3550/com.google.android.rkpdapp: 0% user + 0% kernel
 +0% 3570/com.google.android.settings.intelligence: 0% user + 0% kernel
 +0% 3653/com.android.emergency: 0% user + 0% kernel
 +0% 3655/com.android.traceur: 0% user + 0% kernel
 +0% 3665/com.google.android.gms.ui: 0% user + 0% kernel
 +0% 3686/com.google.android.healthconnect.controller: 0% user + 0% kernel
 +0% 3723/com.google.android.marvin.talkback: 0% user + 0% kernel
 +0% 3931/artd: 0% user + 0% kernel
 +0% 3942/dumpsys: 0% user + 0% kernel
27% TOTAL: 11% user + 8.7% kernel + 1.5% iowait + 5% irq + 0.3% softirq
```
