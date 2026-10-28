# dumpsys 存档：05-power.md（讲解版）

命令：`adb shell dumpsys power`

**这个服务是什么**：PowerManagerService（PMS，和包管理的 PMS 缩写撞了，注意区分），回答「屏幕亮没亮、系统睡没睡、谁拿着 wakelock 不让睡」。

**这段输出在讲什么**：模拟器处于 Awake（唤醒）状态、插着电源不担心没电、屏保超时被设成「永不休眠」，有 15 个 wakelock 被持有（全是后台服务拿的 PARTIAL 型，没有一个是让屏幕常亮的）。

## 逐段讲解

### 1. Power Manager State：电源状态机的核心字段

```text
Power Manager State:
  mWakefulness=Awake
  mWakefulnessChanging=false
  mIsPowered=false
  mPlugType=0
  mBatteryLevel=100
  mBatteryLevelLow=false
  mDeviceIdleMode=false
  mHoldingWakeLockSuspendBlocker=true
```

**讲解**：`mWakefulness=Awake` 是核心——**wakefulness（清醒度）是电源状态机的一等公民**，取值有 Awake / Dreaming / Dozing / Asleep 四态。当前是 Awake（醒着）。`mIsPowered=false` 说明没接电源（纯模拟器默认），`mBatteryLevel=100` 满电。`mHoldingWakeLockSuspendBlocker=true` 表示系统因为持有 wakelock 而「挡住 CPU 挂起」。

### 2. 超时设置：为什么屏幕一直不灭

```text
Screen off timeout: 2147483647 ms
Sleep timeout: -1 ms
```

**讲解**：`2147483647` 是 `Integer.MAX_VALUE`，也就是「永不自动关屏」——模拟器为了方便调试默认这样设。真机上这个值一般是 30 秒到几分钟。**这就是为什么你的模拟器放多久屏幕都不黑。**

### 3. Wake Locks：谁在阻止系统休眠

```text
Wake Locks: size=15
  PARTIAL_WAKE_LOCK              '*telephony-radio*' ACQ=-16s776ms (uid=1001 pid=937 ws=WorkSource{1001 com.android.phone})
  PARTIAL_WAKE_LOCK              '*job*/com.google.android.googlequicksearchbox/...' ACQ=-23s565ms (uid=1000 pid=554 ...)
  PARTIAL_WAKE_LOCK              'fiid-sync' ACQ=-22s776ms (uid=10155 pid=1591)
  ...
```

**讲解**：15 个 wakelock 正在被持有。关键点：
- **全是 `PARTIAL_WAKE_LOCK`**——这种只让 CPU 保持运行、**不让屏幕亮**。没有一个是 `SCREEN_BRIGHT_WAKE_LOCK` 或 `FULL_WAKE_LOCK`（那两种才会点亮屏幕）。所以屏幕虽然不灭，但也不是被 wakelock 点亮的。
- 持有者全是后台服务：telephony（电话）、GMS 的 job 调度、fiid-sync（Firebase 实例 ID 同步）。**这是 Android 上「App 偷偷耗电」的头号来源——后台服务拿着 wakelock 不让 CPU 睡。**
- `ACQ=-16s776ms` 是「acquire 于 16.7 秒前」。

### 4. Suspend Blockers：比 wakelock 更底层的「挂起闸门」

```text
Suspend Blockers: size=5
  PowerManagerService.Booting: ref count=0 []
  PowerManagerService.WakeLocks: ref count=1 [unknown: (10-28 11:02:25.378)]
  PowerManagerService.Display: ref count=1 [holding display: (10-28 11:02:23.590)]
```

**讲解**：SuspendBlocker 是内核 autosleep 之上的闸门。`WakeLocks` 和 `Display` 两个 blocker 的 ref count=1，对应前面看到的「有 wakelock + 屏幕显示中」。**面试区分：wakelock 是 App 层的 API，SuspendBlocker 是 PowerManagerService 内部管理的内核挂起闸门，一层套一层。**

### 5. 其余快速认路

- `UID states`（第 104 行）：每个 UID 的电源状态（ACTIVE/INACTIVE），Doze 白名单机制会看它。
- `Battery saver policy`（第 200 行起）：省电模式的策略配置，仅省电模式开启时生效。
- `Wake Lock Log`（第 364 行起，600 多行）：wakelock 的获取/释放历史流水账，查「谁在反复拿锁」翻这里。

**一句话结论**：这份 dump 是「系统的睡眠决策报告」。查「手机为什么老不睡 / 谁在偷偷拿 wakelock / 屏幕为什么不灭」，就对着 `mWakefulness`、`Wake Locks`、超时设置这三段看。

## 完整原始输出


```text
POWER MANAGER (dumpsys power)

Power Manager State:
  Settings power_manager_constants:
    no_cached_wake_locks=true
  mDirty=0x0
  mWakefulness=Awake
  mWakefulnessChanging=false
  mIsPowered=false
  mPlugType=0
  mBatteryLevel=100
  mDreamsBatteryLevelDrain=0
  mDockState=0
  mStayOn=false
  mProximityPositive=false
  mBootCompleted=true
  mSystemReady=true
  mEnhancedDischargeTimeElapsed=0
  mLastEnhancedDischargeTimeUpdatedElapsed=0
  mEnhancedDischargePredictionIsPersonalized=false
  mHalAutoSuspendModeEnabled=false
  mHalInteractiveModeEnabled=true
  mWakeLockSummary=0x1
  mNotifyLongScheduled=+33s455ms
  mNotifyLongDispatched=(none)
  mNotifyLongNextCheck=(none)
  mRequestWaitForNegativeProximity=false
  mInterceptedPowerKeyForProximity=false
  mSandmanScheduled=false
  mBatteryLevelLow=false
  mLightDeviceIdleMode=false
  mDeviceIdleMode=false
  mDeviceIdleWhitelist=[2000, 10084, 10088, 10090, 10128, 10164, 10189]
  mDeviceIdleTempWhitelist=[10120, 10121, 10127, 10185]
  mLowPowerStandbyActive=false
  mLastWakeTime=0 (36880 ms ago)
  mLastSleepTime=0 (36880 ms ago)
  mLastSleepReason=application
  mLastGlobalWakeTimeRealtime=0 (36880 ms ago)
  mLastGlobalSleepTimeRealtime=0 (36880 ms ago)
  mLastInteractivePowerHintTime=12294 (24586 ms ago)
  mLastScreenBrightnessBoostTime=0 (36880 ms ago)
  mScreenBrightnessBoostInProgress=false
  mHoldingWakeLockSuspendBlocker=true
  mHoldingDisplaySuspendBlocker=true
  mLastFlipTime=0
  mIsFaceDown=false

Settings and Configuration:
  mDecoupleHalAutoSuspendModeFromDisplayConfig=false
  mDecoupleHalInteractiveModeFromDisplayConfig=false
  mWakeUpWhenPluggedOrUnpluggedConfig=false
  mWakeUpWhenPluggedOrUnpluggedInTheaterModeConfig=false
  mTheaterModeEnabled=false
  mKeepDreamingWhenUnplugging=false
  mSuspendWhenScreenOffDueToProximityConfig=false
  mDreamsSupportedConfig=true
  mDreamsEnabledByDefaultConfig=true
  mDreamsActivatedOnSleepByDefaultConfig=false
  mDreamsActivatedOnDockByDefaultConfig=true
  mDreamsEnabledOnBatteryConfig=false
  mDreamsBatteryLevelMinimumWhenPoweredConfig=-1
  mDreamsBatteryLevelMinimumWhenNotPoweredConfig=15
  mDreamsBatteryLevelDrainCutoffConfig=5
  mDreamsEnabledSetting=true
  mDreamsActivateOnSleepSetting=false
  mDreamsActivateOnDockSetting=true
  mDozeAfterScreenOff=true
  mMinimumScreenOffTimeoutConfig=10000
  mMaximumScreenDimDurationConfig=7000
  mMaximumScreenDimRatioConfig=0.20000005
  mAttentiveTimeoutConfig=-1
  mAttentiveTimeoutSetting=-1
  mAttentiveWarningDurationConfig=30000
  mScreenOffTimeoutSetting=2147483647
  mSleepTimeoutSetting=-1
  mMaximumScreenOffTimeoutFromDeviceAdmin=9223372036854775807 (enforced=false)
  mStayOnWhilePluggedInSetting=1
  mScreenBrightnessOverrideFromWindowManager=NaN
  mUserActivityTimeoutOverrideFromWindowManager=-1
  mUserInactiveOverrideFromWindowManager=false
  mDozeScreenStateOverrideFromDreamManager=0
  mDrawWakeLockOverrideFromSidekick=false
  mDozeScreenBrightnessOverrideFromDreamManager=-1
  mScreenBrightnessMinimum=0.035433073
  mScreenBrightnessMaximum=1.0
  mScreenBrightnessDefault=0.39763778
  mDoubleTapWakeEnabled=false
  mForegroundProfile=0
  mUserId=0

Attentive timeout: -1 ms
Sleep timeout: -1 ms
Screen off timeout: 2147483647 ms
Screen dim duration: 7000 ms

UID states (changing=false changed=false):
  UID 1000:   ACTIVE  count=2 state=0
  UID 1001:   ACTIVE  count=1 state=0
  UID 1002:   ACTIVE  count=0 state=0
  UID 1068:   ACTIVE  count=0 state=0
  UID 1073:   ACTIVE  count=0 state=0
  UID 2000:   ACTIVE  count=0 state=19
  UID u0a84:   ACTIVE  count=0 state=15
  UID u0a86:   ACTIVE  count=0 state=5
  UID u0a88:   ACTIVE  count=0 state=19
  UID u0a91:   ACTIVE  count=0 state=19
  UID u0a92: INACTIVE  count=0 state=19
  UID u0a97:   ACTIVE  count=0 state=19
  UID u0a104:   ACTIVE  count=0 state=19
  UID u0a105:   ACTIVE  count=0 state=19
  UID u0a118:   ACTIVE  count=0 state=19
  UID u0a120:   ACTIVE  count=0 state=8
  UID u0a121:   ACTIVE  count=0 state=15
  UID u0a123:   ACTIVE  count=0 state=19
  UID u0a124:   ACTIVE  count=0 state=19
  UID u0a125:   ACTIVE  count=0 state=19
  UID u0a126:   ACTIVE  count=0 state=5
  UID u0a127:   ACTIVE  count=0 state=19
  UID u0a128:   ACTIVE  count=8 state=3
  UID u0a129:   ACTIVE  count=0 state=19
  UID u0a130:   ACTIVE  count=1 state=5
  UID u0a131:   ACTIVE  count=0 state=5
  UID u0a132:   ACTIVE  count=0 state=3
  UID u0a135:   ACTIVE  count=0 state=19
  UID u0a139:   ACTIVE  count=0 state=19
  UID u0a141: INACTIVE  count=0 state=19
  UID u0a145:   ACTIVE  count=1 state=19
  UID u0a147: INACTIVE  count=0 state=19
  UID u0a149:   ACTIVE  count=0 state=19
  UID u0a151:   ACTIVE  count=0 state=7
  UID u0a153:   ACTIVE  count=0 state=15
  UID u0a155:   ACTIVE  count=1 state=19
  UID u0a156:   ACTIVE  count=1 state=19
  UID u0a162:   ACTIVE  count=0 state=2
  UID u0a164: INACTIVE  count=0 state=19
  UID u0a167:   ACTIVE  count=0 state=15
  UID u0a169:   ACTIVE  count=0 state=0
  UID u0a170: INACTIVE  count=0 state=19
  UID u0a182:   ACTIVE  count=0 state=6
  UID u0a185:   ACTIVE  count=0 state=19
  UID u0a186:   ACTIVE  count=0 state=0
  UID u0a187:   ACTIVE  count=0 state=5
  UID u0a189:   ACTIVE  count=0 state=19
  UID u0a191:   ACTIVE  count=0 state=19

Looper state:
  Looper (PowerManagerService, tid 49) {77cfc17}
    Message 0: { when=+33s455ms what=4 target=android.os.Handler }
    Message 1: { when=+24d20h30m52s61ms what=1 target=android.os.Handler }
    (Total messages: 2, polling=true, quitting=false)

Wake Locks: size=15
  PARTIAL_WAKE_LOCK              '*telephony-radio*' ACQ=-16s776ms (uid=1001 pid=937 ws=WorkSource{1001 com.android.phone})
  PARTIAL_WAKE_LOCK              '*job*/com.google.android.googlequicksearchbox/com.google.android.apps.gsa.tasks.BackgroundTasksJobService#-151' ACQ=-23s565ms (uid=1000 pid=554 ws=WorkSource{10132 com.google.android.googlequicksearchbox})
  PARTIAL_WAKE_LOCK              'fiid-sync' ACQ=-22s776ms (uid=10155 pid=1591)
  PARTIAL_WAKE_LOCK              '*gms_scheduler*/com.google.android.gms/.phenotype.service.sync.PhenotypeConfigurator' ACQ=-21s805ms (uid=10128 pid=1344 ws=WorkSource{10128 com.google.android.gms})
  PARTIAL_WAKE_LOCK              'fiid-sync' ACQ=-21s380ms (uid=10156 pid=1647)
  PARTIAL_WAKE_LOCK              'fiid-sync' ACQ=-21s326ms (uid=10130 pid=2358)
  PARTIAL_WAKE_LOCK              'fiid-sync' ACQ=-20s215ms (uid=10145 pid=3356)
  PARTIAL_WAKE_LOCK              'IntentOp:.chimera.container.InitConfigOperation' ACQ=-20s205ms (uid=10128 pid=1659 ws=WorkSource{10128 com.google.android.gms})
  PARTIAL_WAKE_LOCK              '*job*/com.google.android.partnersetup/.PhenotypeJobService#1' ACQ=-19s973ms (uid=1000 pid=554 ws=WorkSource{10120 com.google.android.partnersetup})
  PARTIAL_WAKE_LOCK              '*gms_scheduler*/com.google.android.gms/.chimera.container.ConfigService' ACQ=-19s899ms (uid=10128 pid=1344 ws=WorkSource{10128 com.google.android.gms})
  PARTIAL_WAKE_LOCK              'wake:com.google.android.gms/.chimera.GmsIntentOperationService - 913' ACQ=-18s389ms (uid=10128 pid=1659)
  PARTIAL_WAKE_LOCK              'Checkin Service' ACQ=-18s383ms (uid=10128 pid=1659 ws=WorkSource{10128 com.google.android.gms})
  PARTIAL_WAKE_LOCK              'IntentOp:.chimera.container.InitConfigOperation' ACQ=-18s249ms (uid=10128 pid=1659 ws=WorkSource{10128 com.google.android.gms})
  PARTIAL_WAKE_LOCK              'IntentOp:.chimera.container.InitConfigOperation' ACQ=-18s37ms (uid=10128 pid=1659 ws=WorkSource{10128 com.google.android.gms})
  PARTIAL_WAKE_LOCK              'IntentOp:.chimera.container.InitConfigOperation' ACQ=-17s996ms (uid=10128 pid=1659 ws=WorkSource{10128 com.google.android.gms})

Suspend Blockers: size=5
  PowerManagerService.Booting: ref count=0 []
  PowerManagerService.WakeLocks: ref count=1 [unknown: (10-28 11:02:25.378)]
  PowerManagerService.Display: ref count=1 [holding display: (10-28 11:02:23.590)]
  PowerManagerService.Broadcasts: ref count=0 []
  PowerManagerService.WirelessChargerDetector: ref count=0 []

Display Power: com.android.server.power.PowerManagerService$1@5d08804

Battery saving stats:
  Battery Saver is currently: OFF
    Times full enabled: 0
    Times adaptive enabled: 0
  
  Drain stats:
                     Battery saver OFF                          ON
  NonDoze NonIntr:      0m      0mAh(  0%)      0.0mAh/h          0m      0mAh(  0%)      0.0mAh/h
             Intr:      0m      0mAh(  0%)      0.0mAh/h          0m      0mAh(  0%)      0.0mAh/h
  Deep    NonIntr:      0m      0mAh(  0%)      0.0mAh/h          0m      0mAh(  0%)      0.0mAh/h
             Intr:      0m      0mAh(  0%)      0.0mAh/h          0m      0mAh(  0%)      0.0mAh/h
  Light   NonIntr:      0m      0mAh(  0%)      0.0mAh/h          0m      0mAh(  0%)      0.0mAh/h
             Intr:      0m      0mAh(  0%)      0.0mAh/h          0m      0mAh(  0%)      0.0mAh/h

Battery saver policy (*NOTE* they only apply when battery saver is ON):
  Settings: battery_saver_constants
    value: 
  Settings: (overlay)
    value: 
  DeviceConfig: battery_saver
    N/A
  mAccessibilityEnabled=false
  mAutomotiveProjectionActive=false
  mPolicyLevel=0
  
  Policy 'default full'
    advertise_is_enabled=true
    disable_vibration=true
    disable_animation=false
    defer_full_backup=true
    defer_keyvalue_backup=true
    enable_firewall=true
    enable_datasaver=false
    disable_launch_boost=true
    enable_brightness_adjustment=false
    adjust_brightness_factor=0.5
    location_mode=3
    force_all_apps_standby=true
    force_background_check=true
    disable_optional_sensors=true
    disable_aod=true
    soundtrigger_mode=1
    enable_quick_doze=true
    enable_night_mode=true
  
  Policy 'current full'
    advertise_is_enabled=true
    disable_vibration=true
    disable_animation=false
    defer_full_backup=true
    defer_keyvalue_backup=true
    enable_firewall=true
    enable_datasaver=false
    disable_launch_boost=true
    enable_brightness_adjustment=false
    adjust_brightness_factor=0.5
    location_mode=3
    force_all_apps_standby=true
    force_background_check=true
    disable_optional_sensors=true
    disable_aod=true
    soundtrigger_mode=1
    enable_quick_doze=true
    enable_night_mode=true
  
  Policy 'default adaptive'
    advertise_is_enabled=false
    disable_vibration=false
    disable_animation=false
    defer_full_backup=false
    defer_keyvalue_backup=false
    enable_firewall=false
    enable_datasaver=false
    disable_launch_boost=false
    enable_brightness_adjustment=false
    adjust_brightness_factor=1.0
    location_mode=0
    force_all_apps_standby=false
    force_background_check=false
    disable_optional_sensors=false
    disable_aod=false
    soundtrigger_mode=0
    enable_quick_doze=false
    enable_night_mode=false
  
  Policy 'current adaptive'
    advertise_is_enabled=false
    disable_vibration=false
    disable_animation=false
    defer_full_backup=false
    defer_keyvalue_backup=false
    enable_firewall=false
    enable_datasaver=false
    disable_launch_boost=false
    enable_brightness_adjustment=false
    adjust_brightness_factor=1.0
    location_mode=0
    force_all_apps_standby=false
    force_background_check=false
    disable_optional_sensors=false
    disable_aod=false
    soundtrigger_mode=0
    enable_quick_doze=false
    enable_night_mode=false
  
  Policy 'effective'
    advertise_is_enabled=false
    disable_vibration=false
    disable_animation=false
    defer_full_backup=false
    defer_keyvalue_backup=false
    enable_firewall=false
    enable_datasaver=false
    disable_launch_boost=false
    enable_brightness_adjustment=false
    adjust_brightness_factor=1.0
    location_mode=0
    force_all_apps_standby=false
    force_background_check=false
    disable_optional_sensors=false
    disable_aod=false
    soundtrigger_mode=0
    enable_quick_doze=false
    enable_night_mode=false

Battery saver state machine:
  Enabled=false
    full=false
    adaptive=false
  mState=1
  mLastChangedIntReason=0
  mLastChangedStrReason=null
  mBootCompleted=true
  mSettingsLoaded=true
  mBatteryStatusSet=true
  mIsPowered=false
  mBatteryLevel=100
  mIsBatteryLevelLow=false
  mSettingAutomaticBatterySaver=0
  mSettingBatterySaverEnabled=false
  mSettingBatterySaverEnabledSticky=false
  mSettingBatterySaverStickyAutoDisableEnabled=true
  mSettingBatterySaverStickyAutoDisableThreshold=90
  mSettingBatterySaverTriggerThreshold=0
  mBatterySaverStickyBehaviourDisabled=false
  mDynamicPowerSavingsDefaultDisableThreshold=80
  mDynamicPowerSavingsDisableThreshold=80
  mDynamicPowerSavingsEnableBatterySaver=false
  mLastAdaptiveBatterySaverChangedExternallyElapsed=0
AttentionDetector:
 mIsSettingEnabled=false
 mMaxExtensionMillis=900000
 mPreDimCheckDurationMillis=2000
 mEffectivePostDimTimeout=0
 mLastUserActivityTime(excludingAttention)=12294
 mAttentionServiceSupported=false
 mRequested=false

Profile power states: size=0
Display Group User Activity:
  displayGroupId=0
  userActivitySummary=0x1
  lastUserActivityTime=12294 (24588 ms ago)
  lastUserActivityTimeNoChangeLights=0 (36882 ms ago)
  mWakeLockSummary=0x1

Wireless Charger Detector State:
  mGravitySensor={Sensor name="Gravity Sensor", vendor="AOSP", version=3, type=9, maxRange=19.6133, resolution=2.480159E-4, power=12.7, minDelay=10000}
  mPoweredWirelessly=false
  mAtRest=false
  mRestX=0.0, mRestY=0.0, mRestZ=0.0
  mDetectionInProgress=false
  mDetectionStartTime=0 (never)
  mMustUpdateRestPosition=false
  mTotalSamples=0
  mMovingSamples=0
  mFirstSampleX=0.0, mFirstSampleY=0.0, mFirstSampleZ=0.0
  mLastSampleX=0.0, mLastSampleY=0.0, mLastSampleZ=0.0
Wake Lock Log
  10-28 11:02:24.805 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:24.819 - 1000 - REL NetworkStats
  10-28 11:02:24.820 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:24.835 - 1000 - REL NetworkStats
  10-28 11:02:24.842 - 1000 - ACQ GnssVisibilityControl (partial)
  10-28 11:02:24.864 - 1000 - REL GnssVisibilityControl
  10-28 11:02:24.873 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:24.883 - 1000 - ACQ WiredAccessoryManager (partial)
  10-28 11:02:24.906 - 1000 - REL NetworkStats
  10-28 11:02:24.908 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:24.927 - 1000 - REL NetworkStats
  10-28 11:02:24.934 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:24.961 - 1000 - REL NetworkStats
  10-28 11:02:24.973 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:24.998 - 1000 - REL NetworkStats
  10-28 11:02:24.999 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:25.027 - 1000 - REL NetworkStats
  10-28 11:02:25.027 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:25.051 - 1000 - REL NetworkStats
  10-28 11:02:25.194 - 1000 - REL WiredAccessoryManager
  10-28 11:02:25.329 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:25.363 - 1000 - REL NetworkStats
  10-28 11:02:25.378 - 1001 - ACQ *telephony-radio* (partial)
  10-28 11:02:25.380 - 1001 - REL *telephony-radio*
  10-28 11:02:25.380 - 1001 - ACQ *telephony-radio* (partial)
  10-28 11:02:25.449 - 1001 - ACQ GsmInboundSmsHandler (partial)
  10-28 11:02:25.450 - 1001 - ACQ CdmaInboundSmsHandler (partial)
  10-28 11:02:25.459 - 1073 - ACQ GsmCellBroadcastHandler (partial)
  10-28 11:02:25.465 - 1073 - ACQ CellBroadcastHandler (partial)
  10-28 11:02:25.468 - 1073 - ACQ CdmaServiceCategoryProgramHandler (partial)
  10-28 11:02:25.495 - 1002 - ACQ bluetooth_timer (partial)
  10-28 11:02:25.503 - 1002 - REL bluetooth_timer
  10-28 11:02:25.515 - 1001 - ACQ RILJ_ACK_WL (partial)
  10-28 11:02:25.541 - 10169 - ACQ SysUI:BroadcastSender (partial)
  10-28 11:02:25.542 - 10169 - REL SysUI:BroadcastSender
  10-28 11:02:25.772 - 1001 - REL GsmInboundSmsHandler
  10-28 11:02:25.772 - 1001 - REL CdmaInboundSmsHandler
  10-28 11:02:25.779 - 1001 - ACQ NitzSignalInputFilterPredicateFactory (partial)
  10-28 11:02:25.779 - 1001 - REL NitzSignalInputFilterPredicateFactory
  10-28 11:02:25.781 - 1000 - ACQ time_detector (partial)
  10-28 11:02:25.782 - 1000 - REL time_detector
  10-28 11:02:25.803 - 1000 - ACQ *job*/c.a.s/.s.r.SimSlotChangeService#2131558498 (partial)
  10-28 11:02:25.803 - 1000 - ACQ *job*/c.a.s/.s.r.SimSlotChangeService#2131558498 (partial)
  10-28 11:02:25.804 - 1000 - REL *job*/c.a.s/.s.r.SimSlotChangeService#2131558498
  10-28 11:02:25.821 - 1000 - REL *job*/c.a.s/.s.r.SimSlotChangeService#2131558498
  10-28 11:02:25.925 - 10169 - ACQ AmbientIndication (partial)
  10-28 11:02:26.004 - 10169 - ACQ SysUI:BroadcastSender (partial)
  10-28 11:02:26.005 - 10169 - REL SysUI:BroadcastSender
  10-28 11:02:26.153 - 1001 - REL RILJ_ACK_WL
  10-28 11:02:26.175 - 1001 - ACQ RILJ_ACK_WL (partial)
  10-28 11:02:26.476 - 1001 - ACQ NitzSignalInputFilterPredicateFactory (partial)
  10-28 11:02:26.476 - 1001 - REL NitzSignalInputFilterPredicateFactory
  10-28 11:02:26.616 - 1000 - ACQ *job*/a/c.a.s.n.NotificationHistoryJobService#237039804 (partial)
  10-28 11:02:26.616 - 1000 - ACQ *job*/a/c.a.s.n.NotificationHistoryJobService#237039804 (partial)
  10-28 11:02:26.641 - 1001 - REL RILJ_ACK_WL
  10-28 11:02:26.646 - 1000 - REL *job*/a/c.a.s.n.NotificationHistoryJobService#237039804
  10-28 11:02:26.662 - 1001 - ACQ RILJ_ACK_WL (partial)
  10-28 11:02:26.663 - 1000 - REL *job*/a/c.a.s.n.NotificationHistoryJobService#237039804
  10-28 11:02:26.768 - 1000 - ACQ *launch* (partial)
  10-28 11:02:26.844 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-350 (partial)
  10-28 11:02:26.844 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-350 (partial)
  10-28 11:02:26.854 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-350
  10-28 11:02:26.854 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-462 (partial)
  10-28 11:02:26.855 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-462 (partial)
  10-28 11:02:26.866 - 1000 - ACQ SyncLoopWakeLock (partial)
  10-28 11:02:26.947 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-462
  10-28 11:02:26.947 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362 (partial)
  10-28 11:02:26.947 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362 (partial)
  10-28 11:02:26.947 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362
  10-28 11:02:26.947 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326 (partial)
  10-28 11:02:26.947 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326 (partial)
  10-28 11:02:26.947 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326
  10-28 11:02:26.966 - 1000 - REL SyncLoopWakeLock
  10-28 11:02:27.063 - 1001 - REL RILJ_ACK_WL
  10-28 11:02:27.207 - 10169 - REL AmbientIndication
  10-28 11:02:27.334 - 10155 - ACQ fiid-sync (partial)
  10-28 11:02:27.364 - 1000 - ACQ *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#0 (partial)
  10-28 11:02:27.364 - 1000 - ACQ *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#0 (partial)
  10-28 11:02:27.373 - 10155 - REL fiid-sync
  10-28 11:02:27.408 - 1000 - REL *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#0
  10-28 11:02:27.478 - 1000 - ACQ *job*/c.g.a.a/c.g.a.a.m.a.e.s.EchoJobService#310487677 (partial)
  10-28 11:02:27.478 - 1000 - ACQ *job*/c.g.a.a/c.g.a.a.m.a.e.s.EchoJobService#310487677 (partial)
  10-28 11:02:27.479 - 1000 - REL *job*/c.g.a.a/c.g.a.a.m.a.e.s.EchoJobService#310487677
  10-28 11:02:27.630 - 10121 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:27.637 - 10121 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:27.695 - 1000 - ACQ GnssVisibilityControl (partial)
  10-28 11:02:27.695 - 1000 - REL GnssVisibilityControl
  10-28 11:02:27.709 - 1000 - REL *launch*
  10-28 11:02:27.714 - 10121 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() -> Synclet: SnapshotSynclet -> Use Google Account (partial)
  10-28 11:02:27.715 - 10121 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() -> Synclet: SnapshotSynclet -> Use Google Account (partial)
  10-28 11:02:27.716 - 10121 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() -> Synclet: SnapshotSynclet -> Use Google Account
  10-28 11:02:27.747 - 1000 - REL *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#0
  10-28 11:02:27.748 - 10121 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:27.749 - 1000 - ACQ *job*/c.g.a.a/a.w.i.b.s.SystemJobService#14 (partial)
  10-28 11:02:27.749 - 1000 - ACQ *job*/c.g.a.a/a.w.i.b.s.SystemJobService#14 (partial)
  10-28 11:02:27.782 - 1000 - REL *job*/c.g.a.a/a.w.i.b.s.SystemJobService#14
  10-28 11:02:27.783 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-151 (partial)
  10-28 11:02:27.785 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-151 (partial)
  10-28 11:02:27.785 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-151
  10-28 11:02:27.810 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#9 (partial)
  10-28 11:02:27.810 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#9 (partial)
  10-28 11:02:27.810 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#9
  10-28 11:02:27.811 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#10 (partial)
  10-28 11:02:27.811 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#10 (partial)
  10-28 11:02:27.811 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#10
  10-28 11:02:27.815 - 1041 - ACQ AudioMix (partial)
  10-28 11:02:27.820 - 1041 - ACQ AudioMix (partial)
  10-28 11:02:27.839 - 10128 - ACQ GCoreFlp (partial)
  10-28 11:02:27.979 - 10121 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() -> Synclet: SnapshotSynclet -> Use Google Account
  10-28 11:02:28.055 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:28.056 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:28.089 - 10121 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:28.189 - 10128 - REL GCoreFlp
  10-28 11:02:28.197 - 10128 - ACQ GCoreFlp (partial)
  10-28 11:02:28.202 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362
  10-28 11:02:28.202 - 1000 - ACQ *job*/c.g.a.a/a.w.i.b.s.SystemJobService#18 (partial)
  10-28 11:02:28.202 - 1000 - ACQ *job*/c.g.a.a/a.w.i.b.s.SystemJobService#18 (partial)
  10-28 11:02:28.203 - 1000 - REL *job*/c.g.a.a/a.w.i.b.s.SystemJobService#18
  10-28 11:02:28.231 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:28.231 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:28.277 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-462
  10-28 11:02:28.288 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:28.289 - 1000 - ACQ *job*/c.g.a.a/c.g.a.a.m.a.e.n.s.i.NotificationJobService#738561924 (partial)
  10-28 11:02:28.289 - 1000 - ACQ *job*/c.g.a.a/c.g.a.a.m.a.e.n.s.i.NotificationJobService#738561924 (partial)
  10-28 11:02:28.309 - 1000 - REL *job*/c.g.a.a/c.g.a.a.m.a.e.n.s.i.NotificationJobService#738561924
  10-28 11:02:28.310 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#20 (partial)
  10-28 11:02:28.310 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#20 (partial)
  10-28 11:02:28.320 - 1000 - REL NetworkStats
  10-28 11:02:28.321 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#20
  10-28 11:02:28.322 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362 (partial)
  10-28 11:02:28.322 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362 (partial)
  10-28 11:02:28.327 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362
  10-28 11:02:28.327 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-350
  10-28 11:02:28.327 - 1000 - ACQ *job*/c.g.a.a/c.g.a.a.m.a.c.s.i.PeriodicCleanupService#272538963 (partial)
  10-28 11:02:28.327 - 1000 - ACQ *job*/c.g.a.a/c.g.a.a.m.a.c.s.i.PeriodicCleanupService#272538963 (partial)
  10-28 11:02:28.328 - 1000 - REL *job*/c.g.a.a/c.g.a.a.m.a.c.s.i.PeriodicCleanupService#272538963
  10-28 11:02:28.328 - 1000 - ACQ *job*/c.g.a.p.m.m/c.a.p.m.MediaService#-300 (partial)
  10-28 11:02:28.329 - 1000 - ACQ *job*/c.g.a.p.m.m/c.a.p.m.MediaService#-300 (partial)
  10-28 11:02:28.344 - 1000 - REL *job*/c.g.a.p.m.m/c.a.p.m.MediaService#-300
  10-28 11:02:28.349 - 10132 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:28.389 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:28.394 - 10128 - ACQ CMWakeLock (partial)
  10-28 11:02:28.395 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326
  10-28 11:02:28.400 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-362
  10-28 11:02:28.401 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#9
  10-28 11:02:28.404 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326 (partial)
  10-28 11:02:28.404 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326 (partial)
  10-28 11:02:28.406 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326
  10-28 11:02:28.408 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-326
  10-28 11:02:28.410 - 10132 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:28.429 - 1000 - REL NetworkStats
  10-28 11:02:28.432 - 1000 - ACQ *job*/c.g.a.a.y.m/a.w.i.b.s.SystemJobService#6 (partial)
  10-28 11:02:28.432 - 1000 - ACQ *job*/c.g.a.a.y.m/a.w.i.b.s.SystemJobService#6 (partial)
  10-28 11:02:28.437 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:28.437 - 1000 - REL *job*/c.g.a.a.y.m/a.w.i.b.s.SystemJobService#6
  10-28 11:02:28.451 - 1000 - REL *job*/c.g.a.a.y.m/a.w.i.b.s.SystemJobService#6
  10-28 11:02:28.462 - 1000 - REL NetworkStats
  10-28 11:02:28.465 - 1000 - ACQ NetworkTimeUpdateService (partial)
  10-28 11:02:28.473 - 1073 - REL CdmaServiceCategoryProgramHandler
  10-28 11:02:28.478 - 1073 - REL CellBroadcastHandler
  10-28 11:02:28.478 - 1073 - REL GsmCellBroadcastHandler
  10-28 11:02:28.519 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#20
  10-28 11:02:28.529 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:28.535 - 10132 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:28.538 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#10
  10-28 11:02:28.553 - 10128 - REL GCoreFlp
  10-28 11:02:28.557 - 1000 - REL NetworkStats
  10-28 11:02:28.574 - 10155 - ACQ fiid-sync (partial)
  10-28 11:02:28.574 - 10128 - REL CMWakeLock
  10-28 11:02:28.597 - 10128 - ACQ GCoreFlp (partial)
  10-28 11:02:28.639 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:28.639 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:28.640 - 10132 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:28.644 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:28.645 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:28.713 - 1000 - REL *job*/c.g.a.a/c.g.a.a.m.a.e.n.s.i.NotificationJobService#738561924
  10-28 11:02:28.747 - 1000 - REL *job*/c.g.a.a/a.w.i.b.s.SystemJobService#14
  10-28 11:02:28.752 - 1000 - REL *job*/c.g.a.a/a.w.i.b.s.SystemJobService#18
  10-28 11:02:28.773 - 1000 - REL *job*/c.g.a.a/c.g.a.a.m.a.e.s.EchoJobService#310487677
  10-28 11:02:28.777 - 1000 - REL *job*/c.g.a.a/c.g.a.a.m.a.c.s.i.PeriodicCleanupService#272538963
  10-28 11:02:28.860 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1000 (partial)
  10-28 11:02:28.860 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1000 (partial)
  10-28 11:02:28.867 - 10130 - ACQ SingleRegistrationCapabilityReceiver Receive broadcast -> vendor_ims_call -> WorkQueueImpl#queueWorkItemAndReturnFuture -> WorkQueueImpl#queueWorkItemAndReturnFuture -> executeInTransaction running transactionBlock -> vendor_ims_call (partial)
  10-28 11:02:28.869 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1000
  10-28 11:02:28.907 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1008 (partial)
  10-28 11:02:28.907 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1008 (partial)
  10-28 11:02:28.910 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1008
  10-28 11:02:28.915 - 10130 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:28.932 - 10130 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:28.962 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:28.963 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:28.969 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:28.988 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:29.007 - 10130 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:29.013 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1000
  10-28 11:02:29.046 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:29.049 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:29.061 - 10130 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:29.088 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:29.092 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:29.123 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.124 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.136 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.138 - 10128 - ACQ CMWakeLock (partial)
  10-28 11:02:29.139 - 10128 - ACQ NlpWakeLock (partial)
  10-28 11:02:29.141 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.150 - 1000 - ACQ *job*/c.g.a.a.w/.p.i.PowerStateJobService#3 (partial)
  10-28 11:02:29.150 - 1000 - ACQ *job*/c.g.a.a.w/.p.i.PowerStateJobService#3 (partial)
  10-28 11:02:29.150 - 1000 - REL *job*/c.g.a.a.w/.p.i.PowerStateJobService#3
  10-28 11:02:29.151 - 1000 - ACQ *job*/c.g.a.a.w/.a.i.AutoDndJobService#1 (partial)
  10-28 11:02:29.151 - 1000 - ACQ *job*/c.g.a.a.w/.a.i.AutoDndJobService#1 (partial)
  10-28 11:02:29.155 - 1000 - REL *job*/c.g.a.a.w/.a.i.AutoDndJobService#1
  10-28 11:02:29.159 - 1000 - REL *job*/c.g.a.a.w/.p.i.PowerStateJobService#3
  10-28 11:02:29.160 - 1000 - REL *job*/c.g.a.a.w/.a.i.AutoDndJobService#1
  10-28 11:02:29.184 - 1000 - ACQ *job*/c.g.a.d/a.w.i.b.s.SystemJobService#3 (partial)
  10-28 11:02:29.184 - 1000 - ACQ *job*/c.g.a.d/a.w.i.b.s.SystemJobService#3 (partial)
  10-28 11:02:29.185 - 1000 - REL *job*/c.g.a.d/a.w.i.b.s.SystemJobService#3
  10-28 11:02:29.187 - 10130 - REL SingleRegistrationCapabilityReceiver Receive broadcast -> vendor_ims_call -> WorkQueueImpl#queueWorkItemAndReturnFuture -> WorkQueueImpl#queueWorkItemAndReturnFuture -> executeInTransaction running transactionBlock -> vendor_ims_call
  10-28 11:02:29.193 - 1000 - ACQ *job*/c.g.a.d/a.w.i.b.s.SystemJobService#16 (partial)
  10-28 11:02:29.193 - 1000 - ACQ *job*/c.g.a.d/a.w.i.b.s.SystemJobService#16 (partial)
  10-28 11:02:29.193 - 1000 - REL *job*/c.g.a.d/a.w.i.b.s.SystemJobService#16
  10-28 11:02:29.195 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.196 - 10128 - REL CMWakeLock
  10-28 11:02:29.212 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1008
  10-28 11:02:29.215 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.215 - 10128 - ACQ CMWakeLock (partial)
  10-28 11:02:29.222 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.223 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:29.255 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:29.256 - 10128 - REL CMWakeLock
  10-28 11:02:29.259 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:29.276 - 1000 - REL *job*/c.g.a.d/a.w.i.b.s.SystemJobService#3
  10-28 11:02:29.276 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:29.287 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:29.297 - 1000 - REL *job*/c.g.a.d/a.w.i.b.s.SystemJobService#16
  10-28 11:02:29.316 - 10128 - ACQ CMWakeLock (partial)
  10-28 11:02:29.336 - 1000 - ACQ *job*/c.g.a.d/a.w.i.b.s.SystemJobService#18 (partial)
  10-28 11:02:29.337 - 1000 - ACQ *job*/c.g.a.d/a.w.i.b.s.SystemJobService#18 (partial)
  10-28 11:02:29.341 - 1000 - REL *job*/c.g.a.d/a.w.i.b.s.SystemJobService#18
  10-28 11:02:29.350 - 10128 - ACQ GOOGLE_C2DM (partial)
  10-28 11:02:29.390 - 1000 - REL *job*/c.g.a.d/a.w.i.b.s.SystemJobService#18
  10-28 11:02:29.427 - 10128 - ACQ GCM_CONN_ALARM (partial)
  10-28 11:02:29.428 - 10128 - REL GOOGLE_C2DM
  10-28 11:02:29.430 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:29.431 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:29.432 - 10128 - REL GCM_WORK
  10-28 11:02:29.461 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.476 - 1000 - ACQ GnssVisibilityControl (partial)
  10-28 11:02:29.476 - 1000 - REL GnssVisibilityControl
  10-28 11:02:29.541 - 10130 - ACQ PhoneBootAndPackageReplacedReceiver Receive broadcast -> ReceiverDoInBackground -> refresh_incoming_message_notifications -> WorkQueueImpl#queueWorkItemAndReturnFuture -> WorkQueueImpl#queueWorkItemAndReturnFuture -> executeInTransaction running transactionBlock -> refresh_incoming_message_notifications (partial)
  10-28 11:02:29.542 - 10128 - ACQ Icing (partial)
  10-28 11:02:29.545 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.p.s.s.PhenotypeConfigurator (partial)
  10-28 11:02:29.574 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:29.575 - 10128 - REL GCM_WORK
  10-28 11:02:29.577 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.597 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1013 (partial)
  10-28 11:02:29.597 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1013 (partial)
  10-28 11:02:29.598 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:29.598 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:29.598 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:29.598 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1013
  10-28 11:02:29.599 - 10130 - ACQ bugle_datamodel_executor_wakelock (partial)
  10-28 11:02:29.614 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:29.621 - 10128 - REL GCM_WORK
  10-28 11:02:29.621 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:29.622 - 10128 - REL GCM_WORK
  10-28 11:02:29.631 - 10130 - REL bugle_datamodel_executor_wakelock
  10-28 11:02:29.635 - 10128 - REL GCM_CONN_ALARM
  10-28 11:02:29.650 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:29.653 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:29.658 - 10128 - REL NlpWakeLock
  10-28 11:02:29.664 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.a.a.b.l.AuthCronService (partial)
  10-28 11:02:29.670 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:29.674 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:29.677 - 10130 - REL PhoneBootAndPackageReplacedReceiver Receive broadcast -> ReceiverDoInBackground -> refresh_incoming_message_notifications -> WorkQueueImpl#queueWorkItemAndReturnFuture -> WorkQueueImpl#queueWorkItemAndReturnFuture -> executeInTransaction running transactionBlock -> refresh_incoming_message_notifications
  10-28 11:02:29.677 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1013
  10-28 11:02:29.680 - 10128 - ACQ NlpWakeLock (partial)
  10-28 11:02:29.686 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:29.688 - 10128 - ACQ NlpWakeLock (partial)
  10-28 11:02:29.689 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:29.690 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.732 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.741 - 10128 - REL NlpWakeLock
  10-28 11:02:29.749 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:29.749 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:29.749 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:29.758 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.771 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:29.775 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:29.810 - 10128 - REL *gms_scheduler*/c.g.a.g/.a.a.b.l.AuthCronService
  10-28 11:02:29.813 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:29.814 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:29.814 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:29.852 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:29.878 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:29.927 - 10130 - ACQ PhoneBootAndPackageReplacedReceiver Receive broadcast -> ReceiverDoInBackground -> expire_wap_push_si_message -> WorkQueueImpl#queueWorkItemAndReturnFuture -> WorkQueueImpl#queueWorkItemAndReturnFuture -> executeInTransaction running transactionBlock -> expire_wap_push_si_message (partial)
  10-28 11:02:29.930 - 10130 - ACQ bugle_datamodel_executor_wakelock (partial)
  10-28 11:02:29.936 - 10088 - ACQ CalendarReceiver_Provider (partial)
  10-28 11:02:29.951 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:29.951 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:29.952 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1014 (partial)
  10-28 11:02:29.952 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1014 (partial)
  10-28 11:02:29.959 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1014
  10-28 11:02:29.965 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.p.g.PayGcmTaskService (partial)
  10-28 11:02:29.970 - 10156 - ACQ fiid-sync (partial)
  10-28 11:02:30.024 - 10130 - ACQ fiid-sync (partial)
  10-28 11:02:30.092 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1015 (partial)
  10-28 11:02:30.092 - 1000 - ACQ *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1015 (partial)
  10-28 11:02:30.093 - 10088 - REL CalendarReceiver_Provider
  10-28 11:02:30.119 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:30.123 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1015
  10-28 11:02:30.139 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1014
  10-28 11:02:30.165 - 10128 - REL *gms_scheduler*/c.g.a.g/.p.g.PayGcmTaskService
  10-28 11:02:30.166 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:30.203 - 10130 - REL PhoneBootAndPackageReplacedReceiver Receive broadcast -> ReceiverDoInBackground -> expire_wap_push_si_message -> WorkQueueImpl#queueWorkItemAndReturnFuture -> WorkQueueImpl#queueWorkItemAndReturnFuture -> executeInTransaction running transactionBlock -> expire_wap_push_si_message
  10-28 11:02:30.204 - 1000 - REL *job*/c.g.a.a.m/a.w.i.b.s.SystemJobService#1015
  10-28 11:02:30.216 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:30.250 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:30.330 - 1000 - ACQ *job*/c.g.a.y/a.w.i.b.s.SystemJobService#15 (partial)
  10-28 11:02:30.330 - 1000 - ACQ *job*/c.g.a.y/a.w.i.b.s.SystemJobService#15 (partial)
  10-28 11:02:30.365 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:30.373 - 10128 - REL GCM_WORK
  10-28 11:02:30.379 - 1000 - REL *job*/c.g.a.y/a.w.i.b.s.SystemJobService#15
  10-28 11:02:30.432 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:30.438 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.c.EventLogService (partial)
  10-28 11:02:30.482 - 1000 - REL *job*/c.g.a.y/a.w.i.b.s.SystemJobService#15
  10-28 11:02:30.502 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:30.503 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:30.524 - 10128 - ACQ wake:com.google.android.gms/.auth.account.be.accountstate.LoginAccountsChangedIntentService - 999 (partial)
  10-28 11:02:30.550 - 10128 - REL wake:com.google.android.gms/.auth.account.be.accountstate.LoginAccountsChangedIntentService - 999
  10-28 11:02:30.612 - 10169 - ACQ AmbientIndication (partial)
  10-28 11:02:30.621 - 1000 - ACQ *job*/c.g.a.t/a.w.i.b.s.SystemJobService#0 (partial)
  10-28 11:02:30.621 - 1000 - ACQ *job*/c.g.a.t/a.w.i.b.s.SystemJobService#0 (partial)
  10-28 11:02:30.622 - 1000 - REL *job*/c.g.a.t/a.w.i.b.s.SystemJobService#0
  10-28 11:02:30.654 - 10149 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:30.654 - 10149 - ACQ WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork() (partial)
  10-28 11:02:30.690 - 10149 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:30.692 - 1000 - REL *job*/c.g.a.t/a.w.i.b.s.SystemJobService#0
  10-28 11:02:30.720 - 10149 - REL WorkManager:TikTokListenableWorker startWork -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> com.google.apps.tiktok.sync.impl.workmanager.SyncWorker startWork() -> NoAccountWorkerFactory startWork()
  10-28 11:02:30.723 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:30.790 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:30.791 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:30.791 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:30.798 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:30.816 - 10153 - ACQ ChimeExecutorApi::com.google.android.contacts (partial)
  10-28 11:02:30.816 - 1041 - REL AudioMix
  10-28 11:02:30.819 - 1000 - REL NetworkStats
  10-28 11:02:30.822 - 1041 - REL AudioMix
  10-28 11:02:30.898 - 10153 - REL ChimeExecutorApi::com.google.android.contacts
  10-28 11:02:30.945 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:30.951 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:30.955 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:30.955 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:30.971 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:30.972 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:30.972 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:30.983 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:31.014 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:31.029 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-369 (partial)
  10-28 11:02:31.029 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-369 (partial)
  10-28 11:02:31.030 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-369
  10-28 11:02:31.040 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-369
  10-28 11:02:31.049 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:31.055 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-237 (partial)
  10-28 11:02:31.055 - 1000 - ACQ *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-237 (partial)
  10-28 11:02:31.056 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-237
  10-28 11:02:31.068 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#27 (partial)
  10-28 11:02:31.068 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#27 (partial)
  10-28 11:02:31.069 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#27
  10-28 11:02:31.080 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#27
  10-28 11:02:31.090 - 1000 - REL *job*/c.g.a.g/c.g.a.a.g.t.BackgroundTasksJobService#-237
  10-28 11:02:31.101 - 10128 - REL GCoreFlp
  10-28 11:02:31.105 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:31.109 - 10132 - ACQ ChimeBroadcastReceiver (partial)
  10-28 11:02:31.113 - 10132 - REL ChimeBroadcastReceiver
  10-28 11:02:31.114 - 10128 - REL *gms_scheduler*/c.g.a.g/.c.EventLogService
  10-28 11:02:31.119 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.133 - 1000 - ACQ *job*/c.g.a.g/.j.GoogleMailWidgetAndShortcutSwitchJob$GoogleMailWidgetAndShortcutSwitchJobService#2000018 (partial)
  10-28 11:02:31.133 - 1000 - ACQ *job*/c.g.a.g/.j.GoogleMailWidgetAndShortcutSwitchJob$GoogleMailWidgetAndShortcutSwitchJobService#2000018 (partial)
  10-28 11:02:31.135 - 10145 - ACQ fiid-sync (partial)
  10-28 11:02:31.135 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:31.137 - 1000 - REL *job*/c.g.a.g/.j.GoogleMailWidgetAndShortcutSwitchJob$GoogleMailWidgetAndShortcutSwitchJobService#2000018
  10-28 11:02:31.138 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.140 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.140 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:31.142 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.s.s.SnetNormalTaskService (partial)
  10-28 11:02:31.145 - 10128 - ACQ IntentOp:.c.c.InitConfigOperation (partial)
  10-28 11:02:31.147 - 1000 - REL NetworkStats
  10-28 11:02:31.178 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.181 - 10128 - REL *gms_scheduler*/c.g.a.g/.s.s.SnetNormalTaskService
  10-28 11:02:31.189 - 10169 - REL AmbientIndication
  10-28 11:02:31.193 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.197 - 1000 - ACQ *job*/c.g.a.g/.j.ProviderCreatedJob$ProviderCreatedJobService#2000015 (partial)
  10-28 11:02:31.197 - 1000 - ACQ *job*/c.g.a.g/.j.ProviderCreatedJob$ProviderCreatedJobService#2000015 (partial)
  10-28 11:02:31.198 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.199 - 1000 - REL *job*/c.g.a.g/.j.ProviderCreatedJob$ProviderCreatedJobService#2000015
  10-28 11:02:31.215 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.215 - 1000 - ACQ *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005 (partial)
  10-28 11:02:31.215 - 1000 - ACQ *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005 (partial)
  10-28 11:02:31.218 - 1000 - REL *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005
  10-28 11:02:31.222 - 1000 - REL *job*/c.g.a.g/.j.GoogleMailWidgetAndShortcutSwitchJob$GoogleMailWidgetAndShortcutSwitchJobService#2000018
  10-28 11:02:31.225 - 1000 - REL *job*/c.g.a.g/.j.ProviderCreatedJob$ProviderCreatedJobService#2000015
  10-28 11:02:31.231 - 10130 - REL bugle_datamodel_executor_wakelock
  10-28 11:02:31.236 - 1000 - REL *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005
  10-28 11:02:31.240 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.t.s.f.BorderRouterSyncBoundService (partial)
  10-28 11:02:31.241 - 1000 - ACQ *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005 (partial)
  10-28 11:02:31.241 - 1000 - ACQ *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005 (partial)
  10-28 11:02:31.242 - 1000 - REL *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005
  10-28 11:02:31.246 - 1000 - REL *job*/c.g.a.g/c.a.m.w.NotifyDatasetChangedJob$NotifyDatasetChangedJobService#2000005
  10-28 11:02:31.257 - 1000 - ACQ *job*/c.g.a.g/c.a.e.j.BootCompletedJob$BootCompletedJobService#2000021 (partial)
  10-28 11:02:31.257 - 1000 - ACQ *job*/c.g.a.g/c.a.e.j.BootCompletedJob$BootCompletedJobService#2000021 (partial)
  10-28 11:02:31.258 - 1000 - REL *job*/c.g.a.g/c.a.e.j.BootCompletedJob$BootCompletedJobService#2000021
  10-28 11:02:31.269 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#555000005 (partial)
  10-28 11:02:31.269 - 1000 - ACQ *job*/c.g.a.g/a.w.i.b.s.SystemJobService#555000005 (partial)
  10-28 11:02:31.270 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#555000005
  10-28 11:02:31.278 - 10145 - ACQ ChimeBroadcastReceiver (partial)
  10-28 11:02:31.279 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.291 - 10145 - REL ChimeBroadcastReceiver
  10-28 11:02:31.303 - 1000 - REL *job*/c.g.a.g/a.w.i.b.s.SystemJobService#555000005
  10-28 11:02:31.305 - 1000 - REL *job*/c.g.a.g/c.a.e.j.BootCompletedJob$BootCompletedJobService#2000021
  10-28 11:02:31.336 - 10128 - REL *gms_scheduler*/c.g.a.g/.t.s.f.BorderRouterSyncBoundService
  10-28 11:02:31.337 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.345 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.353 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.365 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.a.a.b.a.GcmTaskService (partial)
  10-28 11:02:31.376 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:31.376 - 1000 - ACQ NetworkStats (partial)
  10-28 11:02:31.377 - 1000 - ACQ *job*/c.g.a.p/.PhenotypeJobService#1 (partial)
  10-28 11:02:31.377 - 1000 - ACQ *job*/c.g.a.p/.PhenotypeJobService#1 (partial)
  10-28 11:02:31.383 - 1000 - REL *job*/c.g.a.p/.PhenotypeJobService#1
  10-28 11:02:31.386 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.391 - 1000 - REL NetworkStats
  10-28 11:02:31.391 - 1000 - REL *alarm*
  10-28 11:02:31.437 - 10128 - REL *gms_scheduler*/c.g.a.g/.a.a.b.a.GcmTaskService
  10-28 11:02:31.438 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.444 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.445 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:31.451 - 10128 - ACQ *gms_scheduler*/c.g.a.g/.c.c.ConfigService (partial)
  10-28 11:02:31.460 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:31.867 - 1000 - REL *job*/c.g.a.p.m.m/c.a.p.m.MediaService#-300
  10-28 11:02:32.373 - 10128 - REL Icing
  10-28 11:02:32.838 - 10128 - ACQ IntentOp:.a.f.FrpUpdateIntentOperation (partial)
  10-28 11:02:32.842 - 10128 - REL IntentOp:.a.f.FrpUpdateIntentOperation
  10-28 11:02:32.894 - 10128 - ACQ IntentOp:.u.e.InstallationIntentOperation (partial)
  10-28 11:02:32.896 - 10128 - REL IntentOp:.u.e.InstallationIntentOperation
  10-28 11:02:32.961 - 10128 - ACQ wake:com.google.android.gms/.chimera.GmsIntentOperationService - 913 (partial)
  10-28 11:02:32.967 - 10128 - ACQ Checkin Service (partial)
  10-28 11:02:32.971 - 10128 - ACQ GmsDownloadIntentOp (partial)
  10-28 11:02:32.981 - 10128 - REL GmsDownloadIntentOp
  10-28 11:02:33.025 - 10128 - ACQ Icing (partial)
  10-28 11:02:33.028 - 10128 - REL Icing
  10-28 11:02:33.085 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.092 - 10128 - ACQ Wakeful StateMachine: GeofencerStateMachine (partial)
  10-28 11:02:33.093 - 10128 - REL Wakeful StateMachine: GeofencerStateMachine
  10-28 11:02:33.097 - 10128 - ACQ wake:CollectionChimeraSvc (partial)
  10-28 11:02:33.101 - 10128 - REL wake:CollectionChimeraSvc
  10-28 11:02:33.102 - 10128 - ACQ IntentOp:.c.c.InitConfigOperation (partial)
  10-28 11:02:33.107 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.113 - 10128 - ACQ messaging_service_start_wakelock (partial)
  10-28 11:02:33.115 - 10128 - ACQ messaging_service_work_wakelock (partial)
  10-28 11:02:33.115 - 10128 - REL messaging_service_start_wakelock
  10-28 11:02:33.116 - 10128 - REL messaging_service_work_wakelock
  10-28 11:02:33.167 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:33.168 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:33.238 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.241 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.244 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.250 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.251 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.261 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.262 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.264 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.265 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.270 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.270 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.272 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.286 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.288 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.313 - 10128 - ACQ IntentOp:.c.c.InitConfigOperation (partial)
  10-28 11:02:33.322 - 10128 - ACQ IntentOp:.r.n.RefreshNotificationsIntentOperation (partial)
  10-28 11:02:33.326 - 10128 - ACQ IntentOp:.r.n.ScheduleTimeRemindersIntentOperation (partial)
  10-28 11:02:33.326 - 10128 - REL IntentOp:.r.n.RefreshNotificationsIntentOperation
  10-28 11:02:33.331 - 10128 - REL IntentOp:.r.n.ScheduleTimeRemindersIntentOperation
  10-28 11:02:33.354 - 10128 - ACQ IntentOp:.c.c.InitConfigOperation (partial)
  10-28 11:02:33.391 - 10128 - ACQ wake:CollectionChimeraSvc (partial)
  10-28 11:02:33.394 - 10128 - REL wake:CollectionChimeraSvc
  10-28 11:02:33.399 - 10128 - REL CMWakeLock
  10-28 11:02:33.413 - 1000 - ACQ *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#18 (partial)
  10-28 11:02:33.413 - 1000 - ACQ *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#18 (partial)
  10-28 11:02:33.414 - 1000 - REL *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#18
  10-28 11:02:33.418 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:33.420 - 10128 - ACQ CMWakeLock (partial)
  10-28 11:02:33.421 - 10128 - REL CMWakeLock
  10-28 11:02:33.421 - 1000 - ACQ *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#19 (partial)
  10-28 11:02:33.421 - 1000 - ACQ *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#19 (partial)
  10-28 11:02:33.421 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:33.422 - 1000 - REL *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#19
  10-28 11:02:33.430 - 1000 - REL *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#18
  10-28 11:02:33.432 - 10128 - ACQ CMWakeLock (partial)
  10-28 11:02:33.433 - 10128 - REL CMWakeLock
  10-28 11:02:33.436 - 1000 - REL *job*/c.g.a.a.w/a.w.i.b.s.SystemJobService#19
  10-28 11:02:34.687 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:34.688 - 10128 - ACQ NlpWakeLock (partial)
  10-28 11:02:34.688 - 1000 - REL *alarm*
  10-28 11:02:34.689 - 10128 - ACQ GCoreFlp (partial)
  10-28 11:02:34.690 - 10128 - REL NlpWakeLock
  10-28 11:02:34.690 - 10128 - REL NlpWakeLock
  10-28 11:02:34.719 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:34.723 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:34.964 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:34.968 - 1000 - ACQ *job*/c.a.p.c/.CalendarProviderJobService#82808775 (partial)
  10-28 11:02:34.968 - 1000 - ACQ *job*/c.a.p.c/.CalendarProviderJobService#82808775 (partial)
  10-28 11:02:34.971 - 1000 - REL *job*/c.a.p.c/.CalendarProviderJobService#82808775
  10-28 11:02:34.972 - 1000 - REL *alarm*
  10-28 11:02:34.977 - 1000 - REL *job*/c.a.p.c/.CalendarProviderJobService#82808775
  10-28 11:02:34.984 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:34.984 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:34.984 - 10128 - ACQ UlrDispSvcFastWL (partial)
  10-28 11:02:34.996 - 10128 - REL UlrDispSvcFastWL
  10-28 11:02:35.281 - 1000 - ACQ *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100006 (partial)
  10-28 11:02:35.282 - 1000 - ACQ *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100006 (partial)
  10-28 11:02:35.288 - 1000 - REL *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100006
  10-28 11:02:35.299 - 1000 - REL *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100006
  10-28 11:02:36.574 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:36.578 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:36.579 - 10128 - REL GCM_WORK
  10-28 11:02:36.580 - 1000 - REL *alarm*
  10-28 11:02:36.581 - 10128 - ACQ GCM_CONN_ALARM (partial)
  10-28 11:02:36.584 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:36.585 - 10128 - REL GCM_WORK
  10-28 11:02:36.590 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:36.591 - 10128 - REL GCM_WORK
  10-28 11:02:36.592 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:36.593 - 10128 - REL GCM_WORK
  10-28 11:02:36.594 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:36.594 - 10128 - REL GCM_WORK
  10-28 11:02:36.598 - 10128 - REL GCM_CONN_ALARM
  10-28 11:02:36.696 - 10128 - REL GCoreFlp
  10-28 11:02:36.851 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:36.859 - 1000 - REL *alarm*
  10-28 11:02:38.421 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:38.425 - 1000 - REL *alarm*
  10-28 11:02:38.425 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:38.431 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:38.509 - 1000 - ACQ *job*/c.g.a.a.m/.s.d.a.e.ActionJobService#124 (partial)
  10-28 11:02:38.510 - 1000 - ACQ *job*/c.g.a.a.m/.s.d.a.e.ActionJobService#124 (partial)
  10-28 11:02:38.531 - 1000 - REL *job*/c.g.a.a.m/.s.d.a.e.ActionJobService#124
  10-28 11:02:38.539 - 10130 - ACQ bugle_datamodel_executor_wakelock (partial)
  10-28 11:02:38.584 - 1000 - REL *job*/c.g.a.a.m/.s.d.a.e.ActionJobService#124
  10-28 11:02:38.585 - 10130 - REL bugle_datamodel_executor_wakelock
  10-28 11:02:38.996 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:38.997 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:38.999 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:39.003 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:39.004 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:39.006 - 10128 - ACQ IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation (partial)
  10-28 11:02:39.007 - 10128 - ACQ Icing (partial)
  10-28 11:02:39.009 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:39.011 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:39.013 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:39.019 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:39.029 - 10128 - REL Icing
  10-28 11:02:39.033 - 10128 - ACQ Icing (partial)
  10-28 11:02:39.044 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:39.046 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:39.046 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:39.048 - 10128 - REL IntentOp:.c.b.BackgroundBroadcastReceiverSupport$PersistentReceiverIntentOperation
  10-28 11:02:39.061 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:39.061 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:39.071 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:39.071 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:39.083 - 10128 - ACQ nearby:ENWearableDeviceManager (partial)
  10-28 11:02:39.084 - 10128 - REL nearby:ENWearableDeviceManager
  10-28 11:02:40.072 - 10128 - REL Icing
  10-28 11:02:43.313 - 10128 - ACQ *gms_scheduler*:internal (partial)
  10-28 11:02:43.321 - 10128 - REL *gms_scheduler*:internal
  10-28 11:02:44.300 - 1000 - ACQ *job*/c.g.a.c/c.g.a.a.c.s.ShortcutJobService#7 (partial)
  10-28 11:02:44.301 - 1000 - ACQ *job*/c.g.a.c/c.g.a.a.c.s.ShortcutJobService#7 (partial)
  10-28 11:02:44.304 - 1000 - REL *job*/c.g.a.c/c.g.a.a.c.s.ShortcutJobService#7
  10-28 11:02:44.319 - 1000 - REL *job*/c.g.a.c/c.g.a.a.c.s.ShortcutJobService#7
  10-28 11:02:45.310 - 1000 - ACQ *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100007 (partial)
  10-28 11:02:45.310 - 1000 - ACQ *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100007 (partial)
  10-28 11:02:45.312 - 1000 - REL *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100007
  10-28 11:02:45.324 - 1000 - REL *job*/c.g.a.c/a.w.i.b.s.SystemJobService#100007
  10-28 11:02:48.594 - 1000 - REL NetworkTimeUpdateService
  10-28 11:02:49.719 - 10130 - ACQ bugle_datamodel_executor_wakelock (partial)
  10-28 11:02:49.729 - 10130 - REL bugle_datamodel_executor_wakelock
  10-28 11:02:49.746 - 10130 - ACQ bugle_datamodel_executor_wakelock (partial)
  10-28 11:02:49.748 - 10130 - REL bugle_datamodel_executor_wakelock
  10-28 11:02:50.808 - 1000 - ACQ *alarm* (partial)
  10-28 11:02:50.812 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:50.813 - 10128 - REL GCM_WORK
  10-28 11:02:50.814 - 1000 - REL *alarm*
  10-28 11:02:50.817 - 10128 - ACQ GCM_CONN_ALARM (partial)
  10-28 11:02:50.818 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:50.819 - 10128 - REL GCM_WORK
  10-28 11:02:50.819 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:50.820 - 10128 - REL GCM_WORK
  10-28 11:02:50.822 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:50.823 - 10128 - REL GCM_WORK
  10-28 11:02:50.824 - 10128 - ACQ GCM_WORK (partial)
  10-28 11:02:50.825 - 10128 - REL GCM_WORK
  10-28 11:02:50.828 - 10128 - REL GCM_CONN_ALARM
  -
  Events: 603, Time-Resets: 16
  Buffer, Bytes used: 1659
FaceDownDetector:
  mFaceDown=false
  mActive=true
  mLastFlipTime=0
  mSensorMaxLatencyMicros=2000000
  mUserInteractionBackoffMillis=60000
  mPreviousResultTime=0
  mPreviousResultType=1
  mMillisSaved=0
  mZAccelerationThreshold=-9.5
  mAccelerationThreshold=0.2
  mTimeThreshold=PT1S
AmbientDisplaySuppressionController:
 ambientDisplaySuppressed=false
 mSuppressionTokens={}

Low Power Standby Controller:
  mIsActive=false
  mIsEnabled=false
  mSupportedConfig=false
  mEnabledByDefaultConfig=false
  mStandbyTimeoutConfig=0
  mEnableCustomPolicy=false
  Allowed UIDs=[]
  
  UID allowed reasons:
```
