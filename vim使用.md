[toc]

# 1、vim常用命令

## 1.1、复制



**将第9行至第15行的数据，复制到第16行**

~~~markdown
1. 方法一

：9，15 copy 16 或 ：9，15 co 16

2. 方法二
光标移动到结束行，ma
光标移动到起始行,输入y'a
光标移动到需要复制的行，输入p,行前复制则输入大写P

3. 方法三
光标移动到起始行，输入ma
光标移动到结束行，输入mb
光标移动到粘贴行，输入mc
然后输入:'a,'b, co 'c  把co换成m就是剪切
若要删除多行，则输入：'a,'b de

4. 方法4
把光标移到第9行 shift + v
再把光标移动到第15行 ctrl + c
再把光标移动到第16行 p 

5. 方法5
把光标移到第9行 6yy
把光标移到第15行 p
nyy   //将当前行向下n行复制到缓冲区，也可以用 "anyy 复制，"a 为缓冲区，a也可以替换为a到z的任意字母，可以完成多个复制任务。
~~~



**Vim中如何全选并复制**

~~~markdown
1. 全部删除：按esc后，然后dG
2. 全部复制：按esc后，然后ggyG
3. 全选高亮显示：按esc后，然后ggvG或者ggVG
~~~



**单行复制**

```cpp
yy    //将当前行复制到缓存区，也可以用 "ayy 复制，"a 为缓冲区，a也可以替换为a到z的任意字母，可以完成多个复制任务。

yw    //复制从光标开始到词尾的字符。
nyw   //复制从光标开始的n个单词。
y^      //复制从光标到行首的内容。 
y$      //复制从光标到行尾的内容。
p        //粘贴剪切板里的内容在光标后，如果使用了前面的自定义缓冲区，建议使用"ap 进行粘贴。
P        //粘贴剪切板里的内容在光标前，如果使用了前面的自定义缓冲区，建议使用"aP 进行粘贴。
```

## 1.2、剪切

：9，15 move 16 或 :9,15 m 16 将第9行到第15行的文本内容到第16行的后面 

## 1.3、翻页和跳转

~~~markdown
1. 翻页
PageDown(或Ctrl+F):下翻一屏
PageUp(或Ctrl+B):上翻一屏

2. 跳转到指定行
num G:跳转到指定行
:num + Enter移动到第num行
num gg跳转到指定行
G:移动到缓冲区的最后一行
gg:移动到缓冲区的第一行
:$ 跳转到最后一行
:1 跳转到第一行

3. 跳值行首
home建
shit+6

4. 调治行尾
end
shit+4

~~~





vi设置自动缩进：set smartindent
vi设置显示行号：set number 或 set nu

## 1.4、插入文本或行

```markdown
- vi命令模式下使用，执行下面命令后将进入插入模式，按ESC键可退出插入模式
    
a      //在当前光标位置的右边添加文本
i      //在当前光标位置的左边添加文本
A      //在当前行的末尾位置添加文本
I      //在当前行的开始处添加文本(非空字符的行首)
O      //在当前行的上面新建一行
o      //在当前行的下面新建一行
R      //替换(覆盖)当前光标位置及后面的若干文本
J      //合并光标所在行及下一行为一行(依然在命令模式)
```

## 1.5、代码对齐

~~~markdown
1. 单行代码对齐
按ESC进入命令行模式；
按==即可对齐单行代码。

2. 代码块对齐
按ESC进入命令行模式；
ctrl+v选中块；
按j选择下一行，按k选择上一行;
按=即可对齐选中代码。

3. 全部对齐
按ESC进入命令行模式；
输入gg=G即可对齐。

4. 总结
gg的意思为将光标移到文件开始位置；
G的意思为将光标移到文件结束位置；
=为代码对齐。
~~~

## 1.6、替换

~~~markdown
1. 将当前行第一个a替换为b
:s/a/b/
 
2. 将当前行的所有a替换为b
:s/a/b/g

3. 将每行第一个a替换为b
:%s/a/b

4. 将整个文件的所有a替换为b
:%s/a/b/g

5. 将1至3行的第一个a替换为b
:1,3s/a/b/

6. 将1至3行的所有a替换为b
:1,3s/a/b/g

~~~

## 1.7、删除

~~~markdown
1. 多行删除
命令输入“：32,65d”,回车键，32-65行就被删除了
~~~

## 1.8、鼠标功能

~~~mysql
打开鼠标功能
:set mouse=a

关闭鼠标功能
:set mouse-=a


在~/.vimrc中加入 set mouse=a 后，vim鼠标右键变得不能复制了，解决办法如下：

按住 shift 键，然后选择，此时表示由 X 处理该选择，copy 选项就 enable 了。如果放掉shift键，则由 vim处理该选择
~~~

## 1.9、粘贴模式

~~~markdown
不知道大家是否会有这种困扰，例如在Android Studio有一段缩进优美的代码实现，例如：

public void sayHello() {
    String msg = "Hello Vim Paste Mode";
    System.out.println(msg);
}

当你把这段缩进优美的代码直接ctrl+c，ctrl+v到Vim的时候，会导致代码丢失和缩进错乱等情况。

解决方案
vim进入paste模式，命令如下：

:set paste
1
进入paste模式之后，再按i进入插入模式，进行复制、粘贴就很正常了。


命令模式下，输入

:set nopaste
1
解除paste模式。

paste模式主要帮我们做了如下事情：

textwidth设置为0
wrapmargin设置为0
set noai
set nosi
softtabstop设置为0
revins重置
ruler重置
showmatch重置
formatoptions使用空值
~~~

## 1.10、vim窗口命令



```
分 割 窗 口

":tag" 命令会将当前窗口的文件替换为包含新函数的文件。怎样才能同时查看两个文件
呢？你可以使用 ":split" 命令将窗口分开然后再用 ":tag" 命令。Vim 有个缩写命令可
以做到这些：

        :stag tagname

使用下面的命令可以分割当前窗口并跳转到光标下的标签:

        CTRL-W ]

如果指定了计数参数，新窗口将包含指定的那么多行。

Ctrl+w 切换窗口


:qall -- 关闭所有窗口，退出vim。
:wall -- 保存所有修改过的窗口。
:only -- 只保留当前窗口，关闭其它窗口。(CTRL-W o)
:close -- 关闭当前窗口，CTRL-W c能实现同样的功能。 (象 :q :x同样工作 )


1、打开多个窗口
打开多个窗口的命令以下几个：
横向切割窗口
:new+窗口名(保存后就是文件名)
:split+窗口名，也可以简写为:sp+窗口名
纵向切割窗口名
:vsplit+窗口名，也可以简写为：vsp+窗口名
2、关闭多窗口
可以用：q!，也可以使用：close，最后一个窗口不能使用close关闭。使用close只是暂时关闭窗口，其内容还在缓存中，只有使用q!、w!或x才能真能退出。
:tabc 关闭当前窗口
:tabo 关闭所有窗口

3、窗口切换

ctrl + w + j

按键的按法是：先按下 ctrl键 不放， 再按下 w 后放开所有的按键，然后再按下 j ，则光标可移动到下方的窗口。

ctrl + w + k  同上，只不过 光标是移动到上方的窗口。
ctrl + w + h   同上，只不过光标是移动到左边的窗口。
ctrl + w + l   同上，只不过光标是移动到右边的窗口。
可用箭头按键代替
4、窗口大小调整
纵向调整
:ctrl+w + 纵向扩大（行数增加）
:ctrl+w - 纵向缩小 （行数减少）
:res(ize) num  例如：:res 5，显示行数调整为5行
:res(ize)+num 把当前窗口高度增加num行
:res(ize)-num 把当前窗口高度减少num行
横向调整
:vertical res(ize) num 指定当前窗口为num列
:vertical res(ize)+num 把当前窗口增加num列
:vertical res(ize)-num 把当前窗口减少num列
5、给窗口重命名
:f file
6、vi打开多文件
vi a b c
:n 跳至下一个文件，也可以直接指定要跳的文件，如:n c，可以直接跳到c文件
:e# 回到刚才编辑的文件
7、文件浏览
:Ex 开启目录浏览器，可以浏览当前目录下的所有文件，并可以选择
:Sex 水平分割当前窗口，并在一个窗口中开启目录浏览器
:ls 显示当前buffer情况
8、vi与shell切换
:shell 可以在不关闭vi的情况下切换到shell命令行
:exit 从shell回到vi
```

# 2、ctags使用

1. 下载ctags **sudo apt-get install ctags**

2. 生成ctags 文件：ctags -R

3. 设置索引文件在.vimrc中添加set tags=tags;/
   如果不设置索引文件位置，然后执行 ctrl+] 则会出现错误：
   E433: 没有 tag 文件
   E426: 找不到 tag: XXXXX

Ctrl+]  奔赴tag标签

Ctrl+T 回到原处

当然也可以选择源码包方式进行安装，[https://sourceforge.net/projects/ctags/files/](https://link.zhihu.com/?target=https%3A//sourceforge.net/projects/ctags/files/)，解压缩之后，在源代码目录中依次执行下述命令即可

```bash
$ ./configure
$ make 
$ make install
```



ctags跳转错误

用 `:ts TAGNAME` 列出列表 然后再选择跳转。

或者

1. 使用 `:ts` 命令
2. 在 .vimrc 中添加以下配置：`map <c-]> g<c-]>`



为ctags生成系统tags

如上之后，你会发现。ctags只支持源文件里定义的宏。变量和函数，可是我们调用的基本函数和系统函数都没办法实现跳转。
使用以下的命令生成系统头文件tags

```bash
ctags -I __THROW --file-scope=yes --langmap=c:+.h --languages=c,c++ --links=yes --c-kinds=+p --fields=+S  -R -f ~/.vim/systags /usr/include /usr/local/include
```

最后，设置你的~/.vimrc，加入一行：

```
set tags+=~/.vim/systags
```

就能够享受系统库函数跳转等功能了。

# 3、taglist

『下载和安装』

​     1）从http://www.vim.org/scripts/script.php?script_id=273下载安装包，也可以从http://vim-taglist.sourceforge.net/index.html下载。

​    2）进入~/.vim目录，将Taglist安装包解压，解压后会在~/.vim目录中生成几个新子目录，如plugin和doc（安装其它插件时，可能还会新建autoload等其它目录）。

​    3）进入~/.vim/doc目录，在Vim下运行"helptags ."命令。此步骤是将doc下的帮助文档加入到Vim的帮助主题中，这样我们就可以通过在Vim中运行“help taglist.txt”查看taglist帮助。

​    4）打开配置文件~/.vimrc，加入以下几行：

~~~shell
let Tlist_Show_One_File=1   "不同时显示多个文件的tag，只显示当前文件的  
let Tlist_Exit_OnlyWindow=1  "如果taglist窗口是最后一个窗口，则退出vim  
let Tlist_Ctags_Cmd="/usr/bin/ctags" "将taglist与ctags关联 
let Tlist_WinWidth=40    "设置taglist宽度
let Tlist_WinHeight=50设置 "taglist窗口高度为50"
let Tlist_Use_Right_Window=1 "在Vim窗口右侧显示taglist窗口
~~~

<font color = "red">在Vim命令行下运行":Tlist"就可以打开Taglist窗口，再次运行":Tlist"则关闭。</font>

# 4、NERDTree

nerdtree可以显示当前项目的文件结构。安装方法如下。
执行以下命令即可：
1、创建文件夹：mkdir ~/.vim，如果这个文件夹已存在就不用执行这一步了。
2、进入文件夹：cd ~/.vim
3、下载nerdtree压缩包：wget http://www.vim.org/scripts/download_script.php?src_id=17123 -O nerdtree.zip
4、unzip nerdtree.zip

安装好后，打开vim，输入”: NERDTree”即可打开NERDTree。: NERDTreeToggle关闭NERDTree

| 功能                     | 快捷键        | 解释                                                         |
| ------------------------ | ------------- | ------------------------------------------------------------ |
| 新建文件                 | ma            | 在要创建文件的目录中按命令 ma然后键入你要创建的文件名称即可。 |
| 删除文件                 | md            | 在要删除的文件上按命令md然后输入y回车即可。                  |
| 移动文件/修改文件名      | mm            | 在要修改的文件上按命令mm然后输入对应的目录和名称回车即可。   |
| 设置当前目录为项目根目录 | C             | 在要设置为根目录的目录上按命令C【大写】即可。                |
| 查看当前文件所在目录     | :NERDTreeFind | 执行命令 :NERDTreeFind 或则在.vimrc中添加 map <leader>v :NERDTreeFind<CR> 全局使用 <leader>v命令(我的是,v)直接显示当前文件所在目录。 |

# 5、代码补全(YouCompleteMe)

1 下载vundle
默认下载到~/.vim/bundle/vundle目录下

git clone https://github.com/gmarik/vundle.git ~/.vim/bundle/vundle

2 配置
在.vimrc 中添加bundle的配置
注意，.vimrc是自己在home目录下创建，可以在里面对vim进行基本配置。
对于bundle的配置，将下面代码全部复制即可。

~~~makefile
set nocompatible                " be iMproved
filetype off                    " required!
set rtp+=~/.vim/bundle/vundle/
call vundle#rc()

" let Vundle manage Vundle
Bundle 'gmarik/vundle'

"my Bundle here:
"
" original repos on github
Bundle 'kien/ctrlp.vim'
Bundle 'sukima/xmledit'
Bundle 'sjl/gundo.vim'
Bundle 'jiangmiao/auto-pairs'
Bundle 'klen/python-mode'
Bundle 'Valloric/ListToggle'
Bundle 'SirVer/ultisnips'
Bundle 'Valloric/YouCompleteMe'
Bundle 'scrooloose/syntastic'
Bundle 't9md/vim-quickhl'
" Bundle 'Lokaltog/vim-powerline'
Bundle 'scrooloose/nerdcommenter'
"..................................
" vim-scripts repos
Bundle 'YankRing.vim'
Bundle 'vcscommand.vim'
Bundle 'ShowPairs'
Bundle 'SudoEdit.vim'
Bundle 'EasyGrep'
Bundle 'VOoM'
Bundle 'VimIM'
"..................................
" non github repos
" Bundle 'git://git.wincent.com/command-t.git'
"......................................
filetype plugin indent on

~~~

3 安装插件
在命令行输入下面命令开始安装所有插件

BundleInstall

完成之后进入vim 在命令模式下BundleList可以查看当前安装的插件

其他常用命令：

- 更新插件:BundleUpdate
- 清除不再使用的插件:BundleClean,
- 列出所有插件:BundleList
- 查找插件:BundleSearch

4 vim/bundle/YouCompleteMe下执行./install.py



## 5.1、遇到的问题

vim升级到8.2后 打开文件报错

处理 /home/she/.vimrc 时发生错误:
行   76:
E185: Cannot find color scheme 'desert'
行   77:
E484: 无法打开文件 /usr/share/vim/vim80/syntax/syntax.vim

但是也能打开vim，进去之后没有高亮提示：

将vim82/ 拷贝一份，重命名成vim80/，在运行就行了(原因不详)。

# 6、显示git信息

git 信息直接在 NERDTree 中显示出来，修改的文件和增加的文件都给出相应的标注， 这时需要安装的插件就是 [nerdtree-git-plugin](https://github.com/Xuyuanp/nerdtree-git-plugin)