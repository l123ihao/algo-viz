# -*- coding: utf-8 -*-
"""
算法可视化 —— 二分查找 / 排序算法逐步执行可视化工具

功能：
  * 内置模板：二分查找、线性查找、冒泡排序、选择排序、插入排序
  * 代码可自由修改（必须定义 solve(nums, target) 函数）
  * 逐步执行：高亮"下一步将要执行"的行，数组上方显示 l/r/mid/i/j 等指针
  * 打开 .py 文件后停留在该文件，不会跳回默认模板

零第三方依赖：只用 Python 标准库（tkinter + sys.settrace）。
"""

import ast
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ---------------------------------------------------------------------------
# 内置算法模板
# ---------------------------------------------------------------------------

# 供 C/C++、Java 模拟模式使用的等价 Python 演示脚本
_PY_BINARY = '''def solve(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            l = mid + 1
        else:
            r = mid - 1
    return -1
'''

_PY_BUBBLE = '''def solve(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(0, n - i - 1):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
    return nums
'''

_PY_LIST_REVERSE = '''def solve(head, target):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
'''

_PY_MERGE = '''def solve(head, head2):
    dummy = ListNode(0)
    cur = dummy
    while head and head2:
        if head.val <= head2.val:
            cur.next = head
            head = head.next
        else:
            cur.next = head2
            head2 = head2.next
        cur = cur.next
    cur.next = head if head else head2
    return dummy.next
'''

# 链表模板共用的准备代码：定义 ListNode、把输入构建成 head
_LISTNODE_SETUP = '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build_list(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next
'''

_LIST_SETUP = _LISTNODE_SETUP + '''
head = build_list(nums)
'''

# 用户代码已自带 ListNode、但没有 build_list 时，只补一个 build_list
_BUILD_LIST_SETUP = '''def build_list(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next
'''

# 合并两个有序链表：构建 head 和 head2
_MERGE_SETUP = '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build_list(vals):
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next

head = build_list(nums)
head2 = build_list(nums2 if nums2 is not None else [])
'''

# 环形链表：target 表示环入口下标（-1/空 = 无环）
_CYCLE_SETUP = '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build_list_with_cycle(vals, pos):
    nodes = [ListNode(v) for v in vals]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    if 0 <= pos < len(nodes):
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None

head = build_list_with_cycle(nums, target if target is not None else -1)
'''

# 每个模板字段说明：
#   lang       - python：真正执行；cpp/java：模拟模式
#   code       - 显示在编辑器里的代码
#   python_ref - 模拟模式下真正执行的等价 Python 脚本（仅 cpp/java）
#   line_map   - 模拟模式下 python_ref 行号 -> 显示代码行号
TEMPLATES = {
    'Python - 自定义代码': {
        'lang': 'python',
        'nums': '1 3 5 7 9',
        'target': '7',
        'code': '''# 自定义代码模板：把下面的 solve 改成你自己的算法即可运行。
# 数组类：def solve(nums, target):   （或 def solve(nums):）
# 链表类：def solve(head, target):   （无需自己定义 ListNode）
# 合并两个链表：def solve(head, head2):
#
# 也可以不写 solve，直接把整个文件当主程序写，
# 例如：for i in range(len(nums)): print(nums[i])
def solve(nums, target):
    # 在这里写你的代码
    return -1
''',
    },
    'Python - 二分查找': {
        'lang': 'python',
        'nums': '1 3 5 7 9 11 13 15',
        'target': '7',
        'code': '''def solve(nums, target):
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            l = mid + 1
        else:
            r = mid - 1
    return -1
''',
    },
    'Python - 线性查找': {
        'lang': 'python',
        'nums': '1 3 5 7 9 11 13 15',
        'target': '7',
        'code': '''def solve(nums, target):
    for i in range(len(nums)):
        if nums[i] == target:
            return i
    return -1
''',
    },
    'Python - 冒泡排序': {
        'lang': 'python',
        'nums': '29 10 14 37 13',
        'target': '',
        'code': '''def solve(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(0, n - i - 1):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
    return nums
''',
    },
    'Python - 选择排序': {
        'lang': 'python',
        'nums': '29 10 14 37 13',
        'target': '',
        'code': '''def solve(nums, target):
    n = len(nums)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if nums[j] < nums[min_idx]:
                min_idx = j
        nums[i], nums[min_idx] = nums[min_idx], nums[i]
    return nums
''',
    },
    'Python - 插入排序': {
        'lang': 'python',
        'nums': '5 2 4 6 1 3',
        'target': '',
        'code': '''def solve(nums, target):
    n = len(nums)
    for i in range(1, n):
        key = nums[i]
        j = i - 1
        while j >= 0 and nums[j] > key:
            nums[j + 1] = nums[j]
            j -= 1
        nums[j + 1] = key
    return nums
''',
    },
    'C++ - 二分查找': {
        'lang': 'cpp',
        'nums': '1 3 5 7 9 11 13 15',
        'target': '7',
        'code': '''int solve(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    while (l <= r) {
        int mid = (l + r) / 2;
        if (nums[mid] == target) {
            return mid;
        } else if (nums[mid] < target) {
            l = mid + 1;
        } else {
            r = mid - 1;
        }
    }
    return -1;
}
''',
        'python_ref': _PY_BINARY,
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9,
                     10: 10, 11: 13},
    },
    'C++ - 冒泡排序': {
        'lang': 'cpp',
        'nums': '29 10 14 37 13',
        'target': '',
        'code': '''void solve(vector<int>& nums, int target) {
    int n = nums.size();
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (nums[j] > nums[j + 1]) {
                swap(nums[j], nums[j + 1]);
            }
        }
    }
    return;
}
''',
        'python_ref': _PY_BUBBLE,
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 10},
    },
    'Java - 二分查找': {
        'lang': 'java',
        'nums': '1 3 5 7 9 11 13 15',
        'target': '7',
        'code': '''int solve(int[] nums, int target) {
    int l = 0, r = nums.length - 1;
    while (l <= r) {
        int mid = (l + r) / 2;
        if (nums[mid] == target) {
            return mid;
        } else if (nums[mid] < target) {
            l = mid + 1;
        } else {
            r = mid - 1;
        }
    }
    return -1;
}
''',
        'python_ref': _PY_BINARY,
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9,
                     10: 10, 11: 13},
    },
    'Java - 冒泡排序': {
        'lang': 'java',
        'nums': '29 10 14 37 13',
        'target': '',
        'code': '''void solve(int[] nums, int target) {
    int n = nums.length;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (nums[j] > nums[j + 1]) {
                int temp = nums[j];
                nums[j] = nums[j + 1];
                nums[j + 1] = temp;
            }
        }
    }
    return;
}
''',
        'python_ref': _PY_BUBBLE,
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 12},
    },
    'Python - 链表反转': {
        'lang': 'python',
        'nums': '1 2 3 4 5',
        'target': '',
        'code': '''def solve(head, target):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
''',
        'setup': _LIST_SETUP,
        'entry': 'solve(head, target)',
    },
    'Python - 链表删除节点': {
        'lang': 'python',
        'nums': '1 2 6 3 4 5 6',
        'target': '6',
        'code': '''def solve(head, target):
    dummy = ListNode(0)
    dummy.next = head
    prev = dummy
    cur = head
    while cur:
        if cur.val == target:
            prev.next = cur.next
            cur = cur.next
        else:
            prev = cur
            cur = cur.next
    return dummy.next
''',
        'setup': _LIST_SETUP,
        'entry': 'solve(head, target)',
    },
    'Python - 单调栈': {
        'lang': 'python',
        'nums': '2 1 2 4 3',
        'target': '',
        'code': '''def solve(nums, target):
    stack = []
    result = [-1] * len(nums)
    for i in range(len(nums)):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)
    return result
''',
    },
    'C++ - 链表反转': {
        'lang': 'cpp',
        'nums': '1 2 3 4 5',
        'target': '',
        'code': '''ListNode* solve(ListNode* head, int target) {
    ListNode* prev = nullptr;
    ListNode* cur = head;
    while (cur) {
        ListNode* nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }
    return prev;
}
''',
        'python_ref': _PY_LIST_REVERSE,
        'setup': _LIST_SETUP,
        'entry': 'solve(head, target)',
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 10},
    },
    'Java - 链表反转': {
        'lang': 'java',
        'nums': '1 2 3 4 5',
        'target': '',
        'code': '''ListNode solve(ListNode head, int target) {
    ListNode prev = null;
    ListNode cur = head;
    while (cur != null) {
        ListNode nxt = cur.next;
        cur.next = prev;
        prev = cur;
        cur = nxt;
    }
    return prev;
}
''',
        'python_ref': _PY_LIST_REVERSE,
        'setup': _LIST_SETUP,
        'entry': 'solve(head, target)',
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 10},
    },
    'Python - 两数之和 II': {
        'lang': 'python',
        'nums': '2 7 11 15',
        'target': '9',
        'code': '''def solve(nums, target):
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return [l, r]
        elif s < target:
            l += 1
        else:
            r -= 1
    return [-1, -1]
''',
    },
    'Python - 长度最小的子数组': {
        'lang': 'python',
        'nums': '2 3 1 2 4 3',
        'target': '7',
        'code': '''def solve(nums, target):
    l = 0
    total = 0
    ans = len(nums) + 1
    for r in range(len(nums)):
        total += nums[r]
        while total >= target:
            ans = min(ans, r - l + 1)
            total -= nums[l]
            l += 1
    return 0 if ans == len(nums) + 1 else ans
''',
    },
    'Python - 每日温度': {
        'lang': 'python',
        'nums': '73 74 75 71 69 72 76 73',
        'target': '',
        'code': '''def solve(nums, target):
    stack = []
    result = [0] * len(nums)
    for i in range(len(nums)):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)
    return result
''',
    },
    'Python - 合并两个有序链表': {
        'lang': 'python',
        'nums': '1 2 4',
        'nums2': '1 3 4',
        'target': '',
        'needs_second': True,
        'code': '''def solve(head, head2):
    dummy = ListNode(0)
    cur = dummy
    while head and head2:
        if head.val <= head2.val:
            cur.next = head
            head = head.next
        else:
            cur.next = head2
            head2 = head2.next
        cur = cur.next
    cur.next = head if head else head2
    return dummy.next
''',
        'setup': _MERGE_SETUP,
        'entry': 'solve(head, head2)',
    },
    'Python - 环形链表': {
        'lang': 'python',
        'nums': '3 2 0 -4',
        'target': '1',
        'code': '''def solve(head, target):
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
''',
        'setup': _CYCLE_SETUP,
        'entry': 'solve(head, target)',
    },
    'Python - 删除链表倒数第 N 个节点': {
        'lang': 'python',
        'nums': '1 2 3 4 5',
        'target': '2',
        'code': '''def solve(head, target):
    dummy = ListNode(0)
    dummy.next = head
    fast = dummy
    slow = dummy
    for _ in range(target + 1):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next
''',
        'setup': _LIST_SETUP,
        'entry': 'solve(head, target)',
    },
    'C++ - 合并两个有序链表': {
        'lang': 'cpp',
        'nums': '1 2 4',
        'nums2': '1 3 4',
        'target': '',
        'needs_second': True,
        'code': '''ListNode* solve(ListNode* head, ListNode* head2) {
    ListNode* dummy = new ListNode(0);
    ListNode* cur = dummy;
    while (head && head2) {
        if (head->val <= head2->val) {
            cur->next = head;
            head = head->next;
        } else {
            cur->next = head2;
            head2 = head2->next;
        }
        cur = cur->next;
    }
    cur->next = head ? head : head2;
    return dummy->next;
}
''',
        'python_ref': _PY_MERGE,
        'setup': _MERGE_SETUP,
        'entry': 'solve(head, head2)',
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9,
                     10: 10, 11: 12, 12: 14, 13: 15},
    },
    'Java - 合并两个有序链表': {
        'lang': 'java',
        'nums': '1 2 4',
        'nums2': '1 3 4',
        'target': '',
        'needs_second': True,
        'code': '''ListNode solve(ListNode head, ListNode head2) {
    ListNode dummy = new ListNode(0);
    ListNode cur = dummy;
    while (head != null && head2 != null) {
        if (head.val <= head2.val) {
            cur.next = head;
            head = head.next;
        } else {
            cur.next = head2;
            head2 = head2.next;
        }
        cur = cur.next;
    }
    cur.next = head != null ? head : head2;
    return dummy.next;
}
''',
        'python_ref': _PY_MERGE,
        'setup': _MERGE_SETUP,
        'entry': 'solve(head, head2)',
        'line_map': {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9,
                     10: 10, 11: 12, 12: 14, 13: 15},
    },
}


# 指针变量名 -> 颜色
POINTER_COLORS = {
    'l': '#e53935', 'lo': '#e53935', 'left': '#e53935', 'low': '#e53935',
    'start': '#e53935',
    'r': '#1e88e5', 'hi': '#1e88e5', 'right': '#1e88e5', 'high': '#1e88e5',
    'end': '#1e88e5',
    'mid': '#43a047', 'm': '#43a047',
    'i': '#fb8c00',
    'j': '#8e24aa',
    'min_idx': '#00897b', 'min_index': '#00897b', 'pos': '#00897b',
    'p': '#6d4c41', 'q': '#6d4c41',
    'cur': '#546e7a', 'idx': '#546e7a', 'index': '#546e7a',
}
POINTER_NAMES = set(POINTER_COLORS.keys())
# 链表指针变量名 -> 颜色
LL_POINTER_COLORS = {
    'head': '#1e88e5', 'dummy': '#8e24aa', 'prev': '#e53935',
    'cur': '#fb8c00', 'curr': '#fb8c00', 'nxt': '#43a047',
    'tail': '#00897b', 'p': '#6d4c41', 'q': '#6d4c41',
    'slow': '#3949ab', 'fast': '#d81b60',
}
# 栈变量名
STACK_NAMES = {'stack', 'st', 'stk', 's', 'mono_stack', 'monostack'}
# 变量面板显示顺序
VAR_ORDER = ['nums', 'arr', 'array', 'a', 'target', 'head', 'dummy',
             'prev', 'cur', 'curr', 'nxt', 'tail', 'l', 'r', 'mid', 'm',
             'i', 'j', 'min_idx', 'min_index', 'key', 'n', 'stack', 'st',
             'result']


# ---------------------------------------------------------------------------
# 执行引擎：用 sys.settrace 在每一行暂停，抓取变量快照
# ---------------------------------------------------------------------------

class _StopExecution(Exception):
    """用户点了“停止”。"""


def _is_listnode(v):
    """判断对象是否像链表节点（有 val 和 next 属性）。"""
    return (hasattr(v, 'val') and hasattr(v, 'next')
            and not isinstance(v, (list, tuple, dict, str, bytes)))


def _serialize_listnode(node):
    """把链表节点序列化成可绘制结构（沿 next 走，防环，记录环入口）。"""
    values = []
    ids = []
    seen = set()
    cycle_to = None
    cur = node
    while cur is not None:
        cid = id(cur)
        if cid in seen:
            if cid in ids:
                cycle_to = ids.index(cid)
            break
        seen.add(cid)
        values.append(getattr(cur, 'val', None))
        ids.append(cid)
        cur = getattr(cur, 'next', None)
    return {'__kind__': 'linked_list',
            'self_id': id(node),
            'values': values,
            'ids': ids,
            'cycle_to': cycle_to}


def infer_setup_and_entry(fn, env):
    """根据用户自定义代码里的 solve 签名，推断执行环境与入口表达式。

    约定（与使用说明一致）：
      * solve(nums, target) / solve(nums)      -> 数组类，无需准备代码
      * solve(head, target) / solve(head)      -> 链表类，自动注入 ListNode
                                                 并把 nums 构建成 head
      * solve(head, head2)                     -> 合并两个链表，nums/nums2
                                                 分别构建成 head/head2
    返回 (setup, entry)；setup 为要追加执行的准备代码（可能为空字符串）。
    """
    args = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    setup = ''
    if args and args[0] == 'head':
        # 链表类：用户代码没定义 ListNode 时补上，缺 build_list 时补上
        if 'ListNode' not in env:
            setup += _LISTNODE_SETUP
        elif 'build_list' not in env:
            setup += _BUILD_LIST_SETUP
        if len(args) >= 2 and args[1] == 'head2':
            setup += ('head = build_list(nums)\n'
                      'head2 = build_list(nums2 if nums2 is not None else [])\n')
            entry = 'solve(head, head2)'
        else:
            setup += 'head = build_list(nums)\n'
            entry = 'solve(head, target)' if len(args) >= 2 else 'solve(head)'
    else:
        # 数组类或其他参数名：位置传参，不依赖参数名
        if len(args) == 0:
            entry = 'solve()'
        elif len(args) == 1:
            entry = 'solve(nums)'
        else:
            entry = 'solve(nums, target)'
    return setup, entry


class AlgorithmStepper:
    def __init__(self):
        self.q = queue.Queue()          # 快照/结果队列（线程安全）
        self.resume = threading.Event()  # GUI 放行信号
        self.paused = threading.Event()  # 已暂停、等待放行的信号
        self.stop_flag = threading.Event()
        self.code_obj = None

    def run(self, code, nums, target, setup=None,
            entry=None, nums2=None):
        """在后台线程中编译并执行用户代码，每行暂停。

        setup：执行用户代码前先执行的准备代码（如定义 ListNode、构建链表）。
        entry：实际调用的入口表达式，例如 solve(head, target)。
        nums2：第二组数据（合并两个链表等场景使用，None 表示空）。

        两种模式：
          * 代码里定义了 solve 函数 -> 只逐步执行 solve（模板 / 自定义代码）
          * 代码里没有 solve 函数  -> 任意代码模式：把整个文件当作
            主程序逐步执行，顶层语句和文件内定义的函数都会逐行高亮。
        """
        try:
            tree = ast.parse(code)
            compiled = compile(tree, '<algo>', 'exec')
        except SyntaxError as e:
            self.q.put({'type': 'error',
                        'message': '代码编译失败：SyntaxError: %s' % e})
            return

        env = {'nums': nums, 'target': target, 'nums2': nums2}
        has_solve = any(isinstance(node, ast.FunctionDef)
                        and node.name == 'solve' for node in tree.body)

        if has_solve:
            self._run_solve_mode(compiled, env, setup, entry)
        else:
            self._run_script_mode(tree, compiled, env)

    def _run_solve_mode(self, compiled, env, setup, entry):
        """函数模式：执行代码拿到 solve，推断环境后逐步执行 solve。"""
        try:
            exec(compiled, env)
        except Exception as e:
            self.q.put({'type': 'error',
                        'message': '代码运行失败：%s: %s' % (type(e).__name__, e)})
            return

        fn = env.get('solve')
        if not callable(fn):
            self.q.put({'type': 'error',
                        'message': '代码里没有定义 solve 函数'})
            return

        if setup is None or entry is None:
            auto_setup, auto_entry = infer_setup_and_entry(fn, env)
            setup = auto_setup if setup is None else setup
            entry = auto_entry if entry is None else entry

        if setup:
            try:
                exec(compile(setup, '<setup>', 'exec'), env)
            except Exception as e:
                self.q.put({'type': 'error',
                            'message': '准备代码执行失败：%s: %s'
                                       % (type(e).__name__, e)})
                return

        self.code_obj = fn.__code__
        old_trace = sys.gettrace()

        def tracer(frame, event, arg):
            if frame.f_code is self.code_obj:
                if self.stop_flag.is_set():
                    raise _StopExecution()
                if event == 'line':
                    self._pause(frame)
                elif event == 'return':
                    result = arg
                    if _is_listnode(result):
                        result = _serialize_listnode(result)
                    self.q.put({'type': 'done',
                                'result': result,
                                'vars': self._snapshot_vars(frame)})
                    return None
            return tracer

        sys.settrace(tracer)
        try:
            eval(entry, env)
        except _StopExecution:
            self.q.put({'type': 'stopped'})
        except Exception as e:
            self.q.put({'type': 'error',
                        'message': '%s: %s' % (type(e).__name__, e)})
        finally:
            sys.settrace(old_trace)

    def _run_script_mode(self, tree, compiled, env):
        """任意代码模式：逐步执行整个文件（含顶层语句和自定义函数）。"""
        if not tree.body:
            self.q.put({'type': 'error',
                        'message': '代码为空，请输入要运行的 Python 代码'})
            return

        # 用到 ListNode / build_list 但没定义时，自动注入链表环境，
        # 方便直接写链表代码（例如 head = build_list(nums)）
        defines_listnode = any(isinstance(node, ast.ClassDef)
                               and node.name == 'ListNode'
                               for node in tree.body)
        defines_build_list = any(isinstance(node, ast.FunctionDef)
                                 and node.name == 'build_list'
                                 for node in tree.body)
        used_names = {node.id for node in ast.walk(tree)
                      if isinstance(node, ast.Name)}
        uses_listnode = 'ListNode' in used_names
        uses_build_list = 'build_list' in used_names
        if (uses_listnode or uses_build_list) and not defines_listnode:
            try:
                exec(compile(_LISTNODE_SETUP, '<setup>', 'exec'), env)
            except Exception as e:
                self.q.put({'type': 'error',
                            'message': '准备代码执行失败：%s: %s'
                                       % (type(e).__name__, e)})
                return
        elif uses_build_list and not defines_build_list:
            try:
                exec(compile(_BUILD_LIST_SETUP, '<setup>', 'exec'), env)
            except Exception as e:
                self.q.put({'type': 'error',
                            'message': '准备代码执行失败：%s: %s'
                                       % (type(e).__name__, e)})
                return

        self.code_obj = compiled
        old_trace = sys.gettrace()

        def script_tracer(frame, event, arg):
            if self.stop_flag.is_set():
                raise _StopExecution()
            # 只跟踪本次打开的文件里的代码（顶层 + 其中定义的函数）
            if frame.f_code.co_filename == '<algo>':
                if event == 'line':
                    self._pause(frame)
            return script_tracer

        sys.settrace(script_tracer)
        try:
            exec(compiled, env)
        except _StopExecution:
            self.q.put({'type': 'stopped'})
            return
        except Exception as e:
            self.q.put({'type': 'error',
                        'message': '%s: %s' % (type(e).__name__, e)})
            return
        finally:
            sys.settrace(old_trace)

        # 整个文件执行完毕（模块级变量都在 env 里）
        self.q.put({'type': 'done',
                    'result': None,
                    'vars': self._snapshot_mapping(env)})

    def _pause(self, frame):
        self.q.put({'type': 'line',
                    'lineno': frame.f_lineno,
                    'vars': self._snapshot_vars(frame)})
        self.paused.set()           # 通知 GUI：已经暂停，等待放行
        self.resume.wait()          # 阻塞，直到 GUI 点“下一步”
        self.resume.clear()
        self.paused.clear()

    @staticmethod
    def _snapshot_vars(frame):
        return AlgorithmStepper._snapshot_mapping(frame.f_locals)

    @staticmethod
    def _snapshot_mapping(mapping):
        """把变量字典转换成可发给 GUI 的快照（跳过不可绘制对象）。"""
        out = {}
        for k, v in mapping.items():
            if k.startswith('__'):
                continue
            if isinstance(v, (int, float, str, bool)) or v is None:
                out[k] = v
            elif isinstance(v, list):
                out[k] = list(v)
            elif isinstance(v, tuple):
                out[k] = tuple(v)
            elif isinstance(v, dict):
                out[k] = dict(v)
            elif _is_listnode(v):
                out[k] = _serialize_listnode(v)
        return out


# ---------------------------------------------------------------------------
# 工具函数：从变量快照里找数组和指针
# ---------------------------------------------------------------------------

def get_array(vars_):
    """返回 (数组变量名, 数组)。优先常见数组名，否则取第一个 list。"""
    preferred = ['nums', 'arr', 'array', 'a', 'lst', 'data', 'items',
                 'numbers', 'list']
    for name in preferred:
        v = vars_.get(name)
        if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
            return name, v
    for name, v in vars_.items():
        if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
            return name, v
    return None, None


def get_pointers(vars_, arr):
    """把名字像指针、值落在数组下标范围内的 int 变量识别为指针。"""
    pointers = []
    for name, value in vars_.items():
        if name in ('target', 'key', 'n'):
            continue
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and name in POINTER_NAMES \
                and 0 <= value < len(arr):
            pointers.append((name, value, POINTER_COLORS.get(name, '#546e7a')))
    return pointers


def get_stack(vars_):
    """识别栈变量（名字像栈的 list）。"""
    for name in STACK_NAMES:
        v = vars_.get(name)
        if isinstance(v, list) and all(isinstance(x, (int, float))
                                       for x in v):
            return name, v
    return None, None


def fmt_value(v):
    if isinstance(v, dict) and v.get('__kind__') == 'linked_list':
        return ' -> '.join(map(str, v.get('values', []))) + ' -> None'
    if isinstance(v, list):
        if len(v) > 12:
            return '[' + ', '.join(map(str, v[:12])) + ', ...]'
        return '[' + ', '.join(map(str, v)) + ']'
    if isinstance(v, float):
        return '%g' % v
    return str(v)


def sorted_var_names(vars_):
    def rank(k):
        try:
            return VAR_ORDER.index(k)
        except ValueError:
            return 100
    return sorted(vars_.keys(), key=lambda k: (rank(k), k))


def parse_nums(text):
    text = text.strip().replace(',', ' ')
    if not text:
        return None
    try:
        return [int(x) for x in text.split()]
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# 数组可视化 Canvas
# ---------------------------------------------------------------------------

class ArrayView:
    def __init__(self, canvas):
        self.canvas = canvas
        self.last = None
        self._redraw_job = None
        canvas.bind('<Configure>', self._on_resize)

    def draw(self, arr, pointers, highlight=()):
        """直接画数组（旧接口，保留兼容）。"""
        self.last = ('array', list(arr), list(pointers), set(highlight))
        self._render()

    def draw_state(self, vars_, highlight=()):
        """统一入口：根据变量快照自动选择数组/栈/链表视图。"""
        self.last = ('state', dict(vars_), set(highlight))
        self._render()

    def _on_resize(self, _event):
        if self._redraw_job is not None:
            self.canvas.after_cancel(self._redraw_job)
        self._redraw_job = self.canvas.after(80, self._render)

    def _render(self):
        if self.last is None:
            return
        if self.last[0] == 'array':
            _, arr, pointers, highlight = self.last
            self._render_array(arr, pointers, highlight)
        else:
            _, vars_, highlight = self.last
            self._render_state(vars_, highlight)

    # ---------------- 数组 ----------------

    def _render_array(self, arr, pointers, highlight, y_offset=30):
        c = self.canvas
        c.delete('all')
        w = max(10, c.winfo_width())
        h = max(10, c.winfo_height())

        n = len(arr)
        if n == 0:
            c.create_text(w // 2, h // 2, text='数组为空',
                          font=('Microsoft YaHei UI', 14), fill='#78909c')
            return

        margin = 36
        gap = 6
        box_w = (w - 2 * margin - (n - 1) * gap) / n
        box_w = max(16, min(88, box_w))
        box_h = 56
        total_w = n * box_w + (n - 1) * gap
        x0 = (w - total_w) / 2
        y_top = y_offset + 16

        small_font = box_w < 34
        val_font = ('Consolas', 10 if small_font else 14, 'bold')
        idx_font = ('Consolas', 9 if small_font else 10)

        for i, val in enumerate(arr):
            x = x0 + i * (box_w + gap)
            fill, outline = '#f7f9fb', '#b0bec5'
            if i in highlight:
                fill, outline = '#fff3cd', '#e0a800'
            c.create_rectangle(x, y_top, x + box_w, y_top + box_h,
                               fill=fill, outline=outline, width=2)
            c.create_text(x + box_w / 2, y_top + box_h / 2, text=str(val),
                          font=val_font, fill='#263238')
            c.create_text(x + box_w / 2, y_top + box_h + 15, text=str(i),
                          font=idx_font, fill='#90a4ae')

        # 指针箭头：按 index 分组
        by_index = {}
        for name, idx, color in pointers:
            if 0 <= idx < n:
                by_index.setdefault(idx, []).append((name, color))

        arrow_base = y_top + box_h + 34
        for idx, lst in by_index.items():
            x = x0 + idx * (box_w + gap) + box_w / 2
            for k, (name, color) in enumerate(lst):
                start_x = x + (k - (len(lst) - 1) / 2.0) * 26
                end_y = arrow_base + 16
                c.create_line(start_x, arrow_base, x, end_y,
                              arrow=tk.LAST, fill=color, width=2)
                c.create_text(start_x, end_y + 14 + (k % 3) * 14, text=name,
                              font=('Consolas', 11, 'bold'), fill=color)

    # ---------------- 统一分派 ----------------

    def _render_state(self, vars_, highlight):
        c = self.canvas
        c.delete('all')
        w = max(10, c.winfo_width())
        h = max(10, c.winfo_height())

        ll = {k: v for k, v in vars_.items()
              if isinstance(v, dict) and v.get('__kind__') == 'linked_list'}
        if ll:
            self._render_linked_list(ll, vars_, w, h, highlight)
            return

        stack_name, stack = get_stack(vars_)
        arr_name, arr = get_array(vars_)
        if stack is not None:
            if arr is not None and arr_name != stack_name:
                self._render_array_and_stack(arr, stack, vars_, w, h,
                                             highlight)
            else:
                self._render_stack(stack, stack_name, w, h, top_y=30,
                                   bottom_y=h - 30)
            return

        if arr is not None:
            hl = set(highlight)
            lv = vars_.get('l')
            rv = vars_.get('r')
            if isinstance(lv, int) and not isinstance(lv, bool) \
                    and isinstance(rv, int) and not isinstance(rv, bool) \
                    and 0 <= lv <= rv < len(arr):
                hl.update(range(lv, rv + 1))
            self._render_array(arr, get_pointers(vars_, arr), hl)
        else:
            c.create_text(w // 2, h // 2,
                          text='当前没有可绘制的数组 / 链表 / 栈',
                          font=('Microsoft YaHei UI', 14), fill='#78909c')

    # ---------------- 栈 ----------------

    def _render_stack(self, stack, name, w, h, top_y=30, bottom_y=None):
        c = self.canvas
        if bottom_y is None:
            bottom_y = h - 30
        n = len(stack)
        c.create_text(w // 2, top_y, text='栈 %s（栈顶在上，%d 个元素）'
                      % (name, n),
                      font=('Microsoft YaHei UI', 12, 'bold'),
                      fill='#37474f')
        if n == 0:
            c.create_text(w // 2, (top_y + bottom_y) // 2, text='栈为空',
                          font=('Microsoft YaHei UI', 14), fill='#78909c')
            return
        box_w = 150
        gap = 6
        box_h = max(22, min(42, (bottom_y - top_y - 30) / n - gap))
        total_h = n * box_h + (n - 1) * gap
        x0 = w // 2 - box_w // 2
        y_bottom = bottom_y
        y_start = y_bottom - total_h
        for i in range(n):
            idx = n - 1 - i          # i=0 是栈顶
            y = y_start + i * (box_h + gap)
            is_top = (idx == n - 1)
            fill = '#e3f2fd' if is_top else '#f7f9fb'
            outline = '#1565c0' if is_top else '#b0bec5'
            c.create_rectangle(x0, y, x0 + box_w, y + box_h,
                               fill=fill, outline=outline, width=2)
            c.create_text(x0 + box_w / 2, y + box_h / 2,
                          text='%s [%d]' % (stack[idx], idx),
                          font=('Consolas', 12, 'bold'), fill='#263238')
            if is_top:
                c.create_text(x0 + box_w + 16, y + box_h / 2, text='栈顶',
                              anchor='w', font=('Microsoft YaHei UI', 11,
                                                'bold'), fill='#1565c0')

    # ---------------- 数组 + 栈 ----------------

    def _render_array_and_stack(self, arr, stack, vars_, w, h, highlight):
        c = self.canvas
        split = int(h * 0.52)
        hl = set(highlight)
        lv = vars_.get('l')
        rv = vars_.get('r')
        if isinstance(lv, int) and not isinstance(lv, bool) \
                and isinstance(rv, int) and not isinstance(rv, bool) \
                and 0 <= lv <= rv < len(arr):
            hl.update(range(lv, rv + 1))
        self._render_array(arr, get_pointers(vars_, arr), hl,
                           y_offset=4)
        c.create_line(10, split + 2, w - 10, split + 2,
                      fill='#cfd8dc', dash=(4, 4))
        stack_name = get_stack(vars_)[0] or 'stack'
        self._render_stack(stack, stack_name, w, h, top_y=split + 10,
                           bottom_y=h - 16)

    # ---------------- 链表 ----------------

    def _render_linked_list(self, ll_vars, vars_, w, h, highlight):
        c = self.canvas
        # 双链场景：反转（prev/cur）、合并（head/head2）
        if 'prev' in ll_vars and 'cur' in ll_vars:
            self._render_two_chains(ll_vars, vars_, w, h, highlight,
                                    ['prev', 'cur'])
            return
        if 'head' in ll_vars and 'head2' in ll_vars:
            self._render_two_chains(ll_vars, vars_, w, h, highlight,
                                    ['head', 'head2'])
            return

        def key_of(item):
            name = item[0]
            info = item[1]
            rank = 0 if name == 'head' else 1 if name == 'dummy' else 2
            return (rank, -len(info.get('values', [])))

        main_name, main_info = min(ll_vars.items(), key=key_of)
        values = main_info.get('values', [])
        ids = main_info.get('ids', [])

        c.create_text(w // 2, 18, text='链表（主链：%s）' % main_name,
                      font=('Microsoft YaHei UI', 12, 'bold'),
                      fill='#37474f')
        if not values:
            c.create_text(w // 2, h // 2, text='链表为空（None）',
                          font=('Microsoft YaHei UI', 14), fill='#78909c')
            return

        box_w = 58
        box_h = 44
        gap = 48
        y_top = 64
        centers, _ = self._draw_chain(main_info, main_name, w, y_top,
                                      box_w, box_h, gap, highlight)

        k = 0
        self._draw_ll_arrow(c, centers[0], main_name,
                            LL_POINTER_COLORS.get(main_name, '#546e7a'),
                            y_top, box_h, k)
        k += 1
        float_lines = []
        for name, info in ll_vars.items():
            if name == main_name:
                continue
            sid = info.get('self_id')
            if sid in ids:
                self._draw_ll_arrow(c, centers[ids.index(sid)], name,
                                    LL_POINTER_COLORS.get(name, '#546e7a'),
                                    y_top, box_h, k)
                k += 1
            else:
                vals = info.get('values', [])
                text = '%s -> %s' % (name,
                                      ' -> '.join(map(str, vals[:3]))
                                      + (' ...' if len(vals) > 3 else ''))
                float_lines.append(text)
        for name in ('prev', 'cur', 'curr', 'nxt', 'tail', 'head', 'dummy',
                     'slow', 'fast', 'p', 'q', 'head2'):
            if name in vars_ and vars_[name] is None:
                float_lines.append('%s = None' % name)

        fy = y_top + box_h + 52
        for line in float_lines:
            c.create_text(w // 2, fy, text=line,
                          font=('Consolas', 11), fill='#607d8b')
            fy += 18

    def _render_two_chains(self, ll_vars, vars_, w, h, highlight, pair):
        c = self.canvas
        box_w = 52
        box_h = 40
        gap = 44
        y_split = h // 2
        chain_data = []
        for idx, name in enumerate(pair):
            info = ll_vars.get(name)
            top = 26 if idx == 0 else y_split + 6
            centers, ids = self._draw_chain(info, name, w, top, box_w,
                                            box_h, gap, highlight)
            chain_data.append((name, centers, ids))
            if centers:
                self._draw_ll_arrow(c, centers[0], name,
                                    LL_POINTER_COLORS.get(name, '#546e7a'),
                                    top, box_h, 0)

        k = 0
        for name, info in ll_vars.items():
            if name in pair:
                continue
            sid = info.get('self_id')
            placed = False
            for (pname, centers, ids) in chain_data:
                if sid in ids:
                    top = 26 if pname == pair[0] else y_split + 6
                    self._draw_ll_arrow(
                        c, centers[ids.index(sid)], name,
                        LL_POINTER_COLORS.get(name, '#546e7a'),
                        top, box_h, 1 + (k % 2))
                    k += 1
                    placed = True
                    break
            if not placed and name in ('dummy', 'cur', 'curr', 'slow',
                                       'fast', 'nxt', 'tail'):
                vals = info.get('values', [])
                c.create_text(
                    w // 2, h - 24 - k * 15,
                    text='%s -> %s' % (name,
                                       ' -> '.join(map(str, vals[:3]))
                                       + (' ...' if len(vals) > 3 else '')),
                    font=('Consolas', 10), fill='#607d8b')
                k += 1

    def _draw_chain(self, info, name, w, top, box_w, box_h, gap, highlight):
        """画一条链，返回 (节点中心 x 列表, 节点 id 列表)。"""
        c = self.canvas
        if info is None:
            return [], []
        values = info.get('values', [])
        ids = info.get('ids', [])
        cycle_to = info.get('cycle_to')
        c.create_text(w // 2, top - 6, text=name,
                      font=('Consolas', 11, 'bold'),
                      fill=LL_POINTER_COLORS.get(name, '#546e7a'))
        if not values:
            c.create_text(w // 2, top + box_h / 2 + 4, text='%s = None' % name,
                          font=('Consolas', 12), fill='#78909c')
            return [], []
        n = len(values)
        total_w = n * box_w + (n - 1) * gap
        x0 = max(20, (w - total_w) / 2)
        y = top + 12
        centers = []
        for i, val in enumerate(values):
            x = x0 + i * (box_w + gap)
            fill = '#fff3cd' if i in highlight else '#f7f9fb'
            outline = '#e0a800' if i in highlight else '#b0bec5'
            c.create_rectangle(x, y, x + box_w, y + box_h,
                               fill=fill, outline=outline, width=2)
            c.create_text(x + box_w / 2, y + box_h / 2, text=str(val),
                          font=('Consolas', 12, 'bold'), fill='#263238')
            centers.append(x + box_w / 2)
            if i < n - 1:
                c.create_line(x + box_w + 3, y + box_h / 2,
                              x + box_w + gap - 3, y + box_h / 2,
                              arrow=tk.LAST, fill='#78909c', width=2)
        # 环回箭头：尾节点 -> 环入口
        if cycle_to is not None and 0 <= cycle_to < n:
            last_x = x0 + (n - 1) * (box_w + gap) + box_w / 2
            cy = centers[cycle_to]
            c.create_line(last_x, y + box_h, last_x, y + box_h + 16,
                          fill='#e53935', width=2)
            c.create_line(last_x, y + box_h + 16, cy, y + box_h + 16,
                          fill='#e53935', width=2)
            c.create_line(cy, y + box_h + 16, cy, y + box_h + 4,
                          arrow=tk.LAST, fill='#e53935', width=2)
            c.create_text((last_x + cy) / 2, y + box_h + 26, text='环入口',
                          font=('Microsoft YaHei UI', 9), fill='#e53935')
        return centers, ids

    def _draw_ll_arrow(self, c, cx, name, color, y_top, box_h, k):
        arrow_y = y_top - 12 - (k % 3) * 18
        c.create_line(cx, arrow_y, cx, y_top - 4, arrow=tk.LAST,
                      fill=color, width=2)
        c.create_text(cx, arrow_y - 11, text=name,
                      font=('Consolas', 10, 'bold'), fill=color)


# ---------------------------------------------------------------------------
# 主程序
# ---------------------------------------------------------------------------

class App:
    def __init__(self, root):
        self.root = root
        root.title('算法可视化 — 二分查找 / 排序')
        root.geometry('1180x780')
        root.minsize(960, 640)

        self.current_vars = None
        self.stepper = None
        self.thread = None
        self.running = False
        self.playing = False
        self.play_job = None
        self.poll_job = None
        self.step_count = 0
        self.current_template = None
        self.current_path = None
        self.line_map = None

        self.nums_var = tk.StringVar()
        self.nums2_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.speed_var = tk.DoubleVar(value=0.5)
        self.status_var = tk.StringVar(value='就绪')

        self._build_ui()
        self.load_template('Python - 二分查找')

    # ---------------- UI 搭建 ----------------

    def _build_ui(self):
        root = self.root

        # 顶部：模板 / 打开文件 / 输入
        top = ttk.Frame(root, padding=(10, 8))
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text='算法模板:').pack(side=tk.LEFT)
        self.template_combo = ttk.Combobox(
            top, values=list(TEMPLATES.keys()), state='readonly', width=24)
        self.template_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.template_combo.bind('<<ComboboxSelected>>',
                                 self.on_template_selected)

        self.open_btn = ttk.Button(top, text='打开文件...',
                                   command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=(0, 6))
        self.new_btn = ttk.Button(top, text='新建自定义代码',
                                  command=self.new_custom)
        self.new_btn.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Separator(top, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y,
                                                    padx=8)

        ttk.Label(top, text='数组 nums:').pack(side=tk.LEFT, padx=(4, 4))
        ttk.Entry(top, textvariable=self.nums_var, width=34).pack(
            side=tk.LEFT)
        ttk.Label(top, text='target:').pack(side=tk.LEFT, padx=(10, 4))
        ttk.Entry(top, textvariable=self.target_var, width=6).pack(
            side=tk.LEFT)
        ttk.Label(top, text='第二组(可选):').pack(side=tk.LEFT, padx=(10, 4))
        ttk.Entry(top, textvariable=self.nums2_var, width=18).pack(
            side=tk.LEFT)

        # 控制栏
        ctrl = ttk.Frame(root, padding=(10, 0))
        ctrl.pack(side=tk.TOP, fill=tk.X)

        self.run_btn = ttk.Button(ctrl, text='运行 (重置)',
                                  command=self.run)
        self.run_btn.pack(side=tk.LEFT)
        self.step_btn = ttk.Button(ctrl, text='下一步', command=self.step)
        self.step_btn.pack(side=tk.LEFT, padx=(6, 0))
        self.play_btn = ttk.Button(ctrl, text='自动播放',
                                   command=self.toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=(6, 0))
        self.stop_btn = ttk.Button(ctrl, text='停止', command=self.stop)
        self.stop_btn.pack(side=tk.LEFT, padx=(6, 0))

        ttk.Label(ctrl, text='每步间隔(秒):').pack(side=tk.LEFT, padx=(18, 4))
        self.speed_scale = ttk.Scale(ctrl, from_=0.05, to=2.0,
                                     variable=self.speed_var, length=140)
        self.speed_scale.pack(side=tk.LEFT)

        # 主体：左（数组 + 变量），右（代码 + 输出）
        paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=11)
        paned.add(right, weight=10)

        # 左：数组视图
        arr_frame = ttk.LabelFrame(left, text='数组视图（彩色箭头 = 指针）',
                                   padding=4)
        arr_frame.pack(fill=tk.BOTH, expand=True)
        self.array_canvas = tk.Canvas(arr_frame, background='white',
                                      height=300, highlightthickness=1,
                                      highlightbackground='#cfd8dc')
        self.array_canvas.pack(fill=tk.BOTH, expand=True)
        self.array_view = ArrayView(self.array_canvas)

        # 左：变量面板
        var_frame = ttk.LabelFrame(left, text='变量', padding=4)
        var_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.var_tree = ttk.Treeview(var_frame, columns=('name', 'value'),
                                     show='headings', height=8)
        self.var_tree.heading('name', text='变量')
        self.var_tree.heading('value', text='值')
        self.var_tree.column('name', width=110, anchor='w')
        self.var_tree.column('value', width=380, anchor='w')
        var_scroll = ttk.Scrollbar(var_frame, orient=tk.VERTICAL,
                                   command=self.var_tree.yview)
        self.var_tree.configure(yscrollcommand=var_scroll.set)
        self.var_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        var_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 右：代码编辑器
        self.code_frame = ttk.LabelFrame(
            right, text='代码（可修改，必须定义 solve(nums, target)）',
            padding=4)
        self.code_frame.pack(fill=tk.BOTH, expand=True)
        text_frame = ttk.Frame(self.code_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.line_text = tk.Text(text_frame, width=4, padx=6, takefocus=0,
                                 bd=0, background='#f5f5f5',
                                 font=('Consolas', 12), state='disabled',
                                 wrap='none')
        self.line_text.pack(side=tk.LEFT, fill=tk.Y)

        self.code_text = tk.Text(text_frame, wrap='none',
                                 font=('Consolas', 12), undo=True,
                                 background='#fafafa', insertbackground='#000000')
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.code_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.code_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_text.configure(yscrollcommand=self._on_code_scroll)
        self.line_text.configure(yscrollcommand=lambda *a: None)
        self.code_scroll.configure(command=self._on_scrollbar_move)

        self.code_text.tag_config('current', background='#fff59d')
        self.line_text.tag_config('current', background='#fdd835')

        self.code_text.bind('<MouseWheel>', self._on_mousewheel)
        self.line_text.bind('<MouseWheel>', self._on_mousewheel)

        # 右：输出
        out_frame = ttk.LabelFrame(right, text='输出', padding=4)
        out_frame.pack(fill=tk.BOTH, pady=(8, 0))
        self.log_text = tk.Text(out_frame, height=6, wrap='none',
                                state='disabled', font=('Consolas', 10),
                                background='#263238', foreground='#eceff1')
        out_scroll = ttk.Scrollbar(out_frame, orient=tk.VERTICAL,
                                   command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=out_scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        out_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 底部状态栏
        status = ttk.Label(root, textvariable=self.status_var,
                           anchor='w', padding=(10, 4),
                           relief=tk.SUNKEN)
        status.pack(side=tk.BOTTOM, fill=tk.X)

        self.set_buttons_running(False)

    # ---------------- 代码编辑器 ----------------

    def set_code(self, text):
        self.code_text.delete('1.0', 'end')
        self.code_text.insert('1.0', text)
        self._update_line_numbers()
        self.code_text.edit_reset()

    def _update_line_numbers(self):
        n = int(self.code_text.index('end-1c').split('.')[0])
        self.line_text.config(state='normal')
        self.line_text.delete('1.0', 'end')
        self.line_text.insert('1.0',
                              '\n'.join(str(i) for i in range(1, n + 1)))
        self.line_text.config(state='disabled')

    def highlight_line(self, lineno):
        self._update_line_numbers()
        for txt in (self.code_text, self.line_text):
            txt.tag_remove('current', '1.0', 'end')
            if lineno >= 1:
                txt.tag_add('current', '%d.0' % lineno,
                            '%d.0' % (lineno + 1))
                txt.see('%d.0' % lineno)

    def _on_code_scroll(self, first, last):
        self.code_scroll.set(first, last)
        self.line_text.yview_moveto(first)

    def _on_scrollbar_move(self, *args):
        self.code_text.yview(*args)
        self.line_text.yview(*args)

    def _on_mousewheel(self, event):
        delta = -int(event.delta / 120)
        self.code_text.yview_scroll(delta, 'units')
        self.line_text.yview_scroll(delta, 'units')
        return 'break'

    # ---------------- 模板 / 文件 ----------------

    def load_template(self, name):
        meta = TEMPLATES[name]
        self.set_code(meta['code'].strip() + '\n')
        self.nums_var.set(meta['nums'])
        self.nums2_var.set(meta.get('nums2', ''))
        self.target_var.set(meta['target'])
        self.current_template = name
        self.current_path = None
        self.line_map = meta.get('line_map')
        self.template_combo.set(name)
        lang = meta.get('lang', 'python')
        mode_text = '真执行' if lang == 'python' else '模拟模式'
        if lang == 'python':
            frame_text = ('代码（可修改：定义 solve 逐步执行该函数；'
                          '不定义 solve 则逐步执行整个文件）')
        else:
            frame_text = ('代码（%s 模拟模式：按内置演示逻辑执行，'
                          '改代码不会改变步骤）' % lang.upper())
        self.code_frame.config(text=frame_text)
        self.root.title('算法可视化 — %s' % name)
        self.status_var.set('已载入模板：%s（%s）' % (name, mode_text))
        self.log('[就绪] 已载入模板：%s（%s）' % (name, mode_text))

    def new_custom(self):
        """切到自定义代码模板：给出可编辑的 solve 起步代码。"""
        name = 'Python - 自定义代码'
        current = self.code_text.get('1.0', 'end-1c').strip()
        if current and current != TEMPLATES[name]['code'].strip():
            if not messagebox.askyesno(
                    '新建自定义代码', '这会覆盖当前编辑器里的代码，确定吗？'):
                return
        self.load_template(name)

    def on_template_selected(self, _event=None):
        name = self.template_combo.get()
        if name not in TEMPLATES:
            return
        current = self.code_text.get('1.0', 'end-1c').strip()
        if current and current != TEMPLATES[name]['code'].strip():
            if not messagebox.askyesno(
                    '载入模板',
                    '载入「%s」会覆盖当前编辑器里的代码，确定吗？' % name):
                self.template_combo.set(self.current_template
                                        or list(TEMPLATES)[0])
                return
        self.load_template(name)

    def open_file(self):
        path = filedialog.askopenfilename(
            title='打开代码文件',
            filetypes=[('Python 文件', '*.py'),
                       ('C/C++ 文件', '*.cpp *.c *.h'),
                       ('Java 文件', '*.java'),
                       ('文本文件', '*.txt'),
                       ('所有文件', '*.*')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except OSError as e:
            messagebox.showerror('打开失败', str(e))
            return
        self.set_code(content)
        self.current_path = path
        self.current_template = None
        self.line_map = None
        self.code_frame.config(
            text='代码（已打开文件：按 Python 执行；定义 solve 则逐步执行该函数，'
                 '否则逐步执行整个文件）')
        self.root.title('算法可视化 — %s' % path)
        self.status_var.set('已打开文件：%s（将停留在这个文件）' % path)
        self.log('[就绪] 已打开文件：%s' % path)

    # ---------------- 运行控制 ----------------

    def set_buttons_running(self, running):
        self.run_btn.config(state='disabled' if running else 'normal')
        state = 'normal' if running else 'disabled'
        self.step_btn.config(state=state)
        self.play_btn.config(state=state)
        self.stop_btn.config(state=state)
        # 运行中锁定代码编辑器，防止行号和 trace 错位
        self.code_text.config(state='disabled' if running else 'normal')

    def run(self):
        if self.running:
            messagebox.showinfo('提示', '正在运行中，请先点“停止”或等它结束')
            return
        code = self.code_text.get('1.0', 'end-1c')
        meta = TEMPLATES.get(self.current_template)
        lang = meta.get('lang', 'python') if meta else 'python'
        # 模板给显式 setup/entry；自定义代码 / 打开文件时为 None，
        # 由 AlgorithmStepper 根据 solve 的签名自动推断。
        setup = meta.get('setup') if meta else None
        entry = meta.get('entry') if meta else None
        if lang == 'python':
            exec_code = code
            self.line_map = None
            if not code.strip():
                messagebox.showerror('提示', '代码为空，请输入要运行的 Python 代码')
                return
        else:
            # 模拟模式：执行内置等价脚本，代码编辑器只负责显示对应语言
            exec_code = meta['python_ref']
            self.line_map = meta.get('line_map')
            if code.strip() != meta['code'].strip():
                if not messagebox.askyesno(
                        '模拟模式',
                        '当前是 %s 模拟模式：演示步骤按内置逻辑执行，'
                        '你对代码的修改不会改变执行过程。\n\n继续运行吗？'
                        % lang.upper()):
                    return
        nums = parse_nums(self.nums_var.get())
        if nums is None:
            messagebox.showerror('提示',
                                 '数组输入有误：请输入用空格隔开的整数，'
                                 '例如 1 3 5 7 9')
            return
        target_text = self.target_var.get().strip()
        target = None
        if target_text:
            try:
                target = int(target_text)
            except ValueError:
                messagebox.showerror('提示',
                                     'target 必须是整数，排序算法可以留空')
                return
        nums2 = None
        if self.nums2_var.get().strip():
            nums2 = parse_nums(self.nums2_var.get())
            if nums2 is None:
                messagebox.showerror('提示',
                                     '第二组数据输入有误：请输入用空格隔开的整数')
                return

        self.step_count = 0
        self.current_vars = None
        self._clear_log()
        if lang != 'python':
            self.log('[模拟模式] 正在演示 %s（执行内置等价脚本）'
                     % self.current_template)
        self.log('[开始] 正在运行...')
        self.highlight_line(1)
        self.stepper = AlgorithmStepper()
        self.running = True
        self.set_buttons_running(True)
        self.thread = threading.Thread(
            target=self.stepper.run,
            args=(exec_code, nums, target, setup, entry, nums2),
            daemon=True)
        self.thread.start()
        self._schedule_poll()

    def step(self):
        if self.running and self.stepper is not None \
                and self.stepper.paused.is_set():
            self.stepper.resume.set()

    def toggle_play(self):
        if not self.running:
            messagebox.showinfo('提示', '请先点“运行”开始执行')
            return
        self.playing = not self.playing
        if self.playing:
            self.play_btn.config(text='暂停播放')
            self.play_tick()
        else:
            self.play_btn.config(text='自动播放')

    def play_tick(self):
        if self.playing and self.running:
            self.step()
            delay = max(30, int(self.speed_var.get() * 1000))
            self.play_job = self.root.after(delay, self.play_tick)
        else:
            self.stop_play()

    def stop_play(self):
        self.playing = False
        self.play_btn.config(text='自动播放')
        if self.play_job is not None:
            self.root.after_cancel(self.play_job)
            self.play_job = None

    def stop(self):
        if self.stepper is not None:
            self.stepper.stop_flag.set()
            self.stepper.resume.set()

    # ---------------- 队列轮询 / 渲染 ----------------

    def _schedule_poll(self):
        if self.poll_job is not None:
            self.root.after_cancel(self.poll_job)
        self.poll_job = self.root.after(50, self.poll_queue)

    def poll_queue(self):
        try:
            while True:
                item = self.stepper.q.get_nowait()
                self.handle_item(item)
        except queue.Empty:
            pass
        if self.running:
            self.poll_job = self.root.after(50, self.poll_queue)
        else:
            self.poll_job = None

    def handle_item(self, item):
        t = item['type']
        if t == 'line':
            self.step_count += 1
            self.current_vars = item['vars']
            lineno = item['lineno']
            display = self.line_map.get(lineno, lineno) \
                if self.line_map else lineno
            self.highlight_line(display)
            self.render_state(item['vars'], highlight=set())
            self.status_var.set('第 %d 步 — 黄色高亮行 = 下一步将要执行'
                                % self.step_count)
            self.log('[第 %d 步] 高亮第 %d 行' % (self.step_count,
                                                   display))
        elif t == 'done':
            self.current_vars = item.get('vars') or self.current_vars
            result = item.get('result')
            highlight = set()
            if isinstance(result, int) and not isinstance(result, bool):
                _, arr = get_array(self.current_vars or {})
                if arr is not None and 0 <= result < len(arr):
                    highlight = {result}
            self.render_state(self.current_vars or {}, highlight)
            self.running = False
            self.set_buttons_running(False)
            self.stop_play()
            if result is None:
                self.status_var.set('执行完成')
                self.log('[完成] 执行完成')
            else:
                self.status_var.set('执行完成，返回值 = %s' % fmt_value(result))
                self.log('[完成] 返回值 = %s' % fmt_value(result))
        elif t == 'error':
            self.running = False
            self.set_buttons_running(False)
            self.stop_play()
            self.status_var.set('运行出错')
            self.log('[出错] %s' % item['message'])
            messagebox.showerror('运行出错', item['message'])
        elif t == 'stopped':
            self.running = False
            self.set_buttons_running(False)
            self.stop_play()
            self.status_var.set('已停止')
            self.log('[停止] 已手动停止')

    def render_state(self, vars_, highlight=()):
        self.array_view.draw_state(vars_, highlight)
        self.update_var_panel(vars_)

    def update_var_panel(self, vars_):
        self.var_tree.delete(*self.var_tree.get_children())
        for name in sorted_var_names(vars_):
            self.var_tree.insert('', 'end', values=(name,
                                                     fmt_value(vars_[name])))

    # ---------------- 日志 ----------------

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def _clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')

    # ---------------- 退出 ----------------

    def on_close(self):
        self.stop_play()
        if self.stepper is not None:
            self.stepper.stop_flag.set()
            self.stepper.resume.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()


if __name__ == '__main__':
    main()
