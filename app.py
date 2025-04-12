import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# Generate a secure key for encryption (in production, save this securely)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# In-memory data store
stored_data = {}  # Format: {encrypted_text: {"encrypted_text": ..., "passkey": ...}}
failed_attempts = 0

# Function to hash passkey using SHA-256
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Encrypt data using Fernet
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

# Decrypt data securely
def decrypt_data(encrypted_text, passkey):
    global failed_attempts
    hashed_passkey = hash_passkey(passkey)

    if encrypted_text in stored_data and stored_data[encrypted_text]["passkey"] == hashed_passkey:
        failed_attempts = 0
        return cipher.decrypt(encrypted_text.encode()).decode()
    else:
        failed_attempts += 1
        return None

# Reset failed attempts on successful login
def reset_attempts():
    global failed_attempts
    failed_attempts = 0

# Streamlit App UI
st.set_page_config(page_title="Secure Vault", layout="centered")
st.title("DataFort: End-to-End Encrypted Memory Vault")

menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.radio("Navigation", menu)

if choice == "Home":
    st.header("Welcome")
    st.write("Effortlessly protect and access your confidential data with secure encryption and personalized passkeys — your privacy, redefined.")

elif choice == "Store Data":
    st.header("Store New Data")
    user_data = st.text_area("Enter the data you want to store")
    passkey = st.text_input("Create a secure passkey", type="password")

    if st.button("Encrypt and Store"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data)
            stored_data[encrypted_text] = {"encrypted_text": encrypted_text, "passkey": hashed_passkey}
            st.success("Data has been encrypted and stored successfully.")
            st.code(encrypted_text, language="text")
        else:
            st.error("Please provide both data and a passkey.")

elif choice == "Retrieve Data":
    st.header("Retrieve Stored Data")
    encrypted_input = st.text_area("Paste your encrypted data")
    passkey_input = st.text_input("Enter your passkey", type="password")

    if st.button("Decrypt"):
        if encrypted_input and passkey_input:
            decrypted_text = decrypt_data(encrypted_input, passkey_input)

            if decrypted_text:
                st.success("Decryption successful. Your data:")
                st.text_area("Decrypted Data", decrypted_text, height=150)
            else:
                st.error(f"Invalid passkey. Attempts left: {3 - failed_attempts}")
                if failed_attempts >= 3:
                    st.warning("Too many failed attempts. Redirecting to login...")
                    st.experimental_rerun()
        else:
            st.error("Please fill in both fields.")

elif choice == "Login":
    st.header("User Login")
    login_password = st.text_input("Enter master password to continue", type="password")

    if st.button("Login"):
        if login_password == "admin123":  # Demo master password
            reset_attempts()
            st.success("Access granted. You may now return to retrieve your data.")
        else:
            st.error("Incorrect master password. Please try again.")
