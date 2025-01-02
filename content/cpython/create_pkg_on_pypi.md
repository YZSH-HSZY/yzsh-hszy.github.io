---
Title: Cpython Package Publish Notes.
Date: 2024-07-18 12:00
Lang: zh-cn
Category: Cpython
---

## 如何在 pypi(即python package index，python包索引)上发布自己新建的工具包？


### setup.cfg vs setup.py vs pyproject.toml区别

这三个文件是Python项目的配置文件,他们分别用于不同的目的:
1. setup.cfg: 这是一个全局配置文件,它存储了用于构建、发布和安装Python包的选项。例如,您可以在此文件中指定需要安装的依赖项或构建选项。
2. setup.py: 这是Python项目的关键配置文件,它包含了有关项目的信息,例如项目名称、版本、描述、作者等。您可以使用此文件来管理项目的构建、发布和安装过程。
3. pyproject.toml: 这是Python项目的新标准配置文件,提供了一种更简洁、清晰的配置方式。
它可以用于描述项目的依赖项、构建选项、扩展等信息。

> 总的来说,如果您正在开发一个新项目,建议使用pyproject.toml,因为它是Python项目的最新标准。
如果您正在开发一个旧项目,则可能需要使用setup.py和setup.cfg.

