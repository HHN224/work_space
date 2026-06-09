1.有效的括号：
给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s ，判断字符串是否有效。
有效字符串需满足：
左括号必须用相同类型的右括号闭合。
左括号必须以正确的顺序闭合。
每个右括号都有一个对应的相同类型的左括号。

    这个算是这段时间做过最简单的了hh，基本上第一时间就想到了要用栈，卡的点主要是语法和不会用字典，其实这里用字典更快，而且可拓展性更强，现在这样可读性强但是拓展性很差，附上ai写的字典思路。

    我写的：
        stack = []
        for i in range(len(s)):
            entering = s[i]
            if len(stack) == 0:
                stack.append(entering)
                continue
            up = stack[-1]
            if entering == ")" and up == "(" or entering == "]" and up == "[" or entering == "}" and up == "{":
                stack.pop()
            else:
                stack.append(entering)
        is_empty = (len(stack) == 0)
        if is_empty:
            return True
        else:
            return False

    ai：
        stack = []
        match = {')':'(', ']':'[', '}':'{'}
        for c in s:
            if c not in match:
                # 左括号直接入栈
                stack.append(c)
            else:
                # 右括号，栈空/栈顶不匹配直接False
                if not stack or stack.pop() != match[c]:
                    return False
        return not stack



2.最小栈：
设计一个支持 push ，pop ，top 操作，并能在常数时间内检索到最小元素的栈。
实现 MinStack 类:
MinStack() 初始化堆栈对象。
void push(int value) 将元素 value 推入堆栈。
void pop() 删除堆栈顶部的元素。
int top() 获取堆栈顶部的元素。
int getMin() 获取堆栈中的最小元素。

    这题一开始想复杂了，想着在getmin里面每次都排序，然后获取第一个元素，然后超时了就一直在优化getmin啥的。其实后来发现完全不用，只需要多一个min栈，每次push的值比top低就入栈，每次pop到top的相同值就把min栈的top也pop了，这样一直取min栈的栈顶就是最小值。


class MinStack(object):

    def __init__(self):
        self.data = []
        self.min = []
        

    def push(self, val):
        """
        :type val: int
        :rtype: None
        """
        self.data.append(val)

        if not self.min or val <= self.min[-1]:
            self.min.append(val)
        

    def pop(self):
        """
        :rtype: None
        """
        if self.data.pop() == self.min[-1]:
            self.min.pop()
        

    def top(self):
        """
        :rtype: int
        """
        return self.data[-1]
        

    def getMin(self):
        """
        :rtype: int
        """
        return self.min[-1]
