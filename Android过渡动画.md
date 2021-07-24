Activity的切换动画指的是从一个activity跳转到另外一个activity时的动画。
它包括两个部分：
一部分是第一个activity退出时的动画；
另外一部分时第二个activity进入时的动画；

下面简单介绍下几种修改方式

## 1、overridePendingTransition

在Android的2.0版本之后，有了一个函数来帮我们实现这个动画。这个函数就是overridePendingTransition(int enterAnim, int exitAnim)，enterAnim是第二个activity进入时的动画，exitAnim是第一个activity退出时的动画。如下，其中R.anim.slide_in_left和R.anim.slide_out_right是android自带的动画，用户也可以自己定义动画，建议在startActivity后或onPause方法中调用overridePendingTransition，否则可能会不生效。

~~~java
//添加位置
startActivity(intent);
overridePendingTransition(enterAnim,exitAnim) 
//或
protected void onPause() {
    super.onPause();
    overridePendingTransition(enterAnim,exitAnim)
}
//overridePendingTransition(0,0）表示无动画
~~~

当不想要Activity到另一个Activity的过度动画时候可以设置为overridePendingTransition(0,0)。另外经验证发现enterAnim为0时，将无法看到exitAnim动画

> **注意：** 进入和退出动画的时间设置要一样，不然会有黑屏效果。例如：如果打开从一个ActivityA打开一个另外一个ActivityB，如果进入界面动画快，退出界面动画慢，进入动画还没有执行完，退出动画已执行完,ActivityA会变成黑屏。如果一个需要动画，另外一个不需要变化，也请设置时间相同的没有任何变化的动画，防止黑屏出现。

如下，不平移无动画，仅有持续事件

~~~xml
<?xml version="1.0" encoding="utf-8"?>
<translate xmlns:android="http://schemas.android.com/apk/res/android"
    android:fromXDelta="0"
    android:toXDelta="0"
    android:duration="2000">
</translate>
~~~

## 2、使用ActivityOptions + Transition

先看下ActivityOptions里面几个函数

~~~java
/**
 * 和overridePendingTransition类似,设置跳转时候的进入动画和退出动画
 */
public static ActivityOptions makeCustomAnimation(Context context, int enterResId, int exitResId);

/**
 * 通过把要进入的Activity通过放大的效果过渡进去
 * 举一个简单的例子来理解source=view,startX=view.getWidth(),startY=view.getHeight(),startWidth=0,startHeight=0
 * 表明新的Activity从view的中心从无到有慢慢放大的过程
 */
public static ActivityOptions makeScaleUpAnimation(View source, int startX, int startY, int width, int height);

/**
 * 通过放大一个图片过渡到新的Activity
 */
public static ActivityOptions makeThumbnailScaleUpAnimation(View source, Bitmap thumbnail, int startX, int startY);

/**
 * 场景动画，体现在两个Activity中的某些view协同去完成过渡动画效果
 */
public static ActivityOptions makeSceneTransitionAnimation(Activity activity, View sharedElement, String sharedElementName);

/**
 * 场景动画，同上是对多个View同时起作用
 */
public static ActivityOptions makeSceneTransitionAnimation(Activity activity, android.util.Pair<View, String>... sharedElements);
~~~

其中使用的比较多的是makeSceneTransitionAnimation

使用前先打开窗口内容转换开关，有两种方式

1. 在风格定义中设置：

```xml
<style name="BaseAppTheme" parent="Theme.AppCompat.Light">
  <!-- enable window content transitions -->
  <item name="android:windowContentTransitions">true</item>
</style>
```

2. 在代码中设置

~~~java
//注意需要在setContentView前调用
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState)
    getWindow().requestFeature(Window.FEATURE_CONTENT_TRANSITIONS)
}
~~~

接下来就可以设置动画了

可通过getWindow().setXXXXX()设置

1. setExitTransition() - 当A startB时，使A中的View退出场景的transition    在A中设置

2. setEnterTransition() - 当A startB时，使B中的View进入场景的transition    在B中设置

3. setReturnTransition() - 当B 返回A时，使B中的View退出场景的transition  在B中设置

4. setReenterTransition() - 当B 返回A时，使A中的View进入场景的transition   在A中设置

启动Activity时要用startActivity的重载方法。

~~~java
startActivity(intent, ActivityOptions.makeSceneTransitionAnimation(MainActivity.this).toBundle());
~~~



> **注意**：如果没有指定`returnTransition`和`reenterTransition`，返回 MainActivity 时会分别执行反转的进入和退出转换,当B的启动模式为SingleInstance时setReenterTransition将不会起作用。
>
> 还有一点，当不设置过渡动画时，启动模式为SingleInstance的activity在被启动和退出时的动画会与其它启动模式大的过渡动画不同。



## 3、使用style的方式定义Activity的切换动画



通过style定义过渡动画方式如下：(但不清楚为何验证时并未生效)

~~~xml
<resources xmlns:tools="http://schemas.android.com/tools">
    <!-- Base application theme. -->
    <style name="Theme.Launcher" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <!-- Primary brand color. -->
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <!-- Secondary brand color. -->
        <item name="colorSecondary">@color/teal_200</item>
        <item name="colorSecondaryVariant">@color/teal_700</item>
        <item name="colorOnSecondary">@color/black</item>
        <!-- Status bar color. -->
        <item name="android:statusBarColor" tools:targetApi="l">?attr/colorPrimaryVariant</item>
        <!-- Customize your theme here. -->
         <item name="android:windowContentTransitions">true</item>
        <item name="android:windowAnimationStyle">@style/anim</item>
    </style>
    
<!-- 使用style方式定义activity切换动画 -->
    <style name="anim">
        <item name="android:activityOpenEnterAnimation">@anim/slide_in_top</item>
        <item name="android:activityOpenExitAnimation">@anim/slide_in_top</item>
    </style>
</resources>


~~~


而在windowAnimationStyle中存在四种动画：

activityOpenEnterAnimation // 用于设置打开新的Activity并进入新的Activity展示的动画
activityOpenExitAnimation  // 用于设置打开新的Activity并销毁之前的Activity展示的动画
activityCloseEnterAnimation  // 用于设置关闭当前Activity进入上一个Activity展示的动画
activityCloseExitAnimation  // 用于设置关闭当前Activity时展示的动画
