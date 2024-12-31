---
Title: multiprocess blog.
Date: 2024-12-30 19:00
Lang: zh-cn
Category: Test
---

# 笔记介绍
该笔记用于记录工作中多进程相关问题和学习笔记.主要为python语言.
[参阅官方多进程文档获取详细说明](https://docs.python.org/zh-cn/3/library/multiprocessing.html)

> python内部提供一个multiprocessing模块, 其支持使用与 threading 模块类似的 API 来操作进程。可用其来绕过GIL

## 环境准备


```python
import os
from os.path import splitext, join, dirname, basename, abspath
import multiprocessing

print(f"current ipynb path is: {os.getcwd()}")
print(f"mkdir cache dir in order to run py in shell")

os.makedirs('.cache', exist_ok=True)

print(f"\ncreate dir {join(os.getcwd(), '.cache')} success.")
```

    current ipynb path is: /home/smartwork/work/mblog/process
    mkdir cache dir in order to run py in shell
    
    create dir /home/smartwork/work/mblog/process/.cache success.


**注意** multiprocessing 需要能够通过 `__main__` 模块加载target, 因此在一些交互式环境中无法使用.如在 jupyter 中无法运行, 可使用外置shell执行 `!python <py_file>`. 此处暂不深究repl中可加载 `__main__` 但仍无法运行multiprocess



## multiprocessing的支持上下文

1. spawn, 父进程启动一个新的python解释器进程. 子进程只继承运行进程对象的 run() 方法所必须的资源。
2. fork, 在posix系统上可用.
3. forkserver

其中,在window上默认使用 `spawn` 方式启动

## spawn探讨


```python
%%writefile .cache/test_spwan.py
import multiprocessing

print("import running output.")

def spawn_example():
    print(f"{8**9}")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    print("current mp start method is: ",  multiprocessing.get_start_method())

    t = multiprocessing.Process(target=spawn_example)
    t.start()
    t.join()
```

    Overwriting .cache/test_spwan.py



```python
!python .cache/test_spwan.py
```

    import running output.
    current mp start method is:  spawn
    import running output.
    134217728


从上述执行结果中可以看到, `import running output.` 输出了两次. 一次为python运行时解析执行的print语句,


```python
import collections
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
import math
import multiprocessing.context
import multiprocessing.pool
import multiprocessing.shared_memory
import multiprocessing.synchronize
from random import randint
import shutil
import struct
import os
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from warnings import warn
import tqdm
from os.path import join, basename, dirname, splitext, isdir, isfile, isdir
from glob import glob

from math import pi as PI
from math import log, tan, atan, exp

from datetime import datetime
import numpy as np
import multiprocessing as mp
from multiprocessing.sharedctypes import Value, Array
from multiprocessing import Pool, Lock, Queue
import queue

from PyQt5.QtCore import QVariant
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY, QgsProject, QgsApplication, QgsVectorLayer
from qgis.gui import QgisInterface
from qgis.utils import iface
from qgis._core import QgsCoordinateReferenceSystem, QgsFields, QgsField, QgsVectorFileWriter, QgsWkbTypes, QgsProject, QgsVectorLayer
from qgis._core import QgsApplication

def LonLat2WebMercator(lon, lat):
  """
    lonLat is from GPS's WGS84
    webMercator is the fromat in baidumap, googlemap
    longitude and latitude to web Mercator
  """
  x = lon*20037508.34/180
  y = log(tan((90+lat)*PI/360))/(PI / 180)
  y = y*20037508.34/180
  return [x, y]

def WebMercator2LonLat( x, y ):
  """
    web Mercator to longitude and latitude
  """
  lon = x/20037508.34*180
  lat = y/20037508.34*180
  lat = 180/PI*(2*atan(exp(lat*PI/180))-PI/2)
  return [lon, lat]

@dataclass
class A:
    i: int
    l: list
    d: dict

@dataclass
class Point:
    x: float
    y: float
    def to_qgs_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPointXY(QgsPointXY(*WebMercator2LonLat(self.x, self.y)))
    def handle_convert_geometry(self, 
            attrs: QgsFields, val_dicts: Dict[str, Any], layer: QgsVectorLayer = None) -> QgsGeometry:
        return self.to_qgs_geometry()

@dataclass
class Point25D:
    x: float
    y: float
    depth: float
    def to_qgs_geometry(self) -> QgsGeometry:
        return QgsGeometry.fromPointXY(QgsPointXY(*WebMercator2LonLat(self.x, self.y)))
    def handle_convert_geometry(self, 
            attrs: QgsFields, val_dicts: Dict[str, Any], layer: QgsVectorLayer = None) -> QgsGeometry:
        # if layer is not None: 
        #     layer.addAttribute(QgsField("depth", QVariant.String, None, 254))
        #     feature.setAttribute("depth", str(self.depth))
        if "depth" not in attrs.names(): 
            attrs.append(QgsField("depth", QVariant.String, None, 254))
        elif not val_dicts.get("depth", ""):
            # warn(f'Point25D 类型对应layer中, depth字段已存在,参{val_dicts},self.depth:{str(self.depth)}')
            pass
        else:
            warn(f'Point25D 类型对应layer中, depth字段已存在,参{val_dicts},self.depth:{str(self.depth)}')

        val_dicts['depth'] = str(self.depth)
        return self.to_qgs_geometry()

@dataclass
class Pline:
    minx: float
    miny: float
    maxx: float
    maxy: float
    points_number: int
    repeat_points: List[Point]
    def to_qgs_geometry(self) -> QgsGeometry:
        if self.points_number != len(self.repeat_points):
            warn(
                f"points_number is not equal to repeat_points, "
                f"points_number = {self.points_number}, repeat_points = {len(self.repeat_points)}")
        return QgsGeometry.fromPolylineXY(
            [QgsPointXY(*WebMercator2LonLat(t.x, t.y)) for t in self.repeat_points]
        )
    def handle_convert_geometry(self, 
            attrs: QgsFields, val_dicts: Dict[str, Any], layer: QgsVectorLayer = None) -> QgsGeometry:
        return self.to_qgs_geometry()

MULT_POLYGON_COUNT = 0  # 多部分多边形计数

@dataclass
class Polygon:
    minx: float
    miny: float
    maxx: float
    maxy: float
    polygon_num: int
    repeat_plines: List[Pline]  # 不包含mixx/y,maxx/y
    def to_qgs_geometry(self) -> List[QgsGeometry]:
        if self.polygon_num != len(self.repeat_plines):
            warn(
                f"polygon_num is not equal to repeat_plines, "
                f"polygon_num = {self.polygon_num}, repeat_plines = {len(self.repeat_plines)}")
        if self.polygon_num > 1:
            warn(
                f'handle multiple polygon. num is :{self.polygon_num}'
            )
        res = []
        for t in self.repeat_plines:
            res.append(QgsGeometry.fromPolygonXY(
                [[QgsPointXY(*WebMercator2LonLat(k.x, k.y)) for k in t.repeat_points]]
            ))
        return res
    def handle_convert_geometry(self, 
            attrs: QgsFields, val_dicts: Dict[str, Any], layer: QgsVectorLayer = None) -> QgsGeometry:
        global MULT_POLYGON_COUNT
        the_geoms = self.to_qgs_geometry()
        for polygon in the_geoms[1:]:
            MULT_POLYGON_COUNT += 1
            # Dat2Shp.add_feature_to_layer(-1, attrs, val_dicts, polygon, layer)
        return the_geoms[0]


def mp_handle_func(mp_queue: Queue):
    for i in range(1, 3):
        t = A(randint(1,10), [1,2], {})
        tt = randint(1,4) 
        if tt == 1:
            t = Point(1.2,2.4)
        if tt == 2:
            t = Polygon(0,1,2,3,1,[Pline(3,4,5,6,1,[Point(8,9)])])
        mp_queue.put(t)
    return mp.current_process().pid

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    mp_queue = mp.Manager().Queue()
    
    a = A(1, [2,3], {'a':4})
    mp_queue.put(A)
    
    async_res: List[multiprocessing.pool.ApplyResult] = []
    
    with mp.Pool(2) as pool:
        pool: multiprocessing.pool.Pool
        async_res.append(pool.apply_async(mp_handle_func, args=(mp_queue, )))
        async_res.append(pool.apply_async(mp_handle_func, args=(mp_queue, )))
    
        [tem_p.wait() for tem_p in async_res]
    
    try:
        print([tem_p.get() for tem_p in async_res])
        while not mp_queue.empty():
            print(mp_queue.get_nowait())
    except queue.Empty as e:
        print('mp_queue is empty')
    pass

```

输出如下:
```python
[18952, 5852]
<class '__main__.A'>
A(i=9, l=[1, 2], d={})
A(i=7, l=[1, 2], d={})
Polygon(minx=0, miny=1, maxx=2, maxy=3, polygon_num=1, repeat_plines=[Pline(minx=3, miny=4, maxx=5, maxy=6, points_number=1, repeat_points=[Point(x=8, y=9)])])
A(i=4, l=[1, 2], d={})
```
