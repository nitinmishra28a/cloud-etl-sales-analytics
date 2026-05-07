import hashlib
import streamlit as st
import mysql.connector


# =========================================
# DATABASE CONNECTION
# =========================================

def connect_db():

    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        database=st.secrets["DB_NAME"]
    )


# =========================================
# PASSWORD HASHING
# =========================================

def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()


# =========================================
# CREATE USER
# =========================================

def create_user(username, email, password):

    conn = connect_db()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """

    try:

        cursor.execute(
            query,
            (username, email, hashed_pw)
        )

        conn.commit()

        return True

    except Exception as e:

        st.error(f"Signup Error: {e}")

        return False

    finally:

        cursor.close()
        conn.close()


# =========================================
# LOGIN USER
# =========================================

def login_user(username, password):

    conn = connect_db()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    query = """
    SELECT * FROM users
    WHERE username=%s
    AND password=%s
    """

    cursor.execute(
        query,
        (username, hashed_pw)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user