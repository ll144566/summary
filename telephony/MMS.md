SmsReceiverService.java这个是短信的，TransactionService.java是彩信的，当你因为网络状态不对发不了彩信的时候，你会经常遇到它。SendTransaction.java彩信发送，NotificationTransaction.java自动接收彩信，RetrieveTransaction.java手动下载彩信，TransactionSettings.java获取apn相关信息的。短信呢是走RIL出去的，彩信呢是走http协议的，一个电路域，一个分组域。

![1347629908_7292](F:\总结文档\picture\1347629908_7292.png)

