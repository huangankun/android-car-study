# dumpsys 存档：06-battery.md（讲解版）

命令：`adb shell dumpsys battery`

**这个服务是什么**：BatteryService，回答「电池现在什么状态：供电方式、电量、温度、电压、健康状况」。

**这段输出在讲什么**：这份 dump 很小（就 20 几行），但每一行都有含义——模拟器是一块「满电、健康、没在充电、25℃」的虚拟电池。

## 逐段讲解（几乎全量）

```text
Current Battery Service state:
  AC powered: false          # 没接交流电（充电器）
  USB powered: false         # 没接 USB 供电
  Wireless powered: false    # 没在无线充电
  Dock powered: false        # 没插底座
  Max charging current: 0    # 充电电流 0（因为没在充）
  Max charging voltage: 0    # 充电电压 0
  Charge counter: 10000      # 电池剩余电量计数（单位 mAh 的百分之一，10000=100mAh）
  status: 4                  # 4 = NOT_CHARGING（未充电）
  health: 2                  # 2 = GOOD（健康）
  present: true              # 电池在位
  level: 100                 # 电量 100（满）
  scale: 100                 # 电量刻度 100（level/scale = 100%）
  voltage: 5000              # 电压 5000 mV = 5V
  temperature: 250           # 温度 250 = 25.0℃（单位是十分之一度）
  technology: Li-ion         # 锂电池
```

**讲解**：两个数字字段要会「解码」，面试经常问：

| 字段 | 值 | 含义 |
|---|---|---|
| `status: 4` | 4 | 枚举值：1=UNKNOWN, 2=CHARGING, 3=DISCHARGING, 4=NOT_CHARGING, 5=FULL |
| `health: 2` | 2 | 枚举值：1=UNKNOWN, 2=GOOD, 3=OVERHEAT, 4=DEAD, 5=OVER_VOLTAGE, 6=UNSPECIFIED_FAILURE, 7=COLD |
| `level` / `scale` | 100 / 100 | 电量百分比 = level ÷ scale = 100% |
| `temperature: 250` | 250 | 单位是 **0.1℃**，250 = 25.0℃ |
| `voltage: 5000` | 5000 | 单位 **mV**，5000 = 5V |

**注意**：这里 `status=4`（NOT_CHARGING）而不是 `5`（FULL），因为模拟器没接任何电源。真机上插着充电器充满后才会看到 `status=5`。`level=100` 只是「电量满」，和「是否在充电」是两回事。

**一句话结论**：`dumpsys battery` 是最短的 dump 之一，但 status/health 是枚举、temperature 是 0.1℃、voltage 是 mV——**三个单位/枚举一错，读出来的状态就全反了**。

## 完整原始输出


```text
Current Battery Service state:
  AC powered: false
  USB powered: false
  Wireless powered: false
  Dock powered: false
  Max charging current: 0
  Max charging voltage: 0
  Charge counter: 10000
  status: 4
  health: 2
  present: true
  level: 100
  scale: 100
  voltage: 5000
  temperature: 250
  technology: Li-ion
```
