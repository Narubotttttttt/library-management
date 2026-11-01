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

# Users list (includes admin, registered students, and faculty members)
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
        "username": "teacher",
        "password": "123",
        "name": "Kay Rejoice Waga",
        "role": "teacher",
        "email": "kaywaga@school.edu",
        "course": "Faculty - BSIT",
        "department": "College of Information Technology",
        "contact": "09171112233"
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

# Faculty & Student Loan Policies
FINE_RATE = 10.0            # 10 pesos fine per day overdue for students
BORROW_DAYS = 7             # 7 days standard student loan period
MAX_BORROW_LIMIT = 3        # Maximum 3 books for students

TEACHER_BORROW_DAYS = 14     # 14 days extended faculty loan period
TEACHER_MAX_LIMIT = 5        # Maximum 5 books for faculty
TEACHER_FINE_RATE = 0.0      # Faculty members are exempt from overdue fines

# Faculty Course Reading List Recommendations
recommendations = []

# Faculty Book Purchase / Acquisition Requests
acquisitions = []


# ================= USER / AUTH LOGIC =================

def authenticate_user(username, password):
    """Authenticate user with username and password."""
    for u in users:
        if u["username"].lower() == username.strip().lower() and u["password"] == password.strip():
            return u
    return None


def register_user(name, username, password, email, course, contact, role="student"):
    """Register a new student or teacher account."""
    name = name.strip()
    username = username.strip()
    password = password.strip()
    email = email.strip()
    course = course.strip()
    contact = contact.strip()
    role = role.strip().lower() if role in ("student", "teacher") else "student"

    if not name or not username or not password:
        id_label = "Faculty / Employee ID" if role == "teacher" else "Student ID"
        return False, f"Name, {id_label}, and Password are required!"

    for u in users:
        if u["username"].lower() == username.lower():
            id_label = "Faculty ID" if role == "teacher" else "Student ID"
            return False, f"{id_label} '{username}' is already registered!"

    default_dept = "College Faculty" if role == "teacher" else "Student"
    users.append({
        "username": username,
        "password": password,
        "name": name,
        "role": role,
        "email": email if email else f"{username.lower()}@school.edu",
        "course": course if course else default_dept,
        "department": course if role == "teacher" else "",
        "contact": contact
    })
    role_label = "Faculty Member" if role == "teacher" else "Student"
    return True, f"Registration successful!\nYou can now log in as {role_label} using ID '{username}'."


def register_student(name, student_id, password, email, course, contact, role="student"):
    """Alias for register_user to maintain backward compatibility."""
    return register_user(name, student_id, password, email, course, contact, role)


def get_all_students():
    """Retrieve all registered student records."""
    return [u for u in users if u.get("role") == "student"]


def get_all_faculty():
    """Retrieve all registered faculty records."""
    return [u for u in users if u.get("role") == "teacher"]


def find_user_by_username(username):
    """Find user dictionary by username."""
    return next((u for u in users if u["username"].lower() == username.strip().lower()), None)


# ================= BOOK & INVENTORY LOGIC =================

def _enrich_books_with_meta(book_list):
    """Attach faculty course recommendation tags to books."""
    rec_map = {}
    for r in recommendations:
        rec_map.setdefault(r["book_id"], []).append({
            "id": r["id"],
            "teacher_name": r["teacher_name"],
            "course": r["course"],
            "notes": r["notes"]
        })
    enriched = []
    for b in book_list:
        b_dict = dict(b)
        b_dict["recommendations"] = rec_map.get(b["id"], [])
        b_dict["is_recommended"] = len(b_dict["recommendations"]) > 0
        enriched.append(b_dict)
    return enriched


def get_all_books():
    """Return all books with faculty recommendation metadata."""
    return _enrich_books_with_meta(books)


def find_book_by_id(book_id):
    """Find a book by its unique ID."""
    return next((b for b in books if b["id"] == int(book_id)), None)


def search_books(query):
    """Filter books by title, author, or category with recommendations."""
    q = query.strip().lower()
    if not q:
        return _enrich_books_with_meta(books)
    matched = [
        b for b in books
        if q in b["title"].lower() or q in b["author"].lower() or q in b["category"].lower() or q in b.get("shelf", "").lower()
    ]
    return _enrich_books_with_meta(matched)


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
    Faculty/teachers are exempt from overdue fines.
    """
    if record["status"] != "Borrowed" or not record.get("due_date"):
        return 0, record.get("fine", 0.0), False

    if record.get("role") == "teacher":
        return 0, 0.0, False

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
    Borrow Request Workflow:
    Submits a borrow request to the Librarian for approval.
    Stock copy is not deducted until the Librarian approves it.
    Supports both student (max 3, 7 days) and faculty (max 5, 14 days) policies.
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

    is_teacher = user.get("role") == "teacher"
    max_limit = TEACHER_MAX_LIMIT if is_teacher else MAX_BORROW_LIMIT

    active_or_pending = [
        r for r in borrow_records
        if r["username"] == user["username"] and r["status"] in ("Borrowed", "Pending Approval")
    ]
    if len(active_or_pending) >= max_limit:
        role_label = "Faculty" if is_teacher else "Student"
        return False, f"Borrow Limit Reached: You have {len(active_or_pending)} active/pending loan(s). Maximum allowed for {role_label} is {max_limit}."

    record = {
        "record_id": len(borrow_records) + 1,
        "username": user["username"],
        "name": user["name"],
        "role": user.get("role", "student"),
        "course": user.get("department") or user.get("course", "Student"),
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
    """Alias for student/faculty request_borrow_book."""
    return request_borrow_book(user, book_id)


def approve_borrow_request(record_id):
    """
    Librarian Workflow:
    Approves a student or faculty borrow request, deducts stock copy, and initiates loan.
    Sets 14 days for faculty, 7 days for students.
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
    is_teacher = record.get("role") == "teacher"
    loan_days = TEACHER_BORROW_DAYS if is_teacher else BORROW_DAYS
    due_d = borrow_d + timedelta(days=loan_days)

    record["borrow_date"] = borrow_d.strftime("%Y-%m-%d")
    record["due_date"] = due_d.strftime("%Y-%m-%d")
    record["status"] = "Borrowed"

    term_note = f"{loan_days}-day faculty loan" if is_teacher else "7-day standard loan"
    return True, f"Approved! '{record['book_title']}' has been officially issued to {record['name']} ({term_note}).\nReturn deadline is {due_d.strftime('%b %d, %Y')}."


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


def issue_book_to_student(user_id, book_id):
    """Librarian feature: Issue book directly to walk-in student or faculty immediately at the desk."""
    target_user = find_user_by_username(user_id)
    if not target_user:
        return False, f"User with ID '{user_id}' not found."

    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    if book["copies"] <= 0:
        return False, f"Out of Stock: '{book['title']}' has 0 copies available."

    is_teacher = target_user.get("role") == "teacher"
    max_limit = TEACHER_MAX_LIMIT if is_teacher else MAX_BORROW_LIMIT
    loan_days = TEACHER_BORROW_DAYS if is_teacher else BORROW_DAYS

    active_loans = [
        r for r in borrow_records
        if r["username"] == target_user["username"] and r["status"] == "Borrowed"
    ]
    if len(active_loans) >= max_limit:
        role_label = "Faculty" if is_teacher else "Student"
        return False, f"Borrow limit reached: {target_user['name']} has {len(active_loans)} active borrowed books (max {max_limit})."

    book["copies"] -= 1
    borrow_d = date.today()
    due_d = borrow_d + timedelta(days=loan_days)

    record = {
        "record_id": len(borrow_records) + 1,
        "username": target_user["username"],
        "name": target_user["name"],
        "role": target_user.get("role", "student"),
        "course": target_user.get("department") or target_user.get("course", "Member"),
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
    term_note = f"{loan_days}-day faculty loan" if is_teacher else f"{loan_days}-day standard loan"
    return True, f"'{book['title']}' successfully issued to {target_user['name']} ({term_note}).\nDue date: {due_d.strftime('%b %d, %Y')}."


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


# ================= COURSE READING LISTS & RECOMMENDATIONS =================

def get_all_recommendations():
    """Retrieve all teacher recommended reading entries."""
    return recommendations


def get_teacher_recommendations(username):
    """Retrieve recommendations created by a specific teacher."""
    return [r for r in recommendations if r.get("teacher_username") == username]


def recommend_book(user, book_id, course, notes):
    """Teacher feature: Recommend a book for a syllabus / class reading list."""
    book = find_book_by_id(book_id)
    if not book:
        return False, "Book not found in catalog."

    existing = next((r for r in recommendations if r["book_id"] == book["id"] and r["teacher_username"] == user["username"]), None)
    if existing:
        existing["course"] = course.strip() if course else "Course Reading List"
        existing["notes"] = notes.strip()
        existing["date_added"] = date.today().strftime("%Y-%m-%d")
        return True, f"Updated course recommendation for '{book['title']}'!"

    rec = {
        "id": len(recommendations) + 1,
        "book_id": book["id"],
        "book_title": book["title"],
        "teacher_username": user["username"],
        "teacher_name": user["name"],
        "course": course.strip() if course else "Course Reading List",
        "notes": notes.strip(),
        "date_added": date.today().strftime("%Y-%m-%d")
    }
    recommendations.append(rec)
    return True, f"'{book['title']}' successfully added to Course Recommendations!"


def remove_recommendation(rec_id, teacher_username=None):
    """Remove a book from recommendations."""
    global recommendations
    rec = next((r for r in recommendations if r["id"] == int(rec_id)), None)
    if not rec:
        return False, "Recommendation record not found."
    if teacher_username and rec["teacher_username"] != teacher_username:
        return False, "Permission denied: You can only remove your own recommendations."
    recommendations = [r for r in recommendations if r["id"] != int(rec_id)]
    return True, f"Recommendation for '{rec['book_title']}' removed."


# ================= BOOK ACQUISITIONS (TEACHER PURCHASE REQUESTS) =================

def request_book_acquisition(user, title, author, category, reason):
    """Teacher feature: Request a new book purchase/acquisition for the library."""
    title = title.strip()
    author = author.strip()
    if not title or not author:
        return False, "Title and Author are required."

    acq = {
        "id": len(acquisitions) + 1,
        "teacher_username": user["username"],
        "teacher_name": user["name"],
        "department": user.get("department") or user.get("course") or "College Faculty",
        "title": title,
        "author": author,
        "category": category.strip() if category else "General",
        "reason": reason.strip() if reason else "Faculty curriculum recommendation",
        "request_date": date.today().strftime("%Y-%m-%d"),
        "status": "Pending Review"
    }
    acquisitions.append(acq)
    return True, f"Acquisition request for '{title}' submitted to Librarian for review!"


def get_all_acquisitions(teacher_username=None):
    """Retrieve book acquisition requests."""
    if teacher_username:
        return [a for a in acquisitions if a.get("teacher_username") == teacher_username]
    return acquisitions


def approve_acquisition_request(acq_id, shelf="Shelf A-1", copies=3):
    """Librarian feature: Approve acquisition and directly add book to catalog inventory."""
    try:
        aid = int(acq_id)
    except (ValueError, TypeError):
        return False, "Invalid acquisition request ID."

    acq = next((a for a in acquisitions if a["id"] == aid), None)
    if not acq:
        return False, "Acquisition request not found."
    if acq["status"] != "Pending Review":
        return False, f"Cannot approve: Request is already marked as '{acq['status']}'."

    new_book_id = len(books) + 1
    new_book = {
        "id": new_book_id,
        "title": acq["title"],
        "author": acq["author"],
        "category": acq["category"],
        "shelf": shelf.strip() if shelf else "Shelf A-1",
        "copies": max(1, int(copies)) if copies else 3
    }
    books.append(new_book)
    acq["status"] = "Approved & Added"
    return True, f"Acquisition approved! '{acq['title']}' officially added to inventory with {new_book['copies']} copies on {new_book['shelf']}."


def reject_acquisition_request(acq_id, reason="Budget / policy constraints"):
    """Librarian feature: Decline an acquisition request."""
    try:
        aid = int(acq_id)
    except (ValueError, TypeError):
        return False, "Invalid acquisition request ID."

    acq = next((a for a in acquisitions if a["id"] == aid), None)
    if not acq:
        return False, "Acquisition request not found."
    if acq["status"] != "Pending Review":
        return False, f"Cannot reject: Request is already marked as '{acq['status']}'."

    acq["status"] = "Declined"
    return True, f"Acquisition request for '{acq['title']}' declined."


# ================= LIBRARIAN ANALYTICS & DASHBOARD METRICS =================

def get_analytics_metrics():
    """
    Calculate summary metrics for librarian dashboard metric cards:
    - Total catalog titles
    - Active borrowed books
    - Pending borrow requests
    - Overdue books
    - Pending reservations
    - Pending faculty acquisitions
    """
    total_titles = len(books)
    active_borrowed = sum(1 for r in borrow_records if r["status"] == "Borrowed")
    pending_requests = sum(1 for r in borrow_records if r["status"] == "Pending Approval")
    pending_acquisitions = sum(1 for a in acquisitions if a["status"] == "Pending Review")
    total_faculty = sum(1 for u in users if u.get("role") == "teacher")
    total_recommendations = len(recommendations)
    
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
        "pending_reservations": pending_reservations,
        "pending_acquisitions": pending_acquisitions,
        "total_faculty": total_faculty,
        "total_recommendations": total_recommendations
    }
