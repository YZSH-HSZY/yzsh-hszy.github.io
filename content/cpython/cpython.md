---
Title: Cpython Learen Notes.
Date: 2024-07-18 12:00
Lang: zh-cn
Category: Cpython
---

# cpython
一个python的c语言解释器，同样的python解释器实现还有jython、pypy等

[github官网](https://github.com/python/cpython)

## 准备
在学习python的过程中，我对python的一些工作细节感到困惑，因此有了本文。在这里我将学习cpython源码的一些细节记录在下面:

**环境** cpython 3.12.3,ubuntu 20.04 in wsl2,gun/gcc系列编译器
**注意** cpython在编译安装时，需要已有pyhton环境

## cpython编译
[python官方开发构建文档](https://devguide.python.org/getting-started/setup-building/#build-dependencies)

在进行cpython的编译时，需要注意可能缺少相应的依赖项，可以使用`apt search`和`apt-file`命令找到包在机器上的安装名和文件存在与那些包中。

这里列出一些需要的安装包
- build-essential 包含一系列的C/C++开发工具，主要为GNU系列编译器
- python3-pip python的pip包管理器
- manpages-dev 适用于开发环境的man手册(包含系统调用和库调用的介绍信息)
- pkg-config 管理库的编译和链接标志的工具，在项目包含依赖库时有用
- cmake 一个简易的、生成makefile文件的项目构建工具
- gdb GNU系列的调试器，进行源码调试的工具

**注意** 模块n/a(not available)有以下几种情况:
1. 模块不支持当前 Python 版本：某些模块可能只支持特定的 Python 版本，如果你使用的 Python 版本不在支持范围内，模块可能无法编译。
2. 缺少依赖库：某些模块可能依赖于特定的库或框架，如果这些库或框架未安装或不可用，模块可能无法编译。
3. 编译错误：模块的源代码可能存在错误，导致编译失败。
4. 不支持当前操作系统：某些模块可能只支持特定的操作系统，如果你使用的操作系统不在支持范围内，模块可能无法编译。

### 编译过程
```sh
./configure --help  # 查看帮助信息
# 调试构建
mkdir debug
cd debug
../configure --with-pydebug
make
make test
```

#### configure文件生成
CPython 的 `configure` 脚本是使用 `GNU Autoconf` 从 `configure.ac` 生成
你可以在更改 `configure.ac` 后，运行 `make regen-configure` 生成 `configure`/`pyconfig.h.in`/`aclocal.m4`

**注意** 不同cpython版本使用的autoconf版本不同
- 对于 Python 3.12 及更新版本，需要 `GNU Autoconf v2.71`
- 对于 Python 3.11 及更早版本，需要 `GNU Autoconf v2.69`


### 编译过程中报缺少模块的错误

一般是由于缺少头文件造成的，可以通过`find`查看有无对应头文件，无则需要安装开发库，可通过`apt-file`搜索可安装包，以下是一些模块对应缺少的依赖库

- no module _ssl
    安装tk-itk4-dev tcl-itcl4-dev libssl-dev
- ctype
    libffi-dev
- readline
    [libreadline-dev | lib32readline-dev]
- _bz2
    libbz2-dev
     介绍:
      high-quality block-sorting file compressor library- development(高质量的块排序文件压缩程序库-开发)
- _lzma
    liblzma-dev
     介绍:
      XZ-format compression library(xz格式的压缩算法库)
      注意: 5.6.0,5.6.1版本中存在xz安全漏洞,请安装低版本
- _gdbm _dbm
    libgdbm-dev libgdbm-compat-dev
     介绍:
      dbm: kv型数据库  
      libgdbm-dev: GNU dbm database routines(GNU数据库例程)
      libgdbm-compat-dev: legacy support development files(遗留支持开发文件)。解决无dbm.h文件问题    

**注意** `apt-file`需要使用`apt install apt-file`安装，并且使用`apt-file update`更新数据库之后，才能使用。

### 使用 `dev container` 进行 `cpython` 的学习开发

[参vscode开发容器创建教程](https://code.visualstudio.com/docs/devcontainers/create-dev-container#_dockerfile)

> 其中 `devcontainer.json` 可在cpython官方仓库中获取

## cpython目录结构

- `Doc`                 文档
- `Grammar`             包含 Python 的 EBNF(Extended Backus-Naur Form) 语法文件
- `Include`             cpython解释器头文件
- `Lib`                 纯 Python 实现的标准库
- `Misc`                独立目录，包含文档等
- `Modules`             用 C 实现的标准库
- `Objects`             所有内置类型的代码
- `Mac`                 Mac 特定代码
- `PC`                  Windows 特定代码
- `PCbuild`             MSVC 构建文件
- `Parser`              解析器相关的代码。包含 AST 节点定义
- `Programs`            C 可执行文件的源代码，包括 CPython 解释器的 main 函数
- `Python`              CPython core runtime。包括编译器、评估循环和各种内置模块
- `Tools`               维护 Python 的工具

## 相关术语解释

### EBNF(Extended Backus-Naur Form, 扩展巴科斯范式)

巴科斯范式（Backus Normal Form简称为BNF），又称为巴科斯-诺尔范式，是一种上下文无关的语言，广泛地使用于程序设计语言、指令集、通信协议的语法表示中。

> 上下文无关语言的典型代表: 正则语言 -- 一种通过有限状态机或正则表达式表达的语言，这种语言是上下文无关语言的子集。
> 一个表示数字相加的BNF示例如下:
```
<addition> ::= <number>+<number>
<number> ::= <sign><integer>|<integer>
<integer> ::= <digit>|<digit><integer>
<digit>::=0|1|2|3|4|5|6|7|8|9
<sign> ::= +|-
```

## cpython源码分析

## 分析实例