import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import db


def main():
    print("=" * 45)
    print("   Create New Librarian / Staff Account")
    print("=" * 45)

    user_id = input("Librarian ID (e.g. LIB-002 or 2026-101): ").strip()
    name = input("Full Name (e.g. Junar Abcede): ").strip()
    email = input("Email (e.g. junar@tcc.edu.ph): ").strip()
    password = input("Password: ").strip()

    if not user_id or not name or not email or not password:
        print("\n[!] Error: All fields are required.")
        return

    success, msg = db.create_librarian(user_id, name, email, password)
    print()
    if success:
        print(f"[✓] {msg}")
        print(f"[✓] You can now log in at: http://localhost:8080/librarian/login")
        print(f"    Identifier: {user_id} or {email}")
    else:
        print(f"[!] {msg}")


if __name__ == '__main__':
    main()
