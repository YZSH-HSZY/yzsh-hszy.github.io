---
Title: mblog python multiprocess Survey Research md.
Status: skip
---

# 介绍
这部分是接触高性能计算时笔记，主语言为python

## multiprocessing包
python提供一个multiprocessing包用于在进行大量计算指令之类的高cpu资源请求时，移除GIL，以充分利用多核性能。

**注意** 对于multiprocessing中pool的使用，与普通的Process有区别，相应的manger不同，使用`multiprocessing.Manager().Queue()|Lock()`获取适用于pool的队列或锁

## 多进程和多线程的区别
以实际开发来说，python中多线程在同一个python解释器上，因此对于一些三方的类或组件，可以在同一个环境中进行访问。
而对于多进程来说，只能通过队列或socket连接传递可序列化的对象，对于一些简易的c类型，可通过共享内存获取

## 示例

### python多进程共享内存加速numpy计算

```python
# 在外部创建共享内存
shm = multiprocessing.shared_memory.SharedMemory(create=True, size=self.FEATURE_NP_ARRAY.nbytes)
cp_np = np.frombuffer(shm.buf, dtype=np.uint8)  # 将共享内存区解释为一维数组（非拷贝）
cp_np[:] = self.FEATURE_NP_ARRAY[:]  # 拷贝数据到共享内存

# 在多进程函数中通过name获取共享内存
shm = multiprocessing.shared_memory.SharedMemory(name=shm_name)

# 通过multiprocess内置的进程池管理
with Pool(multiprocessing.cpu_count()) as pool:
    pool: multiprocessing.pool.Pool
    a_task_handle_num = 10000
    features_num = len(reset_features_pos)
    hangle_tasks_count = math.ceil(features_num/a_task_handle_num)
    for tt in range(hangle_tasks_count):
        fea_i = tt*a_task_handle_num
        async_res.append(pool.apply_async(
            multi_process_handle_func, 
            args=(
                reset_features_pos[fea_i: min(fea_i+a_task_handle_num, features_num)], 
                shm.name, mp_queue, mp_lock, mp_tqdm_count)
        ))
    [tem_p.wait() for tem_p in async_res]
```

## bug

### python的multiprocessing中目标函数为类方法时，报不能序列化
<!-- TODO -->

### python的multiprocessing中报错 `队列对象只能通过继承在进程之间共享`

> 问题描述: 在Pool中通过参数传递一个queue，在运行时报错 `Queue objects should only be shared between processes through inheritance`
> 解决方案: Pool有自己的管理Manager，请提供 `multiprocessing.Manager().Queue()` 创建队列

### multiprocessing使用tqdm参数，序列化错误

> 问题描述: 对于多部分拆解的多进程任务，想用tqdm进行进度显示时，直接传递tqdm对象在子进程更新，报运行时报错 `_io.TextWapper pick error`
> 解决方案: 提供multiprocessing提供的queue，在主线程中开一个守护进程进行更新，如:
```python
def handle_mult_process_result(self, mp_queue: Queue, mp_tqdm: tqdm.tqdm):
    while True:
        v = mp_queue.get()
        mp_tqdm.update(1)
daemon_t = Thread(target=self.handle_mult_process_result, args=(mp_queue, mp_tqdm))
daemon_t.setDaemon(True)
daemon_t.start()
# 子进程处理
# wait subprocess
while not mp_queue.empty(): pass  # 等待守护线程处理完毕
```
