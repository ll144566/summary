# 1、完全关闭网络检查服务

- **方法：**无需 Root，使用 ADB 命令关闭系统网络检查服务：`adb shell settings put global captive_portal_detection_enabled 0`
- **缺点：**当你使用公共 Wi-Fi 这种需要使用 portal 验证的网络时，因为网络检查被关闭，系统在访问 portal 验证页面时无法返回正确的值，**最终导致无法完成验证和上网**。



# 2、替换网络检查服务的网址

7.1.0及之前为：

- `adb shell settings put global captive_portal_server connect.rom.miui.com`
- `adb shell settings put global captive_portal_server www.v2ex.com`

7.1.0及之后为：

adb shell "settings put global captive_portal_https_url https://captive.v2ex.co/generate_204"

