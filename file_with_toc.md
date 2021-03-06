<a name="index">**Index**</a>
<a href="#0">1 常见注解</a>  
&emsp;<a href="#1">1.1 @Rule</a>  
&emsp;<a href="#2">1.2 @Before，@After，@BeforeClass，@AfterClass</a>  
&emsp;<a href="#3">1.3 @Test</a>  
&emsp;<a href="#4">1.4 @Ignore</a>  
<a href="#5">2 执行apk中的单元测试</a>  
# <a name="0">1 常见注解</a><a style="float:right;text-decoration:none;" href="#index">[Top]</a>

## <a name="1">1.1 @Rule</a><a style="float:right;text-decoration:none;" href="#index">[Top]</a>

被@Rule注解的属性需要实现TestRule接口，TestRule只有一个apply()方法，该方法返回一个Statement对象。.

在每次进行测试时会执行Statement的evaluate方法。

~~~java
public class LoopRule implements TestRule {
    @Override
    public Statement apply(Statement base, Description desc) {
        return new Statement() {
            @Override
            public void evaluate() throws Throwable {
                 base.evaluate();
            }
        };
    }
}
~~~



Junit有很多内置Rule，也可以自定义Rule，自定义时注意执行base.evaluate();否则测试方法不会执行

## <a name="2">1.2 @Before，@After，@BeforeClass，@AfterClass</a><a style="float:right;text-decoration:none;" href="#index">[Top]</a>

| @BeforeClass | @BeforeAll  | 在当前类的**所有测试方法**之前执行。注解在【静态方法】上。   |
| ------------ | ----------- | ------------------------------------------------------------ |
| @AfterClass  | @AfterAll   | 在当前类中的**所有测试方法**之后执行。注解在【静态方法】上。 |
| @Before      | @BeforeEach | 在**每个测试方法**之前执行。注解在【非静态方法】上。         |
| @After       | @AfterEach  | 在**每个测试方法**之后执行。注解在【非静态方法】上。         |

有点面向切面编程的感觉

## <a name="3">1.3 @Test</a><a style="float:right;text-decoration:none;" href="#index">[Top]</a>

常用于需要测试的方法，该注解可以有两个参数, expected和timeout。

@Test (expected = NullPointException.class)表示期望该方法抛出一个NullPointException异常，否则报错

@Test (timeOut = 1000)，限制方法执行时间为1秒

## <a name="4">1.4 @Ignore</a><a style="float:right;text-decoration:none;" href="#index">[Top]</a>

忽略当前测试

# <a name="5">2 执行apk中的单元测试</a><a style="float:right;text-decoration:none;" href="#index">[Top]</a>

~~~markdown
adb shell am instrument -w -e class com.google.android.media.gts.DrmSessionManagerTest#testReclaimSession com.google.android.media.gts /androidx.test.runner.AndroidJUnitRunner

com.google.android.media.gts.DrmSessionManagerTest是类的全限定名，

testReclaimSession是方法名（不写则执行当前类所有测试方法），

com.google.android.media.gts是包名
~~~

