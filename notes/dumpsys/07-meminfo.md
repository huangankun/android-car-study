# dumpsys 存档：07-meminfo.md（讲解版 · 你的强项，讲深）

命令：`adb shell dumpsys meminfo`

**这个服务是什么**：AMS 的内存子系统，回答「系统总内存多少、每个进程占多少、按什么维度切分、哪些能回收」。

**这段输出在讲什么**：这是一台 2.4GB 内存的模拟器（Total RAM 2,537,912K），系统进程 system_server 独占 168MB PSS，大量 Google 后台进程蹲在 Cached 档随时可被杀回收。

## 逐段讲解

### 1. Total RAM / Free RAM / Used RAM（先看结论，在文件末尾）

```text
Total RAM: 2,537,912K (status normal)
 Free RAM: 1,135,253K (  627,545K cached pss +   305,836K cached kernel +   201,872K free)
 Used RAM: 1,553,467K (1,252,311K used pss +   301,156K kernel)
 Lost RAM:    64,554K
     ZRAM:    73,860K physical used for   299,520K in swap (1,903,428K total swap)
```

**讲解**：`Free RAM` 的三项构成是精髓：**cached pss（627MB，进程的缓存页，可回收）+ cached kernel（306MB，内核缓存）+ 真正 free（202MB）**。Android 的「可用内存」大头是 cached——这些是进程还活着但可以随时释放的页。**面试问「Android 内存够不够」，不能只看 free，要看 free + cached。**

### 2. RSS vs PSS：为什么一份 dump 里两套排行

```text
Total RSS by process:
    341,880K: system (pid 554)
    308,036K: com.google.android.apps.wellbeing (pid 1405)
    258,836K: com.google.android.gms (pid 1659)
```

```text
Total PSS by process:
    168,526K: system (pid 554)
    119,380K: com.google.android.apps.wellbeing (pid 1405)
    114,246K: com.google.android.googlequicksearchbox:search (pid 1632)
```

**讲解**：这是内存里最容易混淆、也最常被考的三个概念：
- **RSS**（Resident Set Size）= 进程实际占用的物理内存页，但**共享库（.so）被算进了每个用它进程的 RSS**，所以加起来会重复计算。
- **PSS**（Proportional Set Size）= RSS 减去「共享内存按使用进程数均摊」的部分。system_server 的 RSS 341MB → PSS 168MB，差了一倍，就是共享库被均摊掉了。
- **USS**（Unique Set Size）= 进程独占、别人不共享的部分（这份 dump 没直接列，但 `dumpsys meminfo <pid>` 会显示）。

**一句话：RSS 高估（重复算共享）、USS 低估（不算共享）、PSS 最接近真实代价。** 这是你面试一定能拉开差距的点。

### 3. Total RSS by OOM adjustment：按「可杀优先级」分组

```text
Total RSS by OOM adjustment:
    544,788K: Native
    341,880K: System
    572,284K: Persistent
    443,948K: Foreground
  1,344,636K: Visible
  3,350,624K: Cached
```

**讲解**：进程按 oom_adj 值分组（Native/System/Persistent/Foreground/Visible/Cached），**越靠后越容易被 LMK（Low Memory Killer）杀掉**。注意 `Cached: 3,350,624K`（3.3GB RSS）远超物理内存 2.4GB——因为 Cached 里大部分是共享/可回收的，RSS 重复计算，实际压力没那么大。**查「内存紧张时谁先被杀」就看这个分组。**

### 4. 内存构成分类：一个进程的 PSS 花在哪

```text
Total PSS by category:
    606,903K: .apk mmap     # APK 文件内存映射
    297,534K: Native        # native 堆（C/C++）
    204,937K: Dalvik        # Java 堆
     84,090K: Dalvik Other  # 类结构/元数据等
     71,051K: .jar mmap
     66,850K: .so mmap      # 共享库映射
     43,515K: .dex mmap     # dex 字节码映射
```

**讲解**：这就是 `dumpsys meminfo <包名>` 单进程版里的经典分类（Dalvik Heap / Native Heap / .so mmap / .art mmap...）。你的多媒体背景里，「Native 堆涨了是 native 泄漏」「Dalvik 堆涨了是 Java 泄漏」——**这份分类就是定位内存泄漏的第一刀**。

**一句话结论**：全局 meminfo 看三件事——① 总内存和可用构成（Free=cached+free），② 谁占得多（PSS 排行，不是 RSS），③ 谁可被杀（OOM adj 分组）。定位单进程泄漏再用 `dumpsys meminfo <pid>` 看分类明细。

## 完整原始输出


```text
Applications Memory Usage (in Kilobytes):
Uptime: 36941 Realtime: 36941


Total RSS by process:
    341,880K: system (pid 554)
    308,036K: com.google.android.apps.wellbeing (pid 1405)
    258,836K: com.google.android.gms (pid 1659)
    253,164K: com.google.android.googlequicksearchbox:search (pid 1632)
    218,192K: com.google.android.gms.persistent (pid 1344)
    211,028K: com.google.android.settings.intelligence (pid 3570)
    193,320K: com.android.systemui (pid 765)
    190,784K: com.google.android.apps.nexuslauncher (pid 1054 / activities)
    181,488K: com.google.android.tts (pid 2647)
    171,252K: com.google.android.as (pid 1503)
    164,492K: com.google.android.youtube (pid 1647)
    163,632K: com.google.android.googlequicksearchbox:interactor (pid 1515)
    160,688K: com.google.android.apps.messaging (pid 2358)
    160,036K: com.google.android.apps.youtube.music (pid 1591)
    151,260K: com.google.android.gm (pid 3356)
    151,240K: com.android.settings (pid 939)
    147,216K: com.google.android.inputmethod.latin (pid 1397)
    141,988K: com.google.android.gms.unstable (pid 2374)
    137,336K: com.google.android.apps.messaging:rcs (pid 2753)
    132,372K: com.google.android.gms.ui (pid 3665)
    129,280K: com.google.android.permissioncontroller (pid 1318)
    122,448K: com.android.phone (pid 937)
    121,864K: zygote64 (pid 358)
    121,668K: com.google.android.dialer (pid 2693)
    117,996K: com.google.android.contacts (pid 3297)
    111,612K: com.android.chrome (pid 3181)
    109,596K: com.google.android.providers.media.module (pid 1478)
    102,344K: com.google.android.bluetooth (pid 897)
    100,040K: android.process.acore (pid 1758)
     96,628K: com.android.networkstack.process (pid 847)
     92,960K: com.google.android.cellbroadcastreceiver (pid 1138)
     90,216K: com.google.android.marvin.talkback (pid 3723)
     89,788K: com.google.android.devicelockcontroller (pid 1939)
     88,972K: com.google.android.apps.wallpaper (pid 2052)
     88,108K: com.google.process.gservices (pid 1495)
     86,668K: com.google.android.partnersetup (pid 3483)
     86,644K: com.google.process.gapps (pid 1917)
     86,148K: com.google.android.rkpdapp (pid 3550)
     86,020K: android.process.media (pid 1837)
     85,936K: com.android.providers.calendar (pid 2993)
     82,908K: com.google.android.configupdater (pid 3195)
     82,676K: com.google.android.webview:webview_service (pid 2439)
     82,404K: com.google.android.as.oss (pid 2223)
     82,348K: com.google.android.projection.gearhead:shared (pid 3511)
     82,336K: com.android.traceur (pid 3655)
     80,592K: com.android.localtransport (pid 2998)
     80,496K: com.android.dynsystem:dynsystem (pid 2912)
     80,072K: com.android.externalstorage (pid 2636)
     80,024K: com.android.emulator.multidisplay (pid 1551)
     79,864K: com.android.se (pid 905)
     79,860K: com.android.printspooler (pid 1594)
     79,696K: com.android.camera2 (pid 2869)
     79,604K: com.google.android.healthconnect.controller (pid 3686)
     79,460K: com.android.emergency (pid 3653)
     79,456K: com.android.imsserviceentitlement (pid 2226)
     79,332K: com.android.managedprovisioning (pid 2926)
     79,012K: com.google.android.ext.services (pid 974)
     78,772K: com.android.dynsystem (pid 2884)
     78,128K: com.google.android.packageinstaller (pid 3409)
     76,996K: com.google.android.onetimeinitializer (pid 2577)
     76,960K: com.android.shell (pid 3066)
     67,128K: webview_zygote (pid 837)
     15,300K: surfaceflinger (pid 395)
     12,276K: mediaserver (pid 450)
     11,264K: media.extractor (pid 448)
     10,672K: artd (pid 3931)
      9,752K: audioserver (pid 392)
      9,644K: cameraserver (pid 435)
      7,560K: adbd (pid 410)
      6,996K: keystore2 (pid 176)
      6,792K: netd (pid 357)
      6,736K: android.hardware.graphics.composer3-service.ranchu (pid 384)
      6,496K: media.swcodec (pid 454)
      5,948K: logd (pid 151)
      5,700K: android.hardware.graphics.allocator@3.0-service.ranchu (pid 368)
      5,440K: libgoldfish-rild (pid 453)
      5,396K: drmserver (pid 421)
      5,388K: media.metrics (pid 449)
      5,176K: android.hardware.camera.provider.ranchu (pid 362)
      5,080K: wificond (pid 452)
      4,996K: wpa_supplicant (pid 753)
      4,940K: android.hardware.neuralnetworks-service-sample-all (pid 371)
      4,936K: android.hardware.media.c2@1.0-service-goldfish (pid 370)
      4,856K: android.hardware.wifi-service (pid 379)
      4,760K: android.hardware.neuralnetworks-service-sample-limited (pid 372)
      4,636K: credstore (pid 393)
      4,628K: gpuservice (pid 394)
      4,588K: android.hardware.audio.service (pid 360)
      4,512K: android.hardware.neuralnetworks-shim-service-sample (pid 373)
      4,508K: vold (pid 168)
      4,480K: android.hardware.sensors-service.multihal (pid 374)
      4,384K: init (pid 1)
      4,336K: dumpsys (pid 3942)
      4,320K: statsd (pid 356)
      4,292K: android.hardware.bluetooth-service.default (pid 380)
      4,280K: android.hardware.camera.provider@2.7-service-google (pid 366)
      4,180K: android.system.suspend-service (pid 175)
      4,176K: gatekeeperd (pid 456)
      4,156K: android.hardware.health-service.example (pid 369)
      4,152K: installd (pid 439)
      4,112K: storaged (pid 451)
      4,048K: android.hardware.power-service.example (pid 387)
      4,024K: incidentd (pid 437)
      3,984K: lmkd (pid 158)
      3,968K: android.hardware.gnss-service.ranchu (pid 806)
      3,916K: android.hardware.biometrics.fingerprint-service.ranchu (pid 726)
      3,844K: android.hardware.authsecret-service.example (pid 361)
      3,840K: android.hardware.usb-service.example (pid 378)
      3,836K: android.hardware.biometrics.face-service.example (pid 383)
      3,788K: android.hardware.power.stats-service.example (pid 388)
      3,788K: android.hardware.rebootescrow-service.default (pid 389)
      3,780K: android.hardware.lights-service.example (pid 386)
      3,764K: android.hardware.vibrator-service.example (pid 390)
      3,760K: servicemanager (pid 159)
      3,716K: android.hardware.security.keymint-service (pid 180)
      3,680K: android.hardware.cas-service.example (pid 381)
      3,672K: android.hardware.contexthub-service.example (pid 382)
      3,648K: android.hardware.identity-service.example (pid 385)
      3,436K: android.hardware.drm-service.widevine (pid 391)
      3,168K: android.hidl.allocator@1.0-service (pid 359)
      3,092K: prng_seeder (pid 142)
      3,024K: logcat (pid 433)
      2,992K: hwservicemanager (pid 160)
      2,952K: android.hardware.gatekeeper@1.0-service.software (pid 367)
      2,928K: ip6tables-restore (pid 402)
      2,896K: mdnsd (pid 455)
      2,780K: bt_vhci_forwarder (pid 434)
      2,776K: android.hardware.thermal@2.0-service.mock (pid 377)
      2,704K: iptables-restore (pid 401)
      2,624K: dhcpclient (pid 344)
      2,560K: ueventd (pid 87)
      2,552K: traced (pid 428)
      2,528K: qemu-props (pid 167)
      2,488K: traced_probes (pid 422)
      2,460K: init (pid 86)
      2,432K: android.hardware.atrace@1.0-service (pid 177)
      2,272K: tombstoned (pid 201)
      2,232K: sh (pid 166)

Total RSS by OOM adjustment:
    544,788K: Native
        121,864K: zygote64 (pid 358)
         67,128K: webview_zygote (pid 837)
         15,300K: surfaceflinger (pid 395)
         12,276K: mediaserver (pid 450)
         11,264K: media.extractor (pid 448)
         10,672K: artd (pid 3931)
          9,752K: audioserver (pid 392)
          9,644K: cameraserver (pid 435)
          7,560K: adbd (pid 410)
          6,996K: keystore2 (pid 176)
          6,792K: netd (pid 357)
          6,736K: android.hardware.graphics.composer3-service.ranchu (pid 384)
          6,496K: media.swcodec (pid 454)
          5,948K: logd (pid 151)
          5,700K: android.hardware.graphics.allocator@3.0-service.ranchu (pid 368)
          5,440K: libgoldfish-rild (pid 453)
          5,396K: drmserver (pid 421)
          5,388K: media.metrics (pid 449)
          5,176K: android.hardware.camera.provider.ranchu (pid 362)
          5,080K: wificond (pid 452)
          4,996K: wpa_supplicant (pid 753)
          4,940K: android.hardware.neuralnetworks-service-sample-all (pid 371)
          4,936K: android.hardware.media.c2@1.0-service-goldfish (pid 370)
          4,856K: android.hardware.wifi-service (pid 379)
          4,760K: android.hardware.neuralnetworks-service-sample-limited (pid 372)
          4,636K: credstore (pid 393)
          4,628K: gpuservice (pid 394)
          4,588K: android.hardware.audio.service (pid 360)
          4,512K: android.hardware.neuralnetworks-shim-service-sample (pid 373)
          4,508K: vold (pid 168)
          4,480K: android.hardware.sensors-service.multihal (pid 374)
          4,384K: init (pid 1)
          4,336K: dumpsys (pid 3942)
          4,320K: statsd (pid 356)
          4,292K: android.hardware.bluetooth-service.default (pid 380)
          4,280K: android.hardware.camera.provider@2.7-service-google (pid 366)
          4,180K: android.system.suspend-service (pid 175)
          4,176K: gatekeeperd (pid 456)
          4,156K: android.hardware.health-service.example (pid 369)
          4,152K: installd (pid 439)
          4,112K: storaged (pid 451)
          4,048K: android.hardware.power-service.example (pid 387)
          4,024K: incidentd (pid 437)
          3,984K: lmkd (pid 158)
          3,968K: android.hardware.gnss-service.ranchu (pid 806)
          3,916K: android.hardware.biometrics.fingerprint-service.ranchu (pid 726)
          3,844K: android.hardware.authsecret-service.example (pid 361)
          3,840K: android.hardware.usb-service.example (pid 378)
          3,836K: android.hardware.biometrics.face-service.example (pid 383)
          3,788K: android.hardware.power.stats-service.example (pid 388)
          3,788K: android.hardware.rebootescrow-service.default (pid 389)
          3,780K: android.hardware.lights-service.example (pid 386)
          3,764K: android.hardware.vibrator-service.example (pid 390)
          3,760K: servicemanager (pid 159)
          3,716K: android.hardware.security.keymint-service (pid 180)
          3,680K: android.hardware.cas-service.example (pid 381)
          3,672K: android.hardware.contexthub-service.example (pid 382)
          3,648K: android.hardware.identity-service.example (pid 385)
          3,436K: android.hardware.drm-service.widevine (pid 391)
          3,168K: android.hidl.allocator@1.0-service (pid 359)
          3,092K: prng_seeder (pid 142)
          3,024K: logcat (pid 433)
          2,992K: hwservicemanager (pid 160)
          2,952K: android.hardware.gatekeeper@1.0-service.software (pid 367)
          2,928K: ip6tables-restore (pid 402)
          2,896K: mdnsd (pid 455)
          2,780K: bt_vhci_forwarder (pid 434)
          2,776K: android.hardware.thermal@2.0-service.mock (pid 377)
          2,704K: iptables-restore (pid 401)
          2,624K: dhcpclient (pid 344)
          2,560K: ueventd (pid 87)
          2,552K: traced (pid 428)
          2,528K: qemu-props (pid 167)
          2,488K: traced_probes (pid 422)
          2,460K: init (pid 86)
          2,432K: android.hardware.atrace@1.0-service (pid 177)
          2,272K: tombstoned (pid 201)
          2,232K: sh (pid 166)
    341,880K: System
        341,880K: system (pid 554)
    572,284K: Persistent
        193,320K: com.android.systemui (pid 765)
        122,448K: com.android.phone (pid 937)
         96,628K: com.android.networkstack.process (pid 847)
         80,024K: com.android.emulator.multidisplay (pid 1551)
         79,864K: com.android.se (pid 905)
    211,940K: Persistent Service
        109,596K: com.google.android.providers.media.module (pid 1478)
        102,344K: com.google.android.bluetooth (pid 897)
    443,948K: Foreground
        253,164K: com.google.android.googlequicksearchbox:search (pid 1632)
        190,784K: com.google.android.apps.nexuslauncher (pid 1054 / activities)
  1,344,636K: Visible
        258,836K: com.google.android.gms (pid 1659)
        218,192K: com.google.android.gms.persistent (pid 1344)
        171,252K: com.google.android.as (pid 1503)
        163,632K: com.google.android.googlequicksearchbox:interactor (pid 1515)
        141,988K: com.google.android.gms.unstable (pid 2374)
        129,280K: com.google.android.permissioncontroller (pid 1318)
        100,040K: android.process.acore (pid 1758)
         82,404K: com.google.android.as.oss (pid 2223)
         79,012K: com.google.android.ext.services (pid 974)
    284,552K: Perceptible
        147,216K: com.google.android.inputmethod.latin (pid 1397)
        137,336K: com.google.android.apps.messaging:rcs (pid 2753)
     86,668K: Perceptible Medium
         86,668K: com.google.android.partnersetup (pid 3483)
    775,776K: Previous
        308,036K: com.google.android.apps.wellbeing (pid 1405)
        117,996K: com.google.android.contacts (pid 3297)
         88,972K: com.google.android.apps.wallpaper (pid 2052)
         88,108K: com.google.process.gservices (pid 1495)
         86,644K: com.google.process.gapps (pid 1917)
         86,020K: android.process.media (pid 1837)
  3,350,624K: Cached
        211,028K: com.google.android.settings.intelligence (pid 3570)
        181,488K: com.google.android.tts (pid 2647)
        164,492K: com.google.android.youtube (pid 1647)
        160,688K: com.google.android.apps.messaging (pid 2358)
        160,036K: com.google.android.apps.youtube.music (pid 1591)
        151,260K: com.google.android.gm (pid 3356)
        151,240K: com.android.settings (pid 939)
        132,372K: com.google.android.gms.ui (pid 3665)
        121,668K: com.google.android.dialer (pid 2693)
        111,612K: com.android.chrome (pid 3181)
         92,960K: com.google.android.cellbroadcastreceiver (pid 1138)
         90,216K: com.google.android.marvin.talkback (pid 3723)
         89,788K: com.google.android.devicelockcontroller (pid 1939)
         86,148K: com.google.android.rkpdapp (pid 3550)
         85,936K: com.android.providers.calendar (pid 2993)
         82,908K: com.google.android.configupdater (pid 3195)
         82,676K: com.google.android.webview:webview_service (pid 2439)
         82,348K: com.google.android.projection.gearhead:shared (pid 3511)
         82,336K: com.android.traceur (pid 3655)
         80,592K: com.android.localtransport (pid 2998)
         80,496K: com.android.dynsystem:dynsystem (pid 2912)
         80,072K: com.android.externalstorage (pid 2636)
         79,860K: com.android.printspooler (pid 1594)
         79,696K: com.android.camera2 (pid 2869)
         79,604K: com.google.android.healthconnect.controller (pid 3686)
         79,460K: com.android.emergency (pid 3653)
         79,456K: com.android.imsserviceentitlement (pid 2226)
         79,332K: com.android.managedprovisioning (pid 2926)
         78,772K: com.android.dynsystem (pid 2884)
         78,128K: com.google.android.packageinstaller (pid 3409)
         76,996K: com.google.android.onetimeinitializer (pid 2577)
         76,960K: com.android.shell (pid 3066)

Total RSS by category:
  1,557,564K: .so mmap
  1,477,784K: .jar mmap
  1,372,780K: .apk mmap
  1,371,668K: .art mmap
    615,820K: Dalvik
    615,240K: .oat mmap
    379,240K: Native
    135,024K: Other mmap
    130,708K: Unknown
    107,380K: Dalvik Other
     91,296K: .dex mmap
     34,276K: Ashmem
     33,488K: Other dev
     31,316K: Stack
      3,512K: .ttf mmap
          0K: Cursor
          0K: Gfx dev
          0K: EGL mtrack
          0K: GL mtrack
          0K: Other mtrack

Total PSS by process:
    168,526K: system (pid 554)
    119,380K: com.google.android.apps.wellbeing (pid 1405)
    114,246K: com.google.android.googlequicksearchbox:search (pid 1632)
     90,595K: com.google.android.tts (pid 2647)
     75,022K: com.google.android.gms (pid 1659)
     74,877K: com.android.systemui (pid 765)
     71,037K: com.google.android.gms.persistent (pid 1344)
     68,769K: com.google.android.youtube (pid 1647)
     67,057K: com.google.android.apps.nexuslauncher (pid 1054 / activities)
     64,540K: com.google.android.settings.intelligence (pid 3570)
     54,686K: com.google.android.gm (pid 3356)
     52,871K: com.google.android.as (pid 1503)
     49,902K: com.google.android.apps.youtube.music (pid 1591)
     48,662K: com.google.android.inputmethod.latin (pid 1397)
     46,675K: com.google.android.apps.messaging (pid 2358)
     46,539K: com.google.android.googlequicksearchbox:interactor (pid 1515)
     39,983K: com.android.settings (pid 939)
     28,265K: com.google.android.apps.messaging:rcs (pid 2753)
     27,035K: com.google.android.dialer (pid 2693)
     25,062K: com.google.android.contacts (pid 3297)
     22,939K: com.android.phone (pid 937)
     22,715K: com.google.android.gms.ui (pid 3665)
     21,857K: com.android.chrome (pid 3181)
     20,099K: com.google.android.gms.unstable (pid 2374)
     19,997K: com.google.android.permissioncontroller (pid 1318)
     18,827K: com.google.android.providers.media.module (pid 1478)
     18,215K: surfaceflinger (pid 395)
     15,431K: com.google.android.bluetooth (pid 897)
     14,908K: android.hardware.graphics.composer3-service.ranchu (pid 384)
     12,655K: android.process.acore (pid 1758)
     12,115K: com.google.android.marvin.talkback (pid 3723)
     10,407K: com.google.android.cellbroadcastreceiver (pid 1138)
     10,231K: com.google.android.apps.wallpaper (pid 2052)
      9,958K: com.android.networkstack.process (pid 847)
      9,896K: com.google.android.devicelockcontroller (pid 1939)
      8,528K: zygote64 (pid 358)
      8,125K: media.swcodec (pid 454)
      8,036K: com.google.process.gservices (pid 1495)
      7,641K: com.google.android.healthconnect.controller (pid 3686)
      7,369K: com.android.emergency (pid 3653)
      7,263K: com.google.android.projection.gearhead:shared (pid 3511)
      7,078K: com.android.traceur (pid 3655)
      7,059K: com.google.android.rkpdapp (pid 3550)
      6,822K: com.google.process.gapps (pid 1917)
      6,683K: android.process.media (pid 1837)
      6,304K: com.google.android.as.oss (pid 2223)
      6,286K: com.google.android.partnersetup (pid 3483)
      6,197K: com.google.android.webview:webview_service (pid 2439)
      5,928K: com.android.imsserviceentitlement (pid 2226)
      5,904K: audioserver (pid 392)
      5,724K: com.google.android.packageinstaller (pid 3409)
      5,718K: com.google.android.configupdater (pid 3195)
      5,619K: com.android.providers.calendar (pid 2993)
      5,585K: mediaserver (pid 450)
      5,567K: android.hardware.graphics.allocator@3.0-service.ranchu (pid 368)
      5,560K: com.android.managedprovisioning (pid 2926)
      5,445K: cameraserver (pid 435)
      5,427K: media.extractor (pid 448)
      5,207K: com.android.camera2 (pid 2869)
      4,964K: com.android.printspooler (pid 1594)
      4,895K: com.google.android.ext.services (pid 974)
      4,755K: com.android.emulator.multidisplay (pid 1551)
      4,753K: com.android.se (pid 905)
      4,718K: webview_zygote (pid 837)
      4,619K: com.android.shell (pid 3066)
      4,581K: com.android.externalstorage (pid 2636)
      4,541K: com.android.dynsystem:dynsystem (pid 2912)
      4,539K: com.android.localtransport (pid 2998)
      4,487K: adbd (pid 410)
      4,385K: com.android.dynsystem (pid 2884)
      4,378K: com.google.android.onetimeinitializer (pid 2577)
      4,330K: init (pid 1)
      3,966K: logd (pid 151)
      3,557K: keystore2 (pid 176)
      3,294K: netd (pid 357)
      3,183K: artd (pid 3931)
      3,036K: libgoldfish-rild (pid 453)
      2,575K: android.hardware.media.c2@1.0-service-goldfish (pid 370)
      2,346K: media.metrics (pid 449)
      2,289K: android.hardware.camera.provider@2.7-service-google (pid 366)
      2,246K: android.hardware.audio.service (pid 360)
      2,013K: wpa_supplicant (pid 753)
      1,983K: vold (pid 168)
      1,949K: statsd (pid 356)
      1,857K: ueventd (pid 87)
      1,842K: android.hardware.camera.provider.ranchu (pid 362)
      1,785K: installd (pid 439)
      1,723K: android.hardware.wifi-service (pid 379)
      1,718K: wificond (pid 452)
      1,613K: servicemanager (pid 159)
      1,578K: gpuservice (pid 394)
      1,565K: init (pid 86)
      1,546K: drmserver (pid 421)
      1,430K: android.hardware.neuralnetworks-service-sample-all (pid 371)
      1,394K: android.hardware.neuralnetworks-shim-service-sample (pid 373)
      1,388K: credstore (pid 393)
      1,377K: android.hardware.sensors-service.multihal (pid 374)
      1,276K: hwservicemanager (pid 160)
      1,260K: android.hardware.neuralnetworks-service-sample-limited (pid 372)
      1,256K: android.hardware.security.keymint-service (pid 180)
      1,245K: android.system.suspend-service (pid 175)
      1,209K: prng_seeder (pid 142)
      1,087K: android.hardware.bluetooth-service.default (pid 380)
      1,076K: ip6tables-restore (pid 402)
      1,068K: storaged (pid 451)
      1,063K: lmkd (pid 158)
      1,029K: iptables-restore (pid 401)
      1,016K: incidentd (pid 437)
      1,014K: android.hardware.drm-service.widevine (pid 391)
        995K: gatekeeperd (pid 456)
        944K: android.hardware.gnss-service.ranchu (pid 806)
        943K: android.hardware.biometrics.fingerprint-service.ranchu (pid 726)
        938K: android.hardware.health-service.example (pid 369)
        924K: mdnsd (pid 455)
        910K: android.hardware.identity-service.example (pid 385)
        887K: android.hardware.biometrics.face-service.example (pid 383)
        884K: android.hardware.gatekeeper@1.0-service.software (pid 367)
        877K: android.hardware.atrace@1.0-service (pid 177)
        868K: android.hardware.usb-service.example (pid 378)
        864K: dumpsys (pid 3942)
        855K: logcat (pid 433)
        851K: traced (pid 428)
        827K: android.hardware.cas-service.example (pid 381)
        819K: traced_probes (pid 422)
        810K: android.hardware.power-service.example (pid 387)
        809K: sh (pid 166)
        808K: android.hardware.thermal@2.0-service.mock (pid 377)
        807K: qemu-props (pid 167)
        801K: android.hardware.power.stats-service.example (pid 388)
        797K: android.hardware.vibrator-service.example (pid 390)
        784K: android.hardware.authsecret-service.example (pid 361)
        784K: android.hardware.lights-service.example (pid 386)
        780K: android.hardware.contexthub-service.example (pid 382)
        779K: android.hardware.rebootescrow-service.default (pid 389)
        746K: android.hidl.allocator@1.0-service (pid 359)
        665K: bt_vhci_forwarder (pid 434)
        639K: tombstoned (pid 201)
        610K: dhcpclient (pid 344)

Total PSS by OOM adjustment:
    182,096K: Native
         18,215K: surfaceflinger (pid 395)
         14,908K: android.hardware.graphics.composer3-service.ranchu (pid 384)
          8,528K: zygote64 (pid 358)
          8,125K: media.swcodec (pid 454)
          5,904K: audioserver (pid 392)
          5,585K: mediaserver (pid 450)
          5,567K: android.hardware.graphics.allocator@3.0-service.ranchu (pid 368)
          5,445K: cameraserver (pid 435)
          5,427K: media.extractor (pid 448)
          4,718K: webview_zygote (pid 837)
          4,487K: adbd (pid 410)
          4,330K: init (pid 1)
          3,966K: logd (pid 151)
          3,557K: keystore2 (pid 176)
          3,294K: netd (pid 357)
          3,183K: artd (pid 3931)
          3,036K: libgoldfish-rild (pid 453)
          2,575K: android.hardware.media.c2@1.0-service-goldfish (pid 370)
          2,346K: media.metrics (pid 449)
          2,289K: android.hardware.camera.provider@2.7-service-google (pid 366)
          2,246K: android.hardware.audio.service (pid 360)
          2,013K: wpa_supplicant (pid 753)
          1,983K: vold (pid 168)
          1,949K: statsd (pid 356)
          1,857K: ueventd (pid 87)
          1,842K: android.hardware.camera.provider.ranchu (pid 362)
          1,785K: installd (pid 439)
          1,723K: android.hardware.wifi-service (pid 379)
          1,718K: wificond (pid 452)
          1,613K: servicemanager (pid 159)
          1,578K: gpuservice (pid 394)
          1,565K: init (pid 86)
          1,546K: drmserver (pid 421)
          1,430K: android.hardware.neuralnetworks-service-sample-all (pid 371)
          1,394K: android.hardware.neuralnetworks-shim-service-sample (pid 373)
          1,388K: credstore (pid 393)
          1,377K: android.hardware.sensors-service.multihal (pid 374)
          1,276K: hwservicemanager (pid 160)
          1,260K: android.hardware.neuralnetworks-service-sample-limited (pid 372)
          1,256K: android.hardware.security.keymint-service (pid 180)
          1,245K: android.system.suspend-service (pid 175)
          1,209K: prng_seeder (pid 142)
          1,087K: android.hardware.bluetooth-service.default (pid 380)
          1,076K: ip6tables-restore (pid 402)
          1,068K: storaged (pid 451)
          1,063K: lmkd (pid 158)
          1,029K: iptables-restore (pid 401)
          1,016K: incidentd (pid 437)
          1,014K: android.hardware.drm-service.widevine (pid 391)
            995K: gatekeeperd (pid 456)
            944K: android.hardware.gnss-service.ranchu (pid 806)
            943K: android.hardware.biometrics.fingerprint-service.ranchu (pid 726)
            938K: android.hardware.health-service.example (pid 369)
            924K: mdnsd (pid 455)
            910K: android.hardware.identity-service.example (pid 385)
            887K: android.hardware.biometrics.face-service.example (pid 383)
            884K: android.hardware.gatekeeper@1.0-service.software (pid 367)
            877K: android.hardware.atrace@1.0-service (pid 177)
            868K: android.hardware.usb-service.example (pid 378)
            864K: dumpsys (pid 3942)
            855K: logcat (pid 433)
            851K: traced (pid 428)
            827K: android.hardware.cas-service.example (pid 381)
            819K: traced_probes (pid 422)
            810K: android.hardware.power-service.example (pid 387)
            809K: sh (pid 166)
            808K: android.hardware.thermal@2.0-service.mock (pid 377)
            807K: qemu-props (pid 167)
            801K: android.hardware.power.stats-service.example (pid 388)
            797K: android.hardware.vibrator-service.example (pid 390)
            784K: android.hardware.authsecret-service.example (pid 361)
            784K: android.hardware.lights-service.example (pid 386)
            780K: android.hardware.contexthub-service.example (pid 382)
            779K: android.hardware.rebootescrow-service.default (pid 389)
            746K: android.hidl.allocator@1.0-service (pid 359)
            665K: bt_vhci_forwarder (pid 434)
            639K: tombstoned (pid 201)
            610K: dhcpclient (pid 344)
    168,526K: System
        168,526K: system (pid 554)
    117,282K: Persistent
         74,877K: com.android.systemui (pid 765)
         22,939K: com.android.phone (pid 937)
          9,958K: com.android.networkstack.process (pid 847)
          4,755K: com.android.emulator.multidisplay (pid 1551)
          4,753K: com.android.se (pid 905)
     34,258K: Persistent Service
         18,827K: com.google.android.providers.media.module (pid 1478)
         15,431K: com.google.android.bluetooth (pid 897)
    181,303K: Foreground
        114,246K: com.google.android.googlequicksearchbox:search (pid 1632)
         67,057K: com.google.android.apps.nexuslauncher (pid 1054 / activities)
    309,419K: Visible
         75,022K: com.google.android.gms (pid 1659)
         71,037K: com.google.android.gms.persistent (pid 1344)
         52,871K: com.google.android.as (pid 1503)
         46,539K: com.google.android.googlequicksearchbox:interactor (pid 1515)
         20,099K: com.google.android.gms.unstable (pid 2374)
         19,997K: com.google.android.permissioncontroller (pid 1318)
         12,655K: android.process.acore (pid 1758)
          6,304K: com.google.android.as.oss (pid 2223)
          4,895K: com.google.android.ext.services (pid 974)
     76,927K: Perceptible
         48,662K: com.google.android.inputmethod.latin (pid 1397)
         28,265K: com.google.android.apps.messaging:rcs (pid 2753)
      6,286K: Perceptible Medium
          6,286K: com.google.android.partnersetup (pid 3483)
    176,214K: Previous
        119,380K: com.google.android.apps.wellbeing (pid 1405)
         25,062K: com.google.android.contacts (pid 3297)
         10,231K: com.google.android.apps.wallpaper (pid 2052)
          8,036K: com.google.process.gservices (pid 1495)
          6,822K: com.google.process.gapps (pid 1917)
          6,683K: android.process.media (pid 1837)
    627,545K: Cached
         90,595K: com.google.android.tts (pid 2647)
         68,769K: com.google.android.youtube (pid 1647)
         64,540K: com.google.android.settings.intelligence (pid 3570)
         54,686K: com.google.android.gm (pid 3356)
         49,902K: com.google.android.apps.youtube.music (pid 1591)
         46,675K: com.google.android.apps.messaging (pid 2358)
         39,983K: com.android.settings (pid 939)
         27,035K: com.google.android.dialer (pid 2693)
         22,715K: com.google.android.gms.ui (pid 3665)
         21,857K: com.android.chrome (pid 3181)
         12,115K: com.google.android.marvin.talkback (pid 3723)
         10,407K: com.google.android.cellbroadcastreceiver (pid 1138)
          9,896K: com.google.android.devicelockcontroller (pid 1939)
          7,641K: com.google.android.healthconnect.controller (pid 3686)
          7,369K: com.android.emergency (pid 3653)
          7,263K: com.google.android.projection.gearhead:shared (pid 3511)
          7,078K: com.android.traceur (pid 3655)
          7,059K: com.google.android.rkpdapp (pid 3550)
          6,197K: com.google.android.webview:webview_service (pid 2439)
          5,928K: com.android.imsserviceentitlement (pid 2226)
          5,724K: com.google.android.packageinstaller (pid 3409)
          5,718K: com.google.android.configupdater (pid 3195)
          5,619K: com.android.providers.calendar (pid 2993)
          5,560K: com.android.managedprovisioning (pid 2926)
          5,207K: com.android.camera2 (pid 2869)
          4,964K: com.android.printspooler (pid 1594)
          4,619K: com.android.shell (pid 3066)
          4,581K: com.android.externalstorage (pid 2636)
          4,541K: com.android.dynsystem:dynsystem (pid 2912)
          4,539K: com.android.localtransport (pid 2998)
          4,385K: com.android.dynsystem (pid 2884)
          4,378K: com.google.android.onetimeinitializer (pid 2577)

Total PSS by category:
    606,903K: .apk mmap
    297,534K: Native
    204,937K: Dalvik
    104,394K: Unknown
     84,090K: Dalvik Other
     71,051K: .jar mmap
     66,850K: .so mmap
     48,032K: .art mmap
     43,515K: .dex mmap
     30,820K: Stack
     15,656K: Other mmap
     13,643K: .oat mmap
      1,198K: Other dev
      1,092K: .ttf mmap
        919K: Ashmem
          0K: Cursor
          0K: Gfx dev
          0K: EGL mtrack
          0K: GL mtrack
          0K: Other mtrack

Total RAM: 2,537,912K (status normal)
 Free RAM: 1,135,253K (  627,545K cached pss +   305,836K cached kernel +   201,872K free)
DMA-BUF:         0K (        0K mapped +         0K unmapped)
DMA-BUF Heaps:         0K
      GPU:         0K
 Used RAM: 1,553,467K (1,252,311K used pss +   301,156K kernel)
 Lost RAM:    64,554K
     ZRAM:    73,860K physical used for   299,520K in swap (1,903,428K total swap)
   Tuning: 192 (large 576), oom   322,560K, restore limit   107,520K (high-end-gfx)
```
