# dumpsys 存档：01-activity.md（讲解版）

命令：`adb shell dumpsys activity activities`

**这个服务是什么**：ActivityManagerService（AMS）的 activity 子系统，回答「系统里现在有哪些任务栈（task）、每个栈里有哪些 Activity、谁在前台、焦点在哪」。

**这段输出在讲什么**：模拟器刚 boot 完，只有一个前台 Launcher（`com.google.android.apps.nexuslauncher`）在屏幕上 RESUMED 状态，后面还挂着几个系统预创建的空任务栈。

## 逐段讲解

### 1. 任务栈层级：Display → Task → ActivityRecord

```text
Display #0 (activities from top to bottom):
  * Task{afe9a41 #1 type=home U=0 visible=true ... sz=1}
    * Task{cb9944e #6 type=home I=com.google.android.apps.nexuslauncher/.NexusLauncherActivity U=0 rootTaskId=1 ...}
      topResumedActivity=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
```

**讲解**：三层嵌套是 Android 任务模型的骨架。`Task{#1}` 是**根任务栈**（type=home，放所有 home 类 Activity），里面又嵌了一个 `Task{#6}`（这是 Launcher 具体所在的叶子 task）。`U=0` 是用户 0（主用户）。`topResumedActivity` 就是「当前真正处于 RESUMED、正在交互的那个 Activity」——面试问「现在前台是什么」，就看这一行。

### 2. 前台 Activity 的完整档案

```text
      * Hist  #0: ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
        packageName=com.google.android.apps.nexuslauncher processName=com.google.android.apps.nexuslauncher
        app=ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}
        Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] ... cmp=com.google.android.apps.nexuslauncher/.NexusLauncherActivity }
        baseDir=/system_ext/priv-app/NexusLauncherRelease/NexusLauncherRelease.apk
        dataDir=/data/user/0/com.google.android.apps.nexuslauncher
        state=RESUMED delayedResume=false finishing=false
```

**讲解**：`Hist #0` 是 task 里的 Activity 历史栈顶。注意几个关键字段：
- `Intent{ act=MAIN cat=[HOME] }` —— 它是因为「HOME 键」被拉起的，这就是 Launcher 的启动 Intent。
- `baseDir` 指向 APK 位置（`/system_ext/priv-app`，说明是系统特权应用）。
- `state=RESUMED` —— Activity 生命周期走到了前台交互态。**面试常问 Activity 有哪几种状态，RESUMED 是其中之一（还有 INITIALIZING/CREATED/STARTED/PAUSED/STOPPING/STOPPED/FINISHING/DESTROYING）。**

### 3. 焦点：谁在接收输入

```text
  ResumedActivity: ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
  mCurrentFocus=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
  mFocusedApp=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
```

**讲解**：`mCurrentFocus` 是**窗口焦点**（键盘/触摸输入给谁），`mFocusedApp` 是**应用焦点**。两者通常一致，但弹出输入法或权限弹窗时会分离——「焦点」和「前台」是两个概念。

### 4. 其余部分快速认路（不用逐行读）

- `Display areas in top down Z order` / `Task display areas...`：显示分区和任务分区的 z 顺序，做分屏/画中画才细看。
- `DisplayPolicy` 段：屏幕状态（`mAwake=true`）、状态栏/导航栏窗口句柄、刘海（displayCutout）信息。
- `WindowInsetsStateController` 段：状态栏/导航栏/刘海这些「系统 insets」的尺寸来源。
- `KeyguardController`：锁屏状态（`mKeyguardShowing=false`，没锁屏）。

**一句话结论**：这份 dump 就是「Android 桌面的任务栈快照」——1 个前台 Launcher + 若干空壳 task。查「应用卡在哪个状态/焦点错乱/任务栈异常」都从这里开始。

## 完整原始输出


```text
ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)
Display #0 (activities from top to bottom):
  * Task{afe9a41 #1 type=home U=0 visible=true visibleRequested=true mode=fullscreen translucent=false sz=1}
    * Task{cb9944e #6 type=home I=com.google.android.apps.nexuslauncher/.NexusLauncherActivity U=0 rootTaskId=1 visible=true visibleRequested=true mode=fullscreen translucent=false sz=1}
      mLastNonFullscreenBounds=Rect(276, 692 - 804, 1772)
      isSleeping=false
      topResumedActivity=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
      * Hist  #0: ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
        packageName=com.google.android.apps.nexuslauncher processName=com.google.android.apps.nexuslauncher
        launchedFromUid=0 launchedFromPackage=null launchedFromFeature=null userId=0
        app=ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}
        Intent { act=android.intent.action.MAIN cat=[android.intent.category.HOME] flg=0x10000100 cmp=com.google.android.apps.nexuslauncher/.NexusLauncherActivity (has extras) }
        rootOfTask=true task=Task{cb9944e #6 type=home I=com.google.android.apps.nexuslauncher/.NexusLauncherActivity}
        taskAffinity=null
        mActivityComponent=com.google.android.apps.nexuslauncher/.NexusLauncherActivity
        baseDir=/system_ext/priv-app/NexusLauncherRelease/NexusLauncherRelease.apk
        dataDir=/data/user/0/com.google.android.apps.nexuslauncher
        stateNotNeeded=true componentSpecified=false mActivityType=home
        compat={420dpi} labelRes=0x7f130067 icon=0x7f080291 theme=0x7f140014
        mLastReportedConfigurations:
          mGlobalConfig={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.102 fontWeightAdjustment=0}
          mOverrideConfig={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=home mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.4 fontWeightAdjustment=0}
        CurrentConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=home mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.5 fontWeightAdjustment=0}
        RequestedOverrideConfiguration={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=undefined mDisplayWindowingMode=undefined mActivityType=home mAlwaysOnTop=undefined mRotation=undefined} as.3 ?fontWeightAdjustment}
        taskDescription: label="null" icon=null iconResource=/0 iconFilename=null primaryColor=fff0f0f3
          backgroundColor=fff0f0f3 statusBarColor=0 navigationBarColor=0
         backgroundColorFloating=fff0f0f3
        launchFailed=false launchCount=1 lastLaunchTime=-24s319ms
        mHaveState=false mIcicle=null
        state=RESUMED delayedResume=false finishing=false
        keysPaused=false inHistory=true idle=true
        occludesParent=true noDisplay=false immersive=false launchMode=2
        frozenBeforeDestroy=false forceNewConfig=false
        mActivityType=home
        mImeInsetsFrozenUntilStartInput=false
        windows=[Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}, Window{aba4a09 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}]
        windowType=2 waitingToShow=true
        mOccludesParent=true
        overrideOrientation=SCREEN_ORIENTATION_NOSENSOR
        requestedOrientation=SCREEN_ORIENTATION_NOSENSOR
        mVisibleRequested=true mVisible=true mClientVisible=true reportedDrawn=true reportedVisible=true
        mNumInterestingWindows=2 mNumDrawnWindows=2 allDrawn=true lastAllDrawn=true)
        startingData=null firstWindowDrawn=true mIsExiting=false
        nowVisible=true lastVisibleTime=-20s407ms
        connections={ConnectionRecord{4cb207b u0 CR IMP com.google.android.googlequicksearchbox/com.google.android.apps.gsa.nowoverlayservice.DrawerOverlayService:@a4f600a flags=0x41}, ConnectionRecord{90fc94e u0 com.google.android.apps.nexuslauncher/com.android.quickstep.TouchInteractionService:@adaac49 flags=0x0}}
        resizeMode=RESIZE_MODE_RESIZEABLE
        mLastReportedMultiWindowMode=false mLastReportedPictureInPictureMode=false
        supportsSizeChanges=SIZE_CHANGES_UNSUPPORTED_METADATA
        configChanges=0xdf3
        neverSandboxDisplayApis=false
        alwaysSandboxDisplayApis=false
        areBoundsLetterboxed=false
        mCameraCompatControlState=hidden
        mCameraCompatControlEnabled=true

  * Task{5d7b7ac #2 type=undefined U=0 visible=false visibleRequested=false mode=fullscreen translucent=true sz=2}
    mCreatedByOrganizer=true
    * Task{3dea298 #4 type=undefined U=0 rootTaskId=2 visible=false visibleRequested=false mode=multi-window translucent=true sz=0}
      mBounds=Rect(0, 2400 - 1080, 3600)
      mCreatedByOrganizer=true
      isSleeping=false
    * Task{abe40a #3 type=undefined U=0 rootTaskId=2 visible=false visibleRequested=false mode=multi-window translucent=true sz=0}
      mCreatedByOrganizer=true
      isSleeping=false

  Resumed activities in task display areas (from top to bottom):
    Resumed: ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}

  ResumedActivity: ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}

ActivityTaskSupervisor state:
  topDisplayFocusedRootTask=Task{afe9a41 #1 type=home}
  Display: mDisplayId=0 (organized)
    init=1080x2400 420dpi mMinSizeOfResizeableTaskDp=220 cur=1080x2400 app=1080x2209 rng=1080x954-2272x2209
    deferred=false mLayoutNeeded=false mTouchExcludeRegion=SkRegion((0,0,1080,2400))

  mLastOrientationSource=WindowedMagnification:0:31@221654859
  deepestLastOrientationSource=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
  overrideConfig={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
  mLayoutSeq=126
  mCurrentFocus=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
  mFocusedApp=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}

  mHoldScreenWindow=null
  mObscuringWindow=Window{1d941d9 u0 com.android.systemui.wallpapers.ImageWallpaper}
  mLastWakeLockHoldingWindow=null
  mLastWakeLockObscuringWindow=null

  displayId=0
  mWallpaperTarget=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
  mLastWallpaperX=0.0 mLastWallpaperY=0.5

  mSystemGestureExclusion=SkRegion()

  Display areas in top down Z order:
    * Leaf:36:36
    * HideDisplayCutout:32:35
      * OneHanded:34:35
        * FullscreenMagnification:34:35
          * Leaf:34:35
      * FullscreenMagnification:33:33
        * Leaf:33:33
      * OneHanded:32:32
        * Leaf:32:32
    * WindowedMagnification:0:31
      * HideDisplayCutout:26:31
        * OneHanded:26:31
          * FullscreenMagnification:29:31
            * Leaf:29:31
          * Leaf:28:28
          * FullscreenMagnification:26:27
            * Leaf:26:27
      * Leaf:24:25
      * HideDisplayCutout:18:23
        * OneHanded:18:23
          * FullscreenMagnification:18:23
            * Leaf:18:23
      * OneHanded:17:17
        * FullscreenMagnification:17:17
          * Leaf:17:17
      * HideDisplayCutout:16:16
        * OneHanded:16:16
          * FullscreenMagnification:16:16
            * Leaf:16:16
      * OneHanded:15:15
        * FullscreenMagnification:15:15
          * Leaf:15:15
      * HideDisplayCutout:0:14
        * OneHanded:0:14
          * ImePlaceholder:13:14
            * ImeContainer
          * FullscreenMagnification:0:12
            * Leaf:3:12
            * DefaultTaskDisplayArea (organized)
            * Leaf:0:1

  Task display areas in top down Z order:
    TaskDisplayArea DefaultTaskDisplayArea
      overrideConfig={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=undefined} ?fontWeightAdjustment}
      mPreferredTopFocusableRootTask=Task{afe9a41 #1 type=home}
      mLastFocusedRootTask=Task{afe9a41 #1 type=home}
      Application tokens in top down Z order:
      * Task{afe9a41 #1 type=home U=0 visible=true visibleRequested=true mode=fullscreen translucent=false sz=1}
        bounds=[0,0][1080,2400]
        * Task{cb9944e #6 type=home I=com.google.android.apps.nexuslauncher/.NexusLauncherActivity U=0 rootTaskId=1 visible=true visibleRequested=true mode=fullscreen translucent=false sz=1}
          bounds=[0,0][1080,2400]
          * ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
      * Task{5d7b7ac #2 type=undefined U=0 visible=false visibleRequested=false mode=fullscreen translucent=true sz=2}
        bounds=[0,0][1080,2400]
        * Task{3dea298 #4 type=undefined U=0 rootTaskId=2 visible=false visibleRequested=false mode=multi-window translucent=true sz=0}
          bounds=[0,2400][1080,3600]
        * Task{abe40a #3 type=undefined U=0 rootTaskId=2 visible=false visibleRequested=false mode=multi-window translucent=true sz=0}
          bounds=[0,0][1080,2400]

  no ScreenRotationAnimation 

  rootHomeTask=Task=1

  PinnedTaskController
    mIsImeShowing=false
    mImeHeight=0
    mMinAspectRatio=0.41841003
    mMaxAspectRatio=2.39

  DisplayFrames w=1080 h=2400 r=0

  DisplayPolicy
    mCarDockEnablesAccelerometer=true mDeskDockEnablesAccelerometer=true
    mDockMode=EXTRA_DOCK_STATE_UNDOCKED mLidState=LID_OPEN
    mAwake=true mScreenOnEarly=true mScreenOnFully=true
    mKeyguardDrawComplete=true mWindowManagerDrawComplete=true
    mHdmiPlugged=false
    mLastBehavior=DEFAULT
    mShowingDream=false mDreamingLockscreen=false
    mStatusBar=Window{2a6083d u0 StatusBar}
    mExpandedPanel=Window{a79440b u0 NotificationShade}
    isKeyguardShowing=false
    mNavigationBar=Window{27d2984 u0 NavigationBar0}
    mNavBarOpacityMode=2
    mNavigationBarCanMove=false
    mNavigationBarPosition=4
    mLeftGestureHost=Window{27d2984 u0 NavigationBar0}
    mTopGestureHost=Window{2a6083d u0 StatusBar}
    mRightGestureHost=Window{27d2984 u0 NavigationBar0}
    mBottomGestureHost=Window{27d2984 u0 NavigationBar0}
    mFocusedWindow=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
    mTopFullscreenOpaqueWindowState=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
    mSystemBarColorApps={ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}}
    mNavBarColorWindowCandidate=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
    mNavBarBackgroundWindow=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
    mLastStatusBarAppearanceRegions=
      AppearanceRegion{ bounds=[0,0][1080,2400]}
    mLastLetterboxDetails=
    mStatusBarBackgroundWindows=
      Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
    mTopIsFullscreen=false
    mForceShowNavigationBarEnabled=false mAllowLockscreenWhenOn=false
    mRemoteInsetsControllerControlsSystemBars=false
    mDecorInsetsInfo:
      ROTATION_0={nonDecorInsets=[0,128][0,63], configInsets=[0,128][0,63], nonDecorFrame=[0,128][1080,2337], configFrame=[0,128][1080,2337]}
      ROTATION_90={nonDecorInsets=[128,0][0,63], configInsets=[128,63][0,63], nonDecorFrame=[128,0][2400,1017], configFrame=[128,63][2400,1017]}
      ROTATION_180={nonDecorInsets=[0,0][0,191], configInsets=[0,63][0,191], nonDecorFrame=[0,0][1080,2209], configFrame=[0,63][1080,2209]}
      ROTATION_270={nonDecorInsets=[0,0][128,63], configInsets=[0,63][128,63], nonDecorFrame=[0,0][2272,1017], configFrame=[0,63][2272,1017]}
    SystemGestures:
      mDisplayCutoutTouchableRegionSize=32
      mSwipeStartThreshold=Rect(63, 160 - 63, 63)
      mSwipeDistanceThreshold=63
    Looper state:
      Looper (android.ui, tid 22) {d55ec34}
        (Total messages: 0, polling=true, quitting=false)

  DisplayRotation
    mCurrentAppOrientation=SCREEN_ORIENTATION_NOSENSOR
    mLastOrientation=5
    mRotation=0 mDeferredRotationPauseCount=0
    mLandscapeRotation=ROTATION_90 mSeascapeRotation=ROTATION_270
    mPortraitRotation=ROTATION_0 mUpsideDownRotation=ROTATION_180
    mSupportAutoRotation=true
    WindowOrientationListener
      mEnabled=true
      mCurrentRotation=ROTATION_0
      mSensorType=null
      mSensor={Sensor name="Goldfish 3-axis Accelerometer", vendor="The Android Open Source Project", version=1, type=1, maxRange=39.300102, resolution=2.480159E-4, power=3.0, minDelay=10000}
      mRate=2
      AccelSensorJudge
        mProposedRotation=0
        mPredictedRotation=0
        mLastFilteredX=0.0
        mLastFilteredY=9.776321
        mLastFilteredZ=0.812345
        mLastFilteredTimestampNanos=36612471546 (35.320595ms ago)
        mTiltHistory={last: 5.0}
        mFlat=false
        mSwinging=false
        mAccelerating=false
        mOverhead=false
        mTouched=false
        mTiltToleranceConfig=[[-25, 70], [-25, 65], [-25, 60], [-25, 65]]

    mCarDockRotation=-1 mDeskDockRotation=-1
    mUserRotationMode=USER_ROTATION_FREE mUserRotation=ROTATION_0 mCameraRotationMode=0 mAllowAllRotations=unknown
    mDemoHdmiRotation=ROTATION_90 mDemoHdmiRotationLock=false mUndockedHdmiRotation=-1
    mLidOpenRotation=-1
    mFixedToUserRotation=false

  InputConsumers:
    name=recents_animation_input_consumer pid=1054 user=UserHandle{0}

  WindowInsetsStateController
    InsetsState
      mDisplayFrame=Rect(0, 0 - 1080, 2400)
      mDisplayCutout=DisplayCutout{insets=Rect(0, 128 - 0, 0) waterfall=Insets{left=0, top=0, right=0, bottom=0} boundingRect={Bounds=[Rect(0, 0 - 0, 0), Rect(492, 0 - 610, 128), Rect(0, 0 - 0, 0), Rect(0, 0 - 0, 0)]} cutoutPathParserInfo={CutoutPathParserInfo{displayWidth=1080 displayHeight=2400 physicalDisplayWidth=1080 physicalDisplayHeight=2400 density={2.625} cutoutSpec={M 507,64 a 33,33 0 1 0 66,0 33,33 0 1 0 -66,0 Z @left} rotation={0} scale={1.0} physicalPixelDisplaySizeRatio={1.0}}}}
      mRoundedCorners=RoundedCorners{[RoundedCorner{position=TopLeft, radius=28, center=Point(28, 28)}, RoundedCorner{position=TopRight, radius=28, center=Point(1052, 28)}, RoundedCorner{position=BottomRight, radius=28, center=Point(1052, 2372)}, RoundedCorner{position=BottomLeft, radius=28, center=Point(28, 2372)}]}
      mRoundedCornerFrame=Rect(0, 0 - 0, 0)
      mPrivacyIndicatorBounds=PrivacyIndicatorBounds {static bounds=Rect(827, 0 - 1043, 128) rotation=0}
      mDisplayShape=DisplayShape{ spec=-1893857183 displayWidth=1080 displayHeight=2400 physicalPixelDisplaySizeRatio=1.0 rotation=0 offsetX=0 offsetY=0 scale=1.0}
        InsetsSource id=9e000000 type=statusBars frame=[0,0][1080,128] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=9e000005 type=mandatorySystemGestures frame=[0,0][1080,160] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=9e000006 type=tappableElement frame=[0,0][1080,128] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=3 type=ime frame=[0,0][0,0] visible=false flags= insetsRoundedCornerFrame=false
        InsetsSource id=27 type=displayCutout frame=[0,0][1080,128] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=54c30001 type=navigationBars frame=[0,2337][1080,2400] visible=true flags=SUPPRESS_SCRIM insetsRoundedCornerFrame=false
        InsetsSource id=54c30004 type=systemGestures frame=[0,0][78,2400] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=54c30005 type=mandatorySystemGestures frame=[0,2316][1080,2400] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=54c30006 type=tappableElement frame=[0,0][0,0] visible=true flags= insetsRoundedCornerFrame=false
        InsetsSource id=54c30024 type=systemGestures frame=[1002,0][1080,2400] visible=true flags= insetsRoundedCornerFrame=false
    Control map:
      Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}:
        InsetsSourceControl: {3 mType=ime mSurfacePosition=Point(0, 128) mInsetsHint=Insets{left=0, top=0, right=0, bottom=0}}
        InsetsSourceControl: {9e000000 mType=statusBars initiallyVisible mSurfacePosition=Point(0, 0) mInsetsHint=Insets{left=0, top=128, right=0, bottom=0}}
        InsetsSourceControl: {54c30001 mType=navigationBars initiallyVisible mSurfacePosition=Point(0, 2274) mInsetsHint=Insets{left=0, top=0, right=0, bottom=63}}
    InsetsSourceProviders:
      InsetsSourceProvider
        mSource=InsetsSource id=54c30024 type=systemGestures frame=[1002,0][1080,2400] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(1002, 0 - 1080, 2400)
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{27d2984 u0 NavigationBar0}
      InsetsSourceProvider
        mSource=InsetsSource id=54c30006 type=tappableElement frame=[0,0][0,0] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 0 - 0, 0)
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{27d2984 u0 NavigationBar0}
      InsetsSourceProvider
        mSource=InsetsSource id=54c30005 type=mandatorySystemGestures frame=[0,2316][1080,2400] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 2316 - 1080, 2400)
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{27d2984 u0 NavigationBar0}
      InsetsSourceProvider
        mSource=InsetsSource id=54c30004 type=systemGestures frame=[0,0][78,2400] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 0 - 78, 2400)
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{27d2984 u0 NavigationBar0}
      InsetsSourceProvider
        mSource=InsetsSource id=54c30001 type=navigationBars frame=[0,2337][1080,2400] visible=true flags=SUPPRESS_SCRIM insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 2337 - 1080, 2400)
        mOverrideFrames={2011=Rect(0, 2274 - 1080, 2400)}
        mControl=InsetsSourceControl mId=54c30001 mType=navigationBars mLeash=Surface(name=Surface(name=27d2984 NavigationBar0)/@0xe3050d6 - animation-leash of insets_animation)/@0x7ee8f5a mInitiallyVisible=true mSurfacePosition=Point(0, 2274) mInsetsHint=Insets{left=0, top=0, right=0, bottom=63} mSkipAnimationOnce=false
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{27d2984 u0 NavigationBar0}
        mAdapter=ControlAdapter mCapturedLeash=Surface(name=Surface(name=27d2984 NavigationBar0)/@0xe3050d6 - animation-leash of insets_animation)/@0x7ee8f5a
        mControlTarget=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
      ImeInsetsSourceProvider
        mSource=InsetsSource id=3 type=ime frame=[0,0][0,0] visible=false flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 2274 - 1080, 2400)
        mControl=InsetsSourceControl mId=3 mType=ime mLeash=Surface(name=Surface(name=545c42d InputMethod)/@0x3f69ef3 - animation-leash of insets_animation)/@0x9dca58b mInitiallyVisible=false mSurfacePosition=Point(0, 128) mInsetsHint=Insets{left=0, top=0, right=0, bottom=0} mSkipAnimationOnce=false
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{545c42d u0 InputMethod}
        mAdapter=ControlAdapter mCapturedLeash=Surface(name=Surface(name=545c42d InputMethod)/@0x3f69ef3 - animation-leash of insets_animation)/@0x9dca58b
        mControlTarget=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
        mImeShowing=false
      InsetsSourceProvider
        mSource=InsetsSource id=9e000006 type=tappableElement frame=[0,0][1080,128] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 0 - 1080, 128)
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{2a6083d u0 StatusBar}
      InsetsSourceProvider
        mSource=InsetsSource id=9e000005 type=mandatorySystemGestures frame=[0,0][1080,160] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 0 - 1080, 160)
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{2a6083d u0 StatusBar}
      InsetsSourceProvider
        mSource=InsetsSource id=9e000000 type=statusBars frame=[0,0][1080,128] visible=true flags= insetsRoundedCornerFrame=false
        mSourceFrame=Rect(0, 0 - 1080, 128)
        mControl=InsetsSourceControl mId=9e000000 mType=statusBars mLeash=Surface(name=Surface(name=2a6083d StatusBar)/@0xb842983 - animation-leash of insets_animation)/@0x1e50668 mInitiallyVisible=true mSurfacePosition=Point(0, 0) mInsetsHint=Insets{left=0, top=128, right=0, bottom=0} mSkipAnimationOnce=false
        mIsLeashReadyForDispatching=true
        mWindowContainer=Window{2a6083d u0 StatusBar}
        mAdapter=ControlAdapter mCapturedLeash=Surface(name=Surface(name=2a6083d StatusBar)/@0xb842983 - animation-leash of insets_animation)/@0x1e50668
        mControlTarget=Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}

  KeyguardController:
    mKeyguardShowing=false
    mAodShowing=false
    mKeyguardGoingAway=false
   KeyguardShowing=false AodShowing=false KeyguardGoingAway=false DismissalRequested=false  Occluded=false DismissingKeyguardActivity=null TurnScreenOnActivity=null at display=0
    mDismissalRequested=false

  LockTaskController:
    mLockTaskModeState=NONE
    mLockTaskModeTasks=
    mLockTaskPackages (userId:packages)=

  mCurTaskIdForUser={0=6}
  mUserRootTaskInFront={}
  mVisibilityTransactionDepth=0
  isHomeRecentsComponent=true
  mNoHistoryActivities=[]

  TaskOrganizerController:
      android.window.ITaskOrganizer$Stub$Proxy@2e79a81 uid=10169:
        (fullscreen) Task{afe9a41 #1 type=home}
        (fullscreen) Task{5d7b7ac #2 type=undefined}
        (multi-window) Task{abe40a #3 type=undefined}
        (multi-window) Task{3dea298 #4 type=undefined}

  VisibleActivityProcess:[ ProcessRecord{f23abee 1054:com.google.android.apps.nexuslauncher/u0a162}]
  NumNonAppVisibleWindowUidMap:[ 10169:5]
```
