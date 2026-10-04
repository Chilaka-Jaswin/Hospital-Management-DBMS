# MediCore — Hospital Management System
## VS Code / Flask / MySQL

### Login
- Admin: `admin` / `admin123`
- Doctor: `doctor` / `doctor123`

### Run
1. Install Python 3.10+ and MySQL.
2. Open this folder in VS Code.
3. `python -m venv venv`
4. `venv\Scripts\activate`
5. `pip install -r requirements.txt`
6. Run `database/schema.sql` in MySQL Workbench.
7. If needed set DB_PASSWORD in `app.py` or as an environment variable.
8. `python app.py`
9. Open `http://127.0.0.1:5000`

The interface includes a polished login page, dashboard, patient management, doctors, appointments, database design and SQL laboratory. The web query runner is intentionally read-only.
