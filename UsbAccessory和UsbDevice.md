UsbAccessory和UsbDevice的区别

- UsbDevice：正常的，USB的Host和USB的Device架构中的USB的Device

- - 所以，此时：Android设备是USB的Host，外接的USB设备是USB的Device

  - - 此时，Android设备作为USB的Host，要做USB Host该干的事情：

    - - 给USB外接设备供电
      - 负责管理USB总线

- UsbAccessory：和标准的USB的概念相反

- - USB设备是USB的Host

  - - 所以，此时USB设备，也要干其作为USB的Host的事情

    - - USB设备，要给作为USB的Device的Android设备供电
      - USB设备要负责管理USB总线

  - 而Android设备是USB的Device

  - - 此时，从概念上说，相当于把Android设备，当做Accessory附件，挂在USB设备上