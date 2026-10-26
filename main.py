import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# sample books
books = [
    {"id": 1, "title": "Introduction to Computer Science", "author": "J. Glenn Brookshear", "category": "Technology", "copies": 5},
    {"id": 2, "title": "Python Programming", "author": "John Zelle", "category": "Programming", "copies": 4},
    {"id": 3, "title": "Data Structures and Algorithms", "author": "Michael Goodrich", "category": "Technology", "copies": 3},
    {"id": 4, "title": "Philippine History", "author": "Teodoro Agoncillo", "category": "History", "copies": 6},
    {"id": 5, "title": "Principles of Economics", "author": "N. Gregory Mankiw", "category": "Business", "copies": 4},
    {"id": 6, "title": "General Chemistry", "author": "John McMurry", "category": "Science", "copies": 3},
    {"id": 7, "title": "Basic Agriculture", "author": "L. Sanchez", "category": "Agriculture", "copies": 5},
    {"id": 8, "title": "To Kill a Mockingbird", "author": "Harper Lee", "category": "Literature", "copies": 2}
]

users = [
    {
        "username": "admin",
        "password": "123",
        "name": "Head Librarian",
        "role": "librarian",
        "course": "Faculty / Staff",
        "contact": "09112223333"
    },

]

borrow_records = []
reservations = []

# 10 pesos fine per day overdue after 7 days
FINE_RATE = 10.0
BORROW_DAYS = 7


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Library Management System")
        self.geometry("780x540")
        self.resizable(False, False)

        self.current_user = None
        self.show_login_screen()

    def clear_frames(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ================= LOGIN SCREEN =================
    def show_login_screen(self):
        self.clear_frames()

        frame = tk.Frame(self, padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title_label = tk.Label(frame, text="School Library Management System", font=("Arial", 16, "bold"), fg="#1a365d")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        sub_label = tk.Label(frame, text="User Login", font=("Arial", 12))
        sub_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))

        tk.Label(frame, text="Student ID / Username:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", pady=5)
        self.username_entry = tk.Entry(frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(frame, text="Password:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(frame, width=25, font=("Arial", 10), show="*")
        self.password_entry.grid(row=3, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

        login_btn = tk.Button(btn_frame, text="Login", width=12, bg="#2b6cb0", fg="white", font=("Arial", 10, "bold"), command=self.handle_login)
        login_btn.pack(side=tk.LEFT, padx=5)

        register_btn = tk.Button(btn_frame, text="Register", width=12, bg="#4a5568", fg="white", font=("Arial", 10), command=self.show_register_dialog)
        register_btn.pack(side=tk.LEFT, padx=5)

        # helpful demo hint
        hint = tk.Label(frame, text="Demo Accounts:\nLibrarian: admin / 123\nStudent: 2024-001 / 123", fg="#718096", font=("Arial", 9))
        hint.grid(row=5, column=0, columnspan=2, pady=(15, 0))

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        for u in users:
            if u["username"].lower() == username.lower() and u["password"] == password:
                self.current_user = u
                messagebox.showinfo("Login Success", f"Welcome back, {u['name']}!")
                if u["role"] == "librarian":
                    self.show_librarian_dashboard()
                else:
                    self.show_student_dashboard()
                return

        messagebox.showerror("Error", "Invalid Student ID/Username or Password.")

    def show_register_dialog(self):
        reg_win = tk.Toplevel(self)
        reg_win.title("Student Registration")
        reg_win.geometry("380x300")
        reg_win.resizable(False, False)

        tk.Label(reg_win, text="Student Registration", font=("Arial", 12, "bold")).pack(pady=10)

        form = tk.Frame(reg_win, padx=15)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Full Name:").grid(row=0, column=0, sticky="w", pady=4)
        name_entry = tk.Entry(form, width=25)
        name_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Student ID:").grid(row=1, column=0, sticky="w", pady=4)
        id_entry = tk.Entry(form, width=25)
        id_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Password:").grid(row=2, column=0, sticky="w", pady=4)
        pass_entry = tk.Entry(form, width=25, show="*")
        pass_entry.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Course & Year:").grid(row=3, column=0, sticky="w", pady=4)
        course_entry = tk.Entry(form, width=25)
        course_entry.grid(row=3, column=1, pady=4)

        tk.Label(form, text="Contact No:").grid(row=4, column=0, sticky="w", pady=4)
        contact_entry = tk.Entry(form, width=25)
        contact_entry.grid(row=4, column=1, pady=4)

        def save_student():
            name = name_entry.get().strip()
            student_id = id_entry.get().strip()
            pwd = pass_entry.get().strip()
            course = course_entry.get().strip()
            contact = contact_entry.get().strip()

            if not name or not student_id or not pwd:
                messagebox.showerror("Error", "Name, Student ID, and Password are required!", parent=reg_win)
                return

            for u in users:
                if u["username"].lower() == student_id.lower():
                    messagebox.showerror("Error", "Student ID already exists!", parent=reg_win)
                    return

            users.append({
                "username": student_id,
                "password": pwd,
                "name": name,
                "role": "student",
                "course": course if course else "Student",
                "contact": contact
            })

            messagebox.showinfo("Success", f"Registration successful!\nYou can now log in using Student ID '{student_id}'.", parent=reg_win)
            reg_win.destroy()

        submit_btn = tk.Button(reg_win, text="Submit Registration", bg="#2b6cb0", fg="white", font=("Arial", 10), command=save_student)
        submit_btn.pack(pady=15)

    # ================= STUDENT DASHBOARD =================
    def show_student_dashboard(self):
        self.clear_frames()

        top_frame = tk.Frame(self, bg="#2b6cb0", pady=10, padx=15)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text=f"Student Portal: {self.current_user['name']} ({self.current_user['course']})", 
                 font=("Arial", 12, "bold"), fg="white", bg="#2b6cb0").pack(side=tk.LEFT)

        tk.Button(top_frame, text="Logout", bg="#e53e3e", fg="white", command=self.show_login_screen).pack(side=tk.RIGHT)

        # search bar
        search_frame = tk.Frame(self, pady=8, padx=15)
        search_frame.pack(fill=tk.X)

        tk.Label(search_frame, text="Search Book:").pack(side=tk.LEFT, padx=5)
        self.student_search_entry = tk.Entry(search_frame, width=30)
        self.student_search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="Search", command=self.filter_student_books).pack(side=tk.LEFT, padx=3)
        tk.Button(search_frame, text="Reset", command=self.refresh_student_books).pack(side=tk.LEFT, padx=3)

        # book table
        table_frame = tk.Frame(self, padx=15)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "author", "category", "copies")
        self.student_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.student_tree.heading("id", text="ID")
        self.student_tree.heading("title", text="Book Title")
        self.student_tree.heading("author", text="Author")
        self.student_tree.heading("category", text="Category")
        self.student_tree.heading("copies", text="Available Copies")

        self.student_tree.column("id", width=40, anchor="center")
        self.student_tree.column("title", width=260)
        self.student_tree.column("author", width=180)
        self.student_tree.column("category", width=120)
        self.student_tree.column("copies", width=110, anchor="center")
        self.student_tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_student_books()

        # action buttons
        action_frame = tk.Frame(self, pady=12)
        action_frame.pack()

        tk.Button(action_frame, text="Borrow Book", width=15, bg="#3182ce", fg="white", font=("Arial", 10, "bold"), command=self.student_borrow_book).pack(side=tk.LEFT, padx=8)
        tk.Button(action_frame, text="Reserve Book", width=15, bg="#4a5568", fg="white", font=("Arial", 10), command=self.student_reserve_book).pack(side=tk.LEFT, padx=8)
        tk.Button(action_frame, text="My Borrowed Books", width=18, bg="#38a169", fg="white", font=("Arial", 10), command=self.show_my_borrowed_dialog).pack(side=tk.LEFT, padx=8)

    def refresh_student_books(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for b in books:
            self.student_tree.insert("", tk.END, values=(b["id"], b["title"], b["author"], b["category"], b["copies"]))

    def filter_student_books(self):
        q = self.student_search_entry.get().strip().lower()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for b in books:
            if q in b["title"].lower() or q in b["author"].lower() or q in b["category"].lower():
                self.student_tree.insert("", tk.END, values=(b["id"], b["title"], b["author"], b["category"], b["copies"]))

    def student_borrow_book(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book from the list to borrow.")
            return

        book_id = self.student_tree.item(selected[0])["values"][0]
        selected_book = next((b for b in books if b["id"] == book_id), None)

        if not selected_book:
            return

        if selected_book["copies"] <= 0:
            messagebox.showwarning("Out of Stock", "Sorry, this book has 0 copies available on the shelf.\nYou can reserve it instead.")
            return

        active_loans = [r for r in borrow_records if r["username"] == self.current_user["username"] and r["status"] == "Borrowed"]
        if len(active_loans) >= 3:
            messagebox.showwarning("Borrow Limit", "You have reached the maximum borrow limit of 3 books.")
            return

        selected_book["copies"] -= 1

        record = {
            "record_id": len(borrow_records) + 1,
            "username": self.current_user["username"],
            "name": self.current_user["name"],
            "course": self.current_user["course"],
            "book_id": selected_book["id"],
            "book_title": selected_book["title"],
            "status": "Borrowed",
            "fine": 0.0
        }
        borrow_records.append(record)

        self.refresh_student_books()
        messagebox.showinfo("Success", f"'{selected_book['title']}' borrowed successfully!\nStandard return period is within {BORROW_DAYS} days.")

    def student_reserve_book(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to reserve.")
            return

        book_id = self.student_tree.item(selected[0])["values"][0]
        selected_book = next((b for b in books if b["id"] == book_id), None)

        res = {
            "id": len(reservations) + 1,
            "username": self.current_user["username"],
            "name": self.current_user["name"],
            "book_title": selected_book["title"],
            "status": "Pending"
        }
        reservations.append(res)
        messagebox.showinfo("Reserved", f"Reservation for '{selected_book['title']}' submitted!")

    def show_my_borrowed_dialog(self):
        win = tk.Toplevel(self)
        win.title("My Borrowed Books & Returns")
        win.geometry("640x360")

        tk.Label(win, text=f"Borrowed Books for {self.current_user['name']}", font=("Arial", 11, "bold")).pack(pady=8)

        cols = ("rec_id", "title", "status", "fine")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=8)
        tree.heading("rec_id", text="Rec #")
        tree.heading("title", text="Book Title")
        tree.heading("status", text="Status")
        tree.heading("fine", text="Fine")

        tree.column("rec_id", width=50, anchor="center")
        tree.column("title", width=340)
        tree.column("status", width=100, anchor="center")
        tree.column("fine", width=80, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        def load_records():
            for item in tree.get_children():
                tree.delete(item)
            my_records = [r for r in borrow_records if r["username"] == self.current_user["username"]]
            for r in my_records:
                tree.insert("", tk.END, values=(r["record_id"], r["book_title"], r["status"], f"P{r['fine']:.2f}"))

        load_records()

        def do_return():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Please select a borrowed book to return.", parent=win)
                return

            rec_id = tree.item(sel[0])["values"][0]
            rec = next((r for r in borrow_records if r["record_id"] == rec_id), None)

            if not rec or rec["status"] == "Returned":
                messagebox.showinfo("Info", "This book is already marked as returned.", parent=win)
                return

            # ask days kept using simple dialog
            days = simpledialog.askinteger("Return Book", f"How many days did you keep this book?\n(Standard loan period: {BORROW_DAYS} days):", parent=win, minvalue=1, initialvalue=BORROW_DAYS)
            if days is None:
                return

            fine = 0.0
            if days > BORROW_DAYS:
                overdue = days - BORROW_DAYS
                fine = overdue * FINE_RATE
                messagebox.showwarning("Overdue Fine", f"Book is {overdue} day(s) overdue!\nFine calculation: {overdue} days x P{FINE_RATE:.2f} = P{fine:.2f}", parent=win)
            else:
                messagebox.showinfo("On Time", "Book returned on time. No overdue penalty!", parent=win)

            rec["status"] = "Returned"
            rec["fine"] = fine

            for b in books:
                if b["id"] == rec["book_id"]:
                    b["copies"] += 1
                    break

            load_records()
            self.refresh_student_books()

        btn_box = tk.Frame(win, pady=10)
        btn_box.pack()
        tk.Button(btn_box, text="Return Selected Book", bg="#38a169", fg="white", font=("Arial", 10), command=do_return).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="Close", command=win.destroy).pack(side=tk.LEFT, padx=5)

    # ================= LIBRARIAN DASHBOARD =================
    def show_librarian_dashboard(self):
        self.clear_frames()

        top_frame = tk.Frame(self, bg="#1a365d", pady=10, padx=15)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="Librarian Administrative Desk", font=("Arial", 12, "bold"), fg="white", bg="#1a365d").pack(side=tk.LEFT)
        tk.Button(top_frame, text="Logout", bg="#e53e3e", fg="white", command=self.show_login_screen).pack(side=tk.RIGHT)

        # book inventory table
        table_frame = tk.Frame(self, padx=15, pady=8)
        table_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(table_frame, text="Book Inventory", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 4))

        columns = ("id", "title", "author", "category", "copies")
        self.admin_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.admin_tree.heading("id", text="ID")
        self.admin_tree.heading("title", text="Title")
        self.admin_tree.heading("author", text="Author")
        self.admin_tree.heading("category", text="Category")
        self.admin_tree.heading("copies", text="Copies")

        self.admin_tree.column("id", width=40, anchor="center")
        self.admin_tree.column("title", width=260)
        self.admin_tree.column("author", width=180)
        self.admin_tree.column("category", width=120)
        self.admin_tree.column("copies", width=80, anchor="center")
        self.admin_tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_admin_books()

        # action buttons matching last year's layout style
        btn_row1 = tk.Frame(self, pady=6)
        btn_row1.pack()

        tk.Button(btn_row1, text="Restock / Change Copies", width=22, bg="#2b6cb0", fg="white", font=("Arial", 10), command=self.admin_restock_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row1, text="Add New Book", width=16, bg="#319795", fg="white", font=("Arial", 10), command=self.admin_add_book_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row1, text="Delete Book", width=14, bg="#c53030", fg="white", font=("Arial", 10), command=self.admin_delete_book).pack(side=tk.LEFT, padx=5)

        btn_row2 = tk.Frame(self, pady=6)
        btn_row2.pack()

        tk.Button(btn_row2, text="View Registered Students", width=22, command=self.show_students_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row2, text="View Borrow Records", width=18, command=self.show_records_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row2, text="View Reservations", width=16, command=self.show_reservations_dialog).pack(side=tk.LEFT, padx=5)

    def refresh_admin_books(self):
        for item in self.admin_tree.get_children():
            self.admin_tree.delete(item)
        for b in books:
            self.admin_tree.insert("", tk.END, values=(b["id"], b["title"], b["author"], b["category"], b["copies"]))

    # Popup matching "How many do you want to Stock?" from the screenshot
    def admin_restock_dialog(self):
        selected = self.admin_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to restock.")
            return

        book_id = self.admin_tree.item(selected[0])["values"][0]
        selected_book = next((b for b in books if b["id"] == book_id), None)
        if not selected_book:
            return

        stock_win = tk.Toplevel(self)
        stock_win.title("Restock Book")
        stock_win.geometry("300x160")
        stock_win.resizable(False, False)

        tk.Label(stock_win, text=f"How many do you want to Stock?", font=("Arial", 11, "bold")).pack(pady=(15, 5))
        tk.Label(stock_win, text=f"Book: {selected_book['title'][:25]} (Current: {selected_book['copies']})", fg="#718096").pack(pady=(0, 10))

        count_entry = tk.Entry(stock_win, width=15, font=("Arial", 11), justify="center")
        count_entry.pack(pady=5)
        count_entry.focus()

        def do_stock():
            try:
                added = int(count_entry.get().strip())
                if added < 0:
                    messagebox.showerror("Error", "Please enter a positive number.", parent=stock_win)
                    return
                selected_book["copies"] += added
                self.refresh_admin_books()
                messagebox.showinfo("Updated", f"Successfully updated copies to {selected_book['copies']}!", parent=stock_win)
                stock_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.", parent=stock_win)

        tk.Button(stock_win, text="Submit", font=("Arial", 10, "bold"), width=12, command=do_stock).pack(pady=10)

    def admin_add_book_dialog(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add New Book")
        add_win.geometry("360x240")
        add_win.resizable(False, False)

        tk.Label(add_win, text="Add New Book to Inventory", font=("Arial", 11, "bold")).pack(pady=8)
        form = tk.Frame(add_win, padx=15)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Title:").grid(row=0, column=0, sticky="w", pady=4)
        t_entry = tk.Entry(form, width=25)
        t_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Author:").grid(row=1, column=0, sticky="w", pady=4)
        a_entry = tk.Entry(form, width=25)
        a_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Category:").grid(row=2, column=0, sticky="w", pady=4)
        c_entry = tk.Entry(form, width=25)
        c_entry.grid(row=2, column=1, pady=4)

        tk.Label(form, text="Copies:").grid(row=3, column=0, sticky="w", pady=4)
        qty_entry = tk.Entry(form, width=25)
        qty_entry.insert(0, "3")
        qty_entry.grid(row=3, column=1, pady=4)

        def save_book():
            title = t_entry.get().strip()
            author = a_entry.get().strip()
            cat = c_entry.get().strip()
            try:
                qty = int(qty_entry.get().strip())
            except ValueError:
                qty = 1

            if not title:
                messagebox.showerror("Error", "Title cannot be empty.", parent=add_win)
                return

            new_id = len(books) + 1
            books.append({
                "id": new_id,
                "title": title,
                "author": author if author else "Unknown",
                "category": cat if cat else "General",
                "copies": qty
            })
            self.refresh_admin_books()
            messagebox.showinfo("Success", f"'{title}' added successfully!", parent=add_win)
            add_win.destroy()

        tk.Button(add_win, text="Save Book", bg="#2b6cb0", fg="white", font=("Arial", 10), command=save_book).pack(pady=10)

    def admin_delete_book(self):
        selected = self.admin_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete.")
            return

        book_id = self.admin_tree.item(selected[0])["values"][0]
        selected_book = next((b for b in books if b["id"] == book_id), None)
        if not selected_book:
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_book['title']}'?"):
            books.remove(selected_book)
            self.refresh_admin_books()
            messagebox.showinfo("Deleted", "Book removed from inventory.")

    def show_students_dialog(self):
        win = tk.Toplevel(self)
        win.title("Registered Students")
        win.geometry("540x300")

        cols = ("id", "name", "course", "contact")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("id", text="Student ID")
        tree.heading("name", text="Full Name")
        tree.heading("course", text="Course & Year")
        tree.heading("contact", text="Contact")

        tree.column("id", width=100)
        tree.column("name", width=180)
        tree.column("course", width=130)
        tree.column("contact", width=110)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for u in users:
            if u["role"] == "student":
                tree.insert("", tk.END, values=(u["username"], u["name"], u["course"], u["contact"]))

    def show_records_dialog(self):
        win = tk.Toplevel(self)
        win.title("All Borrow Records")
        win.geometry("640x300")

        cols = ("rec_id", "student", "book", "status", "fine")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("rec_id", text="#")
        tree.heading("student", text="Student")
        tree.heading("book", text="Book")
        tree.heading("status", text="Status")
        tree.heading("fine", text="Fine")

        tree.column("rec_id", width=35, anchor="center")
        tree.column("student", width=150)
        tree.column("book", width=240)
        tree.column("status", width=90, anchor="center")
        tree.column("fine", width=70, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for r in borrow_records:
            tree.insert("", tk.END, values=(r["record_id"], r["name"], r["book_title"], r["status"], f"P{r['fine']:.2f}"))

    def show_reservations_dialog(self):
        win = tk.Toplevel(self)
        win.title("All Reservations")
        win.geometry("500x260")

        cols = ("id", "student", "book", "status")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("id", text="#")
        tree.heading("student", text="Student")
        tree.heading("book", text="Book")
        tree.heading("status", text="Status")

        tree.column("id", width=40, anchor="center")
        tree.column("student", width=160)
        tree.column("book", width=220)
        tree.column("status", width=80, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for res in reservations:
            tree.insert("", tk.END, values=(res["id"], res["name"], res["book_title"], res["status"]))


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
