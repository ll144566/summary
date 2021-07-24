  ##  1、Android 8.0之后，push framework编译的目标文件

1. 验证framework需要替换如下文件

   ~~~markdown
   adb push out\target\product\xxx\system\framework\framework.jar  system/framework/
   adb push out\target\product\xxx\system\framework\boot-framework.vdex  system/framework
   adb push out\target\product\xxx\system\framework\arm\boot-framework.art  /system/framework/arm
   adb push out\target\product\xxx\system\framework\arm\boot-framework.art.rel  /system/framework/arm
   adb push out\target\product\xxx\system\framework\arm\boot-framework.oat  /system/framework/arm
   adb push out\target\product\xxx\system\framework\arm\boot.art  system/framework/arm/
   adb push out\target\product\xxx\system\framework\arm\boot.oat  system/framework/arm/
   adb push out\target\product\xxx\system\framework\arm64\boot.art  system/framework/arm64/
   adb push out\target\product\xxx\system\framework\arm64\boot.oat  system/framework/arm64/
   adb push out\target\product\xxx\system\framework\arm64\boot-framework.art  /system/framework/arm64
   adb push out\target\product\xxx\system\framework\arm64\boot-framework.art.rel  /system/framework/arm64
   adb push out\target\product\xxx\system\framework\arm64\boot-framework.oat  /system/framework/arm64
   ~~~

2. 验证services需要替换如下文件

   ~~~markdown
   adb push out\target\product\xxx\system\framework\services.jar  system/framework/
   adb push out\target\product\xxx\system\framework\services.jar.prof  system/framework
   adb push out\target\product\xxx\system\framework\oat\arm64\services.art  system/framework/oat/arm64/
   adb push out\target\product\xxx\system\framework\oat\arm64\services.odex  system/framework/oat/arm64/
   adb push out\target\product\xxx\system\framework\oat\arm64\services.vdex  system/framework/oat/arm64/
   ~~~

3. 验证telephony-common需要替换如下文件

   ~~~markdown
   adb push out/target/product/xxx/system/framework/telephony-common.jar /system/framework
   adb push out/target/product/xxx/system/framework/arm/boot-telephony-common.oat /system/framework/arm
   adb push out/target/product/xxx/system/framework/arm/boot-telephony-common.art /system/framework/arm
   adb push out/target/product/xxx/system/framework/arm64/boot-telephony-common.oat /system/framework/arm64
   adb push out/target/product/xxx/system/framework/arm64/boot-telephony-common.art /system/framework/arm64
   ~~~

4. 如果有修改frameworks\base\services\java\com\android\server\SystemServer.java文件中的逻辑，需要要把第一步中framework也替换掉，否则会因为SystemServer类找不到导致system_server进程启动失败！

## 2、刷机时APK可以用，Install这个apk后不能用

[参考连接](https://blog.csdn.net/luliyuan/article/details/78750916)

使用adb install -r安装SnapDragonCamera之后打开相机，有如下报错：

~~~markdown
2021-03-19 09:07:47.242 4656-4656/org.codeaurora.snapcam E/linker: library "/system/lib64/libjni_imageutil.so" ("/system/lib64/libjni_imageutil.so") needed or dlopened by "/apex/com.android.runtime/lib64/libnativeloader.so" is not accessible for the namespace: [name="classloader-namespace", ld_library_paths="", default_library_paths="", permitted_paths="/data:/mnt/expand:/data/data/org.codeaurora.snapcam"]
2021-03-19 09:07:47.243 4656-4656/org.codeaurora.snapcam E/AndroidRuntime: FATAL EXCEPTION: main
    Process: org.codeaurora.snapcam, PID: 4656
    java.lang.UnsatisfiedLinkError: dlopen failed: library "/system/lib64/libjni_imageutil.so" needed or dlopened by "/apex/com.android.runtime/lib64/libnativeloader.so" is not accessible for the namespace "classloader-namespace"
        at java.lang.Runtime.loadLibrary0(Runtime.java:1071)
~~~

这个报错的意思是说，apk通过dlopen打开一个native库时，Nativeloader打不开libjni_imageutil.so。

这个可以在LoadedApk.java中找到原因，相关代码如下：

```java
//frameworks/base/core/java/android/app/LoadedApk.java
private void createOrUpdateClassLoaderLocked(List<String> addedPaths) {
    ...
    boolean isBundledApp = mApplicationInfo.isSystemApp()
            && !mApplicationInfo.isUpdatedSystemApp();

    // Vendor apks are treated as bundled only when /vendor/lib is in the default search
    // paths. If not, they are treated as unbundled; access to system libs is limited.
    // Having /vendor/lib in the default search paths means that all system processes
    // are allowed to use any vendor library, which in turn means that system is dependent
    // on vendor partition. In the contrary, not having /vendor/lib in the default search
    // paths mean that the two partitions are separated and thus we can treat vendor apks
    // as unbundled.
    final String defaultSearchPaths = System.getProperty("java.library.path");
    final boolean treatVendorApkAsUnbundled = !defaultSearchPaths.contains("/vendor/lib");
    if (mApplicationInfo.getCodePath() != null
            && mApplicationInfo.isVendor() && treatVendorApkAsUnbundled) {
        isBundledApp = false;
    }

    makePaths(mActivityThread, isBundledApp, mApplicationInfo, zipPaths, libPaths);

    String libraryPermittedPath = mDataDir;

    if (isBundledApp) {
        // For bundled apps, add the base directory of the app (e.g.,
        // /system/app/Foo/) to the permitted paths so that it can load libraries
        // embedded in module apks under the directory. For now, GmsCore is relying
        // on this, but this isn't specific to the app. Also note that, we don't
        // need to do this for unbundled apps as entire /data is already set to
        // the permitted paths for them.
        libraryPermittedPath += File.pathSeparator
                + Paths.get(getAppDir()).getParent().toString();

        // This is necessary to grant bundled apps access to
        // libraries located in subdirectories of /system/lib
        libraryPermittedPath += File.pathSeparator + defaultSearchPaths;
    }
    ...
}
```

​    

看上面的注释可以知道，如果是系统apk并且没有升级过的话，so库的搜索路径就会增加一个system/lib64，而install -r来安装apk就相当于升级，所以刷机时apk可以用，install升级后不能用。

谷歌原生提供的公共库是放在/system/etc/public.libraries.txt里面，引用这里的库不会存在上述的问题。而cat public.libraries.txt,会发现根本没有libjni_imageutil这个字段

1. 将需要调用的libjni_imageutil.so放到/system/lib下；
2. 运行程序发现报错,百度一查说是要把改so库的名字写到/system/etc/public.libraries.txt,这个文件里；
3. adb pull出来,修改,adb push进去,重启。

以下是Google相关文档说明连接

https://source.android.com/devices/tech/config/namespaces_libraries