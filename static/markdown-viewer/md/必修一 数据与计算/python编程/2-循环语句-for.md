# 2-循环语句-for

## 一、for循环的基本概念  
`for`循环用于按序遍历对象中的每个元素，常用于迭代列表、字符串或范围。  

### 语法：  
```python
for 变量 in 可迭代对象:
    执行代码块
```

---

## 二、利用`range()`的for循环  

### 1. `range()`函数简介  
`range()`用于生成整数序列，常与`for`循环搭配使用。  

### 常用格式：  
```python
range(终点)            # 从0到终点-1
range(起点, 终点)     # 从起点到终点-1
range(起点, 终点, 步长)  # 指定步长
```

#### 示例1：  
```python
# 从0到4的序列
for i in range(5):
    print(i)  
```
**输出:**  
```
0  
1  
2  
3  
4  
```
#### 示例2：  
```python
# 从1到9，步长为2
for i in range(1, 10, 2):
    print(i)  
```
**输出:**  
```
1  
3  
5  
7  
9  
```
#### 示例3：  
```python
# 从10到5降序
for i in range(10, 4, -1):
    print(i)  
```
**输出:**  
```
10
9
8
7
6
5```
---

## 三、直接循环序列  

### 示例：  
```python
# 遍历字符串
for char in "hello":
    print(char)
```
**输出:**  
```
h  
e  
l  
l  
o  
```

```python
# 遍历列表
for item in [10, 20, 30]:
    print(item)
```
**输出:**  
```
10  
20  
30  
```

---

## 四、实践与练习
1. 使用`range()`打印从1到20的偶数。

```python
for i in range(2, 21, 2):
    print(i)
```
或
```python
for i in range(1, 21):
    if __________:
        print(i)
```
2.输出1到n的和
```python
n = int(input())
sum = 0
for i in range(1, n+1):
    __________
print(sum)
```
3.输入10个数字，输出其中3的倍数的个数
```
cnt = 0
for i in range(10):
    x = int(input())
	if x%3==0:
	    __________
print(cnt)
```
4.判断n是否为素数
```python
n = int(input())
flag = True
for i in range(2, int(n**0.5)+1):
    if __________:
	    flag = False
if __________:
    print("Y")
else:
    print("N")
```
---