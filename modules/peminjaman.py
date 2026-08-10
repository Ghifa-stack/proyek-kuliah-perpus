from db import menghubungkan_koneksi, durasi_pinjam, batas_pinjam
from modules.anggota import carianggota_by_id
from modules.buku import cari_buku_by_id, update_status_buku
from modules.petugas import caripetugas_by_id
from datetime import date, timedelta


def catat_peminjaman():
    print("\nCatat Peminjaman Buku ")

    try:
        petugas_id = int(input("ID Petugas   : "))
    except ValueError:
        print(" ID harus berupa angka.")
        return

    petugas = caripetugas_by_id(petugas_id)
    if not petugas:
        print(f" Petugas dengan ID {petugas_id} tidak ditemukan.")
        return
    print(f"    Petugas   : {petugas[1]}")

    
    try:
        anggota_id = int(input("ID Anggota   : "))
    except ValueError:
        print("ID harus berupa angka.")
        return

    anggota = carianggota_by_id(anggota_id)
    if not anggota:
        print(f" Anggota dengan ID {anggota_id} tidak ditemukan.")
        return
    if not anggota[3]:
        print(f" Anggota '{anggota[1]}' tidak aktif, tidak bisa meminjam.")
        return
    print(f"    Anggota   : {anggota[1]}")

    
    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
            select count(*) from peminjaman
            where anggota_id = %s and status = 'dipinjam'
        """, (anggota_id,))
        jumlah_pinjam = cursor.fetchone()[0]

        if jumlah_pinjam >= batas_pinjam:
            print(f" Anggota '{anggota[1]}' sudah meminjam {jumlah_pinjam} buku.")
            print(f"    Batas maksimal peminjaman adalah {batas_pinjam} buku.")
            conn.close()
            return


        try:
            buku_id = int(input("ID Buku      : "))
        except ValueError:
            print(" ID harus berupa angka.")
            return

        buku = cari_buku_by_id(buku_id)
        if not buku:
            print(f" Buku dengan ID {buku_id} tidak ditemukan.")
            return
        if buku[3] == "dipinjam":
            print(f" Buku '{buku[1]}' sedang dipinjam, tidak tersedia.")
            return
        print(f"    Buku      : {buku[1]}")

        
        tgl_pinjam  = date.today()
        tgl_kembali = tgl_pinjam + timedelta(days=durasi_pinjam)
        print(f"    Tgl Pinjam  : {tgl_pinjam}")
        print(f"    Tgl Kembali : {tgl_kembali}")

        konfirmasi = input("\nKonfirmasi peminjaman? (y/n): ").strip().lower()
        if konfirmasi != "y":
            print("Peminjaman dibatalkan.")
            return


        cursor.execute("""
            insert into peminjaman (anggota_id, buku_id, petugas_id, tgl_pinjam, tgl_kembali)
            values (%s, %s, %s, %s, %s)
        """, (anggota_id, buku_id, petugas_id, tgl_pinjam, tgl_kembali))

        
        update_status_buku(buku_id, "dipinjam", cursor)

        conn.commit()
        print(f"\n Peminjaman berhasil dicatat.")
        print(f"    Harap kembalikan sebelum {tgl_kembali}.")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def lihat_peminjaman_aktif():
    print("\nDaftar Peminjaman Aktif ")

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            select pm.id, a.nama, b.judul, pm.tgl_pinjam, pm.tgl_kembali, pt.nama
            from peminjaman pm
            join anggota a  on pm.anggota_id = a.id
            join buku b     on pm.buku_id    = b.id
            join petugas pt on pm.petugas_id = pt.id
            where pm.status = 'dipinjam'
        """)
        rows = cursor.fetchall()

        if not rows:
            print("Tidak ada peminjaman aktif saat ini.")
            return

        print(f"{'ID':<5} {'Anggota':<20} {'Judul Buku':<30} {'Tgl Pinjam':<13} {'Tgl Kembali':<13} {'Petugas'}")
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {str(row[3]):<13} {str(row[4]):<13} {row[5]}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def cari_peminjaman_by_id(peminjaman_id):

    conn = menghubungkan_koneksi()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            select pm.id, a.nama, b.judul, b.id, pm.tgl_kembali, pm.status
            from peminjaman pm
            join anggota a on pm.anggota_id = a.id
            join buku b    on pm.buku_id    = b.id
            where pm.id = %s
        """, (peminjaman_id,))
        return cursor.fetchone()

    except Exception as e:
        print(f"[error] {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def menu_peminjaman():
    while True:
        print("\n Peminjaman Buku ")
        print("1. Catat Peminjaman Baru")
        print("2. Lihat Peminjaman Aktif")
        print("0. Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            catat_peminjaman()
        elif pilihan == "2":
            lihat_peminjaman_aktif()
        elif pilihan == "0":
            break
        else:
            print(" Pilihan tidak valid.")