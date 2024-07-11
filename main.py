from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6'
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy()
db.init_app(app)


class ColumnNames(db.Model):
    __tablename__ = "column_names"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tasks = relationship('Task', back_populates='column_name')


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(250), nullable=False)
    column_id = db.Column(db.Integer, db.ForeignKey("column_names.id"))
    column_name = relationship('ColumnNames', back_populates='tasks')


with app.app_context():
    db.create_all()


with app.app_context():
    columns = db.session.execute((db.Select(ColumnNames))).scalars()
    if columns.first() is None:
        column1 = ColumnNames(name='Backlog')
        db.session.add(column1)
        task = Task(task_name='Example', column_id=1)
        db.session.add(task)
        db.session.commit()


class AddTaskForm(FlaskForm):
    new_task = StringField(label='New Task:', validators=[DataRequired()])
    submit = SubmitField(label='Add Task')


class AddColumnForm(FlaskForm):
    new_column = StringField(label='New Column', validators=[DataRequired()])
    submit = SubmitField(label='Add Column')


@app.route('/', methods=['GET', 'POST'])
def home():
    task_form = AddTaskForm()
    column_form = AddColumnForm()

    if request.args.get('new_task') is None:
        pass
    else:
        new_task = Task(task_name=request.args.get('new_task'), column_id=1)
        with app.app_context():
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for('home'))

    if request.args.get('new_column') is None:
        pass
    else:
        new_column = ColumnNames(name=request.args.get('new_column'))
        with app.app_context():
            db.session.add(new_column)
            db.session.commit()
        return redirect(url_for('home'))

    with app.app_context():
        columns = db.session.execute((db.Select(ColumnNames))).scalars()
        return render_template('index.html',
                               columns=columns,
                               task_form=task_form,
                               column_form=column_form,
                               )


@app.route('/move_task_right/<int:task_id>', methods=['GET', 'PATCH'])
def move_task_right(task_id):
    with app.app_context():
        columns = db.session.execute((db.Select(ColumnNames))).scalars()
        column_ids = [column.id for column in columns]
        task_to_move = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
        for n in range(len(column_ids)):
            if column_ids[n] == task_to_move.column_id:
                current_column_index = n
        try:
            task_to_move.column_id = column_ids[current_column_index + 1]
        except IndexError:
            return redirect(url_for('home'))
        else:
            db.session.commit()
            return redirect(url_for('home'))


@app.route('/move_task_left/<int:task_id>', methods=['GET', 'PATCH'])
def move_task_left(task_id):
    with app.app_context():
        columns = db.session.execute((db.Select(ColumnNames))).scalars()
        column_ids = [column.id for column in columns]
        task_to_move = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
        for n in range(len(column_ids)):
            if column_ids[n] == task_to_move.column_id:
                current_column_index = n
        if current_column_index - 1 < 0:
            pass
        else:
            task_to_move.column_id = column_ids[current_column_index - 1]
            db.session.commit()
        return redirect(url_for('home'))


@app.route('/delete_task/<int:task_id>', methods=['GET', 'DELETE'])
def delete_task(task_id):
    with app.app_context():
        task_to_delete = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/delete_column/<int:column_id>', methods=['GET', 'DELETE'])
def delete_column(column_id):
    with app.app_context():
        column_to_delete = db.session.execute(db.select(ColumnNames).where(ColumnNames.id == column_id)).scalar()
        db.session.delete(column_to_delete)
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(port=5001)
