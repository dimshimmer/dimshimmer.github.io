---
layout: post
title: "Underflow flow"
date: 2022-10-26 09:40:00+0800
level: level_0
---

* TOC
{:toc}


# The blog

这篇博客会记录这个小破博客的搭建过程，和这个过程中，小菜鸡的成长过程。不知道能更新多久呢~:smirk:



## First thing first

首先要学习使用搭建的工具及其内在联系，理清楚其中的工作结构，把大致的框架梳理明白，再深入学习，来一步步完善和巩固

### Git Page
这一部分比较简单，其实只是GitHub上的一个仓库，可以被用来部署静态网页，随着代码的更新来自动重新部署，并且有一个免费的域名

ps：静态网页和动态网页

- 静态网页：

  纯粹的`HTML`格式，没有后台数据库、不含程序和不可交互的网页

- 动态网页：

  基本的`HTML`语法规范与`PHP`、`Java`、`python`等程序语言、数据库等多种技术的融合，可以动态、交互式的管理网站，可以根据不同需求，生成不同的内容

### Jekyll

这一部分就非常陌生了，是第一次接触，并且之前甚至也没有接触过很多的`web`编程，需要慢慢啃官方的文件，还有其他大牛们写的技术贴，一点点学习了

首先，`jekyll`是一个简单的博客形态的静态站点生产机器，有一个模板目录，通过比如`markdown`的转换器和`Liquid`渲染器转化成一个完整的可发布的静态网站

加入模板后的目录结构以及文件是：



先跳过这些比较繁琐的概念，从比较重要的博客部分开始看起，以上的详细部分，在遇到了有关的问题之后，再深入学习

#### Liquid

**Logically control**

因为该模板语言，与`Jekyll`已基本绑定，在该工程中，几乎全部用到了该语言，做有关的处理

代码本身支持两种标签类型：

- `{ { content } }`输出内容到页面

- `{% if condition == true %}`控制逻辑

  `{% endif%}`

每个逻辑控制的代码块结束后，必须跟一个表示结束的声明

**Filter**

基本语法：`{{"内容" | keyword}}`

- `{{ "uppercase" | upcase }}` = UPPERCASE



### Blog

#### Head

任何包含`YAML`头信息的文件，都会在`jekyll`中，被当作一个特殊的文件来处理，可以在当中设置预定义的变量，甚至是自己定义的变量

| 变量名称    | 描述                                                         |
| ----------- | ------------------------------------------------------------ |
| `layout`    | 如果设置的话，会指定使用该模板文件。指定模板文件时候不需要文件扩展名。模板文件必须放在 `_layouts` 目录下。 |
| `permalink` | 如果你需要让你发布的博客的 URL 地址不同于默认值 `/year/month/day/title.html`，那你就设置这个变量，然后变量值就会作为最终的 URL 地址。 |
| `published` | 如果你不想在站点生成后展示某篇特定的博文，那么就设置（该博文的）该变量为 false。 |

#### Contents

创建文章的目录

在引用一些图片和其它的资源时，可以在工程的根目录下创建一个文件夹，将下载好的图片或其它资源放到该文件夹中，使用`site.url`变量来引用：

```markdown
the picture followed:
![picture]({{ site.url }}/assets/screenshot.jpg)
```



小实验

```c
char*p = (char*)& anything;
int i = 5;
while(i--) tranverse_the_byte(p[i]);
```



## Second thing second

### Arrange the Structure of the blogs



### Support MarkDown Randering

