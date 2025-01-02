---
Title: Python Super Class Example Notes.
Date: 2024-07-18 12:00
Lang: zh-cn
Category: Cpython
---

## super笔记
在oop编程中，我们经常需要使用super来调用父类的方法，各个编程语言均有对应的super实现。在python中提供超类super的类定义，有以下几种调用方式。
1. 在类定义代码段中，使用无参数的 `super()` 调用
2. 通过super通过的初始化方法 `super(type, object_or_type=None)` 调用，该初始化方法有三种重载方法:
    - 单参数 `super(type)`,此时返回的super超类对象是未绑定的
    - `super(type, obj)`,必须满足 `isinstance(obj,type)`
    - `super(type, type2)`,必须满足 `issubclass(type,type2)`

**注意** 返回一个代理对象，它会将方法调用委托给 type 的父类或兄弟类。 这对于访问已在类中被重写的继承方法很有用。

[python官方super介绍](https://docs.python.org/zh-cn/3/library/functions.html#super)



```python
""" 
    演示super(type, obj)和super(type,type2)调用
"""
class Father:
    def father_obj_method(self):
        return 'this is obj of Father'
    @classmethod
    def father_classmethod(cls):
        return 'this is method of Father method'

class Child(Father):
    def father_obj_method(self):
        return 'overwrite obj method'
    @classmethod
    def father_classmethod(cls):
        return 'overwrite classmethod'

if __name__ == "__main__":
    child_obj = Child()
    father_obj = Father()
    print('this is child obj`s method:', child_obj.father_obj_method())
    # 获取super代理对象，访问child_obj的父对象部分
    print('get child obj`s Father obj method:', super(Child, child_obj).father_obj_method())

    print('this is Child classmethod:', child_obj.father_classmethod())
    # 获取super代理对象，访问Child类的父类部分
    print('get Child class`s Father classmethod:', super(Child, Child).father_classmethod())
```

    this is child obj`s method: overwrite obj method
    get child obj`s Father obj method: this is obj of Father
    this is Child classmethod: overwrite classmethod
    get Child class`s Father classmethod: this is method of Father method


### super的父类查找顺序
在python官方文档中是这样描述的:
> object_or_type 确定要用于搜索的解析顺序。 搜索会从 type 之后的类开始。
举例来说，如果 object_or_type 的 `__mro__` 为 `D -> B -> C -> A -> object` 并且 type 的值为 B，则 super() 将会搜索 `C -> A -> object`。

> object_or_type 的 `__mro__` 属性列出了 getattr() 和 super() 所共同使用的方法解析搜索顺序。 该属性是动态的并可在任何继承层级结构发生更新时被改变。

**注意** __mro__属性是被类方法mro()填充的，它在类实例化时被调用。即mro定义在元类type上，

>>> type.mro
<method 'mro' of 'type' objects>
>>> list.mro
<built-in method mro of type object at 0x00007FF9553BFAF0>
>>> object.mro
<built-in method mro of type object at 0x00007FF9553C2E00>


```C
Python-3.12.3/Objects/typeobject.c :10147
typedef struct {
    PyObject_HEAD
    PyTypeObject *type;
    PyObject *obj;
    PyTypeObject *obj_type;
} superobject;

static PyMemberDef super_members[] = {
    {"__thisclass__", T_OBJECT, offsetof(superobject, type), READONLY,
     "the class invoking super()"},
    {"__self__",  T_OBJECT, offsetof(superobject, obj), READONLY,
     "the instance invoking super(); may be None"},
    {"__self_class__", T_OBJECT, offsetof(superobject, obj_type), READONLY,
     "the type of the instance invoking super(); may be None"},
    {0}
};
```
