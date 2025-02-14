# 介绍
这是使用qemu的使用教程, 以构建最小linux发行版为例.
[参nir9博客](https://github.com/nir9/welcome/tree/master)

## 从构建linux内核开始

> **env**
    - linux内核源码 `git clone --depth 1 https://git.kernel.org/
pub/scm/linux/kernel/git/torvalds/linux.git`
    - 依赖包 `apt install bzip2 libncurses-dev flex bison bc cpio libelf-dev libssl-dev syslinux dosfstools`
    - 使用qemu启动编译后的内核 `apt install qemu-system-x86`

**注意** 在linux目录下使用 `make help` 查看帮助, 这里我们使用 `make tinyconfig` 配置尽可能小的内核

> 使用 `make menuconfig` 配置编译make选项, 配置如下:
```
General setup  --->Initial RAM filesystem and RAM disk (initramfs/initrd) support 
General setup  --->Configure standard kernel features (expert users)  --->Enable support for printk 
Executable file formats  --->Kernel support for ELF binaries 
Device Drivers  --->Character devices  --->Enable TTY
```


```python
## 
```
