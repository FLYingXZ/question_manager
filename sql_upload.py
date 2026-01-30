from flask import Flask, render_template
import sqlite3
import json
import os

DATABASE = 'questions.db'

def init_db():
    if os.path.exists(DATABASE):

        # 导入JSON数据
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        for item in data:
            print("insert:"+str(item))
            try:
                c.execute('INSERT INTO chongbuluo_url (url, title, description, author) VALUES (?, ?, ?, ?)',
                         (item['url'], item['title'], item['des'], item['user']))
            except sqlite3.IntegrityError:
                pass  # 忽略重复插入
        conn.commit()
        conn.close()


init_db()
print('Database initialized successfully!')
