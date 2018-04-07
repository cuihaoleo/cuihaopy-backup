---
title: "Archlinux优化——part1"
date: 2011-01-15
category: Linux
tags: Archlinux Firefox
layout: post
---

### **1. 从Firefox做起**
作为绝大多数linuxer首选浏览器，Arch的提速从此说起。
     参考文献： [https://wiki.archlinux.org/index.php/Firefox_Tips_and_Tweaks](https://wiki.archlinux.org/index.php/Firefox_Tips_and_Tweaks)
    
     **a. 利用tmpfs加快缓存**
         介绍：就是把缓存放在内存里。
         操作：
             在浏览器地址栏输入“*about:config*”。
             找到（或新建）string项目“*browser.cache.disk.parent_directory*”。
             设置为“*/dev/shm/ffcache*”。
         其他：内存紧张的就不要用了。关机或重启后缓存不会保留（因为存在内存里了）。
        
     **b. 关闭pango**
         介绍：据说这玩意儿没啥用，还拖累速度。
         操作：
             用文本编辑器打开“*~/.profile*”。
             添加一行“*export MOZ_DISABLE_PANGO=1*”。
            
     **c. 优化版的firefox**
         介绍：PGO优化版的firefox。
         操作：
             AUR中，请自行编译（sorry，不提供新人指导）：
             FF3: [http://aur.archlinux.org/packages.php?ID=22296](http://aur.archlinux.org/packages.php?ID=22296)
             FF4: [http://aur.archlinux.org/packages.php?ID=22919](http://aur.archlinux.org/packages.php?ID=22919)
         其他：编译需要比较长时间。



### **2. pacman提速**
首先，pacman默认的下载工具是单线程的。还有众所周知，pacman在开机后第一两次使用时数据库检索速度特别慢。尽管有pacman-optimize这个工具，但每次开机运行一次实在麻烦。
     参考文献： [https://wiki.archlinux.org/index.php/Improve_Pacman_Performance](https://wiki.archlinux.org/index.php/Improve_Pacman_Performance)
    
     **a. 选择合适的服务器**
         介绍：官方服务器带宽有限，下载巨慢。
         操作：
             用文本编辑器打开“*/etc/pacman.d/mirrorlist*”。
             用“#”注释掉官方源（“*Server = ftp://mirrors.kernel.org/archlinux/$repo/os/$arch*”）。
             在China下面选择一个合适的服务器，去掉前面的“#”。
             保存后执行“*pacman -Sy*”同步。
    
     **b. 使用其他下载工具**
         介绍：用axel、aria2c、proz……为下载提速。
         操作：
             首先请确保你安装过这些下载工具。
             然后用文本编辑器打开“/etc/pacman.conf”，找到“XferCommand”打头的行，用“#”注释掉。
             根据实际添加下面的行（链接数等配置请自行修改）：
             ——axel “*XferCommand = /usr/bin/axel -o %o %u*”
             ——aria2c “*XferCommand = /usr/bin/aria2c -o %o %u*”
             ——proz ”*XferCommand = /usr/bin/proz -r --no-curses --no-netrc %u %o*“
             保存后使用pacman测试效果。
         其他：community仓库提供了一个powerpill软件包，也可以达到提速目的，参阅：[https://wiki.archlinux.org/index.php/Powerpill](https://wiki.archlinux.org/index.php/Powerpill) 。
  
     **c. 利用pacman-cage优化本地数据库**
         介绍：单独把pacman数据库放在一个虚拟磁盘文件中，大大加快访问。
         操作：
             到aur下载并安装pactools： [http://aur.archlinux.org/packages.php?ID=5907](http://aur.archlinux.org/packages.php?ID=5907) 。
             以管理员身份运行”*pt-pacman-cage 60*“，会创建一个叫做/var/lib/pacman.db的loop文件系统，并备份数据库。
             检查/etc/fstab文件，应该有（若无请添加）类似下面的内容：
                 */var/lib/pacman.db /var/lib/pacman ext2 loop,defaults,noatime,nodiratime 0 0*
