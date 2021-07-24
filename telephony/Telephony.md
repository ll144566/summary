消息主要分两种：一种是RILJ主动发送的请求（solicited），常见的有`RIL_REQUEST_GET_SIM_STATUS`(获取SIM卡状态）， `RIL_REQUEST_DIAL`(拨打电话），`RIL_REQUEST_SEND_SMS`（发送短信）， `RIL_REQUEST_GET_CURRENT_CALLS`（获取当前通话状态），`RIL_REQUEST_VOICE_REGISTRATION_STATE`（获取网络状态）； 另一种则是从CP主动上报给RIL的消息（unsolicited)，如网络状态发生变化时，CP会上报`RIL_UNSOL_RESPONSE_VOICE_NETWORK_STATE_CHANGED`，有新短信时，会上报`RIL_UNSOL_RESPONSE_NEW_SMS`，有来电时会上报`RIL_UNSOL_CALL_RING`。





在Android平台中，RIL层位于Framework层与modem之间，分成两个部分：一部分是rild,它创建socket服务与framework层进行通信；一部分是Vendor RIL，在高通平台中称为qcril。





AMSS：Advanced Mobile Subscriber Software

ril：Radio Interface Layer

qcril：qualcomm radio interface layer 高通提供的ril层接口

QMI: Qualcomm Modem Interface 高通提供的与modem交互的接口





```java
qmi_client_send_msg_sync发送

05:17:25.497450	[0x1544]	QMI_MCS_QCSI_PKT
packetVersion = 2
V2 {
   MsgType = Request
   Counter = 1
   ServiceId = VOICE
   MajorRev = 2
   MinorRev = 104
   ConHandle = 0x000000B2
   MsgId = 0x00000003
   QmiLength = 4
   Service_VOICE {
      ServiceVOICEV2 {
         voice_indication_register {
            voice_indication_register_reqTlvs[0] {
               Type = 0x10
               Length = 1
               reg_dtmf_events {
                  reg_dtmf_events = true
               }
            }
         }
      }
   }
}


05:20:11.497241	[0x1544]	QMI_MCS_QCSI_PKT
packetVersion = 2
V2 {
   MsgType = Response
   Counter = 1
   ServiceId = VOICE
   MajorRev = 2
   MinorRev = 104
   ConHandle = 0x000000B3
   MsgId = 0x00000003
   QmiLength = 7
   Service_VOICE {
      ServiceVOICEV2 {
         voice_indication_register {
            voice_indication_register_respTlvs[0] {
               Type = 0x02
               Length = 4
               resp {
                  result = QMI_RESULT_SUCCESS
                  error = QMI_ERR_NONE
               }
            }
         }
      }
   }
}
```











1. DTMF信号处理主要涉及到的文件：

package/apps/phone/src/com/android/phone/InCallScreen.java: 是拨打电话，接通电话所产生的界面。

package/apps/phone/src/com/android/phone/DTMFTwelveKeyDialer.java: 用于处理当用户按键的操作，如处理DTMF按键的信号。在此文件中，当用户按下软键盘上得键时，会调用onKeyDown()来处理，onKeyDown()会继续调用processDtmf()来处里DTMF按键。然后会继续调用ril.java中的startDtmf()函数发送到ril层处理。







紧急号码的来源--三种
手机中内置----3GPP协议中规定的这8个号码
存在SIM/USIM卡中的
当插入SIM卡时从网络中获取的





~~~markdown
信号值由下往上的流程  
1.modem获取信号值 
Qmi_nas.c (amss\mpss.ta.2.2\modem_proc\mmcp\mmode\qmi\src) qmi_nasi_get_signal_strength  
2.通过qmi给ril 
Qcril_qmi_nas.c (android\vendor\qcom\proprietary\qcril\qcril_qmi) qcril_qmi_nas_signal_strength_con_conv_cache2ril  
3.这里会打一个log，搜索这里的log，便可以得知modem给ril的各个信号值 
qcril_qmi_nas_dump_sign_strength_report 
void qcril_qmi_nas_dump_sign_strength_report(RIL_SignalStrength* ril_signal_strength) { 
    QCRIL_LOG_FUNC_ENTRY();  
    QCRIL_LOG_INFO( "..GW");     QCRIL_LOG_INFO( ".. signalStrength %d, bitErrorRate %d", ril_signal_strength->GW_SignalStrength.signalStrength, 
                                                             ril_signal_strength->GW_SignalStrength.bitErrorRate );  
    QCRIL_LOG_INFO( "..TDSCDMA"); #ifndef QMI_RIL_UTF     QCRIL_LOG_INFO( ".. signalStrength %d", ril_signal_strength->TD_SCDMA_SignalStrength.rscp ); #endif  
    QCRIL_LOG_INFO( "..CDMA");     QCRIL_LOG_INFO( ".. dbm %d, ecio %d ", ril_signal_strength->CDMA_SignalStrength.dbm, 
                                                             ril_signal_strength->CDMA_SignalStrength.ecio );  
    QCRIL_LOG_INFO( "..EVDO");     QCRIL_LOG_INFO( ".. dbm %d, ecio %d, signalNoiseRatio %d", ril_signal_strength->EVDO_SignalStrength.dbm, 
                                                             ril_signal_strength->EVDO_SignalStrength.ecio, 
                                                             ril_signal_strength->EVDO_SignalStrength.signalNoiseRatio );  
    QCRIL_LOG_INFO( "..LTE"); 

    QCRIL_LOG_INFO( ".. signalStrength %d, rsrp %d, rsrq %d, rsnnr %d", 

ril_signal_strength->LTE_SignalStrength.signalStrength, 
                                                              ril_signal_strength->LTE_SignalStrength.rsrp, 
                                                              ril_signal_strength->LTE_SignalStrength.rsrq, 
                                                              ril_signal_strength->LTE_SignalStrength.rssnr );  
    QCRIL_LOG_FUNC_RETURN(); }  
4.往上再给Qcril_qmi_nas的qcril_qmi_nas_request_signal_strength Qcril_qmi_nas.c (android\vendor\qcom\proprietary\qcril\qcril_qmi) qcril_qmi_nas_request_signal_strength  
5.往上，接受ril的RIL_REQUEST_SIGNAL_STRENGTH 请求 
Qcril.c (android\vendor\qcom\proprietary\qcril\qcril_qmi) qcril_event_table 
/* 19 - RIL_REQUEST_SIGNAL_STRENGTH */ { QCRIL_REG_ALL_ACTIVE_STATES( RIL_REQUEST_SIGNAL_STRENGTH, qcril_qmi_nas_request_signal_strength ) },  
6.往上，给RIL的getSignalStrength 
RIL.java (android\frameworks\opt\telephony\src\java\com\android\internal\telephony) getSignalStrength  
7.往上给GSST的queueNextSignalStrengthPoll 
GsmServiceStateTracker.java 
(android\frameworks\opt\telephony\src\java\com\android\internal\telephony\gsm) handleMessage 
EVENT_SIM_READY 
EVENT_GET_SIGNAL_STRENGTH queueNextSignalStrengthPoll  
8.往上给SST的onSignalStrengthResult和notifySignalStrength ServiceStateTracker.java 
(frameworks\opt\telephony\src\java\com\android\internal\telephony) onSignalStrengthResult notifySignalStrength  
9.往上给PhoneBase的notifySignalStrength 
PhoneBase.java (frameworks\opt\telephony\src\java\com\android\internal\telephony) notifySignalStrength

10.往上给DefaultPhoneNotifier的notifySignalStrength 
DefaultPhoneNotifier.java 
(frameworks\opt\telephony\src\java\com\android\internal\telephony) notifySignalStrength 
Rlog.d(LOG_TAG, "notifySignalStrength: mRegistry=" + mRegistry 
        + " ss=" + sender.getSignalStrength() + " sender=" + sender);  
11.往上给TelephonyRegistry的notifySignalStrengthForSubscriber 
TelephonyRegistry.java (frameworks\base\services\core\java\com\android\server) notifySignalStrengthForSubscriber  
如此，SignalStrength的各个成员变量便有了对应的信号值，做为显示几格的标准 
~~~





android P上面的qcril已经使用qcril-hal新架构















~~~c++
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
    QCRIL_LOG_INFO("DTMF digit_buffer = %c, type = %d",(dtmf_ind->dtmf_info.digit_buffer)[0],(int)dtmfEvent);
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
    }
  }
}

//include/interfaces/voice/QcRilUnsolDtmfMessage.h

~~~



























































https://github.com/SleepyMorning/Notes/blob/master/Telephony%E4%B8%93%E9%A2%98/ril/%E9%AB%98%E9%80%9ARIL%E5%88%9D%E5%A7%8B%E5%8C%96%E6%B5%81%E7%A8%8B.md

# Qcril的基本机制

@(Qcril)[高通|rild|Telephony]

> **声明：** **文中涉及高通平台精简后的部分源码，如有侵权，请联系作者删除**。

`rild`是由C/C++编写的linux域后台进程，是连接Java Telephony Frameworks和Modem的中间传输层。

`Qcril`是高通平台`rild`的平台RIL。

## rild - RIL入口

`rild`的入口函数`main`的主要流程如下，

```
//@rild.c

int main(int argc, char **argv) {
    ...
    //加载动态链接库 rilLibPath
    dlHandle = dlopen(rilLibPath, RTLD_NOW);
    ...
    //获取入口 RIL_Init
    rilInit = (const RIL_RadioFunctions *(*)(const struct RIL_Env *, int, char **))
        dlsym(dlHandle, "RIL_Init");
    ...
    //调用 RIL_Init 完成模块初始化，并返回一个RIL_RadioFunctions结构体
    funcs = rilInit(&s_rilEnv, argc, rilArgv);
    ...
    //将返回的结构体注册在本地
    RIL_register(funcs);
    ...
    while (true) { //保证进程不退出
        sleep(UINT32_MAX);
    }
}
```

在main函数中`rilLibPath`和`s_rilEnv`是值得关注的两个变量，前者代表高通提供的RIL实现方案（即Qcril动态链接库路径），后者代表一个`RIL_Env `结构体，包含了一组向Java Telephony Frameworks返回请求结果的函数。

下面是`s_rilEnv`的定义和类型，

```
//@rild.c
static struct RIL_Env s_rilEnv = {
    RIL_onRequestComplete,
    RIL_onUnsolicitedResponse,
    RIL_requestTimedCallback,
    RIL_onRequestAck
};
//@ril.h
struct RIL_Env {
    void (*OnRequestComplete)(  \
        RIL_Token t,  \
        RIL_Errno e,  \
        void *response,  \
        size_t responselen);

    void (*OnUnsolicitedResponse)(  \
        int unsolResponse,  \
        const void *data,  \
        size_t datalen,  \
        RIL_SOCKET_ID socket_id);


    void (*RequestTimedCallback) (  \
        RIL_TimedCallback callback,  \
        void *param,  \
        const struct timeval *relativeTime);

    void (*OnRequestAck) (RIL_Token t);
};
```

## RIL_Init - 初始化

`RIL_Init`函数将执行`android_ril_module`的初始化，此外将main函数传入的`s_rilEnv`赋值给本地变量`qcril_response_api`，同时将`qcril_request_api`返回给main函数完成注册操作。

细心的朋友会发现，RIL_Init中使用了`client_id`，此变量的值由rild创建时传入的参数决定，其目的是建立SIM卡槽与RIL的绑定关系，通俗的将就是双卡设备的rild进程将创建两个qcril。

```
//@ril_api.cpp

extern "C"const RIL_RadioFunctions * RIL_Init(const struct RIL_Env * env, int argc, char * *argv) {
    ...
    //QCRIL_DEFAULT_INSTANCE_ID值为0，QCRIL_SECOND_INSTANCE_ID值为1；
    //qcril响应请求和主动上报的函数接口，与SIM卡槽对应
    qcril_response_api[QCRIL_DEFAULT_INSTANCE_ID] = (struct RIL_Env * ) env;
    qcril_response_api[QCRIL_SECOND_INSTANCE_ID] = (struct RIL_Env * ) env;
    ...

    //执行android_ril_module的ril_init，它将指引我们进入qcril初始化流程
    get_android_ril_module().ril_init(instance_id, env, argc, c_argv);

    //qcril处理请求的函数接口
    return & qcril_request_api[QCRIL_DEFAULT_INSTANCE_ID];
} /* RIL_Init() */
```

这里只看下`qcril_response_api`和`qcril_request_api`的定义，如何使用的这些函数接口将在后文介绍。

```
//@ril_api.cpp

static RIL_Env *qcril_response_api[QCRIL_MAX_INSTANCE_ID];

static const RIL_RadioFunctions qcril_request_api[] = {
    {
        QCRIL_RIL_VERSION,
        onRequest,
        currentState_rid,
        onSupports_rid,
        onCancel_rid,
        getVersion_rid
    }
};
```

接下来看`get_android_ril_module().ril_init(...)`，我们找到`get_android_ril_module()`的返回值的是`the_module.get_module()`，我们先弄清楚`the_module`是啥。

```
//@Android_ril_module.cpp

//定义局部变量 the_module
static load_module<android_ril_module> the_module;

android_ril_module &get_android_ril_module() {
    return the_module.get_module();
}
```

首先，`load_module`是一个C++模板，其定义如下，

```
//@Module.h

template <typename M>
class load_module
{
    public:
        load_module() {
            get_module().init();
        }
        M &get_module() {
            static M module{};
            return module;
        }
};
```

将`android_ril_module`代入进去，就得到了`the_module`的类型：

```
class load_module
{
    public:
        load_module() {
            get_module().init();
        }
        android_ril_module &get_module() {
            static android_ril_module module{};
            return module;
        }
};
```

所以`the_module`得类型是`load_module`，调用`get_module()`返回的是函数中类型为`android_ril_module`的全局变量`module`。

因此，`get_android_ril_module().ril_init(...)`其实就是是调用`android_ril_module`中定义的`ril_init`。

```
//@Android_ril_module.cpp

void android_ril_module::ril_init
(
    qcril_instance_id_e_type instance_id,
    const struct RIL_Env *env,
    int argc,
    char **argv
)
{
    //将env保存到本地，并替换掉OnRequestComplete和OnRequestAck
    local_env = *env;
    local_env.OnRequestComplete = ::local_on_request_complete;
    local_env.OnRequestAck = ::local_on_request_ack;

    //legacy_RIL_Init才是qcril的实际入口，返回的结构体被
    //赋值给qcril_legacy_functions而没有直接返回给rild，这是
    //高通做的适配层，这样做好处多多，自行体会吧。
    qcril_legacy_functions[instance_id] = legacy_RIL_Init(&local_env, instance_id, argc, argv);

    std::shared_ptr<QcrilInitMessage> qcril_init_msg = std::make_shared<QcrilInitMessage>(instance_id);
    if(qcril_init_msg) {
      qcril_init_msg->broadcast();
    }
}
```

我们继续看下`QcrilInitMessage`的定义，

```
class QcrilInitMessage: public UnSolicitedMessage,
        public add_message_id<QcrilInitMessage>
```

又是使用了模板，这次`add_message_id<QcrilInitMessage>`直接展开，

```
class add_message_id
{
    public:
        static inline message_id_t get_class_message_id() {
            //Dispatcher是单例模式编写
            static message_id_t id = Dispatcher::getInstance()
                .registerMessage("com.qualcomm.qti.qcril.core.qcril_init")
            return id;
        }
};
//@Dispatcher.cpp

message_id_t Dispatcher::registerMessage(const string &msg_name)
{
    lock_guard<recursive_mutex> lock(mMutex);
    message_id_info *h = nullptr;
    for (auto &mh : mMessageHandlers ) {
        const std::string &name = mh.get_name();
        if (name == msg_name) {
            h = &mh;
            break;
        }
    }
    if (h == nullptr) {
        auto it = mMessageHandlers.insert(mMessageHandlers.end(), message_id_info{msg_name});
        h = &*it;
        h->idx = mMessageHandlers.size() - 1;
    }
    return new message_id_info(*h);
}
//@Mesage_id.h

typedef struct message_id_info *message_id_t;

struct message_id_info
{
    friend class Dispatcher;
    private:
        std::shared_ptr<std::string> m_name;
        std::vector<Module*> module_list;

    public:
        size_t idx = 0;
}
```

## RIL_register - 注册

看下Qcril初始化完成返回的结构体是什么和这个结构体被用来做什么。

我们打开`RIL_RadioFunctions`的定义，就知道里面封装了4个函数和一个版本信息。

```
//@ril.cpp

typedef struct {
    int version;        /* 当前ril的版本号 */
    RIL_RequestFunc onRequest;  /*函数指针，用于处理RilRequest*/
    RIL_RadioStateRequest onStateRequest;  /*用于查询Radio状态*/
    RIL_Supports supports;  /*是否支持某个RilRequest，1为支持，0为不支持*/
    RIL_Cancel onCancel;  /*取消一个未处理的RilRequest*/
    RIL_GetVersion getVersion;  /*获取当前ril实现的版本号*/
} RIL_RadioFunctions;
//@ril.h

typedef void * RIL_Token;

typedef void (*RIL_RequestFunc) ( \
    int request, \     /*命名为RIL_REQUEST_*的请求ID*/
    void *data, \      /*请求中携带的数据*/
    size_t datalen, \  /*请求中携带数据的长度*/
    RIL_Token t, \
    RIL_SOCKET_ID socket_id);

typedef RIL_RadioState (*RIL_RadioStateRequest)( \
    RIL_SOCKET_ID socket_id);

typedef int (*RIL_Supports)(int requestCode);

typedef const char * (*RIL_GetVersion) (void);
```

我们再看下RIL_RadioFunctions是怎么被处理的，找到`RIL_register`的函数，

```
//@ril.cpp

extern "C" void RIL_register (const RIL_RadioFunctions *callbacks) {
    ...
    //保存到全局变量s_callbacks，这样其他地方也可以使用到
    memcpy(&s_callbacks, callbacks, sizeof (RIL_RadioFunctions));
    //标识s_callbacks已经被赋值
    s_registerCalled = 1;
    ...
    //使用radio命名空间下的registerService进行注册
    radio::registerService(&s_callbacks, s_commands);
}
@ril_service.cpp

void radio::registerService(RIL_RadioFunctions *callbacks, CommandInfo *commands) {
    using namespace android::hardware;
    int simCount = 1;
    const char *serviceNames[] = {
            android::RIL_getServiceName(), RIL2_SERVICE_NAME};

    simCount = SIM_COUNT;

    configureRpcThreadpool(1, true /* callerWillJoin */);
    for (int i = 0; i < simCount; i++) {
        pthread_rwlock_t *radioServiceRwlockPtr = getRadioServiceRwlock(i);
        int ret = pthread_rwlock_wrlock(radioServiceRwlockPtr);
        assert(ret == 0);

        radioService[i] = new RadioImpl;
        radioService[i]->mSlotId = i;
        oemHookService[i] = new OemHookImpl;
        oemHookService[i]->mSlotId = i;
        RLOGD("registerService: starting android::hardware::radio::V1_1::IRadio %s",
                serviceNames[i]);
        android::status_t status = radioService[i]->registerAsService(serviceNames[i]);
        status = oemHookService[i]->registerAsService(serviceNames[i]);

        ret = pthread_rwlock_unlock(radioServiceRwlockPtr);
        assert(ret == 0);
    }

    s_vendorFunctions = callbacks;
    s_commands = commands;
}
```









~~~markdown
编译
make libril-qc-hal-qmi   qcril-hal/qcril_qmi

make qcrild   qcril-hal/qcrild/qcrild

make qcrild_libril 

qcril_qmi_nas_unsolicited_indication_cb_helper
~~~

