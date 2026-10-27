import tkinter as tk
from tkinter import messagebox
import backend


class LoginView(tk.Frame):
    """View handling multi-role user login and student registration modal."""
    def __init__(self, master):
        super().__init__(master, padx=20, pady=20)
        self.master = master
        self.build_ui()

    def build_ui(self):
        # Center container
        center_frame = tk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        title_label = tk.Label(
            center_frame, 
            text="School Library Management System", 
            font=("Arial", 16, "bold"), 
            fg="#1a365d"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        sub_label = tk.Label(center_frame, text="User Login Portal", font=("Arial", 12))
        sub_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))

        tk.Label(center_frame, text="Student ID / Username:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", pady=5)
        self.username_entry = tk.Entry(center_frame, width=25, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=5, padx=5)

        tk.Label(center_frame, text="Password:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", pady=5)
        self.password_entry = tk.Entry(center_frame, width=25, font=("Arial", 10), show="*")
        self.password_entry.grid(row=3, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(center_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

        login_btn = tk.Button(
            btn_frame, 
            text="Login", 
            width=12, 
            bg="#2b6cb0", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            command=self.handle_login
        )
        login_btn.pack(side=tk.LEFT, padx=5)

        register_btn = tk.Button(
            btn_frame, 
            text="Register", 
            width=12, 
            bg="#4a5568", 
            fg="white", 
            font=("Arial", 10), 
            command=self.show_register_dialog
        )
        register_btn.pack(side=tk.LEFT, padx=5)

        hint = tk.Label(
            center_frame, 
            text="Demo Accounts:\nLibrarian: admin / 123\nStudent: 2024-001 / 123", 
            fg="#718096", 
            font=("Arial", 9)
        )
        hint.grid(row=5, column=0, columnspan=2, pady=(15, 0))

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = backend.authenticate_user(username, password)
        if user:
            messagebox.showinfo("Login Success", f"Welcome back, {user['name']}!")
            self.master.open_dashboard(user)
        else:
            messagebox.showerror("Error", "Invalid Student ID/Username or Password.")

    def show_register_dialog(self):
        reg_win = tk.Toplevel(self)
        reg_win.title("Student Registration")
        reg_win.geometry("400x340")
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

        tk.Label(form, text="Email Address:").grid(row=3, column=0, sticky="w", pady=4)
        email_entry = tk.Entry(form, width=25)
        email_entry.grid(row=3, column=1, pady=4)

        tk.Label(form, text="Course & Year:").grid(row=4, column=0, sticky="w", pady=4)
        course_entry = tk.Entry(form, width=25)
        course_entry.grid(row=4, column=1, pady=4)

        tk.Label(form, text="Contact No:").grid(row=5, column=0, sticky="w", pady=4)
        contact_entry = tk.Entry(form, width=25)
        contact_entry.grid(row=5, column=1, pady=4)

        def save_student():
            success, msg = backend.register_student(
                name=name_entry.get(),
                student_id=id_entry.get(),
                password=pass_entry.get(),
                email=email_entry.get(),
                course=course_entry.get(),
                contact=contact_entry.get()
            )
            if success:
                messagebox.showinfo("Success", msg, parent=reg_win)
                reg_win.destroy()
            else:
                messagebox.showerror("Error", msg, parent=reg_win)

        submit_btn = tk.Button(
            reg_win, 
            text="Submit Registration", 
            bg="#2b6cb0", 
            fg="white", 
            font=("Arial", 10, "bold"), 
            command=save_student
        )
        submit_btn.pack(pady=15)
