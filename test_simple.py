"""
Simple, working tests for FlaskTasks application.

These tests use a direct approach and work with the actual application.
"""

import unittest
import tempfile
import os
import sqlite3
from app import app


class FlaskTasksTestCase(unittest.TestCase):
    """Test Flask application functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for the test database
        self.test_dir = tempfile.mkdtemp()
        self.original_db_path = 'todos.db'
        self.test_db_path = os.path.join(self.test_dir, 'test_todos.db')
        
        # Configure Flask for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Change working directory temporarily
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize test database
        self.init_test_db()
    
    def tearDown(self):
        """Clean up after tests."""
        # Change back to original directory
        os.chdir(self.original_cwd)
        
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    def init_test_db(self):
        """Initialize the test database."""
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
            conn.commit()
    
    def test_index_page_loads(self):
        """Test that the index page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'FlaskTasks', response.data)
        self.assertIn(b'No tasks yet!', response.data)
    
    def test_about_page_loads(self):
        """Test that the about page loads successfully."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About FlaskTasks', response.data)
        self.assertIn(b'task management application', response.data)
    
    def test_add_task_success(self):
        """Test adding a task successfully."""
        # Add a task
        response = self.client.post('/add', data={'task': 'Test Task'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Task', response.data)
        self.assertIn(b'Task added successfully!', response.data)
    
    def test_add_empty_task_fails(self):
        """Test that adding empty task shows error."""
        response = self.client.post('/add', data={'task': ''}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a task!', response.data)
    
    def test_task_operations_workflow(self):
        """Test complete task workflow: add, edit, toggle, delete."""
        # Add a task
        response = self.client.post('/add', data={'task': 'Workflow Task'}, follow_redirects=True)
        self.assertIn(b'Workflow Task', response.data)
        
        # Get the task ID from database
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Workflow Task',))
            task_row = cursor.fetchone()
            self.assertIsNotNone(task_row)
            task_id = task_row[0]
        
        # Edit the task
        response = self.client.post(f'/edit/{task_id}', 
                                  data={'task': 'Updated Workflow Task'}, 
                                  follow_redirects=True)
        self.assertIn(b'Updated Workflow Task', response.data)
        self.assertIn(b'Task updated!', response.data)
        
        # Toggle task completion
        response = self.client.get(f'/toggle/{task_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify task is completed in database
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT completed FROM todos WHERE id = ?', (task_id,))
            completed_row = cursor.fetchone()
            self.assertIsNotNone(completed_row)
            self.assertTrue(completed_row[0])
        
        # Delete the task
        response = self.client.get(f'/delete/{task_id}', follow_redirects=True)
        self.assertNotIn(b'Updated Workflow Task', response.data)
        self.assertIn(b'Task deleted!', response.data)
    
    def test_hierarchical_tasks(self):
        """Test parent-child task relationships."""
        # Add parent task
        response = self.client.post('/add', data={'task': 'Parent Task'}, follow_redirects=True)
        self.assertIn(b'Parent Task', response.data)
        
        # Get parent task ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent Task',))
            parent_id = cursor.fetchone()[0]
        
        # Add subtask
        response = self.client.post('/add', 
                                  data={'task': 'Child Task', 'parent_id': parent_id}, 
                                  follow_redirects=True)
        self.assertIn(b'Child Task', response.data)
        self.assertIn(b'Parent Task', response.data)
        
        # Test toggle with children
        response = self.client.get(f'/toggle_with_children/{parent_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify both tasks are completed
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT completed FROM todos WHERE id IN (?, ?)', 
                                (parent_id, parent_id + 1))
            results = cursor.fetchall()
            for result in results:
                self.assertTrue(result[0])
    
    def test_database_structure(self):
        """Test that database has correct structure."""
        with sqlite3.connect('todos.db') as conn:
            # Check table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
            )
            self.assertIsNotNone(cursor.fetchone())
            
            # Check columns
            cursor = conn.execute("PRAGMA table_info(todos)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'task', 'completed', 'parent_id', 'created_at', 'updated_at']
            for col in expected_columns:
                self.assertIn(col, column_names)
    
    def test_error_handling(self):
        """Test error handling for invalid operations."""
        # Test operations on non-existent task
        invalid_id = 99999
        
        # These should not crash the application
        response = self.client.get(f'/toggle/{invalid_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f'/delete/{invalid_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(f'/edit/{invalid_id}', 
                                  data={'task': 'Updated'}, 
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)


class BasicUITestCase(unittest.TestCase):
    """Test basic UI components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize test database
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
            conn.commit()
    
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_navbar_elements(self):
        """Test that navbar contains correct elements."""
        response = self.client.get('/')
        self.assertIn(b'FlaskTasks', response.data)
        self.assertIn(b'Tasks', response.data)
        self.assertIn(b'About', response.data)
    
    def test_form_elements(self):
        """Test that form elements are present."""
        response = self.client.get('/')
        self.assertIn(b'name="task"', response.data)
        self.assertIn(b'Add Task', response.data)
        self.assertIn(b'placeholder="Add a new task..."', response.data)
    
    def test_footer_present(self):
        """Test that footer is present."""
        response = self.client.get('/')
        self.assertIn(b'FlaskTasks. Built with Flask', response.data)
    
    def test_responsive_elements(self):
        """Test that responsive CSS classes are present."""
        response = self.client.get('/')
        # Check for Bootstrap classes
        self.assertIn(b'container', response.data)
        self.assertIn(b'col-lg-8', response.data)
        self.assertIn(b'btn btn-primary', response.data)


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)