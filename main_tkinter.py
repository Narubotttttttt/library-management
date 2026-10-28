import tkinter as tk
from views import LoginView, StudentView, AdminView


class LibraryApp(tk.Tk):
    """Main window controller for the School Library Management System."""
    def __init__(self):
        super().__init__()
        self.title("School Library Management System")
        self.geometry("780x540")
        self.resizable(False, False)

        self.current_user = None
        self.show_login_screen()

    def clear_frames(self):
        """Removes existing screen widgets before transitioning views."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """Displays login & registration screen."""
        self.clear_frames()
        self.current_user = None
        view = LoginView(self)
        view.pack(fill=tk.BOTH, expand=True)

    def open_dashboard(self, user):
        """Routes to either Librarian Desk or Student Portal based on role."""
        self.clear_frames()
        self.current_user = user
        if user["role"] == "librarian":
            view = AdminView(self, user)
        else:
            view = StudentView(self, user)
        view.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
