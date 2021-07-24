[转载](https://www.codeleading.com/article/8063729492/)

 Binder是Android系统进程间通信（IPC）常用方式之一，client/service端是通过binder驱动作为通信介质的。Android系统中可以通过binder，实现JAVA/C++层的双向IPC通信，即JAVA - JAVA 、 JAVA - C++ 、 C++ - C++ 都可以通过Binder进行IPC双向通信。

   在Android 系统中个，很多模块的service放到了native层，用C++去实现，例如CameraService、SurfaceFlinger等。Client端则可以通过ServiceManger去获取service对象，然后通过AIDL接口进行服务端的调用。至于为什么没有用到JNI，是因为Android系统以及都帮忙做好了，在此只谈应用。

   下面举个例子，介绍 客户端(JAVA) 和 服务端(C++）通过 binder(AIDL)实现IPC双向通信用例。

1、创建AIDL文件，可以放在一个公共目录中，以方便client/service端都可以通过mk文件将其编译进去。

   再test目录下面 新建aidl目录 aidl\com\test\evs\ ，然后新建两个aidl文件 IEvsTestInterface.aidl (调用) IEvsTestCallback.aidl (回调)

 **IEvsTestCallback.aidl**

~~~java
package com.test.evs;
 
interface IEvsTestCallback {
 
    void onEvsStatus(int type, int arg0, int arg1);
 
    void onErrorStatus(int type, int value);
}
~~~

**IEvsTestInterface.aidl**

~~~java
package com.test.evs;
 
import com.test.evs.IEvsTestCallback;
 
interface IEvsTestInterface {
 
    void setCmd(int type, int arg0);
 
    int getStatus(int type, int arg0);
 
    void registerEvsCallback(IEvsTestCallback callback);
}
~~~

2、JAVA client端实现

为方便测试，JAVA client端则直接编译成一个apk进行测试。

Test 目录下面创建一个 test_client目录，存放client端的code

**MainActivity.java**

```java
package com.example.sampletest;
 
import android.content.Context;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Parcel;
import android.os.RemoteException;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.os.ServiceManager;
import android.app.Activity;
 
import com.test.evs.IEvsTestInterface;
import com.test.evs.IEvsTestCallback;
 
public class MainActivity extends Activity {
	
    private static final String TAG = "sampleService";
    private static final java.lang.String DESCRIPTOR = "evs.test";
    private static final int FUNC_CALLFUNCTION = 1;
 
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initData();
    } 
    
    private void initData() {
    	Log.i(TAG, "client initData");
    	
    	//Parcel _data = Parcel.obtain();
    	//Parcel _reply = Parcel.obtain();
    	
    	IBinder binder = ServiceManager.getService(DESCRIPTOR); //服务端对象
        if (binder == null) {
            Log.d(TAG, "biner get is null");
        }
 
        IEvsTestInterface evsInterface = IEvsTestInterface.Stub.asInterface(binder);
        
        if (evsInterface != null) {
            try {
                evsInterface.registerEvsCallback(callback); // 注册回调
                evsInterface.setCmd(1, 100);
                Log.d(TAG, "setCmd");
            } catch (RemoteException e) {
 
            }
        }
        
    	Log.i(TAG, "client initData end");
    	
    }
 
    private IEvsTestCallback callback = new IEvsTestCallback.Stub() {
        @Override
        public void onEvsStatus(int type, int arg0, int arg1)
              throws RemoteException {
           Log.i(TAG, "onEvsStatus " + type + " " + arg0 + " " + arg1);
        }
        
        @Override
        public void onErrorStatus(int type, int value) 
             throws RemoteException {
       
        }
    };
}
```

Client 端 mk文件

Android.mk，需要将aidl 文件编译进去，以便生成 .java文件。

**Android.mk**

~~~makefile
LOCAL_PATH:= $(call my-dir)
 
include $(CLEAR_VARS)
 
LOCAL_MODULE_TAGS := optional
 
LOCAL_STATIC_JAVA_LIBRARIES := android-support-v13
LOCAL_STATIC_JAVA_LIBRARIES += android-ex-camera2-portability
LOCAL_STATIC_JAVA_LIBRARIES += xmp_toolkit
LOCAL_STATIC_JAVA_LIBRARIES += glide
LOCAL_STATIC_JAVA_LIBRARIES += guava
LOCAL_STATIC_JAVA_LIBRARIES += jsr305
 
LOCAL_AIDL_INCLUDES := $(LOCAL_PATH)/../aidl
 
LOCAL_SRC_FILES := $(call all-java-files-under, src) \
   ../aidl/com/test/evs/IEvsTestCallback.aidl \
   ../aidl/com/test/evs/IEvsTestInterface.aidl \
  
#LOCAL_SRC_FILES += $(call all-java-files-under, src_pd)
#LOCAL_SRC_FILES += $(call all-java-files-under, src_pd_gcam)
 
LOCAL_RESOURCE_DIR += \
	$(LOCAL_PATH)/res \
 
LOCAL_PACKAGE_NAME := evsClient
 
LOCAL_CERTIFICATE := platform
~~~

3、native C++ 端

在test目录下面创建 test_server目录，并新建

EvsTestService.h EvsTestService.cpp main.cpp 三个文件

**EvsTestService.h**，会继承 BnEvsTestInterface 类，它是由AIDL文件在服务端编译生成的。

```c++
#ifndef _EVS_TEST_SERVICE_H
#define _EVS_TEST_SERVICE_H
 
#include <com/test/evs/BnEvsTestInterface.h>
#include <com/test/evs/IEvsTestInterface.h>
 
#include <cutils/multiuser.h>
#include <utils/Vector.h>
#include <utils/KeyedVector.h>
#include <binder/AppOpsManager.h>
#include <binder/BinderService.h>
#include <binder/IAppOpsCallback.h>
 
using namespace android;
//using namespace android::notification;
using namespace android::binder;
using namespace std;
 
namespace android {
class EvsTestService :
     public com::test::evs::BnEvsTestInterface,
     public IBinder::DeathRecipient
{
public:
    EvsTestService();
    virtual ~EvsTestService();
    virtual binder::Status setCmd(int type, int arg0) override;
    virtual binder::Status getStatus(int type, int arg0, int32_t* _aidl_return) override;
    virtual binder::Status registerEvsCallback(const ::android::sp<::com::test::evs::IEvsTestCallback>& callback) override;
 
    void sendMsgToClient(int status, int arg0, int arg1);
private:
    void binderDied(const wp<IBinder>& who) override;
 
    android::sp<::com::test::evs::IEvsTestCallback> callback_;
    std::mutex mutex_;
    
};
}
 
#endif 
```

**EvsTestService.cpp** 文件

~~~c++
#include <utils/Log.h>
#include <binder/IPCThreadState.h>
#include <binder/Status.h>
 
#include "EvsTestService.h"
 
namespace android {
 
    EvsTestService::EvsTestService() {
        ALOGI("EvsTestService...");
    }
 
    EvsTestService::~EvsTestService() {
 
    }
 
    binder::Status EvsTestService:: setCmd(int type, int arg0) {
	ALOGI("setCmd %d, %d\n", type, arg0);
        //status_t res;
 
        sendMsgToClient(type, arg0, 101);
        return binder::Status::ok();
    }
 
    binder::Status EvsTestService::getStatus(int type, int arg0, int32_t* _aidl_return) {
       ALOGI("getStatus %d, %d", type, arg0);
       *_aidl_return = 1;
       return binder::Status::ok();
    }
 
    binder::Status EvsTestService::registerEvsCallback(const ::android::sp<::com::test::evs::IEvsTestCallback>& callback) {
        //mcallback = callback;
        //callback = nullptr;
        
        std::lock_guard < std::mutex > guard(mutex_);
        if (callback_.get()) {
            ALOGD("Notification>>Failed to register callback, already registered");
            return binder::Status::fromStatusT(ALREADY_EXISTS);
        }
        ALOGD("Notification>>Success to register callback, already registered");
        callback_ = callback;
        IInterface::asBinder(callback_)->linkToDeath(this);
 
        return binder::Status::ok();
    }
 
    void EvsTestService:: sendMsgToClient(int type, int arg0, int arg1) {
        if (!callback_.get()) {
            ALOGD("Notification>>INotificationGatewayCallback callback_ is null");
            return;
        }
        ALOGD("SendMsgToClient %d, %d, %d", type, arg0, arg1);
        binder::Status status = callback_->onEvsStatus(type, arg0, arg1);
    }
 
    void EvsTestService::binderDied(const wp<IBinder>& /* who */) {
        std::lock_guard < std::mutex > guard(mutex_);
        callback_ = nullptr;
    }
}
~~~

**main.cpp**

~~~c++
#include "EvsTestService.h"
#include <hidl/HidlTransportSupport.h>
 
#include <binder/IServiceManager.h>
#include <binder/IBinder.h>
#include <binder/Parcel.h>
#include <binder/ProcessState.h>
#include <binder/IPCThreadState.h>
#include <utils/Log.h>
 
int main() {
     sp <EvsTestService> server = new EvsTestService();
 
     sp <IServiceManager> sm = defaultServiceManager();
     EvsTestService* samServ = new EvsTestService();
     status_t ret = sm->addService(String16("evs.test"), samServ); //注册服务 
     ALOGI("Service main addservice %d ", ret);
     ProcessState::self()->startThreadPool();
     IPCThreadState::self()->joinThreadPool(true);
    // while(1);
     return 0;
}
~~~

**Android.mk**, 将服务端编译成可执行文件，也需要将aidl文件编译进去。

~~~makefile
LOCAL_PATH:= $(call my-dir)
 
##################################
include $(CLEAR_VARS)
 
LOCAL_MODULE_TAGS := optional
 
LOCAL_STATIC_JAVA_LIBRARIES := android-support-v13
LOCAL_STATIC_JAVA_LIBRARIES += android-ex-camera2-portability
LOCAL_STATIC_JAVA_LIBRARIES += xmp_toolkit
LOCAL_STATIC_JAVA_LIBRARIES += glide
LOCAL_STATIC_JAVA_LIBRARIES += guava
LOCAL_STATIC_JAVA_LIBRARIES += jsr305
 
#LOCAL_AIDL_INCLUDES := $(LOCAL_PATH)/ 
LOCAL_AIDL_INCLUDES := $(LOCAL_PATH)/../aidl \
 
LOCAL_SRC_FILES := \
   EvsTestService.cpp \
    main.cpp \
    ../aidl/com/test/evs/IEvsTestCallback.aidl \
    ../aidl/com/test/evs/IEvsTestInterface.aidl \
 
LOCAL_SHARED_LIBRARIES := \
    libui \
    libgui \
    libEGL \
    libGLESv2 \
    libbase \
    libbinder \
    libcutils \
    libhardware \
    libhidlbase \
    libhidltransport \
    liblog \
    libutils \
 
#LOCAL_EXPORT_SHARED_LIBRARY_HEADERS := libbinder libcamera_client libfmq
 
LOCAL_C_INCLUDES += \
    system/media/private/camera/include \
    frameworks/native/include/media/openmax
 
#LOCAL_EXPORT_C_INCLUDE_DIRS := \
#    frameworks/av/services/camera/libcameraservice
 
LOCAL_MODULE := evsServer
 
#LOCAL_MODULE_TAGS := optional
#LOCAL_STRIP_MODULE := keep_symbols
 
LOCAL_CFLAGS += -DLOG_TAG=\"EvsSample\"
#LOCAL_CFLAGS += -DGL_GLEXT_PROTOTYPES -DEGL_EGLEXT_PROTOTYPES
LOCAL_CFLAGS +=  
 
# NOTE:  It can be helpful, while debugging, to disable optimizations
#LOCAL_CFLAGS += -O0 -g
 
include $(BUILD_EXECUTABLE)
#include $(BUILD_SHARED_LIBRARY)
~~~



**java做客户端，c/c++做服务端的方法**

~~~java
//ServiceManager.java 添加服务
public static void addService(String name, IBinder service) {
    addService(name, service, false, IServiceManager.DUMP_FLAG_PRIORITY_DEFAULT);
}

//C/C++获取服务
defaultServiceManager()->getService(android::String16(serviceName));
~~~

