import psycopg2
import streamlit as st

def init_db():
    """Initialize database connection and create/update tables."""
    try:
        conn = psycopg2.connect(
            dbname="mfa_db",
            user=st.secrets["db_user"],
            password=st.secrets["db_password"],
            host=st.secrets["db_host"],
            port="5432"
        )
        print("🛠 Database connection successful")
        with conn.cursor() as cursor:
            # Create or verify tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    username VARCHAR(100) NOT NULL
                );
                DROP TABLE IF EXISTS nonces;
            """)
            conn.commit()
            print("🛠 Tables created or updated")
            cursor.execute("SELECT user_id, username FROM users")
            users = cursor.fetchall()
            print(f"🛠 Current users in database: {users}")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

def store_user_metadata(user_id, username):
    """Store user metadata in the database."""
    if not username:
        print("❌ Error: Username cannot be empty")
        raise ValueError("Username cannot be empty")
    conn = init_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username",
                (user_id, username)
            )
            conn.commit()
            print(f"🛠 Stored metadata for user {user_id} (username: {username})")
            cursor.execute("SELECT user_id, username FROM users WHERE user_id = %s", (user_id,))
            stored = cursor.fetchone()
            print(f"🛠 Verified stored metadata: {stored}")
    except Exception as e:
        print(f"❌ Error storing user metadata: {e}")
        raise
    finally:
        conn.close()

def get_user_metadata(user_id):
    """Retrieve user metadata from the database."""
    conn = init_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            print(f"🛠 Retrieved metadata for user {user_id}: {result}")
            return result[0] if result else None
    except Exception as e:
        print(f"❌ Error retrieving user metadata: {e}")
        return None
    finally:
        conn.close()