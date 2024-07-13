import sys
print(sys.path)
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:secret@localhost:5432/todo_db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    date = db.Column(db.Date)
    notes = db.Column(db.Text)
    reminder = db.Column(db.DateTime)
    priority = db.Column(db.Integer)
    tag = db.Column(db.String(50))
    category = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('todos', lazy=True))

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('notes', lazy=True))
    


@app.route('/')
def index():
    todos = Todo.query.all()
    notes = Note.query.all()
    return render_template('index.html', todos = todos, notes = notes)


if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0' )