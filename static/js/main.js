document.addEventListener('DOMContentLoaded', () => {
    const bookSearchInput = document.getElementById('book-search-input');
    const categoryFilter = document.getElementById('category-filter');
    const bookCards = document.querySelectorAll('.book-card');

    function filterBooks() {
        const query = (bookSearchInput ? bookSearchInput.value.toLowerCase().trim() : '');
        const selectedCat = (categoryFilter ? categoryFilter.value.toLowerCase().trim() : 'all');

        bookCards.forEach(card => {
            const title = (card.getAttribute('data-title') || '').toLowerCase();
            const author = (card.getAttribute('data-author') || '').toLowerCase();
            const isbn = (card.getAttribute('data-isbn') || '').toLowerCase();
            const category = (card.getAttribute('data-category') || '').toLowerCase();

            const matchesQuery = !query || title.includes(query) || author.includes(query) || isbn.includes(query);
            const matchesCategory = selectedCat === 'all' || category === selectedCat;

            if (matchesQuery && matchesCategory) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }

    if (bookSearchInput) {
        bookSearchInput.addEventListener('input', filterBooks);
    }
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterBooks);
    }

    const tableSearchInput = document.getElementById('table-search-input');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('input', () => {
            const query = tableSearchInput.value.toLowerCase().trim();
            const rows = document.querySelectorAll('.data-table tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    document.querySelectorAll('.modal-backdrop').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    const roleBtns = document.querySelectorAll('.role-btn');
    const roleInput = document.getElementById('login-role-input');
    const idLabel = document.getElementById('login-id-label');
    const idInput = document.getElementById('login-id-input');

    if (roleBtns.length && roleInput) {
        roleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                roleBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const role = btn.getAttribute('data-role');
                roleInput.value = role;

                if (idLabel && idInput) {
                    if (role === 'librarian') {
                        idLabel.textContent = 'Librarian ID or Email';
                        idInput.placeholder = 'e.g. LIB-001 or librarian@university.edu';
                    } else {
                        idLabel.textContent = 'Student ID or Email';
                        idInput.placeholder = 'e.g. STU-2026-001 or alex@student.edu';
                    }
                }
            });
        });
    }

    window.openEditBookModal = function(book) {
        document.getElementById('edit-book-id').value = book.id;
        document.getElementById('edit-title').value = book.title;
        document.getElementById('edit-author').value = book.author;
        document.getElementById('edit-isbn').value = book.isbn;
        document.getElementById('edit-category').value = book.category_id;
        document.getElementById('edit-copies').value = book.total_copies;
        document.getElementById('edit-shelf').value = book.shelf_location;
        document.getElementById('edit-description').value = book.description || '';
        openModal('modal-edit-book');
    };

    window.openIssueModalForBook = function(bookId, bookTitle) {
        const bookSelect = document.getElementById('issue-book-select');
        if (bookSelect) {
            bookSelect.value = bookId;
        }
        openModal('modal-issue-book');
    };

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
