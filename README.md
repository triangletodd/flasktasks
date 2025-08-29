# FlaskTasks

A responsive, feature-rich task management application built with Flask and SQLite, featuring nested subtasks and a clean, modern interface.

![FlaskTasks Screenshot](https://via.placeholder.com/800x400/007bff/ffffff?text=FlaskTasks)

## Features

### ✨ Core Functionality
- **Add, Edit, Delete Tasks** - Full CRUD operations with inline editing
- **Mark Complete/Incomplete** - Toggle completion status with visual feedback
- **Nested Subtasks** - Organize tasks with unlimited subtask nesting
- **Collapsible Interface** - Fold/expand subtasks to reduce visual clutter
- **Persistent Storage** - SQLite database ensures your data is always saved

### 🎨 User Experience
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Modern UI** - Bootstrap 5 with custom styling and smooth animations
- **Keyboard Shortcuts** - Quick actions with Ctrl/Cmd+Enter and Escape
- **Visual Hierarchy** - Clear indentation and color coding for nested tasks
- **Smart Persistence** - Remembers your collapse/expand preferences

### 🔧 Technical Features
- **Flask Backend** - Lightweight Python web framework
- **SQLite Database** - Self-contained, serverless database
- **Bootstrap Icons** - Comprehensive icon set for intuitive UI
- **Local Storage** - Client-side state persistence for UI preferences
- **Cross-Browser Compatible** - Works on Chrome, Firefox, Safari, Brave, and Edge

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd flasktasks
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

The database will be created automatically on first run.

## Usage Guide

### Basic Operations
- **Add Task**: Type in the input field and press Enter or click "Add Task"
- **Complete Task**: Click the checkbox next to any task
- **Edit Task**: Click the pencil icon and modify the text inline
- **Delete Task**: Click the trash icon (confirms before deletion)

### Working with Subtasks
- **Create Subtask**: Click the `+` button on any parent task
- **Expand/Collapse**: Click the chevron arrow (►/▼) to show/hide subtasks
- **Bulk Operations**: Use the "check all" button to toggle parent and all subtasks
- **Visual Indicators**: Subtasks are indented and show their parent relationship

### Keyboard Shortcuts
- `Ctrl/Cmd + Enter`: Quickly add new task
- `Escape`: Cancel editing or subtask creation
- `Enter`: Confirm inline edits

## Project Structure

```
flasktasks/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── todos.db              # SQLite database (created on first run)
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles and responsive design
│   └── js/
│       └── app.js        # Client-side functionality
└── templates/
    ├── index.html        # Main task interface
    └── about.html        # About page
```

## Database Schema

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    parent_id INTEGER,                    -- Links to parent task for nesting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES todos (id) ON DELETE CASCADE
);
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Display main task interface |
| POST | `/add` | Add new task (with optional parent_id) |
| GET | `/toggle/<id>` | Toggle completion status |
| GET | `/toggle_with_children/<id>` | Toggle parent and all subtasks |
| POST | `/edit/<id>` | Update task text |
| GET | `/delete/<id>` | Delete task and all subtasks |
| GET | `/about` | Display about page |

## Customization

### Styling
Modify `static/css/style.css` to customize:
- Color scheme and themes
- Layout and spacing
- Animation timing and effects
- Responsive breakpoints

### Functionality  
Extend `app.py` to add:
- User authentication
- Task categories/tags
- Due dates and reminders
- Import/export functionality
- REST API for mobile apps

## Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| Brave | Latest | ✅ Fully Supported |

## Dependencies

- **Flask 3.0.0** - Web framework
- **Werkzeug 3.0.1** - WSGI utilities
- **Bootstrap 5.3.0** - CSS framework (CDN)
- **Bootstrap Icons** - Icon library (CDN)

## Development

### Running in Development Mode
The app runs in debug mode by default, enabling:
- Auto-reload on code changes
- Detailed error messages
- Flask development server

### Database Management
- Database file: `todos.db` (SQLite)
- Automatic schema creation/migration
- Foreign key constraints enabled
- Cascade deletion for nested tasks

## Security Notes

For production deployment:
- Change the Flask secret key in `app.py`
- Use environment variables for configuration
- Consider adding HTTPS
- Implement rate limiting
- Add input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:
1. Check the browser console for JavaScript errors
2. Verify Python dependencies are installed correctly
3. Ensure you're using a supported browser version
4. Create an issue with detailed reproduction steps

---

**Built with ❤️ using Flask, SQLite, and Bootstrap**