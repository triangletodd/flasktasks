from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def init_db():
    with sqlite3.connect('todos.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                parent_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES todos (id) ON DELETE CASCADE
            )
        ''')
        
        # Add parent_id column to existing table if it doesn't exist
        try:
            conn.execute('ALTER TABLE todos ADD COLUMN parent_id INTEGER')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()

def get_todos_hierarchical():
    with sqlite3.connect('todos.db') as conn:
        conn.row_factory = sqlite3.Row
        
        # Get all todos with their children count
        todos = conn.execute('''
            SELECT t.*, 
                   COUNT(c.id) as child_count,
                   COALESCE(p.task, '') as parent_task
            FROM todos t
            LEFT JOIN todos c ON t.id = c.parent_id
            LEFT JOIN todos p ON t.parent_id = p.id
            GROUP BY t.id
            ORDER BY 
                COALESCE(t.parent_id, t.id),
                CASE WHEN t.parent_id IS NULL THEN 0 ELSE 1 END,
                t.completed ASC,
                t.created_at DESC
        ''').fetchall()
        
        return todos

def get_todos():
    return get_todos_hierarchical()

@app.route('/')
def index():
    todos = get_todos()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    task = request.form.get('task', '').strip()
    parent_id = request.form.get('parent_id', None)
    
    if task:
        with sqlite3.connect('todos.db') as conn:
            if parent_id:
                conn.execute('INSERT INTO todos (task, parent_id) VALUES (?, ?)', (task, parent_id))
            else:
                conn.execute('INSERT INTO todos (task) VALUES (?)', (task,))
            conn.commit()
        flash('Task added successfully!', 'success')
    else:
        flash('Please enter a task!', 'error')
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    with sqlite3.connect('todos.db') as conn:
        conn.execute(
            'UPDATE todos SET completed = NOT completed, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (todo_id,)
        )
        conn.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    with sqlite3.connect('todos.db') as conn:
        # Delete the todo and its children (CASCADE will handle children)
        conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
    flash('Task deleted!', 'info')
    return redirect(url_for('index'))

@app.route('/toggle_with_children/<int:todo_id>')
def toggle_todo_with_children(todo_id):
    with sqlite3.connect('todos.db') as conn:
        # Get the current completion status
        current = conn.execute('SELECT completed FROM todos WHERE id = ?', (todo_id,)).fetchone()
        if current:
            new_status = not current[0]
            # Update parent and all children
            conn.execute(
                'UPDATE todos SET completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? OR parent_id = ?',
                (new_status, todo_id, todo_id)
            )
            conn.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    new_task = request.form.get('task', '').strip()
    if new_task:
        with sqlite3.connect('todos.db') as conn:
            conn.execute(
                'UPDATE todos SET task = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (new_task, todo_id)
            )
            conn.commit()
        flash('Task updated!', 'success')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)