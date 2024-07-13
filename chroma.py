import chromadb
from flask import request
from models import Todo

chroma_client = chromadb.Client()

@routes.route('/index-todos', methods=['POST'])
@jwt_required()
def index_todos():
    user_id = get_jwt_identity()
    todos = Todo.query.filter_by(user_id=user_id).all()
    todo_vectors = [{
        'id': todo.id,
        'values': [todo.priority, todo.date.toordinal() if todo.date else 0],  # Example vector
        'metadata': {
            'title': todo.title,
            'notes': todo.notes,
            'reminder': todo.reminder,
            'tag': todo.tag,
            'category': todo.category
        }
    } for todo in todos]

    chroma_client.upsert('todo_index', todo_vectors)
    return jsonify({"message": "Todos indexed"}), 200
