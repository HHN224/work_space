class Node:
    def __init__(self, key=0, val=0):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRU_cache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = {}
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _move_to_head(self, node):
        self._remove(node)
        self._add_to_head(node)

    def _pop_tail(self):
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

