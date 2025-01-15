from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms.fields import StringField, DateField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date
import datetime

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tasks.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date,nullable=False)

with app.app_context():
    db.create_all()

class TaskForm(FlaskForm):
    description = StringField("Task Description",validators=[DataRequired()])
    date = DateField("Date to be Completed",validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/",methods=['GET','POST'])
def home():
    form = TaskForm()
    if request.method == "GET":
        with app.app_context():
            result = db.session.execute(db.select(Task))
            tasks = result.scalars().all()
            current_date = datetime.date.today()
        return render_template("index.html",form=form,tasks=tasks,cd=current_date)
    elif request.method == 'POST':
        if form.validate_on_submit():
            with app.app_context():
                if datetime.date.today() > form.date.data:
                    flash("The date you have entered is before the current date. Try again.")
                    return redirect(url_for("home"))

                task_to_add = Task(description=form.description.data,date=form.date.data)
                db.session.add(task_to_add)
                db.session.commit()
                return redirect(url_for("home"))

@app.route("/delete/<id>")
def delete(id):
    with app.app_context():
        task_to_delete = db.session.execute(db.select(Task).where(Task.id == id)).scalar()
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for("home"))

@app.route("/update/<id>",methods=['GET','POST'])
def update(id):
    form = TaskForm()
    if request.method == 'GET':
        return render_template("update.html",form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            with app.app_context():
                task_to_update = db.session.execute(db.select(Task).where(Task.id == id)).scalar()
                task_to_update.description = form.description.data
                task_to_update.date = form.date.data
                db.session.commit()
                return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()