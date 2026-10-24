# 📚 University Library Management System (LMS)
**1st-Year College Capstone Project**  
*Built with Plain Python (`http.server`), MySQL (XAMPP), HTML5, and Vanilla CSS.*

---

## 🌟 Overview & Key Features

This project is a complete, role-based Library Management System designed specifically for college academic evaluation. It uses **pure Python** (no Flask or Django) so you can explain every line of code during your defense.

### 👥 2 Distinct User Portals:
1. **Librarian / Staff Portal (`LIB-001`)**:
   - **Circulation Desk**: Issue books, record checkout dates, and set loan durations.
   - **One-Click Returns**: Automatically calculates overdue fines (₱10.00 / day late).
   - **Book Inventory Management (CRUD)**: Add new titles, edit details, track shelf codes, and monitor total vs. available copies.
   - **Reservation Queue**: Review and approve book hold requests submitted by students.
   - **Student Directory**: Monitor registered students, contact numbers, and borrowing records.
   - **Analytics Dashboard**: Live KPI counters for total books, active loans, overdue alerts, and pending holds.

2. **Student Member Portal (`STU-2026-001`)**:
   - **Online Public Access Catalog (OPAC)**: Live instant search by title, author, or ISBN, plus category filtering.
   - **Hold Reservations**: 1-click book reservation for pickup at the circulation desk.
   - **Personal Dashboard ("My Loans")**: View active borrowed books with live due-date countdowns and penalty warnings.
   - **Self-Registration**: New students can register accounts directly.

---

## 🚀 Quick Start Guide

### Step 1: Start XAMPP
1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **MySQL** (and Apache if you use phpMyAdmin).

### Step 2: Install Python MySQL Driver (One-time)
Open your Command Prompt or PowerShell and install the lightweight MySQL driver:
```bash
pip install pymysql
```

### Step 3: Database Setup
You have two easy options:
- **Option A (Automatic)**: The Python server automatically detects and imports `database/schema.sql` into XAMPP MySQL when you run it!
- **Option B (Manual via phpMyAdmin)**:
  1. Go to `http://localhost/phpmyadmin`.
  2. Click **Import** at the top.
  3. Choose the file `database/schema.sql` and click **Import**.

### Step 4: Run the Server
In your terminal, navigate to the project directory and run:
```bash
python server.py
```
Open your web browser and visit: **`http://localhost:8080`**

---

## 🔑 Demo Login Accounts

| Role | Identifier (ID or Email) | Password | Description |
| :--- | :--- | :--- | :--- |
| **Librarian** | `librarian@university.edu` or `LIB-001` | `password123` | Head Librarian access to circulation & inventory |
| **Student #1** | `alex.rivera@student.edu` or `STU-2026-001` | `password123` | Active student with 1 borrowed book & 1 reservation |
| **Student #2** | `samantha.cruz@student.edu` or `STU-2026-002` | `password123` | Student with 1 overdue book (demonstrates fine penalty) |

*(New students can also register their own accounts from the login page!)*

---

## 📁 Project File Structure

```text
library_management_system/
├── server.py              # Main Python backend (Plain Python http.server & routing)
├── README.md              # Documentation and defense guide
├── database/
│   ├── db.py              # Database queries, fine calculation, connection layer
│   └── schema.sql         # Database schema & sample seed data for XAMPP
├── static/
│   ├── css/
│   │   └── style.css      # Custom Vanilla CSS design system (Midnight glassmorphism)
│   └── js/
│       └── main.js        # Live search, modal popups, and UI interactions
└── templates/
    ├── login.html                 # Unified login with role switcher
    ├── register.html              # Student registration form
    ├── librarian_dashboard.html   # Librarian analytics & recent transactions
    ├── librarian_books.html       # Book inventory CRUD with Add/Edit modals
    ├── librarian_circulation.html # Issue books, returns, and reservations
    ├── librarian_students.html    # Student directory
    ├── student_dashboard.html     # Student loans, countdowns, and fines
    └── student_catalog.html       # Online book search and reservation modal
```

---

## 🎓 Oral Defense FAQ (Common Panel Questions)

**Q1: Why didn't you use Flask or Django?**  
*Answer:* "As a 1st-year student, I wanted to understand the core computer science fundamentals of web development. Instead of using complex third-party frameworks with hidden magic, I built our backend using Python's built-in `http.server`. This demonstrated request routing (GET/POST), HTTP status codes, cookies/sessions, and database connectivity from the ground up."

**Q2: How does the system calculate overdue fines?**  
*Answer:* "When active borrow records are retrieved, the Python backend compares `CURDATE()` with the record's `due_date`. For every day the return is overdue, it calculates `days_overdue * ₱10.00` and automatically updates the status to 'overdue'."

**Q3: How is data integrity maintained in MySQL?**  
*Answer:* "We use Foreign Keys (`fk_borrow_user`, `fk_borrow_book`, `fk_books_category`) and prevent deleting books that are currently loaned out. When a book is issued, the available copies count automatically decrements by 1; when returned, it increments by 1."
