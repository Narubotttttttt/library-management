import tkinter as tk
from tkinter import ttk, messagebox
import backend


class StudentView(tk.Frame):
    """Student portal view for browsing, searching, borrowing, and returning books."""
    def __init__(self, master, current_user):
        super().__init__(master)
        self.master = master
        self.current_user = current_user
        self.build_ui()

    def build_ui(self):
        # Top banner
        top_frame = tk.Frame(self, bg="#2b6cb0", pady=10, padx=15)
        top_frame.pack(fill=tk.X)

        header_text = f"Student Portal: {self.current_user['name']} ({self.current_user.get('course', 'Student')})"
        tk.Label(
            top_frame, 
            text=header_text, 
            font=("Arial", 12, "bold"), 
            fg="white", 
            bg="#2b6cb0"
        ).pack(side=tk.LEFT)

        tk.Button(
            top_frame, 
            text="Logout", 
            bg="#e53e3e", 
            fg="white", 
            command=self.master.show_login_screen
        ).pack(side=tk.RIGHT)

        # Search bar
        search_frame = tk.Frame(self, pady=8, padx=15)
        search_frame.pack(fill=tk.X)

        tk.Label(search_frame, text="Search Book:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="Search", command=self.filter_books).pack(side=tk.LEFT, padx=3)
        tk.Button(search_frame, text="Reset", command=self.refresh_books).pack(side=tk.LEFT, padx=3)

        # Book catalog table with Shelf Location
        table_frame = tk.Frame(self, padx=15)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "author", "category", "shelf", "copies")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Book Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("category", text="Category")
        self.tree.heading("shelf", text="Shelf Location")
        self.tree.heading("copies", text="Available Copies")

        self.tree.column("id", width=35, anchor="center")
        self.tree.column("title", width=240)
        self.tree.column("author", width=160)
        self.tree.column("category", width=110)
        self.tree.column("shelf", width=100, anchor="center")
        self.tree.column("copies", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_books()

        # Action buttons
        action_frame = tk.Frame(self, pady=12)
        action_frame.pack()

        tk.Button(
            action_frame, 
            text="Borrow Book", 
            width=15, 
            bg="#3182ce", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            command=self.borrow_selected_book
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            action_frame, 
            text="Reserve Book", 
            width=15, 
            bg="#4a5568", 
            fg="white", 
            font=("Arial", 10), 
            command=self.reserve_selected_book
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            action_frame, 
            text="My Borrowed Books & Returns", 
            width=26, 
            bg="#38a169", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            command=self.show_my_borrowed_dialog
        ).pack(side=tk.LEFT, padx=8)

    def refresh_books(self):
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

    def filter_books(self):
        query = self.search_entry.get()
        filtered = backend.search_books(query)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for b in filtered:
            self.tree.insert("", tk.END, values=(
                b["id"], 
                b["title"], 
                b["author"], 
                b["category"], 
                b.get("shelf", "Main Shelf"), 
                b["copies"]
            ))

    def borrow_selected_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book from the list to borrow.")
            return

        book_id = self.tree.item(selected[0])["values"][0]
        success, msg = backend.borrow_book(self.current_user, book_id)
        if success:
            self.refresh_books()
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showwarning("Borrow Notice", msg)

    def reserve_selected_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a book to reserve.")
            return

        book_id = self.tree.item(selected[0])["values"][0]
        success, msg = backend.reserve_book(self.current_user, book_id)
        if success:
            messagebox.showinfo("Reserved", msg)
        else:
            messagebox.showwarning("Notice", msg)

    def show_my_borrowed_dialog(self):
        """Student Personal Member Portal displaying active loans and deadlines."""
        win = tk.Toplevel(self)
        win.title("Student Member Portal - My Borrowed Books")
        win.geometry("700x380")

        tk.Label(
            win, 
            text=f"Active Loans & Borrow History for {self.current_user['name']}", 
            font=("Arial", 11, "bold")
        ).pack(pady=8)

        cols = ("rec_id", "title", "borrow_date", "due_date", "status", "fine")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=9)
        tree.heading("rec_id", text="#")
        tree.heading("title", text="Book Title")
        tree.heading("borrow_date", text="Borrowed Date")
        tree.heading("due_date", text="Due Date")
        tree.heading("status", text="Status")
        tree.heading("fine", text="Penalty Fine")

        tree.column("rec_id", width=35, anchor="center")
        tree.column("title", width=250)
        tree.column("borrow_date", width=95, anchor="center")
        tree.column("due_date", width=95, anchor="center")
        tree.column("status", width=85, anchor="center")
        tree.column("fine", width=85, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        def load_records():
            for item in tree.get_children():
                tree.delete(item)
            records = backend.get_user_borrow_records(self.current_user["username"])
            for r in records:
                tree.insert("", tk.END, values=(
                    r["record_id"], 
                    r["book_title"], 
                    r.get("borrow_date", "N/A"),
                    r.get("due_date", "N/A"),
                    r["status"], 
                    f"P{r['fine']:.2f}"
                ))

        load_records()

        def do_return():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Please select a borrowed book to return.", parent=win)
                return

            rec_id = tree.item(sel[0])["values"][0]

            # Automated fine calculation via backend - no manual date counting needed!
            success, msg, fine, is_overdue = backend.return_borrowed_book(rec_id)
            if not success:
                messagebox.showinfo("Info", msg, parent=win)
                return

            if is_overdue:
                messagebox.showwarning("Overdue Notice", msg, parent=win)
            else:
                messagebox.showinfo("Return Successful", msg, parent=win)

            load_records()
            self.refresh_books()

        btn_box = tk.Frame(win, pady=10)
        btn_box.pack()
        tk.Button(
            btn_box, 
            text="Return Selected Book", 
            bg="#38a169", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            command=do_return
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="Close", command=win.destroy).pack(side=tk.LEFT, padx=5)
