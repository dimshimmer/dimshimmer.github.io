---
layout: post
title: "The way to the kernel of Linux🌏"
date: 2022-10-26 09:50:00+0800
chap: Beginning
---

# The notes🌏

学习操作系统的笔记，探究`Linux`的内核

所有的博客排布大致与上课的进度相同，但会与`linux`的开源内核代码结合，并梳理清代码和整个系统之间的关系

## Overview

- `Batch Processing System`

  `jobs`在内存外或者外存里，内存始终有一个`job`在运行，操作系统负责在结束后加载下一个，在`IO`时停止运行

- `Multiprogramming Batch System`

  在上一个的基础上，当前`job`发生`IO`时，运行另一个`job`

- `Time Sharing System`

  各个`job`轮转运行

现代操作系统都是中断驱动

在中断时，保存和恢复现场状态的过程时不应当被打断的

但低级中断会被高级中断中断

系统调用的功能包括：

- `Process control`
  - `create, terminate`
  - `load, execute`
  - `get process attributes, set process attributes`
  - `wait event, signal event`
  - `allocate and free memory`
- `File management`
  - `create, delete`
  - `open, close`
  - `read, write, reposition`
  - `get file attributes, set file attributes`
- `Device management`
  - `request device, release device`
  - `read, write, reposition`
  - `get deviece attributes, set device sttributes`
  - `logically attach or detach device`
- `Information maintenance`
  - `get or settime or date, `
  - `get, set system data`
  - `get attributes`
  - `set attributes`
- `Communications`
  - `crearte, delete connection`
  - `send, receive message`
  - `transfer status information`
  - `attach or detach remote devices`
- `Protection`
  - `get, set permissions`
