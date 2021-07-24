# 针对特定作者/文件/文件夹的git format-patch

针对特定作者

~~~shell
git log X..Y --author='<AUTHOR>' --format="%H" | sed 's/$/^!/g' | xargs -I{} git format-patch {}
~~~


`git log X…Y –author =’< AUTHOR>‘ –format =“％H”以commit id`的格式生成X到Y之间author为输出

`sed’s / $/ ^！/ g’`加^！在每一行的末尾

`xargs -I {} git format-patch {}`只需对每一行运行git format-patch

针对特定文件/文件夹

~~~shell
git log X..Y  --format=%H path/to/file | sed 's/$/^!/g' | xargs -I{} git format-patch {}
~~~

`path/to/file` 需要`format-patch`的文件或者文件夹









git log X..Y --author='<Cody.Su>' --format="%H" | sed 's/$/^!/g' | xargs -I{} git format-patch {}

