### 理解ActivityManagerService

- [一.与ActivityMangerService相关的类](https://www.pianshen.com/article/84951064773/#ActivityMangerService_2)

- - [1.Android7.0版本中与AMS相关的类](https://www.pianshen.com/article/84951064773/#1Android70AMS_4)
  - [2.Android8.0版本中与AMS相关的类](https://www.pianshen.com/article/84951064773/#2Android80AMS_13)

- [二.ActivityManagerService的启动过程](https://www.pianshen.com/article/84951064773/#ActivityManagerService_20)

- [三.ActivityManagerService与应用程序进程的关系](https://www.pianshen.com/article/84951064773/#ActivityManagerService_39)

- [四.与ActivityManagerService相关的数据结构类](https://www.pianshen.com/article/84951064773/#ActivityManagerService_42)

- - [1.ActivityRecord](https://www.pianshen.com/article/84951064773/#1ActivityRecord_43)
  - [2.TaskRecord](https://www.pianshen.com/article/84951064773/#2TaskRecord_56)
  - [3.ActivityStack](https://www.pianshen.com/article/84951064773/#3ActivityStack_66)
  - [4.ActivityStackSupervisor](https://www.pianshen.com/article/84951064773/#4ActivityStackSupervisor_81)
  - [5.ActivityState](https://www.pianshen.com/article/84951064773/#5ActivityState_88)

- [五.Activity栈管理](https://www.pianshen.com/article/84951064773/#Activity_99)

- - [1.Activity任务栈模型](https://www.pianshen.com/article/84951064773/#1Activity_100)
  - [2.Activity的启动方式——LaunchMode](https://www.pianshen.com/article/84951064773/#2ActivityLaunchMode_103)
  - [3.Intent与Activity相关的常用FLAG](https://www.pianshen.com/article/84951064773/#3IntentActivityFLAG_108)
  - [4.栈亲和度——taskTaffinity](https://www.pianshen.com/article/84951064773/#4taskTaffinity_118)


   ActivityManagerService是Android系统中重要的系统服务之一，主要负责Android中四大组件的启动、通信、部分生命周期的管理等等。通常，为了方便书写，习惯将ActivityManagerService简写为AMS。



# 一.与ActivityMangerService相关的类

   常见的ActivityManager、ActivityManagerNative、ActivityMangerProxy等等都是和ActivityManagerService相关的类，它们一起协同工作，保证系统正常运行。它们的关系在Android7.0之前和之后有很大的不同。

## 1.Android7.0版本中与AMS相关的类

![在这里插入图片描述](https://www.pianshen.com/images/399/3b2cb7490dd289469b88c09b27067447.png)
**1）调用过程**
   ActivityManager通过调用ActivityMangerNative的getDefault方法获取ActivityManagerProxy对象，通过调用ActivityManagerProxy的方法与ActivityManagerNative进行通信，而ActivityMangerNative是一个抽象类，其具体实现为ActivityManagerService。所以ActivityManager通过ActivityManagerProxy和ActivityMangerService进行通信。
**2）类之间的关系**
   **i）** IActivityManager接口继承了IInterface接口，Binder实现了IBinder接口。
   **ii）** ActivityMangerProxy是ActivityManagerNative的内部类，实现了IActivityManager接口。
   **iii）** ActivityManagerNative继承了Binder实现了IActivityManager接口。
   **iv）** ActivityManagerService继承了ActivityManagerNative。

## 2.Android8.0版本中与AMS相关的类

![在这里插入图片描述](https://www.pianshen.com/images/916/cbbf7aed3fddcec80fe0d4a4d906887c.png)
**1）调用流程**
   通过AIDL实现通信，ActivityManager调用其静态方法getService获取IActivityManager对象。
**2）类之间的关系**
   **i）** IActivityManager内部的IActivityManager.Stub实现了IActivityManager。
   **ii）** ActivityManangerService继承了IActivityManager.Stub。

# 二.ActivityManagerService的启动过程

**AMS在SystemServer进程中启动。**

**SystemServer.java中startBootstrapServices方法的执行过程：**
   **1**.调用SystemServiceManager对象的startService方法，参数为ActivityManagerService.Lifecycle.class。返回Lifecycle对象，Lifecycle继承自SystemService。
   **2**.调用Lifecycle对象的getService方法，获取AMS对象。

**SystemServiceManager.java中startService方法的执行过程：**
   **1**.将传入的SystemService对象加入到ArrayList中。
   **2**.调用SystemService对象的onStart方法。
   根据传入的参数，该SystemService对象为Lifecycle对象。

**ActivityManagerService.java中Lifecycle类的onStart方法的执行过程：**
   Lifecycle在构造函数中创建AMS对象，在onStart方法中，调用AMS对象的onStart方法。

**AMS对象启动完成，使用时通过调用Lifecycle类的getService方法获取。**

**ActivityManagerService.java中Lifecycle类的getService方法的执行过程：**
   返回AMS对象。

# 三.ActivityManagerService与应用程序进程的关系

   AMS在启动应用程序时会检查应用程序的进程是否存在。
   若不存在，AMS会请求Zygote进程创建需要的应用程序进程。

# 四.与ActivityManagerService相关的数据结构类

## 1.ActivityRecord

   ActivityRecord用来描述一个Activity，它记录了Activity的所有信息。
**1）ActivityRecord中重要的成员变量**
  **ActivityManagerService service**：AMS的引用。
  **ActivityInfo info**：Activity代码和AndroidManifest中设置的节点信息。
  **String launchedFromPackage**：启动Activity的包名。
  **String taskAffinity**：Activity希望归属的栈。
  **TaskRecord task**：ActivityRecord所在的TaskRecord。
  **ProcessRecord app**：ActivityRecord所在的应用程序进程。
  **ActivityState state**：当前Activity的状态。
  **int icon**：Activity的图标资源标识符。
  **int theme**：Activity主题资源标识符。

## 2.TaskRecord

   TaskRecord用来描述一个Activity任务栈。
**1）TaskRecord中重要的成员变量**
  **int taskId**：任务栈的唯一标识符。
  **String affinity**：任务栈的倾向性。
  **Intent intent**：启动这个任务栈的Intent。
  **ArrayList<ActivityRecord> mActivites**：按照历史顺序排列的Activity记录。
  **ActivityStack mStack**：当前归属的ActivityStack。
  **ActivityManagerService mService**：AMS的引用。

## 3.ActivityStack

   ActivityStack是一个管理类，用来管理系统所有的Activity。
**1）ActivityStack中一些特殊状态的Activity**
  **ActivityRecord mPausingActivity**：正在暂停的Activity。
  **ActivityRecord mLastPausedActivity**：上一个已经暂停的Activity。
  **ActivityRecord mLastNoHistoryActivity**：最近一次没有历史纪录的Activity。
  **ActivityRecord mResumedActivity**：已经resume的Activity。
  **ActivityRecord mLastStartedActivity**：最近一次启动的Activity。
  **ActivityRecord mTranslucentActivityWaiting**：传递给convertToTranslucent方法的最上层的Activity。
**2）ActivityStack中重要的ArrayList**
  **ArrayList<TaskRecord> mTaskHistory**：所有没有被销毁的Activity任务栈。
  **ArrayList<ActivityRecord> mLRUActivities**：根据LRU算法存储的正在运行的Activity。
  **ArrayList<ActivityRecord> mNoAnimActivities**：不考虑动画转换的Activity。
  **ArrayList<TaskGroup> mValidateAppTokens**：用于和WindowManger验证应用令牌。

## 4.ActivityStackSupervisor

   ActivityStackSupervisor用于对ActivityStack进行管理，ActivityStackSupervisor在AMS的构造方法中通过调用createStackSupervisor进行创建。
**1）ActivityStackSupervisor中重要的ActivityStack**
  **ActivityStack mHomeStack**：用来存储Launch的所有Activity。
  **ActivityStack mFocusedStack**：表示当前正在接收输入或者启动下一个Activity的所有Activity。
  **ActivityStack mLastFocusedStack**：表示此前接收输入的所有Activity。

## 5.ActivityState

   ActivityState是一个枚举类，用来存储Activity的所有状态。
  **INITIALIZING
  RESUMED
  PAUSING
  PAUSED
  STOPPING
  STOPPED
  FINISHING
  DESTROYING
  DESTROYED**

# 五.Activity栈管理

## 1.Activity任务栈模型

![在这里插入图片描述](https://www.pianshen.com/images/303/597f3496a8e0b90d25fdfda0d498ffb7.png)
    一个ActivityStack包含一个或多个TaskRecord，一个TaskRecord包含一个或多个ActivityRecord。ActivityStack用来管理TaskRecord，TaskRecord用来管理ActivityRecord。

## 2.Activity的启动方式——LaunchMode

  **1）standard**：默认模式，每次启动都会创建一个Activity。
  **2）singleTop**：栈顶复用模式。若启动的Activity在栈顶存在，则不会创建Activity。同时该Activity的onNewIntent方法会被调用。
  **3）singleTask**：栈内复用模式。若启动的Activity在栈内存在，则不会创建Activity。同时该Activity的onNewIntent方法会被调用。
  **4）singleInstance**：单例模式，为启动的Activity创建一个新栈，该栈中只能有这一个Activity。

## 3.Intent与Activity相关的常用FLAG

  **1）FLAG_ACTIVITY_SINGLE_TOP**：同singleTop
  **2）FLAG_ACTIVITY_NEW_TASK**：同SingleTask。
  **3）FLAG_ACTIVITY_CLEAR_TOP**：若启动的Activity已经存在于栈内，则将它上面所有的Activity出栈，singleTask默认有此标记效果。
  **4）FLAG_ACTIVITY_NO_HISTORY**：Activity一旦退出，不会存在于栈中。对应android:noHistory。
  **5）FLAG_ACTIVITY_MULTIPLE_TASK**：需要和FLAG_ACTIVITY_NEW_TASK一起使用，系统会启动一个新栈来容纳新启动的Activity。
  **6）FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS**：Activity不会被放到最近启动的Activity列表。
  **7）FLAG_ACTIVITY_BROUGHT_TO_FRONT**：当启动方式为SingleTask时，系统自动附加。
  **8）FLAG_ACTIVITY_LAUNCHED_FROM_HISTORY**：当从历史记录中启动时，系统自动附加。
  **9）FLAG_ACTIVITY_CLEAR_TASK**：需要和FLAG_ACTIVITY_NEW_TASK一起使用，用于清除与启动的Activity相关栈的所有其它的Activity。

## 4.栈亲和度——taskTaffinity

   在AndroidManifest.xml中，通过android:taskTaffinity来指定Activity希望归属的栈。默认情况同一个应用程序进程启动的Activity有相同的taskTaffinity。
**1）taskTaffinity与FLAG_ACTIVITY_NEW_TASK或singleTask配合。**
  启动的Activity的taskTaffinity和栈的taskTaffinity相同时则加入该栈，若不同则创建新栈。
**2）taskTaffinity与allowTaskReparenting配合。**
  若allowTaskReparenting为true，则Activity具有转移能力。当与Activity的taskTaffinity相同的栈位于前台时，则Activity转移到与它的taskTaffinity相同的栈。