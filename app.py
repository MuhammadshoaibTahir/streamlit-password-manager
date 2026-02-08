import streamlit as st
import json, os, hashlib
from cryptography.fernet import Fernet
from datetime import datetime

# ================== ENCRYPTION ==================

def generate_key():
    if not os.path.exists("key.key"):
        with open("key.key", "wb") as f:
            f.write(Fernet.generate_key())

def load_key():
    return open("key.key", "rb").read()

generate_key()
cipher = Fernet(load_key())

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt(text):
    return cipher.decrypt(text.encode()).decode()

# ================== DATABASE ==================

def load_json(file):
    if not os.path.exists(file):
        return {}
    return json.load(open(file))

def save_json(file, data):
    json.dump(data, open(file, "w"), indent=4)

users = load_json("users.json")
passwords_db = load_json("passwords.json")

# ================== HASHING ==================

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ================== STREAMLIT UI ==================

st.set_page_config(page_title="Secure Password Manager", layout="centered")
st.title("🔐 Multi-User Secure Password Manager")

# Session state
if "user" not in st.session_state:
    st.session_state.user = None

menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Vault"])

# ================== REGISTER ==================

if menu == "Register":
    st.subheader("🆕 Create New User")

    username = st.text_input("Username")
    passcode = st.text_input("Passcode", type="password")

    if st.button("Register"):
        if username in users:
            st.error("User already exists!")
        elif username and passcode:
            users[username] = hash_pass(passcode)
            passwords_db[username] = {}
            save_json("users.json", users)
            save_json("passwords.json", passwords_db)
            st.success("User registered!")
        else:
            st.error("Fill all fields")

# ================== LOGIN ==================

elif menu == "Login":
    st.subheader("🔓 Unlock Vault")

    username = st.text_input("Username")
    passcode = st.text_input("Passcode", type="password")

    if st.button("Login"):
        if username in users and users[username] == hash_pass(passcode):
            st.session_state.user = username
            st.success(f"Welcome {username}")
        else:
            st.error("Invalid credentials")

# ================== VAULT ==================

elif menu == "Vault":
    if not st.session_state.user:
        st.warning("Please login first!")
        st.stop()

    user = st.session_state.user
    st.subheader(f"🔐 {user}'s Password Vault")

    action = st.selectbox("Action", ["Add Password", "View & Edit Passwords"])

    # ---------- ADD PASSWORD ----------
    if action == "Add Password":
        platform = st.text_input("Platform (Facebook, Gmail, etc)")
        uname = st.text_input("Account Username/Email")
        pwd = st.text_input("Password", type="password")

        if st.button("Save"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if platform not in passwords_db[user]:
                passwords_db[user][platform] = []

            passwords_db[user][platform].append({
                "username": uname,
                "password": encrypt(pwd),
                "date": now
            })

            save_json("passwords.json", passwords_db)
            st.success("Password saved with history!")

    # ---------- VIEW & EDIT ----------
    if action == "View & Edit Passwords":
        user_data = passwords_db.get(user, {})

        if not user_data:
            st.info("No passwords saved")
        else:
            for platform, records in user_data.items():
                st.write(f"## 🔹 {platform}")

                for i, rec in enumerate(records[::-1]):
                    saved_time = datetime.strptime(rec["date"], "%Y-%m-%d %H:%M:%S")
                    days = (datetime.now() - saved_time).days

                    st.write(f"Version {len(records)-i}")
                    st.write("Username:", rec["username"])
                    st.write("Password:", decrypt(rec["password"]))
                    st.write("Saved:", rec["date"])

                    if days >= 45:
                        st.error("⚠️ CHANGE PASSWORD (45 days old)")
                    else:
                        st.success("Password fresh")

                    st.write("-----")
