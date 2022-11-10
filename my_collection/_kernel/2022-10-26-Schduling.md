---
layout: post
title: "Scheduling🕐"
date: 2022-10-26 10:16:00+0800
chap: Scheduling
---

# Scheduling🕐

大多数的进程都要切换在`CPU`和`IO`之间，其中的速度限制分为:

- I/O-bound

  绝大部分需要等待 I/O

  很少的CPU发生

- CPU-bound

  大部分都要等待CPU

  很少的I/O发生

目前的CPU Schedule:

- 非抢占:Non-:Preemptive
- 抢占:Preemptive

#1: RUNNING -> WAITING

#2: RUNNING -> READY(在non-preemptive中不可能发生)

#3: WAITING -> READY

#4: RUNNING -> THERMINATED

#5: NEW -> READY

目前的调度都是抢占式的

调度的目标：

- CPU使用率
- 提高吞吐量
- 减少轮询时间
- 减少等待时间
- 减少响应时间

常见的调度算法：

- First come, First Served

  Convoy effect:“押镖”

- Shortest Job First

  - Non-preemptive
  - Preemptive
  
  局限：在实际的情况下，基本是不知道要运行多长时间的
  
- Round-Robin

- Priority 

- Multilevel Queue

  有多个不同级别优先级的队列

  CPU分配到不同队列上的时间不同

- Multilevel Feedback Queue 

  进程可以在不同级别的队列之间移动

不同系统下的`scheduling`:

- Win XP Scheduling

  不同的优先级，数字越大的，优先级越高

- Linux

  数越小，优先级越高

  `nice`越大，`priority`越大：`pri(new) = pri(old) + nice`

```c
while (1) {
		c = -1;
		next = 0;
		i = NR_TASKS;
		p = &task[NR_TASKS];
		while (--i) {
			if (!*--p)
				continue;
			if ((*p)->state == TASK_RUNNING && (*p)->counter > c)
				c = (*p)->counter, next = i;
		}
		if (c) break;
		for(p = &LAST_TASK ; p > &FIRST_TASK ; --p)
			if (*p) (*p)->counter = ((*p)->counter >> 1) +(*p)->priority;
}
switch_to(next);
```



