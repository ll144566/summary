## 1、一个简单的mk文件分析

```makefile
LOCAL_PATH:= $(call my-dir)
include $(CLEAR_VARS)

LOCAL_MODULE_TAGS := optional

LOCAL_SRC_FILES := $(call all-java-files-under, src)

LOCAL_PACKAGE_NAME := Settings
LOCAL_CERTIFICATE := platform

include $(BUILD_PACKAGE)

# Use the folloing include to make our test apk.
include $(call all-makefiles-under,$(LOCAL_PATH))
```



该Android.mk文件路径是package/app/Settings/Android.mk，来分析该文件

GNU Make‘功能’宏，必须通过使用'$(call  )'来调用，调用他们将返回文本化的信息。



### 1.1、 LOCAL_PATH:= $(call my-dir)

一个Android.mk file首先必须定义好LOCAL_PATH变量。它用于在开发树中查找源文件。

宏函数’my-dir’，由编译系统提供，用于返回当前路径（即包含Android.mk file文件的目录）。



### 1.2、编译模块定义

 Android.mk中可以定义多个编译模块，每个编译模块都是以include $(CLEAR_VARS)开始，以include $(BUILD_XXX)结束。

#### 1.2.1、include $(CLEAR_VARS)

CLEAR_VARS指的是clear_vars.mk，由编译系统提供，它会让GNU MAKEFILE为你清除除LOCAL_PATH以外的所有LOCAL_XXX变量，如LOCAL_MODULE，LOCAL_SRC_FILES，LOCAL_SHARED_LIBRARIES，LOCAL_STATIC_LIBRARIES等。

这是必要的，因为所有的编译控制文件都在同一个GNU MAKE执行环境中，所有的变量都是全局的。

 

#### 1.2.2、include $(BUILD_PACKAGE)    # Tell it to build an APK

$(BUILD_PACKAGE)是用来编译生成package/app/下的apk。

还有其他几种编译情况：

~~~makefile
include $(BUILD_STATIC_LIBRARY)  #表示编译成静态库

include $(BUILD_SHARED_LIBRARY) #表示编译成动态库

include $(BUILD_EXECUTABLE)   #表示编译成可执行程序     
~~~



### 1.3、LOCAL_MODULE_TAGS := optional

解析：

LOCAL_MODULE_TAGS :=user eng tests optional

~~~markdown
user:  指该模块只在user版本下才编译

eng: 指该模块只在eng版本下才编译

tests: 指该模块只在tests版本下才编译

optional:指该模块在所有版本下都编译

取值范围debug eng tests optional samples shell_ash shell_mksh。注意不能取值user，如果要预装，则应定义core.mk。

~~~



### 1.4、LOCAL_SRC_FILES := $(call all-java-files-under, src)

1. 如果要包含的是java源码的话，可以调用all-java-files-under得到。(这种形式来包含local_path目录下的所有java文件)

2. 当涉及到C/C++时，LOCAL_SRC_FILES变量就必须包含将要编译打包进模块中的C或C++源代码文件。注意，在这里你可以不用列出头文件和包含文件，因为编译系统将会自动为你找出依赖型的文件；仅仅列出直接传递给编译器的源代码文件就好。

3. all-java-files-under宏的定义是在build/core/definitions.mk中。



### 1.5、LOCAL_PACKAGE_NAME := Settings

package的名字，这个名字在脚本中将标识这个app或package。



### 1.6、LOCAL_CERTIFICATE := platform

LOCAL_CERTIFICATE 后面是签名文件的文件名，说明Settings.apk是一个**需要platform key签名的APK**



### 1.7、include $(call all-makefiles-under,$(LOCAL_PATH))

加载当前目录下的所有makefile文件，all-makefiles-under会返回一个位于当前'my-dir'路径的子目录中的所有Android.mk的列表。

all-makefiles-under宏的定义是在build/core/definitions.mk中。

这个Android.mk文件最后就生成了Settings.apk。分析完上面的Android.mk文件后，来总结下各种LOCAL_XXX。

三种情况说明：

-   必须定义, 在app或package的Android.mk中必须给定值。

-   可选定义，在app或package的Android.mk中可以也可以不给定值。

-   不用定义，在app或package的Android.mk中不要给定值，脚本自动指定值。




```
LOCAL_PATH，          当前路径，必须定义。
LOCAL_PACKAGE_NAME，  必须定义，package的名字，这个名字在脚本中将标识app或package。
LOCAL_MODULE_SUFFIX， 不用定义，module的后缀，=.apk。
LOCAL_MODULE，        不用定义，=$(LOCAL_PACKAGE_NAME)。
LOCAL_JAVA_RESOURCE_DIRS，     不用定义。
LOCAL_JAVA_RESOURCE_FILES，    不用定义。
LOCAL_MODULE_CLASS，  不用定义。
LOCAL_MODULE_TAGS，   可选定义。默认optional。取值范围user debug eng tests optional samples shell_ash shell_mksh。
LOCAL_ASSET_DIR，     可选定义，推荐不定义。默认$(LOCAL_PATH)/assets
LOCAL_RESOURCE_DIR，  可选定义，推荐不定义。默认product package和device package相应的res路径和$(LOCAL_PATH)/res。
LOCAL_PROGUARD_ENABLED，       可选定义，默认为full，如果是user或userdebug。取值full, disabled, custom。
full_android_manifest，        不用定义，=$(LOCAL_PATH)/AndroidManifest.xml。
LOCAL_EXPORT_PACKAGE_RESOURCES，    可选定义，默认null。如果允许app的资源被其它模块使用，则设置true。
LOCAL_CERTIFICATE，   可选定义，默认为testkey。最终
        private_key := $(LOCAL_CERTIFICATE).pk8
        certificate := $(LOCAL_CERTIFICATE).x509.pem
```



## 2、常用模块、变量、函数介绍

 ### 2.1、模块编译变量

```makefile
   变量                          用途
   LOCAL_SRC_FILES               当前模块包含的源代码文件
   LOCAL_MODULE                  当前模块的名称，这个名称应当是唯一的，模块间的依赖关系就是通过这个名称来引用的
   LOCAL_C_INCLUDES              C/C++ 语言需要的头文件的路径
   LOCAL_STATIC_LIBRARIES        当前模块在静态编译时，需要的静态库
   LOCAL_SHARED_LIBRARIES        当前模块在运行时依赖的动态库
   LOCAL_CFLAGS                  C/C++编译器的参数
   
   include $(BUILD_EXECUTABLE)
   # -I$(LOCAL_C_INCLUDES)       指定头文件搜索路径
   # -l$(LOCAL_SHARED_LIBRARIES) 指令链接的动态库
   gcc $(LOCAL_CFLAGS) $(LOCAL_SRC_FILES) -o $(LOCAL_MODULE) -I$(LOCAL_C_INCLUDES) $(LOCAL_STATIC_LIBRARIES) -l$(LOCAL_SHARED_LIBRARIES) 
   
   LOCAL_JAVA_LIBRARIES          当前模块依赖的Java共享库
   LOCAL_STATIC_JAVA_LIBRARIES   当前模块依赖的Java静态库
   LOCAL_PACKAGE_NAME            当前模块的APK应用的名称
   
   LOCAL_CERTIFICATE             签署当前应用的证书名称
   
   LOCAL_MODULE_TAGS             当前模块所包含的标签，Android.mk的必选，一个模块可以包含多个标签
                                 标签的值可能是debug, eng, tests, samples 或 optional
                                 

```



LOCAL_CFLAGS += -DXXX ，相当于在所有源文件中增加一个宏定义#define XXX

eg：
在Android.mk中增加

~~~makefile
ifeq ($(PRODUCT_MODEL),XXX_A)
LOCAL_CFLAGS += -DBUILD_MODEL
endif
~~~

即能在所编译的Cpp文件中使用：

~~~c++
#ifdef BUILD_MODEL
....
#endif
~~~





### 2.2、模块类型

```makefile
include $(BUILD_EXECUTABLE)              #编译目标机上的可执行文件(ELF)
include $(BUILD_STATIC_LIBRARY)          #编译目标机上的静态库(*.a 编译时使用)
include $(BUILD_SHARED_LIBRARY)          #编译目标机上的动态库文件(*.so)
include $(BUILD_JAVA_LIBRARY)            #编译目标机上的java动态库
include $(BUILD_STATIC_JAVA_LIBRARY)     #编译目标机上的java静态库
include $(BUILD_PACKAGE)                 #编译目标机上的java包
```

### 2.3、函数

~~~makefile
#build/core/definitions.mk
#通常会用下面函数获取上面环境变量的值：
#提供配置编译需要的函数
$(call my-dir)                        #获取当前文件夹路径
$(call all-subdir-java-files)         #获取当前目录子目录下所有的java源代码文件
$(call all-java-files-under, 目录)     #获取指定目录下的所有Java文件
$(call all-c-files-under, 目录)        #获取指定目录下的所有C语言文件
$(call all-Iaidl-files-under, 目录)    #获取指定目录下的所有 AIDL 文件
$(call all-makefiles-under, 目录)      #获取指定目录下的所有Make文件
include $(call all-subdir-makefiles)  #只编译子目录
include $(call all-makefiles-under,$(LOCAL_PATH)) #是遍历$(LOCAL_PATH)下所有的Android.mk
$(call intermediates-dir-for, <class>, <app_name>, <host or target>, <common?>) #获取Build输入的目标文件夹路径。
~~~



## 3、常用简单模板

 

### 3.1、编译apk模板

```makefile
LOCAL_PATH := $(call my-dir)  
include $(CLEAR_VARS)   
# Build all java files in the java subdirectory
LOCAL_SRC_FILES := $(call all-subdir-java-files) 
# Name of the APK to build
LOCAL_PACKAGE_NAME := LocalPackage   
# Tell it to build an APK
include $(BUILD_PACKAGE)
```



### 3.2、编译JAVA库模板



```makefile
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
# Build all java files in the java subdirectory
LOCAL_SRC_FILES := $(call all-subdir-java-files)
# Any libraries that this library depends on
LOCAL_JAVA_LIBRARIES := android.test.runner
# The name of the jar file to create
LOCAL_MODULE := sample
# Build a static jar file.
include $(BUILD_STATIC_JAVA_LIBRARY)
```

 **注**：LOCAL_JAVA_LIBRARIES := android.test.runner表示生成的JAVA库的jar文件名

 

### 3.3、编译C/C++应用程序模板



```makefile
LOCAL_PATH := $(call my-dir)
#include $(CLEAR_VARS)
LOCAL_SRC_FILES := main.c
LOCAL_MODULE := test_exe
#LOCAL_C_INCLUDES :=
#LOCAL_STATIC_LIBRARIES :=
#LOCAL_SHARED_LIBRARIES :=
include $(BUILD_EXECUTABLE)
```



 **注**：‘:=’是赋值的意思，'+='是追加的意思，‘$’表示引用某变量的值

```makefile
LOCAL_SRC_FILES中加入源文件路径，LOCAL_C_INCLUDES中加入需要的头文件搜索路径
LOCAL_STATIC_LIBRARIES 加入所需要链接的静态库(*.a)的名称，
LOCAL_SHARED_LIBRARIES 中加入所需要链接的动态库(*.so)的名称，
LOCAL_LDFLAGS 静态动态都可以
LOCAL_MODULE表示模块最终的名称，BUILD_EXECUTABLE 表示以一个可执行程序的方式进行编译。
```

 

### 3.4、编译C\C++静态库



```makefile
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_SRC_FILES := \
 helloworld.c
LOCAL_MODULE:= libtest_static
 #LOCAL_C_INCLUDES :=
#LOCAL_STATIC_LIBRARIES :=
#LOCAL_SHARED_LIBRARIES :=
include $(BUILD_STATIC_LIBRARY)
```



 和上面相似，BUILD_STATIC_LIBRARY 表示编译一个静态库。

### 3.5、编译C/C++动态库的模板



```makefile
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_SRC_FILES := helloworld.c
LOCAL_MODULE := libtest_shared
TARGET_PRELINK_MODULES := false
#LOCAL_C_INCLUDES :=
#LOCAL_STATIC_LIBRARIES :=
#LOCAL_SHARED_LIBRARIES :=
include $(BUILD_SHARED_LIBRARY)
```



和上面相似，BUILD_SHARED_LIBRARY 表示编译一个共享库。

以上三者的生成结果分别在如下目录中，generic 依具体 target 会变(可能是dkb~~)：

```
out/target/product/generic/obj/APPS
out/target/product/generic/obj/JAVA_LIBRARIES
out/target/product/generic/obj/EXECUTABLE
out/target/product/generic/obj/STATIC_LIBRARY
out/target/product/generic/obj/SHARED_LIBRARY
```



### 3.6、每个模块的目标文件夹分别为：

```
1）APK程序：XXX_intermediates
2）JAVA库程序：XXX_intermediates
3）C\C++可执行程序：XXX_intermediates
4）C\C++静态库： XXX_static_intermediates
5）C\C++动态库： XXX_shared_intermediates
```



## 4、路径变量整理

基于Android8.1系统源码，常量的定义在文件./build/make/core/envsetup.mk中

~~~markdown
TOPDIR – 源码根目录

OUT_DIR – out目录，默认情况下是源码目录下的out目录，如果指定OUT_DIR_COMMON_BASE这个环境变量，则为这个变量指定的目录

TARGET_BUILD_TYPE – 是release还是debug的编译，在环境变量TARGET_BUILD_TYPE中指定

SOONG_OUT_DIR – soong目录，默认情况下是out/soong

DEBUG_OUT_DIR – TARGET_BUILD_TYPE为debug时会用到此目录，默认是out/debug

TARGET_OUT_ROOT – target目录，默认是out/target，debug时为out/debug/target

TARGET_PRODUCT_OUT_ROOT – 默认是out/target/product目录

TARGET_COMMON_OUT_ROOT – 默认是out/target/common目录，用于生成编译时的中间文件

PRODUCT_OUT – 默认是out/target/product/{设备型号}，真正的编译生成文件的目录

TARGET_OUT – $(PRODUCT_OUT)/system目录

TARGET_OUT_GEN – $(PRODUCT_OUT)/gen

TARGET_OUT_EXECUTABLES – $(TARGET_OUT)/bin

TARGET_OUT_OPTIONAL_EXECUTABLES – $(TARGET_OUT)/xbin

TARGET_OUT_RENDERSCRIPT_BITCODE := $(TARGET_OUT_SHARED_LIBRARIES)

TARGET_OUT_JAVA_LIBRARIES :=$(PRODUCT_OUT)/system/framework

TARGET_OUT_APPS :=$(PRODUCT_OUT)/system/app

TARGET_OUT_APPS_PRIVILEGED :=$(PRODUCT_OUT)/system/priv-app

TARGET_OUT_KEYLAYOUT :=$(PRODUCT_OUT)/system/usr/keylayout

TARGET_OUT_KEYCHARS :=$(PRODUCT_OUT)/system/usr/keychars

TARGET_OUT_ETC :=$(PRODUCT_OUT)/system/etc

TARGET_OUT_FAKE := $(PRODUCT_OUT)/fake_packages

TARGET_OUT_TESTCASES := $(PRODUCT_OUT)/testcases

HOST_OUT_ROOT – host目录，默认是out/host

HOST_OUT –

SOONG_HOST_OUT –

HOST_CROSS_OUT –
~~~





对于变量LOCAL_SDK_VERSION 之前一直会使用，标记SDK 的version 状态，值为current system_current test_current core_current 其中一个。

对于使用系统@hide api的，我们默认可以设置 LOCAL_PRIVATE_PLATFORM_APIS 为true即可。
