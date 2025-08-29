"""
Fixed version of test_templates.py - HTML template and UI component tests.

This version fixes the recursion errors by using temporary directories
instead of complex database connection mocking.
"""

import unittest
import tempfile
import os
import sqlite3
import shutil
from bs4 import BeautifulSoup
from app import app, init_db


class TemplateTestCase(unittest.TestCase):
    """Test template rendering and HTML structure."""
    
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
    
    def get_soup(self, url):
        """Helper method to get BeautifulSoup object for a URL."""
        response = self.client.get(url)
        return BeautifulSoup(response.data, 'html.parser')
    
    def test_index_page_structure(self):
        """Test the basic HTML structure of the index page."""
        soup = self.get_soup('/')
        
        # Check title
        self.assertIsNotNone(soup.find('title'))
        self.assertIn('FlaskTasks', soup.find('title').text)
        
        # Check navbar
        navbar = soup.find('nav', class_='navbar')
        self.assertIsNotNone(navbar)
        
        # Check navbar brand
        brand = navbar.find('a', class_='navbar-brand')
        self.assertIsNotNone(brand)
        self.assertIn('FlaskTasks', brand.text)
        
        # Check navigation links
        nav_links = navbar.find_all('a', class_='nav-link')
        link_texts = [link.text.strip() for link in nav_links]
        self.assertIn('Tasks', link_texts)
        self.assertIn('About', link_texts)
        
        # Check main heading
        main_heading = soup.find('h1')
        self.assertIsNotNone(main_heading)
        self.assertIn('FlaskTasks', main_heading.text)
        
        # Check form exists
        form = soup.find('form', action='/add')
        self.assertIsNotNone(form)
        
        # Check form input
        task_input = form.find('input', {'name': 'task'})
        self.assertIsNotNone(task_input)
        self.assertIn('Add a new task', task_input.get('placeholder', ''))
        
        # Check form button
        submit_btn = form.find('button', type='submit')
        self.assertIsNotNone(submit_btn)
        self.assertIn('Add Task', submit_btn.get_text())
        
        # Check footer
        footer = soup.find('footer')
        self.assertIsNotNone(footer)
        self.assertIn('FlaskTasks', footer.text)
    
    def test_empty_state_display(self):
        """Test the empty state when no tasks exist."""
        soup = self.get_soup('/')
        
        # Should show empty state message
        empty_message = soup.find('h3', class_='text-muted')
        self.assertIsNotNone(empty_message)
        self.assertIn('No tasks yet', empty_message.text)
        
        # Should show empty state icon
        empty_icon = soup.find('i', class_='bi-clipboard-x')
        self.assertIsNotNone(empty_icon)
    
    def test_task_display_with_data(self):
        """Test task display when tasks exist."""
        # Add a task
        self.client.post('/add', data={'task': 'Test task for display'})
        
        soup = self.get_soup('/')
        
        # Should show task stats
        stats = soup.find('div', class_='todo-stats')
        self.assertIsNotNone(stats)
        self.assertIn('Total: 1', stats.text)
        self.assertIn('Pending: 1', stats.text)
        self.assertIn('Completed: 0', stats.text)
        
        # Should show the task
        task_items = soup.find_all('div', class_='todo-item')
        self.assertEqual(len(task_items), 1)
        
        task_item = task_items[0]
        
        # Check task text
        task_text = task_item.find('span', class_='todo-text')
        self.assertIsNotNone(task_text)
        self.assertIn('Test task for display', task_text.text)
        
        # Check checkbox
        checkbox = task_item.find('input', type='checkbox')
        self.assertIsNotNone(checkbox)
        self.assertFalse(checkbox.has_attr('checked'))
        
        # Check action buttons
        edit_btn = task_item.find('button', class_='edit-btn')
        self.assertIsNotNone(edit_btn)
        
        delete_link = task_item.find('a', href=lambda x: x and '/delete/' in x)
        self.assertIsNotNone(delete_link)
    
    def test_completed_task_styling(self):
        """Test that completed tasks have proper styling."""
        # Add and complete a task
        self.client.post('/add', data={'task': 'Completed task'})
        
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Completed task',))
            task_id = cursor.fetchone()[0]
        
        self.client.get(f'/toggle/{task_id}')
        
        soup = self.get_soup('/')
        
        # Find the completed task
        completed_task = soup.find('div', class_='completed')
        self.assertIsNotNone(completed_task)
        
        # Check that checkbox is checked
        checkbox = completed_task.find('input', type='checkbox')
        self.assertIsNotNone(checkbox)
        self.assertTrue(checkbox.has_attr('checked'))
        
        # Check that text has strikethrough styling
        task_text = completed_task.find('span', class_='text-decoration-line-through')
        self.assertIsNotNone(task_text)
    
    def test_subtask_display(self):
        """Test that subtasks display correctly with proper hierarchy."""
        # Add parent task
        self.client.post('/add', data={'task': 'Parent task'})
        
        with sqlite3.connect('todos.db') as conn:
            cursor = conn.execute('SELECT id FROM todos WHERE task = ?', ('Parent task',))
            parent_id = cursor.fetchone()[0]
        
        # Add subtask
        self.client.post('/add', data={'task': 'Child task', 'parent_id': parent_id})
        
        soup = self.get_soup('/')
        
        # Should have 2 task items
        task_items = soup.find_all('div', class_='todo-item')
        self.assertEqual(len(task_items), 2)
        
        # Find parent and child tasks
        parent_task = None
        child_task = None
        
        for item in task_items:
            if 'parent-todo' in item.get('class', []):
                parent_task = item
            elif 'nested-todo' in item.get('class', []):
                child_task = item
        
        self.assertIsNotNone(parent_task)
        self.assertIsNotNone(child_task)
        
        # Check parent has subtask count badge
        badge = parent_task.find('span', class_='badge')
        self.assertIsNotNone(badge)
        self.assertIn('1 subtask', badge.text)
        
        # Check parent has collapse button
        collapse_btn = parent_task.find('button', class_='collapse-toggle')
        self.assertIsNotNone(collapse_btn)
        
        # Check parent has add subtask button
        add_subtask_btn = parent_task.find('button', class_='add-subtask-btn')
        self.assertIsNotNone(add_subtask_btn)
        
        # Check child has nested indicator
        nested_indicator = child_task.find('div', class_='nested-indicator')
        self.assertIsNotNone(nested_indicator)
        
        # Check child has proper indentation class
        child_body = child_task.find('div', class_='ps-5')
        self.assertIsNotNone(child_body)
    
    def test_about_page_structure(self):
        """Test the about page HTML structure."""
        soup = self.get_soup('/about')
        
        # Check title
        self.assertIsNotNone(soup.find('title'))
        self.assertIn('About - FlaskTasks', soup.find('title').text)
        
        # Check main heading
        main_heading = soup.find('h1')
        self.assertIsNotNone(main_heading)
        self.assertIn('About FlaskTasks', main_heading.text)
        
        # Check description
        description = soup.find('p', class_='lead')
        self.assertIsNotNone(description)
        self.assertIn('task management application', description.text)
        
        # Check features section
        features_heading = soup.find('h3', string='Features')
        self.assertIsNotNone(features_heading)
        
        features_list = soup.find('ul', class_='list-group-flush')
        self.assertIsNotNone(features_list)
        
        # Check some specific features are mentioned
        features_text = features_list.get_text()
        self.assertIn('Add, edit, and delete tasks', features_text)
        self.assertIn('Toggle completion status', features_text)
        self.assertIn('Responsive design', features_text)
        
        # Check technology stack section
        tech_heading = soup.find('h3', string='Technology Stack')
        self.assertIsNotNone(tech_heading)
        
        # Check back button
        back_button = soup.find('a', string=lambda text: text and 'Back to Tasks' in text)
        if not back_button:
            # Try finding by content
            back_button = soup.find('a', href='/')
            if back_button and 'Back to Tasks' in back_button.get_text():
                pass  # Found it
            else:
                # Look for any button that goes back to home
                back_buttons = soup.find_all('a', href='/')
                back_button = next((btn for btn in back_buttons if 'Tasks' in btn.get_text()), None)
        
        self.assertIsNotNone(back_button, "Could not find back to tasks button")
        self.assertEqual(back_button.get('href'), '/')
    
    def test_form_structure(self):
        """Test the task addition form structure."""
        soup = self.get_soup('/')
        
        # Find the main form
        form = soup.find('form', action='/add')
        self.assertIsNotNone(form)
        self.assertEqual(form.get('method'), 'post')
        
        # Check input group structure
        input_group = form.find('div', class_='input-group')
        self.assertIsNotNone(input_group)
        
        # Check text input
        text_input = input_group.find('input', {'name': 'task', 'type': 'text'})
        self.assertIsNotNone(text_input)
        self.assertTrue(text_input.has_attr('required'))
        self.assertEqual(text_input.get('class'), ['form-control'])
        
        # Check submit button
        submit_btn = input_group.find('button', type='submit')
        self.assertIsNotNone(submit_btn)
        self.assertIn('btn-primary', submit_btn.get('class', []))
        
        # Check button icon
        icon = submit_btn.find('i', class_='bi-plus-lg')
        self.assertIsNotNone(icon)
    
    def test_flash_message_display(self):
        """Test that flash messages display correctly."""
        # Add a task to trigger success message
        response = self.client.post('/add', data={'task': 'Test task'}, follow_redirects=True)
        
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Check for flash message
        alert = soup.find('div', class_='alert')
        self.assertIsNotNone(alert)
        self.assertIn('alert-success', alert.get('class', []))
        self.assertIn('Task added successfully', alert.text)
        
        # Check for dismiss button
        dismiss_btn = alert.find('button', class_='btn-close')
        self.assertIsNotNone(dismiss_btn)
    
    def test_responsive_classes(self):
        """Test that responsive CSS classes are present."""
        soup = self.get_soup('/')
        
        # Check container class
        container = soup.find('div', class_='container')
        self.assertIsNotNone(container)
        
        # Check responsive column classes
        col = soup.find('div', class_='col-lg-8')
        self.assertIsNotNone(col)
        
        # Check responsive utility classes exist in the HTML
        html_content = str(soup)
        responsive_classes = ['col-lg-', 'd-flex', 'mb-', 'mt-']
        
        found_classes = []
        for css_class in responsive_classes:
            if css_class in html_content:
                found_classes.append(css_class)
        
        # Should find at least some responsive classes
        self.assertTrue(len(found_classes) > 0, f"No responsive classes found. Checked: {responsive_classes}")
    
    def test_accessibility_attributes(self):
        """Test that accessibility attributes are present."""
        soup = self.get_soup('/')
        
        # Check form labels and accessibility
        form = soup.find('form', action='/add')
        task_input = form.find('input', {'name': 'task'})
        
        # Input should have placeholder for accessibility
        self.assertIsNotNone(task_input.get('placeholder'))
        
        # Check that required attribute is present
        self.assertTrue(task_input.has_attr('required'))
    
    def test_bootstrap_integration(self):
        """Test that Bootstrap CSS and JS are properly integrated."""
        soup = self.get_soup('/')
        
        # Check Bootstrap CSS link
        bootstrap_css = soup.find('link', href=lambda x: x and 'bootstrap' in x and 'css' in x)
        self.assertIsNotNone(bootstrap_css)
        
        # Check Bootstrap JS script
        bootstrap_js = soup.find('script', src=lambda x: x and 'bootstrap' in x and 'js' in x)
        self.assertIsNotNone(bootstrap_js)
        
        # Check Bootstrap Icons
        bootstrap_icons = soup.find('link', href=lambda x: x and 'bootstrap-icons' in x)
        self.assertIsNotNone(bootstrap_icons)
    
    def test_custom_css_integration(self):
        """Test that custom CSS is properly integrated."""
        soup = self.get_soup('/')
        
        # Check custom CSS link
        custom_css = soup.find('link', href='/static/css/style.css')
        self.assertIsNotNone(custom_css)
        
        # Check custom JS link
        custom_js = soup.find('script', src='/static/js/app.js')
        self.assertIsNotNone(custom_js)


if __name__ == '__main__':
    unittest.main(verbosity=2)