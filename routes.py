from flask import Blueprint, request, jsonify
from models import db, bcrypt, User, Todo, Note
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import pinecone
from langchain.llms import OpenAI

routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"token": access_token})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@routes.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_todo = Todo(
        user_id=user_id,
        title=data['title'],
        date=data.get('date'),
        notes=data.get('notes'),
        reminder=data.get('reminder'),
        priority=data.get('priority'),
        tag=data.get('tag'),
        category=data.get('category')
    )
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.id), 201

@routes.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()
    todos = Todo.query.filter_by(user_id=user_id).all()
    return jsonify([todo.as_dict() for todo in todos])

@routes.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_note = Note(
        user_id=user_id,
        title=data['title'],
        content=data['content']
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify(new_note.id), 201

@routes.route('/notes', methond = ['GET'])
@jwt_required()
def get_notes():
    user_id = get_jwt_identitiy()
    notes = Note.query.filter_by(user_id = user_id).all()
    return jsonify([note.as_dict() for note in notes])

# Initialize Pinecone
pinecone.init(api_key='your_pinecone_api_key')
pinecone_index = pinecone.Index("todo_index")

@routes.route('/index-todos', methods=['POST'])
@jwt_required()
def index_todos():
    user_id = get_jwt_identity()
    todos = Todo.query.filter_by(user_id=user_id).all()
    todo_vectors = [{
        'id': str(todo.id),
        'values': [todo.priority, todo.date.toordinal() if todo.date else 0],  # Example vector
        'metadata': {
            'title': todo.title,
            'notes': todo.notes,
            'reminder': todo.reminder,
            'tag': todo.tag,
            'category': todo.category
        }
    } for todo in todos]

    pinecone_index.upsert(vectors=todo_vectors)
    return jsonify({"message": "Todos indexed"}), 200

openai = OpenAI(api_key='your_openai_api_key')

@routes.route('/query-todos', methods=['POST'])
@jwt_required()
def query_todos():
    user_id = get_jwt_identity()
    query = request.get_json().get('query')

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=f"Convert the following natural language query to SQL: {query}",
        max_tokens=100
    )

    sql_query = response.choices[0].text.strip()
    result = db.session.execute(sql_query).fetchall()
    return jsonify([dict(row) for row in result])
