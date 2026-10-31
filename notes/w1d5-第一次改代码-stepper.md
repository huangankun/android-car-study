# W1D5 · 第一次改代码 Stepper 文档（✅ 完成）

> 任务：改一处 Shizuku 源码（加带标记的日志），编译、安装、启动 server，用 logcat 证明「我改的代码真的跑起来了」。
> 执行人：Hermes（导师）｜学习者：先生（文档 + 自测）
> 最终状态：✅ 构建成功（JDK 21 + NDK 29），logcat 抓到两条标记。证据存 `experiments/w1d5-first-modification/`。

## 任务卡

- **目标**：完成「改 → 编译 → 装 → 日志验证」的完整闭环，证明这次修改真的进入了运行的进程。
- **为什么做**：前面四天都是「读」。今天第一次让代码按我的意志变。这也是整月验收标准第 4 条「至少 1 处自己写的代码修改，且能被 dumpsys/日志验证」的唯一一次实弹。改哪一行不重要，**闭环**才是产出。
- **验收标准**：`adb logcat | grep W1D5-MODIFIED-MARKER` 有输出。

## 执行步骤

### S1 · 环境探底 ✅
```bash
adb devices                 # 模拟器需重启（之前关了）
git submodule update --init  # api 子模块（Shizuku-API）因浅克隆缺失
java -version               # 17 —— 但构建需要 21（见 P2）
```

### S2 · 改代码（两处，确保必定触发）✅
在 `ServiceStarter.main()` 入口加：
```java
Log.i(TAG, "W1D5-MODIFIED-MARKER: ServiceStarter.main() entered");
```
在 `ShizukuService` 构造方法 `LOGGER.i("starting server...")` 之后加：
```java
LOGGER.i("W1D5-MODIFIED-MARKER: server constructor reached (huangankun)");
```
**为什么加两处**：ServiceStarter 是进程入口（最早触发），ShizukuService 构造是 server 启动标志（证明 server 真的起了）。两处都中 = 整条链都通了。

### S3 · 构建（连续踩 3 个坑，见问题日志）✅
```bash
export JAVA_HOME=$HOME/jdk21/Contents/Home
./gradlew :manager:assembleDebug
# 产物：manager/build/outputs/apk/debug/shizuku-v13.6.0.r1.b844bc4-debug.apk
```

### S4 · 验证标记已编译进 dex（第一层证据）✅
```bash
for d in $(unzip -Z1 "$APK" | grep -E '^classes[0-9]*\.dex$'); do
  unzip -p "$APK" "$d" | strings | grep -q "W1D5-MODIFIED-MARKER" && echo "✅ $d 含标记"
done
# 输出：✅ classes2.dex 含标记
```
**讲解**：这是「代码进没进 APK」的**静态证据**——不用运行就能证明编译产物包含你的修改。

### S5 · 安装 + 启动 server ✅
```bash
adb install -r "$APK"
APK=$(adb shell pm path moe.shizuku.privileged.api | sed 's/package://')
adb shell "CLASSPATH='$APK' nohup app_process /system/bin \
  --nice-name=shizuku_server moe.shizuku.starter.ServiceStarter \
  --token=w1d5test --package=moe.shizuku.privileged.api \
  --class=rikka.shizuku.server.ShizukuService --uid=2000 >/data/local/tmp/shizuku_server.log 2>&1 &"
```
**讲解**：`app_process` 就是 `start.sh` 内部实际执行的东西。start.sh 是 manager app 生成的薄包装脚本，本质就是「设 CLASSPATH + 运行 app_process + ServiceStarter」。我们跳过 app UI，直接执行这一层。

### S6 · logcat 验证（第二层证据，核心验收）✅
```bash
adb logcat -c
# （执行 S5 的启动命令）
adb logcat -d | grep W1D5-MODIFIED-MARKER
```
**真实输出**：
```text
21:20:48.821 I ShizukuServiceStarter: W1D5-MODIFIED-MARKER: ServiceStarter.main() entered
21:20:48.980 I Service : W1D5-MODIFIED-MARKER: server constructor reached (huangankun)
```
✅ **两条都在 = 修改真的跑起来了。W1D5 验收通过。**

## 问题日志（本课 4 个真实坑）

| # | 症状 | 原因 | 解法 |
|---|---|---|---|
| P1 | `LicenceNotAcceptedException: ndk;29.0.13113456` | 根 `build.gradle` 钉了 `ndkVersion=29.0.13113456`，本机只有 NDK 25，且 licenses 未接受 | `yes \| sdkmanager --licenses` → `sdkmanager "ndk;29.0.13113456"`（约 1GB） |
| P2 | `:shell:compileDebugJavaWithJavac` → 「无效的源发行版：21」 | `:shell` 模块 source release 21，本机 JDK 17 的 javac 不支持 | 需要 JDK 21（不要改 build 配置降版本） |
| P3 | `brew install openjdk@21` → `HTTP/2 PROTOCOL_ERROR`，下载卡在固定字节 | ghcr.io（GitHub Container Registry）国内不稳；`HOMEBREW_BOTTLE_DOMAIN` 对 ghcr path 不生效 | **别等别重试**，直接从清华 Adoptium 镜像下 Temurin JDK：`https://mirrors.tuna.tsinghua.edu.cn/Adoptium/21/jdk/aarch64/mac/OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.13_9.tar.gz`（190MB / 59MB/s / 3 秒），解压后 `JAVA_HOME=<dir>/Contents/Home` |
| P4 | `start.sh` 未生成，`/sdcard/Android/data/moe.shizuku.privileged.api/` 不存在 | manager app 没走到「Start via ADB」生成脚本那步（或 UI 交互缺失） | 绕过 app，直接 `app_process` 手动拉 server（S5），效果等价 |

**P3 已沉淀进 `android-car-mentor` 技能「已知坑速查」**——以后每次构建前都会看到，不会重蹈。

## 面试高频命令

```bash
adb shell app_process                                    # 看 app_process 用法（Android 进程启动器）
adb shell CLASSPATH=<apk> app_process /system/bin <MainClass>   # 手动拉起一个 Java 进程
adb logcat -d | grep -E "TAG_A|TAG_B"                    # 按 tag 抓日志
```

## 自测（3 题，做完喊我，我们对答案）

1. 为什么 `:shell` 模块用 JDK 17 编译会报「无效的源发行版：21」？我们最后是用什么方式解决的（不是改 build 配置降版本）？
2. 构建出来的 APK 里，怎么**不运行**就证明你的修改被编译进去了？运行后又怎么证明？两层证据分别在哪个文件的哪段？
3. `app_process` 和 `start.sh` 是什么关系？为什么我们跳过 app 直接跑 `app_process` 也能起 server？

---

*本文件由导师会话生成，归档至 `~/projects/android-car-study/notes/`；证据在 `experiments/w1d5-first-modification/`*