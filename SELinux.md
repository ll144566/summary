（大部分内容从网上整理而来）

# 1 基本概念

## 1.1  DAC 和 MAC

SELinux，Security Enhanced Linux 的缩写，也就是安全强化的 Linux。

我们知道，传统的 Linux 系统中，默认权限是对文件或目录的所有者、所属组和其他人的读、写和执行权限进行控制，这种控制方式称为自主访问控制（DAC）方式；而在 SELinux 中，采用的是强制访问控制（MAC）系统，也就是控制一个进程对具体文件系统上面的文件或目录是否拥有访问权限，而判断进程是否可以访问文件或目录的依据，取决于 SELinux 中设定的很多策略规则。

说到这里，读者有必要详细地了解一下这两个访问控制系统的特点：

- 自主访问控制系统（Discretionary Access Control，DAC）

  是 Linux 的默认访问控制方式，也就是依据用户的身份和该身份对文件及目录的 rwx 权限来判断是否可以访问。不过，在 DAC 访问控制的实际使用中我们也发现了一些问题：

  1. root 权限过高，rwx 权限对 root 用户并不生效，一旦 root 用户被窃取或者 root 用户本身的误操作，都是对 Linux 系统的致命威胁。
  2. Linux 默认权限过于简单，只有所有者、所属组和其他人的身份，权限也只有读、写和执行权限，并不利于权限细分与设定。
  3. 不合理权限的分配会导致严重后果，比如给系统敏感文件或目录设定 777 权限，或给敏感文件设定特殊权限——SetUID 权限等。

- 强制访问控制（Mandatory Access Control，MAC）是通过 SELinux 的默认策略规则来控制特定的进程对系统的文件资源的访问。也就是说，即使你是 root 用户，但是当你访问文件资源时，如果使用了不正确的进程，那么也是不能访问这个文件资源的。


这样一来，SELinux 控制的就不单单只是用户及权限，还有进程。每个进程能够访问哪个文件资源，以及每个文件资源可以被哪些进程访问，都靠 SELinux 的规则策略来确定。

注意，在 SELinux 中，Linux 的默认权限还是有作用的，也就是说，一个用户要能访问一个文件，既要求这个用户的权限符合 rwx 权限，也要求这个用户的进程符合 SELinux 的规定。

需要注意的是，SELinux 的 MAC 并不会完全取代 DAC，恰恰相反，对于 Linux 系统安全来说，它是一个额外的安全层，换句话说，当使用 SELinux 时，DAC 仍然被使用，且会首先被使用，如果允许访问，再使用 SELinux 策略；反之，如果 DAC 规则拒绝访问，则根本无需使用 SELinux 策略。

例如，若用户尝试对没有执行权限（rw-）的文件进行执行操作，那么传统的 DAC 规则就会拒绝用户访问，因此，也就无需再使用 SELinux 策略。



关于 DAC 和 MAC，可以总结几个知识点：

~~~markdown
1. Linux 系统先做 DAC 检查。如果没有通过 DAC 权限检查，则操作直接失败。通过 DAC 检查之后，再做 MAC 权限检查。
2. SELinux 有自己的一套规则来编写安全策略文件，这套规则被称之为 SELinux Policy 语言。
~~~



相比传统的 Linux DAC 安全控制方式，SELinux 具有诸多好处，比如说：

~~~markdown
1. 它使用的是 MAC 控制方式，这被认为是最强的访问控制方式；
2. 它赋予了主体（用户或进程）最小的访问特权，这也就意味着，每个主体仅被赋予了完成相关任务所必须的一组有限的权限。通过赋予最小访问特权，可以防止主体对其他用户或进程产生不利的影响；
3. SELinux 管理过程中，每个进程都有自己的运行区域（称为域），各进程仅运行在自己的域内，无法访问其他进程和文件，除非被授予了特殊权限。
4. SELinux 可以调整到 Permissive 模式，此模式允许查看在系统上执行 SELinux 后所产生的印象。在 Permissive 模式中，SELinux 仍然会记录它所认为的安全漏洞，但并不会阻止它们。
~~~



其它几个概念。

1. 主体（Subject）：就是想要访问文件或目录资源的进程。想要得到资源，基本流程是这样的：由用户调用命令，由命令产生进程，由进程去访问文件或目录资源。在自主访问控制系统中（Linux 默认权限中），靠权限控制的主体是用户；而在强制访问控制系统中（SELinux 中），靠策略规则控制的主体则是进程。

2. 目标（Object）：这个概念比较明确，就是需要访问的文件或目录资源。

3. 策略（Policy）

   Linux 系统中进程与文件的数量庞大，那么限制进程是否可以访问文件的 SELinux 规则数量就更加烦琐，如果每个规则都需要管理员手工设定，那么 SELinux 的可用性就会极低。还好我们不用手工定义规则，SELinux 默认定义了两个策略，规则都已经在这两个策略中写好了，默认只要调用策略就可以正常使用了。这两个默认策略如下：

   - -targeted：这是 SELinux 的默认策略，这个策略主要是限制网络服务的，对本机系统的限制极少。
   - -mls：多级安全保护策略，这个策略限制得更为严格。

4. 安全上下文（Security Context）：每个进程、文件和目录都有自己的安全上下文，进程具体是否能够访问文件或目录，就要看这个安全上下文是否匹配。如果进程的安全上下文和文件或目录的安全上下文能够匹配，则该进程可以访问这个文件或目录。当然，判断进程的安全上下文和文件或目录的安全上下文是否匹配，则需要依靠策略中的规则。举个例子，我们需要找对象，男人可以看作主体，女人就是目标了。而男人是否可以追到女人（主体是否可以访问目标），主要看两个人的性格是否合适（主体和目标的安全上下文是否匹配）。不过，两个人的性格是否合适，是需要靠生活习惯、为人处世、家庭环境等具体的条件来进行判断的（安全上下文是否匹配是需要通过策略中的规则来确定的）。

## 1.2 SELinux 3种不同的策略

SELinux 提供 3 种不同的策略可供选择，分别是 Targeted、MLS 以及 MiNimum。每个策略分别实现了可满足不同需求的访问控制，因此，为了正确地选择一个满足特定安全需求的策略，就不得不先了解这些策略类型。

- Target 策略

  Target 策略主要对系统中的服务进程进程访问控制，同时，它还可以限制其他进程和用户。服务进程都被放入沙盒，在此环境中，服务进程会被严格限制，以便使通过此类进程所引发的恶意攻击不会影响到其他服务或 Linux 系统。

  沙盒（sandbox）是一种环境，在此环境中的进程可以运行，但对其他进程或资源的访问会被严格控制。换句话说，位于沙盒中的各个进程，都只是运行在自己的域（进程所运行的区域被称为“域”）内，它们无法访问其他进程或资源（除非被授予特殊的权限）。

  通过使用此策略，可以更加安全地共享打印服务器、文件服务器、Web 服务器或其他服务，同时降低因访问这些服务而对系统中其他资源造成不利影响的风险。

- MLS 策略

  MLS，是 Multi-Level Security 的缩写，该策略会对系统中的所有进程进行控制。MLS将系统的进程和文件进行了分级，不同级别的资源需要对应级别的进程才能访问。启用 MLS 之后，用户即便执行最简单的指令（如 ls），都会报错。

- Minimum 策略

  Minimum 策略的意思是“最小限制”，该策略最初是针对低内存计算机或者设备（比如智能手机）而创建的。

  从本质上来说，Minimun 和 Target 类似，不同之处在于，它仅使用基本的策略规则包。对于低内存设备来说，Minumun 策略允许 SELinux 在不消耗过多资源的情况下运行。



## 1.3 SEAndroid

SEAndroid在架构和机制上与SELinux完全一样，考虑到移动设备的特点，所以移植到SEAndroid的只是SELinux的一个子集。SEAndroid的安全检查覆盖了所有重要的方面包括了域转换、类型转换、进程相关操作、内核相关操作、文件目录相关操作、文件系统相关操作、对设备相关操作、对app相关操作、对网络相关操作、对IPC相关操作。

policy是整个SEAndroid安全机制的核心之一，除了有好的安全架构外还必须有好的安全策略以确保让访问主体只拥有最小权限，使程序既能顺利执行基本功能又能防止被恶意使用。

在SEAndroid中主要采用了两种强制访问方法：

- TE
- MLS

这两种方法都在policy中得以实现，

## 1.4 SEAndroid app 的分类
SELinux(或SEAndroid)将app划分为主要三种类型(根据user不同，也有其他的domain类型)：

1. untrusted_app 第三方app，没有android平台签名，没有system权限
2. platform_app 有android平台签名，没有system权限
3. system_app 有android平台签名和system权限

从上面划分，权限等级，理论上：untrusted_app < platform_app < system_app

# 2 权限

## 2.1 查看进程权限

在android上面，`adb shell`之后进入手机，`ps -Z`可以查看当前进程所拥有的selinux的权限。

```shell
$ ps -Z
LABEL                          USER     PID   PPID  NAME
u:r:init:s0                    root      1     0     /init
u:r:kernel:s0                  root      2     0     kthreadd
...
u:r:kernel:s0                  root      258   2     irq/322-HPH_R O
u:r:logd:s0                    logd      259   1     /system/bin/logd
u:r:healthd:s0                 root      260   1     /sbin/healthd
u:r:lmkd:s0                    root      261   1     /system/bin/lmkd
u:r:servicemanager:s0          system    262   1     /system/bin/servicemanager
u:r:vold:s0                    root      263   1     /system/bin/vold
u:r:surfaceflinger:s0          system    264   1     /system/bin/surfaceflinger
u:r:tctd:s0                    root      265   1     /system/bin/tctd
u:r:rfs_access:s0              system    268   1     /system/bin/rfs_access
u:r:tee:s0                     system    271   1     /system/bin/qseecomd
u:r:kernel:s0                  root      280   2     kworker/3:1H
u:r:kernel:s0                  root      290   2     kauditd
u:r:rmt_storage:s0             nobody    291   1     /system/bin/rmt_storage
u:r:shell:s0                   shell     292   1     /system/bin/sh
u:r:netd:s0                    root      295   1     /system/bin/netd
u:r:debuggerd:s0               root      296   1     /system/bin/debuggerd
u:r:tee:s0                     system    297   271   /system/bin/qseecomd
```

在这个例子中，我们可以进行分析。

- `u`：在android中，只定义了一个user即为`u`

- `r`：进程统一定义成`r` ， 文件统一定义成 `object_r`

- `init`：进程所属的域 , 不唯一。

- `s0`：一种安全等级

  

## 2.2 查看文件权限

另外就是文件，文件想要查看相关SELINUX权限的话，需要去执行`ls -Z`

```shelll
$ ls -Z
drwxr-x--x root     sdcard_r          u:object_r:rootfs:s0 storage
drwx--x--x root     root              u:object_r:tmpfs:s0 synthesis
dr-xr-xr-x root     root              u:object_r:sysfs:s0 sys
drwxr-xr-x root     root              u:object_r:system_file:s0 system
drwxrwxr-x system   tctpersist          u:object_r:tct_persist_file:s0 tctpersist
lrwxrwxrwx root     root              u:object_r:rootfs:s0 tombstones -> /data/tombstones
-rw-r--r-- root     root              u:object_r:rootfs:s0 ueventd.qcom.rc
-rw-r--r-- root     root              u:object_r:rootfs:s0 ueventd.rc
```

- u：在android中，只定义了一个user即为`u`
- object_r：代表是一个文件
- rootfs：这种代表文件所属的域，看有的解释说可以理解成type
- s0：一种安全等级

# 3 配置selinux

## 3.1 分类

SELinux策略分离成平台（platform）和非平台（non-platform）两部分，而平台策略为了给非平台作者导出特定的类型和属性，又分为平台私有（platform private）和平台公有（platform public）部分。

- 平台公有策略（platform public seoplicy）

  平台共有策略全部定义在/system/sepolicy/public下，public下的type和attribute可以被non-platform中的策略所使用，也就是说，设备制造商的sepolicy作者在non-platform下可以对platform public sepolicy的策略进行扩展。

- 平台私有策略（platform private seoplicy）

  与公有策略相反，被声明为私有策略的type或attribute对non-platform的策略作者是不可见的。

## 3.2 上下文描述文件

可以在上下文的描述文件中为您的对象指定标签。

| 文件名              | 归类        |
| ------------------- | ----------- |
| mac_permissions.xml | App进程     |
| seapp_contexts      | App数据文件 |
| file_contexts       | 系统文件    |
| property_contexts   | 系统属性    |

- `file_contexts` 系统中所有file_contexts安全上下文,用于为文件分配标签，并且可供多种用户空间组件使用。在创建新政策时，请创建或更新该文件，以便为文件分配新标签。
- `genfs_contexts` 虚拟文件系统安全上下文,用于为不支持扩展属性的文件系统（例如，`proc` 或 `vfat`）分配标签。
- `property_contexts` 属性的安全上下文,用于为 Android 系统属性分配标签，以便控制哪些进程可以设置这些属性。
- `service_contexts service`文件安全上下文,用于为 Android Binder 服务分配标签，以便控制哪些进程可以为相应服务添加（注册）和查找（查询）Binder 引用。
- `seapp_contexts app`安全上下文,用于为app进程和 /data/data 目录分配标签。
- `mac_permissions.xml` 用于根据应用签名和应用软件包名称（后者可选）为应用分配 `seinfo` 标记。随后，分配的 `seinfo` 标记可在 `seapp_contexts` 文件中用作密钥，以便为带有该 `seinfo` 标记的所有应用分配特定标签。

## 3.3 策略文件te

以te结尾的文件是SELinux中的策略文件，它定义了作用域和标签。
来看一个te文件：

```shell
allow factory ttyMT_device:chr_file { read write open ioctl};
allow factory ttyGS_device:chr_file { read write open ioctl};
allow factory irtx_device:chr_file { read write ioctl open };
```

上面这几行就是最基本的te语句了，相似的te语句的会被归类在一个的te文件下面。如上面的语句都是作用于`factory`，则会在`factory.te`文件里。

例如第一条

```shell
allow factory ttyMT_device:chr_file { read write open ioctl};
# 当然了，实际上面的语句不一定放在上面指定的文件里，放在任何文件里效果是一样的，但是为了方便阅读和管理，还是添加到对应的文件中比较好
```

翻译一下就是

```shell
允许`factory`域里的进程或服务
对类型为`ttyMT_device`的类别为文件(`chr_file`)
执行`read`,`write`,`open`,`ioctl`权限的操作
```



**te文件的基本语法：**

```shell
# rule_name source_type target_type:class perm_set
```

- rule_name：规则名，分别有allow，dontaudit，auditallow，neverallow等
- source_type：源类型，主要作用是用来填写一个域(domain)
- target_type：目标的类型
- class：类别，目标（客体）是哪种类别，主要有File,Dir,Socket,SEAndroid还有Binder等，在这些基础上又细分出设备字符类型（chr_file），链接文件（lnk_file）等。可以通过ls -l查看文件类型
- perm_set：动作集

**我们从上到下按顺序介绍一下：**

### 3.3.1 rule_name

| 规则名称   | 匹配是否允许 | 不匹配是否允许 | 匹配是否记录 | 不匹配是否记录 |
| ---------- | ------------ | -------------- | ------------ | -------------- |
| allow      | **Yes**      | No             | No           | **Yes**        |
| dontaudit  | No           | No             | No           | No             |
| auditallow | No           | No             | **Yes**      | **Yes**        |
| neverallow | -            | -              | -            | -              |

- `allow`：允许某个进程执行某个动作
- `auditallow`：audit含义就是记录某项操作。默认SELinux只记录那些权限检查失败的操作。 auditallow则使得权限检查成功的操作也被记录。注意，allowaudit只是允许记录，它和赋予权限没关系。赋予权限必须且只能使用allow语句。
- `dontaudit`：对那些权限检查失败的操作不做记录。
- `neverallow`：没有被`allow`到的动作默认就不允许执行的。`neverallow`只是显式地写出某个动作不被允许，如果添加了该动作的allow，则会编译错误。

### 3.3.2 source_type
指定一个“域”（`domain`），一般用于描述`进程`，该域内的的进程受该条TE语句的限制。用`type`关键字，把一个自定义的域与原有的域相关联

```shell
type shell, domain;
```

上面这句话的意思是，赋予`shell`给`domain`属性，同时，`shell`域属于`domain`这个集合里。如果有一个`allow domain xxxxx`的语句，同样地也给了`shell xxxxx`的属性

### 3.3.3 target_type

指定进程需要操作的客体（文件，文件夹等）类型，同样是用`type`与一些已有的类型，属性相关联
以上面的ttyMT_device为例：

```shell
# 定义一个类型，属于dev_type属性
type ttyMT_device, dev_type; 
```

属性`dev_type`在`system/sepolicy/public/attributes`的定义如下

```shell
attribute dev_type;
```

`attribute`关键字定义一个属性，`type`可以与一个或多个属性关联，例如：

```shell
type usb_device, dev_type, mlstrustedobject;
```

另外，还有一个关键字`typeattribute`，type有两个作用：

1. 定义（声明）
2. 关联某个属性。

可以把这两个作用分开，`type`定义，`typeattribute`进行关联

```shell
# 定义httpd_user_content_t，并关联两个属性
type httpd_user_content_t, file_type, httpdcontent;
```

分成两条语句进行表述：

```shell
#定义httpd_user_content_t
type httpd_user_content_t;
#关联属性
typeattribute httpd_user_content_t file_type, httpdcontent;
```

在`system/sepolicy/public/attributes`里定义了很多属性，下面截取了一些常见的定义：

```shell
# All types used for devices.
attribute dev_type;
# All types used for processes.
attribute domain;
# All types used for filesystems.
attribute fs_type;
# All types used for files that can exist on a labeled fs.
# Do not use for pseudo file types.
attribute file_type;
# All types used for domain entry points.
attribute exec_type;
# All types used for property service
attribute property_type;
# All service_manager types created by system_server
attribute system_server_service;
# All domains that can override MLS restrictions.
# i.e. processes that can read up and write down.
attribute mlstrustedsubject;
# All types that can override MLS restrictions.
# i.e. files that can be read by lower and written by higher
attribute mlstrustedobject;
# All domains used for apps.
attribute appdomain;
# All domains used for apps with network access.
attribute netdomain;
# All domains used for binder service domains.
attribute binderservicedomain;
```



特别注意：对初学者而言，`attribute`和`type`的关系最难理解，因为`attribute`这个关键词实在是没取好名字，很容易产生误解：

> - 实际上，type和attribute位于同一个命名空间，即不能用type命令和attribute命令定义相同名字的东西。
> - 其实，attribute真正的意思应该是类似type（或domain） group这样的概念。比如，将type A和attribute B关联起来，就是说type A属于group B中的一员。

使用`attribute`有什么好处呢？一般而言，系统会定义数十或数百个Type，每个Type都需要通过allow语句来设置相应的权限，这样我们的安全策略文件编起来就会非常麻烦。有了`attribute`之后呢，我们可以将这些Type与某个`attribute`关联起来，然后用一个`allow`语句，直接将source_type设置为这个`attribute`就可以了：

> - 这也正是type和attribute位于同一命名空间的原因。
> - 这种做法实际上只是减轻了TE文件编写者的烦恼，安全策略文件在编译时会将attribute拓展为其包含的type。



```shell
#定义两个type，分别是A_t和B_t，它们都管理到attribute_test
type A_t attribute_test;
type B_t attribute_test;

#写一个allow语句，直接针对attribute_test
allow attribute_test C_t:file {read write};
#上面这个allow语句在编译后的安全策略文件中会被如下两条语句替代：
allow A_t C_t:file {read write};
allow B_t C_t:file {read write};
```

### 3.3.4 class
客体的具体类别。用`class`来定义一个客体类别，来看一下`system/sepolicy/private/security_classes`文件

```shell
# file-related classes
class filesystem
class file #代表普通文件
class dir #代表目录
class fd #代表文件描述符
class lnk_file #代表链接文件
class chr_file #代表字符设备文件
......
# network-related classes
class socket #socket
class tcp_socket
class udp_socket
......
class binder #Android平台特有的binder
class zygote #Android平台特有的zygote
```

### 3.3.5 perm_set
有两种定义方法。

- 用`common`命令定义：
  格式为：

```shell
common common_name { permission_name ... }
```

`common`定义的`perm_set`能被另外一种`perm_set`命令`class`所继承，而`class`定义的`perm_set`则不能被继承
如：

```shell
common file {
	ioctl read write create getattr setattr lock relabelfrom relabelto
	append unlink link rename execute swapon quotaon mounton
}
```

- 用`class`命令定义：

```shell
class class_name [ inherits common_name ] { permission_name ... }
```

例如`class dir`继承了`file`



```shell
class dir
inherits file
{
	add_name
	remove_name
	reparent
	search
	rmdir
	open
	audit_access
	execmod
}
```

### 3.3.6 其它语法

- self

  规则中可以出现self字样，以下两条规则等价

  allow user_t user_t : process signal;

  allow user_t self: process signal;

- 类型否定

  类型否定用来在一系列的type中减去某个type，比如以下规则从exec_type中减去sbin_t

  allow domain (exec_type -sbin_t): file{read、execute、getattr}

- class的权限

  allow user_t bin_t : {file dir} {read getattr}

  等价于：

  allow user_t bin_t : file {read getattr}

  allow user_t bin_t : dir {read getattr}

- 通配符

  allow user_t bin_t : dir *

  表示赋予所有权限

- 多个type和attribute

  如果有多个type和attribute存在，则可以用括号表示多个，并且type的attribute可以混用

  allow {domain user_t} {file_type bin_t}: file{read、execute、getattr}

- 取反操作符

  allow user_t bin_t : file ~{read getattr}

  表示除了read和getattr之外的权限全部赋予

## 3.4 别名(为确保兼容性而存在)

   别名是引用类型时的一个备选的名字，能够使用类型名的地方就可以使用别名，包括TE规则，安全上下文和标记语句，别名通常用于策略改变时保证一致性，例如：一个旧策略可能引用了类型netscape_t，更新后的策略可能将类型名改为mozilla_t了，但同时提供了一个别名netscape_t以保证与旧模块能够正确兼容。

- 在`type`中声明别名

  ~~~shell
  1. type mozilla_t alias netscape_t, domain; 
  
     注意别名声明是放在属性的前面的。
  ~~~


- 使用`typealias`申明别名

  ~~~shell
  1. # 这两条语句等同于  
  2. type mozilla_t, domain;  
  3. typealias mozilla_t alias netscape_t;  
  4.  
  5. #下面这一条语句  
  6. type mozilla_t alias netscape_t, domain; 
  ~~~

  

- `typealias`语句语法

  <font color=#FF0000 size=4 >typealias 类型名称 alias 别名名称</font>

  - 类型名称：要添加别名的类型的名称，类型必须使用type语句单独声明，而且这里只能指定一个类型名称。
  - 别名名称：如果同时指定多个别名，别名之间用空格分开，并使用大括号将所有别名括起来，如{aliasa_t aliasb_t}。
  - `typealias`语句在单个策略，基础载入模块和非基础载入模块中都有效，只有在条件语句中无效。 

## 3.5  域转换

### 3.5.1 基本语法

 SEAndroid中，init进程的SContext为u:r:init:s0（在init.rc中使用” setcon u:r:init:s0”命令设置），而init创建的子进程显然不会也不可能拥有和init进程一样的SContext（否则根据TE，这些子进程也就在MAC层面上有了和init进程一样的权限）。那么这些子进程是怎么被打上和父进程不一样的SContex呢？

 在SELinux中，上述问题被称为`DomainTransition`，即某个进程的Domain切换到一个更合适的Domain中去。`DomainTransition`也是在安全策略文件中配置的，而且有相关的关键字。

 这个关键字就是`type_transition`，表示类型转换，其完整格式如下：

 ~~~shell
type_transition source_type target_type : class default_type
 ~~~

 表示source_type域的进程在对target_type类型的文件进行class定义的操作时，进程会切换到default_type域中，下面我们看个域转换的例子：

~~~shell
 type_transition init shell_exec:process init_shell
~~~

 这个例子表示：当init域的进程执行（process）shell_exec类型的可执行文件时，进程会从init域切换到init_shell域。那么，哪个文件是shell_exec类型呢？从file_contexts文件能看到，/system/bin/sh的安全属性是u:object_r:shell_exec:s0，也就是说init域的进程如果运行shell脚本的话，进程所在的域就会切换到init_shell域，这就是`DomainTransition`（简称DT）。

 请注意，DT也是SELinux安全策略的一部分，`type_transition`不过只是开了一个头而已，要真正实施成功这个DT，还至少需要下面三条权限设置语句：



~~~shell
 # 首先，你得让init域的进程要能够执行shell_exec类型的文件

 allow init shell_exec:file execute;

 # 然后，你需要告诉SELinux，允许init域的进程切换到init_shell域

 allow init init_shell:process transition;

 # 最后，你还得告诉SELinux，域切换的入口（entrypoint）是执行shell_exec类型的文件

 allow init_shell shell_exec:file entrypoint;
~~~



 看起来挺麻烦，不过SELinux支持宏定义，我们可以定义一个宏，把上面4个步骤全部包含进来。在SEAndroid中，所有的宏都定义在te_macros文件中，其中和DT相关的宏定义如下：



~~~shell
 # 定义domain_trans宏，$1,$2,$3代表宏的第一个，第二个…参数
 define(`domain_trans', `
 allow $1 $2:file { getattr open read execute };
 allow $1 $3:process transition;
 allow $3 $2:file { entrypoint open read execute getattr };
 … …
 ')

 # 定义domain_auto_trans宏，这个宏才是我们在te中直接使用的
 define(`domain_auto_trans', `
 # Allow the necessary permissions.
 domain_trans($1,$2,$3)
 # Make the transition occur by default.
 type_transition $1 $2:process $3;

 ')
~~~



是不是简单多了，domain_trnas宏在DT需要的最小权限的基础上还增加了一些权限，在te文件中可以直接用domain_auto_trans宏来显示声明域转换，如下：

 domain_auto_trans(init, shell_exec, init_shell)

### 3.5.2 经典实例

这是一个SELinux当中的域转换经典例子，在这里引用它，只为了更好地理解域转换

![img](https://img2018.cnblogs.com/blog/1184911/201902/1184911-20190219211821716-584009853.png)

用户joe的进程在user_t域，他想要修改密码，于是fork出一个新的process企图去修改密码。密码们都存在/etc/shadow当中，规则说，只有passwd_t类型的进程才可以去修改这个文件，joe同学fork出来的新进程继承了父进程的user_t域怎么办？得找个方法完成域转换，方法就是，运行/usr/bin/passwd文件，这是一个可执行文件，它的类型是passwd_exec_t，运行了它，就可以把自己的域转换到passwd_t了。这个过程中，包括了三个许可规则。

1、 进程的新域类型对可执行文件类型有entrypoint 访问权

只有运行了passwd_exec_t类型的file（/usr/bin/passwd），进程才能转到passwd_t域

```
allow passwd_t passwd_exec_t : file entrypoint;
```

passwd_t域将passwd_exec_t类型的file（/usr/bin/passwd）作为entrypoint

2、进程的当前（或旧的）域类型对入口文件类型有execute访问权

user_t类型的进程有权去运行passwd_exec_t类型的file（/usr/bin/passwd）

```
allow user_t passwd_exec_t : file {getattr execute};
```

user_t域对passwd_exec_t类型的file（/usr/bin/passwd）有execute权限

3、进程当前的域类型对新的域类型有transition访问权

user_t域有权转换到passwd_t域

```
allow user_t passwd_t : process transition;
```

user_t域对passwd_t类型的process有transition权限



在上面的例子中的三个许可，只是保证了修改密码时需要的域转换能够成功，可是用户才不懂什么域转换，更不会知道修改一下密码都要转来转去的。好吧，用户既然不知道，那就让计算机知道吧。。。

当一个类型为user_t的进程执行一个类型为passwd_exec_t的文件时，进程类型将会尝试转换，除非有其它请求，默认是换到passwd_t。这是一个默认转换规则，有了它，计算机在发现用户想要改密码时，就会根据这条规则进行必要的域转换。

规则中可以同时指定多个源类型，只要使用大括号将它们括起来，并用空格进行分隔就可以了，同样，我们还可以使用属性，在类型规则中列出类型和属性集，如：

~~~shell
type_transition { user_t sysadm_t }passwd_exec_t : process passwd_t;
~~~



这条type_transition规则在源列表中包括两个类型：user_t和sysadm_t。这条规则将会展开为两条规则，前面这条规则与下面这两条规则的含义完全一样：

~~~shell
#这两条规则.
 type_transition user_t passwd_exec_t : process passwd_t;
 type_transition sysadm_t passwd_exec_t : process passwd_t;
~~~



### 3.5.3 什么时候需要域转换

在SEAndroid中，以下两种情况会发生域转换：

1. 某个程序被执行时，其相应的进程会处在相应的domain中，但当程序根据需要又执行了另一个程序时，进程就需要根据typetransition规则进行domaintransition以获得必要的权限从而使新进程能顺利访问到相关文件。
2. 另一个transition的原因是原有的domain权限过大，为了不让新启动的进程也继承过大的权限，因此需要domaintransition。在SEAndroid中几乎全部daemon进程都需要从init进程中启动，这就需要从initdomian转换到daemondomain这一操作

## 3.6 类型转换

 除了DT外，还有针对Type的Transition（简称TT）。举个例子，假设目录A的SContext为u:r:dir_a，那么默认情况下，在该目录下创建的文件的SContext就是u:r:dir_a，如果想让它的SContext发生变化，那么就需要TypeTransition。

 和DT类似，TT的关键字也是type_transition，而且要顺利完成Transition，也需要申请相关权限，废话不多说了，直接看te_macros是怎么定义TT所需的宏：



~~~shell
 # 定义file_type_trans宏，为Type Transition申请相关权限
 define(`file_type_trans', `
 allow $1 $2:dir ra_dir_perms;
 allow $1 $3:notdevfile_class_set create_file_perms;
 allow $1 $3:dir create_dir_perms;
 ')

 # 定义file_type_auto_trans(domain, dir_type, file_type)宏
 # 该宏的意思就是当domain域的进程在dir_type类型的目录创建文件时，该文件的SContext
 # 应该是file_type类型

 define(`file_type_auto_trans', `
 # Allow the necessary permissions.
 file_type_trans($1, $2, $3)
 # Make the transition occur by default.
 type_transition $1 $2:dir $3;
 type_transition $1 $2:notdevfile_class_set $3;
 ')
~~~



## 3.7 几个例子

```shell
# 将init关联到domain，即将domain设置为init类型的属性
type init, domain;

# 允许init类型对unlabeled类型的filesystem进行mount的操作
allow init unlabeled:filesystem mount;

# 允许init类型对fotad类型的unix_stream_socket 进行bind和create的操作
allow init fotad:unix_stream_socket { bind create };

# appdomain是定义在te_macros里面的一个宏，很多的app规则会使用类似app_domain(shell)的命令将其添加进去
# 允许app去对anr_data_file类型的目录进行查找的操作
allow appdomain anr_data_file:dir search;
# 允许app对anr_data_file类型的file进行打开和添加操作
allow appdomain anr_data_file:file { open append };

#绝不允许app(除了有unconfineddomain属性的app)对kmem_device类型的字符设备进行读写的操作
neverallow { appdomain -unconfineddomain } kmem_device:chr_file { read write };

# 绝不允许除了unconfineddomain以外的app对self类型的capability2进行任何的操作
neverallow { appdomain -unconfineddomain } self:capability2 *;

# 声明一个httpd_user_content_t的类型，具有file_type和httpdcontent的属性
type httpd_user_content_t, file_type, httpdcontent;

# 声明一个httpd_user_content_t的类型
type httpd_user_content_t;
# 定义httpd_user_content_t具有file_type, httpdcontent的属性
typeattribute httpd_user_content_t file_type, httpdcontent;

# 允许所有具有app属性的内容可以去对self属性的rawip_socket进行create的操作
allow appdomain self:rawip_socket create_socket_perms;

# 允许user_t和domain属性的类对bin_t, file_type, sbin_t类型的file进行可执行的操作
allow {user_t domain} {bin_t file_type sbin_t}:file execute ;

# 这两条语句的表述其实是一致的，其实self指的是目标的类型和发起人的类型是一致的
allow user_t user_t:process signal;
allow user_t self:process signal;

# 允许user_t对bin_t类型的file进行除了write setattr ioctl相关的操作
allow user_t bin_t:file ~{ write setattr ioctl };

```

## 3.8 常见attribute和type

TE强制访问方式是SEAndroid中的最主要的安全手段，所有关于TE的强制访问规则都被定义在了后缀为te的文件中，在te文件中基本能总结为完成如下操作：

- 对type类型的定义和将type归到相应的attribute中

```
SEAndroid在te文件中定义了安全策略中最基本的参量type，同时将具有共性的type归在一起构成一个称为attribute的集合，policy的规则执行也能以attribute作为执行对象。
```

SEAndroid为所有type共定义了17个attribute：
dev_type:

```
这一attribute包含了所有关于设备的type。
```

domain:

```
这一attribute包含了如下所列的所有关于进程的type，通常策略中的访问主体也就是进程所在的domain都包含在了这一attribute中。
adbd
trusted_app
browser_app
untrusted_app
bluetoothd
dbusd
debuggerd
drmserver
gpsd
init
installd
kernel
keystore
mediaserver
netd
nfc
qemud
radio
rild
servicemanage
shell
surfaceflinger
su
system_app
system
ueventd
vold
wpa
zygote
```

fs_type:

```
这一attribute包含了所有与文件系统相关的type。如下所列，大多是虚拟文件系统。
device
labeledfs
pipefs
sockfs
rootfs
proc
selinuxfs
cgroup
sysfs
sysfs_writable
inotify
devpts
tmpfs
shm
mqueue
sdcard
debugfs
```

file_type:

```
这一attribute包含了所有存在于非伪文件系统的相关文件的type，数量过多不再列举。
```

exec_type:

```
这一attribute包含了所有关于domian接入点的type，多被用在domain transition中，如下所列。
bluetoothd_exec
dbusd_exec
debuggerd_exec
drmserver_exec
gpsd_exec
installd_exec
keystore_exec
mediaserver_exec
netd_exec
qemud_exec
rild_exec
servicemanager_exec
surfaceflinger_exec
vold_exec
wpa_exec
zygote_exec
```

data_file_type:

```
这一attribute包含了所有在/data目录下的文件type，如下所列。
system_data_file
anr_data_file
tombstone_data_file
apk_data_file
dalvikcache_data_file
shell_data_file
gps_data_file
bluetoothd_data_file
bluetooth_data_file
keystore_data_file
vpn_data_file
systemkeys_data_file
wifi_data_file
radio_data_file
nfc_data_file
app_data_file
```

sysfs_type:

```
这一attribute包含了在sysfs文件系统下的所有文件的type，在SEAndroid中只有sysfs_writable包含在这个attribute中。
```

node_type:

```
这一attribute包含了所有与nodes/hosts有关的type，在SEAndroid中只有node包含在这个attribute中。
```

netif_type:

```
这一attribute包含了所有与网络接口相关的type，在SEAndroid中只有netif包含在这个attribute中。
```

port_type:

```
这一attribute包含了所有与网络端口相关的type，在SEAndroid中只有port包含在这个attribute中。
```

mlstrustedsubject:

```
这一attribute包含了所有能越过MLS检查的主体domain。
```

mlstrustedobject:

```
这一attribute包含了所有能越过MLS检查的客体type。
```

unconfineddomain:

```
这一attribute包含了所有拥有无限权限的type。
```

appdomain:

```
这一attribute包含了所有与app相关的type，如下所列。
trusted_app
browser_app
untrusted_app
nfc
radio
shell
system_app
```

netdomain:

```
这一attribute包含了所有与需要访问网络的app相关的type，如下所列。
trusted_app
browser_app
gpsd
mediaserver
radio
rild
system
```

bluetoothdomain:

```
这一attribute包含了所有与需要访问bluetooth的app相关的type，如下所列。
trusted_app
radio
system
```

binderservicedomain:

```
这一attribute包含了所有与binder服务相关的type，如下所列。
mediaserver
surfaceflinger
system
```



- 通过allow语句制定主体客体强制访问规则（白名单规则，不再规则中的都默认为非法操作）
- 通过type_transition语句制定tpye类型转换规则
- 通过dontaudit语句声明对一些被安全策略拒绝的访问不再进行审核。

```
审核是对于发生了访问违规或出现了被系统安全规则拒绝的行为进行日志记录的过程，审核可以帮助系统管理员发现bug和可能的入侵尝试。
默认情况下，SEAndroid会记录被拒绝的访问检查，但策略语言dontaudit允许我们取消这些默认的预料之中的拒绝审核消息。
```


SEAndroid为系统定义了33个te策略文件，这33个策略文件是：
adbd.te、file.te、su.te、app.te、gpsd.te、netd.te、system.te、bluetoothd.te、init.te、net.te、ueventd.te、bluetooth.te、installd.te、nfc.te、unconfined.te、cts.te、kernel.te、qemud.te、vold.te、dbusd.te、keystore.te、radio.te、wpa_supplicant.te、debuggerd.te、mediaserver.te、rild.te、zygote.te、device.te、servicemanager.te、domain.te、shell.te、drmserver.te、surfaceflinger.te。

对上述33个文件根据其策略规则针对的对象可分为三类：

- **针对attribute的策略制定：**

attribute是多个具有共性的type的集合，以下六个文件主要是直接针对attribute制定的策略，这种针对attribute制定的策略也就是同时对多个type制定策略一样。
unconfined.te

```
主要是为unconfineddomain属性制定策略，这些策略基本就是对各种访问客体拥有所有的权限。
```

domain.te

```
主要是为domain属性制定策略，为所有归在其中的访问主体制定一些公共的策略。
```

CTS.te

```
主要是为appdomain制定策略，这些策略一般是在对app进行CTS测试时用到。
```

bluetooth.te

```
主要是为bluetoothdomain制定策略。
```

net.te

```
主要是为netdomain制定策略，这些策略主要是关于对sockets、ports的访问以及与netd的通信。
```

file.te

```
这个文件主要定义了各文件系统的type，各文件的type，socket的type，以及制定了在不同文件系统中创建文件的规则。
```





- **针对daemon domain的策略制定:**

adbd.te、gpsd.te、netd.te、bluetoothd.te、zygote.te、ueventd.te、installd.te、vold.te、dbusd.te、keystore.te、debuggerd.te、mediaserver.te、rild.te、drmserver.te、surfaceflinger.te、qemud.te、servicemanager.te、su.te、shell.te、wpa_supplicant.te
这些文件都是为系统中的daemon进程进行策略的制定，它们都有着相应的daemon domain。



- **针对系统其他模块的策略制定:**

最后的7个文件分别对系统的其他模块进行策略制定。
app.te

```
在这一文件里将安装在系统上的第三方app分类为受信任的app和不受信任的app，分别用不同的type表示，
再分别为这两种app在访问网络，bluetooth，sdcard，数据，缓存，binder等等名感位置时设置相应权限。
```

system.te

```
这一文件主要针对的是系统app和system server进程。对系统app访问binder、system data files、dalvikcatch、keystone等进行权限控制，
对system server访问网络、bluetooth、netlink、app、binder、device、data files、socket、cache files等进行权限控制。
```

init.te

```
在这一文件中声明了init拥有无限权限。
```

nfc.te

```
在这一文件中制定了nfc domain对nfc设备和相关数据文件的访问权限。
```

kernel.te

```
在这一文件中声明了kernel拥有无限权限。
```

radio.te

```
在这一文件中制定了radio domain对init、rild和相关数据文件的访问权限。
```

device.te

```
在这一文件中定义了所有跟设备相关的type，并将这些type都归到了dev_type属性中。
```

## 3.9 生成规则文件的方法

下面介绍一下最简单的安全策略（se-policy）添加方法，大家碰到SELinux导致的访问禁止问题，可以参考用这种方法确认和解决。

1.安装pc上的工具，用于自动生成安全策略

```
$ sudo apt-get install policycoreutils
```

2.刷`userdebug`/`eng`软件，先将`SELinux`设置成`Permissive`模式，只输出警告不阻止操作
使用getenforce命令查看当前模式：

```
$ adb shell getenforce
Enforcing
```

在Enforcing模式下，除安全策略允许外的操作都会被阻止；使用setenforce命令更改当前模式（root权限需要）：

```
$ adb root
restarting adbd as root

$ adb shell setenforce 0

$ adb shell getenforce
Permissive
```

开发如果碰到怀疑是SELinux 可以通过这种方法关闭SELiunx( `setenforce 0`)，以确认是不是SELinux引起的

3.按照流程完成整个操作，抓取log，过滤出警告信息
如果log较多，可以先用grep工具过滤一下：

```
$ grep "avc: *denied" log.txt > denied.txt
$ cat denied.txt
<14>[  389.521062] avc:  denied  { set } for property=audio.ftm.rcv_reverse scontext=u:r:system_app:s0 tcontext=u:object_r:default_prop:s0 tclass=property_servic
```

4.使用pc工具`audit2allow`生成安全策略
命令`audit2allow`用来一次性生成所有安全策略，输入为前面抓取的 log (denied.txt)

```
$ audit2allow -i denied.txt
#============= system_app ==============
allow system_app default_prop:property_servic set;
```

<font color=#FF0000 size=4 >注意</font>

通常情况下，`audit2allow` 给出的声明建议只是一个大致的基础。在添加这些声明后，您可能需要更改来源域和目标标签，并纳入适当的宏，才能实现良好的政策配置。有时，应对拒绝事件的合理方式不是更改政策，而是更改违规的应用。



# 4 关于MLS(Multi-Level Security)

## 4.1 什么是MLS，为何要引入MLS

MLS称为多级别安全是另一种强制访问控制方法，特别适合于政府机密数据的访问控制，早期对计算机安全的研究大多数都是以在操作系统内实现MLS访问控制为驱动的。所有MLS的使用都是建立在TE安全的基础之上。在SELinux中MLS是一个可选访问控制方式，而在SEAndroid中则是被作为安全访问方式的其中之一。

## 4.2 MLS中的相关参量 

在SEAndroid中mls的相关参量就是安全上下文的第四列称为security level，在安全上下文第四列中可以有一个或者两个security level，第一个表示低安全级别，第二个表示高安全级别。

每个security level由两个字段组成：

- **sensitivity**

sensitivity有着严格的分级，它反应了一个有序的数据灵敏度模型，如政府分类控制中的绝密，机密和无密级。

- **category**

category是无序的，它反应的是数据划分的需要。



基本思路是对于要访问的数据你同时需要足够的sensivity和正确的category。



在SEAndroid中sensitivity只有一个级别即s0，category共有1024个，因此最低安全级别就是s0，最高安全级别就是s0:c0.c1023。

security level之间的三种运算关系：

- **dom**

需要主体sensitiviety大于客体，同时客体的category是主体的一个子集。

- **domby**

与dom完全相反

- **eq**

主体客体的sensitivity和category分别相同。



高的security level对低的security level拥有dom，低的security level对高的security level关系为domby（与dom相反），同级的security关系是eq，这三种关系运算符是SEAndroid中特有的。

## 4.3 MLS对进程的约束

- 限制进程的domain转换

对于从一个domain转换到另一个domain的操作要求两个domain的高级别security level和低级别security level同时相等才能许可转换，除非是待转换的domain属于对mls无限权限的type。

- 限制进程读操作

只有当主体domain的低级别security level对客体domain的低级别security level具有dom关系时，或者主体domian是属于对mls无限权限的type，主体才能对客体具有读操作的许可。

这一读操作具体是指：

1. 能获取进程优先权
2. 能获取另一进程的session id
3. 能获取到进程的group id
4. 能获取到系统的capabilities
5. 能获取文件的属性信息
6. 能追踪父程序或子程序的执行
7. 允许通过clone或fork进程实现状态信息共享

总结一下就是MLS限制了低级别进程向高级别进程进行读的操作，即不能上读。

- 限制进程写操作

只有当主体domain的低级别security level对客体domain的低级别security level具有domby关系时，或者主体domain是属于对mls无限权限的type，主体才能对客体具有写操作的许可。

写操作具体是指：

1. 能发送SIGKILL信号
2. 能发送SIGSTOP信号
3. 能发送一个非SIGKILL、SIGSTOP、SIGCHLD的信号
4. 能设置进程优先级
5. 能设置进程group id
6. 能设置系统的capabilities
7. 能改变进程hard limits
8. 能追踪父程序或子程序的执行
9. 允许通过clone或fork进程实现状态信息共享

总结一下就是MLS限制了高级别进程对低级别进程写的操作，即不能下写。

## 4.4 MLS对socket的约束

- 进程对local socket的访问限制

只有当主体进程的domain的高级别security level和低级别security level分别与客体local socket的type的security level相同时即满足eq关系时，或者主体客体任何一个具有对mls无限权限的type时，主体进程才对local socket拥有了某些访问权限。

这些访问权限是指：

1. 读操作
2. 写操作
3. 新建操作
4. 能获取对象属性信息
5. 能设置对象的属性信息
6. 能对对象重新标记安全上下文
7. 能进行bind操作
8. 能发起一个连接请求
9. 能监听连接事件
10. 能接受一个连接请求
11. 能获取到socket options
12. 能关闭socket连接

- 对socket的datagram发送的限制

只有当发送方的低级别security level与接受方的低级别security level满足domby关系时，或者主体客体任何一个具有对mls无限权限的type时，发送方才对接受方拥有了发送权限。

- 对客户端socket和服务端socket建立连接的限制

只有当客户端的低级别security level与服务端的低级别security level满足eq关系时，或者主体客体任何一个具有对mls无限权限的type时，客户端就能获得连接服务端的权限。

## 4.5 MLS对文件和目录的约束

- 对文件的创建和重新标记的限制

对文件操作时，要求客体的文件安全上下文只有一个security level即没有低级别和高级别security level或者说是这两个级别相同。 当主体domain的低级别security level对客体文件的低级别security level相同时，或者主体具有对mls有无限权限的type时，主体对客体文件拥有创建、和重新标记安全上下文的权限。

- 对目录的读操作的限制

只有当主体的低级别security level对客体目录的低级别security level满足dom关系时，或者主体客体任何一个具有对mls无限权限的type时，主体能对目录拥有如下权限：

1. 能读目录
2. 能获得目录的属性信息
3. 能获得某个正在被访问文件的所有上层目录访问权（search权限）

总结一下就是对目录的访问不能上读。

- 对文件的读操作的限制

只有当主体的低级别security level对客体文件的低级别security level满足dom关系时，或者主体客体任何一个具有对mls无限权限的type时，主体能对文件拥有如下权限：

1. 能读文件
2. 能获得文件的属性信息
3. 能执行该文件

总结一下就是对文件的访问不能上读。

- 对目录的写操作的限制

只有当主体的低级别security level对客体目录的低级别security level满足domby关系时，或者主体客体任何一个具有对mls无限权限的type时，主体能对目录拥有如下权限：

1. 能对目录写操作
2. 能设置属性信息
3. 能重命名目录
4. 能添加一个文件到目录中
5. 能从目录中删除一个文件
6. 能改变父目录
7. 能删除一个空目录

总结一下就是对目录访问不能下写。

- 对文件的写操作的限制

只有当主体的低级别security level对客体文件的低级别security level满足domby关系时，或者主体客体任何一个具有对mls无限权限的type时，主体能对文件拥有如下权限：

1. 能对文件进行写操作
2. 能设置文件属性信息
3. 能对文件内容作append操作
4. 能对文件创建链接
5. 能删除一个文件的链接
6. 能对文件重命名

总结一下就是对文件访问不能下写。

## 4.6 MLS对IPC的约束

- 对IPC创建和销毁的限制

要求客体的IPC对象只有一个security level。

只有当主体的低级别security level与客体的低级别security level满足eq关系时，或者主体具有对mls无限权限的type时，主体能对客体IPC拥有创建和销毁的权限。

- 对IPC读操作的限制

只有当主体的低级别security level对客体IPC的低级别security level满足dom关系时，或者主体具有对mls无限权限的type时，主体能对客体IPC拥有如下权限：

1. 获取文件属性信息
2. 能对IPC文件执行读操作
3. 能关联一个key
4. 能执行由IPC操作要求的读操作

总结一下就是对IPC访问不能上读。

- 对IPC写操作的限制

只有当主体的低级别security level对客体IPC的低级别security level满足domby关系时，或者主体具有对mls无限权限的type时，主体能对客体IPC拥有如下权限：

1. 能对文件执行write和append操作
2. 能执行由IPC操作要求的write和append操作

总结一下就是对IPC访问不能下写。

## 4.7 SEAndroid基于MLS的配置

SEAndroid基于MLS的配置，主要是通过mlsconstrain在基于类型的访问控制之外，再对class进行额外的检查。
mlsconstrain语法如下：

~~~shell
mlsconstrain class perm_set expression
~~~

只有满足后面的expression，才能对class进行perm_set里的操作，否则，即使在TE策略中有针对该class的allow策略，也无法成功地访问。



# 5 TE文件中的一些宏

 .te 文件定义中的一些宏

## 5.1 unix_socket_connect(1,1,2, $3 )
这个其实是一个宏。它定义在 te_macros（android系统，mtk 和 qcom 下面都有） 的文件里面的：

```markdown
     #####################################  android 系统 te_macros 文件中的定义
 # unix_socket_connect(clientdomain, socket, serverdomain)
 # Allow a local socket connection from clientdomain via
 # socket to serverdomain.
 #
 # Note: If you see denial records that distill to the
 # following allow rules:
 # allow clientdomain property_socket:sock_file write;
 # allow clientdomain init:unix_stream_socket connectto;
 # allow clientdomain something_prop:property_service set;
 #
 # This sequence is indicative of attempting to set a property.
 # use set_prop(sourcedomain, targetproperty)
 #
 define(`unix_socket_connect', `
 allow $1 $2_socket:sock_file write;
 allow $1 $3:unix_stream_socket connectto;
')

#####################################  平台下 te_macros 的定义，（各有不同）
# qmux_socket(clientdomain)
# Allow client domain to connecto and send
# via a local socket to the qmux domain.
# Also allow the client domain to remove
# its own socket.
define(`qmux_socket', `
allow $1 qmuxd_socket:dir create_dir_perms;
unix_socket_connect($1, qmuxd, qmuxd)
allow $1 qmuxd_socket:sock_file { read getattr write setattr create unlink };
')

#####################################
# netmgr_socket(clientdomain)
# Allow client domain to connecto and send
# via a local socket to the netmgrd domain.
# Also allow the client domain to remove
# its own socket.
define(`netmgr_socket', `
allow $1 netmgrd_socket:dir r_dir_perms;
unix_socket_connect($1, netmgrd, netmgrd)
allow $1 netmgrd_socket:sock_file { read getattr write };
')
```




## 5.2 init_daemon_domain($1)

~~~markdown
#####################################  android 系统 te_macros 文件中的定义
# init_daemon_domain(domain)
# Set up a transition from init to the daemon domain
# upon executing its binary.
define(`init_daemon_domain', `
domain_auto_trans(init, $1_exec, $1)
tmpfs_domain($1)
')
~~~

## 5.3 appdomain app_domain($1)

~~~markdown
#####################################android 系统 te_macros 文件中的定义
# app_domain(domain)
# Allow a base set of permissions required for all apps.
define(`app_domain', `
typeattribute $1 appdomain;
# Label ashmem objects with our own unique type.
tmpfs_domain($1)
# Map with PROT_EXEC.
allow $1 $1_tmpfs:file execute;
')
~~~

