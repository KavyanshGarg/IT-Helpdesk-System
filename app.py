from flask import Flask, request, redirect, render_template, session
import sqlite3
import secrets
import hmac
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    return session["csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

def get_db():
    conn = sqlite3.connect("helpdesk.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)

        # Add user_number column if it does not already exist
    columns = conn.execute("PRAGMA table_info(users)").fetchall()

    if not any(column["name"] == "user_number" for column in columns):
        conn.execute("ALTER TABLE users ADD COLUMN user_number INTEGER")

        users = conn.execute(
            "SELECT id FROM users WHERE role = 'user' ORDER BY id"
        ).fetchall()

        for number, user in enumerate(users, start=1):
            conn.execute(
                "UPDATE users SET user_number = ? WHERE id = ?",
                (number, user["id"])
            )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Open'
        )
    """)

    conn.execute(
    """
    INSERT OR IGNORE INTO users
    (name, email, password, role)
    VALUES (?, ?, ?, ?)
    """,
    (
        "Administrator",
        "admin@helpdesk.com",
        generate_password_hash("admin123"),
        "admin"
    )
)






                                                            # Add password migration
# When your application starts:

# It reads the existing users.
# Checks whether their password is already hashed.
# If it's old plain text → hashes it.
# If it's already hashed → leaves it alone.
# So we don't accidentally hash an already-hashed password every time the server starts.
    users = conn.execute("SELECT id, password FROM users").fetchall()

    for user in users:
        password = user["password"]

        if not password.startswith(("scrypt:", "pbkdf2:")):
            new_password = generate_password_hash(password)

            conn.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (new_password, user["id"])
            )







    conn.commit()
    conn.close()





init_db()

@app.route("/")
def home():
    return redirect("/register")





                                                #Register Details
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        csrf_token = request.form.get("csrf_token", "")

        if not hmac.compare_digest(
            csrf_token,
            session.get("csrf_token", "")
        ):
            return render_template(
                "register.html",
                error="Invalid security token. Please try again."
            )

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        if not name.strip() or not email.strip() or not password:
            return render_template(
            "register.html",
            error="Please fill in all fields."
            )


        if len(password) < 8:
                return render_template(
                "register.html",
                error="Password must be at least 8 characters."
                )


        
        if not any(c.isupper() for c in password):
            return render_template(
            "register.html",
            error="Password must contain an uppercase letter.",
            name=name,
            email=email
            )

        if not any(c.islower() for c in password):
            return render_template(
            "register.html",
            error="Password must contain a lowercase letter.",
            name=name,
            email=email
            )

        if not any(c.isdigit() for c in password):
             return render_template(
              "register.html",
             error="Password must contain a number.",
             name=name,
             email=email
            )


        if "@" not in email or "." not in email:
            return render_template(
             "register.html",
             error="Please enter a valid email address."
              )

        password = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute(
            """
            INSERT INTO users (name, email, password, user_number)
            VALUES (?, ?, ?, COALESCE((SELECT MAX(user_number) FROM users), 0) + 1)
            """,
            (name, email, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            return render_template(
                 "register.html",
                  error="This email is already registered."
            )
    return render_template("register.html")




                                                   # LOGIN DETAILS
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            if user["role"] == "admin":
                return redirect("/admin")

            return redirect("/dashboard")


        message = "Invalid email or password."

    return render_template("login.html", message=message)




                                                    # Dashboard Page
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    tickets = conn.execute(
        """
        SELECT *,
                ROW_NUMBER() OVER (
                PARTITION BY user_id
                ORDER BY id ASC
                ) AS ticket_number
        FROM tickets
        WHERE user_id = ?
        ORDER BY id ASC
        """,
        (session["user_id"],)
    ).fetchall()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return render_template(
    "dashboard.html",
    tickets=tickets,
    user=user
    )





                                                    #Create Ticket Details
@app.route("/create", methods=["GET", "POST"])
def create_ticket():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        csrf_token = request.form.get("csrf_token", "")

        if not hmac.compare_digest(
            csrf_token,
            session.get("csrf_token", "")
        ):

            return render_template(
                "create_ticket.html",
                error="Invalid security token. Please try again."
            )

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]

        if not title.strip() or not description.strip():
            return render_template(
                "create_ticket.html",
                error="Please fill in all ticket fields."
            )

        if category not in ["Hardware", "Software", "Network", "Account", "Other"]:
            return render_template(
                "create_ticket.html",
                error="Invalid ticket category."
            )

        if priority not in ["Low", "Medium", "High"]:
            return render_template(
                "create_ticket.html",
                error="Invalid ticket priority."
            )

        conn = get_db()

        conn.execute(
    """
    INSERT INTO tickets
    (user_id, title, description, category, priority)
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        session["user_id"],
        title,
        description,
        category,
        priority
    )
)

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create_ticket.html")





@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")





                                                    #Admin Page Details
@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if user["role"] != "admin":
        conn.close()
        return redirect("/dashboard")

    tickets = conn.execute(
        """
        SELECT
            tickets.*, 
            users.name, 
            users.email, 
            users.user_number,
            COALESCE(users.user_number, 0) AS user_group,
            ROW_NUMBER() OVER (
                PARTITION BY tickets.user_id
                ORDER BY tickets.id ASC
            ) AS ticket_number
        FROM tickets
        JOIN users ON tickets.user_id = users.id
        ORDER BY users.user_number ASC, tickets.id ASC
        """
    ).fetchall()

    total_users = conn.execute(
    "SELECT COUNT(*) FROM users WHERE role = 'user'"
    ).fetchone()[0]

    total_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets"
    ).fetchone()[0]

    open_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Open'"
    ).fetchone()[0]

    in_progress_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'In Progress'"
    ).fetchone()[0]

    resolved_tickets = conn.execute(
        "SELECT COUNT(*) FROM tickets WHERE status = 'Resolved'"
    ).fetchone()[0]

    conn.close()

    return render_template(
    "admin.html",
    tickets=tickets,
    total_users=total_users,
    total_tickets=total_tickets,
    open_tickets=open_tickets,
    in_progress_tickets=in_progress_tickets,
    resolved_tickets=resolved_tickets
    )



                                                    #Checks the updated status
@app.route("/update_status/<int:ticket_id>", methods=["POST"])
def update_status(ticket_id):

    if "user_id" not in session:
        return redirect("/login")

    csrf_token = request.form.get("csrf_token", "")

    if not hmac.compare_digest(
        csrf_token,
        session.get("csrf_token", "")
    ):

        return redirect("/admin")

    conn = get_db()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if user["role"] != "admin":
        conn.close()
        return redirect("/dashboard")

    status = request.form["status"]

    conn.execute(
        "UPDATE tickets SET status = ? WHERE id = ?",
        (status, ticket_id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=False) 