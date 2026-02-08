import streamlit as st
import json
import os
from cryptography.fernet import Fernet
from datetime import datetime

# ================== ENCRYPTION ==================

def generate_key():
    if not os.path.exists("key.key"):
        key = Fernet.generate_key()
        with open("key.key", "wb") as f:
            f.write(key)

def load_key():
    return open("key.key", "rb").read()

generate_key()
cipher = Fernet(load_key())

# ================== DATABASE ==================

def load_db():
    if not os.path.exists("passwords.json"):
        return {}

    with open("passwords.json", "r") as f:
        data = json.load(f)

    # AUTO FIX: Convert dict to list if needed
    for account in list(data.keys()):
        if isinstance(data[account], dict):
            data[account] = [data[account]]

    return data

def save_db(data):
    with open("passwords.json", "w") as f:
        json.dump(data, f, indent=4)

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt(text):
    return cipher.decrypt(text.encode()).decode()

# ================== STREAMLIT UI ==================

st.set_page_config(page_title="Password Manager", layout="centered")
st.title("🔐 Social Media Password Manager")

menu = st.sidebar.selectbox("Menu", ["Add Password", "View Passwords"])

db = load_db()

# ================== ADD PASSWORD ==================

if menu == "Add Password":
    st.subheader("➕ Add New Password")

    account = st.selectbox(
        "Select Social Media",
        ["Facebook", "Instagram", "Twitter", "LinkedIn", "YouTube", "TikTok", "Other"]
    )

    if account == "Other":
        account = st.text_input("Enter Platform Name")

    username = st.text_input("Username / Email")
    password = st.text_input("Password", type="password")

    if st.button("Save Password"):
        if account and username and password:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Ensure list for history
            if account not in db:
                db[account] = []

            db[account].append({
                "username": username,
                "password": encrypt(password),
                "date_time": now
            })

            save_db(db)
            st.success(f"Password saved for {account} (history enabled)!")
        else:
            st.error("Fill all fields!")

# ================== VIEW PASSWORDS ==================

elif menu == "View Passwords":
    st.subheader("📂 Saved Passwords")

    if not db:
        st.info("No passwords saved yet.")
    else:
        for account, records in db.items():
            st.write(f"## 🔹 {account}")

            for i, entry in enumerate(records[::-1]):
                saved_time = datetime.strptime(entry["date_time"], "%Y-%m-%d %H:%M:%S")
                days_passed = (datetime.now() - saved_time).days

                st.write(f"### Version {len(records)-i}")
                st.write(f"👤 Username: {entry['username']}")
                st.write(f"🔑 Password: {decrypt(entry['password'])}")
                st.write(f"🕒 Saved on: {entry['date_time']}")
                st.write(f"📆 Days Passed: {days_passed}")

                if days_passed >= 45:
                    st.error("⚠️ CHANGE PASSWORD (Older than 45 days)")
                else:
                    st.success("✅ Password is fresh")

                st.write("------")
