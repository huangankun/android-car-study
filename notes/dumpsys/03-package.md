# dumpsys 存档：03-package.md（讲解版）

命令：`adb shell dumpsys package com.android.settings`

**这个服务是什么**：PackageManagerService（PMS）针对**单个包**的完整档案，回答「这个包注册了哪些组件（Activity/Receiver/Service/Provider）、有哪些权限、版本和安装信息」。

**这段输出在讲什么**：Settings 这个系统应用的全家桶——它能响应哪些 Intent、声明了哪些权限、对外提供了哪些 ContentProvider。2808 行里绝大多数是组件清单，真正要会看的是下面几段。

## 逐段讲解

### 1. Activity Resolver Table：Intent 匹配的数据来源

```text
Activity Resolver Table:
  Full MIME Types:
      vnd.android.cursor.item/telephony-carrier:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f93a7dc
          Action: "android.intent.action.EDIT"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.item/telephony-carrier"
```

**讲解**：这张表是系统做 **Intent 解析（resolve）** 的原料。含义：当有人发一个 `ACTION_EDIT` 且 MIME 类型是 `vnd.android.cursor.item/telephony-carrier` 的 Intent 时，系统会匹配到 `Settings$ApnEditorActivity`（APN 编辑器）。**面试问「`startActivity` 后系统怎么找到目标 Activity」，答案就是 PMS 维护的这套 Resolver Table 做 Intent filter 匹配。**

### 2. 四张 Resolver Table（结构相同，对象不同）

文件里依次是：
- `Activity Resolver Table`（第 8 行起）
- `Receiver Resolver Table`（第 1788 行起）—— 广播接收者匹配
- `Service Resolver Table`（第 1957 行起）—— 服务匹配
- `Provider Resolver Table`（第 1979 行起）—— ContentProvider 匹配

四张表同一套格式，看懂第一张就够了。

### 3. Permissions 段：这个包声明的权限

**讲解**：Settings 声明了它自己定义/使用的权限（如各种 `android.permission.WRITE_SETTINGS` 之类）。注意区分两个概念：**「声明权限」是 manifest 里 `<permission>` 定义一个新权限，「请求权限」是 `<uses-permission>` 去用别人的权限。** 这里列的是前者。

### 4. ContentProvider：对外暴露的数据接口

```text
Registered ContentProviders:
  ...
ContentProvider Authorities:
  ...
```

**讲解**：`authority` 是 ContentProvider 的唯一名字（形如 `com.android.settings.xxx`），App 通过 `content://authority/...` 这个 URI 访问数据。Settings 把一些系统设置项包装成 Provider 对外暴露。

### 5. Packages 段：真正的包元信息（第 2126 行起，最常用）

这一段才是 `dumpsys package` 的精华，包含：
```text
    versionCode=34 minSdk=34 targetSdk=34
    versionName=14
```
- 版本号、SDK 适配（targetSdk=34 = 面向 Android 14 编译）
- 四大组件的完整清单（activities/services/receivers/providers）
- 请求的权限（`requested permissions`，Settings 共引用了 464 处 `android.permission`）
- 签名信息（signatures）

**一句话结论**：`dumpsys package <包名>` 是「查一个 App 的户口本」。查「这个 App 有哪些组件/权限/签名、targetSdk 是多少」都用它。**对比记忆**：`dumpsys package`（不带包名）会 dump 所有包，量巨大；带包名才是精准查询的正确姿势。

## 完整原始输出


```text
Activity Resolver Table:
  Full MIME Types:
      vnd.android.cursor.item/telephony-carrier:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f93a7dc
          Action: "android.intent.action.EDIT"
          Action: "android.intent.action.VIEW"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.item/telephony-carrier"
      vnd.android.document/root:
        2de8b29 com.android.settings/.Settings$PublicVolumeSettingsActivity filter 1ddeeae
          Action: "android.provider.action.DOCUMENT_ROOT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "content"
          Authority: "com.android.externalstorage.documents": -1
          StaticType: "vnd.android.document/root"
      vnd.android.cursor.dir/telephony-carrier:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f2bb0e5
          Action: "android.intent.action.INSERT"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.dir/telephony-carrier"

  Base MIME Types:
      vnd.android.document:
        2de8b29 com.android.settings/.Settings$PublicVolumeSettingsActivity filter 1ddeeae
          Action: "android.provider.action.DOCUMENT_ROOT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "content"
          Authority: "com.android.externalstorage.documents": -1
          StaticType: "vnd.android.document/root"
      vnd.android.cursor.dir:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f2bb0e5
          Action: "android.intent.action.INSERT"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.dir/telephony-carrier"
      vnd.android.cursor.item:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f93a7dc
          Action: "android.intent.action.EDIT"
          Action: "android.intent.action.VIEW"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.item/telephony-carrier"

  Schemes:
      printjob:
        e921412 com.android.settings/.Settings$PrintJobSettingsActivity filter e3c37e3
          Action: "android.settings.ACTION_PRINT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "printjob"
          Path: "PatternMatcher{GLOB: *}"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      package:
        d371ec5 com.android.settings/.Settings$LongBackgroundTasksAppActivity filter d36501a
          Action: "android.settings.MANAGE_APP_LONG_RUNNING_JOBS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        17617d com.android.settings/.localepicker.AppLocalePickerActivity filter d56c872
          Action: "android.settings.APP_LOCALE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        2da165c com.android.settings/.datausage.AppDataUsageActivity filter d3bd65
          Action: "android.settings.IGNORE_BACKGROUND_DATA_RESTRICTIONS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        efa9a3a com.android.settings/.fuelgauge.RequestIgnoreBatteryOptimizations filter e8d86eb
          Action: "android.settings.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        e82006 com.android.settings/.applications.InstalledAppDetails filter 73ba6c7
          Action: "android.intent.action.AUTO_REVOKE_PERMISSIONS"
          Action: "android.settings.APPLICATION_DETAILS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        620d4f4 com.android.settings/.applications.InstalledAppOpenByDefaultActivity filter 595341d
          Action: "android.settings.APP_OPEN_BY_DEFAULT_SETTINGS"
          Action: "com.android.settings.APP_OPEN_BY_DEFAULT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        c4113f0 com.android.settings/.Settings$AppUsageAccessSettingsActivity filter 768cd69
          Action: "android.settings.USAGE_ACCESS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        4812715 com.android.settings/.Settings$AppPictureInPictureSettingsActivity filter 4243a2a
          Action: "android.settings.PICTURE_IN_PICTURE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        ea3cef6 com.android.settings/.Settings$AppTurnScreenOnSettingsActivity filter d1242f7
          Action: "android.settings.TURN_SCREEN_ON_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        b5e482 com.android.settings/.Settings$AppInteractAcrossProfilesSettingsActivity filter 79e1793
          Action: "android.settings.MANAGE_CROSS_PROFILE_ACCESS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        83103d0 com.android.settings/.Settings$ZenAccessDetailSettingsActivity filter ee82fc9
          Action: "android.settings.NOTIFICATION_POLICY_ACCESS_DETAIL_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        da3d7e7 com.android.settings/.Settings$PremiumSmsAccessActivity filter e357f94
          Action: "android.settings.PREMIUM_SMS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        acd2b06 com.android.settings/.Settings$OverlaySettingsActivity filter 3b057f4
          Action: "android.settings.action.MANAGE_OVERLAY_PERMISSION"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        799fb1d com.android.settings/.Settings$AppDrawOverlaySettingsActivity filter c80f192
          Action: "android.settings.MANAGE_APP_OVERLAY_PERMISSION"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        3e02c19 com.android.settings/.Settings$AppWriteSettingsActivity filter 83894de
          Action: "android.settings.action.MANAGE_WRITE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        4be70d5 com.android.settings/.Settings$AlarmsAndRemindersAppActivity filter 53520ea
          Action: "android.settings.REQUEST_SCHEDULE_EXACT_ALARM"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        c024551 com.android.settings/.Settings$ManageAppExternalSourcesActivity filter bbc61b6
          Action: "android.settings.MANAGE_UNKNOWN_APP_SOURCES"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        9b74d89 com.android.settings/.Settings$AppManageExternalStorageActivity filter da1f18e
          Action: "android.settings.MANAGE_APP_ALL_FILES_ACCESS_PERMISSION"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        a3e3945 com.android.settings/.Settings$AppMediaManagementAppsActivity filter 24f989a
          Action: "android.settings.REQUEST_MANAGE_MEDIA"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        bee054 com.android.settings/.fuelgauge.AdvancedPowerUsageDetailActivity filter e974bfd
          Action: "android.settings.VIEW_ADVANCED_POWER_USAGE_DETAIL"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        240a0f2 com.android.settings/.Settings$AccountDashboardActivity filter e53adc0
          Action: "android.settings.CREDENTIAL_PROVIDER"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        28f5c4a com.android.settings/.applications.autofill.AutofillPickerTrampolineActivity filter 6507bb
          Action: "android.settings.REQUEST_SET_AUTOFILL_SERVICE"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        cd6fa81 com.android.settings/.AppManageFullScreenIntent filter 8a22726
          Action: "android.settings.MANAGE_APP_USE_FULL_SCREEN_INTENT"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
        25c6f67 com.android.settings/com.google.android.settings.AppDebuggingDataActivity filter bf70114
          Action: "android.settings.MANAGE_APP_DEBUGGING_DATA_PERMISSION"
          Category: "android.intent.category.DEFAULT"
          Scheme: "package"
      DPP:
        27fa187 com.android.settings/.wifi.dpp.WifiDppConfiguratorActivity filter 6ce8cdd
          Action: "android.settings.PROCESS_WIFI_EASY_CONNECT_URI"
          Category: "android.intent.category.DEFAULT"
          Scheme: "DPP"
      content:
        2de8b29 com.android.settings/.Settings$PublicVolumeSettingsActivity filter 1ddeeae
          Action: "android.provider.action.DOCUMENT_ROOT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "content"
          Authority: "com.android.externalstorage.documents": -1
          StaticType: "vnd.android.document/root"
      settings:
        6203c48 com.android.settings/.slices.SliceDeepLinkSpringBoard filter 5c7cae1
          Action: "android.intent.action.VIEW"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.BROWSABLE"
          Scheme: "settings"
          Authority: "com.android.settings.slices": -1

  Non-Data Actions:
      android.settings.FINGERPRINT_SETUP:
        d5d09fe com.android.settings/.biometrics.fingerprint.SetupFingerprintEnrollIntroduction filter 21cd55f
          Action: "android.settings.FINGERPRINT_SETUP"
          Category: "android.intent.category.DEFAULT"
      android.net.wifi.PICK_WIFI_NETWORK:
        7ca98ac com.android.settings/.wifi.WifiPickerActivity filter ccf9975
          Action: "android.net.wifi.PICK_WIFI_NETWORK"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.SHOW_REGULATORY_INFO:
        681f5c4 com.android.settings/.RegulatoryInfoDisplayActivity filter 7cf8cad
          Action: "android.settings.SHOW_REGULATORY_INFO"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
      android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION:
        a7f0f53 com.android.settings/.Settings$ManageExternalStorageActivity filter bf70090
          Action: "android.settings.MANAGE_ALL_FILES_ACCESS_PERMISSION"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.NAVIGATION_MODE_SETTINGS:
        9f64335 com.android.settings/.Settings$NavigationModeSettingsActivity filter 652f3ca
          Action: "com.android.settings.NAVIGATION_MODE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.action.SUPPORT_SETTINGS:
        fa5e5ec com.android.settings/.support.SupportDashboardActivity filter 638fdb5
          Action: "com.android.settings.action.SUPPORT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.SHOW_MANUAL:
        3160056 com.android.settings/.ManualDisplayActivity filter cfc88d7
          Action: "android.settings.SHOW_MANUAL"
          Category: "android.intent.category.DEFAULT"
      android.settings.NETWORK_OPERATOR_SETTINGS:
        a490913 com.android.settings/.Settings$MobileNetworkActivity filter 98ed750
          Action: "android.settings.NETWORK_OPERATOR_SETTINGS"
          Action: "android.telephony.ims.action.SHOW_CAPABILITY_DISCOVERY_OPT_IN"
          Action: "android.intent.action.MAIN"
          Action: "android.settings.MMS_MESSAGE_SETTING"
          Action: "android.settings.DATA_ROAMING_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.action.SETTINGS:
        b9e47ba com.android.settings/.Settings$DevelopmentSettingsDashboardActivity filter 6a165c8
          Action: "com.android.settings.action.SETTINGS"
          Action: "com.android.intent.action.SHOW_CONTRAST_DIALOG"
        5f8f96e com.android.settings/.Settings$UserSettingsActivity filter a2909c
          Action: "com.android.settings.action.SETTINGS"
      android.net.wifi.action.REQUEST_ENABLE:
        b09cbe2 com.android.settings/.wifi.RequestToggleWiFiActivity filter 216db73
          Action: "android.net.wifi.action.REQUEST_ENABLE"
          Action: "android.net.wifi.action.REQUEST_DISABLE"
          Category: "android.intent.category.DEFAULT"
      android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS:
        972c846 com.android.settings/.Settings$NotificationAccessSettingsActivity filter b08ca07
          Action: "android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.USER_SETTINGS:
        5f8f96e com.android.settings/.Settings$UserSettingsActivity filter 15e80f
          Action: "android.settings.USER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.USER_DICTIONARY_INSERT:
        a679521 com.android.settings/.inputmethod.UserDictionaryAddWordActivity filter 610bd46
          Action: "com.android.settings.USER_DICTIONARY_INSERT"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.STYLUS_USI_DETAILS_SETTINGS:
        b294eee com.android.settings/.Settings$StylusUsiDetailsActivity filter b74f8f
          Action: "com.android.settings.STYLUS_USI_DETAILS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.SHOW_RESTRICTED_SETTING_DIALOG:
        d4e58d com.android.settings/.ActionDisabledByAppOpsDialog filter a4e342
          Action: "android.settings.SHOW_RESTRICTED_SETTING_DIALOG"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DISPLAY_SETTINGS:
        f389bce com.android.settings/.Settings$DisplaySettingsActivity filter 9e74aef
          Action: "android.settings.DISPLAY_SETTINGS"
          Action: "com.android.settings.DISPLAY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DATA_SAVER_SETTINGS:
        3a4db09 com.android.settings/.Settings$DataSaverSummaryActivity filter 9e4310e
          Action: "android.settings.DATA_SAVER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.security.SECURITY_ADVANCED_SETTINGS:
        39f8ee com.android.settings/com.google.android.settings.security.SecurityAdvancedSettingsActivity filter 89bb18f
          Action: "com.google.android.settings.security.SECURITY_ADVANCED_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.BLUETOOTH_DEVICE_DETAIL_SETTINGS:
        5850684 com.android.settings/.Settings$BluetoothDeviceDetailActivity filter fb82e6d
          Action: "com.android.settings.BLUETOOTH_DEVICE_DETAIL_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.warranty.SUW_DIGITAL_WARRANTY:
        be437c6 com.android.settings/com.google.android.settings.warranty.SuwWarrantyActivity filter 24e4387
          Action: "com.google.android.settings.warranty.SUW_DIGITAL_WARRANTY"
          Category: "android.intent.category.DEFAULT"
      android.settings.LOCATION_SOURCE_SETTINGS:
        cfe96b6 com.android.settings/.Settings$LocationSettingsActivity filter 115cfb7
          Action: "android.settings.LOCATION_SOURCE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.BLUETOOTH_SETTINGS:
        131236f com.android.settings/.Settings$ConnectedDeviceDashboardActivity filter 192187c
          Action: "android.settings.BLUETOOTH_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.telephony.ims.action.SHOW_CAPABILITY_DISCOVERY_OPT_IN:
        a490913 com.android.settings/.Settings$MobileNetworkActivity filter 98ed750
          Action: "android.settings.NETWORK_OPERATOR_SETTINGS"
          Action: "android.telephony.ims.action.SHOW_CAPABILITY_DISCOVERY_OPT_IN"
          Action: "android.intent.action.MAIN"
          Action: "android.settings.MMS_MESSAGE_SETTING"
          Action: "android.settings.DATA_ROAMING_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.credentials.INSTALL:
        bdb82ec com.android.settings/.security.CredentialStorage filter ce2d6b5
          Action: "com.android.credentials.INSTALL"
          Action: "com.android.credentials.RESET"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.APPLICATION_DEVELOPMENT_SETTINGS:
        b9e47ba com.android.settings/.Settings$DevelopmentSettingsDashboardActivity filter 1b666b
          Action: "android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Action: "android.service.quicksettings.action.QS_TILE_PREFERENCES"
          Action: "com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        6b7661 com.android.settings/.development.DevelopmentSettingsDisabledActivity filter bd92586
          Action: "android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Action: "com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=-1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MEDIA_BROADCAST_DIALOG:
        4df2aa2 com.android.settings/.Settings$BluetoothBroadcastActivity filter d4eb333
          Action: "android.settings.MEDIA_BROADCAST_DIALOG"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.SETTINGS:
        e1f044c com.android.settings/.homepage.SettingsHomepageActivity filter 54c2c95
          Action: "android.settings.SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.SETUP_LOCK_SCREEN:
        17bc80a com.android.settings/.password.SetupChooseLockGeneric filter a63687b
          Action: "com.android.settings.SETUP_LOCK_SCREEN"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.HARD_KEYBOARD_SETTINGS:
        71de4b3 com.android.settings/.Settings$PhysicalKeyboardActivity filter 8db1a70
          Action: "android.settings.HARD_KEYBOARD_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.VR_LISTENER_SETTINGS:
        2fbb2a0 com.android.settings/.Settings$VrListenersSettingsActivity filter d57fe59
          Action: "android.settings.VR_LISTENER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.development.START_DSU_LOADER:
        53d25e0 com.android.settings/.development.DSULoader filter 7d39099
          Action: "android.settings.development.START_DSU_LOADER"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.sim.SIM_SUB_INFO_SETTINGS:
        d7790e4 com.android.settings/.Settings$NetworkDashboardActivity filter e66594d
          Action: "com.android.settings.sim.SIM_SUB_INFO_SETTINGS"
          Action: "android.settings.WIRELESS_SETTINGS"
          Action: "android.settings.AIRPLANE_MODE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ADD_ACCOUNT_SETTINGS:
        c4e6a35 com.android.settings/.accounts.AddAccountSettings filter bbd8eca
          Action: "android.settings.ADD_ACCOUNT_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.action.CONFIRM_FACE_ENROLLMENT:
        588afb5 com.android.settings/com.google.android.settings.biometrics.face.FaceEnrollConfirmation filter bba264a
          Action: "com.google.android.settings.action.CONFIRM_FACE_ENROLLMENT"
          Category: "android.intent.category.DEFAULT"
      android.settings.COLOR_INVERSION_SETTINGS:
        a91809b com.android.settings/.Settings$AccessibilityInversionSettingsActivity filter 8052c38
          Action: "android.settings.COLOR_INVERSION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MANAGED_PROFILE_SETTINGS:
        8d6791f com.android.settings/.Settings$ManagedProfileSettingsActivity filter 933346c
          Action: "android.settings.MANAGED_PROFILE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.USAGE_ACCESS_SETTINGS:
        9362fa2 com.android.settings/.Settings$UsageAccessSettingsActivity filter 7e1d433
          Action: "android.settings.USAGE_ACCESS_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.device.action.CONNECTION_ACCESS_CANCEL:
        c83a5c2 com.android.settings/.bluetooth.BluetoothPermissionActivity filter 69adfd3
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_CANCEL"
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_REQUEST"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.TRUSTED_CREDENTIALS_USER:
        70414a7 com.android.settings/.Settings$TrustedCredentialsSettingsActivity filter b31dd54
          Action: "com.android.settings.TRUSTED_CREDENTIALS_USER"
          Action: "com.android.settings.TRUSTED_CREDENTIALS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.BIOMETRIC_ENROLL:
        ca254b2 com.android.settings/.biometrics.BiometricEnrollActivity filter a987c03
          Action: "android.settings.BIOMETRIC_ENROLL"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
      android.app.action.CONFIRM_FRP_CREDENTIAL:
        ffbb14e com.android.settings/.password.ConfirmDeviceCredentialActivity filter e84726f
          Action: "android.app.action.CONFIRM_FRP_CREDENTIAL"
          Action: "android.app.action.CONFIRM_DEVICE_CREDENTIAL"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.ADD_DEVICE_ADMIN:
        aefa816 com.android.settings/.applications.specialaccess.deviceadmin.DeviceAdminAdd filter 4457597
          Action: "android.app.action.ADD_DEVICE_ADMIN"
          Category: "android.intent.category.DEFAULT"
          mPriority=1000, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.device.action.CONNECTION_ACCESS_REQUEST:
        c83a5c2 com.android.settings/.bluetooth.BluetoothPermissionActivity filter 69adfd3
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_CANCEL"
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_REQUEST"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.action.RETAIL_DEMO_LOCALE_SETUP:
        20c799e com.android.settings/com.google.android.settings.retaildemo.RetailDemoLocaleUpdateActivity filter a921c7f
          Action: "com.google.android.settings.action.RETAIL_DEMO_LOCALE_SETUP"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.WIFI_TETHER_SETTINGS:
        a11a2d1 com.android.settings/.Settings$WifiTetherSettingsActivity filter 7c43136
          Action: "com.android.settings.WIFI_TETHER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.LICENSE:
        5468fb com.android.settings/.SettingsLicenseActivity filter 90f5d18
          Action: "android.settings.LICENSE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.nfc.cardemulation.action.ACTION_CHANGE_DEFAULT:
        2961a88 com.android.settings/.nfc.PaymentDefaultDialog filter 32eec21
          Action: "android.nfc.cardemulation.action.ACTION_CHANGE_DEFAULT"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.NOTIFICATION_ASSISTANT_SETTINGS:
        e0322d2 com.android.settings/.Settings$NotificationAssistantSettingsActivity filter c5dffa3
          Action: "android.settings.NOTIFICATION_ASSISTANT_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.LANGUAGE_SETTINGS:
        93244c3 com.android.settings/.Settings$LanguageAndInputSettingsActivity filter d2ce140
          Action: "android.settings.LANGUAGE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
        544f9be com.android.settings/.Settings$LanguageSettingsActivity filter 96a6a1f
          Action: "android.settings.LANGUAGE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.ACTION_OTHER_SOUND_SETTINGS:
        a1e9a3d com.android.settings/.Settings$SoundSettingsActivity filter a347232
          Action: "android.settings.ACTION_OTHER_SOUND_SETTINGS"
          Action: "android.settings.SOUND_SETTINGS"
          Action: "com.android.settings.SOUND_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ACCOUNT_SYNC_SETTINGS:
        b914f79 com.android.settings/.Settings$AccountSyncSettingsActivity filter 3abe4be
          Action: "android.settings.ACCOUNT_SYNC_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.net.action.PROMPT_UNVALIDATED:
        5bac9e5 com.android.settings/.wifi.WifiNoInternetDialog filter 629ecba
          Action: "android.net.action.PROMPT_UNVALIDATED"
          Category: "android.intent.category.DEFAULT"
      android.settings.MANAGE_APP_LONG_RUNNING_JOBS:
        bef572f com.android.settings/.Settings$LongBackgroundTasksActivity filter ed2a13c
          Action: "android.settings.MANAGE_APP_LONG_RUNNING_JOBS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.COMMUNAL_SETTINGS:
        7d20d70 com.android.settings/.Settings$CommunalSettingsActivity filter 92808e9
          Action: "android.settings.COMMUNAL_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.LOCATION_SCANNING_SETTINGS:
        4905e8d com.android.settings/.Settings$ScanningSettingsActivity filter c556842
          Action: "android.settings.LOCATION_SCANNING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.intent.action.MAIN:
        cbce5a7 com.android.settings/com.google.android.settings.gestures.assist.AssistGestureTrainingIntroActivity filter 12abdfd
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.ASSIST_GESTURE"
        3c42af2 com.android.settings/com.google.android.settings.gestures.AssistGestureSuggestion filter 8c83543
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
          mPriority=30, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        24b47c0 com.android.settings/com.google.android.settings.gestures.columbus.ColumbusGestureTrainingIntroActivity filter 566043e
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.COLUMBUS_GESTURE"
        d2909bb com.android.settings/com.google.android.settings.aware.AwareSettingsActivity filter 7e19231
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        87c5d16 com.android.settings/com.google.android.settings.aware.WakeScreenSuggestionActivity filter 6548697
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        74291aa com.android.settings/.Settings filter 336019b
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.LAUNCHER"
        d7790e4 com.android.settings/.Settings$NetworkDashboardActivity filter f57ac02
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        a490913 com.android.settings/.Settings$MobileNetworkActivity filter 98ed750
          Action: "android.settings.NETWORK_OPERATOR_SETTINGS"
          Action: "android.telephony.ims.action.SHOW_CAPABILITY_DISCOVERY_OPT_IN"
          Action: "android.intent.action.MAIN"
          Action: "android.settings.MMS_MESSAGE_SETTING"
          Action: "android.settings.DATA_ROAMING_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        a926505 com.android.settings/.Settings$BluetoothSettingsActivity filter 1fab95a
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=10, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        1d65d03 com.android.settings/.Settings$NetworkProviderSettingsActivity filter aa20ab9
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        89e9398 com.android.settings/.Settings$ConfigureWifiSettingsActivity filter 7e00fd6
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        f8e822d com.android.settings/.Settings$WifiInfoActivity filter 7255362
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEVELOPMENT_PREFERENCE"
          Category: "android.intent.category.DEFAULT"
        a188cf3 com.android.settings/.wifi.WifiConfigInfo filter e583db0
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEVELOPMENT_PREFERENCE"
          Category: "android.intent.category.DEFAULT"
        47e1429 com.android.settings/.Settings$WifiAPITestActivity filter 48943ae
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEVELOPMENT_PREFERENCE"
          Category: "android.intent.category.DEFAULT"
        7a5054f com.android.settings/.wifi.WifiStatusTest filter 2fb84dc
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEVELOPMENT_PREFERENCE"
          Category: "android.intent.category.DEFAULT"
        52a12c8 com.android.settings/.Settings$ApnSettingsActivity filter 3fa1a86
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        514415b com.android.settings/.Settings$TetherSettingsActivity filter cebbdf8
          Action: "android.intent.action.MAIN"
          Action: "android.settings.TETHER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        a11a2d1 com.android.settings/.Settings$WifiTetherSettingsActivity filter b4b9837
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=4, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        91ac1a4 com.android.settings/.Settings$WifiP2pSettingsActivity filter 3c9b0d
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        a1a2ac2 com.android.settings/.Settings$VpnSettingsActivity filter 9145410
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=5, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        aa4374b com.android.settings/.Settings$DateTimeSettingsActivity filter defe241
          Action: "android.intent.action.MAIN"
          Action: "android.intent.action.QUICK_CLOCK"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        55953e6 com.android.settings/.Settings$LocalePickerActivity filter 583dbd4
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        93244c3 com.android.settings/.Settings$LanguageAndInputSettingsActivity filter 3d9879
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        544f9be com.android.settings/.Settings$LanguageSettingsActivity filter 19ed16c
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        454ddb1 com.android.settings/.Settings$KeyboardSettingsActivity filter b948296
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        9f891e9 com.android.settings/.Settings$SpellCheckersSettingsActivity filter e814e6e
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        a08190f com.android.settings/.inputmethod.InputMethodAndSubtypeEnablerActivity filter 9bf63a5
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
        d77e37a com.android.settings/.Settings$UserDictionarySettingsActivity filter 13c788
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        8f01b07 com.android.settings/.Settings$ZenModeSettingsActivity filter f0b67d2
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=41, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        fe960a3 com.android.settings/.notification.zen.ZenSuggestionActivity filter 2e1ffa0
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.ZEN"
        fe960a3 com.android.settings/.notification.zen.ZenSuggestionActivity filter bdcc759
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        f18411b com.android.settings/.wallpaper.WallpaperSuggestionActivity filter 50f0891
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        f18411b com.android.settings/.wallpaper.WallpaperSuggestionActivity filter d2903f6
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.PERSONALIZE"
        fefd3f7 com.android.settings/.wallpaper.StyleSuggestionActivity filter 3bcb264
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        30a9ccd com.android.settings/.Settings$ZenModeScheduleRuleSettingsActivity filter 943b893
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        f389bce com.android.settings/.Settings$DisplaySettingsActivity filter 429e9fc
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=30, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        b9885 com.android.settings/.Settings$SmartAutoRotateSettingsActivity filter 87a70b
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=32, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        c29a9e8 com.android.settings/.Settings$NightDisplaySettingsActivity filter f23801
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=32, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        f87a8e7 com.android.settings/.Settings$DarkThemeSettingsActivity filter be37c94
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=32, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        ac33732 com.android.settings/.Settings$NightDisplaySuggestionActivity filter 29bec83
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        ec5ce00 com.android.settings/.Settings$MyDeviceInfoActivity filter ce9947e
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=71, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        bf699d7 com.android.settings/.Settings$ManageApplicationsActivity filter c9a85ad
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=20, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        1d63692 com.android.settings/.Settings$RunningServicesActivity filter 3c1e863
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.MONKEY"
          Category: "android.intent.category.VOICE_LAUNCH"
        df04c60 com.android.settings/.Settings$StorageUseActivity filter e1d29de
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.MONKEY"
          Category: "android.intent.category.VOICE_LAUNCH"
        4e0a7bf com.android.settings/.Settings$NotificationStationActivity filter 37dce8c
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=22, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        dc7c9d5 com.android.settings/.notification.history.NotificationHistoryActivity filter d0200db
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        cfe96b6 com.android.settings/.Settings$LocationSettingsActivity filter a1d6324
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=52, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        315689 com.android.settings/.Settings$SecurityDashboardActivity filter ad8feaf
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        8a304fd com.android.settings/.Settings$PrivacySettingsActivity filter 19c65f2
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        f73e1d8 com.android.settings/.Settings$DeviceAdminSettingsActivity filter 8372931
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        e6ba3ee com.android.settings/.Settings$IccLockSettingsActivity filter 7db808f
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        73b7f1c com.android.settings/.Settings$AccessibilitySettingsActivity filter d7210fa
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=60, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        1d8f287 com.android.settings/.TextReadingForSetupWizardActivity filter eae95b4
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.DISPLAY_SETTINGS"
        f2ac5dd com.android.settings/.FontSizeSettingsForSetupWizardActivity filter 36dc552
          Action: "android.intent.action.MAIN"
        992e2d9 com.android.settings/.Settings$AccessibilityDaltonizerSettingsActivity filter ce3ab7f
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        e6ae74c com.android.settings/.Settings$ReduceBrightColorsSettingsActivity filter 2f0acaa
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        a91809b com.android.settings/.Settings$AccessibilityInversionSettingsActivity filter 8fd1411
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        381368 com.android.settings/.SetupRedactionInterstitial filter 83a2381
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.LOCK_SCREEN_REDACTION"
        5c3fbac com.android.settings/.SetupFingerprintSuggestionActivity filter e28c075
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FINGERPRINT_ENROLL"
        4165ad6 com.android.settings/.password.ScreenLockSuggestionActivity filter 4b61157
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        b181444 com.android.settings/.biometrics.fingerprint.FingerprintEnrollSuggestionActivity filter 5892d
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
          mPriority=2, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        7f54e62 com.android.settings/.Settings$StorageDashboardActivity filter 6a430b0
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=50, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        87fe47 com.android.settings/.Settings$PrintSettingsActivity filter 188179d
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        399dee6 com.android.settings/.Settings$PowerUsageSummaryActivity filter 79aded4
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=51, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        b73883b com.android.settings/.FallbackHome filter c552b58
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.HOME"
          Category: "android.intent.category.DEFAULT"
          mPriority=-1000, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        18874b1 com.android.settings/.Settings$DataUsageSummaryActivity filter 5086d17
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=3, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        1ef4aa5 com.android.settings/.Settings$PaymentSettingsActivity filter 852f62b
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        fcc9a1e com.android.settings/.Settings$PictureInPictureSettingsActivity filter 67958cc
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        3a1c01b com.android.settings/.Settings$TurnScreenOnSettingsActivity filter 5da1f91
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        96a8cfc com.android.settings/.Settings$ConfigureNotificationSettingsActivity filter 8d781da
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=21, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        a1e9a3d com.android.settings/.Settings$SoundSettingsActivity filter 7cc0b83
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=40, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        f28395c com.android.settings/.sim.SimDialogActivity filter ec2a465
          Action: "android.intent.action.MAIN"
        214f53a com.android.settings/.Settings$WifiCallingSettingsActivity filter a8045eb
          Action: "android.intent.action.MAIN"
          Action: "android.settings.WIFI_CALLING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        cad8f48 com.android.settings/.wifi.calling.WifiCallingSuggestionActivity filter 13e21e1
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.suggested.category.FIRST_IMPRESSION"
        d7f15cb com.android.settings/.backup.UserBackupSettingsActivity filter dc251a8
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
        240a0f2 com.android.settings/.Settings$AccountDashboardActivity filter b11aaf9
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=53, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        e33da3e com.android.settings/.Settings$SystemDashboardActivity filter 287009f
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=70, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        e690c20 com.android.settings/.Settings$WifiCallingDisclaimerActivity filter 52c19d9
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEFAULT"
        4eac7aa com.android.settings/.Settings$GestureNavigationSettingsActivity filter 848ff9b
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=32, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        9a62b11 com.android.settings/.Settings$ButtonNavigationSettingsActivity filter d05b476
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=32, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        467bd50 com.android.settings/.Settings$OneHandedSettingsActivity filter 6eadc4e
          Action: "android.intent.action.MAIN"
          Category: "com.android.settings.SHORTCUT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        6f13305 com.android.settings/.UsageStatsActivity filter d1c6f5a
          Action: "android.intent.action.MAIN"
          Category: "android.intent.category.DEVELOPMENT_PREFERENCE"
      android.settings.TETHER_SETTINGS:
        514415b com.android.settings/.Settings$TetherSettingsActivity filter cebbdf8
          Action: "android.intent.action.MAIN"
          Action: "android.settings.TETHER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
      android.settings.NOTIFICATION_POLICY_ACCESS_SETTINGS:
        5e1c6ce com.android.settings/.Settings$ZenAccessSettingsActivity filter d0899ef
          Action: "android.settings.NOTIFICATION_POLICY_ACCESS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.intent.action.MANAGE_PACKAGE_STORAGE:
        df04c60 com.android.settings/.Settings$StorageUseActivity filter 8d5f519
          Action: "android.intent.action.MANAGE_PACKAGE_STORAGE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ZEN_MODE_ONBOARDING:
        9942f1e com.android.settings/.notification.zen.ZenOnboardingActivity filter 9a763ff
          Action: "android.settings.ZEN_MODE_ONBOARDING"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.INTERNAL_STORAGE_SETTINGS:
        7f54e62 com.android.settings/.Settings$StorageDashboardActivity filter 3206bf3
          Action: "android.settings.INTERNAL_STORAGE_SETTINGS"
          Action: "android.settings.MEMORY_CARD_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_ADD_NETWORKS:
        c5917a1 com.android.settings/.wifi.addappnetworks.AddAppNetworksActivity filter ea84dc6
          Action: "android.settings.WIFI_ADD_NETWORKS"
          Category: "android.intent.category.DEFAULT"
      android.settings.MANAGE_APPLICATIONS_SETTINGS:
        bf699d7 com.android.settings/.Settings$ManageApplicationsActivity filter e2932c4
          Action: "android.settings.MANAGE_APPLICATIONS_SETTINGS"
          Action: "android.settings.APPLICATION_SETTINGS"
          Action: "android.settings.MANAGE_ALL_APPLICATIONS_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.LOCK_SCREEN_SETTINGS:
        226cddf com.android.settings/.Settings$LockScreenSettingsActivity filter 6b9ca2c
          Action: "android.settings.LOCK_SCREEN_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.CONFIRM_REMOTE_DEVICE_CREDENTIAL:
        a1cbb7c com.android.settings/.ConfirmRemoteDeviceCredentialActivity filter d43cc05
          Action: "android.app.action.CONFIRM_REMOTE_DEVICE_CREDENTIAL"
          Category: "android.intent.category.DEFAULT"
      android.settings.SHOW_REMOTE_BUGREPORT_DIALOG:
        d1b04a4 com.android.settings/.RemoteBugreportActivity filter ac3220d
          Action: "android.settings.SHOW_REMOTE_BUGREPORT_DIALOG"
          Category: "android.intent.category.DEFAULT"
      android.settings.TETHER_UNSUPPORTED_CARRIER_UI:
        acaf655 com.android.settings/.network.TetherProvisioningCarrierDialogActivity filter a36f86a
          Action: "android.settings.TETHER_UNSUPPORTED_CARRIER_UI"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.SYNC_SETTINGS:
        240a0f2 com.android.settings/.Settings$AccountDashboardActivity filter 3ba7343
          Action: "android.settings.SYNC_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.security.SECURITY_ADVANCED_SETTINGS:
        657f2bc com.android.settings/.Settings$SecurityAdvancedSettings filter 8cfd245
          Action: "com.android.settings.security.SECURITY_ADVANCED_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.action.SCREEN_SAVER:
        dfe5c1c com.android.settings/com.google.android.settings.dream.DreamSetupActivity filter f05f025
          Action: "com.android.settings.action.SCREEN_SAVER"
          Category: "android.intent.category.DEFAULT"
      android.settings.NETWORK_PROVIDER_SETTINGS:
        1d65d03 com.android.settings/.Settings$NetworkProviderSettingsActivity filter beeb480
          Action: "android.settings.NETWORK_PROVIDER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.GESTURE_NAVIGATION_SETTINGS:
        4eac7aa com.android.settings/.Settings$GestureNavigationSettingsActivity filter 1d83f38
          Action: "com.android.settings.GESTURE_NAVIGATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.SET_PROFILE_OWNER:
        5314384 com.android.settings/.applications.specialaccess.deviceadmin.ProfileOwnerAdd filter 4a4276d
          Action: "android.app.action.SET_PROFILE_OWNER"
          Category: "android.intent.category.DEFAULT"
          mPriority=1000, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WEBVIEW_SETTINGS:
        a795f5e com.android.settings/.WebViewImplementation filter 1706f3f
          Action: "android.settings.WEBVIEW_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.NFC_PAYMENT_SETTINGS:
        1ef4aa5 com.android.settings/.Settings$PaymentSettingsActivity filter c3f3e7a
          Action: "android.settings.NFC_PAYMENT_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_SCANNING_SETTINGS:
        b2db053 com.android.settings/.Settings$WifiScanningSettingsActivity filter 15f8d90
          Action: "android.settings.WIFI_SCANNING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.TTS_SETTINGS:
        94e2702 com.android.settings/.Settings$TextToSpeechSettingsActivity filter 3b56813
          Action: "com.android.settings.TTS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ACTION_APP_NOTIFICATION_REDACTION:
        e589c26 com.android.settings/.notification.RedactionSettingsStandalone filter 6b24067
          Action: "android.settings.ACTION_APP_NOTIFICATION_REDACTION"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MEMORY_CARD_SETTINGS:
        7f54e62 com.android.settings/.Settings$StorageDashboardActivity filter 3206bf3
          Action: "android.settings.INTERNAL_STORAGE_SETTINGS"
          Action: "android.settings.MEMORY_CARD_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ACCESSIBILITY_SETTINGS:
        73b7f1c com.android.settings/.Settings$AccessibilitySettingsActivity filter b7d725
          Action: "android.settings.ACCESSIBILITY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.REQUEST_SCHEDULE_EXACT_ALARM:
        f2736bf com.android.settings/.Settings$AlarmsAndRemindersActivity filter d1ab18c
          Action: "android.settings.REQUEST_SCHEDULE_EXACT_ALARM"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_CALLING_SETTINGS:
        214f53a com.android.settings/.Settings$WifiCallingSettingsActivity filter a8045eb
          Action: "android.intent.action.MAIN"
          Action: "android.settings.WIFI_CALLING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE_LAUNCH"
      android.settings.ACCESSIBILITY_COLOR_MOTION_SETTINGS:
        8fcd3e4 com.android.settings/.Settings$ColorAndMotionActivity filter 28de04d
          Action: "android.settings.ACCESSIBILITY_COLOR_MOTION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.REVERSE_CHARGING_SETTINGS:
        2c98084 com.android.settings/com.google.android.settings.fuelgauge.reversecharging.ReverseChargingTrampoline filter f0c206d
          Action: "android.settings.REVERSE_CHARGING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DARK_THEME_SETTINGS:
        f87a8e7 com.android.settings/.Settings$DarkThemeSettingsActivity filter e49533d
          Action: "android.settings.DARK_THEME_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.adapter.action.REQUEST_ENABLE:
        5dd0f8 com.android.settings/.bluetooth.RequestPermissionActivity filter 56db9d1
          Action: "android.bluetooth.adapter.action.REQUEST_ENABLE"
          Action: "android.bluetooth.adapter.action.REQUEST_DISCOVERABLE"
          Action: "android.bluetooth.adapter.action.REQUEST_DISABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MOBILE_NETWORK_LIST:
        f4c3d49 com.android.settings/.Settings$MobileNetworkListActivity filter d98864e
          Action: "android.settings.MOBILE_NETWORK_LIST"
          Action: "android.settings.MANAGE_ALL_SIM_PROFILES_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.PRIVACY_SETTINGS:
        1d35443 com.android.settings/.Settings$PrivacyDashboardActivity filter 9797ac0
          Action: "android.settings.PRIVACY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.ADVANCED_CONNECTED_DEVICE_SETTINGS:
        90174d8 com.android.settings/.Settings$AdvancedConnectedDeviceActivity filter e48c031
          Action: "com.android.settings.ADVANCED_CONNECTED_DEVICE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ALL_APPS_NOTIFICATION_SETTINGS:
        7b50100 com.android.settings/.Settings$NotificationAppListActivity filter 45f9d39
          Action: "android.settings.ALL_APPS_NOTIFICATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.MONITORING_CERT_INFO:
        9204dc1 com.android.settings/.MonitoringCertInfoActivity filter eb81966
          Action: "com.android.settings.MONITORING_CERT_INFO"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MMS_MESSAGE_SETTING:
        a490913 com.android.settings/.Settings$MobileNetworkActivity filter 98ed750
          Action: "android.settings.NETWORK_OPERATOR_SETTINGS"
          Action: "android.telephony.ims.action.SHOW_CAPABILITY_DISCOVERY_OPT_IN"
          Action: "android.intent.action.MAIN"
          Action: "android.settings.MMS_MESSAGE_SETTING"
          Action: "android.settings.DATA_ROAMING_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MOBILE_DATA_USAGE:
        c9da504 com.android.settings/.Settings$MobileDataUsageListActivity filter c7eaaed
          Action: "android.settings.MOBILE_DATA_USAGE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.NOTIFICATION_HISTORY:
        dc7c9d5 com.android.settings/.notification.history.NotificationHistoryActivity filter d4e05ea
          Action: "android.settings.NOTIFICATION_HISTORY"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIRELESS_SETTINGS:
        d7790e4 com.android.settings/.Settings$NetworkDashboardActivity filter e66594d
          Action: "com.android.settings.sim.SIM_SUB_INFO_SETTINGS"
          Action: "android.settings.WIRELESS_SETTINGS"
          Action: "android.settings.AIRPLANE_MODE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.action.ONE_HANDED_SETTINGS:
        467bd50 com.android.settings/.Settings$OneHandedSettingsActivity filter 7ba2b49
          Action: "android.settings.action.ONE_HANDED_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.MORE_SECURITY_PRIVACY_SETTINGS:
        8ebbd9a com.android.settings/.Settings$MoreSecurityPrivacySettingsActivity filter f40d6cb
          Action: "com.android.settings.MORE_SECURITY_PRIVACY_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.USER_DICTIONARY_SETTINGS:
        d77e37a com.android.settings/.Settings$UserDictionarySettingsActivity filter db7372b
          Action: "android.settings.USER_DICTIONARY_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.NOTIFICATION_LISTENER_DETAIL_SETTINGS:
        8b65734 com.android.settings/.Settings$NotificationAccessDetailsActivity filter a6d295d
          Action: "android.settings.NOTIFICATION_LISTENER_DETAIL_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ALL_APPS_NOTIFICATION_SETTINGS_FOR_REVIEW:
        ae92d2c com.android.settings/.Settings$NotificationReviewPermissionsActivity filter d13d3f5
          Action: "android.settings.ALL_APPS_NOTIFICATION_SETTINGS_FOR_REVIEW"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_IP_SETTINGS:
        89e9398 com.android.settings/.Settings$ConfigureWifiSettingsActivity filter c0d57f1
          Action: "android.settings.WIFI_IP_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.APPLICATION_SETTINGS:
        bf699d7 com.android.settings/.Settings$ManageApplicationsActivity filter e2932c4
          Action: "android.settings.MANAGE_APPLICATIONS_SETTINGS"
          Action: "android.settings.APPLICATION_SETTINGS"
          Action: "android.settings.MANAGE_ALL_APPLICATIONS_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.device.action.PAIRING_REQUEST:
        ef8136a com.android.settings/.bluetooth.BluetoothPairingDialog filter 386c05b
          Action: "android.bluetooth.device.action.PAIRING_REQUEST"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MANAGE_DEBUGGING_DATA_PERMISSION:
        8a5058b com.android.settings/com.google.android.settings.DebuggingDataActivity filter a75e668
          Action: "android.settings.MANAGE_DEBUGGING_DATA_PERMISSION"
          Category: "android.intent.category.DEFAULT"
      android.service.quicksettings.action.QS_TILE_PREFERENCES:
        b9e47ba com.android.settings/.Settings$DevelopmentSettingsDashboardActivity filter 1b666b
          Action: "android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Action: "android.service.quicksettings.action.QS_TILE_PREFERENCES"
          Action: "com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.TRUSTED_CREDENTIALS:
        70414a7 com.android.settings/.Settings$TrustedCredentialsSettingsActivity filter b31dd54
          Action: "com.android.settings.TRUSTED_CREDENTIALS_USER"
          Action: "com.android.settings.TRUSTED_CREDENTIALS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.credentials.UNLOCK:
        315689 com.android.settings/.Settings$SecurityDashboardActivity filter 455c68e
          Action: "android.credentials.UNLOCK"
          Action: "android.settings.SECURITY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ZEN_MODE_PRIORITY_SETTINGS:
        8f01b07 com.android.settings/.Settings$ZenModeSettingsActivity filter 707625d
          Action: "android.settings.ZEN_MODE_PRIORITY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.FACE_ENROLL:
        2efe14 com.android.settings/.biometrics.face.FaceEnrollIntroduction filter ce476bd
          Action: "android.settings.FACE_ENROLL"
          Category: "android.intent.category.DEFAULT"
      android.settings.SETTINGS_EMBED_DEEP_LINK_ACTIVITY:
        b5e1938 com.android.settings/.homepage.DeepLinkHomepageActivity filter c0ffd11
          Action: "android.settings.SETTINGS_EMBED_DEEP_LINK_ACTIVITY"
          Category: "android.intent.category.DEFAULT"
      android.intent.action.QUICK_CLOCK:
        aa4374b com.android.settings/.Settings$DateTimeSettingsActivity filter defe241
          Action: "android.intent.action.MAIN"
          Action: "android.intent.action.QUICK_CLOCK"
          Category: "android.intent.category.VOICE_LAUNCH"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.action.FACTORY_RESET:
        710a202 com.android.settings/.Settings$FactoryResetActivity filter 2fdc713
          Action: "com.android.settings.action.FACTORY_RESET"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.action.AWARE_SETTING:
        d2909bb com.android.settings/com.google.android.settings.aware.AwareSettingsActivity filter d124ed8
          Action: "com.android.settings.action.AWARE_SETTING"
          Category: "android.intent.category.DEFAULT"
      android.net.vpn.SETTINGS:
        a1a2ac2 com.android.settings/.Settings$VpnSettingsActivity filter a3780d3
          Action: "android.net.vpn.SETTINGS"
          Action: "android.settings.VPN_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.BLUETOOTH_PAIRING_SETTINGS:
        2bcacf5 com.android.settings/.Settings$BlueToothPairingActivity filter 1867a8a
          Action: "android.settings.BLUETOOTH_PAIRING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ZEN_MODE_AUTOMATION_SETTINGS:
        2f775cc com.android.settings/.Settings$ZenModeAutomationSettingsActivity filter 1098015
          Action: "android.settings.ZEN_MODE_AUTOMATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DEVICE_INFO_SETTINGS:
        ec5ce00 com.android.settings/.Settings$MyDeviceInfoActivity filter 2fce639
          Action: "android.settings.DEVICE_INFO_SETTINGS"
          Action: "android.settings.DEVICE_NAME"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.FINGERPRINT_SETTINGS:
        7fe98e3 com.android.settings/.Settings$FingerprintSettingsActivity filter c8e72e0
          Action: "android.settings.FINGERPRINT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      com.android.credentials.RESET:
        bdb82ec com.android.settings/.security.CredentialStorage filter ce2d6b5
          Action: "com.android.credentials.INSTALL"
          Action: "com.android.credentials.RESET"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.net.wifi.action.REQUEST_SCAN_ALWAYS_AVAILABLE:
        6fbfc36 com.android.settings/.wifi.WifiScanModeActivity filter 7e70737
          Action: "android.net.wifi.action.REQUEST_SCAN_ALWAYS_AVAILABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.REQUEST_MANAGE_MEDIA:
        7614daf com.android.settings/.Settings$MediaManagementAppsActivity filter e7395bc
          Action: "android.settings.REQUEST_MANAGE_MEDIA"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.SECURITY_SETTINGS:
        315689 com.android.settings/.Settings$SecurityDashboardActivity filter 455c68e
          Action: "android.credentials.UNLOCK"
          Action: "android.settings.SECURITY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.BLUTOOTH_FIND_BROADCASTS_ACTIVITY:
        18e06f0 com.android.settings/.Settings$BluetoothFindBroadcastsActivity filter d364469
          Action: "android.settings.BLUTOOTH_FIND_BROADCASTS_ACTIVITY"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.intent.action.POWER_USAGE_SUMMARY:
        399dee6 com.android.settings/.Settings$PowerUsageSummaryActivity filter 6522c27
          Action: "android.intent.action.POWER_USAGE_SUMMARY"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.panel.action.NFC:
        fe4a21c com.android.settings/.panel.SettingsPanelActivity filter fdf6bfa
          Action: "android.settings.panel.action.NFC"
          Category: "android.intent.category.DEFAULT"
      android.settings.SHOW_ADMIN_SUPPORT_DETAILS:
        dbf3eb7 com.android.settings/.enterprise.ActionDisabledByAdminDialog filter 813a624
          Action: "android.settings.SHOW_ADMIN_SUPPORT_DETAILS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WARRANTY_DETAILS:
        4a31e08 com.android.settings/com.google.android.settings.warranty.WarrantyDetailsActivity filter eca69a1
          Action: "android.settings.WARRANTY_DETAILS"
          Category: "android.intent.category.DEFAULT"
      com.google.android.settings.COLUMBUS_GESTURE_TRAINING:
        24b47c0 com.android.settings/com.google.android.settings.gestures.columbus.ColumbusGestureTrainingIntroActivity filter 86a3cf9
          Action: "com.google.android.settings.COLUMBUS_GESTURE_TRAINING"
          Category: "android.intent.category.DEFAULT"
      android.settings.PRIVACY_ADVANCED_SETTINGS:
        8ebbd9a com.android.settings/.Settings$MoreSecurityPrivacySettingsActivity filter c0f7ea8
          Action: "android.settings.PRIVACY_ADVANCED_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.ZEN_MODE_SETTINGS:
        8f01b07 com.android.settings/.Settings$ZenModeSettingsActivity filter 4e1d434
          Action: "android.settings.ZEN_MODE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.VPN_SETTINGS:
        a1a2ac2 com.android.settings/.Settings$VpnSettingsActivity filter a3780d3
          Action: "android.net.vpn.SETTINGS"
          Action: "android.settings.VPN_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.intent.action.PICK_ACTIVITY:
        55c710 com.android.settings/.ActivityPicker filter d8cd209
          Action: "android.intent.action.PICK_ACTIVITY"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WALLPAPER_SETTINGS:
        f18411b com.android.settings/.wallpaper.WallpaperSuggestionActivity filter 70c22b8
          Action: "android.settings.WALLPAPER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.AUTO_ROTATE_SETTINGS:
        b9885 com.android.settings/.Settings$SmartAutoRotateSettingsActivity filter 946a6da
          Action: "android.settings.AUTO_ROTATE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.TURN_SCREEN_ON_SETTINGS:
        3a1c01b com.android.settings/.Settings$TurnScreenOnSettingsActivity filter 44935b8
          Action: "android.settings.TURN_SCREEN_ON_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.BUGREPORT_HANDLER_SETTINGS:
        87ec00c com.android.settings/.Settings$BugReportHandlerPickerActivity filter 1c39d55
          Action: "android.settings.BUGREPORT_HANDLER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.net.wifi.action.REQUEST_DISABLE:
        b09cbe2 com.android.settings/.wifi.RequestToggleWiFiActivity filter 216db73
          Action: "android.net.wifi.action.REQUEST_ENABLE"
          Action: "android.net.wifi.action.REQUEST_DISABLE"
          Category: "android.intent.category.DEFAULT"
      android.settings.CONVERSATION_SETTINGS:
        5eee60b com.android.settings/.Settings$ConversationListSettingsActivity filter 8517ce8
          Action: "android.settings.CONVERSATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MANAGE_ALL_APPLICATIONS_SETTINGS:
        bf699d7 com.android.settings/.Settings$ManageApplicationsActivity filter e2932c4
          Action: "android.settings.MANAGE_APPLICATIONS_SETTINGS"
          Action: "android.settings.APPLICATION_SETTINGS"
          Action: "android.settings.MANAGE_ALL_APPLICATIONS_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.action.LAUNCH_VPN_APP_EXCLUSION:
        55012b4 com.android.settings/com.google.android.settings.vpn2.AppBypassActivity filter 402fedd
          Action: "com.google.android.settings.action.LAUNCH_VPN_APP_EXCLUSION"
          Category: "android.intent.category.DEFAULT"
      android.settings.WIFI_DPP_CONFIGURATOR_QR_CODE_GENERATOR:
        27fa187 com.android.settings/.wifi.dpp.WifiDppConfiguratorActivity filter 8f918b4
          Action: "android.settings.WIFI_DPP_CONFIGURATOR_QR_CODE_GENERATOR"
          Action: "android.settings.WIFI_DPP_CONFIGURATOR_QR_CODE_SCANNER"
          Category: "android.intent.category.DEFAULT"
      android.settings.REQUEST_ENABLE_CONTENT_CAPTURE:
        1d35443 com.android.settings/.Settings$PrivacyDashboardActivity filter c9ff3f9
          Action: "android.settings.REQUEST_ENABLE_CONTENT_CAPTURE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ASSIST_GESTURE_SETTINGS:
        f364f47 com.android.settings/.Settings$AssistGestureSettingsActivity filter e319374
          Action: "android.settings.ASSIST_GESTURE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.REGIONAL_PREFERENCES_SETTINGS:
        fd5893b com.android.settings/.Settings$RegionalPreferencesActivity filter c5d9858
          Action: "android.settings.REGIONAL_PREFERENCES_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ENTERPRISE_PRIVACY_SETTINGS:
        ba54a50 com.android.settings/.Settings$EnterprisePrivacySettingsActivity filter be53449
          Action: "android.settings.ENTERPRISE_PRIVACY_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.WIFI_SETTINGS:
        4d2fbd com.android.settings/.Settings$WifiSettingsActivity filter e9719b2
          Action: "android.settings.WIFI_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.adapter.action.REQUEST_DISCOVERABLE:
        5dd0f8 com.android.settings/.bluetooth.RequestPermissionActivity filter 56db9d1
          Action: "android.bluetooth.adapter.action.REQUEST_ENABLE"
          Action: "android.bluetooth.adapter.action.REQUEST_DISCOVERABLE"
          Action: "android.bluetooth.adapter.action.REQUEST_DISABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.APP_NOTIFICATION_SETTINGS:
        84158a com.android.settings/.Settings$AppNotificationSettingsActivity filter 98967fb
          Action: "android.settings.APP_NOTIFICATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.AIRPLANE_MODE_SETTINGS:
        d7790e4 com.android.settings/.Settings$NetworkDashboardActivity filter e66594d
          Action: "com.android.settings.sim.SIM_SUB_INFO_SETTINGS"
          Action: "android.settings.WIRELESS_SETTINGS"
          Action: "android.settings.AIRPLANE_MODE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MANAGE_UNKNOWN_APP_SOURCES:
        6a27fdb com.android.settings/.Settings$ManageExternalSourcesActivity filter 4875a78
          Action: "android.settings.MANAGE_UNKNOWN_APP_SOURCES"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.panel.action.INTERNET_CONNECTIVITY:
        fe4a21c com.android.settings/.panel.SettingsPanelActivity filter b65be25
          Action: "android.settings.panel.action.INTERNET_CONNECTIVITY"
          Category: "android.intent.category.DEFAULT"
      android.settings.MODULE_LICENSES:
        2782371 com.android.settings/.Settings$ModuleLicensesActivity filter 259b556
          Action: "android.settings.MODULE_LICENSES"
          Category: "android.intent.category.DEFAULT"
      android.settings.SOUND_SETTINGS:
        a1e9a3d com.android.settings/.Settings$SoundSettingsActivity filter a347232
          Action: "android.settings.ACTION_OTHER_SOUND_SETTINGS"
          Action: "android.settings.SOUND_SETTINGS"
          Action: "com.android.settings.SOUND_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.VOICE_CONTROL_DO_NOT_DISTURB_MODE:
        a7f4778 com.android.settings/.notification.zen.ZenModeVoiceActivity filter ec82e51
          Action: "android.settings.VOICE_CONTROL_DO_NOT_DISTURB_MODE"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE"
      android.settings.VOICE_INPUT_SETTINGS:
        a28a3ed com.android.settings/.Settings$ManageAssistActivity filter b8e3222
          Action: "android.settings.VOICE_INPUT_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MANAGE_DOMAIN_URLS:
        353d0e2 com.android.settings/.Settings$ManageDomainUrlsActivity filter 520fc73
          Action: "android.settings.MANAGE_DOMAIN_URLS"
          Category: "android.intent.category.DEFAULT"
      android.settings.APP_MEMORY_USAGE:
        fe8b730 com.android.settings/.Settings$AppMemoryUsageActivity filter d06cfa9
          Action: "android.settings.APP_MEMORY_USAGE"
          Category: "android.intent.category.DEFAULT"
      android.settings.action.MANAGE_OVERLAY_PERMISSION:
        acd2b06 com.android.settings/.Settings$OverlaySettingsActivity filter 91b55c7
          Action: "android.settings.action.MANAGE_OVERLAY_PERMISSION"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_SAVED_NETWORK_SETTINGS:
        4be2257 com.android.settings/.Settings$SavedAccessPointsSettingsActivity filter 9b55144
          Action: "android.settings.WIFI_SAVED_NETWORK_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.VOICE_CONTROL_AIRPLANE_MODE:
        1d6878b com.android.settings/.AirplaneModeVoiceActivity filter 6264068
          Action: "android.settings.VOICE_CONTROL_AIRPLANE_MODE"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE"
      com.google.android.settings.fuelgauge.REVERSE_CHARGING_TOOL_SETTINGS:
        7a020f0 com.android.settings/com.google.android.settings.fuelgauge.reversecharging.ReverseChargingToolTrampoline filter 2d75669
          Action: "com.google.android.settings.fuelgauge.REVERSE_CHARGING_TOOL_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DATA_ROAMING_SETTINGS:
        a490913 com.android.settings/.Settings$MobileNetworkActivity filter 98ed750
          Action: "android.settings.NETWORK_OPERATOR_SETTINGS"
          Action: "android.telephony.ims.action.SHOW_CAPABILITY_DISCOVERY_OPT_IN"
          Action: "android.intent.action.MAIN"
          Action: "android.settings.MMS_MESSAGE_SETTING"
          Action: "android.settings.DATA_ROAMING_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.gestures.QUICK_TAP_SETTINGS:
        7aee29f com.android.settings/com.google.android.settings.gestures.columbus.ColumbusSettingsActivity filter 47d1fec
          Action: "com.google.android.settings.gestures.QUICK_TAP_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.NFCSHARING_SETTINGS:
        8ea5c0e com.android.settings/.Settings$AndroidBeamSettingsActivity filter 4a9a62f
          Action: "android.settings.NFCSHARING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ZEN_MODE_SCHEDULE_RULE_SETTINGS:
        30a9ccd com.android.settings/.Settings$ZenModeScheduleRuleSettingsActivity filter ad96982
          Action: "android.settings.ZEN_MODE_SCHEDULE_RULE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.MANAGE_CROSS_PROFILE_ACCESS:
        337f564 com.android.settings/.Settings$InteractAcrossProfilesSettingsActivity filter af023cd
          Action: "android.settings.MANAGE_CROSS_PROFILE_ACCESS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.NIGHT_DISPLAY_SETTINGS:
        c29a9e8 com.android.settings/.Settings$NightDisplaySettingsActivity filter 5f856a6
          Action: "android.settings.NIGHT_DISPLAY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.ASSIST_GESTURE_TRAINING:
        cbce5a7 com.android.settings/com.google.android.settings.gestures.assist.AssistGestureTrainingIntroActivity filter 90da54
          Action: "com.google.android.settings.ASSIST_GESTURE_TRAINING"
          Category: "android.intent.category.DEFAULT"
      android.settings.ACCESSIBILITY_SETTINGS_FOR_SUW:
        733c0a1 com.android.settings/.accessibility.AccessibilitySettingsForSetupWizardActivity filter 34042c6
          Action: "android.settings.ACCESSIBILITY_SETTINGS_FOR_SUW"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.google.android.settings.action.LAUNCH_POWER_USAGE_ADVANCED:
        235a620 com.android.settings/com.google.android.settings.fuelgauge.PowerUsageAdvancedActivity filter 635abd9
          Action: "com.google.android.settings.action.LAUNCH_POWER_USAGE_ADVANCED"
          Category: "android.intent.category.DEFAULT"
      android.settings.ACTION_POWER_MENU_SETTINGS:
        122ca4c com.android.settings/.Settings$PowerMenuSettingsActivity filter 83b7a95
          Action: "android.settings.ACTION_POWER_MENU_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.MANAGE_CLONED_APPS_SETTINGS:
        1b37f7e com.android.settings/.Settings$ClonedAppsListActivity filter 3b9dcdf
          Action: "android.settings.MANAGE_CLONED_APPS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.CONFIRM_DEVICE_CREDENTIAL:
        ffbb14e com.android.settings/.password.ConfirmDeviceCredentialActivity filter e84726f
          Action: "android.app.action.CONFIRM_FRP_CREDENTIAL"
          Action: "android.app.action.CONFIRM_DEVICE_CREDENTIAL"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.NOTIFICATION_SETTINGS:
        96a8cfc com.android.settings/.Settings$ConfigureNotificationSettingsActivity filter 3aff85
          Action: "android.settings.NOTIFICATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DATA_USAGE_SETTINGS:
        18874b1 com.android.settings/.Settings$DataUsageSummaryActivity filter c8dcd96
          Action: "android.settings.DATA_USAGE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DREAM_SETTINGS:
        a512d22 com.android.settings/.Settings$DreamSettingsActivity filter a9cc3b3
          Action: "android.settings.DREAM_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.wifi.action.NETWORK_REQUEST:
        17cc42e com.android.settings/.wifi.NetworkRequestDialogActivity filter f79bbcf
          Action: "com.android.settings.wifi.action.NETWORK_REQUEST"
          Category: "android.intent.category.DEFAULT"
      android.settings.action.MANAGE_WRITE_SETTINGS:
        56d8763 com.android.settings/.Settings$WriteSettingsActivity filter 874ff60
          Action: "android.settings.action.MANAGE_WRITE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_DETAILS_SETTINGS:
        a591efe com.android.settings/.Settings$WifiDetailsSettingsActivity filter 5d7c65f
          Action: "android.settings.WIFI_DETAILS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.REVERSE_CHARGING_BOTTOM_SHEET:
        b5934a2 com.android.settings/com.google.android.settings.fuelgauge.reversecharging.BottomSheetActivity filter a50f533
          Action: "android.settings.REVERSE_CHARGING_BOTTOM_SHEET"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.adapter.action.REQUEST_DISABLE:
        5dd0f8 com.android.settings/.bluetooth.RequestPermissionActivity filter 56db9d1
          Action: "android.bluetooth.adapter.action.REQUEST_ENABLE"
          Action: "android.bluetooth.adapter.action.REQUEST_DISCOVERABLE"
          Action: "android.bluetooth.adapter.action.REQUEST_DISABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.INPUT_METHOD_SUBTYPE_SETTINGS:
        a08190f com.android.settings/.inputmethod.InputMethodAndSubtypeEnablerActivity filter daf6d9c
          Action: "android.settings.INPUT_METHOD_SUBTYPE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.CAST_SETTINGS:
        438443c com.android.settings/.Settings$WifiDisplaySettingsActivity filter 32785c5
          Action: "android.settings.CAST_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.ACCESSIBILITY_COLOR_SPACE_SETTINGS:
        992e2d9 com.android.settings/.Settings$AccessibilityDaltonizerSettingsActivity filter 17ee49e
          Action: "com.android.settings.ACCESSIBILITY_COLOR_SPACE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.panel.action.VOLUME:
        fe4a21c com.android.settings/.panel.SettingsPanelActivity filter 5a7c408
          Action: "android.settings.panel.action.VOLUME"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS:
        b9e47ba com.android.settings/.Settings$DevelopmentSettingsDashboardActivity filter 1b666b
          Action: "android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Action: "android.service.quicksettings.action.QS_TILE_PREFERENCES"
          Action: "com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
        6b7661 com.android.settings/.development.DevelopmentSettingsDisabledActivity filter bd92586
          Action: "android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Action: "com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=-1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.WIFI_DIALOG:
        88aaa30 com.android.settings/.wifi.WifiDialogActivity filter 40546a9
          Action: "com.android.settings.WIFI_DIALOG"
          Category: "android.intent.category.DEFAULT"
      com.android.intent.action.SHOW_CONTRAST_DIALOG:
        b9e47ba com.android.settings/.Settings$DevelopmentSettingsDashboardActivity filter 6a165c8
          Action: "com.android.settings.action.SETTINGS"
          Action: "com.android.intent.action.SHOW_CONTRAST_DIALOG"
      com.android.settings.BATTERY_SAVER_SCHEDULE_SETTINGS:
        a7d4f9e com.android.settings/.Settings$BatterySaverScheduleSettingsActivity filter 7d13a7f
          Action: "com.android.settings.BATTERY_SAVER_SCHEDULE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.ACTION_PRINT_SETTINGS:
        87fe47 com.android.settings/.Settings$PrintSettingsActivity filter b4b1674
          Action: "android.settings.ACTION_PRINT_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WIFI_DPP_CONFIGURATOR_QR_CODE_SCANNER:
        27fa187 com.android.settings/.wifi.dpp.WifiDppConfiguratorActivity filter 8f918b4
          Action: "android.settings.WIFI_DPP_CONFIGURATOR_QR_CODE_GENERATOR"
          Action: "android.settings.WIFI_DPP_CONFIGURATOR_QR_CODE_SCANNER"
          Category: "android.intent.category.DEFAULT"
      android.settings.REDUCE_BRIGHT_COLORS_SETTINGS:
        e6ae74c com.android.settings/.Settings$ReduceBrightColorsSettingsActivity filter 6c5d395
          Action: "android.settings.REDUCE_BRIGHT_COLORS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.INPUT_METHOD_SETTINGS:
        4097e17 com.android.settings/.Settings$AvailableVirtualKeyboardActivity filter 93fe204
          Action: "android.settings.INPUT_METHOD_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.DISPLAY_SETTINGS:
        f389bce com.android.settings/.Settings$DisplaySettingsActivity filter 9e74aef
          Action: "android.settings.DISPLAY_SETTINGS"
          Action: "com.android.settings.DISPLAY_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.LOCALE_SETTINGS:
        55953e6 com.android.settings/.Settings$LocalePickerActivity filter 87cfd27
          Action: "android.settings.LOCALE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.SET_NEW_PASSWORD:
        4b2698 com.android.settings/.password.SetNewPasswordActivity filter 751eef1
          Action: "android.app.action.SET_NEW_PASSWORD"
          Action: "android.app.action.SET_NEW_PARENT_PROFILE_PASSWORD"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.appwidget.action.APPWIDGET_BIND:
        9636828 com.android.settings/.AllowBindAppWidgetActivity filter fffb941
          Action: "android.appwidget.action.APPWIDGET_BIND"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.appwidget.action.APPWIDGET_PICK:
        df42b1a com.android.settings/.AppWidgetPickActivity filter 634764b
          Action: "android.appwidget.action.APPWIDGET_PICK"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.net.action.PROMPT_LOST_VALIDATION:
        5bac9e5 com.android.settings/.wifi.WifiNoInternetDialog filter 7d6a76b
          Action: "android.net.action.PROMPT_LOST_VALIDATION"
          Category: "android.intent.category.DEFAULT"
      android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS:
        4e2192e com.android.settings/.Settings$HighPowerApplicationsActivity filter f84eccf
          Action: "android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.TETHER_PROVISIONING_UI:
        b77e03f com.android.settings/.network.TetherProvisioningActivity filter 817dd0c
          Action: "android.settings.TETHER_PROVISIONING_UI"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.WARRANTY:
        650b5fa com.android.settings/com.google.android.settings.warranty.WarrantyActivity filter 12bd7ab
          Action: "android.settings.WARRANTY"
          Category: "android.intent.category.DEFAULT"
      android.settings.ADVANCED_MEMORY_PROTECTION_SETTINGS:
        a241167 com.android.settings/.Settings$MemtagPageActivity filter b52fb14
          Action: "android.settings.ADVANCED_MEMORY_PROTECTION_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ADAPTIVE_BRIGHTNESS_SETTINGS:
        aa42d0a com.android.settings/.Settings$AdaptiveBrightnessActivity filter d5c697b
          Action: "android.settings.ADAPTIVE_BRIGHTNESS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      com.google.android.settings.notification.CLEAR_CALLING:
        adc0a52 com.android.settings/com.google.android.settings.notification.ClearCallingSettingsActivity filter 8419123
          Action: "com.google.android.settings.notification.CLEAR_CALLING"
          Category: "android.intent.category.DEFAULT"
      android.settings.BLUETOOTH_LE_AUDIO_QR_CODE_SCANNER:
        373c16f com.android.settings/.bluetooth.QrCodeScanModeActivity filter 8135e7c
          Action: "android.settings.BLUETOOTH_LE_AUDIO_QR_CODE_SCANNER"
          Category: "android.intent.category.DEFAULT"
      android.settings.APN_SETTINGS:
        52a12c8 com.android.settings/.Settings$ApnSettingsActivity filter 3531f61
          Action: "android.settings.APN_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.action.IA_SETTINGS:
        d7f15cb com.android.settings/.backup.UserBackupSettingsActivity filter 8e24c1
          Action: "com.android.settings.action.IA_SETTINGS"
      android.security.MANAGE_CREDENTIALS:
        efec14a com.android.settings/.security.RequestManageCredentials filter a9908bb
          Action: "android.security.MANAGE_CREDENTIALS"
          Category: "android.intent.category.DEFAULT"
      android.settings.PRIVACY_CONTROLS:
        806ef3e com.android.settings/.Settings$PrivacyControlsActivity filter fccf19f
          Action: "android.settings.PRIVACY_CONTROLS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.CONFIRM_DEVICE_CREDENTIAL_WITH_USER:
        ee5945a com.android.settings/.password.ConfirmDeviceCredentialActivity$InternalActivity filter 28fc68b
          Action: "android.app.action.CONFIRM_DEVICE_CREDENTIAL_WITH_USER"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      com.android.settings.SEARCH_RESULT_TRAMPOLINE:
        e594c81 com.android.settings/.search.SearchResultTrampoline filter e1b1126
          Action: "com.android.settings.SEARCH_RESULT_TRAMPOLINE"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.SOUND_SETTINGS:
        a1e9a3d com.android.settings/.Settings$SoundSettingsActivity filter a347232
          Action: "android.settings.ACTION_OTHER_SOUND_SETTINGS"
          Action: "android.settings.SOUND_SETTINGS"
          Action: "com.android.settings.SOUND_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.CAPTIONING_SETTINGS:
        604e976 com.android.settings/.Settings$CaptioningSettingsActivity filter 67d8b77
          Action: "android.settings.CAPTIONING_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ZEN_MODE_EVENT_RULE_SETTINGS:
        8c490d0 com.android.settings/.Settings$ZenModeEventRuleSettingsActivity filter b138c9
          Action: "android.settings.ZEN_MODE_EVENT_RULE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.FACE_SETTINGS:
        5c1509d com.android.settings/.Settings$FaceSettingsActivity filter 4d5912
          Action: "android.settings.FACE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.intent.action.CREATE_SHORTCUT:
        e101e76 com.android.settings/.Settings$CreateShortcutActivity filter b691c77
          Action: "android.intent.action.CREATE_SHORTCUT"
          Category: "android.intent.category.DEFAULT"
      android.settings.CHANNEL_NOTIFICATION_SETTINGS:
        451f018 com.android.settings/.notification.app.ChannelPanelActivity filter 89aba71
          Action: "android.settings.CHANNEL_NOTIFICATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ACTION_CONDITION_PROVIDER_SETTINGS:
        2f775cc com.android.settings/.Settings$ZenModeAutomationSettingsActivity filter b501f2a
          Action: "android.settings.ACTION_CONDITION_PROVIDER_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.FINGERPRINT_ENROLL:
        607e780 com.android.settings/.biometrics.fingerprint.FingerprintEnrollIntroduction filter 6e6c1b9
          Action: "android.settings.FINGERPRINT_ENROLL"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
      android.settings.DEVICE_NAME:
        ec5ce00 com.android.settings/.Settings$MyDeviceInfoActivity filter 2fce639
          Action: "android.settings.DEVICE_INFO_SETTINGS"
          Action: "android.settings.DEVICE_NAME"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.TEXT_READING_SETTINGS:
        7483023 com.android.settings/.Settings$TextReadingSettingsActivity filter 6795920
          Action: "android.settings.TEXT_READING_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.MANAGE_ALL_SIM_PROFILES_SETTINGS:
        f4c3d49 com.android.settings/.Settings$MobileNetworkListActivity filter d98864e
          Action: "android.settings.MOBILE_NETWORK_LIST"
          Action: "android.settings.MANAGE_ALL_SIM_PROFILES_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.bluetooth.devicepicker.action.LAUNCH:
        8e75999 com.android.settings/.bluetooth.DevicePickerActivity filter d23f45e
          Action: "android.bluetooth.devicepicker.action.LAUNCH"
          Category: "android.intent.category.DEFAULT"
      android.settings.ACCESSIBILITY_DETAILS_SETTINGS:
        61996ab com.android.settings/.Settings$AccessibilityDetailsSettingsActivity filter 80f7108
          Action: "android.settings.ACCESSIBILITY_DETAILS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.DATE_SETTINGS:
        aa4374b com.android.settings/.Settings$DateTimeSettingsActivity filter fc69528
          Action: "android.settings.DATE_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.panel.action.WIFI:
        fe4a21c com.android.settings/.panel.SettingsPanelActivity filter 26355ab
          Action: "android.settings.panel.action.WIFI"
          Category: "android.intent.category.DEFAULT"
      com.android.settings.BUTTON_NAVIGATION_SETTINGS:
        9a62b11 com.android.settings/.Settings$ButtonNavigationSettingsActivity filter 1adfa77
          Action: "com.android.settings.BUTTON_NAVIGATION_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.app.action.SET_NEW_PARENT_PROFILE_PASSWORD:
        4b2698 com.android.settings/.password.SetNewPasswordActivity filter 751eef1
          Action: "android.app.action.SET_NEW_PASSWORD"
          Action: "android.app.action.SET_NEW_PARENT_PROFILE_PASSWORD"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.VOICE_CONTROL_BATTERY_SAVER_MODE:
        ab63c3 com.android.settings/.fuelgauge.BatterySaverModeVoiceActivity filter d311440
          Action: "android.settings.VOICE_CONTROL_BATTERY_SAVER_MODE"
          Category: "android.intent.category.DEFAULT"
          Category: "android.intent.category.VOICE"
      android.settings.WIFI_DPP_ENROLLEE_QR_CODE_SCANNER:
        4cb8052 com.android.settings/.wifi.dpp.WifiDppEnrolleeActivity filter d2acf23
          Action: "android.settings.WIFI_DPP_ENROLLEE_QR_CODE_SCANNER"
          Category: "android.intent.category.DEFAULT"
      android.settings.BATTERY_SAVER_SETTINGS:
        8cda87d com.android.settings/.Settings$BatterySaverSettingsActivity filter 6950372
          Action: "android.settings.BATTERY_SAVER_SETTINGS"
          Category: "android.intent.category.BROWSABLE"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.PICTURE_IN_PICTURE_SETTINGS:
        fcc9a1e com.android.settings/.Settings$PictureInPictureSettingsActivity filter 246f2ff
          Action: "android.settings.PICTURE_IN_PICTURE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.ACTION_MEDIA_CONTROLS_SETTINGS:
        86e16e4 com.android.settings/.Settings$MediaControlsSettingsActivity filter a31674d
          Action: "android.settings.ACTION_MEDIA_CONTROLS_SETTINGS"
          Category: "android.intent.category.DEFAULT"
      android.settings.NFC_SETTINGS:
        66ef316 com.android.settings/.Settings$NfcSettingsActivity filter 4526497
          Action: "android.settings.NFC_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.STORAGE_MANAGER_SETTINGS:
        9fea466 com.android.settings/.Settings$AutomaticStorageManagerSettingsActivity filter 46743a7
          Action: "android.settings.STORAGE_MANAGER_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false
      android.settings.APP_NOTIFICATION_BUBBLE_SETTINGS:
        2310f01 com.android.settings/.Settings$AppBubbleNotificationSettingsActivity filter d3be1a6
          Action: "android.settings.APP_NOTIFICATION_BUBBLE_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          mPriority=1, mOrder=0, mHasStaticPartialTypes=false, mHasDynamicPartialTypes=false

  MIME Typed Actions:
      android.intent.action.EDIT:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f93a7dc
          Action: "android.intent.action.EDIT"
          Action: "android.intent.action.VIEW"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.item/telephony-carrier"
      android.intent.action.VIEW:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f93a7dc
          Action: "android.intent.action.EDIT"
          Action: "android.intent.action.VIEW"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.item/telephony-carrier"
      android.provider.action.DOCUMENT_ROOT_SETTINGS:
        2de8b29 com.android.settings/.Settings$PublicVolumeSettingsActivity filter 1ddeeae
          Action: "android.provider.action.DOCUMENT_ROOT_SETTINGS"
          Category: "android.intent.category.DEFAULT"
          Scheme: "content"
          Authority: "com.android.externalstorage.documents": -1
          StaticType: "vnd.android.document/root"
      android.intent.action.INSERT:
        2cbd44f com.android.settings/.Settings$ApnEditorActivity filter f2bb0e5
          Action: "android.intent.action.INSERT"
          Category: "android.intent.category.DEFAULT"
          StaticType: "vnd.android.cursor.dir/telephony-carrier"

Receiver Resolver Table:
  Schemes:
      android_secret_code:
        9be99ae com.android.settings/.TestingSettingsBroadcastReceiver filter 38ea34f
          Action: "android.telephony.action.SECRET_CODE"
          Scheme: "android_secret_code"
          Authority: "4636": -1

  Non-Data Actions:
      android.telephony.action.PRIMARY_SUBSCRIPTION_LIST_CHANGED:
        d97d8e0 com.android.settings/.sim.SimSelectNotification filter afbc799
          Action: "android.telephony.action.PRIMARY_SUBSCRIPTION_LIST_CHANGED"
          Action: "android.settings.ENABLE_MMS_DATA_REQUEST"
      com.android.settings.SEARCH_START:
        666d744 com.android.settings/.search.SearchStateReceiver filter 1f8902d
          Action: "com.android.settings.SEARCH_START"
          Action: "com.android.settings.SEARCH_EXIT"
      com.android.settings.battery.action.ACTION_BATTERY_PLUGGING:
        797cadc com.android.settings/.fuelgauge.batteryusage.BatteryUsageBroadcastReceiver filter d9897e5
          Action: "com.android.settings.battery.action.ACTION_BATTERY_PLUGGING"
          Action: "android.intent.action.BATTERY_LEVEL_CHANGED"
          Action: "com.android.settings.battery.action.ACTION_BATTERY_UNPLUGGING"
          Action: "com.android.settings.battery.action.CLEAR_BATTERY_CACHE_DATA"
      android.settings.ENABLE_MMS_DATA_REQUEST:
        d97d8e0 com.android.settings/.sim.SimSelectNotification filter afbc799
          Action: "android.telephony.action.PRIMARY_SUBSCRIPTION_LIST_CHANGED"
          Action: "android.settings.ENABLE_MMS_DATA_REQUEST"
      android.bluetooth.device.action.CONNECTION_ACCESS_CANCEL:
        b9c23b0 com.android.settings/.bluetooth.BluetoothPermissionRequest filter e7b0229
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_CANCEL"
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_REQUEST"
      android.bluetooth.device.action.CONNECTION_ACCESS_REQUEST:
        b9c23b0 com.android.settings/.bluetooth.BluetoothPermissionRequest filter e7b0229
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_CANCEL"
          Action: "android.bluetooth.device.action.CONNECTION_ACCESS_REQUEST"
      androidx.profileinstaller.action.SAVE_PROFILE:
        d7de775 com.android.settings/androidx.profileinstaller.ProfileInstallReceiver filter b23b998
          Action: "androidx.profileinstaller.action.SAVE_PROFILE"
      com.android.settings.battery.action.PERIODIC_JOB_UPDATE:
        3c43086 com.android.settings/.fuelgauge.batteryusage.PeriodicJobReceiver filter ef5ad47
          Action: "com.android.settings.battery.action.PERIODIC_JOB_UPDATE"
      android.net.wifi.wsu.action.WSU_POST_PROVISIONING:
        10747a4 com.android.settings/com.google.android.wifitrackerlib.WsuPostProvisioningReceiver filter 4c5a90d
          Action: "android.net.wifi.wsu.action.WSU_POST_PROVISIONING"
      android.intent.action.BATTERY_LEVEL_CHANGED:
        797cadc com.android.settings/.fuelgauge.batteryusage.BatteryUsageBroadcastReceiver filter d9897e5
          Action: "com.android.settings.battery.action.ACTION_BATTERY_PLUGGING"
          Action: "android.intent.action.BATTERY_LEVEL_CHANGED"
          Action: "com.android.settings.battery.action.ACTION_BATTERY_UNPLUGGING"
          Action: "com.android.settings.battery.action.CLEAR_BATTERY_CACHE_DATA"
      android.telephony.action.SIM_SLOT_STATUS_CHANGED:
        6052e6a com.android.settings/.sim.receivers.SimSlotChangeReceiver filter 4553f5b
          Action: "android.telephony.action.SIM_SLOT_STATUS_CHANGED"
      com.google.android.settings.action.NOTIFY_PACKAGE_ADDED:
        96778b9 com.android.settings/com.google.android.settings.vpn2.AppBypassBroadcastReceiver filter fecf4fe
          Action: "com.google.android.settings.action.NOTIFY_PACKAGE_ADDED"
          Action: "com.google.android.settings.action.UPDATE_CARRIER_APP_LIST"
          Action: "com.google.android.settings.action.UPDATE_PREDEFINED_APP_EXCLUSION_LIST"
          Action: "com.google.android.settings.action.REMOVE_UNINSTALLED_APP"
      com.google.android.settings.routines.RoutinesActionBroadcastReceiver.RINGER_MODE_SILENCE_ACTION:
        3f7bdbd com.android.settings/com.google.android.settings.routines.RoutinesActionBroadcastReceiver filter 9798fb2
          Action: "com.google.android.settings.routines.RoutinesActionBroadcastReceiver.RINGER_MODE_SILENCE_ACTION"
      android.intent.action.USER_INITIALIZE:
        558a5d6 com.android.settings/.SettingsInitialize filter 2ca0057
          Action: "android.intent.action.USER_INITIALIZE"
          Action: "android.intent.action.PRE_BOOT_COMPLETED"
      android.bluetooth.device.action.PAIRING_REQUEST:
        2914962 com.android.settings/.bluetooth.BluetoothPairingRequest filter 44af3
          Action: "android.bluetooth.device.action.PAIRING_REQUEST"
          Action: "android.bluetooth.action.CSIS_SET_MEMBER_AVAILABLE"
      android.provider.Contacts.PROFILE_CHANGED:
        1a2cf12 com.android.settings/.users.ProfileUpdateReceiver filter 755d6e3
          Action: "android.provider.Contacts.PROFILE_CHANGED"
      settings.intelligence.battery.action.FETCH_BLUETOOTH_BATTERY_DATA:
        8369b03 com.android.settings/com.google.android.settings.fuelgauge.BatteryBroadcastReceiver filter 9cd1a80
          Action: "settings.intelligence.battery.action.FETCH_BLUETOOTH_BATTERY_DATA"
      com.google.android.settings.action.UPDATE_CARRIER_APP_LIST:
        96778b9 com.android.settings/com.google.android.settings.vpn2.AppBypassBroadcastReceiver filter fecf4fe
          Action: "com.google.android.settings.action.NOTIFY_PACKAGE_ADDED"
          Action: "com.google.android.settings.action.UPDATE_CARRIER_APP_LIST"
          Action: "com.google.android.settings.action.UPDATE_PREDEFINED_APP_EXCLUSION_LIST"
          Action: "com.google.android.settings.action.REMOVE_UNINSTALLED_APP"
      com.google.android.settings.action.UPDATE_PREDEFINED_APP_EXCLUSION_LIST:
        96778b9 com.android.settings/com.google.android.settings.vpn2.AppBypassBroadcastReceiver filter fecf4fe
          Action: "com.google.android.settings.action.NOTIFY_PACKAGE_ADDED"
          Action: "com.google.android.settings.action.UPDATE_CARRIER_APP_LIST"
          Action: "com.google.android.settings.action.UPDATE_PREDEFINED_APP_EXCLUSION_LIST"
          Action: "com.google.android.settings.action.REMOVE_UNINSTALLED_APP"
      com.google.android.setupwizard.SETUP_WIZARD_FINISHED:
        4fde45f com.android.settings/.sim.receivers.SuwFinishReceiver filter c295eac
          Action: "com.google.android.setupwizard.SETUP_WIZARD_FINISHED"
        85ea2ba com.android.settings/.fuelgauge.batteryusage.BootBroadcastReceiver filter bbc256b
          Action: "com.google.android.setupwizard.SETUP_WIZARD_FINISHED"
          Action: "com.android.settings.battery.action.PERIODIC_JOB_RECHECK"
          Action: "android.intent.action.BOOT_COMPLETED"
      androidx.profileinstaller.action.INSTALL_PROFILE:
        d7de775 com.android.settings/androidx.profileinstaller.ProfileInstallReceiver filter 49f630a
          Action: "androidx.profileinstaller.action.INSTALL_PROFILE"
      com.android.settings.battery.action.PERIODIC_JOB_RECHECK:
        85ea2ba com.android.settings/.fuelgauge.batteryusage.BootBroadcastReceiver filter bbc256b
          Action: "com.google.android.setupwizard.SETUP_WIZARD_FINISHED"
          Action: "com.android.settings.battery.action.PERIODIC_JOB_RECHECK"
          Action: "android.intent.action.BOOT_COMPLETED"
      com.google.android.settings.action.REMOVE_UNINSTALLED_APP:
        96778b9 com.android.settings/com.google.android.settings.vpn2.AppBypassBroadcastReceiver filter fecf4fe
          Action: "com.google.android.settings.action.NOTIFY_PACKAGE_ADDED"
          Action: "com.google.android.settings.action.UPDATE_CARRIER_APP_LIST"
          Action: "com.google.android.settings.action.UPDATE_PREDEFINED_APP_EXCLUSION_LIST"
          Action: "com.google.android.settings.action.REMOVE_UNINSTALLED_APP"
      androidx.profileinstaller.action.SKIP_FILE:
        d7de775 com.android.settings/androidx.profileinstaller.ProfileInstallReceiver filter bc6677b
          Action: "androidx.profileinstaller.action.SKIP_FILE"
      android.bluetooth.intent.DISCOVERABLE_TIMEOUT:
        5509974 com.android.settings/com.android.settingslib.bluetooth.BluetoothDiscoverableTimeoutReceiver filter 5cade9d
          Action: "android.bluetooth.intent.DISCOVERABLE_TIMEOUT"
      com.android.settings.SEARCH_EXIT:
        666d744 com.android.settings/.search.SearchStateReceiver filter 1f8902d
          Action: "com.android.settings.SEARCH_START"
          Action: "com.android.settings.SEARCH_EXIT"
      androidx.profileinstaller.action.BENCHMARK_OPERATION:
        d7de775 com.android.settings/androidx.profileinstaller.ProfileInstallReceiver filter 45285f1
          Action: "androidx.profileinstaller.action.BENCHMARK_OPERATION"
      android.intent.action.PRE_BOOT_COMPLETED:
        558a5d6 com.android.settings/.SettingsInitialize filter 2ca0057
          Action: "android.intent.action.USER_INITIALIZE"
          Action: "android.intent.action.PRE_BOOT_COMPLETED"
      android.intent.action.BOOT_COMPLETED:
        85ea2ba com.android.settings/.fuelgauge.batteryusage.BootBroadcastReceiver filter bbc256b
          Action: "com.google.android.setupwizard.SETUP_WIZARD_FINISHED"
          Action: "com.android.settings.battery.action.PERIODIC_JOB_RECHECK"
          Action: "android.intent.action.BOOT_COMPLETED"
        e44b8c8 com.android.settings/.fuelgauge.BatterySettingsMigrateChecker filter 63fcd61
          Action: "android.intent.action.BOOT_COMPLETED"
        d5aca5e com.android.settings/.fuelgauge.batterytip.AnomalyConfigReceiver filter c04fe3f
          Action: "android.intent.action.BOOT_COMPLETED"
          Action: "android.app.action.STATSD_STARTED"
        cfbe3f8 com.android.settings/.sim.receivers.SimCompleteBootReceiver filter 85d0d1
          Action: "android.intent.action.BOOT_COMPLETED"
        13fc736 com.android.settings/.safetycenter.SafetySourceBroadcastReceiver filter 9e7637
          Action: "android.intent.action.BOOT_COMPLETED"
          Action: "android.safetycenter.action.REFRESH_SAFETY_SOURCES"
      android.bluetooth.action.CSIS_SET_MEMBER_AVAILABLE:
        2914962 com.android.settings/.bluetooth.BluetoothPairingRequest filter 44af3
          Action: "android.bluetooth.device.action.PAIRING_REQUEST"
          Action: "android.bluetooth.action.CSIS_SET_MEMBER_AVAILABLE"
      com.android.settings.action.LAUNCH_BLUETOOTH_PAIRING:
        751a30c com.android.settings/.media.BluetoothPairingReceiver filter 4b84455
          Action: "com.android.settings.action.LAUNCH_BLUETOOTH_PAIRING"
      com.android.settings.battery.action.ACTION_BATTERY_UNPLUGGING:
        797cadc com.android.settings/.fuelgauge.batteryusage.BatteryUsageBroadcastReceiver filter d9897e5
          Action: "com.android.settings.battery.action.ACTION_BATTERY_PLUGGING"
          Action: "android.intent.action.BATTERY_LEVEL_CHANGED"
          Action: "com.android.settings.battery.action.ACTION_BATTERY_UNPLUGGING"
          Action: "com.android.settings.battery.action.CLEAR_BATTERY_CACHE_DATA"
      com.android.settings.battery.action.CLEAR_BATTERY_CACHE_DATA:
        797cadc com.android.settings/.fuelgauge.batteryusage.BatteryUsageBroadcastReceiver filter d9897e5
          Action: "com.android.settings.battery.action.ACTION_BATTERY_PLUGGING"
          Action: "android.intent.action.BATTERY_LEVEL_CHANGED"
          Action: "com.android.settings.battery.action.ACTION_BATTERY_UNPLUGGING"
          Action: "com.android.settings.battery.action.CLEAR_BATTERY_CACHE_DATA"
      android.app.action.STATSD_STARTED:
        d5aca5e com.android.settings/.fuelgauge.batterytip.AnomalyConfigReceiver filter c04fe3f
          Action: "android.intent.action.BOOT_COMPLETED"
          Action: "android.app.action.STATSD_STARTED"
      android.safetycenter.action.REFRESH_SAFETY_SOURCES:
        13fc736 com.android.settings/.safetycenter.SafetySourceBroadcastReceiver filter 9e7637
          Action: "android.intent.action.BOOT_COMPLETED"
          Action: "android.safetycenter.action.REFRESH_SAFETY_SOURCES"

Service Resolver Table:
  Non-Data Actions:
      android.service.quicksettings.action.QS_TILE:
        b09e73c com.android.settings/.development.qstile.DevelopmentTiles$ShowLayout filter c13ecc5 permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        bfe061a com.android.settings/.development.qstile.DevelopmentTiles$GPUProfiling filter 320b54b permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        f2c3b28 com.android.settings/.development.qstile.DevelopmentTiles$ForceRTL filter 8cb9041 permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        7e669e6 com.android.settings/.development.qstile.DevelopmentTiles$AnimationSpeed filter f435b27 permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        c9de1d4 com.android.settings/.development.qstile.DevelopmentTiles$WinscopeTrace filter 7ffef7d permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        a9f3e72 com.android.settings/.development.qstile.DevelopmentTiles$SensorsOff filter 90082c3 permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        2e14740 com.android.settings/.development.qstile.DevelopmentTiles$WirelessDebugging filter 9210679 permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        d9ecfbe com.android.settings/.development.qstile.DevelopmentTiles$ShowTaps filter ade881f permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"
        533976c com.android.settings/.development.qstile.DevelopmentTiles$DesktopMode filter 8a29135 permission android.permission.BIND_QUICK_SETTINGS_TILE
          Action: "android.service.quicksettings.action.QS_TILE"

Provider Resolver Table:
  Non-Data Actions:
      android.content.action.SETTINGS_HOMEPAGE_DATA:
        87c870e com.android.settings/.homepage.contextualcards.SettingsContextualCardProvider filter fff52f
          Action: "android.content.action.SETTINGS_HOMEPAGE_DATA"
      com.android.settings.action.SUGGESTION_STATE_PROVIDER:
        a433a10 com.android.settings/.dashboard.suggestions.SuggestionStateProvider filter 2b0c909
          Action: "com.android.settings.action.SUGGESTION_STATE_PROVIDER"
      android.content.action.SEARCH_INDEXABLES_PROVIDER:
        eb920c2 com.android.settings/.search.SettingsSearchIndexablesProvider filter 4da3ed3
          Action: "android.content.action.SEARCH_INDEXABLES_PROVIDER"

Domain verification status:

Permissions:
  Permission [com.google.android.settings.future.logging.RESTRICTED_SEND_FUTURE_LOGS] (daf37e5):
    sourcePackage=com.android.settings
    uid=1000 gids=[] type=0 prot=signature|privileged
    perm=PermissionInfo{6c0c2ba com.google.android.settings.future.logging.RESTRICTED_SEND_FUTURE_LOGS}
    flags=0x0

Permissions:
  Permission [com.android.settings.BATTERY_DATA] (143c56b):
    sourcePackage=com.android.settings
    uid=1000 gids=[] type=0 prot=signature|privileged
    perm=PermissionInfo{bc3d8c8 com.android.settings.BATTERY_DATA}
    flags=0x0

Permissions:
  Permission [com.google.android.settings.setup.dock.RUN_DOCK_SETUP] (1206d61):
    sourcePackage=com.android.settings
    uid=1000 gids=[] type=0 prot=signature|privileged
    perm=PermissionInfo{6285086 com.google.android.settings.setup.dock.RUN_DOCK_SETUP}
    flags=0x0

Permissions:
  Permission [com.google.android.settings.fuelgauge.BATTERY_SETTING] (5574d47):
    sourcePackage=com.android.settings
    uid=1000 gids=[] type=0 prot=signature|privileged
    perm=PermissionInfo{ba1b974 com.google.android.settings.fuelgauge.BATTERY_SETTING}
    flags=0x0

Permissions:
  Permission [com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION] (e157e9d):
    sourcePackage=com.android.settings
    uid=1000 gids=[] type=0 prot=signature
    perm=PermissionInfo{628ef12 com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION}
    flags=0x0

Permissions:
  Permission [com.google.android.settings.routines.ROUTINES_ACTIONS] (23176e3):
    sourcePackage=com.android.settings
    uid=1000 gids=[] type=0 prot=signature|privileged
    perm=PermissionInfo{7daf8e0 com.google.android.settings.routines.ROUTINES_ACTIONS}
    flags=0x0

Registered ContentProviders:
  com.android.settings/.homepage.contextualcards.SettingsContextualCardProvider:
    Provider{87c870e com.android.settings/.homepage.contextualcards.SettingsContextualCardProvider}
  com.android.settings/.emergency.EmergencyActionContentProvider:
    Provider{d506799 com.android.settings/.emergency.EmergencyActionContentProvider}
  com.android.settings/.dashboard.SummaryProvider:
    Provider{422ea5e com.android.settings/.dashboard.SummaryProvider}
  com.android.settings/.slices.SettingsSliceProvider:
    Provider{8fa9e3f com.android.settings/.slices.SettingsSliceProvider}
  com.android.settings/.dashboard.suggestions.SuggestionStateProvider:
    Provider{a433a10 com.android.settings/.dashboard.suggestions.SuggestionStateProvider}
  com.android.settings/.fuelgauge.batteryusage.BatteryUsageContentProvider:
    Provider{2a6c30c com.android.settings/.fuelgauge.batteryusage.BatteryUsageContentProvider}
  com.android.settings/.deviceinfo.legal.ModuleLicenseProvider:
    Provider{7b6e455 com.android.settings/.deviceinfo.legal.ModuleLicenseProvider}
  com.android.settings/com.android.settingslib.spa.search.SpaSearchProvider:
    Provider{12f4e6a com.android.settings/com.android.settingslib.spa.search.SpaSearchProvider}
  com.android.settings/com.google.android.settings.vpn2.AdvancedVpnContentProvider:
    Provider{b04df5b com.android.settings/com.google.android.settings.vpn2.AdvancedVpnContentProvider}
  com.android.settings/.fuelgauge.batteryusage.bugreport.BugReportContentProvider:
    Provider{88303f8 com.android.settings/.fuelgauge.batteryusage.bugreport.BugReportContentProvider}
  com.android.settings/com.google.android.settings.bugreport.DumpDataContentProvider:
    Provider{4ce70d1 com.android.settings/com.google.android.settings.bugreport.DumpDataContentProvider}
  com.android.settings/com.google.android.settings.external.ExternalSettingsProvider:
    Provider{4ebe736 com.android.settings/com.google.android.settings.external.ExternalSettingsProvider}
  com.android.settings/.search.SettingsSearchIndexablesProvider:
    Provider{eb920c2 com.android.settings/.search.SettingsSearchIndexablesProvider}
  com.android.settings/androidx.core.content.FileProvider:
    Provider{2a81637 com.android.settings/androidx.core.content.FileProvider}
  com.android.settings/.homepage.contextualcards.CardContentProvider:
    Provider{de067a4 com.android.settings/.homepage.contextualcards.CardContentProvider}
  com.android.settings/com.google.android.settings.fuelgauge.BatteryUsageContentProvider:
    Provider{4f8490d com.android.settings/com.google.android.settings.fuelgauge.BatteryUsageContentProvider}

ContentProvider Authorities:
  [com.android.settings.module_licenses]:
    Provider{7b6e455 com.android.settings/.deviceinfo.legal.ModuleLicenseProvider}
      applicationInfo=ApplicationInfo{10740c2 com.android.settings}
  [android.settings.slices]:
    Provider{8fa9e3f com.android.settings/.slices.SettingsSliceProvider}
      applicationInfo=ApplicationInfo{dddded3 com.android.settings}
  [com.android.settings.homepage.CardContentProvider]:
    Provider{de067a4 com.android.settings/.homepage.contextualcards.CardContentProvider}
      applicationInfo=ApplicationInfo{b8e5a10 com.android.settings}
  [com.google.android.settings.bugreport.DumpDataContentProvider]:
    Provider{4ce70d1 com.android.settings/com.google.android.settings.bugreport.DumpDataContentProvider}
      applicationInfo=ApplicationInfo{36d6909 com.android.settings}
  [com.android.settings.files]:
    Provider{2a81637 com.android.settings/androidx.core.content.FileProvider}
      applicationInfo=ApplicationInfo{18ca70e com.android.settings}
  [com.android.settings.battery.usage.bugreport]:
    Provider{88303f8 com.android.settings/.fuelgauge.batteryusage.bugreport.BugReportContentProvider}
      applicationInfo=ApplicationInfo{69d952f com.android.settings}
  [com.android.settings.slices]:
    Provider{8fa9e3f com.android.settings/.slices.SettingsSliceProvider}
      applicationInfo=ApplicationInfo{5e7073c com.android.settings}
  [com.android.settings.homepage.contextualcards]:
    Provider{87c870e com.android.settings/.homepage.contextualcards.SettingsContextualCardProvider}
      applicationInfo=ApplicationInfo{bfa8cc5 com.android.settings}
  [com.google.android.settings.AdvancedVpnContentProvider]:
    Provider{b04df5b com.android.settings/com.google.android.settings.vpn2.AdvancedVpnContentProvider}
      applicationInfo=ApplicationInfo{5f0261a com.android.settings}
  [com.google.android.settings.external]:
    Provider{4ebe736 com.android.settings/com.google.android.settings.external.ExternalSettingsProvider}
      applicationInfo=ApplicationInfo{4f8554b com.android.settings}
  [com.android.settings]:
    Provider{eb920c2 com.android.settings/.search.SettingsSearchIndexablesProvider}
      applicationInfo=ApplicationInfo{abb5b28 com.android.settings}
  [com.android.settings.battery.usage.provider]:
    Provider{2a6c30c com.android.settings/.fuelgauge.batteryusage.BatteryUsageContentProvider}
      applicationInfo=ApplicationInfo{7c3041 com.android.settings}
  [com.android.settings.dashboard.SummaryProvider]:
    Provider{422ea5e com.android.settings/.dashboard.SummaryProvider}
      applicationInfo=ApplicationInfo{eda89e6 com.android.settings}
  [com.android.settings.suggestions.status]:
    Provider{a433a10 com.android.settings/.dashboard.suggestions.SuggestionStateProvider}
      applicationInfo=ApplicationInfo{6f4fb27 com.android.settings}
  [com.android.settings.emergency]:
    Provider{d506799 com.android.settings/.emergency.EmergencyActionContentProvider}
      applicationInfo=ApplicationInfo{1ff01d4 com.android.settings}
  [com.android.settings.spa.search.provider]:
    Provider{12f4e6a com.android.settings/com.android.settingslib.spa.search.SpaSearchProvider}
      applicationInfo=ApplicationInfo{a1a8f7d com.android.settings}
  [com.google.android.settings.fuelgauge.provider]:
    Provider{4f8490d com.android.settings/com.google.android.settings.fuelgauge.BatteryUsageContentProvider}
      applicationInfo=ApplicationInfo{cb55e72 com.android.settings}

Key Set Manager:
  [com.android.settings]
      Signing KeySets: 2

Packages:
  Package [com.android.settings] (3de186d):
    appId=1000
    sharedUser=SharedUserSetting{a2c22c3 android.uid.system/1000}
    pkg=Package{d346740 com.android.settings}
    codePath=/system_ext/priv-app/SettingsGoogle
    resourcePath=/system_ext/priv-app/SettingsGoogle
    legacyNativeLibraryDir=/system_ext/priv-app/SettingsGoogle/lib
    extractNativeLibs=true
    primaryCpuAbi=arm64-v8a
    secondaryCpuAbi=null
    cpuAbiOverride=null
    versionCode=34 minSdk=34 targetSdk=34
    minExtensionVersions=[]
    versionName=14
    usesNonSdkApi=true
    splits=[base]
    apkSigningVersion=3
    flags=[ SYSTEM HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP KILL_AFTER_RESTORE ]
    privateFlags=[ PRIVATE_FLAG_ACTIVITIES_RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION ALLOW_AUDIO_PLAYBACK_CAPTURE DEFAULT_TO_DEVICE_PROTECTED_STORAGE DIRECT_BOOT_AWARE PARTIALLY_DIRECT_BOOT_AWARE PRIVILEGED SYSTEM_EXT PRIVATE_FLAG_ALLOW_NATIVE_HEAP_POINTER_TAGGING ]
    forceQueryable=false
    queriesIntents=[Intent { act=com.android.setupwizard.action.PARTNER_CUSTOMIZATION }]
    dataDir=/data/user_de/0/com.android.settings
    supportsScreens=[small, medium, large, xlarge, resizeable, anyDensity]
    usesLibraries:
      org.apache.http.legacy
    usesOptionalLibraries:
      androidx.window.extensions
      androidx.window.sidecar
    usesLibraryFiles:
      /system/framework/org.apache.http.legacy.jar
      /system_ext/framework/androidx.window.extensions.jar
      /system_ext/framework/androidx.window.sidecar.jar
    timeStamp=2024-07-12 02:51:06
    lastUpdateTime=2024-07-12 02:51:06
    installerPackageName=null
    installerPackageUid=-1
    initiatingPackageName=null
    originatingPackageName=null
    packageSource=0
    appMetadataFilePath=null
    signatures=PackageSignatures{245a679 version:3, signatures:[b2d95fc0], past signatures:[]}
    installPermissionsFixed=false
    pkgFlags=[ SYSTEM HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP KILL_AFTER_RESTORE ]
    privatePkgFlags=[ PRIVATE_FLAG_ACTIVITIES_RESIZE_MODE_RESIZEABLE_VIA_SDK_VERSION ALLOW_AUDIO_PLAYBACK_CAPTURE DEFAULT_TO_DEVICE_PROTECTED_STORAGE DIRECT_BOOT_AWARE PARTIALLY_DIRECT_BOOT_AWARE PRIVILEGED SYSTEM_EXT PRIVATE_FLAG_ALLOW_NATIVE_HEAP_POINTER_TAGGING ]
    apexModuleName=null
    declared permissions:
      com.google.android.settings.routines.ROUTINES_ACTIONS: prot=signature|privileged
      com.google.android.settings.future.logging.RESTRICTED_SEND_FUTURE_LOGS: prot=signature|privileged
      com.google.android.settings.setup.dock.RUN_DOCK_SETUP: prot=signature|privileged
      com.google.android.settings.fuelgauge.BATTERY_SETTING: prot=signature|privileged
      com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: prot=signature
      com.android.settings.BATTERY_DATA: prot=signature|privileged
    requested permissions:
      android.permission.MANAGE_GAME_MODE
      android.permission.WAKE_LOCK
      com.google.android.settings.routines.ROUTINES_ACTIONS
      android.permission.PACKAGE_USAGE_STATS
      com.google.android.settings.intelligence.BATTERY_DATA
      com.google.android.settings.setup.dock.RUN_DOCK_SETUP
      android.permission.MANAGE_ACTIVITY_TASKS
      android.permission.USE_FULL_SCREEN_INTENT
      com.google.android.wildlife.permission.VPN_APP_EXCLUSION_LAUNCH
      com.google.android.wildlife.permission.ADVANCED_VPN_CONFIG
      com.google.android.apps.scone.speedboost.settings.READ_PREFERENCES
      android.permission.MANAGE_USERS
      com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION
      android.permission.WRITE_EXTERNAL_STORAGE
      android.permission.READ_PHONE_STATE
      android.permission.READ_EXTERNAL_STORAGE
      android.permission.REQUEST_NETWORK_SCORES
      android.permission.WRITE_MEDIA_STORAGE
      android.permission.MANAGE_EXTERNAL_STORAGE
      android.permission.READ_MEDIA_IMAGES
      android.permission.READ_MEDIA_VIDEO
      android.permission.READ_MEDIA_AUDIO
      android.permission.WRITE_SETTINGS
      android.permission.WRITE_SECURE_SETTINGS
      android.permission.DEVICE_POWER
      android.permission.CHANGE_CONFIGURATION
      android.permission.CONTROL_UI_TRACING
      android.permission.MOUNT_UNMOUNT_FILESYSTEMS
      android.permission.VIBRATE
      android.permission.BLUETOOTH_ADVERTISE
      android.permission.BLUETOOTH_CONNECT
      android.permission.BLUETOOTH_SCAN
      android.permission.BLUETOOTH_PRIVILEGED
      android.permission.NFC
      android.permission.HARDWARE_TEST
      android.permission.CALL_PHONE
      android.permission.MODIFY_AUDIO_SETTINGS
      android.permission.QUERY_AUDIO_STATE
      android.permission.MASTER_CLEAR
      com.google.android.googleapps.permission.GOOGLE_AUTH
      android.permission.ACCESS_DOWNLOAD_MANAGER
      android.permission.READ_CONTACTS
      android.permission.WRITE_CONTACTS
      android.permission.ACCESS_NETWORK_STATE
      android.permission.LOCAL_MAC_ADDRESS
      android.permission.ACCESS_WIFI_STATE
      com.android.certinstaller.INSTALL_AS_USER
      android.permission.CHANGE_WIFI_STATE
      android.permission.TETHER_PRIVILEGED
      android.permission.FOREGROUND_SERVICE
      android.permission.INTERNET
      android.permission.CLEAR_APP_USER_DATA
      android.permission.READ_PRIVILEGED_PHONE_STATE
      android.permission.MODIFY_PHONE_STATE
      android.permission.READ_PHONE_NUMBERS
      android.permission.USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER
      android.permission.ACCESS_FINE_LOCATION
      android.permission.WRITE_APN_SETTINGS
      android.permission.ACCESS_CHECKIN_PROPERTIES
      android.permission.READ_USER_DICTIONARY
      android.permission.WRITE_USER_DICTIONARY
      android.permission.FORCE_STOP_PACKAGES
      android.permission.BATTERY_STATS
      com.android.launcher.permission.READ_SETTINGS
      com.android.launcher.permission.WRITE_SETTINGS
      android.permission.MOVE_PACKAGE
      android.permission.USE_CREDENTIALS
      android.permission.BACKUP
      android.permission.READ_SYNC_STATS
      android.permission.READ_SYNC_SETTINGS
      android.permission.WRITE_SYNC_SETTINGS
      android.permission.READ_DEVICE_CONFIG
      android.permission.STATUS_BAR
      android.permission.MANAGE_USB
      android.permission.MANAGE_DEBUGGING
      android.permission.SET_POINTER_SPEED
      android.permission.SET_KEYBOARD_LAYOUT
      android.permission.INTERACT_ACROSS_USERS_FULL
      android.permission.COPY_PROTECTED_DATA
      android.permission.MANAGE_PROFILE_AND_DEVICE_OWNERS
      android.permission.READ_PROFILE
      android.permission.CONFIGURE_WIFI_DISPLAY
      android.permission.CONFIGURE_DISPLAY_COLOR_MODE
      android.permission.CONTROL_DISPLAY_COLOR_TRANSFORMS
      android.permission.SUGGEST_MANUAL_TIME_AND_ZONE
      android.permission.ACCESS_NOTIFICATIONS
      android.permission.REBOOT
      android.permission.RECEIVE_BOOT_COMPLETED
      android.permission.MANAGE_DEVICE_ADMINS
      android.permission.READ_SEARCH_INDEXABLES
      android.permission.BIND_SETTINGS_SUGGESTIONS_SERVICE
      android.permission.BIND_REMOTE_LOCKSCREEN_VALIDATION_SERVICE
      android.permission.OEM_UNLOCK_STATE
      android.permission.MANAGE_USER_OEM_UNLOCK_STATE
      android.permission.OVERRIDE_WIFI_CONFIG
      android.permission.RESTART_WIFI_SUBSYSTEM
      android.permission.MANAGE_FINGERPRINT
      android.permission.USE_BIOMETRIC
      android.permission.USE_BIOMETRIC_INTERNAL
      android.permission.USER_ACTIVITY
      android.permission.CHANGE_APP_IDLE_STATE
      android.permission.PEERS_MAC_ADDRESS
      android.permission.MANAGE_NOTIFICATIONS
      android.permission.DELETE_PACKAGES
      android.permission.REQUEST_DELETE_PACKAGES
      android.permission.MANAGE_APP_OPS_RESTRICTIONS
      android.permission.MANAGE_APP_OPS_MODES
      android.permission.HIDE_NON_SYSTEM_OVERLAY_WINDOWS
      android.permission.READ_PRINT_SERVICES
      android.permission.NETWORK_SETTINGS
      android.permission.TEST_BLACKLISTED_PASSWORD
      android.permission.USE_RESERVED_DISK
      android.permission.MANAGE_SCOPED_ACCESS_DIRECTORY_PERMISSIONS
      android.permission.CAMERA
      android.permission.MEDIA_CONTENT_CONTROL
      android.permission.INSTALL_DYNAMIC_SYSTEM
      android.permission.BIND_CELL_BROADCAST_SERVICE
      android.permission.SYSTEM_ALERT_WINDOW
      android.permission.READ_DREAM_STATE
      android.permission.READ_DREAM_SUPPRESSION
      android.permission.MANAGE_APP_HIBERNATION
      android.permission.LAUNCH_MULTI_PANE_SETTINGS_DEEP_LINK
      android.permission.ALLOW_PLACE_IN_MULTI_PANE_SETTINGS
      android.permission.POST_NOTIFICATIONS
      android.permission.READ_APP_SPECIFIC_LOCALES
      android.permission.QUERY_ADMIN_POLICY
      android.permission.READ_SAFETY_CENTER_STATUS
      android.permission.SEND_SAFETY_CENTER_UPDATE
      android.permission.START_VIEW_APP_FEATURES
      android.permission.LIST_ENABLED_CREDENTIAL_PROVIDERS
      android.permission.CUSTOMIZE_SYSTEM_UI
      android.permission.REMAP_MODIFIER_KEYS
      android.permission.ACCESS_GPU_SERVICE
      android.permission.ACCESS_COARSE_LOCATION
      android.permission.READ_MEDIA_VISUAL_USER_SELECTED
    install permissions:
      android.permission.ACCESS_GPU_SERVICE: granted=true
      android.permission.BIND_INCALL_SERVICE: granted=true
      android.permission.WRITE_SETTINGS: granted=true
      android.permission.CONFIGURE_WIFI_DISPLAY: granted=true
      android.permission.CONFIGURE_DISPLAY_COLOR_MODE: granted=true
      android.permission.CONTROL_DISPLAY_COLOR_TRANSFORMS: granted=true
      com.android.keychain.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: granted=true
      android.permission.LIST_ENABLED_CREDENTIAL_PROVIDERS: granted=true
      android.permission.BIND_ATTENTION_SERVICE: granted=true
      android.permission.USE_CREDENTIALS: granted=true
      android.permission.MODIFY_AUDIO_SETTINGS: granted=true
      android.permission.MANAGE_EXTERNAL_STORAGE: granted=true
      android.permission.ACCESS_CHECKIN_PROPERTIES: granted=true
      android.permission.REMAP_MODIFIER_KEYS: granted=true
      android.permission.MODIFY_AUDIO_ROUTING: granted=true
      android.permission.READ_SAFETY_CENTER_STATUS: granted=true
      android.permission.QUERY_AUDIO_STATE: granted=true
      android.permission.INSTALL_LOCATION_PROVIDER: granted=true
      android.permission.USE_RESERVED_DISK: granted=true
      android.permission.SYSTEM_ALERT_WINDOW: granted=true
      android.permission.BROADCAST_PHONE_ACCOUNT_REGISTRATION: granted=true
      android.permission.CLEAR_APP_USER_DATA: granted=true
      android.permission.BROADCAST_CALLLOG_INFO: granted=true
      android.permission.CONTROL_UI_TRACING: granted=true
      android.permission.NFC: granted=true
      android.permission.BIND_ROTATION_RESOLVER_SERVICE: granted=true
      android.permission.NETWORK_SETTINGS: granted=true
      android.permission.CALL_PRIVILEGED: granted=true
      android.permission.MASTER_CLEAR: granted=true
      android.permission.FOREGROUND_SERVICE: granted=true
      android.permission.WRITE_SYNC_SETTINGS: granted=true
      android.permission.READ_INSTALLED_SESSION_PATHS: granted=true
      android.permission.ALLOW_PLACE_IN_MULTI_PANE_SETTINGS: granted=true
      android.permission.MANAGE_DYNAMIC_SYSTEM: granted=true
      android.permission.LAUNCH_MULTI_PANE_SETTINGS_DEEP_LINK: granted=true
      android.permission.MANAGE_ACTIVITY_TASKS: granted=true
      android.permission.RECEIVE_BOOT_COMPLETED: granted=true
      com.google.android.googleapps.permission.GOOGLE_AUTH: granted=true
      android.permission.MANAGE_ROLE_HOLDERS: granted=true
      android.permission.PEERS_MAC_ADDRESS: granted=true
      android.permission.DEVICE_POWER: granted=true
      android.permission.ENFORCE_UPDATE_OWNERSHIP: granted=true
      android.permission.READ_PRINT_SERVICES: granted=true
      android.permission.MANAGE_PROFILE_AND_DEVICE_OWNERS: granted=true
      android.permission.USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER: granted=true
      android.permission.RESTART_WIFI_SUBSYSTEM: granted=true
      android.permission.READ_PROFILE: granted=true
      android.permission.BLUETOOTH: granted=true
      android.permission.WRITE_MEDIA_STORAGE: granted=true
      android.permission.WRITE_BLOCKED_NUMBERS: granted=true
      android.permission.BIND_REMOTE_LOCKSCREEN_VALIDATION_SERVICE: granted=true
      android.permission.INTERNET: granted=true
      android.permission.UPDATE_PACKAGES_WITHOUT_USER_ACTION: granted=true
      android.permission.BLUETOOTH_ADMIN: granted=true
      android.permission.CONTROL_VPN: granted=true
      android.permission.UPDATE_DEVICE_STATS: granted=true
      android.permission.MANAGE_FINGERPRINT: granted=true
      android.permission.READ_PROJECTION_STATE: granted=true
      android.permission.SEND_SAFETY_CENTER_UPDATE: granted=true
      android.permission.BIND_CONNECTION_SERVICE: granted=true
      android.permission.ACCESS_INSTANT_APPS: granted=true
      com.google.android.settings.intelligence.BATTERY_DATA: granted=true
      android.permission.ACCESS_CONTEXT_HUB: granted=true
      android.permission.MANAGE_USB: granted=true
      android.permission.INTERACT_ACROSS_USERS_FULL: granted=true
      android.permission.STOP_APP_SWITCHES: granted=true
      android.permission.BATTERY_STATS: granted=true
      android.permission.PACKAGE_USAGE_STATS: granted=true
      android.permission.MOUNT_UNMOUNT_FILESYSTEMS: granted=true
      android.permission.TETHER_PRIVILEGED: granted=true
      android.permission.WRITE_SECURE_SETTINGS: granted=true
      android.permission.FOREGROUND_SERVICE_SYSTEM_EXEMPTED: granted=true
      android.permission.MANAGE_DEBUGGING: granted=true
      android.permission.MOVE_PACKAGE: granted=true
      android.permission.READ_BLOCKED_NUMBERS: granted=true
      android.permission.STATUS_BAR_SERVICE: granted=true
      android.permission.READ_SEARCH_INDEXABLES: granted=true
      com.google.android.settings.setup.dock.RUN_DOCK_SETUP: granted=true
      android.permission.USE_FULL_SCREEN_INTENT: granted=true
      android.permission.READ_PRIVILEGED_PHONE_STATE: granted=true
      android.permission.ACCESS_DOWNLOAD_MANAGER: granted=true
      android.permission.BLUETOOTH_PRIVILEGED: granted=true
      android.permission.HARDWARE_TEST: granted=true
      android.permission.USE_BIOMETRIC_INTERNAL: granted=true
      android.permission.INSTALL_DYNAMIC_SYSTEM: granted=true
      android.permission.SUBSTITUTE_NOTIFICATION_APP_NAME: granted=true
      android.intent.category.MASTER_CLEAR.permission.C2D_MESSAGE: granted=true
      android.permission.BIND_JOB_SERVICE: granted=true
      android.permission.CONFIRM_FULL_BACKUP: granted=true
      android.permission.WRITE_APN_SETTINGS: granted=true
      android.permission.CHANGE_WIFI_STATE: granted=true
      android.permission.MANAGE_USERS: granted=true
      android.permission.ACCESS_NETWORK_STATE: granted=true
      android.permission.BACKUP: granted=true
      android.permission.CHANGE_CONFIGURATION: granted=true
      android.permission.USER_ACTIVITY: granted=true
      android.permission.LOCAL_MAC_ADDRESS: granted=true
      android.permission.READ_LOGS: granted=true
      android.permission.COPY_PROTECTED_DATA: granted=true
      android.permission.INTERACT_ACROSS_USERS: granted=true
      android.permission.SET_KEYBOARD_LAYOUT: granted=true
      android.permission.BROADCAST_CLOSE_SYSTEM_DIALOGS: granted=true
      android.permission.READ_DREAM_STATE: granted=true
      android.permission.START_VIEW_APP_FEATURES: granted=true
      android.permission.HANDLE_QUERY_PACKAGE_RESTART: granted=true
      android.permission.MANAGE_APP_OPS_RESTRICTIONS: granted=true
      android.permission.MANAGE_USER_OEM_UNLOCK_STATE: granted=true
      com.android.phone.permission.ACCESS_LAST_KNOWN_CELL_ID: granted=true
      android.permission.REQUEST_NETWORK_SCORES: granted=true
      android.permission.CONNECTIVITY_USE_RESTRICTED_NETWORKS: granted=true
      android.permission.WRITE_USER_DICTIONARY: granted=true
      android.permission.READ_DREAM_SUPPRESSION: granted=true
      android.permission.READ_SYNC_STATS: granted=true
      android.permission.REBOOT: granted=true
      android.permission.REQUEST_DELETE_PACKAGES: granted=true
      android.permission.OEM_UNLOCK_STATE: granted=true
      android.permission.MANAGE_DEVICE_ADMINS: granted=true
      android.permission.CHANGE_APP_IDLE_STATE: granted=true
      android.permission.BIND_SETTINGS_SUGGESTIONS_SERVICE: granted=true
      android.permission.TEST_BLACKLISTED_PASSWORD: granted=true
      android.permission.MANAGE_NOTIFICATION_LISTENERS: granted=true
      android.permission.SET_POINTER_SPEED: granted=true
      android.permission.MANAGE_NOTIFICATIONS: granted=true
      android.permission.USE_COLORIZED_NOTIFICATIONS: granted=true
      android.permission.MANAGE_GAME_MODE: granted=true
      android.permission.SEND_SHOW_SUSPENDED_APP_DETAILS: granted=true
      android.permission.READ_SYNC_SETTINGS: granted=true
      android.permission.BIND_CELL_BROADCAST_SERVICE: granted=true
      android.permission.LOADER_USAGE_STATS: granted=true
      android.permission.OVERRIDE_WIFI_CONFIG: granted=true
      android.permission.FORCE_STOP_PACKAGES: granted=true
      android.permission.SUGGEST_MANUAL_TIME_AND_ZONE: granted=true
      android.permission.HIDE_NON_SYSTEM_OVERLAY_WINDOWS: granted=true
      android.permission.ACCESS_NOTIFICATIONS: granted=true
      android.permission.HANDLE_CALL_INTENT: granted=true
      android.permission.MEDIA_RESOURCE_OVERRIDE_PID: granted=true
      android.permission.CUSTOMIZE_SYSTEM_UI: granted=true
      android.permission.VIBRATE: granted=true
      com.android.certinstaller.INSTALL_AS_USER: granted=true
      android.permission.MANAGE_APP_HIBERNATION: granted=true
      android.permission.HANDLE_CAR_MODE_CHANGES: granted=true
      android.permission.READ_USER_DICTIONARY: granted=true
      com.android.server.telecom.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: granted=true
      android.permission.MANAGE_SCOPED_ACCESS_DIRECTORY_PERMISSIONS: granted=true
      android.permission.ACCESS_WIFI_STATE: granted=true
      android.permission.READ_APP_SPECIFIC_LOCALES: granted=true
      android.permission.USE_BIOMETRIC: granted=true
      android.permission.MANAGE_APP_OPS_MODES: granted=true
      com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: granted=true
      android.permission.MODIFY_PHONE_STATE: granted=true
      android.permission.STATUS_BAR: granted=true
      android.permission.QUERY_ALL_PACKAGES: granted=true
      com.google.android.settings.routines.ROUTINES_ACTIONS: granted=true
      android.permission.READ_DEVICE_CONFIG: granted=true
      android.permission.LOCATION_HARDWARE: granted=true
      android.permission.UNLIMITED_TOASTS: granted=true
      android.permission.QUERY_ADMIN_POLICY: granted=true
      android.permission.WAKE_LOCK: granted=true
      android.permission.BIND_NETWORK_RECOMMENDATION_SERVICE: granted=true
      android.permission.UPDATE_APP_OPS_STATS: granted=true
      android.permission.READ_OEM_UNLOCK_STATE: granted=true
      android.permission.MEDIA_CONTENT_CONTROL: granted=true
      android.permission.DELETE_PACKAGES: granted=true
    User 0: ceDataInode=311847 installed=true hidden=false suspended=false distractionFlags=0 stopped=false notLaunched=false enabled=0 instant=false virtual=false
      installReason=0
      firstInstallTime=2024-07-12 02:51:06
      uninstallReason=0
      overlay paths:
        /product/overlay/EmulationPixel6/EmulationPixel6Overlay.apk
        /product/overlay/NavigationBarModeGestural/NavigationBarModeGesturalOverlay.apk
        /product/overlay/SettingsGoogle__auto_generated_rro_product.apk
      legacy overlay paths:
        /product/overlay/EmulationPixel6/EmulationPixel6Overlay.apk
        /product/overlay/NavigationBarModeGestural/NavigationBarModeGesturalOverlay.apk
        /product/overlay/SettingsGoogle__auto_generated_rro_product.apk
      disabledComponents:
        com.android.settings.Settings$LanguageAndInputSettingsActivity
      enabledComponents:
        com.android.settings.WebViewImplementation
        com.android.settings.homepage.DeepLinkHomepageActivity
        com.android.settings.search.SearchStateReceiver
        com.android.settings.Settings$LanguageSettingsActivity

Queries:
  system apps queryable: false
  queries via forceQueryable:
  forceQueryable:
    [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
  queries via package name:
  queries via component:
  queryable via interaction:
    User 0:
      [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]:
        [com.android.mms.service,com.android.phone,com.android.providers.telephony,com.android.stk,com.android.ons]
        [com.android.bluetooth,com.google.android.bluetooth]
        [com.google.android.cellbroadcastservice,com.google.android.networkstack.tethering,com.google.android.networkstack]
        [com.android.providers.downloads,com.android.mtp,com.android.soundpicker,com.android.providers.media,com.android.providers.downloads.ui]
        [com.android.calllogbackup,com.android.providers.blockednumber,com.android.providers.userdictionary,com.android.providers.contacts]
        com.android.providers.calendar
        com.android.externalstorage
        com.android.traceur
        com.android.carrierdefaultapp
        com.google.android.partnersetup
        com.google.android.apps.wellbeing
        com.google.android.dialer
        com.google.android.as.oss
        com.google.android.settings.intelligence
        [com.google.android.gsf,com.google.android.gms]
        com.google.android.apps.messaging
        com.google.android.as
        com.google.android.googlequicksearchbox
        com.google.android.gm
        com.google.android.tts
        com.google.android.inputmethod.latin
        com.google.android.contacts
        com.google.android.apps.youtube.music
        com.google.android.youtube
        com.google.android.apps.nexuslauncher
        com.android.systemui
        com.google.android.permissioncontroller
        com.google.android.rkpdapp
        com.google.android.providers.media.module
        com.google.android.ext.services
        com.google.android.cellbroadcastreceiver
        com.google.android.devicelockcontroller
      [com.android.mms.service,com.android.phone,com.android.providers.telephony,com.android.stk,com.android.ons]:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      [com.android.bluetooth,com.google.android.bluetooth]:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      [com.google.android.cellbroadcastservice,com.google.android.networkstack.tethering,com.google.android.networkstack]:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      [com.android.providers.downloads,com.android.mtp,com.android.soundpicker,com.android.providers.media,com.android.providers.downloads.ui]:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      [com.android.calllogbackup,com.android.providers.blockednumber,com.android.providers.userdictionary,com.android.providers.contacts]:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.android.providers.calendar:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.android.printspooler:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.partnersetup:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.apps.wellbeing:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.dialer:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      [com.google.android.gsf,com.google.android.gms]:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.apps.messaging:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.as:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.googlequicksearchbox:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.gm:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.tts:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.inputmethod.latin:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.contacts:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.apps.youtube.music:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.youtube:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.apps.nexuslauncher:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.android.systemui:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.permissioncontroller:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.providers.media.module:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
      com.google.android.ext.services:
        [com.android.dynsystem,com.android.inputdevices,com.android.localtransport,com.android.wallpaperbackup,com.android.settings,com.android.keychain,com.android.location.fused,com.android.emulator.multidisplay,com.android.server.telecom,android,com.android.providers.settings]
  queryable via uses-library:

Shared users:
  SharedUser [android.uid.system] (a2c22c3):
    appId=1000
    Packages
      PackageSetting{180341c com.android.dynsystem/1000}
      PackageSetting{24fcca2 com.android.inputdevices/1000}
      PackageSetting{2824dfa com.android.localtransport/1000}
      PackageSetting{39fad33 com.android.wallpaperbackup/1000}
      PackageSetting{3de186d com.android.settings/1000}
      PackageSetting{41de98f com.android.keychain/1000}
      PackageSetting{a3478f0 com.android.location.fused/1000}
      PackageSetting{c0210ee com.android.emulator.multidisplay/1000}
      PackageSetting{d1ee825 com.android.server.telecom/1000}
      PackageSetting{e998fab android/1000}
      PackageSetting{ed0ce69 com.android.providers.settings/1000}
    install permissions:
      android.permission.ACCESS_GPU_SERVICE: granted=true
      android.permission.BIND_INCALL_SERVICE: granted=true
      android.permission.WRITE_SETTINGS: granted=true
      android.permission.CONFIGURE_WIFI_DISPLAY: granted=true
      android.permission.CONFIGURE_DISPLAY_COLOR_MODE: granted=true
      android.permission.CONTROL_DISPLAY_COLOR_TRANSFORMS: granted=true
      com.android.keychain.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: granted=true
      android.permission.LIST_ENABLED_CREDENTIAL_PROVIDERS: granted=true
      android.permission.BIND_ATTENTION_SERVICE: granted=true
      android.permission.USE_CREDENTIALS: granted=true
      android.permission.MODIFY_AUDIO_SETTINGS: granted=true
      android.permission.MANAGE_EXTERNAL_STORAGE: granted=true
      android.permission.ACCESS_CHECKIN_PROPERTIES: granted=true
      android.permission.REMAP_MODIFIER_KEYS: granted=true
      android.permission.MODIFY_AUDIO_ROUTING: granted=true
      android.permission.READ_SAFETY_CENTER_STATUS: granted=true
      android.permission.QUERY_AUDIO_STATE: granted=true
      android.permission.INSTALL_LOCATION_PROVIDER: granted=true
      android.permission.USE_RESERVED_DISK: granted=true
      android.permission.SYSTEM_ALERT_WINDOW: granted=true
      android.permission.BROADCAST_PHONE_ACCOUNT_REGISTRATION: granted=true
      android.permission.CLEAR_APP_USER_DATA: granted=true
      android.permission.BROADCAST_CALLLOG_INFO: granted=true
      android.permission.CONTROL_UI_TRACING: granted=true
      android.permission.NFC: granted=true
      android.permission.BIND_ROTATION_RESOLVER_SERVICE: granted=true
      android.permission.NETWORK_SETTINGS: granted=true
      android.permission.CALL_PRIVILEGED: granted=true
      android.permission.MASTER_CLEAR: granted=true
      android.permission.FOREGROUND_SERVICE: granted=true
      android.permission.WRITE_SYNC_SETTINGS: granted=true
      android.permission.READ_INSTALLED_SESSION_PATHS: granted=true
      android.permission.ALLOW_PLACE_IN_MULTI_PANE_SETTINGS: granted=true
      android.permission.MANAGE_DYNAMIC_SYSTEM: granted=true
      android.permission.LAUNCH_MULTI_PANE_SETTINGS_DEEP_LINK: granted=true
      android.permission.MANAGE_ACTIVITY_TASKS: granted=true
      android.permission.RECEIVE_BOOT_COMPLETED: granted=true
      com.google.android.googleapps.permission.GOOGLE_AUTH: granted=true
      android.permission.MANAGE_ROLE_HOLDERS: granted=true
      android.permission.PEERS_MAC_ADDRESS: granted=true
      android.permission.DEVICE_POWER: granted=true
      android.permission.ENFORCE_UPDATE_OWNERSHIP: granted=true
      android.permission.READ_PRINT_SERVICES: granted=true
      android.permission.MANAGE_PROFILE_AND_DEVICE_OWNERS: granted=true
      android.permission.USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER: granted=true
      android.permission.RESTART_WIFI_SUBSYSTEM: granted=true
      android.permission.READ_PROFILE: granted=true
      android.permission.BLUETOOTH: granted=true
      android.permission.WRITE_MEDIA_STORAGE: granted=true
      android.permission.WRITE_BLOCKED_NUMBERS: granted=true
      android.permission.BIND_REMOTE_LOCKSCREEN_VALIDATION_SERVICE: granted=true
      android.permission.INTERNET: granted=true
      android.permission.UPDATE_PACKAGES_WITHOUT_USER_ACTION: granted=true
      android.permission.BLUETOOTH_ADMIN: granted=true
      android.permission.CONTROL_VPN: granted=true
      android.permission.UPDATE_DEVICE_STATS: granted=true
      android.permission.MANAGE_FINGERPRINT: granted=true
      android.permission.READ_PROJECTION_STATE: granted=true
      android.permission.SEND_SAFETY_CENTER_UPDATE: granted=true
      android.permission.BIND_CONNECTION_SERVICE: granted=true
      android.permission.ACCESS_INSTANT_APPS: granted=true
      com.google.android.settings.intelligence.BATTERY_DATA: granted=true
      android.permission.ACCESS_CONTEXT_HUB: granted=true
      android.permission.MANAGE_USB: granted=true
      android.permission.INTERACT_ACROSS_USERS_FULL: granted=true
      android.permission.STOP_APP_SWITCHES: granted=true
      android.permission.BATTERY_STATS: granted=true
      android.permission.PACKAGE_USAGE_STATS: granted=true
      android.permission.MOUNT_UNMOUNT_FILESYSTEMS: granted=true
      android.permission.TETHER_PRIVILEGED: granted=true
      android.permission.WRITE_SECURE_SETTINGS: granted=true
      android.permission.FOREGROUND_SERVICE_SYSTEM_EXEMPTED: granted=true
      android.permission.MANAGE_DEBUGGING: granted=true
      android.permission.MOVE_PACKAGE: granted=true
      android.permission.READ_BLOCKED_NUMBERS: granted=true
      android.permission.STATUS_BAR_SERVICE: granted=true
      android.permission.READ_SEARCH_INDEXABLES: granted=true
      com.google.android.settings.setup.dock.RUN_DOCK_SETUP: granted=true
      android.permission.USE_FULL_SCREEN_INTENT: granted=true
      android.permission.READ_PRIVILEGED_PHONE_STATE: granted=true
      android.permission.ACCESS_DOWNLOAD_MANAGER: granted=true
      android.permission.BLUETOOTH_PRIVILEGED: granted=true
      android.permission.HARDWARE_TEST: granted=true
      android.permission.USE_BIOMETRIC_INTERNAL: granted=true
      android.permission.INSTALL_DYNAMIC_SYSTEM: granted=true
      android.permission.SUBSTITUTE_NOTIFICATION_APP_NAME: granted=true
      android.intent.category.MASTER_CLEAR.permission.C2D_MESSAGE: granted=true
      android.permission.BIND_JOB_SERVICE: granted=true
      android.permission.CONFIRM_FULL_BACKUP: granted=true
      android.permission.WRITE_APN_SETTINGS: granted=true
      android.permission.CHANGE_WIFI_STATE: granted=true
      android.permission.MANAGE_USERS: granted=true
      android.permission.ACCESS_NETWORK_STATE: granted=true
      android.permission.BACKUP: granted=true
      android.permission.CHANGE_CONFIGURATION: granted=true
      android.permission.USER_ACTIVITY: granted=true
      android.permission.LOCAL_MAC_ADDRESS: granted=true
      android.permission.READ_LOGS: granted=true
      android.permission.COPY_PROTECTED_DATA: granted=true
      android.permission.INTERACT_ACROSS_USERS: granted=true
      android.permission.SET_KEYBOARD_LAYOUT: granted=true
      android.permission.BROADCAST_CLOSE_SYSTEM_DIALOGS: granted=true
      android.permission.READ_DREAM_STATE: granted=true
      android.permission.START_VIEW_APP_FEATURES: granted=true
      android.permission.HANDLE_QUERY_PACKAGE_RESTART: granted=true
      android.permission.MANAGE_APP_OPS_RESTRICTIONS: granted=true
      android.permission.MANAGE_USER_OEM_UNLOCK_STATE: granted=true
      com.android.phone.permission.ACCESS_LAST_KNOWN_CELL_ID: granted=true
      android.permission.REQUEST_NETWORK_SCORES: granted=true
      android.permission.CONNECTIVITY_USE_RESTRICTED_NETWORKS: granted=true
      android.permission.WRITE_USER_DICTIONARY: granted=true
      android.permission.READ_DREAM_SUPPRESSION: granted=true
      android.permission.READ_SYNC_STATS: granted=true
      android.permission.REBOOT: granted=true
      android.permission.REQUEST_DELETE_PACKAGES: granted=true
      android.permission.OEM_UNLOCK_STATE: granted=true
      android.permission.MANAGE_DEVICE_ADMINS: granted=true
      android.permission.CHANGE_APP_IDLE_STATE: granted=true
      android.permission.BIND_SETTINGS_SUGGESTIONS_SERVICE: granted=true
      android.permission.TEST_BLACKLISTED_PASSWORD: granted=true
      android.permission.MANAGE_NOTIFICATION_LISTENERS: granted=true
      android.permission.SET_POINTER_SPEED: granted=true
      android.permission.MANAGE_NOTIFICATIONS: granted=true
      android.permission.USE_COLORIZED_NOTIFICATIONS: granted=true
      android.permission.MANAGE_GAME_MODE: granted=true
      android.permission.SEND_SHOW_SUSPENDED_APP_DETAILS: granted=true
      android.permission.READ_SYNC_SETTINGS: granted=true
      android.permission.BIND_CELL_BROADCAST_SERVICE: granted=true
      android.permission.LOADER_USAGE_STATS: granted=true
      android.permission.OVERRIDE_WIFI_CONFIG: granted=true
      android.permission.FORCE_STOP_PACKAGES: granted=true
      android.permission.SUGGEST_MANUAL_TIME_AND_ZONE: granted=true
      android.permission.HIDE_NON_SYSTEM_OVERLAY_WINDOWS: granted=true
      android.permission.ACCESS_NOTIFICATIONS: granted=true
      android.permission.HANDLE_CALL_INTENT: granted=true
      android.permission.MEDIA_RESOURCE_OVERRIDE_PID: granted=true
      android.permission.CUSTOMIZE_SYSTEM_UI: granted=true
      android.permission.VIBRATE: granted=true
      com.android.certinstaller.INSTALL_AS_USER: granted=true
      android.permission.MANAGE_APP_HIBERNATION: granted=true
      android.permission.HANDLE_CAR_MODE_CHANGES: granted=true
      android.permission.READ_USER_DICTIONARY: granted=true
      com.android.server.telecom.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: granted=true
      android.permission.MANAGE_SCOPED_ACCESS_DIRECTORY_PERMISSIONS: granted=true
      android.permission.ACCESS_WIFI_STATE: granted=true
      android.permission.READ_APP_SPECIFIC_LOCALES: granted=true
      android.permission.USE_BIOMETRIC: granted=true
      android.permission.MANAGE_APP_OPS_MODES: granted=true
      com.android.settings.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION: granted=true
      android.permission.MODIFY_PHONE_STATE: granted=true
      android.permission.STATUS_BAR: granted=true
      android.permission.QUERY_ALL_PACKAGES: granted=true
      com.google.android.settings.routines.ROUTINES_ACTIONS: granted=true
      android.permission.READ_DEVICE_CONFIG: granted=true
      android.permission.LOCATION_HARDWARE: granted=true
      android.permission.UNLIMITED_TOASTS: granted=true
      android.permission.QUERY_ADMIN_POLICY: granted=true
      android.permission.WAKE_LOCK: granted=true
      android.permission.BIND_NETWORK_RECOMMENDATION_SERVICE: granted=true
      android.permission.UPDATE_APP_OPS_STATS: granted=true
      android.permission.READ_OEM_UNLOCK_STATE: granted=true
      android.permission.MEDIA_CONTENT_CONTROL: granted=true
      android.permission.DELETE_PACKAGES: granted=true
    User 0: 
      gids=[1065, 3002, 3003, 3001, 3007, 1007]
      runtime permissions:
        android.permission.POST_NOTIFICATIONS: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_CALL_LOG: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT|RESTRICTION_UPGRADE_EXEMPT]
        android.permission.ACCESS_FINE_LOCATION: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_PHONE_NUMBERS: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_MEDIA_VISUAL_USER_SELECTED: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.BLUETOOTH_CONNECT: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_EXTERNAL_STORAGE: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT|RESTRICTION_UPGRADE_EXEMPT]
        android.permission.ACCESS_COARSE_LOCATION: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|REVOKE_WHEN_REQUESTED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_PHONE_STATE: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED]
        android.permission.SEND_SMS: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT|RESTRICTION_UPGRADE_EXEMPT]
        android.permission.CALL_PHONE: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_MEDIA_IMAGES: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.WRITE_CONTACTS: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.CAMERA: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.WRITE_CALL_LOG: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT|RESTRICTION_UPGRADE_EXEMPT]
        android.permission.READ_MEDIA_AUDIO: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.READ_MEDIA_VIDEO: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.BLUETOOTH_ADVERTISE: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.GET_ACCOUNTS: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT]
        android.permission.WRITE_EXTERNAL_STORAGE: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT|RESTRICTION_UPGRADE_EXEMPT]
        android.permission.READ_CONTACTS: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT]
        android.permission.ACCESS_BACKGROUND_LOCATION: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|RESTRICTION_SYSTEM_EXEMPT|RESTRICTION_UPGRADE_EXEMPT]
        android.permission.BLUETOOTH_SCAN: granted=true, flags=[ SYSTEM_FIXED|GRANTED_BY_DEFAULT|USER_SENSITIVE_WHEN_GRANTED|USER_SENSITIVE_WHEN_DENIED|RESTRICTION_SYSTEM_EXEMPT]

Dexopt state:
  [com.android.settings]
    path: /system_ext/priv-app/SettingsGoogle/SettingsGoogle.apk
      arm64: [status=verify] [reason=prebuilt] [primary-abi]
        [location is /system_ext/priv-app/SettingsGoogle/oat/arm64/SettingsGoogle.odex]

Compiler stats:
  [com.android.settings]
    (No recorded stats)
```
