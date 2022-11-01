---
layout: post
title: "Heap at High Level Libc"
date: 2022-10-28 10:45:00+0800
chap: level_1
---

# Pwn-Heap

作为这个专栏的开篇，决定先写一写，`pwn`里面，高版本下`libc`的特性以及可能存在的漏洞利用(站在从前师傅的肩膀上)。之前遇到的一个题目印象实在是太深了，在里面碰到了这样的问题，能在开篇里把这个问题梳理好学习好，也是件很有成就感的事情吧

## Description

远程靶机提供的`libc`版本是低于`2.34`的，而在本地的`ubuntu 22.04`中，已经在使用`libc 2.43`及以上了，所以在本地和远程出现的现象，总是会有偏差，花了很长的时间去解决，所以想要梳理一下版本间的不同，学习更多的，`heap`相关的漏洞利用方法

## Before

在`Linux`环境下，通过几个实验和`gdb`的跟踪，来研究`heap`的运行机制：

```shell
# 首先查看该环境下的glibc的版本:
$ ls -l /lib/x86_64-linux-gnu/libc.so.6
lrwxrwxrwx 1 root root 12 Apr  7  2022 /lib/x86_64-linux-gnu/libc.so.6 -> libc-2.31.so
```

一般我们使用到的变量，如果存在于函数中，都是分配到栈上的临时变量，而关于堆，在使用`malloc`函数动态分配空间时，需要从堆中取得内存，分配给程序中要用到的指针，也就是说，这一部分的地址是存在于堆上：

```c
#include<stdlib.h>
#include<stdio.h>

int main(){
    char buf[10] = {0};
    char *buf_h = malloc(sizeof(char) * 10);
    printf("the address of buf: %p\n",buf);
    printf("the address of buf_h: %p\n",buf_h);
    return 0;
}
```

运行观察：

```shell
$ ./test 
the address of buf: 0x7ffcf2b2662e
the address of buf_h: 0x558af36962a0
#结合gdb，观察内存的分布：
gef➤  vmm
[ Legend:  Code | Heap | Stack ]
Start              End                Offset             Perm Path
0x00555555554000 0x00555555555000 0x00000000000000 r-- /test
0x00555555555000 0x00555555556000 0x00000000001000 r-x /test
0x00555555556000 0x00555555557000 0x00000000002000 r-- /test
0x00555555557000 0x00555555558000 0x00000000002000 r-- /test
0x00555555558000 0x00555555559000 0x00000000003000 rw- /test
0x007ffff7dcc000 0x007ffff7dee000 0x00000000000000 r-- /usr/lib/x86_64-linux-gnu/libc-2.31.so
0x007ffff7dee000 0x007ffff7f66000 0x00000000022000 r-x /usr/lib/x86_64-linux-gnu/libc-2.31.so
0x007ffff7f66000 0x007ffff7fb4000 0x0000000019a000 r-- /usr/lib/x86_64-linux-gnu/libc-2.31.so
0x007ffff7fb4000 0x007ffff7fb8000 0x000000001e7000 r-- /usr/lib/x86_64-linux-gnu/libc-2.31.so
0x007ffff7fb8000 0x007ffff7fba000 0x000000001eb000 rw- /usr/lib/x86_64-linux-gnu/libc-2.31.so
0x007ffff7fba000 0x007ffff7fc0000 0x00000000000000 rw- 
0x007ffff7fcb000 0x007ffff7fce000 0x00000000000000 r-- [vvar]
0x007ffff7fce000 0x007ffff7fcf000 0x00000000000000 r-x [vdso]
0x007ffff7fcf000 0x007ffff7fd0000 0x00000000000000 r-- /usr/lib/x86_64-linux-gnu/ld-2.31.so
0x007ffff7fd0000 0x007ffff7ff3000 0x00000000001000 r-x /usr/lib/x86_64-linux-gnu/ld-2.31.so
0x007ffff7ff3000 0x007ffff7ffb000 0x00000000024000 r-- /usr/lib/x86_64-linux-gnu/ld-2.31.so
0x007ffff7ffc000 0x007ffff7ffd000 0x0000000002c000 r-- /usr/lib/x86_64-linux-gnu/ld-2.31.so
0x007ffff7ffd000 0x007ffff7ffe000 0x0000000002d000 rw- /usr/lib/x86_64-linux-gnu/ld-2.31.so
0x007ffff7ffe000 0x007ffff7fff000 0x00000000000000 rw- 
0x007ffffffde000 0x007ffffffff000 0x00000000000000 rw- [stack]
0xffffffffff600000 0xffffffffff601000 0x00000000000000 --x [vsyscall]
#在调用了malloc之后:
==>
gef➤  vmm
[ Legend:  Code | Heap | Stack ]
Start              End                Offset             Perm Path
0x00555555554000 0x00555555555000 0x00000000000000 r-- /test
0x00555555555000 0x00555555556000 0x00000000001000 r-x /test
0x00555555556000 0x00555555557000 0x00000000002000 r-- /test
0x00555555557000 0x00555555558000 0x00000000002000 r-- /test
0x00555555558000 0x00555555559000 0x00000000003000 rw- /test
0x00555555559000 0x0055555557a000 0x00000000000000 rw- [heap]
0x007ffff7dcc000 0x007ffff7dee000 0x00000000000000 r-- /usr/lib/x86_64-linux-gnu/libc-2.31.so
...
```

可以看到，二者的地址相差是比较大的，并且，在调用了`malloc`函数后，虚拟地址上，才出现``[heap]``的标识，并且大小为`0x21000`，并且地址是在可执行代码的正上方

再使用简单的程序进行实验:

```c
//test.c
#include<stdlib.h>

int main(){
    void*chunk[0x20];
    void*bins[0x10];
    for (int i = 0;i < 0x20;i++){
        chunk[i] = malloc(0x20 * i);
    }
    for (int i = 0; i < 0x10 ;i +=2){
        free(chunk[i]);
    }
    for (int i = 0; i < 0x10; i ++) bins[i] = malloc(0x10 * i);
    return 0;
}
```

使用`gdb`调试查看：

```shell
#首先查看未分配内存时，heap下的bin的情况：
gef➤  heap bins
[!] No heap section
[+] Uninitialized tcache for thread 1
─────────── Fastbins for arena at 0x7ffff7fb8b80 ───────────────
Fastbins[idx=0, size=0x20] 0x00
Fastbins[idx=1, size=0x30] 0x00
Fastbins[idx=2, size=0x40] 0x00
Fastbins[idx=3, size=0x50] 0x00
Fastbins[idx=4, size=0x60] 0x00
Fastbins[idx=5, size=0x70] 0x00
Fastbins[idx=6, size=0x80] 0x00
──────────── Unsorted Bin for arena at 0x7ffff7fb8b80 ────────────
[*] Invalid backward and forward bin pointers(fw==bk==NULL)
──────────── Small Bins for arena at 0x7ffff7fb8b80 ──────────────
[*] Invalid backward and forward bin pointers(fw==bk==NULL)
[+] Found 0 chunks in 0 small non-empty bins.
──────────── Large Bins for arena at 0x7ffff7fb8b80 ──────────────
[*] Invalid backward and forward bin pointers(fw==bk==NULL)
[+] Found 0 chunks in 0 large non-empty bins.
#并且此时无任何chunk

#在分配了一个大小为0的chunk之后：
gef➤  heap chunks
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
    [0x0000555555559010        ................]
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
    [0x00005555555592a0         ................]
Chunk(addr=0x5555555592c0, size=0x20d50, flags=PREV_INUSE)
    [0x00005555555592c0         ................]
Chunk(addr=0x5555555592c0, size=0x20d50, flags=PREV_INUSE)  ←  top chunk
#分配了大小为0x20的chunk后:
gef➤  heap chunks
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
    [0x0000555555559010        ................]
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
    [0x00005555555592a0         ................]
Chunk(addr=0x5555555592c0, size=0x30, flags=PREV_INUSE)
    [0x00005555555592c0         ................]
Chunk(addr=0x5555555592f0, size=0x20d20, flags=PREV_INUSE)
    [0x00005555555592f0         ................]
Chunk(addr=0x5555555592f0, size=0x20d20, flags=PREV_INUSE)  ←  top chunk
#全部分配完后：
gef➤  heap chunks
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
Chunk(addr=0x5555555592c0, size=0x30, flags=PREV_INUSE)
Chunk(addr=0x5555555592f0, size=0x50, flags=PREV_INUSE)
Chunk(addr=0x555555559340, size=0x70, flags=PREV_INUSE)
Chunk(addr=0x5555555593b0, size=0x90, flags=PREV_INUSE)
Chunk(addr=0x555555559440, size=0xb0, flags=PREV_INUSE)
Chunk(addr=0x5555555594f0, size=0xd0, flags=PREV_INUSE)
Chunk(addr=0x5555555595c0, size=0xf0, flags=PREV_INUSE)
Chunk(addr=0x5555555596b0, size=0x110, flags=PREV_INUSE)
Chunk(addr=0x5555555597c0, size=0x130, flags=PREV_INUSE)
Chunk(addr=0x5555555598f0, size=0x150, flags=PREV_INUSE)
Chunk(addr=0x555555559a40, size=0x170, flags=PREV_INUSE)
Chunk(addr=0x555555559bb0, size=0x190, flags=PREV_INUSE)
Chunk(addr=0x555555559d40, size=0x1b0, flags=PREV_INUSE)
Chunk(addr=0x555555559ef0, size=0x1d0, flags=PREV_INUSE)
Chunk(addr=0x55555555a0c0, size=0x1f0, flags=PREV_INUSE)
Chunk(addr=0x55555555a2b0, size=0x210, flags=PREV_INUSE)
Chunk(addr=0x55555555a4c0, size=0x230, flags=PREV_INUSE)
Chunk(addr=0x55555555a6f0, size=0x250, flags=PREV_INUSE)
Chunk(addr=0x55555555a940, size=0x270, flags=PREV_INUSE)
Chunk(addr=0x55555555abb0, size=0x290, flags=PREV_INUSE)
Chunk(addr=0x55555555ae40, size=0x2b0, flags=PREV_INUSE)
Chunk(addr=0x55555555b0f0, size=0x2d0, flags=PREV_INUSE)
Chunk(addr=0x55555555b3c0, size=0x2f0, flags=PREV_INUSE)
Chunk(addr=0x55555555b6b0, size=0x310, flags=PREV_INUSE)
Chunk(addr=0x55555555b9c0, size=0x330, flags=PREV_INUSE)
Chunk(addr=0x55555555bcf0, size=0x350, flags=PREV_INUSE)
Chunk(addr=0x55555555c040, size=0x370, flags=PREV_INUSE)
Chunk(addr=0x55555555c3b0, size=0x390, flags=PREV_INUSE)
Chunk(addr=0x55555555c740, size=0x3b0, flags=PREV_INUSE)
Chunk(addr=0x55555555caf0, size=0x3d0, flags=PREV_INUSE)
Chunk(addr=0x55555555cec0, size=0x3f0, flags=PREV_INUSE)
Chunk(addr=0x55555555d2b0, size=0x1cd60, flags=PREV_INUSE)
Chunk(addr=0x55555555d2b0, size=0x1cd60, flags=PREV_INUSE)  ←  top chunk
#第一次调用free后：
gef➤  heap bins
─────── Tcachebins for thread 1 ──────────
Tcachebins[idx=0, size=0x20, count=1] ←  Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
#全部free：
gef➤  heap bins
──────── Tcachebins for thread 1 ────────────
Tcachebins[idx=0, size=0x20, count=1] ←  Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE) 
Tcachebins[idx=3, size=0x50, count=1] ←  Chunk(addr=0x5555555592f0, size=0x50, flags=PREV_INUSE) 
Tcachebins[idx=7, size=0x90, count=1] ←  Chunk(addr=0x5555555593b0, size=0x90, flags=PREV_INUSE) 
Tcachebins[idx=11, size=0xd0, count=1] ←  Chunk(addr=0x5555555594f0, size=0xd0, flags=PREV_INUSE) 
Tcachebins[idx=15, size=0x110, count=1] ←  Chunk(addr=0x5555555596b0, size=0x110, flags=PREV_INUSE) 
Tcachebins[idx=19, size=0x150, count=1] ←  Chunk(addr=0x5555555598f0, size=0x150, flags=PREV_INUSE) 
Tcachebins[idx=23, size=0x190, count=1] ←  Chunk(addr=0x555555559bb0, size=0x190, flags=PREV_INUSE) 
Tcachebins[idx=27, size=0x1d0, count=1] ←  Chunk(addr=0x555555559ef0, size=0x1d0, flags=PREV_INUSE)
#chunks:
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
    [0x0000555555559010     01 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00    ]
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
    [0x00005555555592a0     00 00 00 00 00 00 00 00 10 90 55 55 55 55 00 00    ]
Chunk(addr=0x5555555592c0, size=0x30, flags=PREV_INUSE)
    [0x00005555555592c0     00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ]
Chunk(addr=0x5555555592f0, size=0x50, flags=PREV_INUSE)
    [0x00005555555592f0     00 00 00 00 00 00 00 00 10 90 55 55 55 55 00 00    ]
# free 后的malloc：
gef➤  heap bins
─────────── Tcachebins for thread 1 ─────────
Tcachebins[idx=15, size=0x110, count=1] ←  Chunk(addr=0x5555555596b0, size=0x110, flags=PREV_INUSE) 
Tcachebins[idx=19, size=0x150, count=1] ←  Chunk(addr=0x5555555598f0, size=0x150, flags=PREV_INUSE) 
Tcachebins[idx=23, size=0x190, count=1] ←  Chunk(addr=0x555555559bb0, size=0x190, flags=PREV_INUSE) 
Tcachebins[idx=27, size=0x1d0, count=1] ←  Chunk(addr=0x555555559ef0, size=0x1d0, flags=PREV_INUSE)
```

观察其中值得注意的地方：

-  chunk地址最低的部分没有被分配，其中包含了什么数据
- 分配出的chunk的size与代码中写出的大小不符
- 其它的bin没有被使用

从以上实际出现的情况出发，学习`malloc`和`free`的原理，并结合源码，了解其中的数据结构：





