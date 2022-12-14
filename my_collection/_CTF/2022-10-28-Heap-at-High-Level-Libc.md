---
layout: post
title: "Heap at High Level Libcð©"
date: 2022-10-28 10:45:00+0800
chap: level_1
---

# Pwn-Heapð©

ä½ä¸ºè¿ä¸ªä¸æ çå¼ç¯ï¼å³å®ååä¸åï¼`pwn`éé¢ï¼é«çæ¬ä¸`libc`çç¹æ§ä»¥åå¯è½å­å¨çæ¼æ´å©ç¨(ç«å¨ä»åå¸åçè©èä¸)ãä¹åéå°çä¸ä¸ªé¢ç®å°è±¡å®å¨æ¯å¤ªæ·±äºï¼å¨éé¢ç¢°å°äºè¿æ ·çé®é¢ï¼è½å¨å¼ç¯éæè¿ä¸ªé®é¢æ¢³çå¥½å­¦ä¹ å¥½ï¼ä¹æ¯ä»¶å¾ææå°±æçäºæå§

## Description

è¿ç¨é¶æºæä¾ç`libc`çæ¬æ¯ä½äº`2.34`çï¼èå¨æ¬å°ç`ubuntu 22.04`ä¸­ï¼å·²ç»å¨ä½¿ç¨`libc 2.43`åä»¥ä¸äºï¼æä»¥å¨æ¬å°åè¿ç¨åºç°çç°è±¡ï¼æ»æ¯ä¼æåå·®ï¼è±äºå¾é¿çæ¶é´å»è§£å³ï¼æä»¥æ³è¦æ¢³çä¸ä¸çæ¬é´çä¸åï¼å­¦ä¹ æ´å¤çï¼`heap`ç¸å³çæ¼æ´å©ç¨æ¹æ³

## Before

é¦åï¼å¨`Linux`ç¯å¢ä¸ï¼å éè¿`ptmalloc2`æ¥ç®¡çï¼éè¿å ä¸ªå®éªå`gdb`çè·è¸ªï¼æ¥ç ç©¶`heap`çè¿è¡æºå¶ï¼

```shell
# é¦åæ¥çè¯¥ç¯å¢ä¸çglibcççæ¬:
$ ls -l /lib/x86_64-linux-gnu/libc.so.6
lrwxrwxrwx 1 root root 12 Apr  7  2022 /lib/x86_64-linux-gnu/libc.so.6 -> libc-2.31.so
```

ä¸è¬æä»¬ä½¿ç¨å°çåéï¼å¦æå­å¨äºå½æ°ä¸­ï¼é½æ¯åéå°æ ä¸çä¸´æ¶åéï¼èå³äºå ï¼å¨ä½¿ç¨`malloc`å½æ°å¨æåéç©ºé´æ¶ï¼éè¦ä»å ä¸­åå¾åå­ï¼åéç»ç¨åºä¸­è¦ç¨å°çæéï¼ä¹å°±æ¯è¯´ï¼è¿ä¸é¨åçå°åæ¯å­å¨äºå ä¸ï¼

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

è¿è¡è§å¯ï¼

```shell
$ ./test 
the address of buf: 0x7ffcf2b2662e
the address of buf_h: 0x558af36962a0
#ç»ågdbï¼è§å¯åå­çåå¸ï¼
gefâ¤  vmm
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
#å¨è°ç¨äºmallocä¹å:
==>
gefâ¤  vmm
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

å¯ä»¥çå°ï¼äºèçå°åç¸å·®æ¯æ¯è¾å¤§çï¼å¹¶ä¸ï¼å¨è°ç¨äº`malloc`å½æ°åï¼èæå°åä¸ï¼æåºç°``[heap]``çæ è¯ï¼å¹¶ä¸å¤§å°ä¸º`0x21000`ï¼å¹¶ä¸å°åæ¯å¨å¯æ§è¡ä»£ç çæ­£ä¸æ¹

åä½¿ç¨ç®åçç¨åºè¿è¡å®éª:

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

ä½¿ç¨`gdb`è°è¯æ¥çï¼

```shell
#é¦åæ¥çæªåéåå­æ¶ï¼heapä¸çbinçæåµï¼
gefâ¤  heap bins
[!] No heap section
[+] Uninitialized tcache for thread 1
âââââââââââ Fastbins for arena at 0x7ffff7fb8b80 âââââââââââââââ
Fastbins[idx=0, size=0x20] 0x00
Fastbins[idx=1, size=0x30] 0x00
Fastbins[idx=2, size=0x40] 0x00
Fastbins[idx=3, size=0x50] 0x00
Fastbins[idx=4, size=0x60] 0x00
Fastbins[idx=5, size=0x70] 0x00
Fastbins[idx=6, size=0x80] 0x00
ââââââââââââ Unsorted Bin for arena at 0x7ffff7fb8b80 ââââââââââââ
[*] Invalid backward and forward bin pointers(fw==bk==NULL)
ââââââââââââ Small Bins for arena at 0x7ffff7fb8b80 ââââââââââââââ
[+] Found 0 chunks in 0 small non-empty bins.
ââââââââââââ Large Bins for arena at 0x7ffff7fb8b80 ââââââââââââââ
[+] Found 0 chunks in 0 large non-empty bins.
#å¹¶ä¸æ­¤æ¶æ ä»»ä½chunk

#å¨åéäºä¸ä¸ªå¤§å°ä¸º0çchunkä¹åï¼
gefâ¤  heap chunks
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
    [0x0000555555559010        ................]
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
    [0x00005555555592a0         ................]
Chunk(addr=0x5555555592c0, size=0x20d50, flags=PREV_INUSE)
    [0x00005555555592c0         ................]
Chunk(addr=0x5555555592c0, size=0x20d50, flags=PREV_INUSE)  â  top chunk
#åéäºå¤§å°ä¸º0x20çchunkå:
gefâ¤  heap chunks
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
    [0x0000555555559010        ................]
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
    [0x00005555555592a0         ................]
Chunk(addr=0x5555555592c0, size=0x30, flags=PREV_INUSE)
    [0x00005555555592c0         ................]
Chunk(addr=0x5555555592f0, size=0x20d20, flags=PREV_INUSE)
    [0x00005555555592f0         ................]
Chunk(addr=0x5555555592f0, size=0x20d20, flags=PREV_INUSE)  â  top chunk
#å¨é¨åéå®åï¼
gefâ¤  heap chunks
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
Chunk(addr=0x55555555d2b0, size=0x1cd60, flags=PREV_INUSE)  â  top chunk
#ç¬¬ä¸æ¬¡è°ç¨freeåï¼
gefâ¤  heap bins
âââââââ Tcachebins for thread 1 ââââââââââ
Tcachebins[idx=0, size=0x20, count=1] â  Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
#å¨é¨freeï¼
gefâ¤  heap bins
ââââââââ Tcachebins for thread 1 ââââââââââââ
Tcachebins[idx=0, size=0x20, count=1] â  Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE) 
Tcachebins[idx=3, size=0x50, count=1] â  Chunk(addr=0x5555555592f0, size=0x50, flags=PREV_INUSE) 
Tcachebins[idx=7, size=0x90, count=1] â  Chunk(addr=0x5555555593b0, size=0x90, flags=PREV_INUSE) 
Tcachebins[idx=11, size=0xd0, count=1] â  Chunk(addr=0x5555555594f0, size=0xd0, flags=PREV_INUSE) 
Tcachebins[idx=15, size=0x110, count=1] â  Chunk(addr=0x5555555596b0, size=0x110, flags=PREV_INUSE) 
Tcachebins[idx=19, size=0x150, count=1] â  Chunk(addr=0x5555555598f0, size=0x150, flags=PREV_INUSE) 
Tcachebins[idx=23, size=0x190, count=1] â  Chunk(addr=0x555555559bb0, size=0x190, flags=PREV_INUSE) 
Tcachebins[idx=27, size=0x1d0, count=1] â  Chunk(addr=0x555555559ef0, size=0x1d0, flags=PREV_INUSE)
#chunks:
Chunk(addr=0x555555559010, size=0x290, flags=PREV_INUSE)
    [0x0000555555559010     01 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00    ]
Chunk(addr=0x5555555592a0, size=0x20, flags=PREV_INUSE)
    [0x00005555555592a0     00 00 00 00 00 00 00 00 10 90 55 55 55 55 00 00    ]
Chunk(addr=0x5555555592c0, size=0x30, flags=PREV_INUSE)
    [0x00005555555592c0     00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ]
Chunk(addr=0x5555555592f0, size=0x50, flags=PREV_INUSE)
    [0x00005555555592f0     00 00 00 00 00 00 00 00 10 90 55 55 55 55 00 00    ]
# free åçmallocï¼
gefâ¤  heap bins
âââââââââââ Tcachebins for thread 1 âââââââââ
Tcachebins[idx=15, size=0x110, count=1] â  Chunk(addr=0x5555555596b0, size=0x110, flags=PREV_INUSE) 
Tcachebins[idx=19, size=0x150, count=1] â  Chunk(addr=0x5555555598f0, size=0x150, flags=PREV_INUSE) 
Tcachebins[idx=23, size=0x190, count=1] â  Chunk(addr=0x555555559bb0, size=0x190, flags=PREV_INUSE) 
Tcachebins[idx=27, size=0x1d0, count=1] â  Chunk(addr=0x555555559ef0, size=0x1d0, flags=PREV_INUSE)
```

è§å¯å¶ä¸­å¼å¾æ³¨æçå°æ¹ï¼

-  chunkå°åæä½çé¨åæ²¡æè¢«åéï¼å¶ä¸­åå«äºä»ä¹æ°æ®
- åéåºçchunkçsizeä¸ä»£ç ä¸­ååºçå¤§å°ä¸ç¬¦
- å¶å®çbinæ²¡æè¢«ä½¿ç¨

ä»ä»¥ä¸å®éåºç°çæåµåºåï¼å­¦ä¹ `malloc`å`free`çåçï¼å¹¶ç»åæºç ï¼äºè§£å¶ä¸­çæ°æ®ç»æ

## Heap

### Arena

å¨`glibc`ä¸­ï¼åå§çå ç©ºé´ç±`brk`ç³»ç»è°ç¨äº§çï¼å¯ä»¥å¨ä¸é¢çå®éªä¸­çå°ï¼å¨ç¬¬ä¸æ¬¡ç³è¯·ç©ºé´ä¹åï¼å¹¶ä¸ä¼åºç°å¯¹åºçå ç©ºé´ï¼å¨ç¬¬ä¸æ¬¡`malloc`ä¹åï¼æä¼åºç°å¯¹åºçåå­ç©ºé´

å¦æç¬¬ä¸æ¬¡ç³è¯·åºçå ç©ºé´ä¸å¤å¤§ï¼åä¼ç»§ç»­è°ç¨`brk`ç³»ç»ï¼æ¥æ©å±å ç©ºé´ï¼å½åæ¬¡åéç©ºé´è¿å¤§ï¼åä½¿ç¨`mmap`ï¼æ¥åå»ºå¿åæ å°æ®µä¾ç¨æ·ä½¿ç¨

> brk:**éå¸¸å°å çå½ååå­è¾¹çç§°ä¸ºâProgram brak"ç®ç§°ä¸ºbrkï¼brkç¨äºè®°å½çæ¯å½åå å·²ç»åéä½¿ç¨çç»æå°åï¼å³æªä½¿ç¨åéçèµ·å§å°åï¼ã**
>
> mmap:mmap() ç³»ç»è°ç¨è½å¤å°æä»¶æ å°å°åå­ç©ºé´ï¼ç¶åå¯ä»¥éè¿è¯»ååå­æ¥è¯»åæä»¶

åå¯¹å çæ¦å¿µåä¸ä¸ªæ»æ¦ï¼

`arena`ï¼æ¯å åå­æ¬èº«

- ä¸»çº¿ç¨ç`main_arena`

  æå¼å§è°ç¨`sbrk`å½æ°åå»ºå¤§å°ä¸º(128 KB + `chunk_size`) align 4KBçç©ºé´ä½ä¸º`heap`

  ä½¿ç¨`sbrk`æ`mmap`å¢å å¤§å°

- å¶ä»çº¿ç¨ç`arena`

  æå¼å§è°ç¨`mmap`æ å°ä¸åå¤§å°ä¸º`HEAP_MAX_SIZE`çç©ºé´(64ä½ç³»ç»ä¸é»è®¤ä¸º64MB)ï¼ä½ä¸ºsub-heap

  ä½¿ç¨`mmap`å¢å `top chunk`çå¤§å°

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



`chunk`ä½ä¸º`heap`åéçåºæ¬åä½ï¼åç`malloc.c`ä¸­çæ°æ®ç»æï¼

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
//glibc 2.34ä¸ä¹åççæ¬ç¸æ¯ï¼æ åå
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

å¨glibcä¸­ï¼å¯¹é½ç±malloc.cä¸­çrequest2sizeå®å®ç°ãå¯ä»¥ç®åå°è¯¥æä½çè§£ä¸ºä¸è¡¨ä¸­çæ å°ï¼å³ï¼

å®ésize = è¯·æ±çsize+8åå¯¹åºçä¸ä¸ä¸ª0x10å¯¹é½çå¼

| è¯·æ±å¤§å°    | å®éåéå¤§å° |
| ----------- | ------------ |
| 0x00 ~ 0x18 | 0x20         |
| 0x19 ~ 0x28 | 0x30         |
| 0x29 ~ 0x38 | 0x40         |
| ...         | ...          |
| 0xE9 ~ 0xF8 | 0x100        |
| ...         | ...          |

### Bin

å¨å é¢ä¸­ï¼æå¸¸è¢«å©ç¨å°çï¼æ¯`bin`é¨åï¼æ¯å ç©ºé²åçç®¡çç»æï¼æ¯ç±`free chunk`ç»æçé¾è¡¨ï¼ä¸»è¦çä½ç¨æ¯å å¿«åééåº¦ï¼åä¸ºä»¥ä¸å ç±»ï¼

- `fast bin: last in first out `åé¾è¡¨

  å°å°`chunk`(å¤§å°èå´ä¸º[0x20, 0x80])åç¬ç®¡çï¼ä»¥ååé¾è¡¨çå½¢å¼ç»ç»èµ·æ¥ï¼é¾è¡¨é¿åº¦ä¸éï¼åªæ¯ç¨`fd` è¿æ¥ï¼ä¸éç¨`bk`å­æ®µ

  ```assembly
  fastbinY[0] --- fd ---> [chunk 0x20] --- fd ---> [chunk 0x20] --- fd ---> NULL
  ....
  fastbinY[6] --- fd ---> [chunk 0x80] --- fd ---> NULL
  ```

- `unsorted bin: first in first out`åé¾è¡¨

  å¤§å°æ²¡æé¡ºåºï¼ä»»ä½`size`ç`chunk`é½å¯ä»¥è¢«æ¾å¥è¯¥`bin`ä¸­

  ```assembly
  |---------------------------------->|bins[0]|-------------------------------------------|
  | |---------------------------------|       |<--------------- fd --------------------|  |
  | |                                                                                  |  |
  | |--- fd ----->|chunk| ---- fd --->|chunk| ---- fd -->     ---- fd --->|chunk|------|  |
  |---- bk -------|0x1a0| <--- bk --- |0x20 | <--- bk --- ... <--- bk --- |0x500|<--------| 
  ```

- `small bin: first in first out`åé¾è¡¨

  å®ç°ä¸`unsorted bin`ç¸åï¼ä½æ¯å¤§å°ææç¡®çè§å®

- `large bin: size order large -> small`åé¾è¡¨

  å­é¾æç§ç¸åå¤§å°ç`chunk`ç»ç»è¿æ¥ï¼èå­é¾å¤´åæç§ä¸åå¤§å°ï¼ä»å¤§å°å°è¿æ¥

- `tcache bin: last in first out`åé¾è¡¨

  å¨ç§°ä¸º:`thread local caching`

é¤`large bin`ä¹å¤ï¼é½æ¯å¤´ææ³

å¨ä¸é¢ç`malloc_status`ä¸­ï¼éè¦å³æ³¨çé¨åæ:

```c
  /* Fastbins */
  mfastbinptr fastbinsY[NFASTBINS];
  /* Normal bins packed as described above */
  mchunkptr bins[NBINS * 2 - 2];
```

- `fastbinsY`:fast binçç®¡çç»æï¼ç¨äºå­å¨ä¸åsizeçfast biné¾è¡¨

- `bins`:å­æ¾ææsizeçfree chunkï¼å±æ127ä¸ªé¾è¡¨èç¹ï¼é¿åº¦ä¸é

  - `bin[0]:unsorted bin`
  - `bin[1] ~ bin[62]: small bin`
  - `bin[63] ~ bin[126]: large bin`

  åå§ç¶ææ¶ï¼æ¯ä¸ªé¾è¡¨èç¹å½¢æèªæé­ç¯ï¼è¡¨ç¤ºé¾è¡¨ä¸ºç©º

å¨ä½¿ç¨`malloc`è¿è¡åéæ¶ï¼å¤§è´æµç¨å¦ä¸:

```assembly
size rearrange ---> find in tcache bin ---> find in fast bin ---> find in unsorted bin ---> 

find in small bin or large bin ---> use top chunk
```

ä¹åï¼ä½¿ç¨`free`æ¶çå¤§è´æµç¨å¦ä¸:

```assembly
check if insert to tcache ---> check if insert to fast bin ---> check if merge to prev or later ---> check if mmap use munmap
```

### Attack

å¨`libc-2.34`ä¹åï¼ä¸»è¦æè·¯ä¸ºå«æå½æ°æéï¼ä¾å¦ï¼

`__malloc_hook, __free_hook,__realloc_hook`

ä»¥`malloc.c`ä¸­ç`__libc_malloc`ä¸ºä¾:

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

å ä¸º`free`å½æ°åªæ¥åä¸ä¸ªæéï¼å¹¶ä¸`system`å½æ°ä¹åªæ¥åä¸ä¸ªæéåæ°ï¼æä»¥æ»å»`__free_hook`æ¯æç¨³å®ç

å¸¸è§çå©ç¨ç¹ï¼

- `heap overflow`

  ä½¿ç¨æº¢åºçæ¹å¼ï¼ä¿®æ¹å¶å®å¯è½å·²ç»éæ¾çå åçå¼ï¼ä»¥æ­¤æ¥ç³è¯·

- `UAF`

  ä¸è¬ä½¿ç¨è¯¥æ¹æ³æ¥è¿è¡ä¿¡æ¯æ³é²ï¼æå°ä¸ä¸ª`unsorted bin chunk`ç`fd`æéï¼ç±æ­¤å°±å¯ä»¥æ¿å°`malloc_state`çå°åï¼å¶ç¸å¯¹äº`libc`åºå°åçåç§»æ¯åºå®ç

- `double free`

  ä¸ç§ç¹æ®ç`UAF`ï¼éå¯¹åä¸æéè¿è¡å¤æ¬¡éæ¾ï¼ä½¿å ååçéå 

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

å¸¸è§çèåé¢ï¼ä½å³é­äº`pie`ï¼å¹¶ä¸å¶ä¸­æåé¨å½æ°`magic`ï¼æä»¥å¯ä»¥å©ç¨è¯¥å°åï¼å«æå½æ°æéï¼è°ç¨`system`å½æ°ï¼å ä¸ºè¯¥é¢ä¸æ¸ç©ºé¾è¡¨ä¸­çåå®¹ï¼æä»¥å¯ä»¥å©ç¨ç¸åç´¢å¼ä¸çå°åï¼åæ¬¡è°ç¨å½æ°æé

`exp`çåºæ¬æè·¯æ¯ï¼ååå»º`0x10=>(å¯¹é½å°)0x20`çç»æä½ï¼åç³è¯·`0x20=>0x30`çé¨åï¼å­æ¾å­ç¬¦ä¸²åå®¹ï¼åååæ ·çæä½ï¼è¿æ ·å¨`free`æ¶ï¼å°±å¯ä»¥å¨`fast bin`ä¸­çæ`0x20`ç`bin`é¾è¡¨ï¼å¹¶ä¸ç¬¬äºä¸ª`chunk`çå°åä¸`note[0]`ç¸åï¼æä»¥åªéè¦ååå»ºä¸ä¸ª`0x10 => 0x20`çç»æä½ï¼å`0x08 => 0x20`çåå®¹åï¼å°±å¯ä»¥ä¿®æ¹`put`å½æ°æéä¸º`magic`

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
