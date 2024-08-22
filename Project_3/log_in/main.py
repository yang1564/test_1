# 导入数据库模块
import string
import webbrowser

import pymysql
# 导入Flask框架，这个框架可以快捷地实现了一个WSGI应用
from flask import Flask, redirect
# 默认情况下，flask在程序文件夹中的templates子文件夹中寻找模块
from flask import render_template
# 导入前台请求的request模块
from flask import request
import traceback

# 传递根目录
app = Flask(__name__)

#  github测试上传


@app.route('/book')
def show_book_page():
    return render_template('book.html')


# 默认路径访问登录页面
@app.route('/login_page')
def login():
    return render_template("login.html")


# 默认路径访问注册页面
@app.route('/register')
def register():
    return render_template('register.html')


# 获取注册请求及处理
@app.route('/register', methods=['POST'])
def getRegisterRequest():
    user = str(request.form.get('user'))
    password = str(request.form.get('password'))
    confirm_password = str(request.form.get('confirm_password'))
    # 连接数据库
    db = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="testdb")

    try:
        # 使用cursor()方法获取操作游标
        cursor = db.cursor()

        if not user or not password:
            error_message = "用户或者密码不能为空"
            return render_template('register.html', error_message=error_message)

        if not confirm_password:
            error_message = "请再次输入密码确认"
            return render_template('register.html', error_message=error_message)

        if confirm_password != password:
            error_message = "两次密码不一致"
            return render_template('register.html', error_message=error_message)

        if not validatePassword(password):
            error_message = "密码必须包含至少一个字母和一个符号，并且长度至少为6位"
            return render_template('register.html', error_message=error_message)

        cursor.execute("SELECT * FROM user WHERE user=%s", (user,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "用户名已存在，请选择其他用户名"
            return render_template('register.html', error_message=error_message)

        sql = "INSERT INTO user(user, password) VALUES ('%s','%s')" % (user, password)

        # 执行sql语句
        cursor.execute(sql)

        # 提交到数据库执行
        db.commit()

        # 注册成功之后跳转到登录页面
        return render_template('login.html')
    except Exception as e:
        # 抛出错误信息
        print("Error", e)
        # 如果发生错误则回滚
        db.rollback()
        return render_template('register.html', error_message="注册失败，请重试")
    finally:
        # 关闭数据库连接
        if db:
            db.close()


def validatePassword(password):
    return any(char.isalpha() for char in password) and any(char in string.punctuation for char in password)


# 获取登录参数及处理
@app.route('/login')
def getLoginRequest():
    user = str(request.args.get('user'))
    password = str(request.args.get('password'))

    # 检查请求是否来自注册页面
    referer = request.headers.get("Referer")
    if referer and "book" in referer:
        return render_template('login.html')

    db = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="testdb")

    try:
        cursor = db.cursor()

        if not user or not password:
            error_message = "请输入用户名和密码"
            return render_template('login.html', error_message=error_message)

        # SQL 查询语句
        sql = "select * from user where user= '%s' and password= '%s'" % (user, password)

        # 执行sql语句
        cursor.execute(sql)
        results = cursor.fetchall()
        print(len(results))
        if len(results) == 0:
            error_message = "用户名或密码错误"
            return render_template('login.html', error_message=error_message)
        else:
            return render_template('book.html')
    except:
        # 如果发生错误则回滚
        traceback.print_exc()
        db.rollback()
    db.close()


if __name__ == '__main__':
    app.run(debug=True)
