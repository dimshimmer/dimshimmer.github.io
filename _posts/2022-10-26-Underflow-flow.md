---
layout: post
title: "Underflow flow"
date: 2022-10-26 09:40:00+0800
categories: The_process_of_building_the_blog
---

# The blog

这篇博客会记录这个小破博客的搭建过程，和这个过程中，小菜鸡的成长过程。不知道能更新多久呢:smile:~

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

```shell
│   404.html
│   about.markdown
│   about.md
│   archives.html
│   feed.xml
│   Gemfile
│   Gemfile.lock
│   index.html
│   index.markdown
│   LICENSE
│   README.md
│   _config.yml
│
├───style
│   ├───css
│   │   │   highlight.min.css
│   │   │   style.min.css
│   │   │
│   │   └───iconfont
│   │           iconfont.css
│   │           iconfont.eot
│   │           iconfont.svg
│   │           iconfont.ttf
│   │           iconfont.woff
│   │           iconfont.woff2
│   │
│   ├───image
│   │       bg-ico.png
│   │       favicon.png
│   │       logo.png
│   │       thumbnail.png
│   │
│   └───js
│           headroom.min.js
│           jquery.min.js
│           nav.min.js
│           SmoothScroll.min.js
│
├───_includes
│       comment.html
│       footer.html
│       head.html
│       header.html
│
├───_layouts
│       default.html
│       full.html
│       post.html
│
└───_posts
        ...
```

| 目录             | 描述                                                         |
| ---------------- | ------------------------------------------------------------ |
| _config.yml      | 保存配置数据                                                 |
| _drafts          | 未发布的文章                                                 |
| _includes        | 你可以加载这些包含部分到你的布局或者文章中以方便重用。可以用这个标签 `{% include file.ext %}` 来把文件 `_includes/file.ext` 包含进来。 |
| _layouts         | layouts（布局）是包裹在文章外部的模板。布局可以在 YAML 头信息中根据不同文章进行选择。 这将在下一个部分进行介绍。标签 `{{ content }}` 可以将content插入页面中。 |
| _posts           | 这里放的就是你的文章了。文件格式很重要，必须要符合: `YEAR-MONTH-DAY-title.MARKUP`。  可以在文章中自己定制，但是数据和标记语言都是根据文件名来确定的。 |
| _data            | 格式化好的网站数据应放在这里。`jekyll `的引擎会自动加载在该目录下所有的` yaml` 文件（后缀是 `.yml`, `.yaml`, `.json` 或者 `.csv` ）。这些文件可以经由 `site.data` 访问。如果有一个 `members.yml` 文件在该目录下，你就可以通过 `site.data.members` 获取该文件的内容。 |
| _site            | 一旦 Jekyll 完成转换，就会将生成的页面放在这里（默认）。最好将这个目录放进你的 `.gitignore` 文件中。 |
| .jekyll-metadata | 该文件帮助 Jekyll 跟踪哪些文件从上次建立站点开始到现在没有被修改，哪些文件需要在下一次站点建立时重新生成。该文件不会被包含在生成的站点中。将它加入到你的 `.gitignore` 文件可能是一个好注意。 |
| index.html       | 如果这些文件中包含 YAML 头信息 部分，Jekyll 就会自动将它们进行转换。当然，其他的如 `.html`, `.markdown`, `.md`, 或者 `.textile` 等在你的站点根目录下或者不是以上提到的目录中的文件也会被转换。 |
|                  |                                                              |

先跳过这些比较繁琐的概念，从比较重要的博客部分开始看起，以上的详细部分，在遇到了有关的问题之后，再深入学习

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

