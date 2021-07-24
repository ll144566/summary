## 1、常见状态机介绍

### 1.1、FSM

　　简单讲就是将行为分为一个一个的状态，状态与状态之间的过渡通过事件的触发来形成。比如士兵的行为有“巡逻”，“追击敌人”，“攻击敌人”，“逃跑”等行为，响应的事件就有“发现敌人”，“追到敌人”，“敌人逃跑”，“敌人死亡”，“自己血量不足”等。那么可以写成这样一个状态机：

　　1.士兵 “巡逻”，如果 “发现敌人”，那么，“追击敌人”

　　2.士兵 “追击敌人”， 如果 “追到敌人”， 那么，“攻击敌人”

　　3.士兵 “追击敌人”， 如果 “敌人死亡”， 那么，继续 “巡逻”

　　4.士兵 “攻击敌人”， 如果 “敌人死亡”， 那么，继续 “巡逻”

　　5.士兵 “攻击敌人”， 如果 “血量不足”， 那么，“逃跑”

　　其中，士兵就是这个FSM的执行者，红色的就是状态，蓝色的就是事件，整个状态机的行为可以总结为：当前状态=>是否满足条件1，如果是，则跳转到对应状态，否则=>是否满足条件2，如果是，则跳转到对应状态。

　　由此可看出，状态机是一种“事件触发型”行为，就是只有事件的触发才会发生引起状态的变化。

### 1.2、HSM

先看一下百度百科的说法：

​		“Hierarchical State Machine的缩写。层次状态机是状态机理论中的一种层次结构的模型，各个状态按照树状层次结构组织起来，状态图是层次结构的，也就是说每个状态可以拥有子状态。这个主意很简单，效果却异常强大。从人类思维的角度来看，平面状态模型无法进行扩展。当状态和转换的数量增长时，平面模型就会变得难于理解。而层次状态模型则可以分部分考察，每一部分理解起来相对就变得简单了。以层次结构组织状态行为是最直观的方法，也是实现事件驱动系统的一种很好的形式方法。主要用来描述对象、子系统、系统的生命周期。通过层次状态机可以了解到一个对象能到达的所有状态以及对象收到的事件对对象状态的影响等。状态机指定对象的行为以及不同状态行为的差异。同时，它还能说明事件是如何改变一个对象的状态,因此非常适用于软件开发。
层次状态机较之经典的状态机，最重要的改进就是引入了层次式状态。状态层次嵌套的主要特性来自抽象与层次的结合。这是一种降低复杂性的传统途径，也就是软件中的继承。在面向对象中，类继承概念描述了类和对象之间的关系。类继承描述在类中的is-a 关系。在嵌套状态中，只需用is-in状态关系代替is-a类关系，即它们是等同的分类法。状态嵌套允许子状态继承来自其超状态的状态行为，因此它被称为行为继承。”

　　简单来说，就是FSM当状态太多的时候，不好维护，于是将状态分类，抽离出来，将同类型的状态做为一个状态机，然后再做一个大的状态机，来维护这些子状态机。

　　举个决策小狗行为的例子：我们对小狗定义了有很多行为，比如跑，吃饭，睡觉，咆哮，撒娇，摇尾巴等等，如果每个行为都是一个状态，用常规状态机的话，我们就需要在这些状态间定义跳转，比如在“跑”的状态下，如果累了，那就跳转到“睡觉”状态，再如，在“撒娇”的状态下，如果感到有威胁，那就跳转到“咆哮”的状态等等，我们会考量每一个状态间的关系，定义所有的跳转链接，建立这样一个状态机。如果用层次化的状态机的话，我们就先会把这些行为“分类”，把几个小状态归并到一个状态里，然后再定义高层状态和高层状态中内部小状态的跳转链接。

　　其实层次化状态机从某种程度上，就是限制了状态机的跳转，而且状态内的状态是不需要关心外部状态的跳转的，这样也做到了无关状态间的隔离，比如对于小狗来说，我们可以把小狗的状态先定义为疲劳，开心，愤怒，然后这些状态里再定义小状态，比如在开心的状态中，有撒桥，摇尾巴等小状态，这样我们在外部只需要关心三个状态的跳转（疲劳，开心，愤怒），在每个状态的内部只需要关心自己的小状态的跳转就可以了。



## 2、StateMachine原理分析

StateMachine解释
一个状态是一个State对象，必须实现processMessage接口，可以选择性的实现enter,exit,getName接口，StateMachine里面的enter和exit相当与面向对象编程里面的构造函数和析构函数，分别用来初始化和清除State对象，getName方法返回状态的名字，接口默认是返回class的名字，返回值一般用来描述该状态的实例化对象名字，特别是有些特殊的状态有多个实例化对象的时候。

当一个StateMachine创建的时候，addState用来创建层级，setInitialState用来确认哪个状态是初始状态，构造完毕之后，用户调用start方法来初始化和启动StateMachine，StatMachine的第一个动作是：从初始状态最顶层的父状态开始逐层调用enter方法，enter会在StateMachine的Handler环境中被执行，而不是在call的环境开始，enter会在所有message被执行前被调用，例如，给出一个简单的StateMachine，mP1的enter会被先调用，然后才是mS1的enter，最后message会被发送到StateMachine的当前状态执行。
        mP1
       /       \
      mS2   mS1 ----&gt; initial state

当一个StateMachine被created和started之后，通过sendMessage向StateMachine发送message，message通过obtainMessage创建，当一个状态机收到message之后，当前状态的processMessage方法会被调用，在上面的例子里面，mS1的processMessage会被最先调用，可以通过transitionTo来把当前状态跳转到一个新的状态。

StateMachine里面的每个状态都有零个或一个父状态，如果子状态无法handle这个message，那么该message就会被父状态的processMessage执行，子状态返回false或者NOT_HANDLED，如果一个message永远无法执行，那么unhandledMessage会被调用，用来给message最后一次机会让StateMachine来执行。

当所有的进程完成，StateMachine会选择调用transitionToHaltingState，当current processingMessage返回时，StateMachine会跳转到内部的HaltingState和调用halting，任何后来的message都会触发haltedProcessMessage的调用。

如果StateMachine正常的退出，可以调用quit或者abort，调用quit会退出当前状态和他的父状态，调用onQuiting之后退出Thread和Loopers

不仅仅是processMessage，一般每个状态都会复写一个enter和一个exit接口

自从所有的状态都被层次的安排好了之后，跳转到一个新的状态会导致当前状态的exited和新状态的entered，决定列出当前状态和同一个父亲的兄弟状态的entered/exited，我们然后退出当前状态，父状态唤起，但是不包括同一个父状态的其他兄弟状态，然后层次遍历的进入从当前父状态到新状态的所有状态，如果新状态和当前状态不共父状态，那么当前状态和他的所有父状态都会退出，然后进入新状态。

另外两个可以用到的方法是deferMessage和sendMessageAtFrontOfQueue，sendMessageAtFrontOfQueue发送message，但是会把message放到队列的头部，而不是末尾，deferMessage会把message保存到一个list里面，直到跳转到新的状态，然后最先被defferd message会被放到StateMachine队列的头部，这些message会被当前状态最先执行，然后才是队列里面的其他后来的message，这两个方法是protecte，只能在StateMachine的内部调用

为了说明这些特性，用一个带有8个状态的StateMachine来举个例子
          mP0
         /        \
        mP1   mS0
       /        \
      mS2   mS1
     /        \        \
    mS3   mS4   mS5  ---&gt; initial state

当mS5被叫起来之后，当前活跃的状态依次是mP0,mP1,mS1和mS5，所以当mS5接收到一个message之后，假如所有的processMessage都没有handle这个message，调用processMessage的顺序一次是mS5,mS1,mP1,mP0

假如现在mS5的processMessage收到一个能handle的message，如果handle的结果是跳转到其他状态，可以通过call transitionTo(mS4)，返回true或者HANDLED，当processMessage返回后，StateMachine会找到他们的公共父状态，也就是mP1,然后会调用mS5的exit，mS1的exit，mS2的enter，mS4的enter，然后新的活跃状态表就是mP0,mP1,mS2,mS4，因此当下一个message收到后，mS4的enter会被调用。

## 3、StateMachine代码分析

### 3.1、StateMachine常用成员变量和内部类介绍

#### 3.1.1、method

1. start：启动状态机。
2. sendMessage：通过mSmHandler向状态机发送消息。
3. transitionTo：通过mSmHandler状态转换。
4. setInitialState：通过mSmHandler设置初始状态。
5. initStateMachine：状态机初始化，创建Handle对象。
6. addState：添加一个新新状态，可指定父状态。

#### 3.2.1、field

1. mSmHandler：主要用于处理状态机消息和状态切换。
2. mSmThread：用于创建一个子线程和获取loop对象，每一个状态的的消息最终都在这个子线程处理。

#### 3.1.2、内部类SmHandle

SmHandler 是 StateMachine 类的静态内部类，它继承自 Handler 类。它是整个 StateMachine 消息接收，分发的核心。

1. 内部类StateInfo：对State的进一步封装，包含了State，父状态和是否激活。
2. HaltingState和QuittingState：两个内置状态，暂停和退出。
3. mStateInfo：一个HashMap<State, StateInfo>类型的对象，包含了所有State。
4. mDestState：调用transitionTo时的目标状态。
5. mTempStateStack：临时状态堆栈数组，长度为状态树的高度。
6. mStateStack：状态堆栈数组，长度为状态树的高度。



### 3.2、StateMachine流程分析

#### 3.2.1、StateMachine构造方法

```java
protected StateMachine(String name) {
    // 创建 HandlerThread
    mSmThread = new HandlerThread(name);
    mSmThread.start();
    // 获取HandlerThread对应的Looper
    Looper looper = mSmThread.getLooper();
    // 初始化 StateMachine
    initStateMachine(name, looper);
}
```

- 创建并启动了一个线程`HandlerThread`；

- 获取HandlerThread线程的looper对象

  

```java
private void initStateMachine(String name, Looper looper) {
    mName = name;
    mSmHandler = new SmHandler(looper, this);
}
```

- `SmHandler`构造方法中，将SmHandler对象和loop绑定，并向状态机中添加了两个状态：一个状态为状态机的`暂停状态mHaltingState`、一个状态为状态机的`退出状态mQuittingState`

```java
private SmHandler(Looper looper, StateMachine sm) {
    super(looper);
    mSm = sm;
    // 这两个状态 无父状态
    addState(mHaltingState, null);
    addState(mQuittingState, null);
}
```

- `mHaltingState`状态，让状态机暂停，对应的`processMessage(Message msg)`方法，返回值为true，也就是会将消息消费掉。其实并没有处理，会调用State Machine的haltedProcessMessage方法。
- `mQuittingState`状态， 状态机将退出。`HandlerThread`线程对应的Looper将退出，`HandlerThread`线程会被销毁，所有加入到状态机的状态被清空。

#### 3.2.2、StateMachine的start() 方法

状态机的初始化完成后，想要使用必须先启动，下边来说状态机的启动方法`start()`

```java
public void start() {
    // mSmHandler can be null if the state machine has quit.
    SmHandler smh = mSmHandler;
    if (smh == null) {
        return;
    }
    // 完成状态机建设
   smh.completeConstruction();
}
```

- 主要是`completeConstruction()`方法，用于完成状态机的建设。

```java
private final void completeConstruction() {
    int maxDepth = 0;
    // 循环判断所有状态找出状态树的最大深度
    for (StateInfo si : mStateInfo.values()) {
        int depth = 0;
        for (StateInfo i = si; i != null; depth++) {
            i = i.parentStateInfo;
        }
        if (maxDepth < depth) {
            maxDepth = depth;
        }
    }
    // 状态堆栈
    mStateStack = new StateInfo[maxDepth];
    // 临时状态堆栈
    mTempStateStack = new StateInfo[maxDepth];
    // 初始化堆栈
    setupInitialStateStack();

    // 先发送一个消息，完成初始化
    sendMessageAtFrontOfQueue(obtainMessage(SM_INIT_CMD, mSmHandlerObj));
}
```

- `mStateStack`与`mTempStateStack`为两个用数组。这两个数组最d长的度，即为`maxDepth`。是用来存储`当前状态`与`当前状态的父状态、父父状态、...等`
- `setupInitialStateStack();`完成状态的初始化，将当前的状态与`当前状态的父状态、父父状态、...放入到`mTempStateStack`堆栈中，然后在出栈、入栈到mStateStack。

```java
private final void setupInitialStateStack() {
    StateInfo curStateInfo = mStateInfo.get(mInitialState);
    for (mTempStateStackCount = 0; curStateInfo != null; mTempStateStackCount++) {
        mTempStateStack[mTempStateStackCount] = curStateInfo;
        curStateInfo = curStateInfo.parentStateInfo;
    }

    mStateStackTopIndex = -1;
    moveTempStateStackToStateStack();
}
```

- 接着看completeConstruction最后一个方法调用。

```java
// 发送初始化完成的消息（消息放入到队列的最前边）
sendMessageAtFrontOfQueue(obtainMessage(SM_INIT_CMD, mSmHandlerObj));
```

- 发送一个初始化完成的消息到`SmHandler`当中。

下边来看一下`SmHandler`的`handleMessage(Message msg)`方法，该方法的主要是三大模块，第一个消息处理，或者说是分配到对应的状态再有对应的状态进行处理比较合适，第二个状态的初始化，大概可以理解成执行初始化状态路径上每个状态的enter方法，第三个执行状态转移，即更新状态树。

```java
public final void handleMessage(Message msg) {

    if (!mHasQuit) {
        mMsg = msg;
        State msgProcessedState = null;
        if (mIsConstructionCompleted) {
            msgProcessedState = processMsg(msg);// 1. 第一个消息处理  
        }
        // 接收到 初始化完成的消息
        else if (!mIsConstructionCompleted
                && (mMsg.what == SM_INIT_CMD) && (mMsg.obj == mSmHandlerObj)) {
            /** Initial one time path. */
            // 初始化完成
            mIsConstructionCompleted = true;
            // 调用mStateStack中所有状态的enter方法，并将堆栈中的状态设置为活跃状态
            invokeEnterMethods(0);
            // 2.第二个状态的初始化  
        } else {
		// ..
        }
        // 3.第三个执行状态转移  
        performTransitions(msgProcessedState, msg);
    }
}
```

- 第一次发送消息时mIsConstructionCompleted为false，发送的消息为obtainMessage(SM_INIT_CMD, mSmHandlerObj)，因此mMsg.what == SM_INIT_CMD和mMsg.obj == mSmHandlerObj为true。
- 接收到初始化完成的消息后`mIsConstructionCompleted = true;`对应的标志位变过来
- 执行 `invokeEnterMethods`方法将`mStateStack`堆栈中的所有状态设置为活跃状态，执行堆栈中状态的`enter()`方法
- `performTransitions(msgProcessedState, msg);`第一次发送消息时msgProcessedState为null、msg=-2且mDestState也为null，因此performTransitions中的关键方法都未执行。

`invokeEnterMethods`方法的方法体如下：

```java
private final void invokeEnterMethods(int stateStackEnteringIndex) {
    for (int i = stateStackEnteringIndex; i <= mStateStackTopIndex; i++) {
        if (mDbg) mSm.log("invokeEnterMethods: " + mStateStack[i].state.getName());
        mStateStack[i].state.enter();
        mStateStack[i].active = true;
    }
}
```

- 可以看到，由`父—>子`的顺序执行了`mStateStack`中状态的`enter()`方法，并将所有状态设置为活跃状态，至此start()方法执行完成。接下来就可以发送消息了。

#### 3.2.3、状态转化

状态机后续接收到消息消息时，由于已经完成了初始化，因此`mIsConstructionCompleted`值为true

接着看`processMsg()`方法：

```java
private final State processMsg(Message msg) {
    // 堆栈中找到当前状态
    StateInfo curStateInfo = mStateStack[mStateStackTopIndex];
    // 是否为退出消息
    if (isQuit(msg)) {
        // 转化为退出状态
        transitionTo(mQuittingState);
    } else {
        // 调用状态中的processMessage方法，返回true 表示是可处理此消息，返回false 则表示不可以处理。
        // 如果不能处理，则会调用父状态的processMessage方法，直到父状态为null或能处理此消息。
        while (!curStateInfo.state.processMessage(msg)) {
            curStateInfo = curStateInfo.parentStateInfo;
            if (curStateInfo == null) {
                // 如果都不能处理，则调用StateMachine的unhandledMessage方法
                mSm.unhandledMessage(msg);
                break;
            }
        }
    }
    // 如果消息能处理，则返回处理消息的状态，否则返回null
    return (curStateInfo != null) ? curStateInfo.state : null;
}
```

- 这里如果`mStateStack`堆栈中状态的processMessage(msg)方法返回true，则表示其消费掉了这个消息；
  如果其返回false，则表示不消费此消息，那么该消息将继续向其`父状态`进行传递；
- 最终将返回，消费掉该消息的状态。



由于在处理消息时，子状态可能会执行transitionTo来切换状态，先看一下`transitionTo(mWorkState);`方法：

```java
private final void transitionTo(IState destState) {
    mDestState = (State) destState;
}
```

- 可以看到，`transitionTo(IState destState)`方法很简单，只是mDestState将重新赋值。

接着`SmHandler`的`handleMessage(Message msg)`方法：

- 消息处理完成后，会执行`performTransitions(msgProcessedState, msg);`该方法用于进行状态切换的工作。

```java
private void performTransitions(State msgProcessedState, Message msg) {
    // 获取状态栈中的栈顶元素，即要切换过程的起始状态
    State orgState = mStateStack[mStateStackTopIndex].state;
    // 要切换的状态
    State destState = mDestState;
    if (destState != null) {
        while (true) {
            // 将要enter的方法的StateInfo节点都放入中转状态栈中，返回目标节点和起始 节点的公共父节点
            StateInfo commonStateInfo = setupTempStateStackWithStatesToEnter(destState);
            // 将起始节点到公共父节点的一条线都exit
            invokeExitMethods(commonStateInfo);
            // 将中转状态栈中的所有状态倒序再添加到状态栈中，这样，新的正确的状态栈建立起来了
            int stateStackEnteringIndex = moveTempStateStackToStateStack();
            // 从公共父状态开始，向目标节点的一条路径上，对每个节点依次执行enter方法，这和start状态机时的初始化步骤是一样的过程。
            invokeEnterMethods(stateStackEnteringIndex);
		    //由于已经转换到新状态，因此需要将所有延迟的消息移到消息队列的最前面，以便在消息队列中的其他任何消息之前对其进行处理。
            moveDeferredMessageAtFrontOfQueue();

            if (destState != mDestState) {
                // A new mDestState so continue looping
                // 如果在enter或是exit这些State的过程中，transitionTo方法被调用过，那么还要按照上面的流程再走一遍，进行一轮切换
                destState = mDestState;
            } else {
                // No change in mDestState so we're done
                break;
            }
        }
        //这是必须的，否则下一个State处理消息时不执行transitionTo 还要进入进上面的循环折腾一下
        mDestState = null;
    }
    /**
             * After processing all transitions check and
             * see if the last transition was to quit or halt.
             */
    if (destState != null) {
        if (destState == mQuittingState) {
            /**
                     * Call onQuitting to let subclasses cleanup.
                     */
            mSm.onQuitting();
            cleanupAfterQuitting();
        } else if (destState == mHaltingState) {
            /**
                     * Call onHalting() if we've transitioned to the halting
                     * state. All subsequent messages will be processed in
                     * in the halting state which invokes haltedProcessMessage(msg);
                     */
            mSm.onHalting();
        }
    }
}
```





