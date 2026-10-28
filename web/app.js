// State variables
let currentUser = null;
let cachedBooks = [];
let selectedStudentBookId = null;
let selectedAdminBookId = null;

// Wait for PyWebView API or provide local mock for testing in standalone browser
function getApi() {
  if (window.pywebview && window.pywebview.api) {
    return window.pywebview.api;
  }
  return null;
}

// Toast notification helper
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  let iconSvg = "";
  if (type === "success") {
    iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>`;
  } else if (type === "error") {
    iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`;
  } else {
    iconSvg = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
  }

  toast.innerHTML = `
    ${iconSvg}
    <div class="toast-msg">${message.replace(/\n/g, '<br>')}</div>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Modal management
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.style.display = "flex";
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.style.display = "none";
}

// Quick demo login fill
function quickFill(username, password) {
  document.getElementById("login-username").value = username;
  document.getElementById("login-password").value = password;
}

// Navigation between screens
function showView(viewName) {
  document.getElementById("view-login").style.display = viewName === "login" ? "flex" : "none";
  document.getElementById("view-student").style.display = viewName === "student" ? "flex" : "none";
  document.getElementById("view-admin").style.display = viewName === "admin" ? "flex" : "none";
  document.getElementById("app-header").style.display = viewName === "login" ? "none" : "flex";

  if (currentUser) {
    document.getElementById("header-user-name").textContent = currentUser.name;
    document.getElementById("header-user-avatar").textContent = currentUser.name.charAt(0).toUpperCase();
    document.getElementById("header-user-role").textContent = `(${currentUser.course || currentUser.role})`;

    if (currentUser.role === "librarian") {
      document.getElementById("header-portal-title").textContent = "Librarian Administrative Desk";
      document.getElementById("header-sub-title").textContent = "Inventory Management & Real-time Circulation";
    } else {
      document.getElementById("header-portal-title").textContent = "Student Library Portal";
      document.getElementById("header-sub-title").textContent = "Online Book Catalog & Personal Member Loans";
    }
  }
}

// ----------------- AUTHENTICATION -----------------
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();

  const api = getApi();
  if (!api) {
    showToast("Waiting for Python backend connection...", "error");
    return;
  }

  try {
    const res = await api.login(username, password);
    if (res.success) {
      currentUser = res.user;
      showToast(`Welcome back, ${currentUser.name}!`, "success");
      if (currentUser.role === "librarian") {
        showView("admin");
        loadAdminDashboard();
      } else {
        showView("student");
        loadStudentCatalog();
      }
    } else {
      showToast(res.message || "Invalid credentials", "error");
    }
  } catch (err) {
    showToast("Login error: " + err, "error");
  }
});

document.getElementById("btn-logout").addEventListener("click", async () => {
  const api = getApi();
  if (api) await api.logout();
  currentUser = null;
  selectedStudentBookId = null;
  selectedAdminBookId = null;
  document.getElementById("login-username").value = "";
  document.getElementById("login-password").value = "";
  showView("login");
  showToast("Logged out successfully.", "info");
});

document.getElementById("btn-show-register").addEventListener("click", () => {
  openModal("modal-register");
});

document.getElementById("form-register").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("reg-name").value.trim();
  const studentId = document.getElementById("reg-id").value.trim();
  const password = document.getElementById("reg-password").value.trim();
  const course = document.getElementById("reg-course").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const contact = document.getElementById("reg-contact").value.trim();

  const api = getApi();
  if (!api) return;

  try {
    const res = await api.register(name, studentId, password, email, course, contact);
    if (res.success) {
      closeModal("modal-register");
      document.getElementById("form-register").reset();
      quickFill(studentId, password);
      showToast(res.message, "success");
    } else {
      showToast(res.message, "error");
    }
  } catch (err) {
    showToast("Registration error: " + err, "error");
  }
});

// ----------------- STUDENT PORTAL -----------------
async function loadStudentCatalog(query = "") {
  const api = getApi();
  if (!api) return;

  try {
    cachedBooks = await api.get_books(query);
    renderStudentCatalog(cachedBooks);
  } catch (err) {
    showToast("Failed to load catalog: " + err, "error");
  }
}

function renderStudentCatalog(books) {
  const tbody = document.getElementById("student-books-tbody");
  tbody.innerHTML = "";

  if (books.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 24px;">No books matching your search query.</td></tr>`;
    return;
  }

  books.forEach((b) => {
    const tr = document.createElement("tr");
    if (selectedStudentBookId === b.id) tr.classList.add("selected");

    tr.onclick = () => {
      document.querySelectorAll("#student-books-tbody tr").forEach((r) => r.classList.remove("selected"));
      tr.classList.add("selected");
      selectedStudentBookId = b.id;
    };

    const isAvailable = b.copies > 0;
    const copiesBadge = isAvailable
      ? `<span class="badge badge-stock">${b.copies} available</span>`
      : `<span class="badge badge-out">Out of stock (0)</span>`;

    tr.innerHTML = `
      <td style="font-weight: bold; color: var(--text-muted);">${b.id}</td>
      <td style="font-weight: 600;">${b.title}</td>
      <td>${b.author}</td>
      <td><span class="badge" style="background: #f1f5f9; color: #334155;">${b.category}</span></td>
      <td><span class="badge badge-shelf">${b.shelf || "Main Shelf"}</span></td>
      <td style="text-align: center;">${copiesBadge}</td>
      <td style="text-align: right;">
        ${isAvailable 
          ? `<button class="btn btn-primary" style="padding: 4px 10px; font-size: 0.78rem;" onclick="event.stopPropagation(); directBorrow(${b.id})">Borrow</button>`
          : `<button class="btn btn-outline" style="padding: 4px 10px; font-size: 0.78rem;" onclick="event.stopPropagation(); directReserve(${b.id})">Reserve</button>`
        }
      </td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("student-search-input").addEventListener("input", (e) => {
  loadStudentCatalog(e.target.value);
});

document.getElementById("student-search-reset").addEventListener("click", () => {
  document.getElementById("student-search-input").value = "";
  loadStudentCatalog("");
});

async function directBorrow(bookId) {
  const api = getApi();
  if (!api) return;

  const res = await api.borrow_book(bookId);
  if (res.success) {
    showToast(res.message, "success");
    loadStudentCatalog(document.getElementById("student-search-input").value);
  } else {
    showToast(res.message, "error");
  }
}

async function directReserve(bookId) {
  const api = getApi();
  if (!api) return;

  const res = await api.reserve_book(bookId);
  if (res.success) {
    showToast(res.message, "success");
  } else {
    showToast(res.message, "error");
  }
}

document.getElementById("btn-student-borrow").addEventListener("click", () => {
  if (!selectedStudentBookId) {
    showToast("Please select a book row from the catalog first.", "info");
    return;
  }
  directBorrow(selectedStudentBookId);
});

document.getElementById("btn-student-reserve").addEventListener("click", () => {
  if (!selectedStudentBookId) {
    showToast("Please select a book row from the catalog first.", "info");
    return;
  }
  directReserve(selectedStudentBookId);
});

// Student Loans & Returns Modal
document.getElementById("btn-student-my-loans").addEventListener("click", async () => {
  const api = getApi();
  if (!api) return;

  try {
    const loans = await api.get_my_borrow_records();
    renderStudentLoans(loans);
    openModal("modal-student-loans");
  } catch (err) {
    showToast("Error loading loans: " + err, "error");
  }
});

function renderStudentLoans(loans) {
  const tbody = document.getElementById("student-loans-tbody");
  tbody.innerHTML = "";

  if (loans.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;">You currently have no active or past loans.</td></tr>`;
    return;
  }

  loans.forEach((l) => {
    const tr = document.createElement("tr");
    const isReturned = l.status === "Returned";
    const statusBadge = isReturned
      ? `<span class="badge badge-status-returned">Returned</span>`
      : `<span class="badge badge-status-borrowed">Active Loan</span>`;

    const fineText = l.fine > 0 ? `<span style="color: #dc2626; font-weight: bold;">PHP ${l.fine.toFixed(2)}</span>` : `<span style="color: #10b981;">PHP 0.00</span>`;

    tr.innerHTML = `
      <td style="font-weight: 600;">${l.book_title}</td>
      <td>${l.borrow_date}</td>
      <td>${l.due_date}</td>
      <td>${statusBadge}</td>
      <td>${fineText}</td>
      <td>
        ${!isReturned 
          ? `<button class="btn btn-teal" style="padding: 4px 10px; font-size: 0.78rem;" onclick="processStudentReturn(${l.record_id})">Return Book</button>`
          : `<span style="font-size: 0.8rem; color: var(--text-muted);">Returned on ${l.return_date}</span>`
        }
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function processStudentReturn(recordId) {
  const api = getApi();
  if (!api) return;

  try {
    const res = await api.return_book(recordId);
    if (res.success) {
      showToast(res.message, res.is_overdue ? "error" : "success");
      const updatedLoans = await api.get_my_borrow_records();
      renderStudentLoans(updatedLoans);
      loadStudentCatalog();
    } else {
      showToast(res.message, "error");
    }
  } catch (err) {
    showToast("Return failed: " + err, "error");
  }
}

// ----------------- LIBRARIAN ADMIN DESK -----------------
async function loadAdminDashboard() {
  const api = getApi();
  if (!api) return;

  try {
    // 1. Load metrics
    const metrics = await api.get_admin_metrics();
    document.getElementById("metric-titles").textContent = metrics.total_titles || 0;
    document.getElementById("metric-borrowed").textContent = metrics.active_borrowed || 0;
    document.getElementById("metric-overdue").textContent = metrics.overdue_books || 0;
    document.getElementById("metric-holds").textContent = metrics.pending_reservations || 0;

    // 2. Load inventory
    loadAdminInventory();
  } catch (err) {
    showToast("Failed to refresh admin dashboard: " + err, "error");
  }
}

async function loadAdminInventory(query = "") {
  const api = getApi();
  if (!api) return;

  const books = await api.get_books(query);
  const tbody = document.getElementById("admin-inventory-tbody");
  tbody.innerHTML = "";

  books.forEach((b) => {
    const tr = document.createElement("tr");
    if (selectedAdminBookId === b.id) tr.classList.add("selected");

    tr.onclick = () => {
      document.querySelectorAll("#admin-inventory-tbody tr").forEach((r) => r.classList.remove("selected"));
      tr.classList.add("selected");
      selectedAdminBookId = b.id;
    };

    const copiesBadge = b.copies > 0
      ? `<span class="badge badge-stock">${b.copies}</span>`
      : `<span class="badge badge-out">0</span>`;

    tr.innerHTML = `
      <td style="font-weight: bold; color: var(--text-muted);">${b.id}</td>
      <td style="font-weight: 600;">${b.title}</td>
      <td>${b.author}</td>
      <td><span class="badge" style="background: #f1f5f9; color: #334155;">${b.category}</span></td>
      <td><span class="badge badge-shelf">${b.shelf || "Main Shelf"}</span></td>
      <td style="text-align: center;">${copiesBadge}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("admin-inventory-search").addEventListener("input", (e) => {
  loadAdminInventory(e.target.value);
});

// Admin Tabs Navigation
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach((p) => (p.style.display = "none"));

    btn.classList.add("active");
    const targetId = btn.getAttribute("data-tab");
    document.getElementById(targetId).style.display = "block";

    if (targetId === "tab-inventory") loadAdminInventory();
    if (targetId === "tab-circulation") loadAdminCirculation();
    if (targetId === "tab-students") loadAdminStudents();
    if (targetId === "tab-reservations") loadAdminReservations();
  });
});

// Admin Add Book
document.getElementById("btn-admin-add-book").addEventListener("click", () => {
  openModal("modal-add-book");
});

document.getElementById("form-add-book").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("book-title").value.trim();
  const author = document.getElementById("book-author").value.trim();
  const category = document.getElementById("book-category").value.trim();
  const shelf = document.getElementById("book-shelf").value.trim();
  const copies = parseInt(document.getElementById("book-copies").value) || 1;

  const api = getApi();
  if (!api) return;

  const res = await api.add_book(title, author, category, shelf, copies);
  if (res.success) {
    showToast(res.message, "success");
    closeModal("modal-add-book");
    document.getElementById("form-add-book").reset();
    loadAdminDashboard();
  } else {
    showToast(res.message, "error");
  }
});

// Admin Restock Book
document.getElementById("btn-admin-restock").addEventListener("click", async () => {
  if (!selectedAdminBookId) {
    showToast("Please select a book row from the inventory table first.", "info");
    return;
  }
  const api = getApi();
  const books = await api.get_books();
  const book = books.find((b) => b.id === selectedAdminBookId);
  if (!book) return;

  document.getElementById("restock-book-info").textContent = `Restocking '${book.title}' (Current copies: ${book.copies})`;
  openModal("modal-restock");
});

document.getElementById("form-restock").addEventListener("submit", async (e) => {
  e.preventDefault();
  const qty = parseInt(document.getElementById("restock-qty").value) || 1;
  const api = getApi();
  if (!api) return;

  const res = await api.restock_book(selectedAdminBookId, qty);
  if (res.success) {
    showToast(res.message, "success");
    closeModal("modal-restock");
    loadAdminDashboard();
  } else {
    showToast(res.message, "error");
  }
});

// Admin Delete Book
document.getElementById("btn-admin-delete-book").addEventListener("click", async () => {
  if (!selectedAdminBookId) {
    showToast("Please select a book to delete.", "info");
    return;
  }

  const api = getApi();
  const books = await api.get_books();
  const book = books.find((b) => b.id === selectedAdminBookId);
  if (!book) return;

  if (confirm(`Are you sure you want to delete '${book.title}' from inventory?`)) {
    const res = await api.delete_book(selectedAdminBookId);
    if (res.success) {
      showToast(res.message, "success");
      selectedAdminBookId = null;
      loadAdminDashboard();
    } else {
      showToast(res.message, "error");
    }
  }
});

// Admin Circulation Tab
async function loadAdminCirculation() {
  const api = getApi();
  if (!api) return;

  const records = await api.get_all_borrow_records();
  const tbody = document.getElementById("admin-loans-tbody");
  tbody.innerHTML = "";

  if (records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No loan records found.</td></tr>`;
    return;
  }

  records.forEach((r) => {
    const tr = document.createElement("tr");
    const isReturned = r.status === "Returned";
    const statusBadge = isReturned
      ? `<span class="badge badge-status-returned">Returned</span>`
      : `<span class="badge badge-status-borrowed">Active Loan</span>`;

    const fineDisplay = r.fine > 0
      ? `<span style="color: #dc2626; font-weight: bold;">PHP ${r.fine.toFixed(2)}</span>`
      : `<span style="color: #10b981;">PHP 0.00</span>`;

    tr.innerHTML = `
      <td style="font-weight: bold; color: var(--text-muted);">#${r.record_id}</td>
      <td style="font-family: monospace;">${r.username}</td>
      <td style="font-weight: 600;">${r.name}</td>
      <td>${r.book_title}</td>
      <td>${r.borrow_date}</td>
      <td>${r.due_date}</td>
      <td>${statusBadge}</td>
      <td>${fineDisplay}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Admin Issue Book Modal
document.getElementById("btn-admin-issue-book").addEventListener("click", async () => {
  const api = getApi();
  if (!api) return;

  const [books, students] = await Promise.all([api.get_books(), api.get_all_students()]);

  const bookSelect = document.getElementById("issue-book-select");
  bookSelect.innerHTML = books
    .filter((b) => b.copies > 0)
    .map((b) => `<option value="${b.id}">${b.title} (${b.copies} available)</option>`)
    .join("");

  const studentSelect = document.getElementById("issue-student-select");
  studentSelect.innerHTML = students
    .map((s) => `<option value="${s.username}">${s.name} (${s.username} - ${s.course || 'Student'})</option>`)
    .join("");

  if (books.filter((b) => b.copies > 0).length === 0) {
    showToast("No books currently in stock to issue.", "error");
    return;
  }

  openModal("modal-issue");
});

document.getElementById("form-issue").addEventListener("submit", async (e) => {
  e.preventDefault();
  const bookId = parseInt(document.getElementById("issue-book-select").value);
  const studentId = document.getElementById("issue-student-select").value;

  const api = getApi();
  if (!api) return;

  const res = await api.issue_book(studentId, bookId);
  if (res.success) {
    showToast(res.message, "success");
    closeModal("modal-issue");
    loadAdminDashboard();
    loadAdminCirculation();
  } else {
    showToast(res.message, "error");
  }
});

// Admin Return Book Modal
document.getElementById("btn-admin-return-book").addEventListener("click", async () => {
  const api = getApi();
  if (!api) return;

  const records = await api.get_all_borrow_records();
  const activeRecords = records.filter((r) => r.status === "Borrowed");

  const tbody = document.getElementById("return-admin-tbody");
  tbody.innerHTML = "";

  if (activeRecords.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 18px;">No active borrowed books to return.</td></tr>`;
  } else {
    activeRecords.forEach((r) => {
      const tr = document.createElement("tr");
      const fineText = r.fine > 0 ? `<span style="color: #dc2626; font-weight: bold;">PHP ${r.fine.toFixed(2)}</span>` : `<span style="color: #10b981;">PHP 0.00</span>`;

      tr.innerHTML = `
        <td style="font-weight: bold;">#${r.record_id}</td>
        <td>${r.name} (${r.username})</td>
        <td style="font-weight: 600;">${r.book_title}</td>
        <td>${r.due_date}</td>
        <td><span class="badge badge-status-borrowed">Borrowed</span></td>
        <td>${fineText}</td>
        <td>
          <button class="btn btn-success" style="padding: 4px 10px; font-size: 0.78rem;" onclick="adminProcessReturn(${r.record_id})">
            Accept Return
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  openModal("modal-return-admin");
});

async function adminProcessReturn(recordId) {
  const api = getApi();
  if (!api) return;

  const res = await api.return_book(recordId);
  if (res.success) {
    showToast(res.message, res.is_overdue ? "error" : "success");
    closeModal("modal-return-admin");
    loadAdminDashboard();
    loadAdminCirculation();
  } else {
    showToast(res.message, "error");
  }
}

// Admin Students Tab
async function loadAdminStudents() {
  const api = getApi();
  if (!api) return;

  const students = await api.get_all_students();
  const tbody = document.getElementById("admin-students-tbody");
  tbody.innerHTML = "";

  students.forEach((s) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-family: monospace; font-weight: bold;">${s.username}</td>
      <td style="font-weight: 600;">${s.name}</td>
      <td>${s.course || 'Student'}</td>
      <td>${s.contact || 'N/A'}</td>
      <td>${s.email || 'N/A'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Admin Reservations Tab
async function loadAdminReservations() {
  const api = getApi();
  if (!api) return;

  const reservations = await api.get_all_reservations();
  const tbody = document.getElementById("admin-reservations-tbody");
  tbody.innerHTML = "";

  if (reservations.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;">No pending holds or reservations.</td></tr>`;
    return;
  }

  reservations.forEach((res) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="font-weight: bold;">#${res.id}</td>
      <td style="font-family: monospace;">${res.username}</td>
      <td style="font-weight: 600;">${res.name}</td>
      <td>${res.book_title}</td>
      <td>${res.date_requested}</td>
      <td><span class="badge badge-status-pending">${res.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Initialize view
window.addEventListener("DOMContentLoaded", () => {
  showView("login");
});

