---
主题: 手写简易LRU缓存器
分类: python
日期: 2026-06-15
---


## 一句话定义

LRU（Least Recently Used）缓存器是一种在容量满时淘汰最久未被访问数据的缓存结构，用哈希表实现 O(1) 查找，用双向链表维护访问时序。

## 我的理解

手写LRU cache关键点在于双向链表只关心前后是谁，不关心怎么找；哈希表则负责找，并且保存每个节点的引用。单用哈希表，查找是 O(1) 但没法知道谁最久没用过；单用链表，能维持顺序但查找得 O(n) 遍历。所以把两者结合：哈希表存 key 到链表节点的映射，负责找；双向链表只负责串起前后节点，维护"谁最近用过"的顺序。我一开始踩的坑就是想只用链表，每次 get 都从头遍历找 key，结果复杂度退化成 O(n)。改成哈希表直接定位节点后，挪动节点到头部也是 O(1)，整体就达标了。链表用哨兵头尾节点（dummy head/tail）能省掉很多空指针判断，这是个实用技巧。

## 一个例子

```python
class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRU_cache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = {}               # 哈希表：key → Node
        self.head = Node()            # 哨兵头（最近使用侧）
        self.tail = Node()            # 哨兵尾（最久未用侧）
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):          # 双向链表删除：只改四个指针
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node):     # 插到头部 = 标记为最近使用
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_head(self, node):    # 访问过 → 移到头部
        self._remove(node)
        self._add_to_head(node)

    def _pop_tail(self):              # 踢掉尾部 = 淘汰最久未用
        node = self.tail.prev
        self._remove(node)
        return node

    def get(self, key):
        if key not in self.cache:
            return -1
        self._move_to_head(self.cache[key])
        return self.cache[key].val

    def put(self, key, value):
        if key in self.cache:
            self.cache[key].val = value
            self._move_to_head(self.cache[key])
            return
        node = Node(key, value)
        self.cache[key] = node
        self._add_to_head(node)
        if len(self.cache) > self.cap:
            removed = self._pop_tail()
            del self.cache[removed.key]
```

## 关联

- [[python-字典与哈希表]]
- [[0141-环形链表]]
- [[0155-最小栈]]
