"""
Authentication and User Security Service for StudySync.
Provides PBKDF2-HMAC-SHA256 password security, user registration,
login verification, and Streamlit session auth guards.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import streamlit as st
from .database import get_db_connection, hash_password, verify_password


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def register_user(email: str, password: str, name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Register a new user account with secure hashed password."""
    email = email.strip().lower()
    name = name.strip()

    if not re.match(EMAIL_REGEX, email):
        return False, "Please enter a valid email address.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    if not name:
        return False, "Please provide your full name.", None

    pw_hash, salt = hash_password(password)
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, name, password_hash, salt, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (email, name, pw_hash, salt, "student", now_iso)
            )
            conn.commit()
            user_id = cursor.lastrowid
            user = {
                "id": user_id,
                "email": email,
                "name": name,
                "role": "student"
            }
            return True, "Account created successfully!", user
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return False, "An account with this email already exists.", None
        return False, f"Registration failed: {e}", None


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticate an existing user with email and password."""
    email = email.strip().lower()

    if not email or not password:
        return False, "Please enter both email and password.", None

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, email, name, password_hash, salt, role FROM users WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()
            if not row:
                return False, "No account found with this email address.", None

            stored_hash = row["password_hash"]
            salt = row["salt"]

            if not verify_password(password, stored_hash, salt):
                return False, "Incorrect password. Please try again.", None

            # Update last login timestamp
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now_iso, row["id"]))
            conn.commit()

            user = {
                "id": row["id"],
                "email": row["email"],
                "name": row["name"],
                "role": row["role"]
            }
            return True, "Authentication successful!", user
    except Exception as e:
        return False, f"Login error: {e}", None


def logout_user():
    """Clear session credentials and log out."""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()


def render_auth_screen():
    """Renders the Coursera / Udemy style login & register portal."""
    c_pad1, c_auth, c_pad2 = st.columns([2, 5, 2])

    with c_auth:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px;">
                <span class="badge-blue">SECURE ACCESS</span>
                <h1 style="color: #14382C; font-size: 2.2rem; margin-top: 8px; margin-bottom: 4px;">Welcome to StudySync</h1>
                <p style="color: #64748B; font-size: 1rem;">Sign in to your personalized AI learning ecosystem.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown(
                """
                <div style="background: #EAF3EE; border-left: 4px solid #1B4D3E; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px;">
                    <strong style="color: #14382C;">Demo Student Credentials:</strong><br/>
                    <span style="font-size: 0.88rem; color: #1E293B;">Email: <code>asha@studysync.edu</code> • Password: <code>Password@123</code></span>
                </div>
                """,
                unsafe_allow_html=True
            )

            login_email = st.text_input("Email Address:", value="asha@studysync.edu", key="auth_login_email")
            login_pw = st.text_input("Password:", value="Password@123", type="password", key="auth_login_pw")

            if st.button("Sign In to StudySync", type="primary", use_container_width=True, key="btn_auth_login"):
                with st.spinner("Verifying credentials..."):
                    ok, msg, user = authenticate_user(login_email, login_pw)
                    if ok and user:
                        st.session_state.authenticated = True
                        st.session_state.current_user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_signup:
            reg_name = st.text_input("Full Name:", placeholder="e.g. Rahul Verma", key="auth_reg_name")
            reg_email = st.text_input("Email Address:", placeholder="e.g. rahul@university.edu", key="auth_reg_email")
            reg_pw = st.text_input("Create Password (min 6 chars):", type="password", key="auth_reg_pw")
            reg_pw_confirm = st.text_input("Confirm Password:", type="password", key="auth_reg_pw_conf")

            if st.button("Create My Account", type="primary", use_container_width=True, key="btn_auth_reg"):
                if reg_pw != reg_pw_confirm:
                    st.error("Passwords do not match!")
                else:
                    with st.spinner("Creating secure account..."):
                        ok, msg, user = register_user(reg_email, reg_pw, reg_name)
                        if ok and user:
                            st.session_state.authenticated = True
                            st.session_state.current_user = user
                            st.success("Account created successfully! Logging you in...")
                            st.rerun()
                        else:
                            st.error(msg)


def require_auth() -> Dict[str, Any]:
    """
    Enforces authentication on the page.
    If authenticated, returns current_user dict and adds user profile in sidebar.
    If not authenticated, renders the login portal and halts further execution.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if not st.session_state.authenticated or not st.session_state.current_user:
        render_auth_screen()
        st.stop()

    user = st.session_state.current_user

    # Add user status to the top of the sidebar
    with st.sidebar:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">ACTIVE STUDENT</div>
                <div style="font-size: 1rem; font-weight: 700; color: #14382C;">👤 {user['name']}</div>
                <div style="font-size: 0.8rem; color: #64748B;">{user['email']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚪 Sign Out", key="sidebar_sign_out", use_container_width=True, type="secondary"):
            logout_user()

    return user
