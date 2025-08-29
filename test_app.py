"""
Fixed version of test_app.py - comprehensive Flask application tests.

This version fixes the recursion errors by using temporary directories
instead of complex database connection mocking.
"""

import unittest
import tempfile
import os
import sqlite3
import shutil
from app import app, init_db, get_todos_hierarchical


class FlaskTasksTestCase(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Change to test directory so todos.db is created there
        os.chdir(self.test_dir)
        
        # Configure Flask for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Initialize the test database
        init_db()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Change back to original directory
        os.chdir(self.original_cwd)
        
        # Clean up test directory
        shutil.rmtree(self.test_dir)
    
    def test_index_empty(self):
        """Test the index page with no tasks."""
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'No tasks yet!', rv.data)
        self.assertIn(b'FlaskTasks', rv.data)
    
    def test_add_task(self):
        """Test adding a new task."""
        rv = self.client.post('/add', data={'task': 'Test task'})
        self.assertEqual(rv.status_code, 302)  # Redirect after POST
        
        # Check that the task appears on the index page
        rv = self.client.get('/')
        self.assertIn(b'Test task', rv.data)
        self.assertIn(b'Task added successfully!', rv.data)
    
    def test_add_empty_task(self):
        """Test adding an empty task should fail."""
        rv = self.client.post('/add', data={'task': ''})
        self.assertEqual(rv.status_code, 302)
        
        # Should show error message
        rv = self.client.get('/')
        self.assertIn(b'Please enter a task!', rv.data)
    
    def test_add_subtask(self):
        """Test adding a subtask to a parent task."""
        # First add a parent task
        self.client.post('/add', data={'task': 'Parent task'})
        
        # Get the task ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent task',))
            parent_id = cursor.fetchone()[0]
        
        # Add a subtask
        rv = self.client.post('/add', data={'task': 'Subtask', 'parent_id': parent_id})
        self.assertEqual(rv.status_code, 302)
        
        # Check both tasks appear
        rv = self.client.get('/')
        self.assertIn(b'Parent task', rv.data)
        self.assertIn(b'Subtask', rv.data)
        self.assertIn(b'1 subtask', rv.data)
    
    def test_toggle_task_completion(self):
        """Test toggling task completion status."""
        # Add a task
        self.client.post('/add', data={'task': 'Test task'})
        
        # Get the task ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Test task',))
            task_id = cursor.fetchone()[0]
        
        # Toggle completion
        rv = self.client.get(f'/toggle/{task_id}')
        self.assertEqual(rv.status_code, 302)
        
        # Check task is marked as completed in database
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT completed FROM todos WHERE id = ?', (task_id,))
            completed = cursor.fetchone()[0]
            self.assertTrue(completed)
    
    def test_edit_task(self):
        """Test editing a task."""
        # Add a task
        self.client.post('/add', data={'task': 'Original task'})
        
        # Get the task ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Original task',))
            task_id = cursor.fetchone()[0]
        
        # Edit the task
        rv = self.client.post(f'/edit/{task_id}', data={'task': 'Updated task'})
        self.assertEqual(rv.status_code, 302)
        
        # Check the task was updated
        rv = self.client.get('/')
        self.assertIn(b'Updated task', rv.data)
        self.assertIn(b'Task updated!', rv.data)
        self.assertNotIn(b'Original task', rv.data)
    
    def test_delete_task(self):
        """Test deleting a task."""
        # Add a task
        self.client.post('/add', data={'task': 'Task to delete'})
        
        # Get the task ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Task to delete',))
            task_id = cursor.fetchone()[0]
        
        # Delete the task
        rv = self.client.get(f'/delete/{task_id}')
        self.assertEqual(rv.status_code, 302)
        
        # Check the task is gone
        rv = self.client.get('/')
        self.assertNotIn(b'Task to delete', rv.data)
        self.assertIn(b'Task deleted!', rv.data)
    
    def test_delete_task_with_subtasks(self):
        """Test deleting a parent task also deletes subtasks."""
        # Add parent task
        self.client.post('/add', data={'task': 'Parent task'})
        
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent task',))
            parent_id = cursor.fetchone()[0]
        
        # Add subtask
        self.client.post('/add', data={'task': 'Subtask', 'parent_id': parent_id})
        
        # Verify we have 2 tasks before deletion
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM todos')
            count_before = cursor.fetchone()[0]
            self.assertEqual(count_before, 2)
        
        # Delete parent task
        rv = self.client.get(f'/delete/{parent_id}')
        self.assertEqual(rv.status_code, 302)
        
        # Check that parent task is deleted
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM todos WHERE id = ?', (parent_id,))
            parent_count = cursor.fetchone()[0]
            self.assertEqual(parent_count, 0)  # Parent should be deleted
    
    def test_toggle_with_children(self):
        """Test toggling parent task with all children."""
        # Add parent task
        self.client.post('/add', data={'task': 'Parent task'})
        
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent task',))
            parent_id = cursor.fetchone()[0]
        
        # Add subtask
        self.client.post('/add', data={'task': 'Subtask', 'parent_id': parent_id})
        
        # Toggle parent with children
        rv = self.client.get(f'/toggle_with_children/{parent_id}')
        self.assertEqual(rv.status_code, 302)
        
        # Check both tasks are completed
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT completed FROM todos')
            results = cursor.fetchall()
            for result in results:
                self.assertTrue(result[0])
    
    def test_about_page(self):
        """Test the about page loads correctly."""
        rv = self.client.get('/about')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'About FlaskTasks', rv.data)
        self.assertIn(b'task management application', rv.data)
    
    def test_database_initialization(self):
        """Test that the database initializes correctly."""
        with sqlite3.connect('todos.db') as conn:
            # Check that the todos table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
            )
            table = cursor.fetchone()
            self.assertIsNotNone(table)
            
            # Check table structure
            cursor = conn.execute("PRAGMA table_info(todos)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'task', 'completed', 'parent_id', 'created_at', 'updated_at']
            for col in expected_columns:
                self.assertIn(col, column_names)
    
    def test_hierarchical_task_retrieval(self):
        """Test the get_todos_hierarchical function."""
        # Add tasks with hierarchy
        self.client.post('/add', data={'task': 'Parent 1'})
        self.client.post('/add', data={'task': 'Parent 2'})
        
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent 1',))
            parent1_id = cursor.fetchone()[0]
        
        self.client.post('/add', data={'task': 'Child 1', 'parent_id': parent1_id})
        self.client.post('/add', data={'task': 'Child 2', 'parent_id': parent1_id})
        
        # Test hierarchical retrieval
        todos = get_todos_hierarchical()
        
        # Should have 4 tasks total
        self.assertEqual(len(todos), 4)
        
        # Parent tasks should have child_count > 0
        parent_tasks = [todo for todo in todos if todo['parent_id'] is None]
        parent1 = next((t for t in parent_tasks if t['task'] == 'Parent 1'), None)
        parent2 = next((t for t in parent_tasks if t['task'] == 'Parent 2'), None)
        
        self.assertIsNotNone(parent1)
        self.assertIsNotNone(parent2)
        self.assertEqual(parent1['child_count'], 2)
        self.assertEqual(parent2['child_count'], 0)
    
    def test_task_stats_display(self):
        """Test that task statistics are displayed correctly."""
        # Add some tasks with different completion states
        self.client.post('/add', data={'task': 'Completed task'})
        self.client.post('/add', data={'task': 'Pending task'})
        
        # Complete the first task
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Completed task',))
            task_id = cursor.fetchone()[0]
        
        self.client.get(f'/toggle/{task_id}')
        
        # Check stats on index page
        rv = self.client.get('/')
        self.assertIn(b'Total: 2', rv.data)
        self.assertIn(b'Pending: 1', rv.data)
        self.assertIn(b'Completed: 1', rv.data)
    
    def test_error_handling_invalid_ids(self):
        """Test error handling for invalid task IDs."""
        invalid_id = 99999
        
        # These operations should not crash
        rv = self.client.get(f'/toggle/{invalid_id}')
        self.assertEqual(rv.status_code, 302)
        
        rv = self.client.get(f'/delete/{invalid_id}')
        self.assertEqual(rv.status_code, 302)
        
        rv = self.client.post(f'/edit/{invalid_id}', data={'task': 'Updated'})
        self.assertEqual(rv.status_code, 302)
        
        rv = self.client.get(f'/toggle_with_children/{invalid_id}')
        self.assertEqual(rv.status_code, 302)
    
    def test_flash_message_handling(self):
        """Test that flash messages work correctly."""
        # Add empty task should show error
        rv = self.client.post('/add', data={'task': ''}, follow_redirects=True)
        self.assertIn(b'Please enter a task!', rv.data)
        
        # Add valid task should show success
        rv = self.client.post('/add', data={'task': 'Valid task'}, follow_redirects=True)
        self.assertIn(b'Task added successfully!', rv.data)


class DatabaseFunctionsTest(unittest.TestCase):
    """Test database functions in isolation."""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_init_db_creates_table(self):
        """Test that init_db creates the todos table correctly."""
        init_db()
        
        # Verify table exists and has correct structure
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute("PRAGMA table_info(todos)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'task', 'completed', 'parent_id', 'created_at', 'updated_at']
            for col in expected_columns:
                self.assertIn(col, column_names)
    
    def test_get_todos_hierarchical_empty(self):
        """Test get_todos_hierarchical with empty database."""
        init_db()
        todos = get_todos_hierarchical()
        self.assertEqual(len(todos), 0)
    
    def test_get_todos_hierarchical_with_data(self):
        """Test get_todos_hierarchical with actual data."""
        init_db()
        
        # Add test data
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('INSERT INTO todos (task) VALUES (?)', ('Parent Task',))
            parent_id = cursor.lastrowid
            conn.execute('INSERT INTO todos (task, parent_id) VALUES (?, ?)', ('Child Task', parent_id))
            conn.commit()
        
        todos = get_todos_hierarchical()
        self.assertEqual(len(todos), 2)
        
        # Find parent task
        parent = next((t for t in todos if t['parent_id'] is None), None)
        self.assertIsNotNone(parent)
        self.assertEqual(parent['task'], 'Parent Task')
        self.assertEqual(parent['child_count'], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)