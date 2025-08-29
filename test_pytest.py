"""
Fixed pytest-based tests for FlaskTasks application.

These tests use pytest fixtures and are designed to work with the fixed conftest.py configuration.
Uses temporary directories to avoid recursion issues.
"""

import pytest
import sqlite3
from bs4 import BeautifulSoup


class TestBasicFunctionality:
    """Test basic CRUD operations using pytest."""
    
    def test_index_page_loads(self, client):
        """Test that the index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'FlaskTasks' in response.data
    
    def test_add_task_success(self, client):
        """Test adding a task successfully."""
        response = client.post('/add', data={'task': 'Test Task'})
        assert response.status_code == 302  # Redirect after POST
        
        # Check task appears on index
        response = client.get('/')
        assert b'Test Task' in response.data
    
    def test_add_empty_task_fails(self, client):
        """Test that adding empty task shows error."""
        response = client.post('/add', data={'task': ''})
        assert response.status_code == 302
        
        # Check error message appears
        response = client.get('/')
        assert b'Please enter a task!' in response.data
    
    def test_toggle_task_completion(self, client, sample_task):
        """Test toggling task completion status."""
        task_id = sample_task['id']
        
        # Toggle completion
        response = client.get(f'/toggle/{task_id}')
        assert response.status_code == 302
        
        # Check task is marked completed in the UI
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        completed_task = soup.find('div', class_='completed')
        assert completed_task is not None
    
    def test_edit_task(self, client, sample_task):
        """Test editing a task."""
        task_id = sample_task['id']
        
        response = client.post(f'/edit/{task_id}', data={'task': 'Updated Task'})
        assert response.status_code == 302
        
        # Check updated text appears
        response = client.get('/')
        assert b'Updated Task' in response.data
        assert b'Sample test task' not in response.data
    
    def test_delete_task(self, client, sample_task):
        """Test deleting a task."""
        task_id = sample_task['id']
        
        response = client.get(f'/delete/{task_id}')
        assert response.status_code == 302
        
        # Check task is gone and success message appears
        response = client.get('/')
        assert b'Sample test task' not in response.data
        assert b'Task deleted!' in response.data


class TestHierarchicalTasks:
    """Test hierarchical task functionality."""
    
    def test_add_subtask(self, client):
        """Test adding a subtask to a parent."""
        # Add parent task
        client.post('/add', data={'task': 'Parent Task'})
        
        # Get parent ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent Task',))
            parent_id = cursor.fetchone()[0]
        
        # Add subtask
        response = client.post('/add', data={'task': 'Child Task', 'parent_id': parent_id})
        assert response.status_code == 302
        
        # Check both tasks appear with proper hierarchy
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        parent_task = soup.find('div', class_='parent-todo')
        child_task = soup.find('div', class_='nested-todo')
        
        assert parent_task is not None
        assert child_task is not None
        assert b'1 subtask' in response.data
    
    def test_delete_parent_deletes_children(self, client, sample_hierarchy):
        """Test that deleting parent task also deletes children."""
        parent_id = sample_hierarchy['parent']['id']
        
        # Delete parent
        response = client.get(f'/delete/{parent_id}')
        assert response.status_code == 302
        
        # Check parent task is gone from UI
        response = client.get('/')
        assert b'Parent Task' not in response.data
    
    def test_toggle_with_children(self, client, sample_hierarchy):
        """Test toggling parent with all children."""
        parent_id = sample_hierarchy['parent']['id']
        
        response = client.get(f'/toggle_with_children/{parent_id}')
        assert response.status_code == 302
        
        # Check all tasks are completed
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        completed_tasks = soup.find_all('div', class_='completed')
        assert len(completed_tasks) == 3  # Parent + 2 children


class TestTemplateRendering:
    """Test template rendering and HTML structure."""
    
    def test_navbar_structure(self, client):
        """Test navbar contains correct elements."""
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        navbar = soup.find('nav', class_='navbar')
        assert navbar is not None
        
        brand = navbar.find('a', class_='navbar-brand')
        assert brand is not None
        assert 'FlaskTasks' in brand.text
        
        nav_links = navbar.find_all('a', class_='nav-link')
        link_texts = [link.text.strip() for link in nav_links]
        assert 'Tasks' in link_texts
        assert 'About' in link_texts
    
    def test_form_structure(self, client):
        """Test task addition form structure."""
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        form = soup.find('form', action='/add')
        assert form is not None
        assert form.get('method') == 'post'
        
        task_input = form.find('input', {'name': 'task'})
        assert task_input is not None
        assert task_input.has_attr('required')
        assert 'Add a new task' in task_input.get('placeholder', '')
        
        submit_btn = form.find('button', type='submit')
        assert submit_btn is not None
        assert 'Add Task' in submit_btn.get_text()
    
    def test_empty_state(self, client):
        """Test empty state display."""
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        empty_message = soup.find('h3', class_='text-muted')
        assert empty_message is not None
        assert 'No tasks yet' in empty_message.text
        
        empty_icon = soup.find('i', class_='bi-clipboard-x')
        assert empty_icon is not None
    
    def test_task_stats_display(self, client, sample_hierarchy):
        """Test that task statistics display correctly."""
        # Complete one task
        parent_id = sample_hierarchy['parent']['id']
        child_id = parent_id + 1  # First child
        client.get(f'/toggle/{child_id}')
        
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        stats = soup.find('div', class_='todo-stats')
        assert stats is not None
        assert 'Total: 3' in stats.text
        assert 'Pending: 2' in stats.text
        assert 'Completed: 1' in stats.text


class TestAboutPage:
    """Test about page functionality."""
    
    def test_about_page_loads(self, client):
        """Test about page loads correctly."""
        response = client.get('/about')
        assert response.status_code == 200
        assert b'About FlaskTasks' in response.data
    
    def test_about_page_content(self, client):
        """Test about page contains expected content."""
        response = client.get('/about')
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check main heading
        heading = soup.find('h1')
        assert heading is not None
        assert 'About FlaskTasks' in heading.text
        
        # Check description
        description = soup.find('p', class_='lead')
        assert description is not None
        assert 'task management application' in description.text
        
        # Check features section
        features_list = soup.find('ul', class_='list-group-flush')
        assert features_list is not None
        features_text = features_list.get_text()
        assert 'Add, edit, and delete tasks' in features_text
        
        # Check back button - find button that actually says "Back to Tasks"
        back_button = soup.find('a', string=lambda text: text and 'Back to Tasks' in text)
        if not back_button:
            # Look for any link with "Back" in the text
            back_links = soup.find_all('a', href='/')
            back_button = next((link for link in back_links if 'Back' in link.get_text()), None)
        
        assert back_button is not None, "Could not find back button to tasks"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_task_id_toggle(self, client):
        """Test toggling non-existent task ID."""
        response = client.get('/toggle/999')
        # Should redirect without error (graceful handling)
        assert response.status_code == 302
    
    def test_invalid_task_id_delete(self, client):
        """Test deleting non-existent task ID."""
        response = client.get('/delete/999')
        # Should redirect without error (graceful handling)
        assert response.status_code == 302
    
    def test_invalid_task_id_edit(self, client):
        """Test editing non-existent task ID."""
        response = client.post('/edit/999', data={'task': 'Updated'})
        # Should redirect without error (graceful handling)
        assert response.status_code == 302
    
    def test_edit_with_empty_task(self, client, sample_task):
        """Test editing task with empty content."""
        task_id = sample_task['id']
        response = client.post(f'/edit/{task_id}', data={'task': ''})
        assert response.status_code == 302
        
        # Original task should still exist
        response = client.get('/')
        assert b'Sample test task' in response.data


@pytest.mark.integration
class TestFullUserJourney:
    """Integration tests covering full user workflows."""
    
    def test_complete_task_workflow(self, client):
        """Test complete workflow: add, edit, complete, delete."""
        # Add task
        response = client.post('/add', data={'task': 'Workflow Task'})
        assert response.status_code == 302
        
        # Get task ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Workflow Task',))
            task_id = cursor.fetchone()[0]
        
        # Edit task
        response = client.post(f'/edit/{task_id}', data={'task': 'Updated Workflow Task'})
        assert response.status_code == 302
        
        # Complete task
        response = client.get(f'/toggle/{task_id}')
        assert response.status_code == 302
        
        # Verify completion
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        completed_task = soup.find('div', class_='completed')
        assert completed_task is not None
        
        # Delete task
        response = client.get(f'/delete/{task_id}')
        assert response.status_code == 302
        
        # Verify deletion
        response = client.get('/')
        assert b'Updated Workflow Task' not in response.data
        assert b'No tasks yet!' in response.data
    
    def test_hierarchical_workflow(self, client):
        """Test workflow with nested tasks."""
        # Create parent
        client.post('/add', data={'task': 'Project'})
        
        # Get parent ID
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Project',))
            parent_id = cursor.fetchone()[0]
        
        # Create subtasks
        client.post('/add', data={'task': 'Subtask 1', 'parent_id': parent_id})
        client.post('/add', data={'task': 'Subtask 2', 'parent_id': parent_id})
        
        # Complete all at once
        response = client.get(f'/toggle_with_children/{parent_id}')
        assert response.status_code == 302
        
        # Verify all completed
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        completed_tasks = soup.find_all('div', class_='completed')
        assert len(completed_tasks) == 3
        
        # Toggle again to uncomplete all
        response = client.get(f'/toggle_with_children/{parent_id}')
        assert response.status_code == 302
        
        # Verify all uncompleted
        response = client.get('/')
        soup = BeautifulSoup(response.data, 'html.parser')
        completed_tasks = soup.find_all('div', class_='completed')
        assert len(completed_tasks) == 0


class TestDatabaseFunctions:
    """Test database functions directly."""
    
    def test_database_schema(self, client):
        """Test that database has correct schema."""
        with sqlite3.connect('todos.db') as conn:
            # Check table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='todos'"
            )
            assert cursor.fetchone() is not None
            
            # Check columns
            cursor = conn.execute("PRAGMA table_info(todos)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = ['id', 'task', 'completed', 'parent_id', 'created_at', 'updated_at']
            for col in expected_columns:
                assert col in column_names
    
    def test_hierarchical_data_structure(self, client, sample_hierarchy):
        """Test hierarchical data is stored correctly."""
        with sqlite3.connect('todos.db') as conn:
            # Check parent has no parent_id
            cursor = conn.execute('SELECT parent_id FROM todos WHERE task = ?', ('Parent Task',))
            parent_result = cursor.fetchone()
            assert parent_result[0] is None
            
            # Check children have correct parent_id
            cursor = conn.execute('SELECT parent_id FROM todos WHERE task LIKE ?', ('Child Task%',))
            children_results = cursor.fetchall()
            for result in children_results:
                assert result[0] == sample_hierarchy['parent']['id']