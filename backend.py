"""
Backend module for School Library Management System.
Handles data persistence, automated date/fine calculations, inventory, and circulation.
"""

from datetime import datetime, timedelta, date

# Sample initial books inventory with shelf locations
books = [
    {"id": 1, "title": "Introduction to Computer Science", "author": "J. Glenn Brookshear", "category": "Technology", "shelf": "Shelf A-1", "copies": 5},
    {"id": 2, "title": "Python Programming", "author": "John Zelle", "category": "Programming", "shelf": "Shelf A-2", "copies": 4},
    {"id": 3, "title": "Data Structures and Algorithms", "author": "Michael Goodrich", "category": "Technology", "shelf": "Shelf A-3", "copies": 3},
    {"id": 4, "title": "Philippine History", "author": "Teodoro Agoncillo", "category": "History", "shelf": "Shelf B-1", "copies": 6},
    {"id": 5, "title": "Principles of Economics", "author": "N. Gregory Mankiw", "category": "Business", "shelf": "Shelf B-2", "copies": 4},
    {"id": 6, "title": "General Chemistry", "author": "John McMurry", "category": "Science", "shelf": "Shelf C-1", "copies": 3},
    {"id": 7, "title": "Basic Agriculture", "author": "L. Sanchez", "category": "Agriculture", "shelf": "Shelf C-2", "copies": 5},
    {"id": 8, "title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Literature", "shelf": "Shelf D-1", "copies": 2}
]

# Users list (includes admin and registered students)
users = [
    {
        "username": "admin",
        "password": "123",
        "name": "Head Librarian",
        "role": "librarian",
        "email": "librarian@school.edu",
        "course": "Faculty / Staff",
        "contact": "09112223333"
    },
    {
        "username": "2024-001",
        "password": "123",
        "name": "Juan Dela Cruz",
        "role": "student",
        "email": "juan.delacruz@school.edu",
        "course": "BS Information Technology 3",
        "contact": "09187654321"
    }
]

borrow_records = []
reservations = []

# Loan constants
FINE_RATE = 10.0   # 10 pesos fine per day overdue
BORROW_DAYS = 7    # 7 days standard loan period
MAX_BORROW_LIMIT = 3


# ================= USER / AUTH LOGIC =================

def authenticate_user(username, password):
    """Authenticate user with username and password."""
    for u in users:
        if u["username"].lower() == username.strip().lower() and u["password"] == password.strip():
            return u
    return None


def register_student(name, student_id, password, email, course, contact):
    """Register a new student account."""
    name = name.strip()
    student_id = student_id.strip()
    password = password.strip()
    email = email.strip()
    course = course.strip()
    contact = contact.strip()

    if not name or not student_id or not password:
        return False, "Name, Student ID, and Password are required!"

    for u in users:
        if u["username"].lower() == student_id.lower():
            return False, "Student ID already registered!"

    users.append({
        "username": student_id,
        "password": password,
        "name": name,
        "role": "student",
        "email": email if email else f"{student_id.lower()}@school.edu",
        "course": course if course else "Student",
        "contact": contact
    })
    return True, f"Registration successful!\nYou can now log in using Student ID '{student_id}'."


def get_all_students():
    """Retrieve all registered student records."""
    return [u for u in users if u.get("role") == "student"]


def find_user_by_username(username):
    """Find user dictionary by username."""
    return next((u for u in users if u["username"].lower() == username.strip().lower()), None)


# ================= BOOK & INVENTORY LOGIC =================

def get_all_books():
    """Return all books."""
    return books


def find_book_by_id(book_id):
    """Find a book by its unique ID."""
    return next((b for b in books if b["id"] == int(book_id)), None)


def search_books(query):
    """Filter books by title, author, or category."""
    q = query.strip().lower()
    if not q:
        return books
    return [
        b for b in books
        if q in b["title"].lower() or q in b["author"].lower() or q in b["category"].lower() or q in b.get("shelf", "").lower()
    ]


def restock_book(book_id, count):
    """Add stock to an existing book."""
    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    book["copies"] += count
    return True, f"Successfully updated copies to {book['copies']}!"


def add_book(title, author, category, shelf, copies):
    """Add a new book acquisition with shelf location to the inventory."""
    title = title.strip()
    if not title:
        return False, "Title cannot be empty."

    new_id = len(books) + 1
    new_book = {
        "id": new_id,
        "title": title,
        "author": author.strip() if author.strip() else "Unknown",
        "category": category.strip() if category.strip() else "General",
        "shelf": shelf.strip() if shelf.strip() else "Main Shelf",
        "copies": max(0, copies)
    }
    books.append(new_book)
    return True, f"'{title}' added successfully to inventory ({new_book['shelf']})!"


def delete_book(book_id):
    """Delete a book from inventory."""
    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    books.remove(book)
    return True, "Book removed from inventory."


# ================= AUTOMATED FINE & DATE CALCULATIONS =================

def calculate_overdue_fine(record):
    """
    Automated Fine Calculation:
    Compares the due date with the current system date.
    Returns: (overdue_days, fine_amount, is_overdue)
    """
    if record["status"] == "Returned":
        return 0, record.get("fine", 0.0), False

    today = date.today()
    due_d = datetime.strptime(record["due_date"], "%Y-%m-%d").date()

    if today > due_d:
        overdue_days = (today - due_d).days
        fine = overdue_days * FINE_RATE
        return overdue_days, fine, True
    return 0, 0.0, False


# ================= BORROW & CIRCULATION LOGIC =================

def borrow_book(user, book_id):
    """Process a book borrow for a student with automated due date."""
    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book["copies"] <= 0:
        return False, "Out of Stock: Sorry, this book has 0 copies available on the shelf.\nYou can reserve it instead."

    active_loans = [
        r for r in borrow_records
        if r["username"] == user["username"] and r["status"] == "Borrowed"
    ]
    if len(active_loans) >= MAX_BORROW_LIMIT:
        return False, f"Borrow Limit: You have reached the maximum borrow limit of {MAX_BORROW_LIMIT} books."

    book["copies"] -= 1

    borrow_d = date.today()
    due_d = borrow_d + timedelta(days=BORROW_DAYS)

    record = {
        "record_id": len(borrow_records) + 1,
        "username": user["username"],
        "name": user["name"],
        "course": user.get("course", "Student"),
        "book_id": book["id"],
        "book_title": book["title"],
        "borrow_date": borrow_d.strftime("%Y-%m-%d"),
        "due_date": due_d.strftime("%Y-%m-%d"),
        "return_date": None,
        "status": "Borrowed",
        "fine": 0.0
    }
    borrow_records.append(record)
    return True, f"'{book['title']}' borrowed successfully!\nDue date is {due_d.strftime('%b %d, %Y')} ({BORROW_DAYS} days loan)."


def issue_book_to_student(student_id, book_id):
    """Librarian feature: Issue book directly to any registered student."""
    student = find_user_by_username(student_id)
    if not student:
        return False, f"Student with ID '{student_id}' not found."
    return borrow_book(student, book_id)


def reserve_book(user, book_id):
    """Process a book hold/reservation directly from the catalog."""
    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    res = {
        "id": len(reservations) + 1,
        "username": user["username"],
        "name": user["name"],
        "book_id": book["id"],
        "book_title": book["title"],
        "date_requested": date.today().strftime("%Y-%m-%d"),
        "status": "Pending"
    }
    reservations.append(res)
    return True, f"Reservation for '{book['title']}' submitted successfully!"


def return_borrowed_book(record_id):
    """
    Process book return with fully automated fine calculation based on system date.
    Returns: (success, message, fine, is_overdue)
    """
    record = next((r for r in borrow_records if r["record_id"] == int(record_id)), None)
    if not record:
        return False, "Record not found.", 0.0, False

    if record["status"] == "Returned":
        return False, "This book has already been returned.", record.get("fine", 0.0), False

    overdue_days, fine, is_overdue = calculate_overdue_fine(record)

    record["status"] = "Returned"
    record["return_date"] = date.today().strftime("%Y-%m-%d")
    record["fine"] = fine

    # Restock copy back into library shelf
    book = find_book_by_id(record["book_id"])
    if book:
        book["copies"] += 1

    if is_overdue:
        msg = f"Book returned overdue by {overdue_days} day(s).\nOverdue penalty fee: {overdue_days} days x P{FINE_RATE:.2f} = P{fine:.2f}"
    else:
        msg = "Book returned on time! No overdue penalty."

    return True, msg, fine, is_overdue


def get_user_borrow_records(username):
    """Retrieve borrow records for a specific user, with updated fine calculations."""
    user_recs = [r for r in borrow_records if r["username"] == username]
    for r in user_recs:
        if r["status"] == "Borrowed":
            _, live_fine, _ = calculate_overdue_fine(r)
            r["fine"] = live_fine
    return user_recs


def get_all_borrow_records():
    """Retrieve all borrow records with live automated fines."""
    for r in borrow_records:
        if r["status"] == "Borrowed":
            _, live_fine, _ = calculate_overdue_fine(r)
            r["fine"] = live_fine
    return borrow_records


def get_all_reservations():
    """Retrieve all book reservations."""
    return reservations


# ================= LIBRARIAN ANALYTICS & DASHBOARD METRICS =================

def get_analytics_metrics():
    """
    Calculate summary metrics for librarian dashboard metric cards:
    - Total catalog titles
    - Active borrowed books
    - Overdue books
    - Pending reservations
    """
    total_titles = len(books)
    active_borrowed = sum(1 for r in borrow_records if r["status"] == "Borrowed")
    
    today = date.today()
    overdue_books = 0
    for r in borrow_records:
        if r["status"] == "Borrowed":
            due_d = datetime.strptime(record_due := r["due_date"], "%Y-%m-%d").date()
            if today > due_d:
                overdue_books += 1

    pending_reservations = sum(1 for res in reservations if res["status"] == "Pending")

    return {
        "total_titles": total_titles,
        "active_borrowed": active_borrowed,
        "overdue_books": overdue_books,
        "pending_reservations": pending_reservations
    }
