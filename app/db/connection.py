import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    print("--- Đang kết nối tới HospitalDB... ---")
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='konu14102006', 
            
            database='hospital_patient_manager', 
            
            use_pure=True
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Lỗi kết nối: {err}")
        return None
