---
主题: call方法
分类: python
日期: 2026-06-15
---


## 一句话定义

__call__方法是类内实现的魔术方法，使类变可调用对象，可以用类似函数调用的方式比如class(a,b)的方法调用它

## 一个例子
```python
class Adder:
    def __init__(self, n):
            self.n = n
    def __call__(self, x):
        return x + self.n

add5 = Adder(5)      #类似函数调用
print(add5(10))