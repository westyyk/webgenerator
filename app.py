import random
import string
import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'hello'

USERS_FILE = 'users.json'
PASSWORDS_FILE = 'passwords.json'


class PasswordManager:
    def __init__(self):
        self.users = self.load_users()
        self.passwords = self.load_passwords()

    def load_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        return {}

    def load_passwords(self):
        if os.path.exists(PASSWORDS_FILE):
            with open(PASSWORDS_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f)

    def save_passwords(self):
        with open(PASSWORDS_FILE, 'w') as f:
            json.dump(self.passwords, f)

    def register(self, username, password):
        if username in self.users:
            return False, "Пользователь с таким именем уже существует"

        self.users[username] = password
        self.passwords[username] = []
        self.save_users()
        self.save_passwords()
        return True, "Регистрация успешна"

    def login(self, username, password):
        if username in self.users and self.users[username] == password:
            return True, "Успешный вход"
        else:
            return False, "Неверное имя пользователя или пароль"

    def generate_password(self, level):
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

    def add_password(self, username, service, complexity="Medium", custom_password=None):
        if custom_password:
            password = custom_password
        else:
            password = self.generate_password(complexity)

        if username not in self.passwords:
            self.passwords[username] = []

        self.passwords[username].append({
            "service": service,
            "password": password
        })
        self.save_passwords()

        return True, f"Пароль для {service} сохранен: {password}"

    def get_passwords(self, username):
        user_passwords = self.passwords.get(username, [])
        return user_passwords


manager = PasswordManager()


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    passwords = manager.get_passwords(username)

    return render_template('index.html',
                           username=username,
                           passwords=passwords)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        success, message = manager.login(username, password)
        if success:
            session['username'] = username
            flash(message, 'success')
            return redirect(url_for('index'))
        else:
            flash(message, 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        success, message = manager.register(username, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')

    return render_template('register.html')


@app.route('/generate_password', methods=['POST'])
def generate_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    service = request.form['service']
    complexity = request.form.get('complexity', 'Medium')
    custom_password = request.form.get('custom_password', '')

    username = session['username']

    if custom_password:
        success, message = manager.add_password(username, service, complexity, custom_password)
    else:
        success, message = manager.add_password(username, service, complexity)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host ='0.0.0.0', port=5000)
