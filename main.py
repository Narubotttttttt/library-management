import os
import webview
import backend

_active_window = None
_views_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "views")


class LibraryApi:
    """Python bridge exposing backend database operations and view routing to HTML/JS.
    Note: Window references are kept at module level to avoid .NET reflection recursion.
    """

    def __init__(self):
        self.current_user = None

    # View Navigation
    def navigate(self, view_name):
        """Routes between views/login.html, views/student.html, and views/admin.html."""
        global _active_window
        target_file = os.path.join(_views_dir, f"{view_name}.html")
        if os.path.exists(target_file) and _active_window:
            _active_window.load_url(os.path.abspath(target_file))
            return {"success": True}
        return {"success": False, "message": f"View '{view_name}' not found."}

    # Authentication
    def login(self, username, password):
        user = backend.authenticate_user(username, password)
        if user:
            self.current_user = user
            safe_user = {k: v for k, v in user.items() if k != "password"}
            return {"success": True, "user": safe_user}
        return {"success": False, "message": "Invalid Student ID/Username or Password."}

    def register(self, name, student_id, password, email, course, contact):
        success, msg = backend.register_student(name, student_id, password, email, course, contact)
        return {"success": success, "message": msg}

    def logout(self):
        self.current_user = None
        return {"success": True}

    def get_current_user(self):
        if not self.current_user:
            return None
        return {k: v for k, v in self.current_user.items() if k != "password"}

    # Books & Catalog
    def get_books(self, query=""):
        if query and isinstance(query, str) and query.strip():
            return backend.search_books(query)
        return backend.get_all_books()

    def borrow_book(self, book_id):
        if not self.current_user:
            return {"success": False, "message": "Please log in first."}
        success, msg = backend.borrow_book(self.current_user, int(book_id))
        return {"success": success, "message": msg}

    def reserve_book(self, book_id):
        if not self.current_user:
            return {"success": False, "message": "Please log in first."}
        success, msg = backend.reserve_book(self.current_user, int(book_id))
        return {"success": success, "message": msg}

    def get_my_borrow_records(self):
        if not self.current_user:
            return []
        return backend.get_user_borrow_records(self.current_user["username"])

    def return_book(self, record_id):
        success, msg, fine, is_overdue = backend.return_borrowed_book(int(record_id))
        return {
            "success": success, 
            "message": msg, 
            "fine": fine, 
            "is_overdue": is_overdue
        }

    # Admin Management & Analytics
    def get_admin_metrics(self):
        return backend.get_analytics_metrics()

    def add_book(self, title, author, category, shelf, copies):
        success, msg = backend.add_book(title, author, category, shelf, int(copies))
        return {"success": success, "message": msg}

    def restock_book(self, book_id, count):
        success, msg = backend.restock_book(int(book_id), int(count))
        return {"success": success, "message": msg}

    def delete_book(self, book_id):
        success, msg = backend.delete_book(int(book_id))
        return {"success": success, "message": msg}

    def issue_book(self, student_id, book_id):
        success, msg = backend.issue_book_to_student(student_id, int(book_id))
        return {"success": success, "message": msg}

    def approve_borrow_request(self, record_id):
        try:
            rid = int(record_id)
        except (ValueError, TypeError):
            return {"success": False, "message": f"Invalid record ID: {record_id}"}
        success, msg = backend.approve_borrow_request(rid)
        return {"success": success, "message": msg}

    def reject_borrow_request(self, record_id):
        try:
            rid = int(record_id)
        except (ValueError, TypeError):
            return {"success": False, "message": f"Invalid record ID: {record_id}"}
        success, msg = backend.reject_borrow_request(rid)
        return {"success": success, "message": msg}

    def get_all_borrow_records(self):
        return backend.get_all_borrow_records()

    def get_all_students(self):
        return backend.get_all_students()

    def get_all_reservations(self):
        return backend.get_all_reservations()


def main():
    global _active_window
    api = LibraryApi()
    initial_html = os.path.join(_views_dir, "login.html")

    _active_window = webview.create_window(
        title="School Library Management System",
        url=os.path.abspath(initial_html),
        js_api=api,
        width=1040,
        height=720,
        min_size=(880, 580),
        resizable=True
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
