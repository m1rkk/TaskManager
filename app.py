import werkzeug
from flask import Flask, flash,session, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from sqlalchemy import func

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = "secret"



db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    completed = db.Column(db.Boolean, default = False)



    def __repr__(self):
        return f'<Task>{self.id}'


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), unique = True, nullable = False)
    password = db.Column(db.String(200), nullable = False)

@login_manager.user_loader
def load_user(user_id):
    return  User.query.get(int(user_id))


@app.route("/")
@login_required
def index():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
@login_required
def add_task():
    task_content = request.form['content']
    if task_content:
        new_task = Task(content = task_content)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task_to_delete = Task.query.get(task_id)
    if task_to_delete:
        db.session.delete(task_to_delete)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
@login_required
def complete_task(task_id):
    task_to_complete = Task.query.get(task_id)
    if task_to_complete:
        task_to_complete.completed = True
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task_to_edit = Task.query.get(task_id)
    if request.method == "POST":
        task_to_edit.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", task=task_to_edit)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username = username).first()
        if existing_user:
            flash("This user already exist")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username = username, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username= username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session.pop('_flashes', None)
            return redirect(url_for("index"))
        else:
            flash("Incorrect password or login, please try again")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)