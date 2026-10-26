import http.server
import http.cookies
import urllib.parse
import os
import mimetypes
import uuid
import sys
import socketserver
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import db

PORT = 8080
SESSIONS = {}


class LibraryRequestHandler(http.server.BaseHTTPRequestHandler):

    def get_session(self):
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        cookie = http.cookies.SimpleCookie(cookie_header)
        if 'session_id' in cookie:
            sess_id = cookie['session_id'].value
            return SESSIONS.get(sess_id)
        return None

    def create_session(self, user):
        sess_id = str(uuid.uuid4())
        SESSIONS[sess_id] = user
        cookie = http.cookies.SimpleCookie()
        cookie['session_id'] = sess_id
        cookie['session_id']['path'] = '/'
        cookie['session_id']['httponly'] = True
        return cookie['session_id'].OutputString()

    def destroy_session(self):
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = http.cookies.SimpleCookie(cookie_header)
            if 'session_id' in cookie:
                sess_id = cookie['session_id'].value
                SESSIONS.pop(sess_id, None)
        expired_cookie = http.cookies.SimpleCookie()
        expired_cookie['session_id'] = ''
        expired_cookie['session_id']['path'] = '/'
        expired_cookie['session_id']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        return expired_cookie['session_id'].OutputString()

    def redirect(self, location, cookie_header=None):
        self.send_response(302)
        self.send_header('Location', location)
        if cookie_header:
            self.send_header('Set-Cookie', cookie_header)
        self.end_headers()

    def render_html(self, template_name, context=None):
        if context is None:
            context = {}

        # Resolve template across subfolders (librarian/, student/, login/, auth/)
        candidates = [
            os.path.join(BASE_DIR, 'templates', template_name),
            os.path.join(BASE_DIR, 'templates', 'librarian', template_name),
            os.path.join(BASE_DIR, 'templates', 'student', template_name),
            os.path.join(BASE_DIR, 'templates', 'login', template_name),
            os.path.join(BASE_DIR, 'templates', 'auth', template_name),
        ]
        if '_' in template_name and '/' not in template_name:
            folder, rest = template_name.split('_', 1)
            candidates.append(os.path.join(BASE_DIR, 'templates', folder, rest))

        template_path = None
        for cand in candidates:
            if os.path.exists(cand) and os.path.isfile(cand):
                template_path = cand
                break

        if not template_path:
            self.send_error(404, f"Template '{template_name}' not found")
            return

        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()

        alert_box = ""
        if 'alert_msg' in context and context['alert_msg']:
            alert_type = context.get('alert_type', 'info')
            alert_box = f'<div class="alert alert-{alert_type}">{context["alert_msg"]}</div>'
        html = html.replace('{{ALERT_BOX}}', alert_box)

        for key, value in context.items():
            html = html.replace(f'{{{{{key}}}}}', str(value))

        html_bytes = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_bytes)))
        self.end_headers()
        self.wfile.write(html_bytes)

    def serve_static(self, filepath):
        clean_path = os.path.normpath(filepath).lstrip(os.path.sep)
        disk_path = os.path.join(BASE_DIR, clean_path)

        if not os.path.exists(disk_path) or os.path.isdir(disk_path):
            self.send_error(404, "Static file not found")
            return

        mime_type, _ = mimetypes.guess_type(disk_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        with open(disk_path, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def parse_post_data(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        parsed = urllib.parse.parse_qs(body)
        return {k: v[0] for k, v in parsed.items()}

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        alert_msg = query_params.get('msg', [None])[0]
        alert_type = query_params.get('type', ['info'])[0]

        if path.startswith('/static/'):
            self.serve_static(path)
            return

        user = self.get_session()

        if path == '/':
            if not user:
                self.redirect('/login')
            elif user['role'] == 'librarian':
                self.redirect('/librarian/dashboard')
            else:
                self.redirect('/student/dashboard')
            return

        # Unified Login & Registration routes
        if path in ['/login', '/login/portal', '/librarian/login', '/student/login', '/login/librarian', '/login/student']:
            if user:
                dest = '/librarian/dashboard' if user['role'] == 'librarian' else '/student/dashboard'
                self.redirect(dest)
                return
            self.render_html('login/login.html', {'alert_msg': alert_msg, 'alert_type': alert_type})
            return

        if path in ['/register', '/student/register', '/login/register']:
            if user:
                self.redirect('/')
                return
            self.render_html('student/register.html', {'alert_msg': alert_msg, 'alert_type': alert_type})
            return

        if path == '/logout':
            cookie = self.destroy_session()
            self.redirect('/login?msg=You+have+been+logged+out&type=info', cookie)
            return

        if not user:
            self.redirect('/login?msg=Please+sign+in+first&type=danger')
            return

        if path.startswith('/librarian'):
            if user['role'] != 'librarian':
                self.redirect('/student/dashboard?msg=Access+denied&type=danger')
                return

            if path == '/librarian/dashboard':
                stats = db.get_dashboard_stats()
                recent_txs = db.get_recent_transactions()
                
                rows_html = ""
                if not recent_txs:
                    rows_html = "<tr><td colspan='6' style='text-align:center; color:var(--text-dim);'>No recent circulation records found.</td></tr>"
                else:
                    for tx in recent_txs:
                        status_badge = f"<span class='badge badge-{tx['status']}'><span class='badge-dot'></span>{tx['status'].capitalize()}</span>"
                        fine_str = f"₱{tx['fine_amount']:.2f}" if tx['fine_amount'] > 0 else "-"
                        rows_html += f"""
                        <tr>
                            <td><strong>{tx['student_name']}</strong><br><small class='mono' style='color:var(--text-muted);'>{tx['user_id_number']}</small></td>
                            <td>{tx['book_title']}</td>
                            <td>{tx['borrow_date']}</td>
                            <td>{tx['due_date']}</td>
                            <td>{status_badge}</td>
                            <td style='color:{"#dc2626" if tx["fine_amount"] > 0 else "inherit"}; font-weight:600;'>{fine_str}</td>
                        </tr>
                        """

                context = {
                    'USER_NAME': user['full_name'],
                    'USER_ID_NUMBER': user['user_id_number'],
                    'TOTAL_BOOKS': stats['total_books'],
                    'BORROWED_COUNT': stats['borrowed_count'],
                    'OVERDUE_COUNT': stats['overdue_count'],
                    'RESERVATIONS_COUNT': stats['reservations_count'],
                    'RECENT_TRANSACTIONS_ROWS': rows_html,
                    'alert_msg': alert_msg,
                    'alert_type': alert_type
                }
                self.render_html('librarian/dashboard.html', context)
                return

            if path == '/librarian/books':
                books = db.get_all_books()
                categories = db.get_categories()

                cat_options = "".join([f"<option value='{c['id']}'>{c['name']}</option>" for c in categories])

                rows_html = ""
                if not books:
                    rows_html = "<tr><td colspan='6' style='text-align:center;'>No books in catalog yet.</td></tr>"
                else:
                    for b in books:
                        avail = b['available_copies']
                        total = b['total_copies']
                        avail_badge = f"<span class='badge badge-available'><span class='badge-dot'></span>{avail} of {total} Available</span>" if avail > 0 else "<span class='badge badge-overdue'><span class='badge-dot'></span>Out of Stock</span>"
                        
                        b_safe = {k: str(v).replace("'", "\\'") for k, v in b.items()}
                        edit_arg = f"{{id:{b['id']}, title:'{b_safe['title']}', author:'{b_safe['author']}', isbn:'{b_safe['isbn']}', category_id:{b['category_id']}, total_copies:{b['total_copies']}, shelf_location:'{b_safe['shelf_location']}', description:'{b_safe['description']}'}}"

                        rows_html += f"""
                        <tr>
                            <td><span class='mono' style='font-weight:600;'>{b['isbn']}</span></td>
                            <td><strong>{b['title']}</strong><br><small style='color:var(--text-muted);'>By {b['author']}</small></td>
                            <td><span class='book-badge-category'>{b['category_name']}</span></td>
                            <td>{avail_badge}</td>
                            <td><code>{b['shelf_location']}</code></td>
                            <td style='text-align: right;'>
                                <button type='button' class='btn btn-secondary btn-sm' onclick='openEditBookModal({edit_arg})'>Edit</button>
                                <form action='/librarian/books/delete' method='POST' style='display:inline;' onsubmit='return confirm(\"Delete this book title?\");'>
                                    <input type='hidden' name='book_id' value='{b['id']}'>
                                    <button type='submit' class='btn btn-danger btn-sm'>Delete</button>
                                </form>
                            </td>
                        </tr>
                        """

                context = {
                    'USER_NAME': user['full_name'],
                    'USER_ID_NUMBER': user['user_id_number'],
                    'BOOKS_TABLE_ROWS': rows_html,
                    'CATEGORY_OPTIONS': cat_options,
                    'alert_msg': alert_msg,
                    'alert_type': alert_type
                }
                self.render_html('librarian/books.html', context)
                return

            if path == '/librarian/circulation':
                borrows = db.get_active_borrows()
                reservations = db.get_all_reservations()
                students = db.get_students_directory()
                books = db.get_all_books()

                student_options = "".join([f"<option value='{s['id']}'>{s['full_name']} ({s['user_id_number']}) - {s['course_year']}</option>" for s in students])
                
                avail_books = [b for b in books if b['available_copies'] > 0]
                book_options = "".join([f"<option value='{b['id']}'>{b['title']} - {b['available_copies']} available (Shelf: {b['shelf_location']})</option>" for b in avail_books])
                if not book_options:
                    book_options = "<option disabled>No books currently available in stock</option>"

                borrows_html = ""
                if not borrows:
                    borrows_html = "<tr><td colspan='7' style='text-align:center;'>No active book loans at this moment.</td></tr>"
                else:
                    for br in borrows:
                        status_badge = f"<span class='badge badge-{br['status']}'><span class='badge-dot'></span>{br['status'].capitalize()}</span>"
                        fine_display = f"<strong style='color:#dc2626;'>₱{br['fine_amount']:.2f}</strong>" if br['fine_amount'] > 0 else "₱0.00"

                        borrows_html += f"""
                        <tr>
                            <td><strong>{br['student_name']}</strong><br><small class='mono' style='color:var(--text-muted);'>{br['user_id_number']}</small></td>
                            <td><strong>{br['book_title']}</strong><br><small class='mono' style='color:var(--text-muted);'>ISBN: {br['isbn']}</small></td>
                            <td>{br['borrow_date']}</td>
                            <td><strong>{br['due_date']}</strong></td>
                            <td>{status_badge}</td>
                            <td>{fine_display}</td>
                            <td style='text-align: right;'>
                                <form action='/librarian/circulation/return' method='POST' style='display:inline;'>
                                    <input type='hidden' name='record_id' value='{br['id']}'>
                                    <button type='submit' class='btn btn-success btn-sm'>Process Return</button>
                                </form>
                            </td>
                        </tr>
                        """

                reservations_html = ""
                if not reservations:
                    reservations_html = "<tr><td colspan='6' style='text-align:center;'>No pending student book reservations.</td></tr>"
                else:
                    for r in reservations:
                        stock_tag = f"<span class='badge badge-available'>{r['available_copies']} in stock</span>" if r['available_copies'] > 0 else "<span class='badge badge-overdue'>0 in stock</span>"
                        reservations_html += f"""
                        <tr>
                            <td><strong>{r['student_name']}</strong> ({r['user_id_number']})</td>
                            <td><strong>{r['book_title']}</strong></td>
                            <td>{stock_tag}</td>
                            <td>{r['reservation_date']}</td>
                            <td><span class='badge badge-pending'><span class='badge-dot'></span>Pending Review</span></td>
                            <td style='text-align: right;'>
                                <form action='/librarian/circulation/issue' method='POST' style='display:inline;'>
                                    <input type='hidden' name='user_id' value='{r['student_id']}'>
                                    <input type='hidden' name='book_id' value='{r['book_id']}'>
                                    <input type='hidden' name='loan_days' value='7'>
                                    <button type='submit' class='btn btn-primary btn-sm' {'disabled' if r['available_copies'] <= 0 else ''}>Issue Book</button>
                                </form>
                                <form action='/librarian/circulation/cancel_reserve' method='POST' style='display:inline;'>
                                    <input type='hidden' name='reservation_id' value='{r['id']}'>
                                    <button type='submit' class='btn btn-secondary btn-sm'>Reject</button>
                                </form>
                            </td>
                        </tr>
                        """

                context = {
                    'USER_NAME': user['full_name'],
                    'USER_ID_NUMBER': user['user_id_number'],
                    'ACTIVE_BORROWS_ROWS': borrows_html,
                    'RESERVATIONS_ROWS': reservations_html,
                    'STUDENT_OPTIONS': student_options,
                    'AVAILABLE_BOOK_OPTIONS': book_options,
                    'alert_msg': alert_msg,
                    'alert_type': alert_type
                }
                self.render_html('librarian/circulation.html', context)
                return

            if path == '/librarian/students':
                students = db.get_students_directory()
                rows_html = ""
                if not students:
                    rows_html = "<tr><td colspan='6' style='text-align:center;'>No students registered yet.</td></tr>"
                else:
                    for s in students:
                        standing_badge = "<span class='badge badge-overdue'>Has Overdue Books</span>" if s['overdue_count'] > 0 else "<span class='badge badge-available'>Good Standing</span>"
                        rows_html += f"""
                        <tr>
                            <td><span class='mono' style='font-weight:600;'>{s['user_id_number']}</span></td>
                            <td><strong>{s['full_name']}</strong></td>
                            <td>{s['course_year']}</td>
                            <td>{s['email']}<br><small style='color:var(--text-muted);'>{s['contact_number'] or 'No contact'}</small></td>
                            <td><strong>{s['active_loans']}</strong> book(s)</td>
                            <td>{standing_badge}</td>
                        </tr>
                        """

                context = {
                    'USER_NAME': user['full_name'],
                    'USER_ID_NUMBER': user['user_id_number'],
                    'STUDENTS_TABLE_ROWS': rows_html,
                    'alert_msg': alert_msg,
                    'alert_type': alert_type
                }
                self.render_html('librarian/students.html', context)
                return

        if path.startswith('/student'):
            if user['role'] != 'student':
                self.redirect('/librarian/dashboard?msg=Access+denied&type=danger')
                return

            if path == '/student/dashboard':
                borrows = db.get_student_borrow_records(user['id'])
                reservations = db.get_student_reservations(user['id'])

                borrowed_active = [b for b in borrows if b['return_date'] is None]
                overdue_active = [b for b in borrowed_active if b['status'] == 'overdue']
                pending_res = [r for r in reservations if r['status'] == 'pending']
                total_fines = sum([float(b['fine_amount']) for b in borrowed_active])

                borrows_html = ""
                if not borrowed_active:
                    borrows_html = "<tr><td colspan='6' style='text-align:center; color:var(--text-dim);'>You have no books currently checked out.</td></tr>"
                else:
                    for b in borrowed_active:
                        if b['status'] == 'overdue':
                            badge = f"<span class='badge badge-overdue'><span class='badge-dot'></span>Overdue</span>"
                        else:
                            days = b['days_left']
                            badge = f"<span class='badge badge-available'><span class='badge-dot'></span>{days} days remaining</span>" if days > 0 else "<span class='badge badge-pending'>Due Today</span>"

                        fine_text = f"<strong style='color:#dc2626;'>₱{b['fine_amount']:.2f}</strong>" if b['fine_amount'] > 0 else "₱0.00"

                        borrows_html += f"""
                        <tr>
                            <td><strong>{b['book_title']}</strong><br><small class='mono' style='color:var(--text-muted);'>ISBN: {b['isbn']}</small></td>
                            <td>{b['author']}</td>
                            <td>{b['borrow_date']}</td>
                            <td><strong>{b['due_date']}</strong></td>
                            <td>{badge}</td>
                            <td>{fine_text}</td>
                        </tr>
                        """

                reservations_html = ""
                if not reservations:
                    reservations_html = "<tr><td colspan='5' style='text-align:center; color:var(--text-dim);'>You have no book reservations.</td></tr>"
                else:
                    for r in reservations:
                        status_tag = f"<span class='badge badge-pending'><span class='badge-dot'></span>{r['status'].capitalize()}</span>"
                        cancel_btn = ""
                        if r['status'] == 'pending':
                            cancel_btn = f"""
                            <form action='/student/cancel_reserve' method='POST' style='display:inline;'>
                                <input type='hidden' name='reservation_id' value='{r['id']}'>
                                <button type='submit' class='btn btn-danger btn-sm'>Cancel Hold</button>
                            </form>
                            """

                        reservations_html += f"""
                        <tr>
                            <td><strong>{r['book_title']}</strong><br><small style='color:var(--text-muted);'>By {r['author']}</small></td>
                            <td><code>{r['shelf_location']}</code></td>
                            <td>{r['reservation_date']}</td>
                            <td>{status_tag}</td>
                            <td style='text-align: right;'>{cancel_btn}</td>
                        </tr>
                        """

                context = {
                    'USER_NAME': user['full_name'],
                    'USER_ID_NUMBER': user['user_id_number'],
                    'USER_COURSE': user.get('course_year', 'Student Member'),
                    'BORROWED_COUNT': len(borrowed_active),
                    'OVERDUE_COUNT': len(overdue_active),
                    'RESERVATIONS_COUNT': len(pending_res),
                    'TOTAL_FINE': f"{total_fines:.2f}",
                    'FINE_COLOR': '#dc2626' if total_fines > 0 else '#059669',
                    'STUDENT_BORROWED_ROWS': borrows_html,
                    'STUDENT_RESERVATIONS_ROWS': reservations_html,
                    'alert_msg': alert_msg,
                    'alert_type': alert_type
                }
                self.render_html('student/dashboard.html', context)
                return

            if path == '/student/catalog':
                books = db.get_all_books()
                categories = db.get_categories()

                cat_filter_opts = "".join([f"<option value='{c['name'].lower()}'>{c['name']}</option>" for c in categories])

                cards_html = ""
                for b in books:
                    avail = b['available_copies']
                    total = b['total_copies']
                    is_avail = avail > 0
                    
                    status_pill = f"<span class='badge badge-available'><span class='badge-dot'></span>{avail} Available</span>" if is_avail else "<span class='badge badge-overdue'><span class='badge-dot'></span>Out of Stock</span>"

                    safe_title = b['title'].replace("'", "\\'")
                    safe_author = b['author'].replace("'", "\\'")
                    safe_shelf = b['shelf_location'].replace("'", "\\'")

                    action_btn = f"""
                    <button type='button' class='btn btn-primary btn-sm' onclick='promptReserve({b['id']}, "{safe_title}", "{safe_author}", "{safe_shelf}")'>
                        Reserve Copy
                    </button>
                    """ if is_avail else "<button class='btn btn-secondary btn-sm' disabled>Unavailable</button>"

                    cards_html += f"""
                    <div class='book-card' data-title='{b['title']}' data-author='{b['author']}' data-isbn='{b['isbn']}' data-category='{b['category_name'].lower()}'>
                        <div class='book-header'>
                            <span class='book-badge-category'>{b['category_name']}</span>
                            {status_pill}
                        </div>
                        <h3 class='book-title'>{b['title']}</h3>
                        <p class='book-author'>By {b['author']}</p>
                        <div class='book-details-list'>
                            <div class='book-detail-item'><span>ISBN:</span><code class='mono'>{b['isbn']}</code></div>
                            <div class='book-detail-item'><span>Shelf:</span><code>{b['shelf_location']}</code></div>
                            <div class='book-detail-item'><span>Copies:</span><span>{avail} of {total} in library</span></div>
                        </div>
                        <div class='book-footer'>
                            <span style='font-size:12px; color:var(--text-dim);'>Ref #{b['id']}</span>
                            {action_btn}
                        </div>
                    </div>
                    """

                context = {
                    'USER_NAME': user['full_name'],
                    'USER_ID_NUMBER': user['user_id_number'],
                    'CATEGORY_FILTER_OPTIONS': cat_filter_opts,
                    'CATALOG_BOOK_CARDS': cards_html,
                    'alert_msg': alert_msg,
                    'alert_type': alert_type
                }
                self.render_html('student/catalog.html', context)
                return

        self.send_error(404, "Page not found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        post_data = self.parse_post_data()

        if path in ['/login', '/librarian/login', '/student/login', '/login/librarian', '/login/student']:
            identifier = post_data.get('identifier', '').strip()
            password = post_data.get('password', '').strip()

            if not identifier or not password:
                self.redirect('/login?msg=Please+enter+both+ID%2FEmail+and+password&type=danger')
                return

            try:
                # Automatic role detection from database
                user = db.authenticate_user(identifier, password)
                if user:
                    cookie = self.create_session(user)
                    dest = '/librarian/dashboard' if user['role'] == 'librarian' else '/student/dashboard'
                    self.redirect(dest, cookie)
                else:
                    self.redirect('/login?msg=Invalid+ID%2FEmail+or+password!&type=danger')
            except Exception as e:
                self.redirect(f'/login?msg=Database+error:+{urllib.parse.quote(str(e))}&type=danger')
            return

        if path in ['/register', '/student/register', '/login/register']:
            full_name = post_data.get('full_name', '').strip()
            user_id_number = post_data.get('user_id_number', '').strip()
            email = post_data.get('email', '').strip()
            course_year = post_data.get('course_year', '').strip()
            contact_number = post_data.get('contact_number', '').strip()
            password = post_data.get('password', '').strip()
            confirm_pwd = post_data.get('confirm_password', '').strip()

            back_url = '/student/register' if 'student' in path else '/register'
            if password != confirm_pwd:
                self.redirect(f'{back_url}?msg=Passwords+do+not+match!&type=danger')
                return

            success, msg = db.register_student(user_id_number, full_name, email, password, course_year, contact_number)
            if success:
                self.redirect('/student/login?msg=Registration+successful!+Please+log+in.&type=success')
            else:
                self.redirect(f'{back_url}?msg={urllib.parse.quote(msg)}&type=danger')
            return

        user = self.get_session()
        if not user:
            self.redirect('/login?msg=Session+expired.+Please+sign+in+again.&type=danger')
            return

        if user['role'] == 'librarian':
            if path == '/librarian/books/add':
                title = post_data.get('title', '').strip()
                author = post_data.get('author', '').strip()
                isbn = post_data.get('isbn', '').strip()
                category_id = post_data.get('category_id')
                total_copies = post_data.get('total_copies', 1)
                shelf_location = post_data.get('shelf_location', 'Shelf A-1').strip()
                description = post_data.get('description', '').strip()

                success, msg = db.add_book(title, author, isbn, category_id, total_copies, shelf_location, description)
                msg_type = 'success' if success else 'danger'
                self.redirect(f'/librarian/books?msg={urllib.parse.quote(msg)}&type={msg_type}')
                return

            if path == '/librarian/books/edit':
                book_id = post_data.get('book_id')
                title = post_data.get('title', '').strip()
                author = post_data.get('author', '').strip()
                isbn = post_data.get('isbn', '').strip()
                category_id = post_data.get('category_id')
                total_copies = post_data.get('total_copies', 1)
                shelf_location = post_data.get('shelf_location', '').strip()
                description = post_data.get('description', '').strip()

                success, msg = db.update_book(book_id, title, author, isbn, category_id, total_copies, shelf_location, description)
                msg_type = 'success' if success else 'danger'
                self.redirect(f'/librarian/books?msg={urllib.parse.quote(msg)}&type={msg_type}')
                return

            if path == '/librarian/books/delete':
                book_id = post_data.get('book_id')
                success, msg = db.delete_book(book_id)
                msg_type = 'success' if success else 'danger'
                self.redirect(f'/librarian/books?msg={urllib.parse.quote(msg)}&type={msg_type}')
                return

            if path == '/librarian/circulation/issue':
                user_id = post_data.get('user_id')
                book_id = post_data.get('book_id')
                loan_days = post_data.get('loan_days', 7)

                success, msg = db.issue_book(user_id, book_id, loan_days)
                msg_type = 'success' if success else 'danger'
                self.redirect(f'/librarian/circulation?msg={urllib.parse.quote(msg)}&type={msg_type}')
                return

            if path == '/librarian/circulation/return':
                record_id = post_data.get('record_id')
                success, msg = db.process_return(record_id)
                msg_type = 'success' if success else 'danger'
                self.redirect(f'/librarian/circulation?msg={urllib.parse.quote(msg)}&type={msg_type}')
                return

            if path == '/librarian/circulation/cancel_reserve':
                reservation_id = post_data.get('reservation_id')
                db.cancel_reservation(reservation_id)
                self.redirect('/librarian/circulation?msg=Reservation+cancelled&type=info')
                return

        if user['role'] == 'student':
            if path == '/student/reserve':
                book_id = post_data.get('book_id')
                success, msg = db.reserve_book(user['id'], book_id)
                msg_type = 'success' if success else 'danger'
                self.redirect(f'/student/dashboard?msg={urllib.parse.quote(msg)}&type={msg_type}')
                return

            if path == '/student/cancel_reserve':
                reservation_id = post_data.get('reservation_id')
                db.cancel_reservation(reservation_id, user_id=user['id'])
                self.redirect('/student/dashboard?msg=Reservation+hold+cancelled&type=info')
                return

        self.send_error(400, "Bad Request")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server():
    db.initialize_database()

    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, LibraryRequestHandler)
    print(f"Library Server running on http://localhost:{PORT}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    run_server()
