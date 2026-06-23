---
主题: 装饰器底层实现
分类: python
日期: 2026-06-15
---


## 一句话定义

装饰器本质是一个可调用对象，调用之后返回一个包装后的可调用对象

## 我的理解

包装器的语法是@wrap，类似func = warp(func)这种写法。实现函数包装器只需要实现外层被调用时接收一个函数，然后返回的是一个被包装好的函数就可以了；实现自己的类包装器对象的话，要在内部实现__init__的逻辑，要有接收func和其它参数（可选）的逻辑。还要实现__call__方法，要能接收参数，并且在这里面实现包装器本身的逻辑和被包装对象的调用逻辑等。

## 例子
```python
#函数包装器
def log(func):
     def wrapper(*args, **kwargs):
          print(f"调用 {func.__name__}, 参数 {args}")
          result = func(*args, **kwargs)
          print(f"{func.__name__} 返回 {result}")
          return result
     return wrapper

@log
def add(a, b):
     return a + b

print(add(2, 3))


#类包装器
class log:
     def __init__(self, func):     # 接收 func
          self.func = func
     def __call__(self, *args):    # 让实例可调用 = 等价于 wrapper
          print(f"调用 {self.func.__name__}")
          result = self.func(*args)
          print(f"{self.func.__name__} 返回 {result}")
          return result

@log
def add(a, b):
     return a + b

print(add(2,3))