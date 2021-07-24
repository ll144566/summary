先删除默认的地址：

adb shell settings delete global captive_portal_https_url
adb shell settings delete global captive_portal_http_url

再修改新的地址：

adb shell settings put global captive_portal_https_url https://connect.rom.miui.com/generate_204
adb shell settings put global captive_portal_http_url http://connect.rom.miui.com/generate_204











