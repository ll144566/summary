在Android中我们可以通过下面这段代码获取SIM的iccid

```java
TelephonyManager telephonyManager = (TelephonyManager) getSystemService(TELEPHONY_SERVICE); 
String simSerialNumber = telephonyManager.getSimSerialNumber();
```

注：ICCID （Integrate circuit card identity ） 集成电路卡识别码（固化在手机SIM 卡中） ICCID 为IC 卡的唯一识别号码，共有20 位数字组成。

```java
//frameworks/base/telephony/java/android/telephony/TelephonyManager.java

public String getSimSerialNumber() {
    return getSimSerialNumber(getSubId());
}

public String getSimSerialNumber(int subId) {
    android.util.SeempLog.record_str(388, ""+subId);
    try {
        IPhoneSubInfo info = getSubscriberInfo();
        if (info == null)
            return null;
        return info.getIccSerialNumberForSubscriber(subId, mContext.getOpPackageName());
    } catch (RemoteException ex) {
        return null;
    } catch (NullPointerException ex) {
        // This could happen before phone restarts due to crashing
        return null;
    }
}
```

getIccSerialNumberForSubscriber是在PhoneSubInfoController.java中实现，具体方式如下：

```java
//frameworks/opt/telephony/src/java/com/android/internal/telephony/PhoneSubInfoController.java
public String getIccSerialNumberForSubscriber(int subId, String callingPackage) {
	return callPhoneMethodForSubIdWithReadSubscriberIdentifiersCheck(subId, callingPackage,
                "getIccSerialNumber", (phone) -> phone.getIccSerialNumber());
}
//这里使用了Lambda ，不过最终返回的还是phone.getIccSerialNumber()
```

getIccSerialNumber是在GsmCdmaPhone.java实现：

```java
frameworks/opt/telephony/src/java/com/android/internal/telephony/Phone.java
    
public String getIccSerialNumber() {
    IccRecords r = mIccRecords.get();
    return (r != null) ? r.getIccId() : null;
}
```

getIccId是IccRecords.java中定义的，但其赋值是在IccRecords的子类SIMRecords.java中赋值的

```java
//frameworks/opt/telephony/src/java/com/android/internal/telephony/uicc/SIMRecords.java
public void handleMessage(@NonNull Message msg) {
    ...
    case EVENT_GET_ICCID_DONE:
        isRecordLoadResponse = true;
        mEssentialRecordsToLoad -= 1;

        ar = (AsyncResult) msg.obj;
        data = (byte[]) ar.result;

        if (ar.exception != null) {
            break;
        }

        mIccId = IccUtils.bcdToString(data, 0, data.length);
        mFullIccId = IccUtils.bchToString(data, 0, data.length);

        log("iccid: " + SubscriptionInfo.givePrintableIccid(mFullIccId));
        break;
    ...
}


```

这里会调用RIL.java里的iccIOForApp向modem发送查询请求，有结果返回后便会调用EVENT_GET_ICCID_DONE对mIccId进行赋值

```java
//frameworks/opt/telephony/src/java/com/android/internal/telephony/uicc/IccUtils.java

//Decode cdma byte into String.
public static String
    bcdToString(byte[] data, int offset, int length) {
    StringBuilder ret = new StringBuilder(length*2);

    for (int i = offset ; i < offset + length ; i++) {
        int v;

        v = data[i] & 0xf;
        if (v > 9)  break;
        ret.append((char)('0' + v));

        v = (data[i] >> 4) & 0xf;
        // Some PLMNs have 'f' as high nibble, ignore it
        if (v == 0xf) continue;
        if (v > 9)  break;
        ret.append((char)('0' + v));
    }

    return ret.toString();
}    
```

可以看到在bcdToString时，如果data里面包含非0-9的字符，则中止循环。

```java
//frameworks/opt/telephony/src/java/com/android/internal/telephony/uicc/IccUtils.java

//Some fields (like ICC ID) in GSM SIMs are stored as nibble-swizzled BCH
public static String
    bchToString(byte[] data, int offset, int length) {
    StringBuilder ret = new StringBuilder(length*2);

    for (int i = offset ; i < offset + length ; i++) {
        int v;

        v = data[i] & 0xf;
        ret.append(HEX_CHARS[v]);

        v = (data[i] >> 4) & 0xf;
        ret.append(HEX_CHARS[v]);
    }

    return ret.toString();
}
private static final char[] HEX_CHARS = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'
};
```

此时获取到的iccid才是完整的，然而现在很多sim卡的iccid包含0-f之外的字符，还是不能取到完整的iccid