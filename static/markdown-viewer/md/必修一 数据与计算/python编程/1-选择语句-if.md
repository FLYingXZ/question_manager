# 1-选择语句-if

## **1. if 语句的基本结构**
### **1.1 单分支结构**
用于判断某个条件是否成立，如果成立，执行代码块；否则跳过。
**代码块**：python中使用四个空格"    "的缩进表示代码块
```python
# 示例：判断一个数是否为正数
num = int(input("请输入一个整数："))
if num > 0:
    print("该数是正数")
	#注意：曾学习c++语言的同学请注意，python没有语句块括号{}，而是通过4个空格的缩进控制语句块
```
#### 缩进的意义
请思考下面两个程序的区别
```python
a = 10
if a > 15:
    a = 1
a += 5
print(a)
#输出15
```
```python
a = 10
if a > 15:
    a = 1
    a += 5
print(a)
#输出10
```
---

### **1.2 双分支结构**
当条件成立时执行一个代码块，否则执行另一个代码块。

```python
# 示例：判断一个数是奇数还是偶数
num = int(input("请输入一个整数："))
if num % 2 == 0:
    print("该数是偶数")
else:
    print("该数是奇数")
```

---

### **1.3 多分支结构**
检查多个条件，并根据第一个满足的条件执行相应代码块。

```python
# 示例：根据分数判断等级
score = int(input("请输入成绩："))
if score >= 90:
    print("优秀")
elif score >= 75:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

---

## **2. 案例：三个数的大小比较**
比较三个整数的大小，输出最大值。

```python
# 输入三个整数
a = int(input("请输入第一个整数："))
b = int(input("请输入第二个整数："))
c = int(input("请输入第三个整数："))

# 判断最大值
if a >= b and a >= c:
    max_num = a
elif b >= a and b >= c:
    max_num = b
else:
    max_num = c

print("最大值是：", max_num)
```

---

## 扩展阅读：三元表达式
三元表达式是一种简洁的条件判断语法，用于替代简单的 `if-else`。

**语法:**
```python
结果 = 条件为真时的值 if 条件 else 条件为假时的值
```

**示例：**
```python
# 判断一个数的正负
num = int(input("请输入一个整数："))
result = "正数" if num > 0 else "非正数"
print(result)
```