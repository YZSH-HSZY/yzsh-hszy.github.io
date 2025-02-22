---
Title: Build Mini Linux Distro And Use Qemu Running.
Date: 2025-02-10 12:00
Lang: zh-cn
Category: Qemu
---

# 介绍
这是使用qemu的使用教程, 以构建最小linux发行版为例.
[参nir9博客](https://github.com/nir9/welcome/tree/master)

## 术语参考
- `initrd`: 初始化RAM磁盘, 是在实际根文件系统之前装载的初始根文件系统. initrd绑定到内核时会被内核引导过程加载,然后挂载initrd以加载模块使真正的文件系统可用
- `cpio`: cpio是一个将文件复制到 cpio 或 tar 存档文件或从中复制文件的程序,存档可以是磁盘上的另一个文件/磁带/管道

## 从构建linux内核开始

**env**
- linux内核源码 `git clone --depth 1 https://git.kernel.org/
pub/scm/linux/kernel/git/torvalds/linux.git`
- 依赖包 `apt install bzip2 libncurses-dev flex bison bc cpio libelf-dev libssl-dev syslinux dosfstools`
- 使用qemu启动编译后的内核 `apt install qemu-system-x86`
- 如果需要制作iso镜像文件 `apt install isolinux genisoimage`

**注意** 在linux目录下使用 `make help` 查看帮助, 这里我们使用 `make tinyconfig` 配置尽可能小的内核

> 使用 `make menuconfig` 配置编译make选项, 配置如下:
```
64-bit kernel
General setup  --->Initial RAM filesystem and RAM disk (initramfs/initrd) support 
General setup  --->Configure standard kernel features (expert users)  --->Enable support for printk 
Executable file formats  --->Kernel support for ELF binaries 
Device Drivers  --->Character devices  --->Enable TTY
```
> 以上配置分别代表生成 `64位内核`;`启用RAM文件系统和初始化根文件系统`;`启用文本打印支持`;`支持ELF格式执行文件`;`启用tty字符设备`
> 使用 `make -j $(nproc)` 构建, 默认生成的内核镜像在 `arch/x86/boot/bzImage`,为压缩的kernel镜像,约780K
> 查看内核镜像的运行 `qemu-system-x86_64 --kernel arch/x86/boot/bzImage`

**注意** 此时qemu启动kernel会报 `not working init found`, 因为此时没有准备启动初始程序

## 构建一个mini-shell
上述步骤中, 我们完成了一个轻量式的linux-kernel构建,接下来准备构建一个轻量的shell来作为init程序

1. 编写一个简易的调用shell命令程序, 使用POISX接口`write/read/execve/waitid`
```c
#include <unistd.h>
#include <sys/wait.h>

int main(){
    char cmd[255];
    for(;;){
        write(1, "# ", 2);
        int count = read(0, cmd, 255);
        // write(1, "", );
        cmd[count - 1] = 0;
        pid_t child = fork();
        if (child == -1){
            write(1, "fork failed!\nexit!!!", 21);
            break;
        }
        if (child == 0){
            execve(cmd, 0, NULL);
            break;
        }
        siginfo_t infop;
        waitid(P_ALL, 0, &infop, WEXITED);
    }
    return 0;
}
```
2. `gcc -static shell.c -o init` 编译为静态可执行文件
3. `echo init | cpio -H newc -o > init.cpio` 生成一个initrd
4. 重新编译为iso内核 `make isoimage FDARGS="initrd=/init.cpio" FDINITRD=$(pwd)/init.cpio` 生成的arch/x96/boot/image.iso 镜像大小为2.2M
5. 启动iso镜像 `qemu-system-x86_64 -cdrom image.iso`

### 使用assembly进行系统调用,进一步精简init程序

1. 在linux源码目录下参考系统调用的id号 `linux/arch/x86/include/generated/asm/syscalls_64.h`
2. 查阅[inter x86开发手册](https://www.intel.cn/content/www/cn/zh/support/articles/000006715/processors.html)了解各寄存器作用, 这里仅关注rax寄存器用于存储syscall的id
3. [wiki x86 体系结构的调用约定](https://en.wikipedia.org/wiki/X86_calling_conventions)
4. `ld -o init shell.o sys.o --entry main -z noexecstack`
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

echo init | cpio -H newc -o > init.cpio
make isoimage FDARGS="initrd=/init.cpio" FDINITRD=`pwd`/init.cpio
qemu-system-x86_64 -cdram arch/x86/boot/image.iso


```python
## 
```
