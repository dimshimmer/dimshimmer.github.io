---
layout: post
title: "Scheduling"
date: 2022-10-26 10:16:00+0800
categories: The process of learning the kernel of Linux
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