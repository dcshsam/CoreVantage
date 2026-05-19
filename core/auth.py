"""
CodeVantage — Authentication & Role-Based Access Control
Aligned with SAP role model: Admin, Analyst, Developer, Viewer
"""

from __future__ import annotations
import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import streamlit as st

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    import hashlib
    _HAS_BCRYPT = False

DATA_DIR   = Path(__file__).parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

# ── Role definitions (mirrors SAP authorization object pattern) ───────────────
ROLES: dict[str, dict] = {
    "admin": {
        "label":       "System Administrator",
        "sap_role":    "Z_CV_ADMIN",
        "permissions": {"read", "write", "analyze", "remediate", "export", "admin", "configure"},
        "color":       "#BB0000",
        "icon":        "🔴",
    },
    "developer": {
        "label":       "ABAP Developer",
        "sap_role":    "Z_CV_DEVELOPER",
        "permissions": {"read", "analyze", "remediate", "export"},
        "color":       "#0A6ED1",
        "icon":        "🔵",
    },
    "analyst": {
        "label":       "Code Analyst",
        "sap_role":    "Z_CV_ANALYST",
        "permissions": {"read", "analyze", "export"},
        "color":       "#188918",
        "icon":        "🟢",
    },
    "viewer": {
        "label":       "Report Viewer",
        "sap_role":    "Z_CV_VIEWER",
        "permissions": {"read", "export"},
        "color":       "#6D6D6D",
        "icon":        "⚪",
    },
}


@dataclass
class User:
    id:            str
    username:      str
    password_hash: str
    full_name:     str
    email:         str
    role:          str
    active:        bool       = True
    created_at:    str        = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_login:    Optional[str] = None
    analyses_run:  int        = 0

    def has_permission(self, perm: str) -> bool:
        return perm in ROLES.get(self.role, {}).get("permissions", set())

    def role_label(self) -> str:
        return ROLES.get(self.role, {}).get("label", self.role.title())

    def role_icon(self) -> str:
        return ROLES.get(self.role, {}).get("icon", "⚪")

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "User":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    if _HAS_BCRYPT:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(12)).decode()
    return hashlib.sha256(plain.encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    if _HAS_BCRYPT:
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except Exception:
            return False
    return hashlib.sha256(plain.encode()).hexdigest() == hashed


# ── Persistence ───────────────────────────────────────────────────────────────

def _load_raw() -> list[dict]:
    if not USERS_FILE.exists():
        return []
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8")).get("users", [])
    except Exception:
        return []


def _save_raw(users: list[User]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(
        json.dumps({"users": [u.to_dict() for u in users]}, indent=2),
        encoding="utf-8",
    )


def load_users() -> list[User]:
    return [User.from_dict(d) for d in _load_raw()]


def save_users(users: list[User]) -> None:
    _save_raw(users)


def get_user(username: str) -> Optional[User]:
    return next((u for u in load_users() if u.username == username), None)


def get_user_by_id(uid: str) -> Optional[User]:
    return next((u for u in load_users() if u.id == uid), None)


# ── Default admin bootstrap ───────────────────────────────────────────────────

def _ensure_default_admin() -> None:
    existing = _load_raw()
    if any(u.get("role") == "admin" for u in existing):
        return
    admin = User(
        id="usr_admin_001",
        username="admin",
        password_hash=hash_password("Admin@123"),
        full_name="System Administrator",
        email="admin@corevantage.local",
        role="admin",
    )
    _save_raw([admin])


# ── Authentication ────────────────────────────────────────────────────────────

def authenticate(username: str, password: str) -> Optional[User]:
    _ensure_default_admin()
    user = get_user(username.strip().lower())
    if not user or not user.active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    users = load_users()
    for u in users:
        if u.id == user.id:
            u.last_login = datetime.utcnow().isoformat()
    save_users(users)
    return user


# ── User CRUD ─────────────────────────────────────────────────────────────────

def create_user(username: str, password: str, full_name: str,
                email: str, role: str) -> tuple[bool, str]:
    if role not in ROLES:
        return False, f"Invalid role '{role}'."
    users = load_users()
    if any(u.username == username.lower() for u in users):
        return False, f"Username '{username}' already exists."
    users.append(User(
        id=f"usr_{uuid.uuid4().hex[:12]}",
        username=username.strip().lower(),
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        email=email.strip().lower(),
        role=role,
    ))
    save_users(users)
    return True, "User created successfully."


def update_user(uid: str, **kwargs) -> tuple[bool, str]:
    users = load_users()
    found = False
    for u in users:
        if u.id == uid:
            if "password" in kwargs:
                u.password_hash = hash_password(kwargs.pop("password"))
            for k, v in kwargs.items():
                if hasattr(u, k):
                    setattr(u, k, v)
            found = True
            break
    if not found:
        return False, "User not found."
    save_users(users)
    return True, "User updated."


def delete_user(uid: str, current_user_id: str) -> tuple[bool, str]:
    if uid == current_user_id:
        return False, "Cannot delete your own account."
    users = load_users()
    before = len(users)
    users = [u for u in users if u.id != uid]
    if len(users) == before:
        return False, "User not found."
    save_users(users)
    return True, "User deleted."


def increment_analyses(uid: str) -> None:
    users = load_users()
    for u in users:
        if u.id == uid:
            u.analyses_run += 1
    save_users(users)


# ── Streamlit session helpers ─────────────────────────────────────────────────

def login(user: User) -> None:
    st.session_state["cv_authenticated"] = True
    st.session_state["cv_user"]          = user.to_dict()


def logout() -> None:
    for k in ["cv_authenticated", "cv_user"]:
        st.session_state.pop(k, None)
    st.rerun()


def current_user() -> Optional[User]:
    d = st.session_state.get("cv_user")
    return User.from_dict(d) if d else None


def is_authenticated() -> bool:
    return bool(st.session_state.get("cv_authenticated")) and current_user() is not None


def require_auth(redirect: bool = True) -> Optional[User]:
    """Call at the top of every protected page."""
    if not is_authenticated():
        if redirect:
            st.switch_page("app.py")
        st.stop()
    return current_user()


def require_permission(perm: str) -> None:
    u = require_auth()
    if not u.has_permission(perm):
        st.error(f"Access denied — your role ({u.role_label()}) does not have '{perm}' permission.")
        st.stop()


# ── Login UI (rendered inside app.py) ────────────────────────────────────────

def render_login_page() -> None:
    _ensure_default_admin()

    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue",
                     Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        text-transform: none !important;
    }

    /* ── Full-screen background image — slow Ken Burns drift ── */
    [data-testid="stAppViewContainer"] {
        background-image:
            linear-gradient(135deg, rgba(10,15,30,0.68) 0%, rgba(3,45,96,0.50) 100%),
            url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1920&q=80") !important;
        background-size: cover, 140% auto !important;
        background-repeat: no-repeat, no-repeat !important;
        background-position: center center, 0% 30% !important;
        animation: bgdrift 40s ease-in-out infinite alternate !important;
    }

    @keyframes bgdrift {
        0%   { background-position: center center, 0%   30%; background-size: cover, 130% auto; }
        25%  { background-position: center center, 40%  55%; background-size: cover, 140% auto; }
        50%  { background-position: center center, 80%  70%; background-size: cover, 145% auto; }
        75%  { background-position: center center, 55%  25%; background-size: cover, 138% auto; }
        100% { background-position: center center, 10%  50%; background-size: cover, 132% auto; }
    }

    /* Vignette overlay */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        background: radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,0.50) 100%);
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stMain"] { background: transparent !important; position: relative; z-index: 1; }
    [data-testid="stSidebar"]{ display: none !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    /* ── Login card — frosted glass on the gradient ── */
    [data-testid="stForm"] {
        background: rgba(255,255,255,0.92) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.7) !important;
        box-shadow:
            0 8px 40px rgba(0,0,0,0.28),
            0 1px 0 rgba(255,255,255,0.6) inset !important;
        padding: 40px 40px 32px !important;
    }

    /* Inputs */
    input[type="text"], input[type="password"] {
        border-radius: 8px !important;
        border: 1.5px solid #DDDBDA !important;
        background: #FAFAFA !important;
        font-size: 0.875rem !important;
        padding: 10px 14px !important;
        color: #181818 !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        text-transform: none !important;
    }
    input[type="text"]:focus, input[type="password"]:focus {
        border-color: #0176D3 !important;
        box-shadow: 0 0 0 3px rgba(1,118,211,0.18) !important;
        outline: none !important;
        background: #FFFFFF !important;
    }

    /* Sign In button */
    button[data-testid="baseButton-primaryFormSubmit"] {
        background: linear-gradient(135deg, #0176D3 0%, #014486 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        color: #FFFFFF !important;
        height: 46px !important;
        text-transform: none !important;
        letter-spacing: 0.2px !important;
        transition: opacity 0.15s ease, box-shadow 0.15s ease !important;
        box-shadow: 0 4px 14px rgba(1,118,211,0.45) !important;
    }
    button[data-testid="baseButton-primaryFormSubmit"]:hover {
        opacity: 0.90 !important;
        box-shadow: 0 6px 20px rgba(1,118,211,0.55) !important;
    }

    /* Input labels */
    [data-testid="stForm"] [data-testid="stWidgetLabel"] p,
    [data-testid="stForm"] label p,
    [data-testid="stForm"] .stTextInput label {
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        color: #3E3E3C !important;
        margin-bottom: 4px !important;
        text-transform: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # One centred column — form is THE card
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

        with st.form("cv_login", clear_on_submit=False):
            # Logo + title live inside the form so it's all one card
            st.markdown("""
            <div style="text-align:center; margin-bottom:24px; padding-top:4px">
              <div style="
                  display:inline-flex; align-items:center; justify-content:center;
                  background: linear-gradient(135deg, #0176D3 0%, #014486 100%);
                  border-radius: 14px; width: 56px; height: 56px;
                  font-size: 1.7rem; margin-bottom: 16px;
                  box-shadow: 0 4px 16px rgba(1,118,211,0.45);
              ">⚡</div>
              <div style="
                  font-size: 1.55rem; font-weight: 700; color: #032D60;
                  letter-spacing: -0.4px; line-height: 1.2; margin-bottom: 6px;
              ">CodeVantage</div>
              <div style="font-size: 0.84rem; color: #706E6B; letter-spacing: 0.1px;">
                  Enterprise ABAP Intelligence Platform
              </div>
            </div>
            <hr style="border:none;border-top:1px solid #EAEAEA;margin:0 0 20px">
            """, unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        # ── Auth logic ───────────────────────────────────────────────
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
                return
            user = authenticate(username, password)
            if user:
                login(user)
                st.success(f"Welcome back, {user.full_name}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
