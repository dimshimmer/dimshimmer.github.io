---
layout: post
title: "The computer network"
date: 2022-10-31 20:20:00+0800
chap: One_File_Network
---

# README

对计网知识的学习、复习和总结

## Outline

对于整个课程的大纲，最经典网络分层模型是一定要有的(OSI)：

```assembly
 _______________                                                     _______________
|               |                Application protocol               |               |
|  Application  |<=================================================>|   Application |
|_______________|                                                   |_______________|
       /\                                              
       || interface          
 ______\/_______                                                     _______________
|               |                Presectation protocol              |               |
|  Presentation |<=================================================>|   Presentation|
|_______________|                                                   |_______________|
       /\
       ||
 ______\/_______                                                     _______________
|               |                Session protocol                   |               |
|  Session      |<=================================================>|  Session      |
|_______________|                                                   |_______________|
       /\
       ||
 ______\/_______                                                     _______________
|               |                 Transport protocol                |               |
|  Transport    |<=================================================>|  Transport    |
|_______________|                                                   |_______________|
       /\
       ||
 ______\/_______                                                     _______________
|               |                                                   |               |
|  Network      |<=================================================>|  Network      |
|_______________|                                                   |_______________|
       /\
       ||
 ______\/_______                                                     _______________
|               |                                                   |               |
|  Data link    |                                                   |  Data link    |
|_______________|                                                   |_______________|
      /\
      ||
 _____\/________                                                     _______________
|               |                                                   |               |
|  Physical     |                                                   |  Physical     |
|_______________|                                                   |_______________|

```



其中最重要的三个概念是：

- Layer
- Protocol
- Interface

后续梳理的展开，也将按照`OSI`模型结构来进行(虽然从未被真正实现，但更有利于做结构梳理)



## The Medium Access Control Sublayer(MAC)

介质访问控制(MAC)，是数据链路层底层的部分，对于现在的计算机网络系统，静态信道分配不能很好的适应，因为其表现出的**突发性**和该方式本身对信道资源的浪费，所以引入介绍动态信道分配方案：

+ 流量独立(Independent Traffic)
+ 单信道(Single Channel)
+ 冲突可观察(Observable Collision)
+ 时间连续或分槽(Continuous or Slotted Time)
+ 载波侦听或不听(Carrier Sense or No Carrier Sense)

此处重点研究，不同多路访问信道的算法：

基本概念：

Frame time(帧时)：传输一个标准的、固定长度的帧所需要的时间(帧的长度/比特率)

- ALOHA(Additive Link On-Line Hawaii system)

  - Pure ALOHA

    当用户有数据需要发送时就传输

    在该系统中，采用统一长度的帧，比长度可变的帧更能到达最大的吞吐量

    $Throughout: S = G\times e^{-2G}$

    G:每帧时传送的帧数

    S:每帧时成功传送的帧数

    $When\ G = 0.5,S_{max} = \frac{1}{2e}$

    

  - Slotted ALOHA

    将时间分为时间槽(slot)，每个时间槽对应一帧，要求用户遵守统一的时间槽边界

    $S = Ge^{-G}$

    

- Carrier Sense Multiple Access Protocols

  在协议中，如果存在站监听是否存在载波(是否有传输)，并采取相应动作，称这样的协议为载波侦听协议

  

  通过每个站可以检测其他站的能力，来提高前面得到的最高利用率：$\frac{1}{e}$

  - 1-persistent CSMA

    站发送数据时，首先侦听信道：

    - 信道空闲：发送数据
    - 信道繁忙：等待其变为空闲

    ```assembly
    A station tries to send message:
    listen the channel:
    
                      |------wait a random time ---|
                     \/                            |
    busy ---wait---> idle ---send the message---> collision
           		                            \
            	                             \--->success
            	                             
    ******---collision situation---******
    [0] send the message .... 
          /\            /\
           |wait         |wait
    [1] prepare to send  |
                         |
           |-------------
    [2] prepare to send 
    [1] and [2] will send the same time
    or 
    [0] send the message ---sending--->
                               /\
      idle because of the delay|
          |--------------------|
    [1] listen ---send---> collision
    ```

    性能主要取决于**带宽延迟积(bandwidth-delay product)** 

  - Non-persistent CSMA

    与之前有所不同：

    ```assembly
    A station tries to send message:
    listen the channel: 
     /\         idle ---send the message---> collision
     |     		                  \                |
     |      	                   \--->success    |
     |                                             |
     | stop listen<----------------------------------
     | wait a random time
     |
    busy 
    ```

  - p-persistent CSMA

    ```assembly
    A station tries to send message:
    listen the channel:  (p probablity)
     /\         idle ---send the message---> collision
     |     		 /                 \                |
     |      	/ (1-p) probablity  \--->success    |
     |       wait next time slot                    |
     |                                              |
     | stop listen<----------------------------------
     | wait a random time
     |
    busy 
    ```

  - Carrier Sense Multiple Access Protocols

    快速检测到冲突后立即停止传输帧，而不是继续传输
    
    检测的原理是：
    
    站的硬件侦听信道，如果读回的信号不同于放到信道上的信号，则知道发生了碰撞
    
    该模型被分为三个状态：
    
    - contention
    - transmission
    - idle
    
    ```assembly
                       |--------------------|
                       \/                   | no
                 prepare to send frame? -----
                       |
                       |  yes <--------------------------------|
                       \/                                      |
                  carrie sense and listen                      | 
                       |                                       |
                       |                                       |
                       |                                wait a random time
                       \/                                      |
                      send                                     |
                       |                                       |
                       |                                       |
                       |                                       |
                       \/           yes                        | 
                      confilict ------------> strengthen the conflict
                       |             |
                       | no          |
                       |             |
                       \/            \/
                      exit         give up sending
    ```
    
    可以将CSMA/CD的竞争堪称是一个分槽ALOHA系统，时间槽宽为$2\tau$

- Collision-Free Protocols

  - Bit-Map Protocol

    在排队时每个站在槽中传送一位，按照顺序传送数据

    每个站都同意下一个是谁传输，所以永远都不会发生冲突

    信道效率的计算：

    - 低负载：每一帧的额外开销是N位，数据长度为d位，利用率为：d/(N + d)
    - 高负载：每一帧的额外开销只有一位，d/(d + 1)

  - token passing

    通过传递一个称为令牌的短消息，代表发送权限

    令牌环(token ring)：从一个方向上接收，在另一个方向上发送

    令牌总线(token bus)：令牌的拥有者利用总线发送帧，通过总线按照预定义的顺序发送令牌，该协议称为令牌总线

  - binary countdown

    通过二进制位串广播自己的地址，减少拥有太多站的网络的开销

    发送地址时，从高序到低序逐位竞争，信道利用率为:$d/(d + log_2N)$

- Limited-Contention Protocols

  为不同的站分配不同的概率，为不同的时间槽分不同的组

- Wavelength Division Multiple Access Protocols

- Wireless LAN Protocols

  **无限通信系统不能检测出正在发生的冲突，并且传输范围有限**，这样的特性带来了两个问题：

  - hidden station problem(隐藏终端问题)
  - exposed station problem(暴露终端问题)

  MACA协议：

  ```assembly
  sender: A
  reciver: B
      (30 bytes)
  A --- RTS ---> B
  B --- CTS ---> A
  
  Other station get RTS: stay silence
  Other station get CTS: stay silence
  ```


### Ethernet

#### classical Ethernet

经典以太网的MAC子层协议：

```assembly
bytes:   8    |        6             |       6          |   2    |  0-1500  | 0-46  |    4
      precode | destination address  | source addreess  | type   |   data   |  pad  |checksum
(Ehter net)


bytes:   8    |        6             |       6          |   2    |  0-1500  | 0-46  |    4
  precode,SOF | destination address  | source addreess  | type   |   data   |  pad  |checksum
(IEEE 802.3)
      
```

冲突检测、处理的方式:CSMA/CA with Binary Exponentioal Backoff

以太网取$51.2\mu s $为争用期的长度，如果发生冲突，就一定是在发送的前64字节，所以固定了最短有效帧长为64字节，凡长度小于64字节的帧，都是无效帧

强化碰撞：当发送数据的站一旦发现发生了碰撞，还要发送若干比特的人为干扰信号(jamming signal)

#### switched Ethernet

没个站都有一条专用的电线连接到一个中央集线器:

- hub: 作为冲突管理
- switch: 每一个端口，都可以作为冲突管理

#### fast Ethernet

一台计算机的最大带宽还是会受制于连接它到交换机端口的电缆

将比特时间从100纳秒降低到10纳秒

#### gigabit Ethernet

有两种工作模式：

- Full-duplex mode 

  所有的线路具有缓存能力，所以每台计算机或交换机在任何时候都可以自由地发送帧，不必侦听信道，竞争不可能发生

- Half-duplex mode

  计算机被连到集线器(hub)，而不是交换机时，无法缓存入境帧

由于传输速度的增加，使得最大的电缆的速度下降了一百倍，所以增加了特性，使得最大线缆的长度增加：

- carrier extension: 使用填充位，将帧的长度扩充到512字节
- frame bursting: 将多个待发送的帧级联在一起



为了使数据链路层能够更好地适应多种局域网标准，将该层拆为两个子层：

```assembly

LLC
MAC
```

### MAC layer

`MAC`地址：48 bit

路由器由于同时连接到两个网络上，因此有两块网卡和两个硬件地址

```assembly
network card --- get a MAC frame ---> check the MAC address ------> receive
                                                |               (unicast,broadcast,multicast)
                                                |
                                                \/
                                               abondon
```

### Wireless Lans

为了解决无线传输中的问题，采用两种模式：

- DCF: 分布式冲突控制
- PCF: 使用基站来控制所有的活动
