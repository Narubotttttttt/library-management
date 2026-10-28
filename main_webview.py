import os
import sys
import webview
import backend


class LibraryApi:
    """Python bridge exposing backend database operations to HTML/JS frontend."""

    def __init__(self):
        self.current_user = None

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

    def get_books(self, query=""):
        if query:
            return backend.search_books(query)
        return backend.get_all_books()

    def borrow_book(self, book_id):
        if not self.current_user:
            return {"success": False, "message": "User not authenticated."}
        success, msg = backend.borrow_book(self.current_user, int(book_id))
        return {"success": success, "message": msg}

    def reserve_book(self, book_id):
        if not self.current_user:
            return {"success": False, "message": "User not authenticated."}
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

    def get_all_borrow_records(self):
        return backend.get_all_borrow_records()

    def get_all_students(self):
        return backend.get_all_students()

    def get_all_reservations(self):
        return backend.get_all_reservations()


def main():
    api = LibraryApi()
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    html_file = os.path.join(web_dir, "index.html")

    window = webview.create_window(
        title="School Library Management System",
        url=html_file,
        js_api=api,
        width=1000,
        height=680,
        min_size=(850, 560),
        resizable=True
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()

