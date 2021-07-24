AIDL中的定向 tag 表示了在跨进程通信中数据的流向，其中 in 表示数据只能由客户端流向服务端， out 表示数据只能由服务端流向客户端，而 inout 则表示数据可在服务端与客户端之间双向流通。其中，数据流向是针对在客户端中的那个传入方法的对象而言的。in 为定向 tag 的话表现为服务端将会接收到一个那个对象的完整数据，但是客户端的那个对象不会因为服务端对传参的修改而发生变动；out 的话表现为服务端将会接收到那个对象的参数为空的对象，但是在服务端对接收到的空对象有任何修改之后客户端将会同步变动；inout 为定向 tag 的情况下，服务端将会接收到客户端传来对象的完整信息，并且客户端将会同步服务端对该对象的任何变动。

~~~java
@Override
public boolean onTransact(int code, android.os.Parcel data, android.os.Parcel reply, int flags) throws android.os.RemoteException {
    switch (code) {
        case INTERFACE_TRANSACTION: {
            reply.writeString(DESCRIPTOR);
            return true;
        }
        case TRANSACTION_getBooks: {
            data.enforceInterface(DESCRIPTOR);
            java.util.List<com.lypeer.ipcclient.Book> _result = this.getBooks();
            reply.writeNoException();
            reply.writeTypedList(_result);
            return true;
        }
        case TRANSACTION_addBookIn: {
            data.enforceInterface(DESCRIPTOR);
            //很容易看出来，_arg0就是输入的book对象
            com.lypeer.ipcclient.Book _arg0;
            //从输入的_data流中读取book数据，并将其赋值给_arg0
            if ((0 != data.readInt())) {
                _arg0 = com.lypeer.ipcclient.Book.CREATOR.createFromParcel(data);
            } else {
                _arg0 = null;
            }
            //在这里才是真正的开始执行实际的逻辑，调用服务端写好的实现
            this.addBookIn(_arg0);
            //执行完方法之后就结束了，没有针对_reply流的操作，所以客户端不会同步服务端的变化
            reply.writeNoException();
            return true;
        }
        case TRANSACTION_addBookOut: {
            data.enforceInterface(DESCRIPTOR);
            com.lypeer.ipcclient.Book _arg0;
            //可以看到，用out作为定向tag的方法里，根本没有从_data里读取book对象的操作，
            //而是直接new了一个book对象，这就是为什么服务端收不到客户端传过来的数据
            _arg0 = new com.lypeer.ipcclient.Book();
            //执行具体的事物逻辑
            this.addBookOut(_arg0);
            reply.writeNoException();
            //在这里，_arg0是方法的传入参数，故服务端的实现里对传参做出的任何修改，
            //都会在_arg0中有所体现，将其写入_reply流，就有了将这些修改传回客户端的前提
            if ((_arg0 != null)) {
                reply.writeInt(1);
                _arg0.writeToParcel(reply, android.os.Parcelable.PARCELABLE_WRITE_RETURN_VALUE);
            } else {
                reply.writeInt(0);
            }
            return true;
        }
        case TRANSACTION_addBookInout: {
            data.enforceInterface(DESCRIPTOR);
            com.lypeer.ipcclient.Book _arg0;
            //inout同样兼具上两个方法中的细节
            if ((0 != data.readInt())) {
                _arg0 = com.lypeer.ipcclient.Book.CREATOR.createFromParcel(data);
            } else {
                _arg0 = null;
            }
            this.addBookInout(_arg0);
            reply.writeNoException();
            if ((_arg0 != null)) {
                reply.writeInt(1);
                _arg0.writeToParcel(reply, android.os.Parcelable.PARCELABLE_WRITE_RETURN_VALUE);
            } else {
                reply.writeInt(0);
            }
            return true;
        }
    }
    return super.onTransact(code, data, reply, flags);
}

private static class Proxy implements com.lypeer.ipcclient.BookManager {
    private android.os.IBinder mRemote;

    Proxy(android.os.IBinder remote) {
        mRemote = remote;
    }

    @Override
    public android.os.IBinder asBinder() {
        return mRemote;
    }

    public java.lang.String getInterfaceDescriptor() {
        return DESCRIPTOR;
    }

    //保证客户端与服务端是连接上的且数据传输正常
    @Override
    public java.util.List<com.lypeer.ipcclient.Book> getBooks() throws android.os.RemoteException {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        java.util.List<com.lypeer.ipcclient.Book> _result;
        try {
            _data.writeInterfaceToken(DESCRIPTOR);
            mRemote.transact(Stub.TRANSACTION_getBooks, _data, _reply, 0);
            _reply.readException();
            _result = _reply.createTypedArrayList(com.lypeer.ipcclient.Book.CREATOR);
        } finally {
            _reply.recycle();
            _data.recycle();
        }
        return _result;
    }

    //通过三种定位tag做对比试验，观察输出的结果
    @Override
    public void addBookIn(com.lypeer.ipcclient.Book book) throws android.os.RemoteException {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
            _data.writeInterfaceToken(DESCRIPTOR);
            //可以看到，这里执行的操作很简单，仅仅是判断book是否为空，
            // 如果为空，则_data写入int值1,将其book写入_data中
            // 如果不为空，则_data写入int值0
            if ((book != null)) {
                _data.writeInt(1);
                book.writeToParcel(_data, 0);
            } else {
                _data.writeInt(0);
            }
            //之后直接调用transact()方法，将方法的编码，
            // _data（包含从客户端流向服务端的book流），
            // _reply（包含从服务端流向客户端的数据流）传入
            mRemote.transact(Stub.TRANSACTION_addBookIn, _data, _reply, 0);
            _reply.readException();
        } finally {
            _reply.recycle();
            _data.recycle();
        }
    }

    @Override
    public void addBookOut(com.lypeer.ipcclient.Book book) throws android.os.RemoteException {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
            _data.writeInterfaceToken(DESCRIPTOR);
            //在定向tag为out的方法里，没有将book对象写入_data流的操作
            mRemote.transact(Stub.TRANSACTION_addBookOut, _data, _reply, 0);
            _reply.readException();
            //与tag为in的方法里面不同的是，在执行transact方法之后，
            //还有针对_reply的操作，并且将book赋值为_reply流中的数据
            if ((0 != _reply.readInt())) {
                book.readFromParcel(_reply);
            }
        } finally {
            _reply.recycle();
            _data.recycle();
        }
    }

    @Override
    public void addBookInout(com.lypeer.ipcclient.Book book) throws android.os.RemoteException {
        android.os.Parcel _data = android.os.Parcel.obtain();
        android.os.Parcel _reply = android.os.Parcel.obtain();
        try {
            _data.writeInterfaceToken(DESCRIPTOR);
            //定向tag为inout的方法里综合了上两个方法里的操作
            if ((book != null)) {
                _data.writeInt(1);
                book.writeToParcel(_data, 0);
            } else {
                _data.writeInt(0);
            }
            mRemote.transact(Stub.TRANSACTION_addBookInout, _data, _reply, 0);
            _reply.readException();
            if ((0 != _reply.readInt())) {
                book.readFromParcel(_reply);
            }
        } finally {
            _reply.recycle();
            _data.recycle();
        }
    }
}
~~~

