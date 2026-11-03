# W2D1 · AAOS 镜像试跑 Stepper 文档（✅ 完成）

> 任务：在 Mac 上跑起 Android Automotive（AAOS）车端镜像，进系统 + `dumpsys car_service` 有输出。这是 W2 黄金链路的「跑车底座」。
> 执行人：Hermes（导师）｜学习者：先生
> 最终状态：✅ AAOS 启动成功（boot 23.6s，`emulator-5554`，Android 13 / userdebug / `sdk_gcar_arm64`），`dumpsys car_service` 输出 1733 行。
> 证据：`experiments/w2d1-aaos/`（dumpsys 存档 + 服务清单 + 构建信息）

## 任务卡

- **目标**：把 AAOS arm64 镜像跑起来，确认 `dumpsys car_service` 有输出。没有它，后面读 `Vehicle HAL → CarService` 全是纸上谈兵。
- **关键纠正**：计划原文写 `android-34;android-automotive;x86_64`，实际应走 **arm64 版**（`android-33;android-automotive;arm64-v8a`），Mac M 芯片原生跑，不需要 PC 兜底。
- **知识点清单**（自测出题源）：
  1. system image 的「复合 tag」：`android-automotive,google_apis` 是一个 tag，不是两个
  2. QEMU 的 `-drive` 参数用逗号分隔，路径带逗号会被截断（本课最大的坑）
  3. `avdmanager create avd` 的 `-k` 必须用完整 package path（含复合 tag）
  4. AAOS 与普通 Android 的差异：多了 CarService 及其 30+ 个子服务
  5. `dumpsys car_service --list` 列出所有 car 子服务；`dumpsys car_service` 全量 dump

## 执行步骤

### S1 · 拿镜像（腾讯镜像差点坑死）✅
```bash
# 从腾讯镜像清单取准确文件名
curl -s "https://mirrors.cloud.tencent.com/AndroidSDK/sys-img/android-automotive/sys-img2-3.xml" -o /tmp/auto.xml
# → arm64-v8a-33_r05.zip (1,311,397,288 bytes)
```
**踩坑**：腾讯镜像这个文件返回 `HTTP 200` 但 **0 字节卡住**（假成功）。换 Google 直连：
```bash
curl -L -o aaos.zip "https://dl.google.com/android/repository/sys-img/android-automotive/arm64-v8a-33_r05.zip"
# → 13.4 MB/s，1.31GB 约 40 秒下完
```
**讲解**：W1D1 记录的是「腾讯镜像 3MB/s、Google 直连 134KB/s」，这次完全反过来——**网络会变，别信一次测量**。每次下载先测速再决定线路。

### S2 · 解压到 SDK ✅
```bash
mkdir -p ~/Library/Android/sdk/system-images/android-33/android-automotive
unzip -q aaos.zip -d ~/Library/Android/sdk/system-images/android-33/android-automotive
# 解出 arm64-v8a/（含 system.img / vendor.img / kernel-ranchu 等），无嵌套
```
读 `source.properties` 发现：`SystemImage.TagId=android-automotive,google_apis`（**复合 tag**）。

### S3 · 修正目录名 + 建 AVD ✅
```bash
# 目录名必须匹配复合 tag
mv android-automotive "android-automotive,google_apis"
avdmanager create avd -n aaos -k "system-images;android-33;android-automotive,google_apis;arm64-v8a" --device pixel_6 --force
```

### S4 · 绕过逗号截断（本课核心 trick）✅
直接启动会崩：
```
qemu-system-aarch64: Could not open '/Users/.../android-33/android-automotive': No such file or directory
```
**原因**：QEMU 的 `-drive` 参数用逗号分隔选项，镜像目录名 `android-automotive,google_apis` 里的逗号把路径截断了。
**解法**：建无逗号软链 + 改 AVD 配置。
```bash
cd ~/Library/Android/sdk/system-images/android-33
ln -sfn "android-automotive,google_apis" "android-automotive-google_apis"
# 改 ~/.android/avd/aaos.avd/config.ini：
# image.sysdir.1 = system-images/android-33/android-automotive-google_apis/arm64-v8a/
```

### S5 · 启动 + 验证 ✅
```bash
emulator -avd aaos -no-snapshot -gpu auto -no-audio -no-boot-anim
adb devices                       # emulator-5554 device
adb shell getprop ro.product.name # sdk_gcar_arm64
adb shell dumpsys car_service | head -30
```
**真实输出**（节选）：
```text
13 / userdebug / sdk_gcar_arm64 / ranchu
feature:android.hardware.type.automotive

*Dump car service*
Android SDK_INT: 33
Car Version: CarVersion[name=Car.CAR_VERSION, major=33, minor=3]
*CarPropertyService*
  There are 14 clients using CarPropertyService.
  Properties registered:
    propId: 0x11200402 is registered by 1 client(s).
    ...
```
`dumpsys car_service` 全量 **1733 行**。✅ W2D1 验收通过。

## 发现问题速查（本课 3 个真实坑）

| # | 症状 | 原因 | 解法 |
|---|---|---|---|
| P1 | `avdmanager` 报 `Package path is not valid`，提示 `android-automotive,google_apis` | AAOS 镜像的 TagId 是**复合 tag**（Automotive + Google APIs 合成一个），不是单纯 `android-automotive` | 目录名改 `android-automotive,google_apis`，`-k` 用完整复合路径 |
| P2 | 启动崩：`Could not open '.../android-automotive': No such file` | QEMU `-drive` 用逗号分隔选项，目录名里的逗号把路径截断 | 建无逗号软链 `android-automotive-google_apis`，改 `config.ini` 的 `image.sysdir.1` 指向它 |
| P3 | 腾讯镜像下载 0 字节卡死（HTTP 200 假成功） | 腾讯镜像对个别 sys-img 文件服务异常 | 换 Google 直连（实测 13.4MB/s） |

**P1/P2/P3 已沉淀进 `android-car-mentor` 技能「已知坑速查」。**

## 面试高频命令

```bash
adb shell dumpsys car_service            # 全量车服务状态（W2 主战场）
adb shell dumpsys car_service --list     # 列出所有 car 子服务（33 个）
adb shell dumpsys car_service --services CarPropertyService   # 只看某个子服务
```

## 自测（3 题，做完喊我）

1. 为什么 AAOS 镜像的 tag 是 `android-automotive,google_apis` 而不是 `android-automotive`？这个复合 tag 导致了哪两个具体问题？
2. `Could not open '.../android-automotive'` 这个报错的根因是什么？为什么「建软链 + 改 config.ini」能绕过？（提示：QEMU 的参数解析）
3. AAOS 相比普通 Android，`dumpsys car_service --list` 里多出来的那些服务，大致分成哪几类？（提示：property / audio / power / user / ux / cluster）

---

*本文件由导师会话生成，归档至 `~/projects/android-car-study/notes/`；证据在 `experiments/w2d1-aaos/`*