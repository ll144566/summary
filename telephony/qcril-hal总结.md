

术语

AMSS： Advanced Mobile Subscriber Software
ril： Radio Interface Layer
qcril： qualcomm radio interface layer 高通提供的 ril 层接口
QMI: Qualcomm Modem Interface 高通提供的与 modem 交互的接口
RAT： radio access technology
UIM： User Identification Module
STK： SIM Toolkit interface  



1） RIL.java： Framework 侧和 RIL 层交互的接口， RILJ 通过 hidl 方式发送 request 到 ril 层 并接收处理来自 RIL 层的消息。 Framework 层还可以通过 oem_socket 与 ril 层交互，在高通 平台中 APK 可以通过 oem socket 直接与 ril 通信，不需要经过 Framework，具体可参考 IMS 事件的处理，包括 imssender 等类（ims 是通过 ims socket）。
2） Rild.so：主要完成与 AP 侧的 msg 交互， Framework 层通过 rild 下发 request。
3） Ril.so：主要完成 rild 收到的 request 的 dispatch 处理和底层返回的 request 处理结果和 modem 主动上报的消息的 response 处理。 indication 的处理。
5） Qmi.so： ril 与 AMSS 消息交互的接口， ril 有 request 需要下发到 AMSS，通过 qmi 发送； AMSS 返回 response、 unsolicited indication 通过 qmi 上报到 ril  。



高通在android P之前使用的是qcri，android P之后l已经使用qcril-hal新架构。

`rild`是由C/C++编写的linux域后台进程，是连接Java Telephony Frameworks和Modem的中间传输层。rild.c中的main函数主要用来启动RILC，其中最关键的就是将LibRIL和Reference-ril（高通qcril）之间建立起一种互相调用的能力，LibRIL中有指向Reference-ril的funs结构体的指针，而Reference-ril有指向LibRIL的s_rilEnv结构体的指针，两者通过对方提供的函数指针互相调用，从而完成ril消息的交互。

这是Android原生的ril目录结构，高通在此基础上做了修改，其中libril和rild基本没什么变化，主要是替换了reference-ril。

~~~markdown
hardware/ril/
├── Android.bp
├── CleanSpec.mk
├── include
│   ├── libril
│   │   └── ril_ex.h
│   └── telephony
│       ├── librilutils.h
│       ├── record_stream.h
│       ├── ril_cdma_sms.h
│       ├── ril.h
│       ├── ril_mnc.h
│       ├── ril_msim.h
│       └── ril_nv_items.h
├── libril
│   ├── Android.mk
│   ├── MODULE_LICENSE_APACHE2
│   ├── NOTICE
│   ├── ril_commands.h
│   ├── ril.cpp
│   ├── ril_event.cpp
│   ├── ril_event.h
│   ├── ril_internal.h
│   ├── RilSapSocket.cpp
│   ├── RilSapSocket.h
│   ├── ril_service.cpp
│   ├── ril_service.h
│   ├── RilSocket.h
│   ├── rilSocketQueue.h
│   ├── ril_unsol_commands.h
│   ├── sap_service.cpp
│   └── sap_service.h
├── librilutils
│   ├── Android.bp
│   ├── librilutils.c
│   ├── proto
│   │   ├── sap-api.options
│   │   └── sap-api.proto
│   └── record_stream.c
├── OWNERS
├── reference-ril
│   ├── Android.mk
│   ├── atchannel.c
│   ├── atchannel.h
│   ├── at_tok.c
│   ├── at_tok.h
│   ├── misc.c
│   ├── misc.h
│   ├── MODULE_LICENSE_APACHE2
│   ├── NOTICE
│   ├── OWNERS
│   ├── reference-ril.c
│   └── ril.h -> ../include/telephony/ril.h
└── rild
    ├── Android.mk
    ├── MODULE_LICENSE_APACHE2
    ├── NOTICE
    ├── rild.c
    ├── rild.legacy.rc
    └── rild.rc
~~~



**部分内容来自网上整理**

## 1. rild - RIL入口

`rild`的入口函数`main`的主要流程如下，

```c
//@rild.c
//path qcril-hal/qcrild/qcrild/rild.c

int main(int argc, char **argv) {
    ...
	RIL_startEventLoop();

    rilInit = RIL_Init;
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

`s_rilEnv`代表一个`RIL_Env `结构体，包含了一组向Java Telephony Frameworks返回请求结果的函数。

下面是`s_rilEnv`的定义和类型，

```c
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

## 2. Loop循环

~~~c++
#@ril.cpp
#path qcril-hal/qcrild/libril/ril.cpp
extern "C" void
RIL_startEventLoop(void) {
    /* spin up eventLoop thread and wait for it to get started */
    s_started = 0;
    s_startupMutex.lock();

    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
	
    ////创建线程并运行eventLoop
    int result = pthread_create(&s_tid_dispatch, &attr, eventLoop, NULL);
    if (result != 0) {
        RLOGE("Failed to create dispatch thread: %s", strerror(result));
        goto done;
    }

    while (s_started == 0) {
        s_startupCond.wait(s_startupMutex);
    }

done:
    s_startupMutex.unlock();
}

static void *
eventLoop(void *param) {
    int ret;
    int filedes[2];
	//event初始化
    ril_event_init();

    s_startupMutex.lock();

    s_started = 1;
    s_startupCond.notify_all();

    s_startupMutex.unlock();
	//创建通信管道
    ret = pipe(filedes);

    if (ret < 0) {
        RLOGE("Error in pipe() errno:%d", errno);
        return NULL;
    }

    s_fdWakeupRead = filedes[0];//输入的文件描述符
    s_fdWakeupWrite = filedes[1];//输出的文件描述符

    fcntl(s_fdWakeupRead, F_SETFL, O_NONBLOCK);
	//创建event
    ril_event_set (&s_wakeupfd_event, s_fdWakeupRead, true,
                processWakeupCallback, NULL);

    //加入到队列中唤醒
    rilEventAddWakeup (&s_wakeupfd_event);

    // Only returns on error
    //开启event循环
    ril_event_loop();
    RLOGE ("error in event_loop_base errno:%d", errno);
    // kill self to restart on error
    kill(0, SIGKILL);

    return NULL;
}

~~~

继续跟踪event_init函数

初始化文件句柄和，两个列表，timer_list和pending_list还有一个watch_table。
追踪其定义的类型看到两个表是ril_event变量，watch_table是一个指针数组

~~~c++
#@ril_event.cpp
#path qcril-hal/qcrild/libril/ril_event.cpp
void ril_event_init()
{
    FD_ZERO(&readFds);
    init_list(&timer_list);
    init_list(&pending_list);
    memset(watch_table, 0, sizeof(watch_table));
}

static struct ril_event * watch_table[MAX_FD_EVENTS];
static struct ril_event timer_list;
static struct ril_event pending_list;
~~~



看一下ril_event的类型

```cpp
#@/ril_event.h
#path qcril-hal/qcrild/libril/ril_event.h
//一个双向链表
struct ril_event {
    struct ril_event *next;
    struct ril_event *prev;
    int fd;
    int index;
    bool persist;
    struct timeval timeout;
    ril_event_cb func;
    void *param;
};
```

其实timer_list和pending_list还有一个watch_table都是链表
接着跟踪ril_event_loop循环的具体实现

```cpp
#@ril_event.cpp
#path qcril-hal/qcrild/libril/ril_event.cpp
void ril_event_loop()
{
    int n;
    fd_set rfds;
    struct timeval tv;
    struct timeval * ptv;


    for (;;) {

        // make local copy of read fd_set
        memcpy(&rfds, &readFds, sizeof(fd_set));
        if (-1 == calcNextTimeout(&tv)) {
            // no pending timers; block indefinitely
            dlog("~~~~ no timers; blocking indefinitely ~~~~");
            ptv = NULL;
        } else {
            dlog("~~~~ blocking for %ds + %dus ~~~~", (int)tv.tv_sec, (int)tv.tv_usec);
            ptv = &tv;
        }
        printReadies(&rfds);
        n = select(nfds, &rfds, NULL, NULL, ptv);
        printReadies(&rfds);
        dlog("~~~~ %d events fired ~~~~", n);
        if (n < 0) {
            if (errno == EINTR) continue;

            RLOGE("ril_event: select error (%d)", errno);
            // bail?
            return;
        }
		////主要循环调用三个方法
        // Check for timeouts
        processTimeouts();
        // Check for read-ready
        processReadReadies(&rfds, n);
        // Fire away
        firePending();
    }
}
```

处理timer_list列表

```cpp
#@ril_event.cpp
#path qcril-hal/qcrild/libril/ril_event.cpp
static void processTimeouts()
{
    ...
    /如果timer_list中的事件超时，则从timer_list列表中移除，并添加到pending_list中
    while ((tev != &timer_list) && (timercmp(&now, &tev->timeout, >))) {
        // Timer expired
        dlog("~~~~ firing timer ~~~~");
        next = tev->next;
        removeFromList(tev);
        addToList(tev, &pending_list);
        tev = next;
    }
    ...
}

```

处理watch_table列表

```cpp

static void processReadReadies(fd_set * rfds, int n)
{
    ...
	//添加到pending_list中，设置persist为false后从watch_table中移除
    for (int i = 0; (i < MAX_FD_EVENTS) && (n > 0); i++) {
        struct ril_event * rev = watch_table[i];
        if (rev != NULL && FD_ISSET(rev->fd, rfds)) {
            addToList(rev, &pending_list);
            if (rev->persist == false) {
                removeWatch(rev, i);
            }
            n--;
        }
    }
    ...
}
```

处理pengding_list列表，从pending_list中移除，调用ev->func处理事件

```cpp
static void firePending()
{
    struct ril_event * ev = pending_list.next;
    while (ev != &pending_list) {
        struct ril_event * next = ev->next;
        removeFromList(ev);
        ev->func(ev->fd, 0, ev->param);
        ev = next;
    }
}
```


RIL的Event管理体系中存在3个链表结构：watch_table,timer_list,pending_list
watch（如果驻留的话就每次都处理）和timer(如果时间到了的话就分配进去处理)只是分配，实际最后处理的场所是pending_list,),并使用了一个设备句柄池readFDS，把所有的Socket管道的文件句柄保存起来。



## 3. RIL_Init - 初始化

`RIL_Init`函数将执行`android_ril_module`的初始化，此外将main函数传入的`s_rilEnv`赋值给本地变量`qcril_response_api`，同时将`qcril_request_api`返回给main函数完成注册操作。

RIL_Init中使用了`client_id`，此变量的值由rild创建时传入的参数决定，其目的是建立SIM卡槽与RIL的绑定关系，通俗的将就是双卡设备的rild进程将创建两个qcril。

```c++
//@ril_api.cpp
//path qcril-hal/modules/android/src/ril_api.cpp

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

```c++
//@ril_api.cpp
//path qcril-hal/modules/android/src/ril_api.cpp

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

```c++
//@android_ril_module.cpp
//path modules/android/src/android_ril_module.cpp
//定义局部变量 the_module
static load_module<android_ril_module> the_module;

android_ril_module &get_android_ril_module() {
    return the_module.get_module();
}
```

首先，`load_module`是一个C++模板，其定义如下，

```c++
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

```c++
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

所以`the_module`的类型是`load_module`，调用`get_module()`返回的是函数中类型为`android_ril_module`的全局变量`module`。

因此，`get_android_ril_module().ril_init(...)`其实就是是调用`android_ril_module`中定义的`ril_init`。

```c++
//@android_ril_module.cpp
//path qcril-hal/modules/android/src/android_ril_module.cpp
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
    //高通做的适配层。
    qcril_legacy_functions[instance_id] = legacy_RIL_Init(&local_env, instance_id, argc, argv);

    std::shared_ptr<QcrilInitMessage> qcril_init_msg = std::make_shared<QcrilInitMessage>(instance_id);
    if(qcril_init_msg) {
      qcril_init_msg->broadcast();
    }
}
```

我们继续看下`QcrilInitMessage`的定义，

```c++
//@QcrilInitMessage.h
//path qcril-hal/include/framework/QcrilInitMessage.h
class QcrilInitMessage: public UnSolicitedMessage,
        public add_message_id<QcrilInitMessage>
```

又是使用了模板，这次`add_message_id<QcrilInitMessage>`直接展开，REG_MSG对应着Dispatcher.h中的Dispatcher::getInstance().registerMessage(name)

```c++
//@add_message_id.h
//path qcril-hal/include/framework/add_message_id.h
template <typename T>
class add_message_id
{
    public:
        static inline message_id_t get_class_message_id() {
            static message_id_t id = REG_MSG(T::MESSAGE_NAME);
            return id;
        }
};


//@Dispatcher.h
//path qcril-hal/include/framework/Dispatcher.h

//Dispatcher是单例模式编写
#define REG_MSG(name) Dispatcher::getInstance().registerMessage(name)

//@Dispatcher.cpp
//path qcril-hal/framework/src/Dispatcher.cpp
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
//path qcril-hal/include/framework/Mesage_id.h

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

## 4. RIL_register - 注册

看下Qcril初始化完成返回的结构体是什么和这个结构体被用来做什么。

我们打开`RIL_RadioFunctions`的定义，就知道里面封装了4个函数和一个版本信息。

```c++
//@ril.cpp
//path qcril-hal/qcrild/libril/ril.cpp

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

```c++
//@ril.cpp
//path qcril-hal/qcrild/libril/ril.cpp

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

//@ril_service.cpp
//path qcril-hal/qcrild/libril/ril_service.cpp

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

## 4. Unsolicited消息上报

Unsolicited消息的处理在RIL_onUnsolicitedResponse中处理的

~~~c++
//@ril.cpp
//path qcril-hal/qcrild/libril/ril.cpp
void RIL_onUnsolicitedResponse(int unsolResponse, const void *data,
                                size_t datalen)
{
    ...
    ret = s_unsolResponses[unsolResponseIndex].responseFunction(
            (int) soc_id, responseType, 0, RIL_E_SUCCESS, const_cast<void*>(data),
            datalen);

    ...
}

typedef struct {
    int requestNumber;
    int (*responseFunction) (int slotId, int responseType, int token,
            RIL_Errno e, void *response, size_t responselen);//处理函数
    WakeType wakeType;//决定唤醒手机的WakeLock
} UnsolResponseInfo;

static UnsolResponseInfo s_unsolResponses[] = {
#include "ril_unsol_commands.h"
};


//@ril_unsol_commands.h
//path qcril-hal/qcrild/libril/ril_unsol_commands.h
#ifndef QMI_RIL_UTF
    {RIL_UNSOL_RESPONSE_RADIO_STATE_CHANGED, radio::radioStateChangedInd, WAKE_PARTIAL},
	//这些函数都在qcril-hal/qcrild/libril/ril_service.cpp中实现
    ...
#endif

~~~

以接收短信为例

~~~c++
//@ril_unsol_commands.h
//path qcril-hal/qcrild/libril/ril_unsol_commands.h
#ifndef QMI_RIL_UTF
    {RIL_UNSOL_RESPONSE_NEW_SMS, radio::newSmsInd, WAKE_PARTIAL},
    ...
#endif

//找到对应处理函数       
//@ril_service.cpp
//path qcril-hal/qcrild/libril/ril_service.cpp
int radio::newSmsInd(int slotId, int indicationType,
                     int token, RIL_Errno e, void *response, size_t responseLen) {
    if (radioService[slotId] != NULL && radioService[slotId]->mRadioIndication != NULL) {
        if (response == NULL || responseLen == 0) {
            RLOGE("newSmsInd: invalid response");
            return 0;
        }

        hidl_vec<uint8_t> pdu;
        pdu.setToExternal(static_cast<uint8_t*>(response), responseLen);
#if VDBG
        RLOGD("newSmsInd");
#endif
        Return<void> retStatus = radioService[slotId]->mRadioIndication->newSms(
                convertIntToRadioIndicationType(indicationType), pdu);
        radioService[slotId]->checkReturnStatus(retStatus);
    } else {
        RLOGE("newSmsInd: radioService[%d]->mRadioIndication == NULL", slotId);
    }

    return 0;
}



~~~

RadioIndication用来接收主动上报的消息，新短信对应newSms()方法，这样消息就传到了RILJ。

~~~java
//@RadioIndication.java
//path frameworks/opt/telephony/src/java/com/android/internal/telephony/RadioIndication.java
public class RadioIndication extends IRadioIndication.Stub {
    RIL mRil;

    RadioIndication(RIL ril) {
        mRil = ril;
    }
    
        public void newSms(int indicationType, ArrayList<Byte> pdu) {
        mRil.processIndication(indicationType);

        byte[] pduArray = RIL.arrayListToPrimitiveArray(pdu);
        if (RIL.RILJ_LOGD) mRil.unsljLog(RIL_UNSOL_RESPONSE_NEW_SMS);

        SmsMessageBase smsb = com.android.internal.telephony.gsm.SmsMessage.createFromPdu(pduArray);
        if (mRil.mGsmSmsRegistrant != null) {
            mRil.mGsmSmsRegistrant.notifyRegistrant(
                    new AsyncResult(null, smsb == null ? null : new SmsMessage(smsb), null));
        }
    }
}
~~~

Android O的版本对RIL的框架的通信功能进行了改动，不在使用sockect进行通讯，而改用HIDL进行通信。

~~~java

//path hardware/interfaces/radio/1.0/IRadioIndication.hal

package android.hardware.radio@1.0;

/**
 * Interface declaring unsolicited radio indications.
 */
interface IRadioIndication {
    ...
        /**
     * Indicates when new SMS is received.
     * Callee must subsequently confirm the receipt of the SMS with a
     * acknowledgeLastIncomingGsmSms()
     *
     * Server must not send newSms() nor newSmsStatusReport() messages until a
     * acknowledgeLastIncomingGsmSms() has been received
     *
     * @param type Type of radio indication
     * @param pdu PDU of SMS-DELIVER represented as byte array.
     *        The PDU starts with the SMSC address per TS 27.005 (+CMT:)
     */
    oneway newSms(RadioIndicationType type, vec<uint8_t> pdu);
    ...
}
~~~

hardware/interfaces/   vendor/qcom/proprietary/qcril-hal/