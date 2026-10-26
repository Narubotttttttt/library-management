import hashlib
import os
from datetime import datetime, date, timedelta
import pymysql
import pymysql.cursors

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'library_db'
}

DAILY_FINE_RATE = 10.00


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def initialize_database():
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        return False

    try:
        raw_conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        with raw_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` DEFAULT CHARACTER SET utf8mb4;")
        raw_conn.close()

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES LIKE 'users';")
            if not cursor.fetchone():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    sql_statements = f.read().split(';')
                    for stmt in sql_statements:
                        stmt = stmt.strip()
                        if stmt:
                            try:
                                cursor.execute(stmt)
                            except Exception:
                                pass
        conn.close()
        return True
    except Exception:
        return False


def authenticate_user(identifier: str, password: str, role: str = None):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        pwd_hash = hash_password(password)

        if role:
            query = """
                SELECT id, user_id_number, full_name, email, role, course_year
                FROM users 
                WHERE (user_id_number = %s OR email = %s) 
                  AND role = %s 
                  AND (password = %s OR password = %s)
                LIMIT 1;
            """
            cursor.execute(query, (identifier, identifier, role, pwd_hash, password))
        else:
            query = """
                SELECT id, user_id_number, full_name, email, role, course_year
                FROM users 
                WHERE (user_id_number = %s OR email = %s) 
                  AND (password = %s OR password = %s)
                LIMIT 1;
            """
            cursor.execute(query, (identifier, identifier, pwd_hash, password))
        return cursor.fetchone()
    finally:
        conn.close()


def register_student(user_id_number: str, full_name: str, email: str, password: str, course_year: str, contact_number: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        pwd_hash = hash_password(password)

        query = """
            INSERT INTO users (user_id_number, full_name, email, password, role, course_year, contact_number)
            VALUES (%s, %s, %s, %s, 'student', %s, %s);
        """
        cursor.execute(query, (user_id_number, full_name, email, pwd_hash, course_year, contact_number))
        return True, "Registration successful! You may now sign in."
    except Exception as e:
        err_msg = str(e)
        if 'Duplicate' in err_msg or 'UNIQUE' in err_msg:
            return False, "Student ID or Email is already registered!"
        return False, f"Registration failed: {err_msg}"
    finally:
        conn.close()


def create_librarian(user_id_number: str, full_name: str, email: str, password: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        pwd_hash = hash_password(password)

        query = """
            INSERT INTO users (user_id_number, full_name, email, password, role)
            VALUES (%s, %s, %s, %s, 'librarian');
        """
        cursor.execute(query, (user_id_number, full_name, email, pwd_hash))
        return True, "Librarian account created successfully!"
    except Exception as e:
        err_msg = str(e)
        if 'Duplicate' in err_msg or 'UNIQUE' in err_msg:
            return False, "Librarian ID or Email is already registered!"
        return False, f"Failed to create librarian account: {err_msg}"
    finally:
        conn.close()


def get_dashboard_stats():
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT COUNT(*) AS total_books FROM books;")
        total_books = cursor.fetchone()['total_books']

        cursor.execute("SELECT COUNT(*) AS borrowed_count FROM borrow_records WHERE return_date IS NULL;")
        borrowed_count = cursor.fetchone()['borrowed_count']

        cursor.execute("SELECT COUNT(*) AS overdue_count FROM borrow_records WHERE return_date IS NULL AND due_date < CURDATE();")
        overdue_count = cursor.fetchone()['overdue_count']

        cursor.execute("SELECT COUNT(*) AS reservations_count FROM reservations WHERE status = 'pending';")
        reservations_count = cursor.fetchone()['reservations_count']

        return {
            'total_books': total_books,
            'borrowed_count': borrowed_count,
            'overdue_count': overdue_count,
            'reservations_count': reservations_count
        }
    finally:
        conn.close()


def get_recent_transactions(limit=8):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT br.id, br.borrow_date, br.due_date, br.return_date, br.fine_amount, br.status,
                   u.full_name AS student_name, u.user_id_number,
                   b.title AS book_title, b.isbn
            FROM borrow_records br
            JOIN users u ON br.user_id = u.id
            JOIN books b ON br.book_id = b.id
            ORDER BY br.id DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_books():
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT b.id, b.isbn, b.title, b.author, b.category_id, b.total_copies, 
                   b.available_copies, b.shelf_location, b.description,
                   c.name AS category_name
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            ORDER BY b.title ASC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def get_categories():
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, name, description FROM categories ORDER BY name ASC;")
        return cursor.fetchall()
    finally:
        conn.close()


def add_book(title, author, isbn, category_id, total_copies, shelf_location, description):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        total_copies = int(total_copies)
        query = """
            INSERT INTO books (title, author, isbn, category_id, total_copies, available_copies, shelf_location, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (title, author, isbn, category_id, total_copies, total_copies, shelf_location, description))
        return True, "Book title successfully added to catalog!"
    except Exception as e:
        return False, f"Failed to add book: {e}"
    finally:
        conn.close()


def update_book(book_id, title, author, isbn, category_id, total_copies, shelf_location, description):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT total_copies, available_copies FROM books WHERE id = %s;", (book_id,))
        curr = cursor.fetchone()
        if not curr:
            return False, "Book not found."

        new_total = int(total_copies)
        borrowed_currently = curr['total_copies'] - curr['available_copies']
        new_available = max(0, new_total - borrowed_currently)

        query = """
            UPDATE books 
            SET title = %s, author = %s, isbn = %s, category_id = %s, 
                total_copies = %s, available_copies = %s, shelf_location = %s, description = %s
            WHERE id = %s;
        """
        cursor.execute(query, (title, author, isbn, category_id, new_total, new_available, shelf_location, description, book_id))
        return True, "Book details successfully updated!"
    except Exception as e:
        return False, f"Failed to update book: {e}"
    finally:
        conn.close()


def delete_book(book_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM borrow_records WHERE book_id = %s AND return_date IS NULL;", (book_id,))
        if cursor.fetchone()[0] > 0:
            return False, "Cannot delete book while copies are currently issued to students!"

        cursor.execute("DELETE FROM books WHERE id = %s;", (book_id,))
        return True, "Book removed from inventory."
    except Exception as e:
        return False, f"Error deleting book: {e}"
    finally:
        conn.close()


def get_active_borrows():
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        update_fine_sql = """
            UPDATE borrow_records 
            SET status = 'overdue',
                fine_amount = DATEDIFF(CURDATE(), due_date) * %s
            WHERE return_date IS NULL AND due_date < CURDATE();
        """
        cursor.execute(update_fine_sql, (DAILY_FINE_RATE,))

        query = """
            SELECT br.id, br.borrow_date, br.due_date, br.fine_amount, br.status,
                   u.id AS student_pk, u.full_name AS student_name, u.user_id_number,
                   b.id AS book_pk, b.title AS book_title, b.isbn,
                   DATEDIFF(br.due_date, CURDATE()) AS days_left
            FROM borrow_records br
            JOIN users u ON br.user_id = u.id
            JOIN books b ON br.book_id = b.id
            WHERE br.return_date IS NULL
            ORDER BY br.due_date ASC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def issue_book(user_id, book_id, loan_days=7):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT available_copies, title FROM books WHERE id = %s;", (book_id,))
        book = cursor.fetchone()
        if not book or book['available_copies'] <= 0:
            return False, "This book has no available copies to loan right now!"

        cursor.execute("SELECT COUNT(*) AS overdue_cnt FROM borrow_records WHERE user_id = %s AND return_date IS NULL AND due_date < CURDATE();", (user_id,))
        if cursor.fetchone()['overdue_cnt'] > 0:
            return False, "Student has unresolved overdue books! Clear pending returns first."

        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=int(loan_days))

        cursor.execute("""
            INSERT INTO borrow_records (user_id, book_id, borrow_date, due_date, status)
            VALUES (%s, %s, %s, %s, 'borrowed');
        """, (user_id, book_id, borrow_date, due_date))

        cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = %s;", (book_id,))

        cursor.execute("""
            UPDATE reservations 
            SET status = 'completed' 
            WHERE user_id = %s AND book_id = %s AND status = 'pending';
        """, (user_id, book_id))

        return True, f"Successfully issued '{book['title']}'! Due on {due_date.strftime('%B %d, %Y')}."
    except Exception as e:
        return False, f"Failed to issue book: {e}"
    finally:
        conn.close()


def process_return(record_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT book_id, due_date, fine_amount FROM borrow_records WHERE id = %s AND return_date IS NULL;", (record_id,))
        record = cursor.fetchone()
        if not record:
            return False, "Active borrow record not found."

        return_date = date.today()
        fine = 0.00
        if return_date > record['due_date']:
            days_late = (return_date - record['due_date']).days
            fine = days_late * DAILY_FINE_RATE

        cursor.execute("""
            UPDATE borrow_records 
            SET return_date = %s, fine_amount = %s, status = 'returned'
            WHERE id = %s;
        """, (return_date, fine, record_id))

        cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = %s;", (record['book_id'],))

        msg = "Book returned successfully!"
        if fine > 0:
            msg += f" Overdue penalty fine of ₱{fine:.2f} has been assessed."
        return True, msg
    except Exception as e:
        return False, f"Failed to return book: {e}"
    finally:
        conn.close()


def get_all_reservations():
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT r.id, r.reservation_date, r.status,
                   u.id AS student_id, u.full_name AS student_name, u.user_id_number,
                   b.id AS book_id, b.title AS book_title, b.available_copies
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            JOIN books b ON r.book_id = b.id
            WHERE r.status = 'pending'
            ORDER BY r.reservation_date ASC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def reserve_book(user_id, book_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT id FROM reservations WHERE user_id = %s AND book_id = %s AND status = 'pending';", (user_id, book_id))
        if cursor.fetchone():
            return False, "You already have a pending reservation for this title!"

        cursor.execute("SELECT id FROM borrow_records WHERE user_id = %s AND book_id = %s AND return_date IS NULL;", (user_id, book_id))
        if cursor.fetchone():
            return False, "You are currently borrowing a copy of this book!"

        cursor.execute("INSERT INTO reservations (user_id, book_id, status) VALUES (%s, %s, 'pending');", (user_id, book_id))
        return True, "Reservation request submitted! Please visit the circulation desk to collect your copy."
    except Exception as e:
        return False, f"Failed to reserve: {e}"
    finally:
        conn.close()


def cancel_reservation(reservation_id, user_id=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = %s AND user_id = %s;", (reservation_id, user_id))
        else:
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = %s;", (reservation_id,))
        return True, "Reservation cancelled."
    finally:
        conn.close()


def get_students_directory():
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT u.id, u.user_id_number, u.full_name, u.email, u.course_year, u.contact_number,
                   COUNT(CASE WHEN br.return_date IS NULL THEN 1 END) AS active_loans,
                   COUNT(CASE WHEN br.return_date IS NULL AND br.due_date < CURDATE() THEN 1 END) AS overdue_count
            FROM users u
            LEFT JOIN borrow_records br ON u.id = br.user_id
            WHERE u.role = 'student'
            GROUP BY u.id
            ORDER BY u.full_name ASC;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def get_student_borrow_records(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            UPDATE borrow_records 
            SET status = 'overdue',
                fine_amount = DATEDIFF(CURDATE(), due_date) * %s
            WHERE user_id = %s AND return_date IS NULL AND due_date < CURDATE();
        """, (DAILY_FINE_RATE, user_id))

        query = """
            SELECT br.id, br.borrow_date, br.due_date, br.return_date, br.fine_amount, br.status,
                   b.title AS book_title, b.author, b.isbn, b.shelf_location,
                   DATEDIFF(br.due_date, CURDATE()) AS days_left
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            WHERE br.user_id = %s
            ORDER BY (br.return_date IS NULL) DESC, br.due_date ASC;
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_student_reservations(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT r.id, r.reservation_date, r.status,
                   b.title AS book_title, b.author, b.shelf_location
            FROM reservations r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = %s
            ORDER BY r.reservation_date DESC;
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        conn.close()
