import string
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hello'  # Важно: замените на случайный ключ в продакшене




def load_users():
    return  [
            {'username': 'admin', 'password': 'admin', 'role': 'admin'},
            {'username': 'user', 'password': 'user', 'role': 'user'}
            ]



def generate_password(level):

    if level == "Light":
        length = random.randint(6, 8)
        characters = string.ascii_letters
    elif level == "Medium":
        length = random.randint(8, 12)
        characters = string.ascii_letters + string.digits
    elif level == "Hard":
        length = random.randint(12, 16)
        characters = string.ascii_letters + string.digits + string.punctuation
    else:
        raise ValueError("Неизвестный уровень сложности")

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def load_users():
    return [
        {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
        {'username': 'user1', 'password': 'user123', 'role': 'user'},
        {'username': 'user2', 'password': 'user123', 'role': 'user'}
    ]

user_profiles = {
    'admin': {'password': 'admin123', 'name': 'Администратор', 'role': 'admin'},
    'user1': {'password': 'user123', 'name': 'Иван Иванов', 'role': 'user'},
    'user2': {'password': 'user123', 'name': 'Мария Петрова', 'role': 'user'}
}


def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Маршруты аутентификации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        user_found = False
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = user['username']
                session['role'] = user.get('role', 'user')
                print(session)
                flash(f'Добро пожаловать, {username}!', 'success')
                user_found = True
                return redirect(url_for('index'))

        if not user_found:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


# Защищенные маршруты
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))



# Дополнительные защищенные маршруты (пример)
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           username=session.get('username'),
                           role=session.get('role'))


@app.route('/admin')
@login_required
def admin():
    if session.get('role') != 'admin':
        flash('У вас нет прав для доступа к этой странице', 'error')
        return redirect(url_for('index'))
    return render_template('admin.html', username=session.get('username'))


@app.route('/generate', methods=['POST'])
def generate():
    try:
        level = request.form.get('level', 'Medium')
        password = generate_password(level)
        return jsonify({'password': password, 'error': None})
    except Exception as e:
        return jsonify({'password': None, 'error': str(e)})





if __name__ == '__main__':
    app.run(debug=True)
