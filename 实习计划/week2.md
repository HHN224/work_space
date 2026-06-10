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


2.二叉树最大深度：
给定一个二叉树 root ，返回其最大深度。
二叉树的 最大深度 是指从根节点到最远叶子节点的最长路径上的节点数。

    这题其实就是递归就好了，但我一开始真的想太多了，一直想要复杂地实现maxDepth的内容，但实际上只需要递归到叶子节点的外面一个，就会发现这个返回了一个空的root，那么空的root就会返回数值0，所以事情就相当简单了

        if not root:
            return 0

        left_depth = self.maxDepth(root.left)
        right_depth = self.maxDepth(root.right)
        return max(left_depth, right_depth) + 1


3.翻转二叉树：
给你一棵二叉树的根节点 root ，翻转这棵二叉树，并返回其根节点。

    这题其实就比较简单了，因为和上一题是一起做的，所以自己花了点时间没看题解就写出来最优解了，实际上对于二叉树的递归貌似都有些类似的点，都是左边和右边都调用自己这个函数，然后下面一行去实现一些简单的解法即可;
    ps:后来又发现了一种迭代的算法，是广度优先的，也贴在下面了，只是变成了用队列来处理，也很简单

    dfs：
        if not root:
            return root
        root.left = self.invertTree(root.left)
        root.right = self.invertTree(root.right)
        root.left, root.right = root.right, root.left
        return root

    bfs:
        if not root:
            return root
        queue = [root]
        while queue:
            node = queue.pop(0)
            node.left, node.right = node.right, node.left
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return root


4.岛屿数量：
给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。
岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。
此外，你可以假设该网格的四条边均被水包围。

    这题除了数组越界的情况没考虑周全，整体做下来还是比较顺的，但一开始用的递归dps对于我来讲比较好想但是耗时较长，基本在超时边缘了。所以后面去参考了一个迭代dps然后重写了一遍，可能某种程度上更好想（？），毕竟不用递归，也是和上一题差不多，用了模拟栈啊模拟队列一类的东西


    递归dps：
        def widespread(i,j):
            direct = [[0,1],[0,-1],[1,0],[-1,0]]
            if i >= x or j >= y or i < 0 or j < 0:
                return
            else: 
                if grid[j][i] == '0':
                    return
                grid[j][i] = '0'
                n = 0
                while n < 4:
                    i_move = direct[n][0]
                    j_move = direct[n][1]
                    ni, nj = i+i_move, j+j_move
                    widespread(ni, nj)
                    n += 1
            return

        y = len(grid)
        x = len(grid[0])
        count = 0
        for i in range(x):
            for j in range(y):
                if grid[j][i] == '1':
                    count += 1
                    widespread(i,j)
        return count

    迭代dps：
        if not grid or not grid[0]:
            return 0
        rows = len(grid)
        colums = len(grid[0])
        count = 0
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        for j in range(rows):
            for i in range(colums):
                if grid[j][i] == '1':
                    stack = [(j,i)]
                    grid[j][i] = '0'
                    count += 1
                    while stack:
                        r, c = stack.pop()
                        for dr, dc in dirs:
                            nr, nc = r+dr, c+dc
                            if 0 <= nr < rows and 0 <= nc < colums and grid[nr][nc] == '1':
                                grid[nr][nc] = '0'
                                stack.append((nr,nc))
        return count


            
            
        