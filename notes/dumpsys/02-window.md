# dumpsys 存档：02-window.md（讲解版）

命令：`adb shell dumpsys window windows`

**这个服务是什么**：WindowManagerService（WMS）的窗口列表，回答「屏幕上现在有哪些窗口、谁在谁上面（z 顺序）、每个窗口的属性/层级/token 是什么」。

**这段输出在讲什么**：屏幕上有 458 行的窗口信息，最前面几层全是 SystemUI 的系统装饰窗口（屏幕圆角装饰、导航栏、返回手势条），应用窗口 Launcher 在更下层。这是 WMS 的「第一铲」，座舱里查窗口遮挡、层级错乱就靠它。

## 逐段讲解

### 1. z 顺序：Window #0 在最上面

```text
  Window #0 Window{dbbc7d3 u0 ScreenDecorOverlayBottom}:
  Window #1 Window{e39b329 u0 ScreenDecorOverlay}:
  Window #2 Window{3c0af84 u0 SecondaryHomeHandle0}:
  Window #3 Window{b41af6e u0 EdgeBackGestureHandler0}:
  Window #4 Window{27d2984 u0 NavigationBar0}:
```

**讲解**：`Window #0` 在最顶层，数字越大越靠下（这是 z 顺序，不是创建顺序）。最上面几层都是 SystemUI 的「系统装饰」：圆角遮罩（ScreenDecorOverlay）、手势条（EdgeBackGestureHandler）、导航栏（NavigationBar）。**面试问「窗口是怎么叠的」，答案就是这份从上到下的列表。**

### 2. 一个窗口的关键字段（拿 Window #0 拆解）

```text
  Window #0 Window{dbbc7d3 u0 ScreenDecorOverlayBottom}:
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(fillxwrap) gr=BOTTOM CENTER_VERTICAL ... ty=NAVIGATION_BAR_PANEL fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE NOT_TOUCHABLE NOT_TOUCH_MODAL ... }
    Requested w=1080 h=63 mLayoutSeq=126
    mBaseLayer=251000 mSubLayer=0    mToken=WindowToken{7496f37 type=2024 ...}
```

**讲解**：这是理解窗口的核心四行：
- `package=com.android.systemui` —— 窗口归谁所有。
- `ty=NAVIGATION_BAR_PANEL` —— 窗口类型，决定它能排在哪个层级；`fl=NOT_FOCUSABLE NOT_TOUCHABLE` —— 窗口标志位，这层装饰窗不接受焦点也不接受触摸。
- `mBaseLayer=251000` —— 窗口的基础 z 层级数值（WMS 用这个数排序叠加）。
- `mToken=WindowToken{... type=2024}` —— **token 是窗口的「门禁卡」**：窗口必须持有一个有效 token 才能加入窗口系统，type=2024 是系统窗口的 token 类型。

### 3. 窗口的 frame 与 surface

```text
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,2337][1080,2400] ...
      mDrawState=HAS_DRAWN       mLastHidden=false
```

**讲解**：`frame=[0,2337][1080,2400]` 是这个窗口在屏幕上的实际位置（底部 63 像素高的一条，就是导航栏区域）。`mDrawState=HAS_DRAWN` 表示它已经画出来了。每个窗口最终要交给 SurfaceFlinger 合成，这一块和你的图形栈背景正好衔接——**WMS 管「窗口怎么摆」，SurfaceFlinger 管「像素怎么合」**。

### 4. 焦点窗口（在文件靠后位置）

这份 dump 末尾还有 `mCurrentFocus` / `mFocusedWindow` 之类字段，和 01-activity 里看到的是同一件事：当前输入焦点在哪个窗口。两处互相印证。

**一句话结论**：这份 dump 是「屏幕的窗口叠放图」——最上面是 SystemUI 装饰层，往下才是应用窗口。查「谁把谁挡住了」「窗口为什么点不到」就从这里看 z 顺序和 fl 标志位。

## 完整原始输出


```text
WINDOW MANAGER WINDOWS (dumpsys window windows)
  Window #0 Window{dbbc7d3 u0 ScreenDecorOverlayBottom}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@6470436
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(fillxwrap) gr=BOTTOM CENTER_VERTICAL sim={adjust=pan} layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR_PANEL fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE NOT_TOUCHABLE NOT_TOUCH_MODAL LAYOUT_IN_SCREEN SPLIT_TOUCH FLAG_SLIPPERY
      pfl=SHOW_FOR_ALL_USERS NO_MOVE_ANIMATION IS_ROUNDED_CORNERS_OVERLAY COLOR_SPACE_AGNOSTIC USE_BLAST FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
      vsysui=LAYOUT_STABLE
      bhv=DEFAULT}
    Requested w=1080 h=63 mLayoutSeq=126
    mBaseLayer=251000 mSubLayer=0    mToken=WindowToken{7496f37 type=2024 android.os.BinderProxy@6470436}
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mTouchableInsets=3 mGivenInsetsPending=false
    touchable region=SkRegion()
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,2337][1080,2400] last=[0,2337][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{86fafb2 ScreenDecorOverlayBottom}:
      mSurface=Surface(name=ScreenDecorOverlayBottom)/@0x4c23b03
      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
    mForceSeamlesslyRotate=true seamlesslyRotate: pending=null    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #1 Window{e39b329 u0 ScreenDecorOverlay}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@4bfdcb2
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(fillxwrap) gr=TOP CENTER_VERTICAL sim={adjust=pan} layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR_PANEL fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE NOT_TOUCHABLE NOT_TOUCH_MODAL LAYOUT_IN_SCREEN SPLIT_TOUCH FLAG_SLIPPERY
      pfl=SHOW_FOR_ALL_USERS NO_MOVE_ANIMATION IS_ROUNDED_CORNERS_OVERLAY COLOR_SPACE_AGNOSTIC USE_BLAST FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
      vsysui=LAYOUT_STABLE
      bhv=DEFAULT}
    Requested w=1080 h=128 mLayoutSeq=126
    mBaseLayer=251000 mSubLayer=0    mToken=WindowToken{e9b6403 type=2024 android.os.BinderProxy@4bfdcb2}
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mTouchableInsets=3 mGivenInsetsPending=false
    touchable region=SkRegion((492,0,610,128))
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,0][1080,128] last=[0,0][1080,128] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{c003a80 ScreenDecorOverlay}:
      mSurface=Surface(name=ScreenDecorOverlay)/@0xcec18b9
      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
    mForceSeamlesslyRotate=true seamlesslyRotate: pending=null    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #2 Window{3c0af84 u0 SecondaryHomeHandle0}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@c5e3416
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(0x0) sim={adjust=pan} ty=NAVIGATION_BAR_PANEL fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE NOT_TOUCHABLE NOT_TOUCH_MODAL LAYOUT_IN_SCREEN HARDWARE_ACCELERATED FLAG_SLIPPERY
      pfl=NO_MOVE_ANIMATION LAYOUT_SIZE_EXTENDED_BY_CUTOUT USE_BLAST
      bhv=DEFAULT
      fitTypes=NAVIGATION_BARS CAPTION_BAR}
    Requested w=-1 h=-1 mLayoutSeq=41
    mBaseLayer=251000 mSubLayer=0    mToken=WindowToken{6ff1197 type=2024 android.os.BinderProxy@c5e3416}
    mViewVisibility=0x8 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=undefined mDisplayWindowingMode=undefined mActivityType=undefined mAlwaysOnTop=undefined mRotation=undefined} ?fontWeightAdjustment}
    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,128][1080,2400] frame=[540,1200][540,1200] last=[0,0][0,0] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{82514fe SecondaryHomeHandle0}:
      mDrawState=NO_SURFACE       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
      mShownAlpha=0.0 mAlpha=1.0 mLastAlpha=0.0
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=false
    isVisible=false
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #3 Window{b41af6e u0 EdgeBackGestureHandler0}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@c625370
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(276x704) sim={adjust=pan} ty=NAVIGATION_BAR_PANEL fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN HARDWARE_ACCELERATED
      pfl=SHOW_FOR_ALL_USERS EXCLUDE_FROM_SCREEN_MAGNIFICATION USE_BLAST FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
      bhv=DEFAULT}
    Requested w=-1 h=-1 mLayoutSeq=36
    mBaseLayer=251000 mSubLayer=0    mToken=WindowToken{3e9d6e9 type=2024 android.os.BinderProxy@c625370}
    mViewVisibility=0x8 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=undefined mDisplayWindowingMode=undefined mActivityType=undefined mAlwaysOnTop=undefined mRotation=undefined} ?fontWeightAdjustment}
    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,128][1080,2400] frame=[402,848][678,1552] last=[402,848][678,1552] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{ea3845f EdgeBackGestureHandler0}:
      mDrawState=NO_SURFACE       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
      mShownAlpha=0.0 mAlpha=1.0 mLastAlpha=0.0
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=false
    isVisible=false
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #4 Window{27d2984 u0 NavigationBar0}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@5239e16
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(fillx126) gr=BOTTOM CENTER_VERTICAL sim={adjust=pan} layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE NOT_TOUCH_MODAL WATCH_OUTSIDE_TOUCH SPLIT_TOUCH
      pfl=LAYOUT_SIZE_EXTENDED_BY_CUTOUT COLOR_SPACE_AGNOSTIC USE_BLAST FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
      bhv=DEFAULT
      providedInsets:
        InsetsFrameProvider: {id=#54c30001, index=0, type=navigationBars, source=FRAME, flags=[SUPPRESS_SCRIM], insetsSize=Insets{left=0, top=0, right=0, bottom=63}, insetsSizeOverrides=[TypedInsetsSize: {windowType=INPUT_METHOD, insetsSize=null}]}
        InsetsFrameProvider: {id=#54c30006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=0}}
        InsetsFrameProvider: {id=#54c30005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=84}}
        InsetsFrameProvider: {id=#54c30004, index=0, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=78, top=0, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=78, top=0, right=0, bottom=0}}
        InsetsFrameProvider: {id=#54c30024, index=1, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=0, top=0, right=78, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=0, right=78, bottom=0}}
      paramsForRotation:
        ROTATION_0={(0,0)(fillx126) gr=BOTTOM CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE NOT_TOUCH_MODAL WATCH_OUTSIDE_TOUCH SPLIT_TOUCH FLAG_SLIPPERY
          pfl=LAYOUT_SIZE_EXTENDED_BY_CUTOUT COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#54c30001, index=0, type=navigationBars, source=FRAME, flags=[SUPPRESS_SCRIM], insetsSize=Insets{left=0, top=0, right=0, bottom=63}, insetsSizeOverrides=[TypedInsetsSize: {windowType=INPUT_METHOD, insetsSize=null}]}
            InsetsFrameProvider: {id=#54c30006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=84}}
            InsetsFrameProvider: {id=#54c30004, index=0, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=78, top=0, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=78, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30024, index=1, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=0, top=0, right=78, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=0, right=78, bottom=0}}}
        ROTATION_90={(0,0)(fillx126) gr=BOTTOM CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE NOT_TOUCH_MODAL WATCH_OUTSIDE_TOUCH SPLIT_TOUCH FLAG_SLIPPERY
          pfl=LAYOUT_SIZE_EXTENDED_BY_CUTOUT COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#54c30001, index=0, type=navigationBars, source=FRAME, flags=[SUPPRESS_SCRIM], insetsSize=Insets{left=0, top=0, right=0, bottom=63}, insetsSizeOverrides=[TypedInsetsSize: {windowType=INPUT_METHOD, insetsSize=null}]}
            InsetsFrameProvider: {id=#54c30006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=84}}
            InsetsFrameProvider: {id=#54c30004, index=0, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=78, top=0, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=78, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30024, index=1, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=0, top=0, right=78, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=0, right=78, bottom=0}}}
        ROTATION_180={(0,0)(fillx126) gr=BOTTOM CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE NOT_TOUCH_MODAL WATCH_OUTSIDE_TOUCH SPLIT_TOUCH FLAG_SLIPPERY
          pfl=LAYOUT_SIZE_EXTENDED_BY_CUTOUT COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#54c30001, index=0, type=navigationBars, source=FRAME, flags=[SUPPRESS_SCRIM], insetsSize=Insets{left=0, top=0, right=0, bottom=63}, insetsSizeOverrides=[TypedInsetsSize: {windowType=INPUT_METHOD, insetsSize=null}]}
            InsetsFrameProvider: {id=#54c30006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=84}}
            InsetsFrameProvider: {id=#54c30004, index=0, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=78, top=0, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=78, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30024, index=1, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=0, top=0, right=78, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=0, right=78, bottom=0}}}
        ROTATION_270={(0,0)(fillx126) gr=BOTTOM CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=NAVIGATION_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE NOT_TOUCH_MODAL WATCH_OUTSIDE_TOUCH SPLIT_TOUCH FLAG_SLIPPERY
          pfl=LAYOUT_SIZE_EXTENDED_BY_CUTOUT COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED TRUSTED_OVERLAY
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#54c30001, index=0, type=navigationBars, source=FRAME, flags=[SUPPRESS_SCRIM], insetsSize=Insets{left=0, top=0, right=0, bottom=63}, insetsSizeOverrides=[TypedInsetsSize: {windowType=INPUT_METHOD, insetsSize=null}]}
            InsetsFrameProvider: {id=#54c30006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=0, right=0, bottom=84}}
            InsetsFrameProvider: {id=#54c30004, index=0, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=78, top=0, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=78, top=0, right=0, bottom=0}}
            InsetsFrameProvider: {id=#54c30024, index=1, type=systemGestures, source=DISPLAY, flags=[], insetsSize=Insets{left=0, top=0, right=78, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=0, right=78, bottom=0}}}}
    Requested w=1080 h=126 mLayoutSeq=126
    mBaseLayer=241000 mSubLayer=0    mToken=WindowToken{5593397 type=2019 android.os.BinderProxy@7893731}
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mTouchableInsets=3 mGivenInsetsPending=false
    touchable region=SkRegion()
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,2274][1080,2400] last=[0,2274][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    ContainerAnimator:
      mLeash=Surface(name=Surface(name=27d2984 NavigationBar0)/@0xe3050d6 - animation-leash of insets_animation)/@0x7ee8f5a mAnimationType=insets_animation
      Animation: com.android.server.wm.InsetsSourceProvider$ControlAdapter@e6e7eac
        ControlAdapter mCapturedLeash=Surface(name=Surface(name=27d2984 NavigationBar0)/@0xe3050d6 - animation-leash of insets_animation)/@0x7ee8f5a
    WindowStateAnimator{4ac8775 NavigationBar0}:
      mSurface=Surface(name=NavigationBar0)/@0x839830a
      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #5 Window{a79440b u0 NotificationShade}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@a3aad85
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(fillxfill) gr=TOP CENTER_VERTICAL sim={adjust=pan} layoutInDisplayCutoutMode=always ty=2040 fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE TOUCHABLE_WHEN_WAKING WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
      pfl=OPTIMIZE_MEASURE COLOR_SPACE_AGNOSTIC USE_BLAST BEHAVIOR_CONTROLLED FIT_INSETS_CONTROLLED
      bhv=SHOW_TRANSIENT_BARS_BY_SWIPE}
    Requested w=1080 h=2400 mLayoutSeq=46
    mBaseLayer=171000 mSubLayer=0    mToken=WindowToken{5b897da type=2040 android.os.BinderProxy@e0432fc}
    mViewVisibility=0x4 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mTouchableInsets=3 mGivenInsetsPending=false
    touchable region=SkRegion((0,0,1080,128)(492,128,610,160))
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=undefined mDisplayWindowingMode=undefined mActivityType=undefined mAlwaysOnTop=undefined mRotation=undefined} ?fontWeightAdjustment}
    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,0][1080,2400] last=[0,0][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{a26077b NotificationShade}:
      mDrawState=NO_SURFACE       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
      mShownAlpha=0.0 mAlpha=1.0 mLastAlpha=0.0
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=false
    isVisible=false
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #6 Window{2a6083d u0 StatusBar}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@61857a6
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(fillx128) gr=TOP CENTER_VERTICAL sim={adjust=pan} layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
      pfl=COLOR_SPACE_AGNOSTIC USE_BLAST FIT_INSETS_CONTROLLED
      bhv=DEFAULT
      providedInsets:
        InsetsFrameProvider: {id=#9e000000, index=0, type=statusBars, source=FRAME, flags=[], insetsSize=Insets{left=0, top=128, right=0, bottom=0}}
        InsetsFrameProvider: {id=#9e000006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=128, right=0, bottom=0}}
        InsetsFrameProvider: {id=#9e000005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=32, right=0, bottom=0}}
      paramsForRotation:
        ROTATION_0={(0,0)(fillx128) gr=TOP CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE SPLIT_TOUCH DRAWS_SYSTEM_BAR_BACKGROUNDS
          pfl=COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#9e000000, index=0, type=statusBars, source=FRAME, flags=[], insetsSize=Insets{left=0, top=128, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=128, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=128, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=32, right=0, bottom=0}}}
        ROTATION_90={(0,0)(fillx63) gr=TOP CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE SPLIT_TOUCH DRAWS_SYSTEM_BAR_BACKGROUNDS
          pfl=COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#9e000000, index=0, type=statusBars, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=32, right=0, bottom=0}}}
        ROTATION_180={(0,0)(fillx63) gr=TOP CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE SPLIT_TOUCH DRAWS_SYSTEM_BAR_BACKGROUNDS
          pfl=COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#9e000000, index=0, type=statusBars, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=32, right=0, bottom=0}}}
        ROTATION_270={(0,0)(fillx63) gr=TOP CENTER_VERTICAL layoutInDisplayCutoutMode=always ty=STATUS_BAR fmt=TRANSLUCENT
          fl=NOT_FOCUSABLE SPLIT_TOUCH DRAWS_SYSTEM_BAR_BACKGROUNDS
          pfl=COLOR_SPACE_AGNOSTIC FIT_INSETS_CONTROLLED
          bhv=DEFAULT
          providedInsets:
            InsetsFrameProvider: {id=#9e000000, index=0, type=statusBars, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000006, index=0, type=tappableElement, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}}
            InsetsFrameProvider: {id=#9e000005, index=0, type=mandatorySystemGestures, source=FRAME, flags=[], insetsSize=Insets{left=0, top=63, right=0, bottom=0}, mMinimalInsetsSizeInDisplayCutoutSafe=Insets{left=0, top=32, right=0, bottom=0}}}}
    Requested w=1080 h=128 mLayoutSeq=126
    mBaseLayer=151000 mSubLayer=0    mToken=WindowToken{b9de594 type=2000 android.os.BinderProxy@77d9d01}
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,0][1080,128] last=[0,0][1080,128] insetsChanged=false
     surface=[0,0][0,0]
    ContainerAnimator:
      mLeash=Surface(name=Surface(name=2a6083d StatusBar)/@0xb842983 - animation-leash of insets_animation)/@0x1e50668 mAnimationType=insets_animation
      Animation: com.android.server.wm.InsetsSourceProvider$ControlAdapter@c9ad998
        ControlAdapter mCapturedLeash=Surface(name=Surface(name=2a6083d StatusBar)/@0xb842983 - animation-leash of insets_animation)/@0x1e50668
    WindowStateAnimator{fcb25f1 StatusBar}:
      mSurface=Surface(name=StatusBar)/@0x874c5d6
      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #7 Window{2ac318a u0 ShellDropTarget}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@fac18ad
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=SYSTEM_ALERT_WINDOW
    mAttrs={(0,0)(fillxfill) sim={adjust=pan} layoutInDisplayCutoutMode=always ty=APPLICATION_OVERLAY fmt=TRANSLUCENT
      fl=NOT_FOCUSABLE HARDWARE_ACCELERATED
      pfl=SHOW_FOR_ALL_USERS NO_MOVE_ANIMATION USE_BLAST FIT_INSETS_CONTROLLED INTERCEPT_GLOBAL_DRAG_AND_DROP
      bhv=DEFAULT}
    Requested w=1080 h=2400 mLayoutSeq=5
    mBaseLayer=111000 mSubLayer=0    mToken=WindowToken{fc44773 type=2038 android.os.BinderProxy@50d63ba}
    mViewVisibility=0x4 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=undefined mDisplayWindowingMode=undefined mActivityType=undefined mAlwaysOnTop=undefined mRotation=undefined} ?fontWeightAdjustment}
    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,0][1080,2400] last=[0,0][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{783a057 ShellDropTarget}:
      mDrawState=NO_SURFACE       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
      mShownAlpha=0.0 mAlpha=1.0 mLastAlpha=0.0
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=false
    isVisible=false
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #8 Window{aba4a09 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}:
    mDisplayId=0 rootTaskId=1 mSession=Session{e4146e9 1632:u0a10132} mClient=android.os.BinderProxy@86e1f10
    mOwnerUid=10132 showForAllUsers=false package=com.google.android.apps.nexuslauncher appop=NONE
    mAttrs={(0,0)(fillxfill) gr=LEFT CENTER_HORIZONTAL sim={adjust=resize} layoutInDisplayCutoutMode=shortEdges ty=DRAWN_APPLICATION fmt=TRANSPARENT wanim=0x10302f2 alpha=0.0
      fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR WATCH_OUTSIDE_TOUCH SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
      pfl=NO_MOVE_ANIMATION OPTIMIZE_MEASURE FORCE_DRAW_STATUS_BAR_BACKGROUND USE_BLAST APPEARANCE_CONTROLLED FIT_INSETS_CONTROLLED
      vsysui=LIGHT_STATUS_BAR LIGHT_NAVIGATION_BAR
      bhv=DEFAULT
      fitSides=}
    Requested w=1080 h=2400 mLayoutSeq=126
    mBaseLayer=21000 mSubLayer=0    mToken=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
    mActivityRecord=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
    drawnStateEvaluated=true    mightAffectAllDrawn=true
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=home mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.5 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=home mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.5 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,0][1080,2400] last=[0,0][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{82ff744 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}:
      mSurface=Surface(name=com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity)/@0xc5b302d
      Surface: shown=true layer=0 alpha=0.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
      mShownAlpha=0.0 mAlpha=0.0 mLastAlpha=0.0
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #9 Window{545c42d u0 InputMethod}:
    mDisplayId=0 rootTaskId=1 mSession=Session{3d49b4d 1397:u0a10151} mClient=android.os.BinderProxy@6985b44
    mOwnerUid=10151 showForAllUsers=false package=com.google.android.inputmethod.latin appop=NONE
    mAttrs={(0,0)(fillxfill) gr=BOTTOM CENTER_VERTICAL sim={adjust=pan} ty=INPUT_METHOD fmt=TRANSPARENT wanim=0x1030056 receive insets ignoring z-order
      fl=NOT_FOCUSABLE LAYOUT_IN_SCREEN SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
      pfl=USE_BLAST FIT_INSETS_CONTROLLED
      bhv=DEFAULT
      fitTypes=STATUS_BARS NAVIGATION_BARS
      fitSides=LEFT TOP RIGHT}
    Requested w=1080 h=2400 mLayoutSeq=82
    mIsImWindow=true mIsWallpaper=false mIsFloatingLayer=true
    mBaseLayer=131000 mSubLayer=0    mToken=WindowToken{1fd8fad type=2011 android.os.Binder@26a24c4}
    mViewVisibility=0x8 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,2272][0,0] mGivenVisibleInsets=[0,0][0,0]
    mTouchableInsets=3 mGivenInsetsPending=false
    touchable region=SkRegion((0,2274,1080,2400))
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={0.0 ?mcc0mnc ?localeList ?layoutDir ?swdp ?wdp ?hdp ?density ?lsize ?long ?ldr ?wideColorGamut ?orien ?uimode ?night ?touch ?keyb/?/? ?nav/? winConfig={ mBounds=Rect(0, 0 - 0, 0) mAppBounds=null mMaxBounds=Rect(0, 0 - 0, 0) mDisplayRotation=undefined mWindowingMode=undefined mDisplayWindowingMode=undefined mActivityType=undefined mAlwaysOnTop=undefined mRotation=undefined} ?fontWeightAdjustment}
    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false
    Frames: parent=[0,128][1080,2400] display=[0,128][1080,2400] frame=[0,128][1080,2400] last=[0,128][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    ContainerAnimator:
      mLeash=Surface(name=Surface(name=545c42d InputMethod)/@0x3f69ef3 - animation-leash of insets_animation)/@0x9dca58b mAnimationType=insets_animation
      Animation: com.android.server.wm.InsetsSourceProvider$ControlAdapter@b4f6962
        ControlAdapter mCapturedLeash=Surface(name=Surface(name=545c42d InputMethod)/@0x3f69ef3 - animation-leash of insets_animation)/@0x9dca58b
    WindowStateAnimator{6b7eaf3 InputMethod}:
      mDrawState=NO_SURFACE       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
      mShownAlpha=0.0 mAlpha=1.0 mLastAlpha=0.0
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    isOnScreen=false
    isVisible=false
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #10 Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}:
    mDisplayId=0 rootTaskId=1 mSession=Session{416e1af 1054:u0a10162} mClient=android.os.BinderProxy@8847e98
    mOwnerUid=10162 showForAllUsers=false package=com.google.android.apps.nexuslauncher appop=NONE
    mAttrs={(0,0)(fillxfill) sim={adjust=nothing} layoutInDisplayCutoutMode=always ty=BASE_APPLICATION fmt=TRANSPARENT wanim=0x10302f2
      fl=LAYOUT_IN_SCREEN LAYOUT_INSET_DECOR SHOW_WALLPAPER SPLIT_TOUCH HARDWARE_ACCELERATED DRAWS_SYSTEM_BAR_BACKGROUNDS
      pfl=NO_MOVE_ANIMATION OPTIMIZE_MEASURE FORCE_DRAW_STATUS_BAR_BACKGROUND USE_BLAST FIT_INSETS_CONTROLLED
      vsysui=LAYOUT_STABLE LAYOUT_HIDE_NAVIGATION LAYOUT_FULLSCREEN
      bhv=DEFAULT
      fitSides=}
    Requested w=1080 h=2400 mLayoutSeq=126
    mBaseLayer=21000 mSubLayer=0    mToken=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
    mActivityRecord=ActivityRecord{a41c311 u0 com.google.android.apps.nexuslauncher/.NexusLauncherActivity t6}
    drawnStateEvaluated=true    mightAffectAllDrawn=true
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=home mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.5 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=home mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.5 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[0,0][1080,2400] frame=[0,0][1080,2400] last=[0,0][1080,2400] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{d743b0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}:
      mSurface=Surface(name=com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity)/@0xc67a229
      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    mWallpaperX=0.0 mWallpaperY=0.5
    mWallpaperXStep=0.33333334 mWallpaperYStep=1.0
    mWallpaperZoomOut=0.0
    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0
  Window #11 Window{1d941d9 u0 com.android.systemui.wallpapers.ImageWallpaper}:
    mDisplayId=0 rootTaskId=1 mSession=Session{2d76c0 765:u0a10169} mClient=android.os.BinderProxy@a71d420
    mOwnerUid=10169 showForAllUsers=true package=com.android.systemui appop=NONE
    mAttrs={(0,0)(2161x2400) gr=TOP START CENTER layoutInDisplayCutoutMode=always ty=WALLPAPER fmt=RGBX_8888 wanim=0x103030e
      fl=NOT_FOCUSABLE NOT_TOUCHABLE LAYOUT_IN_SCREEN LAYOUT_NO_LIMITS SCALED LAYOUT_INSET_DECOR
      pfl=WANTS_OFFSET_NOTIFICATIONS SHOW_FOR_ALL_USERS USE_BLAST
      bhv=DEFAULT}
    Requested w=922 h=1024 mLayoutSeq=126
    mIsImWindow=false mIsWallpaper=true mIsFloatingLayer=true
    mBaseLayer=11000 mSubLayer=0    mToken=WallpaperWindowToken{2872854 token=android.os.Binder@a83aba7}
    mViewVisibility=0x0 mHaveFrame=true mObscured=false
    mGivenContentInsets=[0,0][0,0] mGivenVisibleInsets=[0,0][0,0]
    mFullConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mLastReportedConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false
    Frames: parent=[0,0][1080,2400] display=[-100000,-100000][100000,100000] frame=[0,0][2161,2400] last=[0,0][2161,2400] insetsChanged=false
     surface=[0,0][0,0]
    WindowStateAnimator{3eb9ae com.android.systemui.wallpapers.ImageWallpaper}:
      mSurface=Surface(name=com.android.systemui.wallpapers.ImageWallpaper)/@0x1dc434f
      Surface: shown=true layer=0 alpha=1.0 rect=(0.0,0.0)  transform=(1.0, 0.0, 0.0, 1.0)
      mDrawState=HAS_DRAWN       mLastHidden=false
      mEnterAnimationPending=false      mSystemDecorRect=[0,0][0,0]
    mForceSeamlesslyRotate=false seamlesslyRotate: pending=null    mHScale=2.3438177 mVScale=2.34375
    mWallpaperX=0.0 mWallpaperY=0.5
    mWallpaperXStep=0.33333334 mWallpaperYStep=1.0
    mWallpaperZoomOut=0.0
    isOnScreen=true
    isVisible=true
    keepClearAreas: restricted=[], unrestricted=[]
    mPrepareSyncSeqId=0

  mGlobalConfiguration={1.0 310mcc260mnc [en_US] ldltr sw411dp w411dp h842dp 420dpi nrml long port finger -keyb/v/h -nav/h winConfig={ mBounds=Rect(0, 0 - 1080, 2400) mAppBounds=Rect(0, 128 - 1080, 2337) mMaxBounds=Rect(0, 0 - 1080, 2400) mDisplayRotation=ROTATION_0 mWindowingMode=fullscreen mDisplayWindowingMode=fullscreen mActivityType=undefined mAlwaysOnTop=undefined mRotation=ROTATION_0} as.3 s.59 fontWeightAdjustment=0}
  mHasPermanentDpad=false
  mTopFocusedDisplayId=0
  imeLayeringTarget in display# 0 Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
  imeInputTarget in display# 0 Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
  imeControlTarget in display# 0 Window{8c66f1 u0 com.google.android.apps.nexuslauncher/com.google.android.apps.nexuslauncher.NexusLauncherActivity}
  Minimum task size of display#0 220  mBlurEnabled=true
  mLastDisplayFreezeDuration=0 due to new-config
 mHighResSnapshotScale=0.8
 mSnapshotEnabled=true
 SnapshotCache Task
 mHighResSnapshotScale=0.6
 mSnapshotEnabled=false
 SnapshotCache Activity
  mInputMethodWindow=Window{545c42d u0 InputMethod}
  mTraversalScheduled=false
  mSystemBooted=true mDisplayEnabled=true
  mTransactionSequence=172
  mDisplayFrozen=false windows=0 client=false apps=0
  mRotation=0
  mLastOrientation=5
  mWaitingForConfig=false
  mDisplayRotationWatchers: [ 10169->0]
  Animation settings: disabled=false window=1.0 transition=1.0 animator=1.0
```
