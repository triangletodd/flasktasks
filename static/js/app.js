// Custom JavaScript for the todo list app

document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Handle inline editing of todos
    const editButtons = document.querySelectorAll('.edit-btn');
    const cancelButtons = document.querySelectorAll('.cancel-edit');

    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const todoItem = this.closest('.todo-item');
            const todoTextContainer = todoItem.querySelector('.todo-text-container');
            const editForm = todoItem.querySelector('.edit-form');
            const editInput = editForm.querySelector('input[name="task"]');
            
            // Hide text container, show form
            todoTextContainer.style.display = 'none';
            editForm.style.display = 'block';
            editInput.focus();
            editInput.select();
        });
    });

    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const todoItem = this.closest('.todo-item');
            const todoTextContainer = todoItem.querySelector('.todo-text-container');
            const editForm = todoItem.querySelector('.edit-form');
            
            // Show text container, hide form
            todoTextContainer.style.display = 'flex';
            editForm.style.display = 'none';
        });
    });

    // Handle adding subtasks
    const addSubtaskButtons = document.querySelectorAll('.add-subtask-btn');
    const subtaskForm = document.getElementById('subtask-form');
    const subtaskInput = subtaskForm.querySelector('input[name="task"]');
    const subtaskParentId = document.getElementById('subtask-parent-id');
    const cancelSubtaskButton = document.getElementById('cancel-subtask');

    addSubtaskButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const parentId = this.getAttribute('data-parent-id');
            const todoItem = this.closest('.todo-item');
            
            // Set parent ID and position the form after this todo
            subtaskParentId.value = parentId;
            subtaskForm.classList.remove('d-none');
            
            // Insert the form after the parent todo
            todoItem.parentNode.insertBefore(subtaskForm, todoItem.nextSibling);
            
            subtaskInput.focus();
        });
    });

    cancelSubtaskButton.addEventListener('click', function(e) {
        e.preventDefault();
        subtaskForm.classList.add('d-none');
        subtaskInput.value = '';
    });

    // Handle escape key to cancel editing or subtask form
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeEditForm = document.querySelector('.edit-form[style*="block"]');
            if (activeEditForm) {
                const todoItem = activeEditForm.closest('.todo-item');
                const todoTextContainer = todoItem.querySelector('.todo-text-container');
                
                todoTextContainer.style.display = 'flex';
                activeEditForm.style.display = 'none';
            }
            
            // Also cancel subtask form
            if (!subtaskForm.classList.contains('d-none')) {
                subtaskForm.classList.add('d-none');
                subtaskInput.value = '';
            }
        }
    });

    // Auto-focus on the add todo input
    const addTodoInput = document.querySelector('input[name="task"]');
    if (addTodoInput && !document.querySelector('.edit-form[style*="block"]')) {
        addTodoInput.focus();
    }

    // Add keyboard shortcut (Ctrl/Cmd + Enter) to submit new todo
    const todoForm = document.querySelector('form[action*="/add"]');
    if (todoForm) {
        todoForm.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.submit();
            }
        });
    }

    // Handle collapse/expand functionality
    const collapseToggles = document.querySelectorAll('.collapse-toggle');
    
    collapseToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const parentId = this.getAttribute('data-parent-id');
            const childTodos = document.querySelectorAll(`[data-parent-id="${parentId}"]`);
            const isCurrentlyExpanded = this.classList.contains('expanded');
            console.log(`Toggle clicked for parent ${parentId}, currently expanded: ${isCurrentlyExpanded}`);
            
            const icon = this.querySelector('.collapse-icon');
            
            if (isCurrentlyExpanded) {
                // Collapse
                this.classList.remove('expanded');
                icon.className = 'bi bi-chevron-right collapse-icon';
                childTodos.forEach(child => {
                    child.classList.add('collapsed');
                });
                saveCollapseState(parentId, true);
                console.log(`Collapsed parent ${parentId}`);
            } else {
                // Expand
                this.classList.add('expanded');
                icon.className = 'bi bi-chevron-down collapse-icon';
                childTodos.forEach(child => {
                    child.classList.remove('collapsed');
                });
                saveCollapseState(parentId, false);
                console.log(`Expanded parent ${parentId}, classes:`, this.classList.toString());
            }
        });
    });
    
    // Initialize collapse states - start with all collapsed by default
    function initializeCollapseStates() {
        console.log(`Initializing ${collapseToggles.length} collapse toggles`);
        collapseToggles.forEach(toggle => {
            const parentId = toggle.getAttribute('data-parent-id');
            const savedState = getCollapseState(parentId);
            const shouldBeCollapsed = savedState !== null ? savedState : true; // Default to collapsed
            console.log(`Parent ${parentId}: savedState=${savedState}, shouldBeCollapsed=${shouldBeCollapsed}`);
            
            const icon = toggle.querySelector('.collapse-icon');
            const childTodos = document.querySelectorAll(`[data-parent-id="${parentId}"]`);
            
            if (shouldBeCollapsed) {
                // Collapsed: no 'expanded' class, right arrow, children get 'collapsed' class
                toggle.classList.remove('expanded');
                icon.className = 'bi bi-chevron-right collapse-icon';
                childTodos.forEach(child => {
                    child.classList.add('collapsed');
                });
                console.log(`Set parent ${parentId} to collapsed`);
            } else {
                // Expanded: add 'expanded' class, down arrow, children lose 'collapsed' class
                toggle.classList.add('expanded');
                icon.className = 'bi bi-chevron-down collapse-icon';
                childTodos.forEach(child => {
                    child.classList.remove('collapsed');
                });
                console.log(`Set parent ${parentId} to expanded, classes:`, toggle.classList.toString());
            }
        });
    }
    
    // Save collapse state to localStorage
    function saveCollapseState(parentId, isCollapsed) {
        const collapseStates = JSON.parse(localStorage.getItem('todoCollapseStates') || '{}');
        collapseStates[parentId] = isCollapsed;
        localStorage.setItem('todoCollapseStates', JSON.stringify(collapseStates));
    }
    
    // Get collapse state from localStorage
    function getCollapseState(parentId) {
        const collapseStates = JSON.parse(localStorage.getItem('todoCollapseStates') || '{}');
        return collapseStates[parentId];
    }
    
    // Initialize collapse states
    initializeCollapseStates();

    console.log('Todo List App initialized successfully!');
});