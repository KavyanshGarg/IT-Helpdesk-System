# IT Helpdesk System 🎫

A simple web-based IT Helpdesk system built with Flask and SQLite for managing users, support tickets, and ticket status.

## Features

* User registration and login
* Password hashing
* User and admin roles
* Create and track support tickets
* Ticket categories and priorities
* Ticket status management
* Admin dashboard
* Ticket statistics
* CSRF protection
* Session-based authentication
* Input validation

## How It Works

```text
User
 ↓
Register / Login
 ↓
Create Support Ticket
 ↓
User Dashboard
 ↓
Admin Reviews Ticket
 ↓
Status Updated
 ↓
Resolved
```

## Ticket Management

Users can create tickets with:

* Title
* Description
* Category
* Priority

Supported categories:

```text
Hardware
Software
Network
Account
Other
```

Priority levels:

```text
Low
Medium
High
```

Admins can view all tickets and update their status:

```text
Open → In Progress → Resolved
```

## Security

The project includes some basic web security practices:

* Passwords are stored using Werkzeug password hashing
* CSRF tokens are used for important POST requests
* Session cookies use `HttpOnly` and `SameSite=Lax`
* SQL queries use parameterized inputs
* Admin routes check the user's role before allowing access
* Sensitive pages are configured with no-cache headers

## Project Structure

```text
IT-Helpdesk-System/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── admin.html
│   ├── create_ticket.html
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
│
└── static/
    └── style.css
```

## Tech Stack

* Python
* Flask
* SQLite
* HTML
* CSS
* Jinja2
* Werkzeug

## Running Locally

Clone the repository:

```bash
git clone https://github.com/KavyanshGarg/IT-Helpdesk-System.git
cd IT-Helpdesk-System
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Then open the local Flask address shown in the terminal.

## What I Learned

This project helped me understand:

* Flask routing
* CRUD operations
* SQLite database handling
* Authentication and sessions
* Role-based access
* Password hashing
* CSRF protection
* Form validation
* Basic web application security

## Future Improvements

* Add email notifications
* Add ticket comments
* Add file attachments
* Add search and filtering
* Add ticket assignment to support staff
* Add SLA tracking
* Deploy the application to Azure
* Replace SQLite with a production database

## Disclaimer

This is a learning/portfolio project and is not intended to be used as a production helpdesk system without additional security, testing, monitoring and deployment configuration.

## Author

**Kavyansh Garg**

GitHub: [KavyanshGarg](https://github.com/KavyanshGarg)

⭐ If you find the project useful, consider giving it a star.
