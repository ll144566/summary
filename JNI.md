## 1、准备工作

下载NDK

![image-20210413195516244](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210413195516244.png)

添加NDK路径(不使用cmake)

![image-20210413195900020](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210413195900020.png)



可能会用到的Java命令

~~~markdown
1. javap -s *.class //查看方法签名

2. javac *.java //编译生成class文件

3. javah [option] com.example.test
	javah [options] <classes>
	其中, [options] 包括:
	  -o <file>                输出文件 (只能使用 -d 或 -o 之一)
	  -d <dir>                 输出目录
	  -v  -verbose             启用详细输出
	  -h  --help  -?           输出此消息
      -version                 输出版本信息
      -jni                     生成 JNI 样式的标头文件 (默认值)
      -force                   始终写入输出文件
      -classpath <path>        从中加载类的路径
      -cp <path>               从中加载类的路径
      -bootclasspath <path>    从中加载引导类的路径
      <classes> 是使用其全限定名称指定的

~~~



## 2、具体实现

### 2.1、创建工具函数

创建一个`class`为`NDKTools`

代码如下：

```java
package com.example.jni;

public class NDKTools {

    public static native String getStringFromNDK();

}
```

然后修改`MainActivity`，在里面调用`NDKTools`的`getStringFromNDK()`方法。



```java
package com.example.jni;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        String text = NDKTools.getStringFromNDK();
        Log.d("Log_print","text="+text);
    }
}
```

### 2.2、获取头文件

1. 编译`NDKTools`得到`javac NDKTools.java`；
2. `javah -jni com.example.jni.NDKTools`获取c头文件`com_example_jni_NDKTools.h`(静态注册native函数需要)；
3. 创建`jni`文件夹；
   ![image-20210413200817153](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210413200817153.png)
4. 将`com_example_jni_NDKTools.h`放入`jni`文件夹下；
5. 在`jni`下创建`ndktool.c`(名字任意取)；

### 2.3、注册native函数

JNI有如下两种注册native方法的途径：

> - 静态注册：
>    先由Java得到本地方法的声明，然后再通过JNI实现该声明方法
> - 动态注册：
>    先通过JNI重载JNI_OnLoad()实现本地方法，然后直接在Java中调用本地方法。

1、静态注册

将`com_example_jni_NDKTools.h`头文件里声明的函数复制到`ndktool.c`里面实现即可

~~~c
#include "com_example_jni_NDKTools.h"
static const char *className = "com/example/jni/NDKTools";
JNIEXPORT jstring JNICALL Java_com_example_jni_NDKTools_getStringFromNDK
  (JNIEnv *env, jobject obj){
     return (*env)->NewStringUTF(env,"Hellow World");
  }
~~~

2、动态注册

~~~c
static const char *className = "com/example/jni/NDKTools";
JNIEXPORT jstring JNICALL Java_com_example_jni_NDKTools_getStringFromNDK
  (JNIEnv *env, jobject obj){
     return (*env)->NewStringUTF(env,"Hellow World");
  }
JNIEXPORT void JNICALL setText(JNIEnv *env, jclass clazz, jobject text_view) {
    
}

static JNINativeMethod gJni_Methods_table[] = {
    {"getStringFromNDK", "()Ljava/lang/String;", (void *)Java_com_example_jni_NDKTools_getStringFromNDK},
    {"setText", "(Landroid/widget/TextView;)V", (void *)setText},
};

static int jniRegisterNativeMethods(JNIEnv* env, const char* className,
    const JNINativeMethod* gMethods, int numMethods)
{
    jclass clazz;

    LOGI("Registering %s natives\n", className);
    clazz = (*env)->FindClass(env, className);
    if (clazz == NULL) {
        LOGE("Native registration unable to find class '%s'\n", className);
        return -1;
    }
    LOGI("start RegisterNatives");
    int result = 0;
    if ((*env)->RegisterNatives(env, clazz, gJni_Methods_table, numMethods) < 0) {
        LOGE("RegisterNatives failed for '%s'\n", className);
        result = -1;
    }

    (*env)->DeleteLocalRef(env, clazz);
    return result;
}

jint JNI_OnLoad(JavaVM* vm, void* reserved){
    LOGI("enter jni_onload");

    JNIEnv* env = NULL;
    jint result = -1;

    if ((*vm)->GetEnv(vm, (void**) &env, JNI_VERSION_1_4) != JNI_OK) {
        return result;
    }

    jniRegisterNativeMethods(env, className, gJni_Methods_table, sizeof(gJni_Methods_table) / sizeof(JNINativeMethod));

    return JNI_VERSION_1_4;
}
~~~

### 2.4、编写`Android.mk`文件

1. 路径在`jni`目录下
   ![image-20210413202228719](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210413202228719.png)

2. `Android.mk`内容

   ~~~makefile
   LOCAL_PATH := $(call my-dir)
   include $(CLEAR_VARS)
   LOCAL_LDLIBS :=-llog
   LOCAL_MODULE := ndkdemo
   LOCAL_SRC_FILES := ndktool.c
   include $(BUILD_SHARED_LIBRARY)
   ~~~

### 2.5、修改`module`下的`build.gradle`

![image-20210413203231850](C:\Users\apricity.qian\AppData\Roaming\Typora\typora-user-images\image-20210413203231850.png)

~~~groovy

        ndk{

            moduleName "ndkdemo"
            abiFilters "arm64-v8a", "armeabi-v7a", "x86", "x86_64"

        }
    }


        externalNativeBuild {
            ndkBuild {
                path 'src/main/jni/Android.mk'
            }
        }

    }

~~~

### 2.5、常见方法和类介绍

#### 2.5.1、JNIEnv 类型

`JNIEnv`类型实际上代表了`Java`环境，通过`JNIEnv*`指针就可以对Java端的代码进行操作。比如我们可以使用`JNIEnv`来创建`Java`类中的对象，调用`Java`对象的方法，获取`Java`对象中的属性等。
JNIEnv类中有很多函数可以用，如下所示:

~~~markdown
1. NewObject: 创建Java类中的对象。
2. NewString: 创建Java类中的String对象。
3. NDKTools.setText(tv);
4. NewArray: 创建类型为Type的数组对象。
5. GetField: 获取类型为Type的字段。
6. SetField: 设置类型为Type的字段的值。
7. GetStaticField: 获取类型为Type的static的字段。
8. SetStaticField: 设置类型为Type的static的字段的值。
9. CallMethod: 调用返回类型为Type的方法。
10. CallStaticMethod: 调用返回值类型为Type的static 方法。
~~~



#### 2.5.2、jobject 类型

`native`函数（c/c++中的实现）都至少有两个参数，JNEIEnv 和jclass或jobject

第二个参数通常为`jclass/jobject`类型，`jobject`可以看做是`java中`的类实例的引用。当然，情况不同，意义也不一样。

~~~markdown
1. 当native（java中的声明）方法为静态（static）时，第二个参数为jclass代表native方法所属的class对象

2. 当native方法为非静态时，第二个参数为jobject代表native方法所属的对象
~~~

C语言调用java中方法的语法类似于java中的反射，java中的对象映射在C语言中都用jobject表示。

#### 2.5.3、获取class对象

~~~markdown
1. (*env)->GetObjectClass(instance);   
2. (*env)->findClass("com/example/jni/NDKTools")//全限定名注意使用/ ，而不是.
~~~

