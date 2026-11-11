# 源码来源与版本

本目录 `src/` 下是 **AOSP 原始文件**（Apache 2.0），用于校验逐行注释的准确性。

| 文件 | 路径（android13-release） | 行数 |
|---|---|---|
| `IVehicle.aidl` | `hardware/interfaces/automotive/vehicle/aidl/android/hardware/automotive/vehicle/IVehicle.aidl` | 255 |
| `VehicleHal.java` | `packages/services/Car/service/src/com/android/car/hal/VehicleHal.java` | 1139 |
| `PropertyHalService.java` | `packages/services/Car/service/src/com/android/car/hal/PropertyHalService.java` | 470 |
| `CarPropertyService.java` | `packages/services/Car/service/src/com/android/car/CarPropertyService.java` | 696 |

## 拉取命令（需走代理，github.com/googlesource 直连不通）

```bash
curl -s -x http://127.0.0.1:7897 \
  "https://android.googlesource.com/platform/<path>?format=TEXT" | base64 -d
```

## 版本

- 分支：`android13-release`（Android 13 / API 33）
- 与当前模拟器（`sdk_gcar_arm64`，Android 13）版本一致
- 若后续升级到 Android 14/15，`CarPropertyService` → `CarPropertyService` 可能有拆分/重构，注意核对

> 这些文件仅作学习校验，版权归 AOSP（Apache 2.0）。