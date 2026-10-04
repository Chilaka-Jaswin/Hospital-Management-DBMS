from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from functools import wraps
import os

# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "medicore_hospital_dbms_2026"
)


# =========================================================
# MYSQL DATABASE CONFIGURATION
# =========================================================

import os

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "hospital_db"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    try:

        return mysql.connector.connect(**DB)

    except Error as e:

        print("MySQL Error:", e)

        return None


# =========================================================
# LOGIN PROTECTION
# =========================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user" not in session:

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return wrapper


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user" in session:

        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        ).strip()


        # ADMIN LOGIN
        if username == "admin" and password == "admin123":

            session["user"] = username
            session["role"] = "Administrator"

            return redirect(
                url_for("dashboard")
            )


        # DOCTOR LOGIN
        elif username == "doctor" and password == "doctor123":

            session["user"] = username
            session["role"] = "Doctor"

            return redirect(
                url_for("dashboard")
            )


        # INVALID LOGIN
        else:

            flash(
                "Invalid username or password.",
                "danger"
            )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    stats = {

        "patients": 0,
        "doctors": 0,
        "appointments": 0,
        "medicines": 0,
        "departments": 0

    }

    recent = []

    conn = get_db()


    if conn:

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            # PATIENT COUNT
            cursor.execute(
                "SELECT COUNT(*) AS total FROM Patient"
            )

            stats["patients"] = cursor.fetchone()["total"]


            # DOCTOR COUNT
            cursor.execute(
                "SELECT COUNT(*) AS total FROM Doctor"
            )

            stats["doctors"] = cursor.fetchone()["total"]


            # APPOINTMENT COUNT
            cursor.execute(
                "SELECT COUNT(*) AS total FROM Appointment"
            )

            stats["appointments"] = cursor.fetchone()["total"]


            # MEDICINE COUNT
            cursor.execute(
                "SELECT COUNT(*) AS total FROM Medicine"
            )

            stats["medicines"] = cursor.fetchone()["total"]


            # DEPARTMENT COUNT
            cursor.execute(
                "SELECT COUNT(*) AS total FROM Department"
            )

            stats["departments"] = cursor.fetchone()["total"]


            # RECENT APPOINTMENTS
            cursor.execute("""
                SELECT
                    a.appointment_id,
                    p.patient_name,
                    d.doctor_name,
                    a.appointment_date,
                    a.appointment_time,
                    a.status

                FROM Appointment a

                JOIN Patient p
                    ON p.patient_id = a.patient_id

                JOIN Doctor d
                    ON d.doctor_id = a.doctor_id

                ORDER BY
                    a.appointment_date DESC,
                    a.appointment_time DESC

                LIMIT 6
            """)

            recent = cursor.fetchall()


        except Error as e:

            print(
                "Dashboard Error:",
                e
            )


        finally:

            cursor.close()
            conn.close()


    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent
    )


# =========================================================
# PATIENTS
# =========================================================

@app.route("/patients")
@login_required
def patients():

    search = request.args.get(
        "q",
        ""
    ).strip()

    patients_list = []

    conn = get_db()


    if conn:

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            if search:

                cursor.execute("""
                    SELECT *
                    FROM Patient

                    WHERE
                        patient_name LIKE %s
                        OR phone LIKE %s

                    ORDER BY patient_id DESC
                """, (

                    f"%{search}%",
                    f"%{search}%"

                ))

            else:

                cursor.execute("""
                    SELECT *
                    FROM Patient

                    ORDER BY patient_id DESC
                """)


            patients_list = cursor.fetchall()


        except Error as e:

            print(
                "Patient Error:",
                e
            )


        finally:

            cursor.close()
            conn.close()


    return render_template(
        "patients.html",
        patients=patients_list,
        q=search
    )


# =========================================================
# ADD PATIENT
# =========================================================

@app.route(
    "/patients/add",
    methods=["POST"]
)
@login_required
def add_patient():

    patient_name = request.form.get(
        "patient_name",
        ""
    ).strip()

    gender = request.form.get(
        "gender",
        ""
    ).strip()

    date_of_birth = request.form.get(
        "date_of_birth",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()


    # VALIDATION
    if not patient_name:

        flash(
            "Patient name is required.",
            "danger"
        )

        return redirect(
            url_for("patients")
        )


    conn = get_db()


    if not conn:

        flash(
            "Could not connect to MySQL.",
            "danger"
        )

        return redirect(
            url_for("patients")
        )


    cursor = conn.cursor()


    try:

        cursor.execute("""
            INSERT INTO Patient
            (
                patient_name,
                gender,
                date_of_birth,
                phone,
                address
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (

            patient_name,
            gender,
            date_of_birth if date_of_birth else None,
            phone,
            address

        ))


        conn.commit()


        flash(
            f"{patient_name} added successfully!",
            "success"
        )


    except Error as e:

        conn.rollback()

        print(
            "Add Patient Error:",
            e
        )

        flash(
            f"Could not add patient: {e}",
            "danger"
        )


    finally:

        cursor.close()
        conn.close()


    return redirect(
        url_for("patients")
    )


# =========================================================
# DOCTORS
# =========================================================

@app.route("/doctors")
@login_required
def doctors():

    doctors_list = []

    conn = get_db()


    if conn:

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute("""
                SELECT
                    d.doctor_id,
                    d.doctor_name,
                    d.specialization,
                    d.phone,
                    d.department_id,
                    dep.department_name

                FROM Doctor d

                LEFT JOIN Department dep
                    ON dep.department_id = d.department_id

                ORDER BY d.doctor_id
            """)


            doctors_list = cursor.fetchall()


        except Error as e:

            print(
                "Doctor Error:",
                e
            )


        finally:

            cursor.close()
            conn.close()


    return render_template(
        "doctors.html",
        doctors=doctors_list
    )


# =========================================================
# APPOINTMENTS
# =========================================================

@app.route(
    "/appointments",
    methods=["GET", "POST"]
)
@login_required
def appointments():

    conn = get_db()


    if not conn:

        flash(
            "Could not connect to MySQL.",
            "danger"
        )

        return render_template(
            "appointments.html",
            appointments=[],
            patients=[],
            doctors=[]
        )


    cursor = conn.cursor(
        dictionary=True
    )


    try:

        # =================================================
        # CREATE APPOINTMENT
        # =================================================

        if request.method == "POST":

            patient_id = request.form.get(
                "patient_id"
            )

            doctor_id = request.form.get(
                "doctor_id"
            )

            appointment_date = request.form.get(
                "appointment_date"
            )

            appointment_time = request.form.get(
                "appointment_time"
            )

            status = request.form.get(
                "status",
                "Scheduled"
            )


            # VALIDATION
            if (
                not patient_id
                or not doctor_id
                or not appointment_date
                or not appointment_time
            ):

                flash(
                    "Please fill all required appointment fields.",
                    "danger"
                )


            else:

                cursor.execute("""
                    INSERT INTO Appointment
                    (
                        patient_id,
                        doctor_id,
                        appointment_date,
                        appointment_time,
                        status
                    )

                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """, (

                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    status

                ))


                conn.commit()


                flash(
                    "Appointment scheduled successfully!",
                    "success"
                )


                return redirect(
                    url_for("appointments")
                )


        # =================================================
        # LOAD PATIENTS
        # =================================================

        cursor.execute("""
            SELECT
                patient_id,
                patient_name

            FROM Patient

            ORDER BY patient_name
        """)


        patients = cursor.fetchall()


        # =================================================
        # LOAD DOCTORS
        # =================================================

        cursor.execute("""
            SELECT
                doctor_id,
                doctor_name,
                specialization

            FROM Doctor

            ORDER BY doctor_name
        """)


        doctors = cursor.fetchall()


        # =================================================
        # LOAD APPOINTMENTS
        # =================================================

        cursor.execute("""
            SELECT

                a.appointment_id,

                p.patient_name,

                d.doctor_name,

                d.specialization,

                a.appointment_date,

                a.appointment_time,

                a.status

            FROM Appointment a

            JOIN Patient p
                ON p.patient_id = a.patient_id

            JOIN Doctor d
                ON d.doctor_id = a.doctor_id

            ORDER BY

                a.appointment_date DESC,

                a.appointment_time DESC
        """)


        appointments_list = cursor.fetchall()


        # =================================================
        # SHOW APPOINTMENTS PAGE
        # =================================================

        return render_template(

            "appointments.html",

            appointments=appointments_list,

            patients=patients,

            doctors=doctors

        )


    except Error as e:

        conn.rollback()

        print(
            "Appointment Error:",
            e
        )

        flash(
            f"Database error: {e}",
            "danger"
        )


        return render_template(

            "appointments.html",

            appointments=[],

            patients=[],

            doctors=[]

        )


    finally:

        cursor.close()
        conn.close()


# =========================================================
# DATABASE DESIGN
# =========================================================

@app.route("/database")
@login_required
def database():

    tables = []

    conn = get_db()


    if conn:

        cursor = conn.cursor()

        try:

            cursor.execute(
                "SHOW TABLES"
            )


            tables = [

                row[0]

                for row in cursor.fetchall()

            ]


        except Error as e:

            print(
                "Database Error:",
                e
            )


        finally:

            cursor.close()
            conn.close()


    return render_template(
        "database.html",
        tables=tables
    )


# =========================================================
# SQL LABORATORY
# =========================================================

@app.route("/queries")
@login_required
def queries():

    return render_template(
        "queries.html"
    )


# =========================================================
# SQL QUERY API
# READ-ONLY QUERIES
# =========================================================

@app.route(
    "/api/query",
    methods=["POST"]
)
@login_required
def api_query():

    data = request.get_json() or {}


    query = data.get(
        "query",
        ""
    ).strip()


    if not query:

        return jsonify({

            "success": False,

            "error":
                "Please enter a SQL query."

        })


    command = query.split()[0].upper()


    allowed = [

        "SELECT",
        "SHOW",
        "DESCRIBE",
        "DESC"

    ]


    if command not in allowed:

        return jsonify({

            "success": False,

            "error":
                "Only SELECT, SHOW and DESCRIBE queries are allowed."

        })


    conn = get_db()


    if not conn:

        return jsonify({

            "success": False,

            "error":
                "Could not connect to MySQL."

        })


    cursor = conn.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            query
        )


        rows = cursor.fetchall()


        return jsonify({

            "success": True,

            "rows": rows

        })


    except Error as e:

        return jsonify({

            "success": False,

            "error": str(e)

        })


    finally:

        cursor.close()
        conn.close()


# =========================================================
# DATABASE HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    conn = get_db()

    connected = bool(conn)


    if conn:

        conn.close()


    return jsonify({

        "status":
            "OK"
            if connected
            else "ERROR",

        "database":
            "Connected"
            if connected
            else "Not Connected"

    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "MEDICORE HOSPITAL MANAGEMENT SYSTEM"
    )

    print("=" * 60)

    print(
        "Database : hospital_db"
    )

    print(
        "User     : root"
    )

    print(
        "Server   : http://127.0.0.1:5000"
    )

    print("=" * 60)


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )