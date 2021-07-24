Apn参数解析
下面是配置一条APN信息的示例：

~~~xml
<apn carrier="中国移动彩信 (China Mobile)"
    mcc="460"
    mnc="00"
    apn="cmwap"
    proxy="10.0.0.172"
    port="80"
    mmsc="http://mmsc.monternet.com"
    mmsproxy="10.0.0.172"
    mmsport="80"
    user="mms"
    password="mms"
    type="mms"
    authtype="1"
    protocol="IPV4V6"
/>
~~~

其对应的属性含义如下：



|   参数   |                             作用                             |
| :------: | :----------------------------------------------------------: |
| carrier  |   apn的名字，可为空，只用来显示apn列表中此apn的显示名字。    |
|   mcc    |         由三位数组成。 用于识别移动用户的所在国家。          |
|   mnc    | 由两位或三位组成。 用于识别移动用户的归属PLMN。 MNC的长度（两位或三位数）取决于MCC的值。 |
|   apn    | APN网络标识（接入点名称），是APN参数中的必选组成部分。此标识由运营商分配。 |
|  proxy   |                      代理服务器的地址。                      |
|   port   |                     代理服务器的端口号。                     |
|   mmsc   |     中继服务器/多媒体消息业务中心，是彩信的交换服务器。      |
| mmsproxy |                    彩信代理服务器的地址。                    |
| mmsport  |                   彩信代理服务器的端口号。                   |
| protocol |                支持的协议，不配置默认为IPV4。                |
|   user   |                            用户。                            |
| password |                            密码。                            |
|   type   | 不同的apn type通常处理不同的业务，如cmiot的type为default，用来拨号上网，ims的type为ims，用来IMS服务，cmwap的type为mms，用来彩信服务，如果type为ia，则代表该apn是用来attach网络的 |
| authtype | apn的认证协议，PAP为口令认证协议，是二次握手机制。CHAP是质询握手认证协议，是三次握手机制None(0)、PAP(1)、CHAP(2)、PAP or CHAP(3) |



APN接入点类型

|  类型   | 作用                                                         |
| :-----: | ------------------------------------------------------------ |
| Default | 默认网络连接。                                               |
|   Mms   | 彩信专用连接，此连接与default类似，用于与载体的多媒体信息服务器对话的应用程序。 |
|  Supl   | 是Secure User Plane Location“安全用户面定位”的简写，此连接与default类似，用于帮助定位设备与载体的安全用户面定位服务器对话的应用程序。 |
|   Dun   | Dial Up Networking拨号网络的简称，此连接与default连接类似，用于执行一个拨号网络网桥，使载体能知道拨号网络流量的应用程序。 |
|  Hipri  | 高优先级网络，与default类似，但路由设置不同。只有当进程访问移动DNS服务器，并明确要求使用requestRouteToHost(int, int)才会使用此连接。 |


此表中的数据连接优先级是由低到高，即default数据连接的优先级最低，而hipri数据连接的优先级最高。比如：手机上网聊天，建立的是default数据连接。如果此时接到一条彩信，由于彩信的数据连接是mms，优先级比default高，所以会先断开default数据连接，建立mms数据连接，让手机先收到彩信。所以收发彩信的同时不能上网。（单条pdp连接的情况）



~~~java
//packages/providers/TelephonyProvider/src/com/android/providers/telephony/TelephonyProvider.java
public void onCreate(SQLiteDatabase db) {
    if (DBG) log("dbh.onCreate:+ db=" + db);
    createSimInfoTable(db, SIMINFO_TABLE);
    createCarriersTable(db, CARRIERS_TABLE);
    // if CarrierSettings app is installed, we expect it to do the initializiation instead
    if (apnSourceServiceExists(mContext)) {
        log("dbh.onCreate: Skipping apply APNs from xml.");
    } else {
        log("dbh.onCreate: Apply apns from xml.");
        initDatabase(db);
    }
    if (DBG) log("dbh.onCreate:- db=" + db);
}
~~~

接着看initDatabase，internal APNS data一般为空

~~~java
private void initDatabase(SQLiteDatabase db) {
    if (VDBG) log("dbh.initDatabase:+ db=" + db);
    // Read internal APNS data
    Resources r = mContext.getResources();
    XmlResourceParser parser = r.getXml(com.android.internal.R.xml.apns);
    int publicversion = -1;
    try {
        XmlUtils.beginDocument(parser, "apns");
        publicversion = Integer.parseInt(parser.getAttributeValue(null, "version"));
        loadApns(db, parser);
    } catch (Exception e) {
        loge("Got exception while loading APN database." + e);
    } finally {
        parser.close();
    }

    // Read external APNS data (partner-provided)
    XmlPullParser confparser = null;
    File confFile = getApnConfFile();

    FileReader confreader = null;
    if (DBG) log("confFile = " + confFile);
    try {
        confreader = new FileReader(confFile);
        confparser = Xml.newPullParser();
        confparser.setInput(confreader);
        XmlUtils.beginDocument(confparser, "apns");

        // Sanity check. Force internal version and confidential versions to agree
        int confversion = Integer.parseInt(confparser.getAttributeValue(null, "version"));
        if (publicversion != confversion) {
            log("initDatabase: throwing exception due to version mismatch");
            throw new IllegalStateException("Internal APNS file version doesn't match "
                                            + confFile.getAbsolutePath());
        }

        loadApns(db, confparser);
    } catch (FileNotFoundException e) {
        // It's ok if the file isn't found. It means there isn't a confidential file
        // Log.e(TAG, "File not found: '" + confFile.getAbsolutePath() + "'");
    } catch (Exception e) {
        loge("initDatabase: Exception while parsing '" + confFile.getAbsolutePath() + "'" +
             e);
    } finally {
        ...
    }
    if (VDBG) log("dbh.initDatabase:- db=" + db);

}
~~~

getApnConfFile根据lastModified time选择最后修改的

~~~java
private static final String PARTNER_APNS_PATH = "etc/apns-conf.xml";
private static final String OEM_APNS_PATH = "telephony/apns-conf.xml";
private static final String OTA_UPDATED_APNS_PATH = "misc/apns/apns-conf.xml";
private File getApnConfFile() {
    // Environment.getRootDirectory() is a fancy way of saying ANDROID_ROOT or "/system".
    File confFile = new File(Environment.getRootDirectory(), PARTNER_APNS_PATH);
    File oemConfFile =  new File(Environment.getOemDirectory(), OEM_APNS_PATH);
    File updatedConfFile = new File(Environment.getDataDirectory(), OTA_UPDATED_APNS_PATH);
    confFile = getNewerFile(confFile, oemConfFile);
    confFile = getNewerFile(confFile, updatedConfFile);
    return confFile;
}

private File getNewerFile(File sysApnFile, File altApnFile) {
    if (altApnFile.exists()) {
        // Alternate file exists. Use the newer one.
        long altFileTime = altApnFile.lastModified();
        long currFileTime = sysApnFile.lastModified();
        if (DBG) log("APNs Timestamp: altFileTime = " + altFileTime + " currFileTime = "
                     + currFileTime);

        // To get the latest version from OEM or System image
        if (altFileTime > currFileTime) {
            if (DBG) log("APNs Timestamp: Alternate image " + altApnFile.getPath() +
                         " is greater than System image");
            return altApnFile;
        }
    } else {
        // No Apn in alternate image, so load it from system image.
        if (DBG) log("No APNs in OEM image = " + altApnFile.getPath() +
                     " Load APNs from system image");
    }
    return sysApnFile;
}
~~~

loadApns向数据库telephony.db中的carriers表中插入数据

~~~java
private void loadApns(SQLiteDatabase db, XmlPullParser parser) {
    if (parser != null) {
        try {
            db.beginTransaction();
            XmlUtils.nextElement(parser);
            while (parser.getEventType() != XmlPullParser.END_DOCUMENT) {
                ContentValues row = getRow(parser);
                if (row == null) {
                    throw new XmlPullParserException("Expected 'apn' tag", parser, null);
                }
                insertAddingDefaults(db, row);
                XmlUtils.nextElement(parser);
            }
            db.setTransactionSuccessful();
        } catch (XmlPullParserException e) {
            loge("Got XmlPullParserException while loading apns." + e);
        } catch (IOException e) {
            loge("Got IOException while loading apns." + e);
        } catch (SQLException e) {
            loge("Got SQLException while loading apns." + e);
        } finally {
            db.endTransaction();
        }
    }
}

private ContentValues getRow(XmlPullParser parser) {
    if (!"apn".equals(parser.getName())) {
        return null;
    }

    ContentValues map = new ContentValues();

    String mcc = parser.getAttributeValue(null, "mcc");
    String mnc = parser.getAttributeValue(null, "mnc");
    String numeric = mcc + mnc;

    map.put(NUMERIC, numeric);
    map.put(MCC, mcc);
    map.put(MNC, mnc);
    map.put(NAME, parser.getAttributeValue(null, "carrier"));

    // do not add NULL to the map so that default values can be inserted in db
    addStringAttribute(parser, "apn", map, APN);
    addStringAttribute(parser, "user", map, USER);
    ...
    return map;
}

private void addBoolAttribute(XmlPullParser parser, String att,
                              ContentValues map, String key) {
    String val = parser.getAttributeValue(null, att);
    if (val != null) {
        map.put(key, Boolean.parseBoolean(val));
    }
}
~~~

关于设置中APN是否可编辑问题

在apns-conf.xml可设置单个apn是否可编辑，carrier_config_(对应mccmnc).xml根据mccmnc设置apn是否可编辑

~~~java
if (!isUserEdited && (mApnData.getInteger(USER_EDITABLE_INDEX, 1) == 0
                      || apnTypesMatch(mReadOnlyApnTypes, mApnData.getString(TYPE_INDEX)))) {
    Log.d(TAG, "onCreate: apnTypesMatch; read-only APN");
    mReadOnlyApn = true;
    disableAllFields();
} 
~~~

