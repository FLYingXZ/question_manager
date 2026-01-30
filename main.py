#主程序，通过一系列的调用进行整个项目的人为的模块化分工

from flask import request, Flask
from flask_migrate import Migrate

#初始化部分---------------------------------------------------------------------------------------------------
from config import app

#模型部分-----------------------------------------------------------------------------------------------------
from models import db, AIModelConfig, AIPromptTemplate

#数据库同步迁移
migrate = Migrate(app, db)

#页面部分-----------------------------------------------------------------------------------------------------
import pages
#控制部分-----------------------------------------------------------------------------------------------------
import control
#用户部分-----------------------------------------------------------------------------------------------------
import users
import utils

#用于tomexam转化word，与本项目无关
from control import upload_docx_page
from control import upload_docx

if __name__ == '__main__':
    with app.app_context():

        try:
            db.create_all()
        except Exception as e:
            print(f"Error initializing database: {e}")
    app.run(host='0.0.0.0', port=5000, debug = True)


