~~~java
//@ SimSettings.java
//path vendor/qcom/proprietary/commonsys/telephony-apps/SimSettings/src/com/qualcomm/qti/simsettings/SimSettings.java
private void updateSmsValues() {//短信
    SubscriptionInfo sir = mSubscriptionManager.getActiveSubscriptionInfo(mSubscriptionManager.getDefaultSmsSubscriptionId());
    simPref.setSummary(sir.getDisplayName());
    simPref.setEnabled(mSelectableSubInfos.size() > 1  && !isAirplaneModeOn());
}

private void updateCellularDataValues() {//流量
    final SubscriptionInfo sir = mSubscriptionManager.getDefaultDataSubscriptionInfo();
    simPref.setTitle(R.string.cellular_data_title);
    simPref.setSummary(sir.getDisplayName());
}

private void updateCallValues() {
    final TelecomManager telecomManager = TelecomManager.from(mContext);
    final PhoneAccountHandle phoneAccount = telecomManager.getUserSelectedOutgoingPhoneAccount();
    PhoneAccount phoneaccount = telecomManager.getPhoneAccount(phoneAccount);
    simPref.setSummary((String) phoneaccount.getLabel());
}

//@ SubscriptionManage.java
//path frameworks/base/telephony/java/android/telephony/SubscriptionManage.java
public SubscriptionInfo getDefaultDataSubscriptionInfo() {
    return getActiveSubscriptionInfo(getDefaultDataSubscriptionId());
}
~~~

getDefaultDataSubscriptionInfo实际使用的还是getActiveSubscriptionInfo，默认通话卡通过PhoneAccountHandle获取。

目前只有数据通道显示会在启用卡1后恢复原始状态。

默认数据卡对应于/data/system/users/0/settings_global.xml下的multi_sim_data_call，其值一般通过SettingsProvider修改。

通过adb shell settings get global multi_sim_data_call获取默认数据卡值是没问题的，在启用卡1启用后发现如下log

`Notifying for 0: content://settings/global/multi_sim_data_call`

是在SettingsProvider的handleMessage中打印出的，说明multi_sim_data_call被修改过

~~~java
//@ SettingsProvider.java
//path frameworks/base/packages/SettingsProvider/src/com/android/providers/settings/SettingsProvider.java
public void handleMessage(Message msg) {
    switch (msg.what) {
        case MSG_NOTIFY_URI_CHANGED: {
            Slog.v(LOG_TAG, "Notifying for " + userId + ": " + uri);
        } break;
    }
}
~~~



通过打印调用栈只找到了SettingsProvider.call。暂不清楚是哪里修改了multi_sim_data_call。

~~~
2021-02-07 20:05:29.732 1435-2030/system_process D/1008682: onCreate: java.lang.Throwable: content://settings/global/multi_sim_data_call
        at com.android.providers.settings.SettingsProvider$SettingsRegistry.notifyGlobalSettingChangeForRunningUsers(SettingsProvider.java:2818)
        at com.android.providers.settings.SettingsProvider$SettingsRegistry.notifyForSettingsChange(SettingsProvider.java:2764)
        at com.android.providers.settings.SettingsProvider$SettingsRegistry.insertSettingLocked(SettingsProvider.java:2402)
        at com.android.providers.settings.SettingsProvider.mutateGlobalSetting(SettingsProvider.java:1033)
        at com.android.providers.settings.SettingsProvider.insertGlobalSetting(SettingsProvider.java:991)
        at com.android.providers.settings.SettingsProvider.call(SettingsProvider.java:403)
        at android.content.ContentProvider$Transport.call(ContentProvider.java:404)
        at android.content.ContentProviderNative.onTransact(ContentProviderNative.java:272)
        at android.os.Binder.execTransact(Binder.java:731)
~~~





~~~
2021-02-08 11:11:04.642 2273-2273/com.android.phone D/1122334455: java.lang.Throwable: subId = 1
        at com.qualcomm.qti.internal.telephony.QtiSubscriptionController.setDefaultDataSubId(QtiSubscriptionController.java:251)
        at com.qualcomm.qti.internal.telephony.QtiSubscriptionController.handleDataPreference(QtiSubscriptionController.java:492)
        at com.qualcomm.qti.internal.telephony.QtiSubscriptionController.updateUserPreferences(QtiSubscriptionController.java:437)
        at com.qualcomm.qti.internal.telephony.QtiUiccCardProvisioner.queryUiccProvisionInfo(QtiUiccCardProvisioner.java:444)
        at com.qualcomm.qti.internal.telephony.QtiUiccCardProvisioner.handleUnsolManualProvisionEvent(QtiUiccCardProvisioner.java:351)
        at com.qualcomm.qti.internal.telephony.QtiUiccCardProvisioner.handleMessage(QtiUiccCardProvisioner.java:281)
        at android.os.Handler.dispatchMessage(Handler.java:106)
        at android.os.Looper.loop(Looper.java:193)
        at android.app.ActivityThread.main(ActivityThread.java:6746)
        at java.lang.reflect.Method.invoke(Native Method)
        at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:493)
        at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:858)

~~~





~~~
2021-02-08 13:27:45.265 2263-2263/? D/1001086: java.lang.Throwable: android.os.AsyncResult@de61f6e
        at com.qualcomm.qcrilhook.QcRilHook.notifyRegistrants(QcRilHook.java:1730)
        at com.qualcomm.qcrilhook.QcRilHook$1.onReceive(QcRilHook.java:176)
        at android.app.LoadedApk$ReceiverDispatcher$Args.lambda$getRunnable$0(LoadedApk.java:1391)
        at android.app.-$$Lambda$LoadedApk$ReceiverDispatcher$Args$_BumDX2UKsnxLVrE6UJsJZkotuA.run(Unknown Source:2)
        at android.os.Handler.handleCallback(Handler.java:873)
        at android.os.Handler.dispatchMessage(Handler.java:99)
        at android.os.Looper.loop(Looper.java:193)
        at android.app.ActivityThread.main(ActivityThread.java:6746)
        at java.lang.reflect.Method.invoke(Native Method)
        at com.android.internal.os.RuntimeInit$MethodAndArgsCaller.run(RuntimeInit.java:493)
        at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:858)
~~~

