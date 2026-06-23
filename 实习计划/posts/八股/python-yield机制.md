---
主题: yield机制
分类: python
日期: 2026-06-15
---


## 一句话定义

yield可以让函数变成一个可迭代对象，使之可以分步执行，一次执行结束之后下次会从暂停处恢复运行。

## 我的理解

yield是python的一个特殊的关键字，当一个函数内部有yield关键字时，调用该函数不执行代码并返回一个生成器，每次迭代都会在yield停下并返回该yield值(如果有)，然后保存现场，下次迭代会在当前位置的下一条指令开始。yield函数可以用next和for迭代。

## 一个例子
```python
def counter():
     print("第一次进来")
     yield 1
     print("第二次进来")
     yield 2
     print("第三次进来")
     yield 3

c = counter()       # 不执行任何代码,只拿到生成器对象
print(next(c))      # 打印"第一次进来" + 1  ← 在 yield 1 处暂停
print(next(c))      # 打印"第二次进来" + 2  ← 从 yield 1 的下一条恢复
print(next(c))      # 打印"第三次进来" + 3
print(next(c))      # 抛 StopIteration(没 yield 了)

c2 = counter()
for p in c2:
     print(p).      #这里每次循环都运行到yield，这种方法很适合对超大数据的处理，对内存友好