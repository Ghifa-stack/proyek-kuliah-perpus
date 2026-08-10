from db import menghubungkan_koneksi

def tambah_anggota():
    print("Tambah Anggota")
    nama=input("Nama Lengkap:")
    telepon=input("Nomor Telepon:")
    alamat=input("Alamat:")

    print("Jenis Kelamin L/P:")
    jenis_kelamin=input().strip().upper()
    if jenis_kelamin not in ("L","P"):
        print("Tidak valid, isi dengan L atau P")
        return
    
    tanggal_lahir = input("Tanggal Lahir (YYYY-MM-DD):")
    email = input("Email (opsional, enter untuk skip):").strip()

    conn = menghubungkan_koneksi()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
 
        cursor.execute(
            "insert into anggota (nama, telepon, alamat) values (%s, %s, %s)",
            (nama, telepon, alamat)
        )
        anggota_id = cursor.lastrowid 
 
        cursor.execute(
            """insert into profil_anggota (anggota_id, tanggal_lahir, jenis_kelamin, email)
               values (%s, %s, %s, %s)""",
            (anggota_id, tanggal_lahir, jenis_kelamin, email or None)
        )
 
        conn.commit()
        print(f"Anggota {nama} berhasil didaftarkan dengan ID: {anggota_id}")
 
    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()

def lihat_anggota():
    print("Daftar Anggota")
    conn = menghubungkan_koneksi()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            select a.id, a.nama, a.telepon, p.jenis_kelamin, p.status_aktif, a.dibuat 
            from anggota a 
            join profil_anggota p on a.id = p.anggota_id
        """)

        rows = cursor.fetchall()
        if not rows:
            print("Tidak ada anggota")
            return
        
        print(f"{'ID':<5} {'Nama':<25} {'Telepon':<15} {'JK':<5} {'Status':<10} {'Terdaftar'}")

        for row in rows:
            status = "Aktif" if row[4] else "Nonaktif"
            print(f"{row[0]:<5} {row[1]:<25} {row[2]:<15} {row[3]:<5} {status:<10} {row[5]}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()

def carianggota_by_id(anggota_id):
    conn = menghubungkan_koneksi()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            select a.id, a.nama, a.telepon, p.status_aktif
            from anggota a
            join profil_anggota p on a.id = p.anggota_id
            where a.id = %s
        """, (anggota_id,))
        return cursor.fetchone()
    
    except Exception as e:
        print(f"[error] {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def menu_anggota():
    while True:
        print("Manajemen Anggota")
        print("1. Tambah Anggota Baru")
        print("2. Lihat Semua Anggota")
        print("0. Kembali")
 
        pilihan = input("Pilih menu: ").strip()
 
        if pilihan == "1":
            tambah_anggota()
        elif pilihan == "2":
            lihat_anggota()
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid.")