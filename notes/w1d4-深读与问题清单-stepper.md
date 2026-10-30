# W1D4 · 深读与问题清单 Stepper 文档（✅ 完成）

> 任务：深读 ShizukuService / BinderSender / ShizukuUserServiceManager，产出 ≥3 条问题并讨论。
> 执行人：Hermes（导师）｜学习者：先生（提问 + 校验理解）
> 最终状态：✅ 四轮讨论完成（attachApplication / observer / 去重 / UserService vs CarService），理解已校正

## 任务卡

- **目标**：深读三处代码，把「不理解 / 存疑 / 和 C++ 经验对不上」的点变成问题清单。
- **为什么做**：W1D3 是「我讲你听」，W1D4 是「你问我答」——主动提问才是真正内化的标志。布卢姆分类里，「能复述」是理解层，「能提问」才是应用/分析层。
- **产出**：问题清单 ≥3 条（本文档收录 4 条，含「我的初理解 → 修正」对照）。

## 问题清单（含「初理解 → 修正」）

> 结构：每题记「学习者最初的表述 → 判定 → 修正后的准确说法 → 代码依据」。
> 这样以后回看，能知道「当时错在哪」，比只记正确答案有用。

### Q1 · attachApplication 到底做什么？

**我的初理解**：「告诉 service 我 app 的情况」

**判定**：方向对，但不完整——只说出了「登记」这一面。

**修正**：`attachApplication(IShizukuApplication application, Bundle args)` 实际做**三件事**：

```java
public void attachApplication(IShizukuApplication application, Bundle args) {
    String requestPackageName = args.getString(ATTACH_APPLICATION_PACKAGE_NAME);
    int callingUid = Binder.getCallingUid();

    // ① 安全校验：你报的包名必须属于你的调用 uid
    List<String> packages = PackageManagerApis.getPackagesForUidNoThrow(callingUid);
    if (!packages.contains(requestPackageName)) {
        throw new SecurityException("Request package ... does not belong to uid ...");
    }

    // ② 登记为 client
    clientRecord = clientManager.addClient(callingUid, callingPid,
            application, requestPackageName, apiVersion);

    // ③ 回执 + 双向通道
    Bundle reply = new Bundle();
    reply.putInt(BIND_APPLICATION_SERVER_UID, OsUtils.getUid());
    reply.putInt(BIND_APPLICATION_SERVER_VERSION, replyServerVersion);
    reply.putString(BIND_APPLICATION_SERVER_SECONTEXT, OsUtils.getSELinuxContext());
    application.bindApplication(reply);   // ← server 通过你的回调 binder 把信息回给你
}
```

**一句话**：报到 + 安全校验 + 交换回调 binder（不只是「告诉」）。

---

### Q2 · BinderSender 的 observer 是「监控数据」还是「投递时机」？

**我的初理解**：「通过系统服务监控需求中希望监控的其他 app 和服务数据」——偏了。

**判定**：错误。observer 不监控数据。

**修正**：`BinderSender` 两个 observer 的唯一职责是：**探测「目标 app 进程什么时候活过来」，作为投递 binder 的时机触发器。**

| Observer | 盯什么 | 触发回调 |
|---|---|---|
| `ProcessObserver` | 进程生命周期 | `onForegroundActivitiesChanged`（进前台）<br>`onProcessStateChanged`（状态变）<br>`onProcessDied`（死亡） |
| `UidObserver` | UID 状态 | `onUidActive` / `onUidCachedChanged(false)` / `onUidIdle` / `onUidGone` |

两者都汇聚到 `sendBinder(uid, pid)` → 查权限 → 投递。

**关键区分**：
- **BinderSender 的 observer** = server 内部的「投递时机探测」
- **「监控其他 app 的数据」** = client 拿到 binder 后，自己用 `IActivityManager.registerProcessObserver` 去做——那是 client 的事，不是 BinderSender 的职责

**一句话**：observer 是「投递时机探测器」，不是「数据监控框架」。

---

### Q3 · 去重是怎么做的？

**我的初理解**：「通过 pid 和 uid 进行去重」——方向对，但遗漏了「两套独立列表」这个关键。

**修正**：
- `PID_LIST` → 给 `ProcessObserver` 用，按 **pid** 去重
- `UID_LIST` → 给 `UidObserver` 用，按 **uid** 去重
- **两个列表互相独立**：同一个 app 可能被两个 observer 各触发一次（pid 一次、uid 一次），投递两次——但无害，因为收到 binder 是幂等覆盖
- 去重的真正目的：防止同一个 observer 反复触发（ProcessObserver 每次状态变化都回调），不是跨 observer 去重

```java
// ProcessObserver：按 pid 去重
if (PID_LIST.contains(pid) || !foreground) return;
PID_LIST.add(pid);
sendBinder(uid, pid);

// UidObserver：按 uid 去重
if (UID_LIST.contains(uid)) return;
UID_LIST.add(uid);
sendBinder(uid, -1);
```

**一句话**：pid / uid 两套独立列表，各自去重；跨 observer 重复投递无害。

---

### Q4 · UserService 和 CarService 是什么关系？（W1D4 最大收获）

**我的初理解**：「CarService 类似 UserService 的功能，方式是在 app 进程中 fork 一个 UserService」——错。

**判定**：功能直觉对了一半（都是「不随 app 挂掉的特权通道」），机制完全相反。

**修正**（AOSP 官方材料佐证）：

```
system_server
  └── CarServiceHelperService        ← 只负责启动/绑定
         │ bindService + ICar
         ▼
com.android.car 进程（CarService，预装 privileged app，开机常驻，崩了重启）
  ├── ICarImpl
  ├── CarPropertyService
  └── 各 HalService → VehicleHal → VHAL

App 进程（uid 10xxx）
  └── Car.createCar() → ICar binder → CarPropertyManager.getProperty()
```

**正确对照**：

| Shizuku | CarService | 关系 |
|---|---|---|
| **ShizukuService**（常驻特权进程） | **CarService**（com.android.car，常驻 privileged） | ✅ 这才是对应 |
| App 拿 ShizukuService binder | App 调 `Car.createCar()` 拿 ICar binder | ✅ 对应 |
| **UserService**（app 内 fork 特权子进程） | AOSP **无直接对应** | ❌ 不是 CarService |

**一句话**：CarService = Shizuku 的 server（ShizukuService），不是 UserService。两者架构方向相反：CarService 服务在 App **之外**（中心化），UserService 在 App **之内**（每个 App 自己 fork「常驻不挂」这个共性，被你错当成了「fork 到 App 进程」这个机制。

---

## 今日四问的共同点

1. **都是「机制 vs 直觉」的偏差**：Q1 漏了安全校验和回调，Q2 把「时机探测」当成「数据监控」，Q3 漏了「两套独立列表」，Q4 把「中心化服务」当成「进程内 fork」。
2. **共同根源**：C++ HAL 背景里，「服务」通常是「一个独立的 native 进程 + HAL 接口」——没有「App 进程里 fork 特权子进程」这种模式，所以容易把 Shizuku 的 hack 套到 AOSP 上。
3. **补齐方向**：以后看任何「系统服务」，先问三句——① 它跑在哪个进程？② 它的特权从哪来（预装 / 借 binder / root）？③ 它是中心化还是每个 App 自建？这三问能过滤掉大部分理解偏差。

## 范围控制（导师提醒）

- **UserService 的 fork 细节不再深挖**——它是 Shizuku 自身实现，对 W2 座舱目标边际收益低。
- W1D4 的验收（≥3 条问题）已满足；W1D5 进入「第一次改代码」，会用到 W1D3/W1D4 的投递链知识。
- 下一课 W1D5 的预埋：你已经知道 `ServiceStarter.sendBinder()` 和 `ShizukuService.sendBinderToUserApp()` 是对称的——W1D5 改代码时，改这两个方法之一，观察 binder 投递的变化，就是一次可验证的实验。

---

*本文件由导师会话生成，归档至 `~/projects/android-car-study/notes/`*