---
Title: Build Mini Linux Distro And Use Qemu Running.
Date: 2025-02-10 12:00
Lang: zh-cn
Category: Qemu
---

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
64-bit kernel
General setup  --->Initial RAM filesystem and RAM disk (initramfs/initrd) support 
General setup  --->Configure standard kernel features (expert users)  --->Enable support for printk 
Executable file formats  --->Kernel support for ELF binaries 
Device Drivers  --->Character devices  --->Enable TTY
```
> 使用 `make -j $(nproc)` 构建, 默认生成的内核镜像在 `arch/x86/boot/bzImage`,为压缩的kernel镜像
> 查看内核镜像的运行 `qemu-system-x86_64 --kernel arch/x86/boot/bzImage`


```python
## 
```
