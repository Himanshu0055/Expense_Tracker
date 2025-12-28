import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import hashlib
import matplotlib.pyplot as plt

# ================= CONFIG =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
DB = "expenses.db"

# ================= DATABASE =================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        category TEXT,
        amount REAL,
        note TEXT
    )""")

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users VALUES(NULL,?,?,?)",
                    ("Himanshu", hash_password("0055"), "admin"))
        cur.execute("INSERT INTO users VALUES(NULL,?,?,?)",
                    ("user", hash_password("user123"), "user"))

    conn.commit()
    conn.close()

init_db()

def authenticate(u, p):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, role FROM users WHERE username=? AND password=?",
        (u, hash_password(p))
    )
    r = cur.fetchone()
    conn.close()
    return r

# ================= MAIN APP =================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Expense Tracker")
        self.geometry("1000x650")
        self.user_id = None
        self.role = None
        self.show_login()

    # ---------- LOGIN ----------
    def show_login(self):
        self.clear()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)

        ctk.CTkLabel(frame, text="🔐 Login",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.u = ctk.CTkEntry(frame, placeholder_text="Username")
        self.p = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        self.u.pack(pady=10)
        self.p.pack(pady=10)

        ctk.CTkButton(frame, text="Login",
                      command=self.login).pack(pady=15)

    def login(self):
        user = authenticate(self.u.get(), self.p.get())
        if not user:
            messagebox.showerror("Error", "Invalid credentials")
            return

        self.user_id, self.role = user
        self.show_dashboard()

    # ---------- DASHBOARD ----------
    def show_dashboard(self):
        self.clear()
        self.selected_expense_id = ctk.IntVar(value=0)

        ctk.CTkLabel(
            self, text="💰 Expense Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)

        form = ctk.CTkFrame(self)
        form.pack(pady=10)

        self.e_date = ctk.CTkEntry(form, placeholder_text="Date (YYYY-MM-DD)", width=160)
        self.e_cat = ctk.CTkEntry(form, placeholder_text="Category", width=160)
        self.e_amt = ctk.CTkEntry(form, placeholder_text="Amount", width=160)
        self.e_note = ctk.CTkEntry(form, placeholder_text="Note", width=160)

        self.e_date.grid(row=0, column=0, padx=5, pady=5)
        self.e_cat.grid(row=0, column=1, padx=5, pady=5)
        self.e_amt.grid(row=0, column=2, padx=5, pady=5)
        self.e_note.grid(row=0, column=3, padx=5, pady=5)

        btns = ctk.CTkFrame(self)
        btns.pack(pady=10)

        if self.role == "admin":
            ctk.CTkButton(btns, text="Add Expense",
                          command=self.add).pack(side="left", padx=5)
            ctk.CTkButton(btns, text="Delete Selected", fg_color="red",
                          command=self.delete).pack(side="left", padx=5)

        ctk.CTkButton(btns, text="Charts",
                      command=self.charts).pack(side="left", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(self, height=350)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.total_lbl = ctk.CTkLabel(
            self, text="Total Expense: ₹0",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.total_lbl.pack(pady=5)

        self.refresh()

    # ---------- FUNCTIONS ----------
    def add(self):
        try:
            amt = float(self.e_amt.get())
        except:
            messagebox.showerror("Error", "Invalid amount")
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses VALUES(NULL,?,?,?,?,?)",
            (self.user_id, self.e_date.get(),
             self.e_cat.get(), amt, self.e_note.get())
        )
        conn.commit()
        conn.close()
        self.refresh()

    def delete(self):
        eid = self.selected_expense_id.get()
        if eid == 0:
            messagebox.showwarning("Select Expense", "Select expense to delete")
            return

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id=?", (eid,))
        conn.commit()
        conn.close()
        self.selected_expense_id.set(0)
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        total = 0
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, date, category, amount, note
            FROM expenses WHERE user_id=?
            ORDER BY date DESC
        """, (self.user_id,))
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=3)
            ctk.CTkRadioButton(
                row, variable=self.selected_expense_id, value=r[0],
                text=f"{r[1]} | {r[2]} | ₹{r[3]:.2f} | {r[4]}"
            ).pack(anchor="w", padx=10)
            total += r[3]

        self.total_lbl.configure(text=f"Total Expense: ₹{total:.2f}")

    def charts(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            SELECT category, SUM(amount)
            FROM expenses WHERE user_id=?
            GROUP BY category
        """, (self.user_id,))
        data = cur.fetchall()
        conn.close()
        if not data:
            return

        c, a = zip(*data)
        plt.figure(figsize=(6,6))
        plt.pie(a, labels=c, autopct="%1.1f%%")
        plt.title("Expense Distribution")
        plt.show()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

# ================= RUN =================
app = App()
app.mainloop()
