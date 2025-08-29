"""
Fixed pytest configuration file for FlaskTasks application.

This file contains shared fixtures and configuration for all pytest tests.
Uses temporary directory approach to avoid recursion issues.
"""

import pytest
import tempfile
import os
import sqlite3
import shutil
from app import app, init_db


@pytest.fixture
def test_dir():
    """Create and cleanup temporary directory for tests."""
    test_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    # Change to test directory
    os.chdir(test_dir)
    
    yield test_dir
    
    # Cleanup
    os.chdir(original_cwd)
    shutil.rmtree(test_dir)


@pytest.fixture
def client(test_dir):
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


@pytest.fixture
def app_context():
    """Create an application context for testing."""
    with app.app_context():
        yield app


@pytest.fixture
def sample_task(client):
    """Create a sample task for testing."""
    response = client.post('/add', data={'task': 'Sample test task'})
    assert response.status_code == 302
    
    # Get the created task ID
    with sqlite3.connect('todos.db') as conn:
        cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Sample test task',))
        task_row = cursor.fetchone()
        task_id = task_row[0] if task_row else 1
    
    return {'task': 'Sample test task', 'id': task_id}


@pytest.fixture
def sample_hierarchy(client):
    """Create a sample task hierarchy for testing."""
    # Create parent task
    client.post('/add', data={'task': 'Parent Task'})
    
    # Get parent ID
    with sqlite3.connect('todos.db') as conn:
        cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent Task',))
        parent_id = cursor.fetchone()[0]
    
    # Create subtasks
    client.post('/add', data={'task': 'Child Task 1', 'parent_id': parent_id})
    client.post('/add', data={'task': 'Child Task 2', 'parent_id': parent_id})
    
    return {
        'parent': {'task': 'Parent Task', 'id': parent_id},
        'children': [
            {'task': 'Child Task 1', 'id': parent_id + 1, 'parent_id': parent_id},
            {'task': 'Child Task 2', 'id': parent_id + 2, 'parent_id': parent_id}
        ]
    }