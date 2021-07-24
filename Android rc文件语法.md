class core ，class main， class late_start。

service类型的section标识了一个service(或者说可执行程序), 那这个service什么时候被执行呢？是在
class_start 这个命令被执行的时候，这个命令行总是存在于某个on类型的section中，“class_start core”这样一条命令被执行，就会启动类型为core的所有service。

这三个“class”,只是标识这个服务的类型是哪一个，然后通过调用class_start, class_reset, class_stop等命令的时候，来统一操作同一类的服务。

举个例子，从system/core/rootdir/init.rc文件中搜索“class main”可以搜到许多，例如有netd， ril-deamon服务被标识为class main,那么当我们调用class_start main命令时，所有标识为main的服务都会被启动，这里的netd ril-deamon就会被启动。对于core， late_start类的服务也是这样的。