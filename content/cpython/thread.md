---
Title: Python Thread Package Example Notes.
Date: 2024-07-18 12:00
Lang: zh-cn
Category: Cpython
---


```python
import atexit
from datetime import datetime
import threading
from time import sleep
def test_p():
    print('this is test', str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
    assert 1 == 1
# atexit.register(test_p)
    
def thread_print():
    i = 0
    while i < 1e3:
        sleep(.001)
        i += 1
    print('threading end print')
def end_print(*args):
    print('atexiting print')
    print(args)
    if isinstance(args[0], threading.Thread):
        p = args[0]
        print(p, p.is_alive(), p.name)
        p.join()
p = threading.Thread(
    target=thread_print,
    args=[]
)
# 1. 对应主进程来说，并不是主线程退出了，主进程就会退出
#   > 而是主进程会等待所有在前景的线程结束才会退出
# 2. 如果线程设置了守护标志，是一个背景线程daemon,那么主进程不会等待其执行完成才退出
#   > 一般无限循环检测标志或为其他线程提供服务的线程被设置为守护线程
# 
p.setDaemon(True)
p.start()
atexit.register(end_print, p)


```
