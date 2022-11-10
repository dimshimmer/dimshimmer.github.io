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

首先，在`Linux`环境下，堆通过`ptmalloc2`来管理，通过几个实验和`gdb`的跟踪，来研究`heap`的运行机制：

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
...
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
[+] Found 0 chunks in 0 small non-empty bins.
──────────── Large Bins for arena at 0x7ffff7fb8b80 ──────────────
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

从以上实际出现的情况出发，学习`malloc`和`free`的原理，并结合源码，了解其中的数据结构

## Heap

### Arena

在`glibc`中，初始的堆空间由`brk`系统调用产生，可以在上面的实验中看到，在第一次申请空间之前，并不会出现对应的堆空间，在第一次`malloc`之后，才会出现对应的内存空间

如果第一次申请出的堆空间不够大，则会继续调用`brk`系统，来扩展堆空间；当单次分配空间过大，则使用`mmap`，来创建匿名映射段供用户使用

> brk:**通常将堆的当前内存边界称为”Program brak"简称为brk，brk用于记录的是当前堆已经分配使用的结束地址（即未使用分配的起始地址）。**
>
> mmap:mmap() 系统调用能够将文件映射到内存空间，然后可以通过读写内存来读写文件

先对堆的概念做一个总概：

`arena`：是堆内存本身

- 主线程的`main_arena`

  最开始调用`sbrk`函数创建大小为(128 KB + `chunk_size`) align 4KB的空间作为`heap`

  使用`sbrk`或`mmap`增加大小

- 其他线程的`arena`

  最开始调用`mmap`映射一块大小为`HEAP_MAX_SIZE`的空间(64位系统上默认为64MB)，作为sub-heap

  使用`mmap`增加`top chunk`的大小

```c
typedef struct malloc_chunk*mfastbinptr;
typedef struct malloc_chunk*mchunkptr;

#define MAX_FAST_SIZE     (80 * SIZE_SZ / 4)
#define NFASTBINS  (fastbin_index (request2size (MAX_FAST_SIZE)) + 1)
#define SIZE_SZ (sizeof (INTERNAL_SIZE_T))

struct malloc_state
{
  /* Serialize access.  */
  __libc_lock_define (, mutex);

  /* Flags (formerly in max_fast).  */
  int flags;

  /* Set if the fastbin chunks contain recently inserted free blocks.  */
  /* Note this is a bool but not all targets support atomics on booleans.  */
  int have_fastchunks;

  /* Fastbins */
  mfastbinptr fastbinsY[NFASTBINS];

  /* Base of the topmost chunk -- not otherwise kept in a bin */
  mchunkptr top;

  /* The remainder from the most recent split of a small request */
  mchunkptr last_remainder;

  /* Normal bins packed as described above */
  mchunkptr bins[NBINS * 2 - 2];

  /* Bitmap of bins */
  unsigned int binmap[BINMAPSIZE];

  /* Linked list */
  struct malloc_state *next;

  /* Linked list for free arenas.  Access to this field is serialized
     by free_list_lock in arena.c.  */
  struct malloc_state *next_free;

  /* Number of threads attached to this arena.  0 if the arena is on
     the free list.  Access to this field is serialized by
     free_list_lock in arena.c.  */
  INTERNAL_SIZE_T attached_threads;

  /* Memory allocated from the system in this arena.  */
  INTERNAL_SIZE_T system_mem;
  INTERNAL_SIZE_T max_system_mem;
};
```



`chunk`作为`heap`分配的基本单位，先看`malloc.c`中的数据结构：

```c
/*
#ifndef INTERNAL_SIZE_T
#define INTERNAL_SIZE_T size_t
#endif
*/
struct malloc_chunk {
  INTERNAL_SIZE_T      mchunk_prev_size;  /* Size of previous chunk (if free).  */
  INTERNAL_SIZE_T      mchunk_size;       /* Size in bytes, including overhead. */

  struct malloc_chunk* fd;         /* double links -- used only if free. */
  struct malloc_chunk* bk;

  /* Only used for large blocks: pointer to next larger size.  */
  struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
  struct malloc_chunk* bk_nextsize;
};
//glibc 2.34与之前的版本相比，无变化
```

```assembly
                 |--------------------------|-------------------------|
                 |prve_size / prve_data     |size           |N |M |P  | P: if prve chunk used
                 |P = 1: prve_data          |N: if blong to idle      |
                 |P = 0: prve_size          |M: if allocated by mmap  |
                 |--------------------------|-------------------------|
                 |fd / data                 |bk / data                |
                 |if freed: next free chunk |if freed: last free chunk|
                 |                          |                         |
                 |--------------------------|-------------------------|
                 |fd_nextsize / data        |bk_nextsize / data       |
                 |next different size large |last different size large|
                 |bin                       |bin                      |
                 |--------------------------|-------------------------|
                 |                                                    |
                 |          unused / data                             |
                 |                                                    |
                 |____________________________________________________| 
                 
```

在glibc中，对齐由malloc.c中的request2size宏实现。可以简单将该操作理解为下表中的映射，即：

实际size = 请求的size+8后对应的下一个0x10对齐的值

| 请求大小    | 实际分配大小 |
| ----------- | ------------ |
| 0x00 ~ 0x18 | 0x20         |
| 0x19 ~ 0x28 | 0x30         |
| 0x29 ~ 0x38 | 0x40         |
| ...         | ...          |
| 0xE9 ~ 0xF8 | 0x100        |
| ...         | ...          |

### Bin

在堆题中，最常被利用到的，是`bin`部分，是堆空闲块的管理结构，是由`free chunk`组成的链表，主要的作用是加快分配速度，分为以下几类：

- `fast bin: last in first out `单链表

  将小`chunk`(大小范围为[0x20, 0x80])单独管理，以单向链表的形式组织起来，链表长度不限，只是用`fd` 连接，不适用`bk`字段

  ```assembly
  fastbinY[0] --- fd ---> [chunk 0x20] --- fd ---> [chunk 0x20] --- fd ---> NULL
  ....
  fastbinY[6] --- fd ---> [chunk 0x80] --- fd ---> NULL
  ```

- `unsorted bin: first in first out`双链表

  大小没有顺序，任何`size`的`chunk`都可以被放入该`bin`中

  ```assembly
  |---------------------------------->|bins[0]|-------------------------------------------|
  | |---------------------------------|       |<--------------- fd --------------------|  |
  | |                                                                                  |  |
  | |--- fd ----->|chunk| ---- fd --->|chunk| ---- fd -->     ---- fd --->|chunk|------|  |
  |---- bk -------|0x1a0| <--- bk --- |0x20 | <--- bk --- ... <--- bk --- |0x500|<--------| 
  ```

- `small bin: first in first out`双链表

  实现与`unsorted bin`相同，但是大小有明确的规定

- `large bin: size order large -> small`双链表

  子链按照相同大小的`chunk`组织连接，而子链头又按照不同大小，从大到小连接

- `tcache bin: last in first out`单链表

  全称为:`thread local caching`

除`large bin`之外，都是头插法

在上面的`malloc_status`中，需要关注的部分有:

```c
  /* Fastbins */
  mfastbinptr fastbinsY[NFASTBINS];
  /* Normal bins packed as described above */
  mchunkptr bins[NBINS * 2 - 2];
```

- `fastbinsY`:fast bin的管理结构，用于存储不同size的fast bin链表

- `bins`:存放所有size的free chunk，共有127个链表节点，长度不限

  - `bin[0]:unsorted bin`
  - `bin[1] ~ bin[62]: small bin`
  - `bin[63] ~ bin[126]: large bin`

  初始状态时，每个链表节点形成自我闭环，表示链表为空

在使用`malloc`进行分配时，大致流程如下:

```assembly
size rearrange ---> find in tcache bin ---> find in fast bin ---> find in unsorted bin ---> 

find in small bin or large bin ---> use top chunk
```

之后，使用`free`时的大致流程如下:

```assembly
check if insert to tcache ---> check if insert to fast bin ---> check if merge to prev or later ---> check if mmap use munmap
```

### Attack

在`libc-2.34`之前，主要思路为劫持函数指针，例如：

`__malloc_hook, __free_hook,__realloc_hook`

以`malloc.c`中的`__libc_malloc`为例:

```c
void *
__libc_malloc (size_t bytes)
{
  mstate ar_ptr;
  void *victim;

  _Static_assert (PTRDIFF_MAX <= SIZE_MAX / 2,
                  "PTRDIFF_MAX is not more than half of SIZE_MAX");

  void *(*hook) (size_t, const void *)
    = atomic_forced_read (__malloc_hook);
  if (__builtin_expect (hook != NULL, 0))
    return (*hook)(bytes, RETURN_ADDRESS (0));

    ......
    
}
```

因为`free`函数只接受一个指针，并且`system`函数也只接受一个指针参数，所以攻击`__free_hook`是最稳定的

常见的利用点：

- `heap overflow`

  使用溢出的方式，修改其它可能已经释放的堆块的值，以此来申请

- `UAF`

  一般使用该方法来进行信息泄露，打印一个`unsorted bin chunk`的`fd`指针，由此就可以拿到`malloc_state`的地址，其相对于`libc`基地址的偏移是固定的

- `double free`

  一种特殊的`UAF`，针对同一指针进行多次释放，使堆块发生重叠

  ```c
  typedef struct tcache_entry
  {
      struct tcache_entry*next;
  /* This field exists to detect double frees. */
      struct tcache_perthread_struct*key;
  } tcache_entry;
  ```

- `Unlink Attack`

## EX(wiki)

### UAF

#### hacknote

常规的菜单题，但关闭了`pie`，并且其中有后门函数`magic`，所以可以利用该地址，劫持函数指针，调用`system`函数；因为该题不清空链表中的内容，所以可以利用相同索引下的地址，再次调用函数指针

`exp`的基本思路是：先创建`0x10=>(对齐到)0x20`的结构体，再申请`0x20=>0x30`的部分，存放字符串内容，再做同样的操作，这样在`free`时，就可以在`fast bin`中生成`0x20`的`bin`链表，并且第二个`chunk`的地址与`note[0]`相同，所以只需要再创建一个`0x10 => 0x20`的结构体，和`0x08 => 0x20`的内容块，就可以修改`put`函数指针为`magic`

```assembly
chunk 1: struct 1[put1, context1] 16 [0]
chunk 2: context1 32
chunk 3: struct 2[put2, context2] 16 [1]
chunk 4: context2 32
free 1
free 2
free 3
free 4
==> 
fastbinY[0] -> chunk3 -> chunk1
fastbinY[1] -> chunk4 -> chunk2

chunk 3: struct 3[put3, context3] [2]
chunk 1: context3 magic 
show 0
```

#### prac(Author: PIG-007)
