---
主题: 生成器vs迭代器
分类: python
日期: 2026-06-15
---


## 一句话定义

迭代器属于可迭代对象；生成器属于可迭代对象，属于迭代器。

## 我的理解

迭代器需要实现__next__和__iter__，iter实现返回一个迭代器，next实现“推进并取值”。这里需要iter的原因是iter是for循环对于可迭代对象的常规入口，for循环执行时会先通过iter拿到一个迭代器，然后在每次循环都执行这个迭代器的next，如果捕获到结束异常抛出就退出。生成器属于迭代器，用yield简单地实现迭代效果。迭代器和生成器都是一次性的，迭代完就空了，想再次使用就得重新构建，这是他们和list(每次新迭代都新建新迭代器，本身是可迭代对象)的区别。

Iterable          ← 可迭代对象：有 __iter__，能被 for
    ├── Iterator      ← 迭代器：多一个 __next__，记住位置
    │   └── Generator ← 生成器：用 yield 自动实现的迭代器
    └── list/str/dict ← 普通可迭代对象：需要 iter() 转成迭代器



## 一个例子
```python
# 迭代器方式：需要类，手动管理状态
class Squares:
    def __init__(self, n):
        self.n = n
        self.i = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        result = self.i ** 2
        self.i += 1
        return result

# 生成器方式：简洁直观
def squares(n):
    for i in range(n):
        yield i ** 2

# 两者用法完全相同
for x in Squares(5): print(x)
for x in squares(5): print(x)


#---------------------------------------------------------------------

#下面的代码显示了python中list的实现的大概原理，这也是list可以反复迭代的原因
class SquaresIterable:
    def __init__(self, n):
        self.n = n
    
    def __iter__(self):
        # 返回一个全新的迭代器，而不是自己
        return SquaresIterator(self.n)

# 迭代器：只负责"逐个取值"
class SquaresIterator:
    def __init__(self, n):
        self.n = n
        self.i = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i >= self.n:
            raise StopIteration
        result = self.i ** 2
        self.i += 1
        return result