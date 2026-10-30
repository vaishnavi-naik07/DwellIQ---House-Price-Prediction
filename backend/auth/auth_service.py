import os
import re
import sqlite3
import hashlib
import hmac
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from backend.core.config import (
    DB_PATH as DEFAULT_DB_PATH,
    PBKDF2_ITERATIONS,
    RATE_LIMIT_WINDOW_SEC,
    MAX_FAILED_ATTEMPTS,
)

DB_PATH = DEFAULT_DB_PATH
SALT_BYTES = 16

# Rate limiting in-memory store: {email: [timestamp, timestamp, ...]}
FAILED_ATTEMPTS: Dict[str, list] = {}

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def get_db_connection() -> sqlite3.Connection:
    """Connect to SQLite database with foreign keys and row factory."""
    global DB_PATH
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    """Initialize secure SQLite tables for users and search history with parameterized schema."""
    conn = get_db_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_estimations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                bhk INTEGER NOT NULL,
                carpet_area REAL NOT NULL,
                estimated_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
    conn.close()


def hash_password(password: str, salt_bytes: Optional[bytes] = None) -> Tuple[str, str]:
    """
    Hash password using standard-library PBKDF2-HMAC-SHA256 with 200,000 iterations.
    Returns (hex_hash, hex_salt).
    """
    if salt_bytes is None:
        salt_bytes = os.urandom(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PBKDF2_ITERATIONS,
    )
    return derived.hex(), salt_bytes.hex()


def verify_password(password: str, stored_hash: str, stored_salt: str) -> bool:
    """Safely verify password against stored PBKDF2 hash using constant-time comparison."""
    try:
        salt_bytes = bytes.fromhex(stored_salt)
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            PBKDF2_ITERATIONS,
        )
        return hmac.compare_digest(derived.hex(), stored_hash)
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Check email pattern."""
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Enforce minimum 8 characters, at least 1 digit or special character."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password) and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one number or special character."
    return True, ""


def check_rate_limit(normalized_email: str) -> Tuple[bool, int]:
    """
    Check if email is temporarily blocked due to repeated failed logins.
    Returns (is_blocked, remaining_seconds).
    """
    now = time.time()
    attempts = FAILED_ATTEMPTS.get(normalized_email, [])
    recent = [t for t in attempts if now - t < RATE_LIMIT_WINDOW_SEC]
    FAILED_ATTEMPTS[normalized_email] = recent

    if len(recent) >= MAX_FAILED_ATTEMPTS:
        oldest = min(recent)
        remaining = int(RATE_LIMIT_WINDOW_SEC - (now - oldest))
        return True, max(remaining, 1)
    return False, 0


def record_failed_attempt(normalized_email: str):
    """Record a failed login attempt timestamp."""
    now = time.time()
    attempts = FAILED_ATTEMPTS.get(normalized_email, [])
    attempts.append(now)
    FAILED_ATTEMPTS[normalized_email] = attempts


def clear_failed_attempts(normalized_email: str):
    """Reset failed attempts on successful login."""
    if normalized_email in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[normalized_email]


def register_user(full_name: str, email: str, password: str) -> Tuple[bool, str]:
    """Register a new user with validation and parameterized query."""
    full_name = full_name.strip()
    email_clean = email.strip().lower()

    if not full_name:
        return False, "Full name is required."
    if not validate_email(email_clean):
        return False, "Please enter a valid email address."

    is_valid_pw, pw_err = validate_password_strength(password)
    if not is_valid_pw:
        return False, pw_err

    init_auth_db()
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
        if cur.fetchone() is not None:
            return False, "An account with this email address already exists."

        pwd_hash, salt_hex = hash_password(password)
        cur.execute(
            """
            INSERT INTO users (email, full_name, password_hash, salt)
            VALUES (?, ?, ?, ?)
            """,
            (email_clean, full_name, pwd_hash, salt_hex),
        )
        conn.commit()
        return True, "Registration successful! You can now log in."
    except Exception as e:
        return False, f"Registration failed due to a database error: {type(e).__name__}"
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticate user with rate limiting and constant-time password verification."""
    email_clean = email.strip().lower()

    if not email_clean or not password:
        return False, "Email and password are required.", None

    is_blocked, wait_sec = check_rate_limit(email_clean)
    if is_blocked:
        return False, f"Too many failed login attempts. Please wait {wait_sec} seconds before trying again.", None

    init_auth_db()
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, full_name, password_hash, salt FROM users WHERE email = ?",
            (email_clean,),
        )
        row = cur.fetchone()

        if row is None:
            record_failed_attempt(email_clean)
            return False, "Invalid email or password.", None

        if verify_password(password, row["password_hash"], row["salt"]):
            clear_failed_attempts(email_clean)
            user_data = {
                "id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
            }
            return True, "Login successful.", user_data
        else:
            record_failed_attempt(email_clean)
            return False, "Invalid email or password.", None
    except Exception as e:
        return False, f"Authentication error: {type(e).__name__}", None
    finally:
        conn.close()


def save_user_estimation(user_id: int, location: str, bhk: int, carpet_area: float, price: float = 0.0, estimated_price: float = 0.0) -> bool:
    """Save user estimation record safely (accepts either price or estimated_price)."""
    final_price = estimated_price if estimated_price > 0 else price
    try:
        conn = get_db_connection()
        with conn:
            conn.execute(
                """
                INSERT INTO saved_estimations (user_id, location, bhk, carpet_area, estimated_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, location, bhk, carpet_area, final_price),
            )
        conn.close()
        return True
    except Exception:
        return False


def get_user_estimations(user_id: int) -> list:
    """Fetch history of estimates for a user."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT location, bhk, carpet_area, estimated_price, created_at
            FROM saved_estimations
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 25
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []
