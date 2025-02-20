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

**env**
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
> 使用 `make -j $(nproc)` 构建, 默认生成的内核镜像在 `arch/x86/boot/bzImage`,为压缩的kernel镜像,约780K
> 查看内核镜像的运行 `qemu-system-x86_64 --kernel arch/x86/boot/bzImage`

**注意** 此时qemu启动kernel会报 `not working init found`, 应为没有准备启动初始程序

## 构建一个mini-shell
上述步骤中, 我们完成了一个轻量式的linux-kernel构建,接下来准备构建一个轻量的shell来作为init程序
```c
// shell.c
#include <unistd.h>
#include <sys/wait.h>

int real_waitid(idtype_t idtype, id_t id, siginfo_t *infop, int options, void*);

int main()
{
	char command[255];
	for (;;) {
		write(1, "# ", 2);
		int count = read(0, command, 255);
		// /bin/ls\n -> /bin/ls\0
		command[count - 1] = 0;
		pid_t fork_result = fork();
		if (fork_result == 0) {
			execve(command, 0, 0);
			break;
		} else {
			// wait
			// 
			siginfo_t info;
			real_waitid(P_ALL, 0, &info, WEXITED, 0);
		}
	}

	_exit(0);
}
```

```asm
sys.S
.intel_syntax noprefix

.global write
.global read
.global fork
.global execve
.global real_waitid
.global _exit

write:
mov rax, 1
syscall
ret

read:
mov rax, 0
syscall
ret

execve:
mov rax, 59
syscall
ret


fork:
mov rax, 57
syscall
ret

real_waitid:
mov rax, 247
mov r10, rcx
syscall
ret

_exit:
mov rax, 60
syscall
```


```python
## 
```
