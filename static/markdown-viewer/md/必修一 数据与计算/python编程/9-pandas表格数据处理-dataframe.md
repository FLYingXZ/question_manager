# Pandas DataFrame 数据处理

在Python中，`pandas`是一个非常强大的数据处理库，广泛用于数据清洗、处理和分析。`pandas`中的数据存储结构主要是`Series`和`DataFrame`，其中`DataFrame`是一个二维表格数据结构，类似于Excel中的表格或SQL中的数据表。

## 1. 创建 DataFrame

### 1.1 从字典创建 DataFrame

可以通过字典将数据转换成`DataFrame`，字典的键表示列名，值表示列数据。

```python
import pandas as pd

data = {
    '姓名': ['张三', '李四', '王五'],
    '年龄': [18, 20, 22],
    '成绩': [85, 90, 88]
}

df = pd.DataFrame(data)
print(df)
```

输出结果：

| 姓名 | 年龄 | 成绩 |
|------|------|------|
| 张三 | 18   | 85   |
| 李四 | 20   | 90   |
| 王五 | 22   | 88   |

### 1.2 从列表创建 DataFrame

如果数据已经是列表的形式，可以通过`DataFrame`将其转换为表格形式。

```python
import pandas as pd

data = [
    ['张三', 18, 85],
    ['李四', 20, 90],
    ['王五', 22, 88]
]

df = pd.DataFrame(data, columns=['姓名', '年龄', '成绩'])
print(df)
```

输出结果与上面相同。

## 2. 访问 DataFrame 数据

### 2.1 访问单列

通过列名来访问某一列数据，返回的是一个`Series`对象。

```python
# 访问 "成绩" 列
print(df['成绩'])
```

### 2.2 访问多列

可以通过列名列表来选择多个列。

```python
# 访问 "姓名" 和 "年龄" 列
print(df[['姓名', '年龄']])
```

### 2.3 访问特定单元格

```python
# 通过行和列标签访问数据
print(df.at[0, '姓名'])  # 第1行'姓名'列的数据，输出：张三
```

## 3. 数据清洗与处理

### 3.1 查看数据基本信息

通过以下方法可以查看DataFrame的基本信息。

```python
# 查看数据的前5行
print(df.head())

# 查看数据的后5行
print(df.tail())

### 3.2 数据筛选

可以通过条件筛选数据，类似SQL中的`WHERE`语句。

```python
# 筛选出年龄大于19的人
print(df[df['年龄'] > 19])

# 筛选出成绩大于85并且年龄小于22的人
df = df[df['成绩'] > 85]
df = df[df['年龄'] < 22]
print(df)
```

### 3.3 修改数据

可以通过索引来修改`DataFrame`中的数据。

```python
# 修改第一行'年龄'为25
df.at[0, '年龄'] = 25
print(df)
```

### 3.5 删除列或行

删除列或行可以使用`drop()`方法。

```python
# 删除"成绩等级"列
df = df.drop(columns=['成绩等级'])
print(df)

# 删除第1行
df = df.drop(index=0)
print(df)
```

### 3.6 重命名列

通过`rename()`方法可以修改列名。
```python
# 将“成绩”列重命名为“分数”
df = df.rename(columns={'成绩': '分数'})
print(df)
```

## 4. 数据汇总与分组

### 4.1 分组聚合
可以通过`groupby()`方法对数据进行分组并进行聚合。

```python
# 按照"年龄"分组，计算每组的"成绩"均值
grouped = df.groupby('年龄')['分数'].mean()
print(grouped)
```

### 4.2 数据排序

可以对DataFrame进行排序，默认为升序排序。

```python
# 按照"成绩"列进行降序排序
df = df.sort_values(by='分数', ascending=False)
print(df)
```

### 4.3 小结

| 功能                           | 代码示例                                                     |
| ------------------------------ | ------------------------------------------------------------ |
| 读取文件                       | `read_excel("文件名")`                                       |
| 获取所有列标题                 | `df.columns`                                                 |
| 获取所有行标题                 | `df.index`                                                   |
| 获取第 i 行姓名列的值          | `df.at[i, '姓名']`                                           |
| 获取某一列（以姓名为例）       | `df.姓名` 或 `df["姓名"]`                                    |
| 筛选（语文列大于 100 的行）    | `df[df.语文 > 100]`                                          |
| 根据语文成绩升序排序           | `df.sort_values("语文")`<br>降序：`df.sort_values("语文", ascending=False)` |
| 根据班级分类，求每班语文最高分 | `df.groupby('班级').语文.max()`                              |
| 姓名、语文列创建柱形图         | `plt.bar(df.姓名, df.语文)`<br>（plot 折线图：`plt.plot(df.姓名, df.语文)`）<br>（pie 饼图：`plt.pie(...)`） |
| 展示图表                       | `plt.show()`                                                 |

## 5. 扩展阅读

### 5.1 `pandas`的更多常用方法

| 方法 | 描述 |
|------|------|
| `df.info()` | 查看DataFrame的摘要信息，包含数据类型及缺失值信息 |
| `df.isnull()` | 判断是否存在缺失值 |
| `df.fillna(value)` | 填充缺失值 |
| `df.dropna()` | 删除缺失值所在的行 |
| `df.apply()` | 对DataFrame的每列或每行应用一个函数 |
| `df.merge()` | 合并多个DataFrame |

### 5.2 参考文献与资源
- 官方文档：[pandas 官方文档](https://pandas.pydata.org/)
- 学习教程：[w3schools Pandas教程](https://www.w3schools.com/python/pandas/default.asp)

## 6. 总结

`pandas`提供了非常丰富且强大的功能来进行数据的处理、清洗和分析，尤其是`DataFrame`结构，它是进行数据操作的核心工具。掌握`DataFrame`的常见操作是学习数据分析的重要一步。