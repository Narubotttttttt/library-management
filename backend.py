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
        "name": "Alexander Romero",
        "role": "librarian",
        "email": "alexanderromero@gmail.com",
        "contact": "09112223333"
    },
    {
        "username": "20264926",
        "password": "123",
        "name": "Richmond Depanso",
        "role": "student",
        "email": "richmonddepanso1@gmail.com",
        "course": "BSIT1A",
        "contact": "09187654321"
    }
]

borrow_records = []
reservations = []

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
    if record["status"] != "Borrowed" or not record.get("due_date"):
        return 0, record.get("fine", 0.0), False

    today = date.today()
    due_d = datetime.strptime(record["due_date"], "%Y-%m-%d").date()

    if today > due_d:
        overdue_days = (today - due_d).days
        fine = overdue_days * FINE_RATE
        return overdue_days, fine, True
    return 0, 0.0, False


# ================= BORROW & CIRCULATION LOGIC =================

def request_borrow_book(user, book_id):
    """
    Student Workflow:
    Submits a borrow request to the Librarian for approval.
    Stock copy is not deducted until the Librarian approves it.
    """
    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book["copies"] <= 0:
        return False, "Out of Stock: Sorry, this book currently has 0 copies available on the shelf.\nYou can place a reservation hold instead."

    # Prevent duplicate pending requests for the same book
    pending_same = any(
        r for r in borrow_records
        if r["username"] == user["username"] and r["book_id"] == book["id"] and r["status"] == "Pending Approval"
    )
    if pending_same:
        return False, f"You already submitted a request for '{book['title']}'.\nPlease wait for the Librarian to review it."

    active_or_pending = [
        r for r in borrow_records
        if r["username"] == user["username"] and r["status"] in ("Borrowed", "Pending Approval")
    ]
    if len(active_or_pending) >= MAX_BORROW_LIMIT:
        return False, f"Borrow Limit Reached: You have {len(active_or_pending)} active/pending loan(s). Maximum allowed is {MAX_BORROW_LIMIT}."

    record = {
        "record_id": len(borrow_records) + 1,
        "username": user["username"],
        "name": user["name"],
        "course": user.get("course", "Student"),
        "book_id": book["id"],
        "book_title": book["title"],
        "request_date": date.today().strftime("%Y-%m-%d"),
        "borrow_date": None,
        "due_date": None,
        "return_date": None,
        "status": "Pending Approval",
        "fine": 0.0
    }
    borrow_records.append(record)
    return True, f"Borrow request for '{book['title']}' sent to Librarian!\nPlease wait for Librarian approval."


def borrow_book(user, book_id):
    """Alias for student request_borrow_book."""
    return request_borrow_book(user, book_id)


def approve_borrow_request(record_id):
    """
    Librarian Workflow:
    Approves a student's borrow request, deducts stock copy, and initiates the 7-day loan.
    """
    try:
        rid = int(record_id)
    except (ValueError, TypeError):
        return False, "Invalid request record ID."

    record = next((r for r in borrow_records if (r.get("record_id") == rid or r.get("id") == rid)), None)
    if not record:
        return False, f"Request record #{record_id} not found."

    if record["status"] != "Pending Approval":
        return False, f"Cannot approve: This request is already marked as '{record['status']}'."

    book = find_book_by_id(record["book_id"])
    if not book or book["copies"] <= 0:
        return False, f"Cannot approve: '{record['book_title']}' is currently out of stock (0 copies on shelf)."

    book["copies"] -= 1
    borrow_d = date.today()
    due_d = borrow_d + timedelta(days=BORROW_DAYS)

    record["borrow_date"] = borrow_d.strftime("%Y-%m-%d")
    record["due_date"] = due_d.strftime("%Y-%m-%d")
    record["status"] = "Borrowed"

    return True, f"Approved! '{record['book_title']}' has been officially issued to {record['name']}.\nReturn deadline is {due_d.strftime('%b %d, %Y')}."


def reject_borrow_request(record_id):
    """
    Librarian Workflow:
    Rejects a student's borrow request.
    """
    try:
        rid = int(record_id)
    except (ValueError, TypeError):
        return False, "Invalid request record ID."

    record = next((r for r in borrow_records if (r.get("record_id") == rid or r.get("id") == rid)), None)
    if not record:
        return False, f"Request record #{record_id} not found."

    if record["status"] != "Pending Approval":
        return False, f"Cannot reject: This request is already marked as '{record['status']}'."

    record["status"] = "Rejected"
    return True, f"Borrow request #{record_id} for '{record['book_title']}' has been rejected."


def issue_book_to_student(student_id, book_id):
    """Librarian feature: Issue book directly to walk-in student immediately at the desk."""
    student = find_user_by_username(student_id)
    if not student:
        return False, f"Student with ID '{student_id}' not found."

    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book["copies"] <= 0:
        return False, f"Out of Stock: '{book['title']}' has 0 copies available."

    active_loans = [
        r for r in borrow_records
        if r["username"] == student["username"] and r["status"] == "Borrowed"
    ]
    if len(active_loans) >= MAX_BORROW_LIMIT:
        return False, f"Borrow limit reached: Student has {len(active_loans)} active borrowed books."

    book["copies"] -= 1
    borrow_d = date.today()
    due_d = borrow_d + timedelta(days=BORROW_DAYS)

    record = {
        "record_id": len(borrow_records) + 1,
        "username": student["username"],
        "name": student["name"],
        "course": student.get("course", "Student"),
        "book_id": book["id"],
        "book_title": book["title"],
        "request_date": borrow_d.strftime("%Y-%m-%d"),
        "borrow_date": borrow_d.strftime("%Y-%m-%d"),
        "due_date": due_d.strftime("%Y-%m-%d"),
        "return_date": None,
        "status": "Borrowed",
        "fine": 0.0
    }
    borrow_records.append(record)
    return True, f"'{book['title']}' successfully issued to {student['name']}.\nDue date: {due_d.strftime('%b %d, %Y')}."


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
    - Pending borrow requests
    - Overdue books
    - Pending reservations
    """
    total_titles = len(books)
    active_borrowed = sum(1 for r in borrow_records if r["status"] == "Borrowed")
    pending_requests = sum(1 for r in borrow_records if r["status"] == "Pending Approval")
    
    today = date.today()
    overdue_books = 0
    for r in borrow_records:
        if r["status"] == "Borrowed" and r.get("due_date"):
            due_d = datetime.strptime(r["due_date"], "%Y-%m-%d").date()
            if today > due_d:
                overdue_books += 1

    pending_reservations = sum(1 for res in reservations if res["status"] == "Pending")

    return {
        "total_titles": total_titles,
        "active_borrowed": active_borrowed,
        "pending_requests": pending_requests,
        "overdue_books": overdue_books,
        "pending_reservations": pending_reservations
    }
