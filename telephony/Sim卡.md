1，手机启动时，

根据SIM卡的类型，进入SIMRecords, 开始探测SIM卡的状态，因为，有些SIM卡会设置有PIN码，如果SIM卡有PIN码的话，手机会弹出输入PIN码的框，等待用户进行解码，注意，这个时候，如果PIN码如果没有解的话，手机是不会去读SIM卡的，因为，读SIM卡时，必须通过PIN才能去读，只有一些比较特殊的字段，可以不用,比如ECC 也就是紧急呼叫号码（一般存在卡上，运营商定制的）。同时，这PIN码未解的情况，手机中SIM卡的状态也是PIN_REQURIED_BLOCK,

2,当解完PIN码，或是手机没有设置PIN码，这时，手机的会探测到SIM是READY的状态，手机只有检测到SIM READY，才会发出读卡的请求。







UiccController收到以下三条消息的时候：

1）IccStatus变化的主动上报： EVENT_ICC_STATUS_CHANGED

```
F:\ubuntu\code\android-p\frameworks\opt\telephony\src\java\com\android\internal\telephony\uicc\UiccController.java1                 case EVENT_ICC_STATUS_CHANGED:
2                     if (DBG) log("Received EVENT_ICC_STATUS_CHANGED, calling getIccCardStatus");
3                     mCis[phoneId].getIccCardStatus(obtainMessage(EVENT_GET_ICC_STATUS_DONE,
4                             phoneId));
5                     break;
```

2）Radio状态变为Available或者On：EVENT_RADIO_AVAILABLE or EVENT_RADIO_ON

```
1                 case EVENT_RADIO_AVAILABLE:
2                 case EVENT_RADIO_ON:
3                     if (DBG) {
4                         log("Received EVENT_RADIO_AVAILABLE/EVENT_RADIO_ON, calling "
5                                 + "getIccCardStatus");
6                     }
7                     mCis[phoneId].getIccCardStatus(obtainMessage(EVENT_GET_ICC_STATUS_DONE,
8                             phoneId));
```

3）SIM卡信息刷新（为RESET或INIT时）：EVENT_SIM_REFRESH

```
1     private void onSimRefresh(AsyncResult ar, Integer index) {
2         // The card status could have changed. Get the latest state.
3         mCis[index].getIccCardStatus(obtainMessage(EVENT_GET_ICC_STATUS_DONE, index));
4     }
```

会触发向底层IccCardStatus的查询（见上面红字部分）。

```
1 mCi.getIccCardStatus(obtainMessage(EVENT_GET_ICC_STATUS_DONE, index));
```
