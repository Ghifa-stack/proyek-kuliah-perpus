import mysql.connector
from mysql.connector import Error

database_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "perpustakaan"
}

denda_perhari = 5000
batas_pinjam = 3
durasi_pinjam = 7

def menghubungkan_koneksi():
    try:
        conn = mysql.connector.connect(**database_config)
        return conn
    except Error as error:
        print(f"Gagal Tehubung Ke Databse:{error}")
        return None
    
def test_koneksi():
    conn = menghubungkan_koneksi()
    if conn and conn.is_connected():
        print("Koneksi ke Database berhasil")
        conn.close()

    else:
        print("Koneksi ke Database Gagal, cek ulang")
    