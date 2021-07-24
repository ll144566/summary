

# 1、实现方式



## 1.1、使用QMITestPro

### 1.1.1、操作步骤如下

![Step01](C:\Users\apricity.qian\Desktop\桌面文档\DTMF\步骤\Step01.png)

![Step02](C:\Users\apricity.qian\Desktop\桌面文档\DTMF\步骤\Step02.png)

![Step03](C:\Users\apricity.qian\Desktop\桌面文档\DTMF\步骤\Step03.png)

![Step04](C:\Users\apricity.qian\Desktop\桌面文档\DTMF\步骤\Step04.png)

### 1.1.2、DTMF消息详情

~~~markdown
11:03:19.935004	[0x1391]	QMI Link 2 TX PDU
IFType = 1
QmiLength = 24
QmiCtlFlags = 128
QmiType = VOICE
Service_Voice {
   ClientId = 4
   SduCtlFlags = IND
   TxId = 10
   MsgType = QMI_VOICE_DTMF_IND_MSG
   MsgLength = 12
   Service_Voc_V2 {
      Tlvs[0] {
         Type = 1
         Length = 4
         DTMF Information Tlv {
            call_id = 1
            dtmf_event = DTMF_EVENT_IP_INCOMING_DTMF_STOP
            digit_cnt = 1
            digit_buffer = 52
         }
      }
      Tlvs[1] {
         Type = 18
         Length = 2
         volume {
            volume = 6
         }
      }
   }
}
~~~





## 1.2、在qcril中添加注册代码

### 1.2.1、消息类型

 根据使用QMITestPro 发送的消息

![image-20210128192616739](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210128192616739.png)

找到对应结构体

~~~c
///qmi/services_ext/voice_service_v02.h
typedef struct {

  /* Optional */
  /*  DTMF Events */
  uint8_t reg_dtmf_events_valid;  /**< Must be set to true if reg_dtmf_events is being passed */
  uint8_t reg_dtmf_events;
  /**<   Values: \n
       - 0x00 -- Disable (default) \n
       - 0x01 -- Enable
  */

  ...
}voice_indication_register_req_msg_v02;  /* Message */
~~~

### 1.2.2、代码实现

~~~c++
void qcril_qmi_voice_ind_registrations
(
  void
)
{
  voice_indication_register_req_msg_v02  indication_req;
  voice_indication_register_resp_msg_v02 indication_resp_msg;

  ...
  memset(&indication_req, 0, sizeof(indication_req));
  memset(&indication_resp_msg, 0, sizeof(indication_resp_msg));

  indication_req.reg_dtmf_events_valid = TRUE;
  indication_req.reg_dtmf_events = 0x01;

  if (get_voice_modem_endpoint()->sendRawSync(QMI_VOICE_INDICATION_REGISTER_REQ_V02,
                                  &indication_req,
                                  sizeof(indication_req),
                                  &indication_resp_msg,
                                  sizeof(indication_resp_msg)
                                  ) != QMI_NO_ERR )
  {
    QCRIL_LOG_INFO("DTMF events haha indication register failed!");
  }
  else
  {
    QCRIL_LOG_INFO("DTMF events hehe registration error code: %d", indication_resp_msg.resp.error);
  }

  ...

} // qcril_qmi_voice_ind_registrations
~~~

### 1.2.3、DTMF消息详情

~~~markdown
11:03:20.113005	[0x1544]	QMI_MCS_QCSI_PKT
packetVersion = 2
V2 {
   MsgType = Indication
   Counter = 14
   ServiceId = VOICE
   MajorRev = 2
   MinorRev = 104
   ConHandle = 0x0000002B
   MsgId = 0x0000002B
   QmiLength = 12
   Service_VOICE {
      ServiceVOICEV2 {
         voice_dtmf {
            voice_dtmf_indTlvs[0] {
               Type = 0x01
               Length = 4
               dtmf_info {
                  call_id = 1
                  dtmf_event = DTMF_EVENT_IP_INCOMING_DTMF_START
                  digit_cnt = 1
                  digit_buffer = 7
               }
            }
            voice_dtmf_indTlvs[1] {
               Type = 0x12
               Length = 2
               volume {
                  volume = 6
               }
            }
         }
      }
   }
}


~~~

可以看出两种方式，DTMF消息结构类型是些差距的。

### 1.2.4、说明

ANDRIOD O  及其之前使用qcril_qmi_client_send_msg_sync() 发送

ANDRIOD O 之后使用get_voice_modem_endpoint()->sendRawSync()发送



## 1.3、DTMF消息上报到RILJ

### 1.3.1、实现思路

`VoiceModule.cpp->qcril_qmi_voice.cpp->qcril.cc->ril.cpp->ril_service.cpp->RadioIndication->RIL.java`

`VoiceModule.cpp->qcril_qmi_voice.cpp`这里高通代码里面已经完成。

### 1.3.2、具体实现代码

DTMF消息是由`VoiceModule.cpp`中传出去的，至于是谁调用了这里面的函数，就暂时不清楚了。这里的`mMessageHandler`是一个`unordered_map`，

而`VoiceModule::handleVoiceQmiIndMessage`就是接收DTMF消息的函数。

~~~c++
//@ VoiceModule.cpp
//path qcril-hal/modules/voice/src/VoiceModule.cpp
VoiceModule::VoiceModule(string name) : AddPendingMessageList(name) {
  mName = name;
  mLooper = nullptr;
  mInitialized = false;
  ModemEndPointFactory<VoiceModemEndPoint>::getInstance().buildEndPoint();

  /* _1 is the place holder for argument to handler method
     TODO: wrap function handler into a macro to make it more pleasing
  */
  using std::placeholders::_1;
  mMessageHandler = {
      // Qcril init complete message
      HANDLER(QcrilInitMessage, VoiceModule::handleQcrilInit),
      HANDLER(QcrilImsClientConnected, VoiceModule::handleQcrilImsClientConnected),
      // RIL request with translators

      ...

#ifdef USING_NAS_PUBLIC_API
      // NAS indication
      {VoiceRegistrationStatusChangeInd::get_class_message_id(),
       std::bind(&VoiceModule::HandleVoiceRegStatusIndMessage, this, _1)},
      {NetworkServiceRteChangeInd::get_class_message_id(),
       std::bind(&VoiceModule::HandleServiceRteChangeIndMessage, this, _1)},
#endif
      // QMI indication
      {REG_MSG("VOICE_QMI_IND"), std::bind(&VoiceModule::handleVoiceQmiIndMessage, this, _1)},
      // QMI Async response
      ...
  };
}
~~~

看一下`handleVoiceQmiIndMessage`，将消息传给了`qcril_qmi_voice_unsol_ind_cb_helper`。

~~~c++
//@ VoiceModule.cpp
//path qcril-hal/modules/voice/src/VoiceModule.cpp
void VoiceModule::handleVoiceQmiIndMessage(std::shared_ptr<Message> msg) {
  Log::getInstance().d("[" + mName + "]: Handling msg = " + msg->dump());
  std::shared_ptr<QmiIndMessage> shared_indMsg(
        std::static_pointer_cast<QmiIndMessage>(msg));

  QmiIndMsgDataStruct *indData = shared_indMsg->getData();
  if (indData != nullptr) {
    qcril_qmi_voice_unsol_ind_cb_helper(indData->msgId, indData->indData,
            indData->indSize);
  } else {
    Log::getInstance().d("Unexpected, null data from message");
  }
}
~~~

接着找被调用的函数。`dtmf_event`是事件类型，`digit_buffer`是具体点击的拨号盘按键，`dtmf_event`值为8和9的时候分别代表`DTMF_EVENT_IP_INCOMING_DTMF_START`和`DTMF_EVENT_IP_INCOMING_DTMF_STOP`，当`dtmf_event`值为8和9时经过`convertDtmfEvent`转换后`dtmfEvent`的值为`qcril::interfaces::DtmfEvent::UNKNOWN`。

关于`Dispatcher::getInstance().dispatchSync(msg)`这里的msg会被谁处理没在继续关注，但是`dtmf_event`值为8和9的时候这块代码是不会执行了。

后面的`qcril_unsol_resp_dtmf`是我后来添加的，因为`dtmf_ind->dtmf_info`已经包含了我们所需要的全部信息，所以这里只要传它就行了。

~~~c++
//@ qcril_qmi_voice.cpp
//path qcril-hal/modules/voice/src/qcril_qmi_voice.cpp
void qcril_qmi_voice_unsol_ind_cb_helper
(
  unsigned int   msg_id,
  unsigned char *decoded_payload,
  uint32_t       decoded_payload_len
)
{
  ...
    switch(msg_id)
    {
            ...
    case QMI_VOICE_DTMF_IND_V02:
      qcril_qmi_voice_dtmf_ind_hdlr(decoded_payload, decoded_payload_len);
      break;
            ...
    }
}

void qcril_qmi_voice_dtmf_ind_hdlr
(
  void *ind_data_ptr,
  uint32 /*ind_data_len*/
)
{
  if (ind_data_ptr != NULL)
  {
    voice_dtmf_ind_msg_v02 *dtmf_ind = (voice_dtmf_ind_msg_v02*) ind_data_ptr;
    qcril::interfaces::DtmfEvent dtmfEvent = convertDtmfEvent(dtmf_ind->dtmf_info.dtmf_event);
    QCRIL_LOG_INFO("DTMF digit_buffer = %s, type = %d",dtmf_ind->dtmf_info.digit_buffer,dtmf_ind->dtmf_info.dtmf_event);
    qcril_unsol_resp_dtmf(ind_data_ptr);
    if (dtmfEvent != qcril::interfaces::DtmfEvent::UNKNOWN)
    {
      auto msg = std::make_shared<QcRilUnsolDtmfMessage>(
          dtmf_ind->dtmf_info.call_id,
          dtmfEvent,
          dtmf_ind->dtmf_info.digit_buffer);
      if (msg)
      {
        if (dtmf_ind->on_length_valid)
        {
          msg->setOnLength(convertOnLength(dtmf_ind->on_length));
        }
        if (dtmf_ind->off_length_valid)
        {
          msg->setOffLength(convertOffLength(dtmf_ind->off_length));
        }
        Dispatcher::getInstance().dispatchSync(msg);
      }
    }else{
        qcril_unsol_resp_dtmf(&(dtmf_ind->dtmf_info));
    }
  }
}

qcril::interfaces::DtmfEvent convertDtmfEvent(dtmf_event_enum_v02 in) {
  qcril::interfaces::DtmfEvent ret = qcril::interfaces::DtmfEvent::UNKNOWN;
  switch(in)
  {
    case DTMF_EVENT_FWD_BURST_V02:
      ret = qcril::interfaces::DtmfEvent::FWD_BURST;
      break;
    case DTMF_EVENT_FWD_START_CONT_V02:
      ret = qcril::interfaces::DtmfEvent::FWD_START_CONT;
      break;
    case DTMF_EVENT_FWD_STOP_CONT_V02:
      ret = qcril::interfaces::DtmfEvent::FWD_STOP_CONT;
      break;
    default:
      break;
  }
  return ret;
}
~~~

`qcril_unsol_resp_dtmf`的具体实现在qcril.cc里面,这里为了方便所以直接写数字了。`qcril_response_api`里面放的是`rild.c`中`funcs = rilInit(&s_rilEnv, argc, rilArgv);`传入的`s_rilEnv`里面有三个结构体指针，目前看来似乎一样，暂不清楚有什么区别。这里使用的是`QCRIL_DEFAULT_INSTANCE_ID`。`OnUnsolicitedResponse`对应的函数为`RIL_onUnsolicitedResponse`，在`ril.cpp`中实现。

```c++
//@ qcril.cc
//path qcril-hal/qcril_qmi/qcril.cc

const RIL_RadioFunctions *legacy_RIL_Init
(
	...
  // o maintain compatibility with data and UIM code which use instance_id and may respond on "second instance" context
  qcril_response_api[ QCRIL_DEFAULT_INSTANCE_ID ] = (struct RIL_Env *) env;
  qcril_response_api[ QCRIL_SECOND_INSTANCE_ID ] = (struct RIL_Env *) env;
  // TODO_TSTS: Check if this is required. Seems not required.
  qcril_response_api[ QCRIL_THIRD_INSTANCE_ID ] = (struct RIL_Env *) env;
	...

} /* RIL_Init() */

void qcril_unsol_resp_dtmf(void *ind_data_ptr)
{
	int len = sizeof(voice_dtmf_info_type_v02);
	void *payload = (void *) qcril_malloc( len );
	memcpy( payload, ind_data_ptr, len );
	qcril_response_api[ QCRIL_DEFAULT_INSTANCE_ID ]->OnUnsolicitedResponse( 1050, payload,len );
}

//@rild.c
//path qcril-hal/qcrild/qcrild/rild.c
static struct RIL_Env s_rilEnv = {
    RIL_onRequestComplete,
    RIL_onUnsolicitedResponse,
    RIL_requestTimedCallback,
    RIL_onRequestAck
};
```

继续看`RIL_onUnsolicitedResponse`,在`ril_unsol_commands.h`中添加`{RIL_UNSOL_DTMF, radio::receiveDtmfInd, WAKE_PARTIAL}`，这样就可以调用到我们自己添加的函数了。

~~~c++
//@ ril.cpp
//path qcril-hal/qcrild/libril/ril.cpp
#ifndef QMI_RIL_UTF
#if defined(ANDROID_MULTI_SIM)
extern "C"
void RIL_onUnsolicitedResponse(int unsolResponse, const void *data,
                                size_t datalen, RIL_SOCKET_ID socket_id)
#else
extern "C"
void RIL_onUnsolicitedResponse(int unsolResponse, const void *data,
                                size_t datalen)
#endif
{
    int unsolResponseIndex;
    int ret;
    bool shouldScheduleTimeout = false;
    RIL_SOCKET_ID soc_id = RIL_SOCKET_1;

#if defined(ANDROID_MULTI_SIM)
    soc_id = socket_id;
#endif


    ...

    unsolResponseIndex = unsolResponse - RIL_UNSOL_RESPONSE_BASE;

    ...
    ret = s_unsolResponses[unsolResponseIndex].responseFunction(
            (int) soc_id, responseType, 0, RIL_E_SUCCESS, const_cast<void*>(data),
            datalen);

    
}
#endif

//@ril_unsol_commands.h
//path qcril-hal/qcrild/libril/ril_unsol_commands.h
#ifndef QMI_RIL_UTF
    ...
    {RIL_UNSOL_DTMF, radio::receiveDtmfInd, WAKE_PARTIAL},
#endif
~~~

`receiveDtmfInd`在`ril_service.cpp`中实现。

~~~c++
//@ ril_service.cpp
//path qcril-hal/qcrild/libril/ril_service.cpp
int radio::receiveDtmfInd(int slotId, int indicationType,
        int token, RIL_Errno e, void *response, size_t responseLen) {
	voice_dtmf_info_type_v02 *dtmf_info = (voice_dtmf_info_type_v02*) response;
	char *digit_buffer = dtmf_info->digit_buffer;
	QCRIL_LOG_DEBUG( "receiveDtmfInd666  %d  %s", dtmf_info->dtmf_event,digit_buffer);
	hidl_string msg = convertCharPtrToHidlString(digit_buffer);
	Return<void> retStatus = radioService[slotId]->mRadioIndication->receiveDtmf(dtmf_info->dtmf_event,msg);
	return 0;
}
~~~

`receiveDtmf`是新添加的函数，需要在`hardware/interfaces/radio/1.0/IRadioIndication.hal`声明

~~~c++
interface IRadioIndication {
	oneway receiveDtmf(int32_t type, string msg);
    ...
}
~~~

接下来就传到了java层,可以通过`ToneGenerator`播放DTMF声音了。



~~~java
//@ RadioIndication.java
//path frameworks/opt/telephony/src/java/com/android/internal/telephony/RadioIndication.java
public void receiveDtmf(int type,String msg) {
		mRil.processDTMF(msg, type);
    }

//@ RIL.java
//path frameworks/opt/telephony/src/java/com/android/internal/telephony/RIL.java
public void processDTMF(String tone, int type) {
    AudioManager audioManager = (AudioManager) mContext.getSystemService(Context.AUDIO_SERVICE);
    int ringerMode = audioManager.getRingerMode();
    if (ringerMode == AudioManager.RINGER_MODE_SILENT
        || ringerMode == AudioManager.RINGER_MODE_VIBRATE) {
        return;
    }
    synchronized (mToneGeneratorLock) {
        if (mToneGenerator == null||!mToneMap.containsKey(tone)) {
            return;
        }
        if (type==PLAY_DTMF){
            mToneGenerator.startTone(mToneMap.get(tone));
        }else {
            mToneGenerator.stopTone();
        }

    }
}
~~~

### 1.3.3、时序图

![image-20210220140834087](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210220140834087.png)

## 1.4、hal文件修改问题整理

### 1.4.1、在RadioIndication.hal文件中添加一个函数，编译报错

~~~markdown
ERROR: android.hardware.radio@1.0::IRadioIndication has hash a8bc838fcc35a6a10bfbe8ed7a1fef77c3c61a59c6c9823f01d1948a75ed3099 which does not match hash on record. This interface has been frozen. Do not change it!
ERROR: Could not parse android.hardware.radio.deprecated@1.0::IOemHook. Aborting.
~~~

**解决办法：**在`hardware/interfaces/current.txt`中将`android.hardware.radio@1.0::IRadioIndication`这一行的hash值修改为`a8bc838fcc35a6a10bfbe8ed7a1fef77c3c61a59c6c9823f01d1948a75ed3099 `

### 1.4.2、修改`current.txt`后编译继续报错

~~~markdown
error: VNDK library: android.hardware.radio@1.0's ABI has INCOMPATIBLE CHANGES Please check compatibility report at: out/soong/.intermediates/hardware/interfaces/radio/1.0/android.hardware.radio@1.0/android_arm64_armv8-a_vendor_shared/android.hardware.radio@1.0.so.abidiff
******************************************************
error: Please update ABI references with: $ANDROID_BUILD_TOP/development/vndk/tools/header-checker/utils/create_reference_dumps.py  -l android.hardware.radio@1.0
~~~

根据提示执行`development/vndk/tools/header-checker/utils/create_reference_dumps.py  -l android.hardware.radio@1.0`

### 1.4.3、根据提示执行有如下报错

~~~markdown
build/make/core/binary.mk:1320: error: vendor/qcom/proprietary/commonsys/securemsm/seccamera/service/jni/Android.mk: libseccamservice: C_INCLUDES must be under the source or output directories: /securemsm/QSEEComAPI.
20:10:14 ckati failed with: exit status 1
Traceback (most recent call last):
  File "development/vndk/tools/header-checker/utils/create_reference_dumps.py", line 254, in <module>
    main()
  File "development/vndk/tools/header-checker/utils/create_reference_dumps.py", line 245, in main
    num_processed = create_source_abi_reference_dumps_for_all_products(args)
  File "development/vndk/tools/header-checker/utils/create_reference_dumps.py", line 199, in create_source_abi_reference_dumps_for_all_products
    args.build_variant, targets)
  File "development/vndk/tools/header-checker/utils/create_reference_dumps.py", line 89, in make_libs_for_product
    make_libraries(product, variant, targets, libs, llndk_mode)
  File "/home/apricity/workspace/SC66_Android10.0_R03_r008/development/vndk/tools/header-checker/utils/utils.py", line 156, in make_libraries
    lsdump_paths = read_lsdump_paths(product, variant, targets, build=True)
  File "/home/apricity/workspace/SC66_Android10.0_R03_r008/development/vndk/tools/header-checker/utils/utils.py", line 226, in read_lsdump_paths
    make_targets(product, variant, [lsdump_paths_file_path])
  File "/home/apricity/workspace/SC66_Android10.0_R03_r008/development/vndk/tools/header-checker/utils/utils.py", line 146, in make_targets
    subprocess.check_call(make_cmd, cwd=AOSP_DIR)
  File "/usr/lib/python3.6/subprocess.py", line 311, in check_call
    raise CalledProcessError(retcode, cmd)
subprocess.CalledProcessError: Command '['build/soong/soong_ui.bash', '--make-mode', '-j', 'TARGET_PRODUCT=aosp_arm_ab', 'TARGET_BUILD_VARIANT=userdebug', 'out/target/product/generic_arm_ab/lsdump_paths.txt']' returned non-zero exit status 1.

~~~

后来发现在执行`development/vndk/tools/header-checker/utils/create_reference_dumps.py  -l android.hardware.radio@1.0`发现有如下提示

<font color=#ff0000>  making libs for aosp_arm_ab-userdebug </font>  

~~~markdown
$ development/vndk/tools/header-checker/utils/create_reference_dumps.py  -l android.hardware.radio@1.0
making libs for aosp_arm_ab-userdebug

~~~

经网上资料搜索，执行`development/vndk/tools/header-checker/utils/create_reference_dumps.py  -l android.hardware.radio@1.0 -products TARGET_PRODUCT`问题得到解决。其中TARGET_PRODUCT是项目的 product 名称,当前使用的是SC66的代码，所以对应TARGET_PRODUCT的值为sdm660_64

**在hardware/interfaces/radio中有4个RadioIndication.hal，是继承关系，所以后面仍会报错error: VNDK library: android.hardware.radio@1.1's ABI has INCOMPATIBLE CHANGES、 error: VNDK library: android.hardware.radio@1.2's ABI has INCOMPATIBLE CHANGES...**

**目前的办法是多次执行development/vndk/tools/header-checker/utils/create_reference_dumps.py  -l android.hardware.radio@1.x -products sdm660_64 （x为0-4）**



# 附录

高通关于DTMF的文档

**kba-170706193342_3_volte_ip_dtmf_function.pdf**

~~~markdown
- kba-170706193342_3_volte_ip_dtmf_function.pdf
- 大概意思是高通没有在RIL/Telephony实现接收处理，需要厂商自己实现
[Background]
For DTMF in normal CS voice call, in-band DTMF tone is sent by network, so modem will play it
with audio interface; however, the current IMS network does not send such in-band DTMF tone, so
modem team had FR#25100, in which two new DTMF events were introduced:
•DTMF_EVENT_IP_INCOMING_DTMF_START (0x08) -- Received an IP-start continuous DTMF
message
•DTMF_EVENT_IP_INCOMING_DTMF_STOP (0x09) -- Received an IP-stop continuous DTMF
message
[Analysis]
Qcril have defined enum value, but have not process these events.
typedef enum {
DTMF_EVENT_ENUM_MIN_ENUM_VAL_V02 = -2147483647, /**< To force a 32 bit signed enum.
Do not change or use*/
DTMF_EVENT_REV_BURST_V02 = 0x00, /**< Sends a CDMA-burst DTMF \n */
DTMF_EVENT_REV_START_CONT_V02 = 0x01, /**< Starts a continuous DTMF tone \n */
DTMF_EVENT_REV_STOP_CONT_V02 = 0x03, /**< Stops a continuous DTMF tone \n */
DTMF_EVENT_FWD_BURST_V02 = 0x05, /**< Received a CDMA-burst DTMF message \n */
DTMF_EVENT_FWD_START_CONT_V02 = 0x06, /**< Received a start-continuous DTMF tone
order \n */
DTMF_EVENT_FWD_STOP_CONT_V02 = 0x07, /**< Received a stop-continuous DTMF tone
order \n */
DTMF_EVENT_IP_INCOMING_DTMF_START_V02 = 0x08, /**< Received an IP-start continuous
DTMF message \n */
DTMF_EVENT_IP_INCOMING_DTMF_STOP_V02 = 0x09, /**< Received an IP-stop continuous
DTMF message */
DTMF_EVENT_ENUM_MAX_ENUM_VAL_V02 = 2147483647 /**< To force a 32 bit signed enum.
Do not change or use*/
}dtmf_event_enum_v02;
[Conclusion]
FR#25100 modem passes DTMF event to QCRIL, it does not play out. RIL/Telephony never got
any requirement to implement this on apps. So need OEM implement it.
With FR#44353 modem will start playing out via adsp. But that's for future targeted for AT 4.2.
~~~

**KBA-170713064404.pdf**

~~~markdown
- KBA-170713064404.pdf
- DTMF indication默认没有注册，厂商需要通过QMI自行注册才能接收到DTMF
Guidance for OEM implantation playing receiving direction DTMF.
Please refer to KBA-170706193342, since DTMF indication doesn’t register by default, OEM
need to enable register DTMF event through QMI, then DTMF events below would be reported
to AP, and OEM could handle playing receiving direction DTMF.
~~~

**kba-170723232827_3_how_to_config_modem_report_qmi_voice_dtmf_ind_to_ap.pdf**

~~~diff
[Background]
Sometimes OEM need modem report QMI_VOICE_DTMF_IND to AP, but qcril didn't reg this
indication now.
[Solution]
Till ANDRIOD O please use below code change:
First of all, you need to confirm if modem CM/IMS report DTMF event to QMI.
If yes, then we need qcril to reg this inidcation.
code change:
qcril_qmi_voice.c
qcril_qmi_voice_ind_registrations(){
...
{
QCRIL_LOG_INFO("conf_participants_events registration error code: %d",
indication_resp_msg.resp.error);
}
+memset(&indication_req, 0, sizeof(indication_req));
+memset(&indication_resp_msg, 0, sizeof(indication_resp_msg));
+
+indication_req.reg_dtmf_events_valid = TRUE;
+indication_req.reg_dtmf_events = 0x01;
+
+if ( qcril_qmi_client_send_msg_sync( QCRIL_QMI_CLIENT_VOICE,
+ QMI_VOICE_INDICATION_REGISTER_REQ_V02,
+ &indication_req,
+ sizeof(indication_req),
+ &indication_resp_msg,
+ sizeof(indication_resp_msg)
+ ) !=E_SUCCESS )
+{
+ QCRIL_LOG_INFO("DTMF events indication register failed!");
+}
+else+{
+ QCRIL_LOG_INFO("DTMF events registration error code: %d", indication_resp_msg.resp.error);
+}
disabled_screen_off_ind = FALSE;
QCRIL_LOG_FUNC_RETURN();
}
From ANDROID P onwards use below code changes:
qcril_qmi_voice.cc
qcril_qmi_voice_ind_registrations(){
...
{
QCRIL_LOG_INFO("conf_participants_events registration error code: %d",
indication_resp_msg.resp.error);
}
+memset(&indication_req, 0, sizeof(indication_req));
+memset(&indication_resp_msg, 0, sizeof(indication_resp_msg));
+
+indication_req.reg_dtmf_events_valid = TRUE;
+ indication_req.reg_dtmf_events= 0x01;
+if (get_voice_modem_endpoint()->sendRawSync(
QMI_VOICE_INDICATION_REGISTER_REQ_V02,
+&indication_req,
+sizeof(indication_req),
+ &indication_resp_msg,
+sizeof(indication_resp_msg)
+) != QMI_NO_ERR )
+{
+ QCRIL_LOG_INFO("DTMF events indication register failed!");
+}
+else
+{+ QCRIL_LOG_INFO("DTMF events registration error code: %d", indication_resp_msg.resp.error);
+}
disabled_screen_off_ind = FALSE;
QCRIL_LOG_FUNC_RETURN();
}
~~~

public static int getNetworkClass(int networkType) {
Switch (networkType) {
case NETWORK_TYPE_GPRS:
case NETWORK_TYPE_EDGE:
case NETWORK_TYPE_CDMA:
case NETWORK_TYPE_1xRTT:
case NETWORK_TYPE_IDEN:
return NETWORK_CLASS_2_G;
case NETWORK_TYPE_UMTS:
case NETWORK_TYPE_EVDO_0:
case NETWORK_TYPE_EVDO_A:
case NETWORK_TYPE_HSDPA:
case NETWORK_TYPE_HSUPA:
case NETWORK_TYPE_HSPA:
case NETWORK_TYPE_EVDO_B:
case NETWORK_TYPE_EHRPD:
case NETWORK_TYPE_HSPAP:
return NETWORK_CLASS_3_G;
case NETWORK_TYPE_LTE:
return NETWORK_CLASS_4_G;
default:
return NETWORK_CLASS_UNKNOWN;
}
}

然后下面是这几个常量的值。
/** Unknown network class. {@hide} */
public static final int NETWORK_CLASS_UNKNOWN = 0;
/** Class of broadly defined "2G" networks. {@hide} */
public static final int NETWORK_CLASS_2_G = 1;
/** Class of broadly defined "3G" networks. {@hide} */
public static final int NETWORK_CLASS_3_G = 2;
/** Class of broadly defined "4G" networks. {@hide} */
public static final int NETWORK_CLASS_4_G = 3;
