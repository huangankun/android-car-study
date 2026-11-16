# 源码来源（App 侧）

本目录 `src/` 下是 **AOSP 原始文件**（Apache 2.0），用于校验逐行注释的准确性。

| 文件 | 路径（android13-release） | 行数 |
|---|---|---|
| `CarPropertyManager.java` | `packages/services/Car/car-lib/src/android/car/hardware/property/CarPropertyManager.java` | 1048 |
| `ICarProperty.aidl` | `packages/services/Car/car-lib/src/android/car/hardware/property/ICarProperty.aidl` | 43 |

拉取命令（走代理）：
```bash
curl -s -x http://127.0.0.1:7897 \
  "https://android.googlesource.com/platform/packages/services/Car/+/refs/heads/android13-release/car-lib/src/android/car/hardware/property/<file>?format=TEXT" | base64 -d
```

> 仅作学习校验，版权归 AOSP（Apache 2.0）。