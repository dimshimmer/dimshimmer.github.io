---
layout: post
title: "Scheduling"
date: 2022-10-26 10:16:00+0800
lesson: Scheduling
---

# Scheduling

大多数的进程都要切换在`CPU`和`IO`之间，其中的速度限制分为:

- I/O-bound

  绝大部分需要等待 I/O

  许多都要等待CPU释放

- CPU-bound

  大部分都要等待CPU

  很少的I/O发生

目前的CPU Schedule:

- 非抢占:Non-:Preemptive
- 抢占:Preemptive

#1: RUNNING -> WAITING

#2: RUNNING -> READY

#3: WAITING -> READY

#4: RUNNING -> THERMINATED

#5: NEW -> READY

目前的调度都是抢占式的

常见的调度算法：

- First come, First Served

  Convoy effect:“押镖”

- Shortest Job First

  ```
  p1 = 15
  p2 = 2
  p3 = 6
  p4 = 0
  ave = 8.25
  ```

- Round-Robin

  