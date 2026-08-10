from db import menghubungkan_koneksi

def tambah_petugas():
    print(" Tambah Petugas")
    nama = input(" Nama Lengkap:")
    username = input(" Username:")
    password = input(" Password:")

    conn = menghubungkan_koneksi()

    if not conn:
        return
    
    try:
        cursor = conn.cursor()

        cursor.execute("select id from petugas where username = %s", (username,))
        if cursor.fetchone():
            print(f"Username anda sudah digunakan, gunakan username lain.")
            return

        cursor.execute(
            "insert into petugas (nama, username, password) values (%s,%s,%s)",
            (nama, username, password)
        )
        conn.commit()
        print(f"Petugas {nama} sudah berhasil ditambahkan")

    except Exception as e:
        print(f" [error] {e}")

    finally:
        cursor.close()
        conn.close()

def lihat_petugas():
    print("Daftar Petugas")

    conn = menghubungkan_koneksi()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("select id, nama, username, dibuat from petugas")
        rows = cursor.fetchall()

        if not rows:
            print("Belum ada petugas")
            return
        
        print(f"{'ID':<5} {'Nama':<25} {'Username':<20} {'Terdaftar'}")
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<20} {row[3]}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()

def caripetugas_by_id(petugas_id):
    conn = menghubungkan_koneksi()
    if not conn:
        return  None
    
    try:
        cursor = conn.cursor()
        cursor.execute("select id, nama from petugas where id = %s ", (petugas_id,))
        return cursor.fetchone()
    
    except Exception as e:
        print(f"[error]{e}")

    finally:
        cursor.close()
        conn.close()

def menu_petugas():
    while True:
        print("Manajemen Petugas")
        print("1. Tambah Petugas")
        print("2. Lihat Semua Petugas")
        print("0. Kembali")
 
        pilihan = input("Pilih menu: ").strip()
 
        if pilihan == "1":
            tambah_petugas()
        elif pilihan == "2":
            lihat_petugas()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")































