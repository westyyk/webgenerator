from flask import Flask, render_template, request, jsonify
import random
import string

app = Flask(__name__)

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


@app.route('/')
def index():
    return render_template('index.html')


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