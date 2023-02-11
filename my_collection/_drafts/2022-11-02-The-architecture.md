---
layout: post
title: "The architecture🗻"
date: 2022-11-02 13:30:00+0800
chap: One_File_Architecture
---

# README🗻

## Intro

数字逻辑设计 -> 计算机组成 ->计算机体系结构(CA)

课程目录:

```assembly
ch1     Quantitativr principles
review  Pipelining
ch2     Memory Hierachy Design
ch3     Instruction_level Parallelism
ch4     Data_level Parallelism
ch5     Thread_level Parallelism
```

## Trend

计算机体系结构的设计，需要考虑整体技术的发展趋势，结合不同硬件的发展，来设计不同的结构

目前的超算中心都需要巨量的制冷装置

定量描述可靠性的量(reliability):

- `MTTF: Mean Time To Failure`
- `MTTR:Mean Time To Repair`
- `FIT: Failure In Time`
- `MTBF:Mean Time Between Failure = MTTF + MTTR`

可用性(`avaliablity`) = `(MTTF / (MTTF + MTTR)) = MTTF / MTBF`

解决故障的方式:

- `Time redudance`
- `Space redunce`

评估性能的方式：

- `Comparing Machines`

  - 执行时间
  - 吞吐量
  - MIPS：每秒执行的百万指令数

- `Comparing Machines Using Sets of programs`

  - Benchmark Suites：测试软件

    spec：不断维护的套件

指标：Wall-clock time 

CPU time : User time , System time 

响应时间一般正比于吞吐量

`performance = 1 / execution time `

`x is n times faster than y:n = exe time y / exe time x`

## Single-cycle,multi-cycle and Pipeline

多周期使指令更加灵活，也就是说，减少了`internal fragmantion`

- Latency

  指令发起到完成之间的时间

- Throughout

  每秒完成的指令条数

Pipeline hazard:

- Data Hazard 
- Structure hazard
- Control hazard

解决方式:

- stall

  流水线停顿：空指令和互锁

- 多个访问

- 多个内存

  以上两种都在解决structural hazard

- 双峰操作

  上升沿写入，下降沿读出

- 多套硬件

- 将指令的阶段切分成更小的执行单元

- 添加更多的硬件

- 旁路直通(Forwarding)

  在同一个周期下，当前指令结果尚未产生，而新的指令就想要读取数据，该情况下，旁路无法起到作用

- 需要添加控制逻辑

- Flush

  代价是无法通过软件优化的，只能在硬件上作出修改：3 --> 2 --> 1

- 延迟跳转

  

ideal流水线：完全没有任何stall





## Memory Hierarchy Design

最基础的两个随机访问存储器：

- `DRAM`:Dynamic Random Access Memory

  主存是DRAM:需要大存储量，并且断电数据不丢

- `SRAM`:Static Random Access Memory

  cache使用SRAM:小内存，响应快，但是断电数据会丢失

一般的存储结构都有两种设计思路：

- `Temporal Locality(Locality in Time)`

  将最常使用的数据放到靠近访问者的位置

- `Spatial Locality(Spatial in Space)`

  将访问数据块整个放到靠近访问者的位置

```assembly
                ┌───────────┐
                │ Registers │ 
                └───────────┘ 
                      ^
                      │ Instr
                      │ Operands
                      v
              ┌───────────────┐
              │     Cache     │ 
              └───────────────┘
                      ^
                      │ Blocks
                      │ 
                      v 
            ┌───────────────────┐
            │       Memory      │ 
            └───────────────────┘
                      ^
                      │ Pages
                      │ 
                      v          
          ┌───────────────────────┐
          │         Disk          │ 
          └───────────────────────┘
                      ^
                      │ Files
                      │ 
                      v                 
      ┌───────────────────────────────┐
      │             Tape              │ 
      └───────────────────────────────┘
```

关于存储的基本概念：

- `hit`: data appears in some block in the faster level
  - `hit rate`: 数据访问中，可以`Hit`的部分占所有操作的数据
  - `hit time`:数据访问时间 + 判断`hit`/`miss`时间
- `miss`:data needs to be retrieved from a block in the slower level
  - `miss rate`:1 - `hit rate`
  - `miss penalty`:将数据取到更高一层的时间 + 将数据送到处理器的时间

在整个体系中，几乎所有的存储单元都可以抽象为`cache`，有了这样的抽象之后，就可以将注意力放到如何优化`cache`上，将优化的过程梳理清除，也就基本明白了内存结构的重点内容：



- `memory`─── `blocks` ───> `cache`(假设`cache`中共有8个`blocks`,每个`block`存放4个`bytes`，32位地址):

  - `Direct mapped`

    直接映射，内存块必须放到`cache`对应的块中:

    ```assembly
    memory: 0x00000000 0x000000100 0x00000200 0x00000300 ... 0x00000700 0x00000800   
      
    cache:      0x0        0x1         0x2        0x3    ...     0x7        0x0
    ```

  - `Set associative`

    多路组相联，将所有的`blocks`分成多个`set`(组)，内存中对应的块，可以存放到组中的任意位置:

    ```assembly
    memory: 0x00000000 0x000000100 0x00000200 0x00000300 0x00000400 
    (2-way)
    cache:      0x0         0x2        0x4        0x6        0x1
    
    memory: 0x00000500 0x00000600 0x00000700 0x00000800 0x00000900 
    (2-way)                                     (maybe)   (maybe)  
    cache:      0x3         0x5        0x7        0x0       0x2   
    ```

  - `Fully associative`

    全相联，内存中的块可以任意存放到`cache`中的任意位置

- `tag`

  以32位地址为例:

  ```assembly
  ┌─────────────┬───────────────┬───────┐  
  │     Tag     │   Index       │Offset │ 
  └─────────────┴───────────────┴───────┘ 
       28 bits     2 bits         2 bits    ---  2-way
       27 bits     3 bits         2 bits    ---  direct
  cache:
  ┌─────────────┬───────────────┬───────┬─────────┐ 
  │     index   │   tag         │ data  │valid bit│ 
  └─────────────┴───────────────┴───────┴─────────┘ 
  ```

  在使用`index`确定了`set`/`block`之后，通过比较`tag`来确定数据是否是所需要的数据

- `replace`

  当在`cache`中，发生了`read miss`，并且将要载入的`block`的位置，已经有了`block`，就需要替换掉一个`block`

  在之前的示意图中，出现了`maybe`，原因是，不知道实际使用的`block`替换策略，使用不同的策略，使得替换发生冲突的组内的`block`时，会产生不同的结果

  - `random replacement`

    随机替换

  - `Least Recently Used(LRU)`

    替换最近最少被使用的块

    ```assembly
    2-way：
    A:0     to be replaced
    B:1
    
    4-way：
       A:0   to be replaced
     0 B:1
     
     1 C:0   
       D:1
    ```

  - `First in First out(FIFO)`

    替换最先进入组内的块

- `write strategy`

  发生了`write miss`时，不仅需要考虑载入数据到`cache`中，还要考虑数据在内存中修改的问题，使用的策略主要分为两种：

  - `write through`:

    载入数据的同时，也将修改的数据写入`memory`中

  - `write back`:

    仅将修改写到`cache`中，标记页为`dirty`，在该页被替换时，将修改写回`memory`

- `performance`

  `Average Memory Access Time = hit time + (miss rate x miss penalty)`

  `Average stalls per instruction = (AMAT – HitTime) x access times/ins`

  最直观的，提升`cache`性能的行为，就是尽可能地降低`miss rate`，有以下几种方式：

  - 增大块
  - 增大缓存
  - 提高组相联程度
  - 采用多级缓存
  - 为`read miss`指定高于`write miss`的优先级

- `TLB`

  用来快速使用最近调用过的`cache`的方法
  
  ```assembly
  ┌──────────────────────────────────────┬──────┬────┬──────┬───────┐   
  │virtual address │ physical address    │ dirty│ ref│valid │access │ 
  └──────────────────────────────────────┴──────┴────┴──────┴───────┘ 
  ```
  
  

`MPI:Memory reference per Instruction`

`Length of memory lantency:访问内存的时间长短`

`Length of latency overlapped:访问内存的时间重叠`

提高`Cache`性能的方式:

- `reduce hit time `

  - `Small and simple Caches`

  - `Way prediction`

  - `Avoid Address Translation:va -> pa`

    `TLB:speed up the translation`

  - 

## ILP

**Instruction-Level Parallelism**

Pipeline CPI = Ideal pipeline CPI Structural Stalls +  Data Hazard Stalls + Control Stalls

The potential overlap among instructions

第三章内容主要针对于数据竞争引起的性能的下降，提出不同的解决方法，主要是动态调度，对性能进行提升

对于结构冲突，在前面的内容中已经解决的大多，此处重点关注数据冲突和控制冲突

**Data Hazard**:

- RAR

  并不算是冲突，因为没有引起数据的改变，不影响执行结果

- RAW

  反依赖

- WAW

  结果输出的依赖

- WAR

  真正的冲突，没有办法解决，只能通过硬件的停顿来处理

需要注意的是，单条指令内部的相关性，如:

```assembly
add a1, a1, a1
```

不认为是相关。

### Dependence

共有三种不同类型的相关：

- Data Dependence 

  数据相关

  指令i生成的结果可能会被j用到则，j指令数据相关于i

  j数据相关于k，k数据相关于i

  如：

  ```assembly
  Loop: 
  	fld f0,0(x1) 	 //f0=array element
  	fadd.d f4,f0,f2  //add scalar in f2
  	fsd f4,0(x1) 	 //store result
  	addi x1,x1,-8    //decrement pointer
  				    //8 bytes (per DW)
  	bne x1,x2,Loop   //branch x16¼x2
  ```

  数据相关传递了三点信息：

  - 冒险的可能性
  - 计算结果必须遵循的顺序
  - 可开发并行度的上限

- Name Dependence

  名称相关

  将寄存器或存储器位置称为名称

  当两条指令使用相同的名称，但于该名称相关的指令之间没有数据流动时，就会发生名称相关

  WAR

  WAW

  因为没有数据流动，这些名称相关中设计的指令可以同时执行，或者重新排序

  所以只要对名称进行重命名，就可以使这些指令不再冲突

- Control Dependence

  控制相关

  指令i相对于分支指令的顺序，除了程序中第一基本块中的指令之外，其它所有指令都与某组分支存在控制相关

**Control Hazard**:

- 分支语句
- 绝对跳转语句

需要解决加载的下一条指令的问题

通常，需要维护数据相关和控制相关，来保护两个特性：

- exception behavior

  异常行为

  例：

  ```assembly
  		DADDU	R2,R3,R4		
  		BEQZ	R2,L1	
  		LW		R1,0(R2)
  L1:     ...
      # if exchange LW and BEQZ
  ```

- data flow

  数据流

  例：

```assembly
    DADDU	R1,R2,R3
    BEQZ	R4,L
    DSUBU	R1,R5,R6
L:	…
    OR	R7,R1,R8
    # OR depends on DADDU or DSUBU
```



**Instruction-Level Parallelism**

指令级别的指令集并行

**Basic Block**

基本块，一段顺序执行代码，除入口外没有其他的转入分支，除出口外没有其他转出分支

一般在一堆分支之间会执行3~6条指令

### Software approaches

在之后出现的例子中，使用以下的FP运算的延迟：

**Instruction                    Instruction                     Execution               Latency 
producing result            using result                    in cycles                 in cycles**

**FP ALU op                    Another FP ALU op           4                            3**

**FP ALU op                    Store double                    4                            2** 

**Load double                 FP ALU op                        1                            1**

**Load double                 Store double                     1                            0**

**Integer op                    Integer op                         1                            0**

例:

```c
for (int i = 999;i >= 0;i--) x[i] = x[i] + s
```

->

```assembly
loop:
    L.D    F0,0(R1)       #1
    #STALL 
    ADD.D  F4,F0,F2       #2
    #STALL
    #STALL
    S.D    F4,0(R1)       #3
    DADDUI R1,R1,-8       #4
    #STALL 
    BNE    R1,R2,loop     #5
```

-->

```assembly
loop:
    L.D    F0,0(R1)       #1
    DADDUI R1,R1,-8       #2
    ADD.D  F4,F0,F2       #3
    #STALL
    #STALL
    S.D    F4,8(R1)       #4
    BNE    R1,R2,loop     #5
```



**loop-leverl parallelism**

最简单的提高ILP的方法是，在循环的各次迭代之间开发并行，根据以上例子可以看到，对数组元素进行的实际运算仅占七个时钟周期中的三个

使用循环展开可以提高运算指令相对于分支和开销指令的数目

```c
for (int i = 0;i < 999; i++) x[i] = y[i] + z[i];
```

--->

```assembly
loop:
    L.D    F0,0(R1)       #1
    ADD.D  F4,F0,F2       #3
    #STALL
    #STALL
    S.D    F4,0(R1)       #4
    L.D    F6,-8(R1)      #1
    ADD.D  F8,F6,F2       #3
    #STALL
    #STALL
    S.D    F8,-8(R1)      #4
    L.D    F0,0(R1)       #1
    ADD.D  F10,F0,F2      #3
    S.D    F12,-16(R1)    #4
    L.D    F14,-24(R1)    #1
    ADD.D  F16,F14,F2     #3
    #STALL
    #STALL
    S.D    F16,-24(R1)    #4
    DADDUI R1,R1,-32
    BNE    R1,R2,loop
```

### Dynamic scheduling

希望一条指令在其数据操作数可用时立即开始执行。这样一种流水线实际是乱序执行，也意味着乱序完成

为了能够进行乱序执行，将五级简单流水线的ID流水级分为两个阶段：

- Issue--译码指令，检查结构性冒险
- Read operands--一直等到没有数据冒险，然后读取操作数



### Scoreboard

顺序发射，乱序完成

在硬件中增加多个数据通路，使用计分板，来记录通路中的信息及状态

**The pipeline stages with scoreboard**

- IF

- IS

  在硬件单元未被占用

  没有其它使用相同寄存器的指令时，发送指令

  用来避免结构冒险和WAW

- RO

  读操作被阻塞，直到两个操作数都可用

  可以动态解决RAW冒险

- EX

  声明计分板已经准备好，功能单元可以被重用

- WB

  计分板检查WAR冒险，必要时阻塞正在进行的指令

```assembly
┌──────────┐   
│Registers ├────── 2 data buses ──────>  FP Mult ┐    
├──────────┤                                     ├───┐  
│          ├────── 2 ─────────────────>  FP Mult ┘   │              
├──────────┤<───── 2 ───────────────────────^────────┘  
│.         ├────── 2 ─────────────────>  FP Div ─────┐     
│.         │<───── 2 ───────────────────────^────────┘   
│.         ├────── 2 ─────────────────>  FP Add ─────┐     
├──────────┤<───── 2 ───────────────────────^────────┘    
│          ├────── 2 ─────────────────>  Int unit ───┐ 
├──────────┤<───── 2 ───────────────────────^────────┘ 
│          │                                │
└──────────┘                                │
 ^                                          │ 
 └── Control ──────> scoreboard <─ Control ─┘ 
```

具体实现：

- IS

  检查结构冲突

- RO

  检查数据冲突

例：

```assembly
    FLD    F6, 34 (R2)
    FLD    F2, 45 (R3)
    FMUL.D F0, F2, F4
    FSUB.D F8, F2, F6
    FDIV.D F10,F0, F6
    FADD.D F6, F8, F2
```

scoreboard会维护三个表：

| Instrution              | IS   | RO   | EX   | WB   |
| ----------------------- | ---- | ---- | ---- | ---- |
| FLD          F6, 34(R2) | v    | v    | v    | v    |
| FLD          F2, 45(R3) | v    | v    | v    |      |
| FMUL.D   F0, F2, F4     | v    |      |      |      |
| FSUB.D    F8, F6, F2    | v    |      |      |      |
| FDIV.D     F10,F0, F6   | v    |      |      |      |
| FADD.D    F6, F8, F2    |      |      |      |      |



| Name    | Busy | Op   | Fi   | Fj   | Fk   | Qj      | Qk      | Rj   | Rk   |
| ------- | ---- | ---- | ---- | ---- | ---- | ------- | ------- | ---- | ---- |
| Integer | v    | Load | F2   | R3   |      |         |         | x    |      |
| Mult1   | v    | MUL  | F0   | F2   | F4   | integer |         | x    | v    |
| Mult2   | x    |      |      |      |      |         |         |      |      |
| Add     | v    | SUB  | F8   | F6   | F2   |         | integer | v    | x    |
| Divide  | v    | DIV  | F10  | F0   | F6   | Mult1   |         | x    | v    |

```assembly
#Rj, Rk:
    yes -- operand is ready but not read
    no && Qj == null -- operand is ready
    no && Qj != null -- operand is not ready
```

|      | F0    | F2      | F4   | F6   | F8   | F10    | ...  | F30  |
| ---- | ----- | ------- | ---- | ---- | ---- | ------ | ---- | ---- |
| Qi   | Mult1 | Integer |      |      | Add  | Divide |      |      |



### Tomasulo 

![image-20221129165405983](C:\Users\86186\AppData\Roaming\Typora\typora-user-images\image-20221129165405983.png)

在不同的运算单位前，增加了保留站，为指令添加了队列或是缓存，以便于对其进行判断

该算法的核心思想是，跟踪指令的操作数，来尽可能地减少RAW

在硬件中引入了寄存器重命名地概念，来最小化WAW和WAR

该算法和scoraeboard算法最核心的不同在于：

- 在IS阶段，只要reservation stations不满，就可以流出到站中，将流出条件变成了检测维护的table
- 在硬件ready后，开始执行，乱序在该步完成
- 写回结果，使用CDB总线，写回结果

将步骤变为了三个阶段：

- IS
- EX
- WB



例

```assembly
    FLD    F6, 34 (R2)
    FLD    F2, 45 (R3)
    FMUL.D F0, F2, F4
    FSUB.D F8, F2, F6
    FDIV.D F10,F0, F6
    FADD.D F6, F8, F2
    
```

假设：

LOAD: 1 cycle

ADD: 2 cycle

MUL: 6 cycle

DIV: 12 cycle

同样的，该算法中的保留站，也需要维护三个表：

| Instrustion        | IS   | EX(st) | EX(end) | WB   |
| ------------------ | ---- | ------ | ------- | ---- |
| FLD    F6, 34 (R2) | v    | v      |         | v    |
| FLD    F2, 45 (R3) | v    | v      |         |      |
| FMUL.D F0, F2, F4  | v    |        |         |      |
| FSUB.D F8, F2, F6  | v    |        |         |      |
| FDIV.D F10,F0, F6  | v    |        |         |      |
| FADD.D F6, F8, F2  | v    |        |         |      |



| Name  | Busy | Op   | Vj   | Vk                 | Qj    | Qk    | A             |
| ----- | ---- | ---- | ---- | ------------------ | ----- | ----- | ------------- |
| Load1 | x    |      |      |                    |       |       |               |
| Load2 | v    | Load |      |                    |       |       | 45 + Regs[R3] |
| Add1  | v    | SUB  |      | Mem[34 + Regs[R2]] | Load2 |       |               |
| Add2  | v    | ADD  |      |                    | Add1  | Load2 |               |
| Add3  | x    |      |      |                    |       |       |               |
| Mult1 | v    | MUL  |      | Regs[F4]           | Load2 |       |               |
| Mult2 | v    | DIV  |      | Mem[34 + Regs[R2]] | Mult1 |       |               |



|      | F0    | F2    | F4   | F6   | F8   | F10   | ...  | F30  |
| ---- | ----- | ----- | ---- | ---- | ---- | ----- | ---- | ---- |
| Qi   | Mult1 | Load2 |      | Add2 | Add1 | Mult2 |      |      |

其中，对于A(Address)字段，只存在于Load器件的reservation station中，并在计算出有效地址之前，存放立即数

一般，最后的结果是：

顺序发射、乱序执行、乱序完成

### Speculation

### Multithreaded Architecture

