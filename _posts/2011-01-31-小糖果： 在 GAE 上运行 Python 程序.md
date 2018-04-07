---
title: "小糖果： 在 GAE 上运行 Python 程序"
date: 2011-01-31
category: Programming
tags: Python GAE
layout: post
---

Here： [Run .py at GAE](/web/20150625095009/http://cuihaopy.appspot.com/runpyatgae)

用exec运行输入的Python程序，输入脚本代码点执行即可。

函数、全局变量什么的都需要global修饰一下才能使用。没有关闭调试信息，所以出错了可以看看怎么回事。GAE限制了些python标准模块，不是所有的函数都可用。



下面是一个关于[collatz问题](http://zh.wikipedia.org/zh-cn/%E8%80%83%E6%8B%89%E5%85%B9%E7%8C%9C%E6%83%B3)的小脚本，

```python
global collatz

def collatz(n):
    print n
    if n>1:
        if n%2==0:
            collatz(3*n + 1)
        else:
            collatz(n / 2)

    collatz(100)
```
