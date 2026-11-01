# School Library Management System

A modern desktop School Library Management System built with **Python** and **HTML/CSS/JavaScript** (powered by `pywebview`). 

This application connects **Students**, **Teachers**, and the **Librarian (Admin)** into one easy-to-use school library system.

---

## The 3 User Roles Explained

The system has 3 different types of users. When you log in, the system automatically detects your role and opens your specific portal:

### 1.  Student
Students use the library to find and borrow books for their studies.
- **Browse the Catalog**: Search books by title, author, category, or shelf location.
- **Request to Borrow**: Send a borrow request to the Librarian for approval.
- **Student Borrowing Rules**:
  - Maximum of **3 books** at a time.
  - Standard loan period of **7 days**.
  - Overdue penalty fee of **₱10.00 per day** if returned late.
- **View Faculty Recommended Books**: See which books are recommended by teachers for their classes.
- **Reserve Books**: Place a hold on books that currently have 0 copies left on the shelf.
- **Return Books**: Return borrowed books directly from their portal.

---

### 2. Teacher / Faculty
Teachers have special academic privileges to help them prepare lessons and recommend reading materials to their classes.
- **Faculty Borrowing Privileges**:
  - Extended loan period of **14 days** (longer time for lesson planning).
  - Higher limit of **5 books** at a time.
  - **Fine Exempt**: Teachers do not pay overdue fines for educational materials.
- **Course Reading Lists**: Teachers can tag any book in the library as "Recommended" for their subjects (e.g., *"Required for BSIT Programming"*).
- **Request New Book Purchases (Acquisitions)**: If the library does not own a book that the teacher needs for their syllabus, the teacher can send an acquisition request to the Librarian.

---

### 3. Librarian (Admin)
The Librarian controls the library desk, manages inventory, and reviews all requests.
- **Dashboard Overview**: View real-time statistics (total book titles, active loans, overdue books, pending requests).
- **Review Borrow Requests**: Approve or reject book borrow requests submitted by students and teachers. Approving a request automatically deducts 1 copy from shelf stock and sets the due date.
- **Manage Book Inventory**: Add new books, restock copies, update shelf locations, or remove books.
- **Review Faculty Acquisitions**: Review book purchase requests submitted by teachers. Approving a request automatically adds the new book directly into the library catalog.
- **Walk-in Desk Issuance**: Issue books immediately to walk-in students or teachers at the physical counter.
- **Accept Returns**: Record returned books and automatically calculate overdue penalties based on the system date.
- **Directories**: View lists of all registered students, faculty members, and book holds.

---

## Comparison of Roles

| Feature / Policy | Student | Teacher / Faculty | Librarian (Admin) |
| :--- | :---: | :---: | :---: |
| **Max Borrow Limit** | 3 books | 5 books | Unlimited (Desk) |
| **Loan Duration** | 7 days | 14 days | Sets Policy |
| **Overdue Fine** | ₱10.00 / day | Exempt (₱0.00) | Collects Fines |
| **Recommend Books to Classes** | ❌ No | ✅ Yes | Views in Catalog |
| **Request New Book Purchases** | ❌ No | ✅ Yes | ✅ Approves & Stocks |
| **Approve / Reject Requests** | ❌ No | ❌ No | ✅ Yes |
| **Add / Delete Books** | ❌ No | ❌ No | ✅ Yes |

---

##  Default Demo Accounts

You can log in immediately using these pre-made accounts, or click the **Register** button on the login screen to create a new Student or Teacher account:

| Role | Username / ID | Password | Portal View |
| :--- | :--- | :--- | :--- |
| **Librarian (Admin)** | `admin` | `123` | Librarian Desk (`admin.html`) |
| **Teacher / Faculty** | `teacher` | `123` | Faculty Portal (`teacher.html`) |
| **Student** | `20264926` | `123` | Student Portal (`student.html`) |

---

## How to Run the Project

### Prerequisites
Make sure you have **Python 3.8 or higher** installed on your computer. You can download it from [python.org](https://www.python.org/).

### Step 1: Clone the Repository
Open your terminal (PowerShell, Command Prompt, or Git Bash) and run:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### Step 2: Install Required Packages
Install the required dependency (`pywebview`) by running:
```bash
pip install -r requirements.txt
```
*(Or install directly using `pip install pywebview`)*

### Step 3: Run the Application
Start the application with:
```bash
python main.py
```
A desktop window will open displaying the login screen.

---

## 📁 Project Structure

```text
library2/
├── backend.py            # Core library logic, user accounts, fines, and borrowing policies
├── main.py               # pywebview desktop launcher and Python-to-JavaScript bridge
├── requirements.txt      # Python dependencies (pywebview)
├── README.md             # Project documentation and guide
└── views/
    ├── styles.css        # Clean stylesheet with responsive sidebar, tables, and cards
    ├── login.html        # Unified login screen & registration modal
    ├── student.html      # Student portal (Catalog, Borrowed Books, Reservations)
    ├── teacher.html      # Faculty portal (Catalog, 14-day Loans, Recommendations, Acquisitions)
    └── admin.html        # Librarian desk (Dashboard, Requests, Inventory, Acquisitions)
```

---

## 🛠️ Built With

- **Python**: Application backend logic, automated fine calculation, user authentication, and desktop window launcher.
- **pywebview**: Lightweight bridge that displays the modern web interface inside a native desktop window.
- **HTML5 & CSS3**: Modern user interface layout featuring responsive sidebars, metric summary cards, status badges, and full-page tables.
- **Vanilla JavaScript**: Front-end controller that handles interactivity and talks directly to Python.

---

## JavaScript Language Role "Please Read"

JavaScript acts as the **interactive bridge** between the user and Python:

1. **Handles User Actions**: Detects when users click buttons (*Borrow*, *Approve*, *Return*, *Search*), type in search bars, or switch pages using the sidebar.
2. **Communicates with Python**: Sends user requests directly to Python backend methods via `window.pywebview.api` and receives results instantly.
3. **Updates the Screen Dynamically**: Draws book rows into tables, opens and closes modal popups, and displays animated alert messages (green/red toasts) without ever reloading the application window.

---



