cd /home/question_manager
export FLASK_APP=main.py
flask db migrate
flask db upgrade
