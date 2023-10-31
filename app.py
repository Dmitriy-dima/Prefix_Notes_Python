import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired
from decouple import config

app = Flask(__name__)

# Define the path for the database file
db_file_path = os.path.join(app.instance_path, 'notes.db')

# Configure the Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Set a secret key for form security. Replace this with a strong, unique secret key.
app.config['SECRET_KEY'] = config('SECRET_KEY')

# Initialize the SQLAlchemy and Migrate extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class NoteForm(FlaskForm):
    """Form for creating and editing notes."""
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])

class Note(db.Model):
    """Model for the Note entity in the database."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String, nullable=False)

@app.route('/')
def index():
    notes = Note.query.all()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Handle the 'Add Note' page.
    """
    form = NoteForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        note = Note(title=title, content=content)
        try:
            db.session.add(note)
            db.session.commit()
            flash('Note added successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    return render_template('add.html', form=form)

@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit(note_id):
    """
    Handle the 'Edit Note' page for a specific note.
    """
    note = Note.query.get(note_id)
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('index'))
    
    form = NoteForm(obj=note)
    if form.validate_on_submit():
        form.populate_obj(note)
        try:
            db.session.commit()
            flash('Note updated successfully', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
    return render_template('edit.html', form=form, note=note)

@app.route('/delete/<int:note_id>', methods=['POST'])
def delete(note_id):
    """
    Handle the deletion of a specific note.
    """
    note = Note.query.get(note_id)
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('index'))
    
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """
    Handle note search based on a query parameter.
    """
    query = request.args.get('query')
    if query:
        notes = Note.query.filter(
            Note.title.like(f'%{query}%') | 
            Note.content.like(f'%{query}%')
        ).all()
    else:
        notes = Note.query.all()
    
    return render_template('index.html', notes=notes, is_search=bool(query))

if __name__ == '__main__':
    app.run(debug=True)
