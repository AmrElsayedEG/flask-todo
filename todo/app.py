from flask import Flask, render_template, request, jsonify
from werkzeug.utils import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

#############
#  Settings #
#############
app = Flask(__name__)
mar = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


#############
#   Models  #
#############
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f'<Task {self.id}>'


#################
#  Serializers  #
#################
class TodoSchema(mar.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "content")

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)


################
#  API Routes  #
################

# Get all Todos and Create
@app.route("/api", methods=["GET", "POST"])
def tasks_api():
    if request.method == "POST":
        if 'content' in request.form:
            task = Todo(content=request.form['content'])
            db.session.add(task)
            db.session.commit()
            return todo_schema.dump(task)
        return jsonify("Error")
    tasks = Todo.query.all()
    return jsonify(todos_schema.dump(tasks))

# Get one Todo and delete and update
@app.route("/api/<int:id>", methods=["GET", "DELETE", "PUT"])
def task_api(id):
    task = Todo.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify("Deleted")
    if request.method == "PUT":
        task.content = request.form['content']
        db.session.commit()
        return todo_schema.dump(task)
    return todo_schema.dump(task)



##################
#  Normal Routes #
##################
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        new_todo = Todo(content=request.form['content'])
        try:
            db.session.add(new_todo)
            db.session.commit()
            return redirect('/')
        except:
            return f"Error adding {new_todo}"
    tasks = Todo.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/task/<int:id>', methods=["GET", "POST", "DELETE"])
def task(id):
    task = Todo.query.get_or_404(id)
    if request.method == "DELETE":
        try:
            db.session.delete(task)
            db.session.commit()
            return redirect('/')
        except:
            return "Error deleting"
    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "ERROR"
    return render_template('task.html', task=task)

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except:
        return "Error deleting"
