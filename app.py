import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "spliteasy-secret-key-change-in-prod"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "spliteasy.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------- HTML PAGE ROUTES ----------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("splitter"))
    session.pop("is_guest", None)
    return render_template("login.html")


@app.route("/guest")
def guest_mode():
    session.clear()
    session["is_guest"] = True
    return redirect(url_for("splitter"))


@app.route("/splitter")
def splitter():
    if "user_id" not in session and not session.get("is_guest"):
        return redirect(url_for("index"))

    conn = get_db()
    states = conn.execute(
        "SELECT state_code, state_name, tax_rate FROM StateTaxes ORDER BY state_name"
    ).fetchall()

    user_info = None
    if "user_id" in session:
        user_info = conn.execute(
            """
            SELECT u.user_id, u.username, u.email, u.state_code, s.state_name, s.tax_rate
            FROM Users u
            JOIN StateTaxes s ON u.state_code = s.state_code
            WHERE u.user_id = ?
            """,
            (session["user_id"],),
        ).fetchone()

    conn.close()
    return render_template(
        "splitter.html",
        states=states,
        user=user_info,
        is_guest=session.get("is_guest", False),
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- RESTFUL API ENDPOINTS ----------

@app.route("/api/states", methods=["GET"])
def api_states():
    conn = get_db()
    rows = conn.execute(
        "SELECT state_code, state_name, tax_rate FROM StateTaxes ORDER BY state_name"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    state_code = data.get("state_code", "").strip().upper()

    if not all([username, email, password, state_code]):
        return jsonify({"error": "All fields are required."}), 400

    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO Users (username, email, password, state_code) VALUES (?, ?, ?, ?)",
            (username, email, password, state_code),
        )
        conn.commit()
        session.clear()
        session["user_id"] = cur.lastrowid
        return jsonify({"message": "Account created", "redirect": url_for("splitter")}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists."}), 409
    finally:
        conn.close()


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    identifier = (data.get("identifier") or data.get("email") or "").strip().lower()
    password = data.get("password", "").strip()

    if not identifier or not password:
        return jsonify({"error": "Username/email and password are required."}), 400

    conn = get_db()
    user = conn.execute(
        """
        SELECT user_id, password
        FROM Users
        WHERE LOWER(email) = ? OR LOWER(username) = ?
        """,
        (identifier, identifier),
    ).fetchone()
    conn.close()

    if not user or user["password"] != password:
        return jsonify({"error": "Invalid username/email or password."}), 401

    session.clear()
    session["user_id"] = user["user_id"]
    return jsonify({"message": "Logged in", "redirect": url_for("splitter")}), 200


@app.route("/api/bills", methods=["GET"])
def api_get_bills():
    if "user_id" not in session:
        return jsonify({"error": "Login required to view saved bills."}), 401

    date_filter = request.args.get("date", "").strip()
    time_filter = request.args.get("time", "").strip()

    query = "SELECT * FROM Bills WHERE user_id = ?"
    params = [session["user_id"]]

    if date_filter:
        query += " AND DATE(entry_timestamp) = ?"
        params.append(date_filter)
    if time_filter:
        query += " AND strftime('%H:%M', entry_timestamp) = ?"
        params.append(time_filter)

    query += " ORDER BY entry_timestamp DESC"

    conn = get_db()
    bills_rows = conn.execute(query, params).fetchall()

    results = []
    for b in bills_rows:
        bill_dict = dict(b)
        participants = conn.execute(
            "SELECT * FROM BillParticipants WHERE bill_id = ?", (b["bill_id"],)
        ).fetchall()

        part_list = []
        for p in participants:
            p_dict = dict(p)
            items = conn.execute(
                "SELECT item_name, item_price FROM ParticipantItems WHERE participant_id = ?",
                (p["participant_id"],),
            ).fetchall()
            p_dict["items"] = [dict(i) for i in items]
            part_list.append(p_dict)

        bill_dict["participants"] = part_list
        results.append(bill_dict)

    conn.close()
    return jsonify(results)


@app.route("/api/bills", methods=["POST"])
def api_create_bill():
    if "user_id" not in session:
        return jsonify({"error": "Guest users cannot save bills. Please log in or sign up."}), 401

    data = request.get_json() or {}
    bill_title = data.get("bill_title", "").strip() or "Untitled Bill"
    split_mode = data.get("split_mode", "equal")
    tip_percent = float(data.get("tip_percent") or 0)
    state_code = data.get("state_code", "").strip().upper()
    participants = data.get("participants", [])

    if not participants:
        return jsonify({"error": "Add at least one participant."}), 400

    conn = get_db()
    state_row = conn.execute(
        "SELECT tax_rate FROM StateTaxes WHERE state_code = ?", (state_code,)
    ).fetchone()
    tax_rate = float(state_row["tax_rate"]) if state_row else 0.0

    num_people = len(participants)

    if split_mode == "equal":
        subtotal = round(float(data.get("subtotal") or 0), 2)
        tax_amount = round(subtotal * tax_rate, 2)
        tip_amount = round(subtotal * (tip_percent / 100.0), 2)
        total_amount = round(subtotal + tax_amount + tip_amount, 2)
        even_share = round(total_amount / num_people, 2)
        for p in participants:
            p["owed_amount"] = even_share
            p["items"] = []
    else:
        subtotal = 0.0
        for p in participants:
            items = p.get("items", [])
            person_sub = sum(float(i.get("item_price") or 0) for i in items)
            p["person_sub"] = person_sub
            subtotal += person_sub

        subtotal = round(subtotal, 2)
        tax_amount = round(subtotal * tax_rate, 2)
        tip_amount = round(subtotal * (tip_percent / 100.0), 2)
        total_amount = round(subtotal + tax_amount + tip_amount, 2)
        shared_extras = (tax_amount + tip_amount) / num_people

        for p in participants:
            p["owed_amount"] = round(p["person_sub"] + shared_extras, 2)

    entry_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur = conn.execute(
        """
        INSERT INTO Bills (user_id, bill_title, split_mode, subtotal, tip_percent, tax_amount, tip_amount, total_amount, entry_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            bill_title,
            split_mode,
            subtotal,
            tip_percent,
            tax_amount,
            tip_amount,
            total_amount,
            entry_timestamp,
        ),
    )
    bill_id = cur.lastrowid

    for p in participants:
        p_cur = conn.execute(
            "INSERT INTO BillParticipants (bill_id, participant_name, owed_amount) VALUES (?, ?, ?)",
            (bill_id, p.get("participant_name", "Person").strip() or "Person", p["owed_amount"]),
        )
        participant_id = p_cur.lastrowid

        if split_mode == "itemized":
            for item in p.get("items", []):
                name = item.get("item_name", "").strip()
                price = float(item.get("item_price") or 0)
                if name:
                    conn.execute(
                        "INSERT INTO ParticipantItems (participant_id, item_name, item_price) VALUES (?, ?, ?)",
                        (participant_id, name, round(price, 2)),
                    )

    conn.commit()
    conn.close()
    return jsonify({"message": "Bill saved!", "bill_id": bill_id}), 201


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        from init_db import init_db
        init_db()
    app.run(debug=True)
