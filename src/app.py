from flask import Flask, jsonify, session, request
from pymongo import MongoClient
from bson import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = 'super-secret'

client = MongoClient('mongodb+srv://kushagra:kushagra@cicd.opzij.mongodb.net/?retryWrites=true&w=majority&appName=cicd')
db = client['todo_app']
users = db['users']
todos = db['todos']


@app.route('/')
@app.route('/home')
def home():
    return jsonify({'message': 'Welcome to TODO API'})


@app.route('/signup', methods=['POST'])
def signup():
    if not request.get_json():
        return jsonify({'error': 'Missing JSON in request'}), 400

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Missing name or email and password'}), 400

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        'name': name,
        'email': email,
        'password': hashed
    }
    users.insert_one(user)

    session['email'] = email
    return jsonify({'message': 'User created successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    session['email'] = email
    return jsonify({'message': 'Logged in successfully'})


@app.route('/todos', methods=['GET'])
def get_todos():
    if 'email' not in session:
        return jsonify({'error': 'Please login first'}), 401

    user_todos = list(todos.find({'user_email': session['email']}))
    for todo in user_todos:
        todo['_id'] = str(todo['_id'])

    return jsonify(user_todos)


@app.route('/todos', methods=['POST'])
def create_todo():
    if 'email' not in session:
        return jsonify({'error': 'Please login first'}), 401

    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    todo = {
        'title': title,
        'description': description,
        'completed': False,
        'user_email': session['email']
    }

    result = todos.insert_one(todo)
    todo['_id'] = str(result.inserted_id)

    return jsonify(todo), 201


@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    if 'email' not in session:
        return jsonify({'error': 'Please login first'}), 401

    data = request.get_json()

    try:
        todo = todos.find_one({'_id': ObjectId(todo_id), 'user_email': session['email']})
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404

        updates = {}
        if 'title' in data:
            updates['title'] = data['title']
        if 'description' in data:
            updates['description'] = data['description']
        if 'completed' in data:
            updates['completed'] = data['completed']

        todos.update_one({'_id': ObjectId(todo_id)}, {'$set': updates})
        return jsonify({'message': 'Todo updated successfully'})
    except:
        return jsonify({'error': 'Invalid todo ID'}), 400


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    if 'email' not in session:
        return jsonify({'error': 'Please login first'}), 401

    try:
        result = todos.delete_one({'_id': ObjectId(todo_id), 'user_email': session['email']})
        if result.deleted_count == 0:
            return jsonify({'error': 'Todo not found'}), 404
        return jsonify({'message': 'Todo deleted successfully'})
    except:
        return jsonify({'error': 'Invalid todo ID'}), 400


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


if __name__ == '__main__':
    app.run(debug=False)