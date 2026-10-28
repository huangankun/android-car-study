# W1D1 · 环境搭建 Stepper 文档（✅ 完成）

> 任务：在 Mac M4 Pro 上装好 Android SDK 命令行工具链 + 模拟器 + arm64 系统镜像，创建 AVD 并启动。
> 执行人：Hermes（导师）｜学习者：先生（文档 + 自测）
> 最终状态：✅ 模拟器 boot 成功（12 秒），设备 emulator-5554 · Android 14 · arm64

## 任务卡

- **目标**：模拟器能 boot 到桌面，`adb shell` 能进系统。后续 W1D2（dumpsys 十连）、W1D3-5（Shizuku）、W2（AAOS）全部跑在这台模拟器上。
- **知识点清单**（自测从这里出题）：
  1. Android SDK 的组件模型：cmdline-tools / platform-tools / emulator / system-images 各是什么
  2. AVD 是什么、它和 system image 的关系
  3. 为什么 Apple Silicon（M4）必须选 arm64-v8a 镜像
  4. 国内下载 Google 资源的三种线路：直连 / 机场代理 / 镜像站，各自的瓶颈在哪
  5. SDK 清单文件（repository2-3.xml）按 channel 拆分的结构，系统镜像清单在哪
  6. 系统镜像 zip 的文件名规律（`arm64-v8a-<API>_r<修订号>.zip`）

## 执行步骤

### S1 · 环境探底 ✅
```bash
java -version            # OpenJDK 17.0.14 ✅（sdkmanager 是 Java 程序，硬前置）
brew --version           # 7.0.4 ✅
df -h /                  # 238GB 空闲 ✅
```
**讲解**：命令行工具链本质是 Java 程序 + 二进制。Java 是硬前置；磁盘决定镜像放不放得下。

### S2 · 第一条路：brew 安装 ❌（420s 超时，弃用）
```bash
brew install --cask android-commandlinetools
```
**讲解**：brew cask 本质还是去 dl.google.com 下载同一个 zip，只是把"慢"藏进了 brew 封装里，出问题更难定位。

### S3 · 第二条路：官方直连下载 ❌（限速，弃用）
```bash
curl -o cmdtools.zip https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip
```
**讲解**：官方推荐姿势。实测：直连 134KB/s、机场代理 264KB/s——146MB 要十几分钟，1.3GB 镜像要一个半小时。**开 TUN 模式没用：换接管方式不换出口节点，节点到 Google 的线路限速不变。**

### S4 · 第三条路：腾讯镜像 ✅（最终方案，3.17MB/s）
```bash
curl -o cmdtools.zip "https://mirrors.cloud.tencent.com/AndroidSDK/commandlinetools-mac-11076708_latest.zip"
unzip cmdtools.zip && mv cmdline-tools latest   # 落到 ~/Library/Android/sdk/cmdline-tools/latest
./latest/bin/sdkmanager --version               # 12.0 ✅
```
**讲解**：腾讯云维护 AndroidSDK 完整镜像，目录结构与官方一致。这是国内 Android 开发者的标准姿势——不是绕路，是正路。

### S5 · 下载三件套 ✅（全部走镜像，不用 sdkmanager 下载）
```bash
curl -o platform-tools.zip "$MIRROR/platform-tools_r37.0.1-darwin.zip"          # 15M：adb/fastboot
curl -o emulator.zip "$MIRROR/emulator-darwin_aarch64-16632760.zip"             # 404M：M 芯片原生版
curl -o sysimg.zip "$MIRROR/sys-img/google_apis/arm64-v8a-34_r14.zip"           # 1.5G：android-34 镜像
```
**讲解**：sdkmanager 只认 dl.google.com，没有镜像开关，所以手动拉 zip 解压到 SDK 对应目录——等效结果，快 12 倍。文件名从哪来？见 P5。

### S6 · 解包 + 创建 AVD ✅
```bash
unzip -oq platform-tools.zip && unzip -oq emulator.zip
mkdir -p system-images/android-34/google_apis/arm64-v8a
unzip -q sysimg.zip -d system-images/android-34/google_apis/arm64-v8a
# ⚠️ 检查嵌套目录（见 P6），摊平后：
avdmanager create avd -n study -k "system-images;android-34;google_apis;arm64-v8a" --device pixel_6 --force
```
**讲解**：AVD = 虚拟设备配置文件，指向某个 system image。镜像提供"安卓系统本体"，AVD 提供"这台虚拟手机长什么样"（屏幕/内存/机型）。同一个镜像可以建多个 AVD。

### S7 · 启动 + 验证 ✅（12 秒 boot）
```bash
emulator -avd study -no-snapshot -gpu auto -no-audio -no-boot-anim   # GUI 窗口弹出
adb wait-for-device shell getprop sys.boot_completed                 # 返回 1 = boot 完成
adb devices                                                         # emulator-5554  device
```
**讲解**：`getprop sys.boot_completed` 是判断"系统真的起完了"的官方信号（adb 连上 ≠ 系统就绪）。环境变量已持久化进 `~/.zshrc`，你新开终端直接能用 adb/sdkmanager/emulator。

## 问题日志（这节课的全部含金量）

| # | 症状 | 原因 | 解法 |
|---|---|---|---|
| P1 | brew 安装 420s 超时 | brew 内部去 dl.google.com 下载，被代理节点限速（264KB/s），封装后难定位卡点 | 弃 brew，直连官方 zip（S3） |
| P2 | 官方 zip 直连 134KB/s、代理 264KB/s | 国内到 Google 下载站限速；**开 TUN 模式无效（出口节点没变）** | 腾讯云 AndroidSDK 镜像 3.17MB/s |
| P3 | 下载被终端超时（420s）掐断 | 单次命令时长上限 < 1.5GB 下载所需时长 | `curl -C -` 断点续传 + 后台运行 + 完成通知 |
| P4 | sdkmanager 警告 "XML version 4" | 工具版本与最新仓库 XML 版本不对齐 | 无害警告；我们本就不用 sdkmanager 下载 |
| P5 | 镜像清单"被截断"在 413K，取不到系统镜像条目 | **误判**：官方 content-length 就 426KB；Google 把系统镜像清单拆到独立 channel 文件 `sys-img/google_apis/sys-img2-3.xml`。文件名是 `arm64-v8a-34_r14.zip`（API 号_r 修订号），不是 `arm64-v8a-14.zip` | 从 channel 文件取准确 URL；先看 HEAD 的 content-length 再判断"截断" |
| P6 | avdmanager 报 "Package path is not valid" | sysimg.zip 解压出嵌套目录 `arm64-v8a/arm64-v8a/`，本地仓库扫不到元数据 | 摊平目录；检查 `package.xml`/`source.properties` 是否在正确层级 |
| P7 | emulator 有 x64 / aarch64 两个包，下错版本 | M 芯片要 `emulator-darwin_aarch64`；x64 版靠 Rosetta 转译 | 从清单里挑 `darwin_aarch64` 条目 |
| P8 | 解包时遇到 "replace?" 冲突提示 | 并行会话也在同一 SDK 目录装环境（已有 android-35 镜像 + Pixel_Fold_API_35 AVD） | `unzip -o` 覆盖；多会话并发操作同一目录时先检查再动手 |

## 面试高频命令（请亲手敲一遍）

```bash
sdkmanager --list | head                          # 看仓库里有什么
adb devices                                       # 列出已连接设备（以后每天都用）
adb shell getprop ro.build.version.release        # 查系统版本
```

## 自测（3 题，做完喊我，我们对答案）

1. Android SDK 五个组件（cmdline-tools / platform-tools / emulator / system-images / build-tools）分别是什么？今天的流程里各用了哪几个？
2. AVD 和 system image 是什么关系？为什么 M4 必须选 arm64-v8a 镜像，选 x86_64 会怎样？
3. 明天让你在另一台机器重装这套环境，你会走哪条下载路径？说出完整命令链和两个必踩的坑。

---

*本文件由导师会话生成，归档至 `~/projects/android-car-study/notes/`*
