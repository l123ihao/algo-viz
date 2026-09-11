# 算法可视化工具（algo-viz）

一个用 Python 编写的算法可视化桌面软件：把力扣经典题单里的算法做成**可逐步执行、可改代码、可看数组/链表/栈变化**的动画演示，适合刷题学习、教学演示和调试理解。

零第三方依赖（tkinter + `sys.settrace`），Python 代码**真正执行**，不是模拟动画。

---

## 下载

**最新版本：v1.0.0**

- [📥 下载 算法可视化 exe（Windows，双击即用，无需安装 Python）](https://github.com/l123ihao/algo-viz/releases/download/v1.0.0/algo-viz-v1.0.0.exe)
- [所有版本（Releases）](https://github.com/l123ihao/algo-viz/releases)

> 首次双击 exe 时 Windows SmartScreen 可能提示“未知发布者”，点“更多信息 → 仍要运行”即可。

---

## 功能特性

- **23 个算法模板**（按力扣经典题单挑选）
  - Python：自定义代码、二分查找、线性查找、冒泡排序、选择排序、插入排序、链表反转、链表删除节点、单调栈、两数之和 II、长度最小的子数组、每日温度、合并两个有序链表、环形链表、删除链表倒数第 N 个节点
  - C++ / Java：二分查找、冒泡排序、链表反转、合并两个有序链表（模拟模式）
- **Python 代码真正执行**：右侧编辑器可随意修改，改完立即生效
- **自定义代码可视化**：自动识别 `solve` 函数签名
  - `solve(nums, target)` / `solve(nums)` → 数组视图
  - `solve(head, target)` / `solve(head)` → 链表视图（自动注入 `ListNode`）
  - `solve(head, head2)` → 合并两个链表视图
- **任意代码可视化**：不写 `solve` 时，整个文件当作主程序逐行执行（含顶层语句和自定义函数），每行高亮、变量实时展示
- **三种视图**：
  - 数组视图：彩色箭头标注 `l / r / mid / i / j / min_idx` 等指针，`l..r` 范围整体高亮
  - 链表视图：节点盒 + `next` 指针 + `head / cur / prev / nxt / slow / fast` 指针标注，环用红色箭头画出
  - 单调栈视图：上半数组、下半垂直栈，栈顶标蓝
- 单步执行 / 自动播放 / 可调速度 / 变量面板 / 输出日志
- 打开自己的 `.py / .cpp / .java` 文件直接可视化（Python 规则执行）

---

## 快速开始

### 方式一：直接下载 exe（推荐）

下载上面的 exe，双击运行。

### 方式二：源码运行

1. 安装 Python 3（勾选 “Add Python to PATH”）
2. 双击 `启动算法可视化.bat`，或命令行运行：

```bash
python algo_viz.py
```

---

## 代码怎么写

### 函数模式（定义了 `solve`）

```python
# 数组类
def solve(nums, target):
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
```

```python
# 链表类（ListNode 自动注入，head 已由 nums 构建好）
def solve(head, target):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
```

### 任意代码模式（没有 `solve`）

整个文件按主程序逐行执行：

```python
total = 0
for i in range(len(nums)):
    total += nums[i]
print(total)

# 链表：ListNode / build_list 自动注入
head = build_list(nums)
cur = head
while cur:
    cur = cur.next
```

### 指针变量命名约定

变量名请用常见名字，软件才会识别成指针画出来：

- 数组：`l` `r` `mid` `i` `j` `min_idx`
- 链表：`head` `cur` `prev` `nxt` `slow` `fast`
- 数组名：`nums` `arr` `a` `lst` 等；栈：`stack`

---

## 更新方向（Roadmap）

以下是我们计划中的发展方向，欢迎提 Issue 或 PR 一起完善：

### 近期计划
- [ ] **C++ / Java 真执行模式**：检测到本机已装 MinGW / JDK 时，自动编译运行并逐步可视化（替换现在的模拟模式）
- [ ] **步骤回退**：支持“上一步”，可倒退查看状态变化
- [ ] **代码语法高亮**：编辑区按 Python/C++/Java 语法着色
- [ ] **递归调用栈可视化**：画出递归树和调用栈帧
- [ ] **随机数据生成**：一键生成随机数组 / 随机链表
- [ ] **GitHub Actions 自动打包**：每次打 tag 自动构建 exe 并发布 Release

### 中期计划
- [ ] **树与图可视化**：二叉树、N 叉树、图的节点/边绘制（支持 DFS/BFS 动画）
- [ ] **更多算法模板**：快速排序、归并排序、二分答案、滑动窗口进阶、动态规划（背包/最长子序列）等
- [ ] **复杂度标注**：每个模板显示时间/空间复杂度卡片
- [ ] **多语言界面**：中英文切换
- [ ] **主题切换**：浅色 / 深色主题

### 长期设想
- [ ] **Web 版**：移植到浏览器（如 Pyodide + 前端画布），免安装在线使用
- [ ] **自定义视图插件**：用户可自定义数据结构的绘制方式
- [ ] **算法对比模式**：同一输入并排对比多个算法的执行步骤与性能

---

## 项目结构

```
algo-viz/
├── algo_viz.py              # 主程序（GUI + 模板 + 执行追踪 + 画布渲染）
├── 使用说明.txt              # 详细使用说明
├── 启动算法可视化.bat         # Windows 一键启动脚本
├── 算法可视化.spec           # PyInstaller 打包配置
└── dist/
    └── 算法可视化.exe         # 打包产物（Release 资产）
```

---

## 从源码打包 exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name 算法可视化 algo_viz.py
# 产物在 dist/ 目录
```

---

## 许可证

MIT License
