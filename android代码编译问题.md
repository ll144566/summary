报错如下

~~~shell
flex-2.5.39: loadlocale.c:130:_nl_intern_locale_data: ?? 'cnt < (sizeof (_nl_value_type_LC_TIME) / sizeof (_nl_value_type_LC_TIME[0]))' ???
~~~

解决办法：
在～/.bashrc最后添加export LC_ALL=C
然后 source ～/.bashrc
解答： 添加export LC_ALL=C是去除本地C化，使得Android的编译工具与本地工具不冲突。