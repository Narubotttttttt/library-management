import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import backend


class AdminView(tk.Frame):
    """Librarian administrative dashboard featuring analytics cards, inventory, and circulation."""
    def __init__(self, master, current_user):
        super().__init__(master)
        self.master = master
        self.current_user = current_user
        self.build_ui()

    def build_ui(self):
        # Header banner
        top_frame = tk.Frame(self, bg="#1a365d", pady=8, padx=15)
        top_frame.pack(fill=tk.X)

        tk.Label(
            top_frame, 
            text="Librarian Administrative Desk & Analytics", 
            font=("Arial", 12, "bold"), 
            fg="white", 
            bg="#1a365d"
        ).pack(side=tk.LEFT)

        tk.Button(
            top_frame, 
            text="Logout", 
            bg="#e53e3e", 
            fg="white", 
            command=self.master.show_login_screen
        ).pack(side=tk.RIGHT)

        # ================= ANALYTICS METRIC CARDS =================
        metrics_frame = tk.Frame(self, pady=8, padx=15)
        metrics_frame.pack(fill=tk.X)

        self.cards = {}
        metric_configs = [
            ("total_titles", "Total Catalog Titles", "#2b6cb0", "#ebf8ff"),
            ("active_borrowed", "Active Borrowed", "#c05621", "#feebc8"),
            ("overdue_books", "Overdue Books", "#c53030", "#fed7d7"),
            ("pending_reservations", "Pending Holds", "#6b46c1", "#e9d8fd")
        ]

        for i, (key, label, text_color, bg_color) in enumerate(metric_configs):
            card = tk.Frame(metrics_frame, bg=bg_color, relief=tk.RIDGE, bd=1, padx=8, pady=4)
            card.grid(row=0, column=i, sticky="nsew", padx=4)
            metrics_frame.columnconfigure(i, weight=1)

            val_label = tk.Label(card, text="0", font=("Arial", 15, "bold"), fg=text_color, bg=bg_color)
            val_label.pack()
            title_label = tk.Label(card, text=label, font=("Arial", 8, "bold"), fg="#4a5568", bg=bg_color)
            title_label.pack()
            self.cards[key] = val_label

        # Inventory Table with Shelf Location
        table_frame = tk.Frame(self, padx=15, pady=4)
        table_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(table_frame, text="Book Inventory Catalog", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))

        columns = ("id", "title", "author", "category", "shelf", "copies")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("category", text="Category")
        self.tree.heading("shelf", text="Shelf Location")
        self.tree.heading("copies", text="Copies")

        self.tree.column("id", width=35, anchor="center")
        self.tree.column("title", width=240)
        self.tree.column("author", width=160)
        self.tree.column("category", width=110)
        self.tree.column("shelf", width=100, anchor="center")
        self.tree.column("copies", width=70, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_dashboard()

        # Action button row 1: Inventory Management
        btn_row1 = tk.Frame(self, pady=4)
        btn_row1.pack()

        tk.Button(
            btn_row1, 
            text="Add New Book", 
            width=16, 
            bg="#319795", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=self.admin_add_book_dialog
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_row1, 
            text="Restock Copies", 
            width=16, 
            bg="#2b6cb0", 
            fg="white", 
            font=("Arial", 9), 
            command=self.admin_restock_dialog
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_row1, 
            text="Delete Book", 
            width=14, 
            bg="#c53030", 
            fg="white", 
            font=("Arial", 9), 
            command=self.admin_delete_book
        ).pack(side=tk.LEFT, padx=4)

        # Action button row 2: Book Borrowing and Returning Circulation
        btn_row2 = tk.Frame(self, pady=4)
        btn_row2.pack()

        tk.Button(
            btn_row2, 
            text="Issue Book to Student", 
            width=20, 
            bg="#2c5282", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=self.admin_issue_book_dialog
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_row2, 
            text="Record Returned Book", 
            width=20, 
            bg="#2f855a", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            command=self.admin_return_book_dialog
        ).pack(side=tk.LEFT, padx=4)

        # Action button row 3: Directories & Records
        btn_row3 = tk.Frame(self, pady=4)
        btn_row3.pack()

        tk.Button(
            btn_row3, 
            text="Student Directory", 
            width=18, 
            command=self.show_students_dialog
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_row3, 
            text="Borrow Records", 
            width=16, 
            command=self.show_records_dialog
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            btn_row3, 
            text="Reservations List", 
            width=16, 
            command=self.show_reservations_dialog
        ).pack(side=tk.LEFT, padx=4)

    def refresh_dashboard(self):
        """Refreshes both the table inventory and live analytics cards."""
        # Refresh table
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in backend.get_all_books():
            self.tree.insert("", tk.END, values=(
                b["id"], 
                b["title"], 
                b["author"], 
                b["category"], 
                b.get("shelf", "Main Shelf"), 
                b["copies"]
            ))

        # Update metric cards
        metrics = backend.get_analytics_metrics()
        for key, val_label in self.cards.items():
            val_label.config(text=str(metrics.get(key, 0)))

    def admin_restock_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to restock.")
            return

        book_id = self.tree.item(selected[0])["values"][0]
        selected_book = backend.find_book_by_id(book_id)
        if not selected_book:
            return

        stock_win = tk.Toplevel(self)
        stock_win.title("Restock Book")
        stock_win.geometry("300x160")
        stock_win.resizable(False, False)

        tk.Label(stock_win, text="How many copies to add?", font=("Arial", 11, "bold")).pack(pady=(15, 5))
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
                success, msg = backend.restock_book(book_id, added)
                if success:
                    self.refresh_dashboard()
                    messagebox.showinfo("Updated", msg, parent=stock_win)
                    stock_win.destroy()
                else:
                    messagebox.showerror("Error", msg, parent=stock_win)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number.", parent=stock_win)

        tk.Button(stock_win, text="Submit", font=("Arial", 10, "bold"), width=12, command=do_stock).pack(pady=10)

    def admin_add_book_dialog(self):
        add_win = tk.Toplevel(self)
        add_win.title("Add New Book Acquisition")
        add_win.geometry("380x280")
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

        tk.Label(form, text="Shelf Location:").grid(row=3, column=0, sticky="w", pady=4)
        shelf_entry = tk.Entry(form, width=25)
        shelf_entry.insert(0, "Shelf A-1")
        shelf_entry.grid(row=3, column=1, pady=4)

        tk.Label(form, text="Copies:").grid(row=4, column=0, sticky="w", pady=4)
        qty_entry = tk.Entry(form, width=25)
        qty_entry.insert(0, "3")
        qty_entry.grid(row=4, column=1, pady=4)

        def save_book():
            try:
                qty = int(qty_entry.get().strip())
            except ValueError:
                qty = 1

            success, msg = backend.add_book(
                title=t_entry.get(),
                author=a_entry.get(),
                category=c_entry.get(),
                shelf=shelf_entry.get(),
                copies=qty
            )
            if success:
                self.refresh_dashboard()
                messagebox.showinfo("Success", msg, parent=add_win)
                add_win.destroy()
            else:
                messagebox.showerror("Error", msg, parent=add_win)

        tk.Button(add_win, text="Save Book", bg="#2b6cb0", fg="white", font=("Arial", 10, "bold"), command=save_book).pack(pady=10)

    def admin_delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to delete.")
            return

        book_id = self.tree.item(selected[0])["values"][0]
        selected_book = backend.find_book_by_id(book_id)
        if not selected_book:
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_book['title']}'?"):
            backend.delete_book(book_id)
            self.refresh_dashboard()
            messagebox.showinfo("Deleted", "Book removed from inventory.")

    def admin_issue_book_dialog(self):
        """Allows the librarian to issue books directly to a registered student."""
        win = tk.Toplevel(self)
        win.title("Issue Book to Student")
        win.geometry("380x220")
        win.resizable(False, False)

        tk.Label(win, text="Issue Book to Student", font=("Arial", 11, "bold")).pack(pady=10)
        form = tk.Frame(win, padx=15)
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Student ID:").grid(row=0, column=0, sticky="w", pady=6)
        student_entry = tk.Entry(form, width=24)
        student_entry.grid(row=0, column=1, pady=6)

        tk.Label(form, text="Book ID:").grid(row=1, column=0, sticky="w", pady=6)
        book_entry = tk.Entry(form, width=24)
        book_entry.grid(row=1, column=1, pady=6)

        # Pre-fill selected book if any
        selected = self.tree.selection()
        if selected:
            book_entry.insert(0, str(self.tree.item(selected[0])["values"][0]))

        def do_issue():
            s_id = student_entry.get().strip()
            try:
                b_id = int(book_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric Book ID.", parent=win)
                return

            success, msg = backend.issue_book_to_student(s_id, b_id)
            if success:
                self.refresh_dashboard()
                messagebox.showinfo("Success", msg, parent=win)
                win.destroy()
            else:
                messagebox.showwarning("Issue Failed", msg, parent=win)

        tk.Button(win, text="Issue Book", bg="#2c5282", fg="white", font=("Arial", 10, "bold"), command=do_issue).pack(pady=12)

    def admin_return_book_dialog(self):
        """Allows librarian to record returned books."""
        win = tk.Toplevel(self)
        win.title("Record Book Return")
        win.geometry("660x340")

        tk.Label(win, text="Active Loans (Select a record to return)", font=("Arial", 11, "bold")).pack(pady=8)

        cols = ("rec_id", "student", "book", "borrow_date", "due_date", "fine")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=8)
        tree.heading("rec_id", text="#")
        tree.heading("student", text="Student")
        tree.heading("book", text="Book")
        tree.heading("borrow_date", text="Borrow Date")
        tree.heading("due_date", text="Due Date")
        tree.heading("fine", text="Overdue Fine")

        tree.column("rec_id", width=35, anchor="center")
        tree.column("student", width=140)
        tree.column("book", width=200)
        tree.column("borrow_date", width=90, anchor="center")
        tree.column("due_date", width=90, anchor="center")
        tree.column("fine", width=80, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def load_active():
            for item in tree.get_children():
                tree.delete(item)
            active = [r for r in backend.get_all_borrow_records() if r["status"] == "Borrowed"]
            for r in active:
                tree.insert("", tk.END, values=(
                    r["record_id"], 
                    f"{r['name']} ({r['username']})", 
                    r["book_title"], 
                    r.get("borrow_date", "N/A"), 
                    r.get("due_date", "N/A"), 
                    f"P{r['fine']:.2f}"
                ))

        load_active()

        def do_process_return():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Please select a loan record to return.", parent=win)
                return

            rec_id = tree.item(sel[0])["values"][0]
            success, msg, fine, is_overdue = backend.return_borrowed_book(rec_id)
            if success:
                self.refresh_dashboard()
                load_active()
                if is_overdue:
                    messagebox.showwarning("Overdue Notice", msg, parent=win)
                else:
                    messagebox.showinfo("Return Recorded", msg, parent=win)
            else:
                messagebox.showerror("Error", msg, parent=win)

        tk.Button(win, text="Confirm Return for Selected Book", bg="#2f855a", fg="white", font=("Arial", 10, "bold"), command=do_process_return).pack(pady=8)

    def show_students_dialog(self):
        """Displays the centralized Student Directory including email and contact info."""
        win = tk.Toplevel(self)
        win.title("Centralized Student Directory")
        win.geometry("640x300")

        cols = ("id", "name", "email", "course", "contact")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("id", text="Student ID")
        tree.heading("name", text="Full Name")
        tree.heading("email", text="Email Address")
        tree.heading("course", text="Course & Year")
        tree.heading("contact", text="Contact")

        tree.column("id", width=90)
        tree.column("name", width=150)
        tree.column("email", width=160)
        tree.column("course", width=120)
        tree.column("contact", width=100)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for u in backend.get_all_students():
            tree.insert("", tk.END, values=(
                u["username"], 
                u["name"], 
                u.get("email", "N/A"), 
                u.get("course", "Student"), 
                u.get("contact", "")
            ))

    def show_records_dialog(self):
        win = tk.Toplevel(self)
        win.title("All Borrow Records")
        win.geometry("700x320")

        cols = ("rec_id", "student", "book", "borrow_date", "due_date", "status", "fine")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("rec_id", text="#")
        tree.heading("student", text="Student")
        tree.heading("book", text="Book")
        tree.heading("borrow_date", text="Borrow Date")
        tree.heading("due_date", text="Due Date")
        tree.heading("status", text="Status")
        tree.heading("fine", text="Fine")

        tree.column("rec_id", width=30, anchor="center")
        tree.column("student", width=130)
        tree.column("book", width=200)
        tree.column("borrow_date", width=85, anchor="center")
        tree.column("due_date", width=85, anchor="center")
        tree.column("status", width=75, anchor="center")
        tree.column("fine", width=65, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for r in backend.get_all_borrow_records():
            tree.insert("", tk.END, values=(
                r["record_id"], 
                r["name"], 
                r["book_title"], 
                r.get("borrow_date", "N/A"), 
                r.get("due_date", "N/A"), 
                r["status"], 
                f"P{r['fine']:.2f}"
            ))

    def show_reservations_dialog(self):
        win = tk.Toplevel(self)
        win.title("Book Hold & Reservation List")
        win.geometry("540x260")

        cols = ("id", "student", "book", "date_requested", "status")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        tree.heading("id", text="#")
        tree.heading("student", text="Student")
        tree.heading("book", text="Book")
        tree.heading("date_requested", text="Date Requested")
        tree.heading("status", text="Status")

        tree.column("id", width=35, anchor="center")
        tree.column("student", width=150)
        tree.column("book", width=200)
        tree.column("date_requested", width=95, anchor="center")
        tree.column("status", width=75, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for res in backend.get_all_reservations():
            tree.insert("", tk.END, values=(
                res["id"], 
                res["name"], 
                res["book_title"], 
                res.get("date_requested", "N/A"), 
                res["status"]
            ))
