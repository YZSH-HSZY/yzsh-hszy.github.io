---
Title: Mindspore Learen Notes -- Tensor Understand.
Date: 2024-07-18 12:00
Lang: zh-cn
Category: Mindspore
---

## 张量介绍
张量（Tensor）是一个可用来表示在一些矢量、标量和其他张量之间的线性关系的多线性函数，这些线性关系的基本例子有内积、外积、线性映射以及笛卡儿积。其坐标在 𝑛 维空间内，有 $n^r$ 个分量的一种量，其中每个分量都是坐标的函数，而在坐标变换时，这些分量也依照某些规则作线性变换。 𝑟 称为该张量的秩或阶（与矩阵的秩和阶均无关系）。

**注意** 张量是一种特殊的数据结构，与数组和矩阵非常相似。张量（Tensor）是MindSpore网络运算中的基本数据结构，本教程主要介绍张量和稀疏张量的属性及用法。

## 张量与矩阵与数组与向量的区别
在numpy中，数据的结构有数组、矩阵、向量这几种描述方式，而在深度学习中通常使用张量来描述所有数据和相应的变换关系。在参与运算时他们之间的差距通常非常小，但却是不同角度下的描述，因此正确的理解并区分他们是必要的。




```python
# mindspore base moudel import
import numpy as np
import mindspore
from mindspore import ops
from mindspore import Tensor, CSRTensor, COOTensor
print('moudel import success')
```

    moudel import success


### a base tensor create
构造张量时，支持传入Tensor、float、int、bool、tuple、list、complex和numpy.ndarray类型。
1. 根据数据直接生成
可以根据数据创建张量，数据类型可以设置或者通过框架自动推断。


```python
# python原生类型
int_tensor = Tensor(1)
float_tensor = Tensor(1.)
bool_tensor = Tensor(True)
tuple_tensor = Tensor((1,2))
list_tensor = Tensor([1,3])
complex_tensor = Tensor(complex(1,9))
temp_dict = locals()
for k,v in temp_dict.items():
    if k.endswith('tensor') and isinstance(v, Tensor):
        print(
            k, 
            ';value is :', v,
            ';shape is :', v.shape,
            ';dtype is :', v.dtype
        )
# Tensor、numpy.ndarray类型
nd_tensor = Tensor(np.array([[1,2],[3,4]], dtype=np.float32))
print('nd_tensor', id(nd_tensor), nd_tensor.shape, nd_tensor.dtype)
cp_tensor = Tensor(nd_tensor)
print('cp_tensor', id(cp_tensor), cp_tensor.shape, cp_tensor.dtype)
```

    int_tensor ;value is : 1 ;shape is : () ;dtype is : Int64
    float_tensor ;value is : 1.0 ;shape is : () ;dtype is : Float32
    bool_tensor ;value is : True ;shape is : () ;dtype is : Bool
    tuple_tensor ;value is : [1 2] ;shape is : (2,) ;dtype is : Int64
    list_tensor ;value is : [1 3] ;shape is : (2,) ;dtype is : Int64
    complex_tensor ;value is : (1+9j) ;shape is : () ;dtype is : Complex128
    nd_tensor 281468910652768 (2, 2) Float32
    cp_tensor 281468910653168 (2, 2) Float32


2. 使用init初始化器构造张量

当使用init初始化器对张量进行初始化时，支持传入的参数有init、shape、dtype。

- init: 支持传入initializer的子类。如：下方示例中的 One() 和 Normal()。

- shape: 支持传入 list、tuple、 int。

- dtype: 支持传入mindspore.dtype。


```python
from mindspore.common.initializer import One, Normal

# Initialize a tensor with ones
tensor1 = mindspore.Tensor(shape=(2, 2), dtype=mindspore.float32, init=One())
print("tensor1:\n", tensor1)
```

    tensor1:
     [[1. 1.]
     [1. 1.]]


Normal初始化器会将数据进行正太分布处理，公式如下:
$f(x) =  \frac{1} {\sqrt{2*π} * sigma}exp(-\frac{(x - mean)^2} {2*{sigma}^2})$
参数默认值 sigma=0.01, mean=0.0，生成的x元素为随机值


```python
# Initialize a tensor from normal distribution
tensor2 = mindspore.Tensor(shape=(2, 3), dtype=mindspore.float32, init=Normal())
print("tensor2:\n", tensor2)
```

    tensor2:
     [[ 0.01408593  0.00398565  0.01824992]
     [-0.00208053  0.01520424  0.01576259]]


> 在我探究Normal()作用时，注意到另一个和 `mindspore.Tensor` 类似的类 `mindspore._c_expression.Tensor`,那么他们有什么区别呢？

> 为了解决这个问题，我编写了以下python代码验证：


```python
from mindspore._c_expression import Tensor as Tensor_
import mindspore._c_expression as _c
# 这个_c_expression是一个so库文件，可以通过__file__属性查看其所在位置
print('the _c_expression so library file path is :', _c.__file__)
some_list = []  # 记载Tensor_和Tensor自身属性地址相同部分
diff_list = []
for k in dir(Tensor_):
    if k.startswith('__'): continue
    if id(getattr(Tensor_, k)) == id(getattr(Tensor,k)):
        some_list.append(k)
    else:
        diff_list.append(k)
print('-' * 20)
print('mindspore.Tensor and mindspore._c_expression.Tensor has some attrs is :',
      ' '.join(some_list))
print('all some attrs nums is :', len(some_list))
print('-' * 20)
print('mindspore.Tensor and mindspore._c_expression.Tensor has diff attrs is :',
       ' '.join(diff_list))
print('all diff attrs nums is :', len(diff_list))
```

    the _c_expression so library file path is : /home/nginx/miniconda/envs/jupyter/lib/python3.9/site-packages/mindspore/_c_expression.cpython-39-aarch64-linux-gnu.so
    --------------------
    mindspore.Tensor and mindspore._c_expression.Tensor has some attrs is : _dtype _flatten_tensors _flush_from_cache _get_flattened_tensors _get_fusion_size _is_flattened _is_test_stub _itemsize _nbytes _shape _size _strides adapter_flag assign_value_cpp data_sync dim getitem_index_info init_flag is_init offload offload_file_path param_info persistent_data_from_numpy set_cast_dtype set_dtype set_init_flag setitem_index_info
    all some attrs nums is : 27
    --------------------
    mindspore.Tensor and mindspore._c_expression.Tensor has diff attrs is : _offload asnumpy asnumpy_of_slice_persistent_data contiguous dtype from_numpy get_bytes is_contiguous is_persistent_data shape
    all diff attrs nums is : 10


可以看到Tensor_和Tensor大部分属性的均指向同一地址，因为_c_expression是一个库扩展模块，要想更加详细的了解他们之间区别，需要去查看对应的c++源码实现。
这里只列出部分我探究的内容，更详细的解析请自行查看源码。
<!-- TODO 未完成，仅列出部分以记录 -->
1. python类Tensor的init方法在`mindspore\python\mindspore\common\tensor.py`;在其初始化方法中最终均会调用`Tensor_.__init__`方法
2. mindspore编写python扩展`_c_expression`是通过`pybind11`进行的，在`mindspore\ccsrc\CMakeLists.txt`文件中存在调用`pybind11_add_module`的cmake宏进行py模块绑定，对应文件为`mindspore\ccsrc\pipeline\jit\ps\init.cc`，内有`PYBIND11_MODULE(_c_expression, m)` 进行`_c_expression`模块的具体代码绑定。
3. 第2步中，`_c_expression`模块缺少py::class Tensor的绑定，我只在`mindspore\ccsrc\pybind_api\ir\tensor_py.cc`中找到 `mindspore.Tensor` 的绑定代码。
4. 进一步研究发现，`tensor_py.cc`对应的`py::class Tensor`绑定代码在函数`RegMetaTensor`中，会被`RegModule`调用，最终在`PYBIND11_MODULE`中通过`mindspore::RegModuleHelper`调用绑定，而`mindspore.Tensor`继承自`_c_expression.Tensor`类，可以通过类的mro方法查看继承关系。



```python
print(Tensor.mro())
print(Tensor_.mro())
```

    [<class 'mindspore.common.tensor.Tensor'>, <class 'mindspore._c_expression.Tensor'>, <class 'mindspore._c_expression.MetaTensor'>, <class 'pybind11_builtins.pybind11_object'>, <class 'object'>]
    [<class 'mindspore._c_expression.Tensor'>, <class 'mindspore._c_expression.MetaTensor'>, <class 'pybind11_builtins.pybind11_object'>, <class 'object'>]



```python
# 回到正题，张量Tensor的创建也可以根据另一个Tensor的属性进行
# mindspore提供了一个ops模块可用于Cell的构造
a_ones = ops.ones_like(tensor1)
a_zeros = ops.zeros_like(tensor1)
print('ops create ones tensor is:', a_ones)
print('ops create zeros tensor is:', a_zeros)
```

    ops create ones tensor is: [[1. 1.]
     [1. 1.]]
    ops create zeros tensor is: [[0. 0.]
     [0. 0.]]


### 张量的常用属性

- 形状（shape）：`Tensor`的shape，是一个tuple。

- 数据类型（dtype）：`Tensor`元素的dtype，是MindSpore的一个数据类型。

- 单个元素大小（itemsize）： `Tensor`中每一个元素占用字节数，是一个整数。

- 占用字节数量（nbytes）： `Tensor`占用的总字节数，是一个整数。

- 维数（ndim）： `Tensor`的秩，也就是len(tensor.shape)，是一个整数。

- 元素个数（size）： `Tensor`中所有元素的个数，是一个整数。

- 每一维步长（strides）： `Tensor`每一维所需要的字节数，是一个tuple。


```python
t = Tensor([[1,2,3],[1,7,9]])
print("t_shape:", t.shape)
print("t_dtype:", t.dtype)
print("t_itemsize:", t.itemsize)
print("t_nbytes:", t.nbytes)
print("t_ndim:", t.ndim)
print("t_size:", t.size)
print("t_strides:", t.strides)
```

    t_shape: (2, 3)
    t_dtype: Int64
    t_itemsize: 8
    t_nbytes: 48
    t_ndim: 2
    t_size: 6
    t_strides: (24, 8)


<span display=hidden>### 维度与维数区别
Tensorflow描述张量的维度：阶，形状以及维数 

TensorFlow用张量这种数据结构来表示所有的数据.你可以把一个张量想象成一个n维的数组或列表.一个张量有一个静态类型和动态类型的维数.张量可以在图中的节点之间流通。

在TensorFlow系统中，张量的维数来被描述为阶。但是张量的阶和矩阵的阶并不是同一个概念。张量的阶（有时是关于如顺序或度数或者是n维）是张量维数的一个数量描述。

比如，下面的张量（使用Python中list定义的）就是2阶。

TensorFlow文档中使用了三种记号来方便地描述张量的维度：阶，形状以及维数.下表展示了他们之间的关系：
</span>

### 张量索引
Tensor索引与Numpy索引类似，索引从0开始编制，负索引表示按倒序编制，冒号:和 ...用于对数据进行切片。


```python
print('the tensor is:', t)
print("First row: {}".format(t[0]))
print("value of bottom right corner: {}".format(t[1, 1]))
print("Last column: {}".format(t[:, -1]))
print("First column: {}".format(t[..., 0]))
```

    the tensor is: [[1 2 3]
     [1 7 9]]
    First row: [1 2 3]
    value of bottom right corner: 7
    Last column: [3 9]
    First column: [1 1]


### 张量运算

张量之间可以使用很多运算，包括算术、线性代数、矩阵处理（转置、标引、切片）、采样等，使用方法和numpy类似


```python
x = Tensor(np.array([9, 2, 3, 5]), mindspore.float32)
y = Tensor(np.array([4, 5, 6, 3]), mindspore.float32)
# 1. 算术运算
print("add:", x + y)
print("sub:", x - y)
print("mul:", x * y)
print("div:", x / y)
print("mod:", x % y)
print("floordiv:", x // y)
# 2. 矩阵处理
print("转置:", x.reshape((2,2)).T)
# 使用`ops.concat`连接张量
print("concat tensors:", ops.concat((x, y), axis=0))
# 使用ops.stack从新维度合并张量
print("stack tensors:", ops.stack([x,y]))
# 3. tensor与np.ndarray转换
print(f"x: {x}", type(x))
n = x.asnumpy()
print(f"n: {n}", type(n))

```

    add: [13.  7.  9.  8.]
    sub: [ 5. -3. -3.  2.]
    mul: [36. 10. 18. 15.]
    div: [2.25      0.4       0.5       1.6666666]
    mod: [1. 2. 3. 2.]
    floordiv: [2. 0. 0. 1.]
    [[9. 3.]
     [2. 5.]]
    concat tensors: [9. 2. 3. 5. 4. 5. 6. 3.]
    stack tensors: [[9. 2. 3. 5.]
     [4. 5. 6. 3.]]
    x: [9. 2. 3. 5.] <class 'mindspore.common.tensor.Tensor'>
    n: [9. 2. 3. 5.] <class 'numpy.ndarray'>


### 几种特殊tensor
#### 稀疏张量

稀疏张量中绝大部分元素的值为零。

在某些应用场景中（比如推荐系统、分子动力学、图神经网络等），数据的特征是稀疏的，若使用普通张量表征这些数据会引入大量不必要的计算、存储和通讯开销。这时就可以使用稀疏张量来表征这些数据。

MindSpore支持常用的`CSR`和`COO`两种稀疏数据格式，如`CSRTensor`、`COOTensor`和`RowTensor`等

常用稀疏张量的表达形式是`<indices:Tensor, values:Tensor, shape:Tensor>`。其中，`indices`表示非零下标元素， `values`表示非零元素的值，shape表示的是被压缩的稀疏张量的形状。

##### CSRTensor

`CSR`（Compressed Sparse Row，压缩稀疏行）稀疏张量格式有着高效的存储与计算的优势。其中，非零元素的值存储在`values`中，非零元素的位置存储在`indptr`（行）和`indices`（列）中。各参数含义如下：

- `indptr`: 一维整数张量, 表示稀疏数据每一行的非零元素在`values`中的起始位置和终止位置, 索引数据类型支持int16、int32、int64。

- `indices`: 一维整数张量，表示稀疏张量非零元素在列中的位置, 与`values`长度相等，索引数据类型支持int16、int32、int64。

- `values`: 一维张量，表示`CSRTensor`相对应的非零元素的值，与`indices`长度相等。

- `shape`: 表示被压缩的稀疏张量的形状，数据类型为`Tuple`，目前仅支持二维`CSRTensor`。


**注意** CSRTensor有以下限制：

1. CSR仅能表示二维张量
2. 行张量`indptr`的`size`为`csrtensor.shape[0]+1`，其索引i表示csr张量第i行，值为列张量`indices`索引，即指向该行第一个非0元素列位置
3. 列张量`indices`，存储每个非0元素的列位置，长度与值张量`values`相等，`indices[i]` 表示第i个非0元素所在列位置
4. 值张量`values` 存储csr所有非0值，按先行后列排序

**注意** 在Ascend平台，CSRTensor很多运算不可用



```python
indptr = Tensor([0, 2, 4], dtype=mindspore.int32)
indices = Tensor([0, 2, 1, 3], dtype=mindspore.int32)
values = Tensor([1, 5, 2, 9], dtype=mindspore.float32)
shape = (2, 4)

# Make a CSRTensor
csr_tensor = CSRTensor(indptr, indices, values, shape)

print(csr_tensor.astype(mindspore.float64).dtype)
print(csr_tensor)
# 第一行元素indptr[0]首个非零元素在indices[indptr[0]]列出现，值为values[indptr[0]]
# 第二行元素indptr[1]首个非零元素在indices[indptr[1]]列出现，值为values[indptr[1]]
# values[indptr[0],indptr[1]]为第一行所有非零元素，列位置在indices中
```

    Float64
    CSRTensor(shape=[2, 4], dtype=Float32, indptr=Tensor(shape=[3], dtype=Int32, value=[0 1 2]), indices=Tensor(shape=[4], dtype=Int32, value=[0 2 1 3]), values=Tensor(shape=[4], dtype=Float32, value=[ 1.00000000e+00  5.00000000e+00  2.00000000e+00  9.00000000e+00]))


上述代码表示如下所示的`CSRTensor`:

$$
 \left[
 \begin{matrix}
   1 & 0 & 5 & 0 \\
   0 & 2 & 0 & 9
  \end{matrix}
  \right]
$$

##### COOTensor

`COO`（Coordinate Format）稀疏张量格式用来表示某一张量在给定索引上非零元素的集合，若非零元素的个数为`N`，被压缩的张量的维数为`ndims`。各参数含义如下：

- `indices`: 二维整数张量，每行代表非零元素下标。形状：`[N, ndims]`， 索引数据类型支持int16、int32、int64。

- `values`: 一维张量，表示相对应的非零元素的值。形状：`[N]`。

- `shape`: 表示被压缩的稀疏张量的形状，目前仅支持二维`COOTensor`。

**注意** values中每个非零元素values[i]在COOTensor中的坐标为indices[i]，因此可支持多维Tensor

下面给出一些COOTensor的使用示例：



```python
indices = Tensor([[0, 1], [1, 2]], dtype=mindspore.int32)
values = Tensor([1, 2], dtype=mindspore.float32)
shape = (3, 4)

# Make a COOTensor
COOTensor(indices, values, shape)

```




    COOTensor(shape=[3, 4], dtype=Float32, indices=Tensor(shape=[2, 2], dtype=Int32, value=
    [[0 1]
     [1 2]]), values=Tensor(shape=[2], dtype=Float32, value=[ 1.00000000e+00  2.00000000e+00]))



上述代码表示如下所示的`COOTensor`:

$$
 \left[
 \begin{matrix}
   0 & 1 & 0 & 0 \\
   0 & 0 & 2 & 0 \\
   0 & 0 & 0 & 0
  \end{matrix}
  \right]
$$



```python
from datetime import datetime
import pytz
print(datetime.now(pytz.timezone('Asia/Shanghai')), '\nuser:YZSH-HSZY')
```

    2024-07-04 16:08:16.273507+08:00 
    user:YZSH-HSZY

