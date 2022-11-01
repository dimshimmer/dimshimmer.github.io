---
layout: post
title: "Structure"
date: 2022-10-31 19:55:00+0800
chap: level_1
---

# Structure🎃

这一部分，要整理清楚`collections`中各部分的关系，以及一些元数据在`jekyll`解析过程中起到的作用，目标是使得生成的静态网页的不同博文，有以下的文件结构：

```shell
/my_collection/*the comllection*
 	|-----index.heml
 	|
 	|-----title_1.md
 	|-----title_2.md
 	|....
```

并且做好不同类别下的`index.heml`的统一模板，使文件之间的引用关系`_layout和include`尽可能简洁一些；整理好博文列表，显示必要的信息；如果有可能的话，尝试规定好每类博文的模板和`metadata`，使得信息尽可能地完整，并且能显示出不同类别之间的区别；最后，解决上次留下的，单个博文悬浮目录的问题，开工