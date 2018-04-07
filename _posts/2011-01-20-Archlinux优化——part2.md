---
title: "Archlinux优化——part2"
date: 2011-01-20
category: Linux
tags: Archlinux
layout: post
---

### 3. 开机速度优化
参考文献： [https://wiki.archlinux.org/index.php/Improve_Boot_Performance](https://wiki.archlinux.org/index.php/Improve_Boot_Performance)

**a. rc.conf：禁用不需要的开机服务，以及后台启动服务**
         介绍：Archlinux默认开机会加载一些服务，诸如cups、crond，可以根据需要关闭一些服务。
         操作：
             用编辑器打开*/etc/rc.conf*，找到如下部分：
                 *DAEMONS=(服务1 服务2 …… 服务n)*
             服务名前加“!”禁止服务自动启动，加“@”开机时后台启动服务（下面只是例子）：
                 *DAEMONS=(dbus hal gdm @syslog-ng @network !netfs @crond @alsa !cups)*
             TIPS：如果不用打印机，可以关闭cups；如果不用网络文件系统，可以关闭netfs。
                 hal、dbus等关键服务建议放在最前面，且不要后台启动，然后是登陆管理器（gdm、kdm、slim），其他的都可以后台启动。

**b. inittab：乱序执行启动脚本**
         介绍：Linux开机时执行的脚本，默认是顺序一个个执行的，可以通过一起同步执行加速。
         操作：
             用编辑器打开*/etc/inittab*，找到如下部分：
 *rc::sysinit:/etc/rc.sysinit*
                 *rs:S1:wait:/etc/rc.single*
                 *rm:2345:wait:/etc/rc.multi*
                 *rh:06:wait:/etc/rc.shutdown*
                 *su:S:wait:/sbin/sulogin -p*
             将其中的wait全部改成once（rc.sysinit不要动）：
 *rc::sysinit:/etc/rc.sysinit*
                 *rs:S1:once:/etc/rc.single*
                 *rm:2345:once:/etc/rc.multi*
                 *rh:06:once:/etc/rc.shutdown*
                 *su:S:once:/sbin/sulogin -p*
             保存即可。
            
**c. inittab：减少控制台数量，节省系统资源**
         介绍：Archlinux默认开6个tty控制台（Ctrl+Alt+F1~6），通常我们根本用不了这么多。
         操作：
             用编辑器打开*/etc/inittab*，找到如下部分：
 *c1:2345:respawn:/sbin/agetty -8 38400 tty1 linux*
                 *c2:2345:respawn:/sbin/agetty -8 38400 tty2 linux*
                 *c3:2345:respawn:/sbin/agetty -8 38400 tty3 linux*
                 *c4:2345:respawn:/sbin/agetty -8 38400 tty4 linux*
                 *c5:2345:respawn:/sbin/agetty -8 38400 tty5 linux*
                 *c6:2345:respawn:/sbin/agetty -8 38400 tty6 linux*
             将不需要的控制台用“#”注释掉：
*#c6:2345:respawn:/sbin/agetty -8 38400 tty6 linux*
             保存即可。
         其他：
             还可以安装fgetty或者mingetty代替agetty，它们比较轻量，节省资源。
             以fgetty为例，安装后把inittab的上述行替换为：
 *c1:2345:respawn:/sbin/fgetty tty1 linux*
                 *c2:2345:respawn:/sbin/fgetty tty2 linux*
             等等，保存重启即可。
            
**d. rc.sysinit：调整开机脚本**
         介绍：跳过模块依赖性检查等费时的操作。有一定风险，请备份文件。
         操作：
             用文本编辑器打开*/etc/rc.sysinit*，找到这一行（检查模块依赖）：
*status "Updating Module Dependencies" /sbin/depmod -A*
             注释掉：
*#status "Updating Module Dependencies" /sbin/depmod -A*
             另外，检查这一行：
*status "Updating Shared Library Links" /sbin/ldconfig*
             默认应该是注释掉的，如果没有，你也可以注释掉它。
         其他：
             如果你明白开机脚本的意思，也可以自己做一些调整。不过一定要给自己留后路，修改开机脚本可能导致无法开机！
