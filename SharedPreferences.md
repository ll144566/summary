```java

//一：通过Activity 获取SharedPreferences对象

//此方法会在/data/data/包名/shared_prefs文件夹下创建一个与该activity类名一样的xml文件，该方法生成的xml文件只能在该activity中调用操作，无法被其他组件使用，除非你直接通过第一种方法的文件名来获取（不提倡）。
SharedPreferences sp2 = getPreferences(Context.MODE_PRIVATE);
SharedPreferences.Editor  editor2 = sp2.edit();
editor2.putBoolean("boolean",false);
editor2.putString("String", "str");
editor2.commit();

//二：通过Context去获取SharedPreferences对象
//参数一：name，即将创建的xml文件的名称
//参数二：mode，操作模式，一般选择MODE_PRIVATE即可，其他的选择在不同的版本中已经被弃用，具体说明可以查看官方文档。
//此方法会在/data/data/包名/shared_prefs文件夹下创建一个name.xml文件。
SharedPreferences sp =  mContext.getSharedPreferences("文件名",Context.MODE_PRIVATE);
SharedPreferences.Editor  editor = sp.edit();
editor.putBoolean("boolean",false);
editor.putString("String", "str");
editor.commit();


//三：PreferenceManager

//此方法会在/data/data/包名/shared_prefs文件夹下创建一个默认的xml文件。
SharedPreferences sp3 =  PreferenceManager.getDefaultSharedPreferences(mContext);
SharedPreferences.Editor  editor3 = sp3.edit();
editor3.putBoolean("boolean",false);
editor3.putString("String", "str");
editor3.commit();
```
**三种方法的区别**

1. public SharedPreferences getPreferences (int mode)

   通过Activity对象获取，获取的是本Activity私有的Preference，保存在系统中的xml形式的文件的名称为这个Activity的名字，因此一个Activity只能有一个，属于这个Activity。

2. public SharedPreferences getSharedPreferences (String name, int mode)

   因为Activity继承了ContextWrapper，因此也是通过Activity对象获取，但是属于整个应用程序，可以有多个，以第一参数的name为文件名保存在系统中。

3. public static SharedPreferences getDefaultSharedPreferences (Context context)

   PreferenceManager的静态函数，保存PreferenceActivity中的设置，属于整个应用程序，但是只有一个，Android会根据包名和PreferenceActivity的布局文件来起一个名字保存。