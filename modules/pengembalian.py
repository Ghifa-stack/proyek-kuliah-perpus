from db import menghubungkan_koneksi, denda_perhari
from modules.peminjaman import cari_peminjaman_by_id
from modules.buku import update_status_buku
from modules.petugas import caripetugas_by_id
from datetime import date


def catat_pengembalian():
    print("\n Catat Pengembalian Buku ")

    try:
        petugas_id = int(input("ID Petugas      : "))
    except ValueError:
        print(" ID harus berupa angka.")
        return

    petugas = caripetugas_by_id(petugas_id)
    if not petugas:
        print(f" Petugas dengan ID {petugas_id} tidak ditemukan.")
        return
    print(f" Petugas : {petugas[1]}")

    
    try:
        peminjaman_id = int(input("ID Peminjaman   : "))
    except ValueError:
        print(" ID harus berupa angka.")
        return

    peminjaman = cari_peminjaman_by_id(peminjaman_id)
    if not peminjaman:
        print(f" Peminjaman dengan ID {peminjaman_id} tidak ditemukan.")
        return
    if peminjaman[5] == "dikembalikan":
        print(f" Buku ini sudah pernah dikembalikan sebelumnya.")
        return

    print(f"    Anggota     : {peminjaman[1]}")
    print(f"    Buku        : {peminjaman[2]}")
    print(f"    Tgl Kembali : {peminjaman[4]}")

    
    tgl_kembali_seharusnya = peminjaman[4]
    if hasattr(tgl_kembali_seharusnya, "date"):
        tgl_kembali_seharusnya = tgl_kembali_seharusnya.date()
    tgl_dikembalikan       = date.today()
    terlambat              = (tgl_dikembalikan - tgl_kembali_seharusnya).days

    if terlambat > 0:
        total_denda = terlambat * denda_perhari
        print(f"\n    Terlambat {terlambat} hari!")
        print(f"    Total denda : Rp{total_denda:,}")
    else:
        print(f"\n    Pengembalian tepat waktu, tidak ada denda.")
        total_denda = 0

    konfirmasi = input("\nKonfirmasi pengembalian? (y/n): ").strip().lower()
    if konfirmasi != "y":
        print("Pengembalian dibatalkan.")
        return

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()

    
        cursor.execute("""
            insert into pengembalian (peminjaman_id, petugas_id, tgl_dikembalikan)
            values (%s, %s, %s)
        """, (peminjaman_id, petugas_id, tgl_dikembalikan))

       
        cursor.execute("""
            update peminjaman set status = 'dikembalikan'
            where id = %s
        """, (peminjaman_id,))

      
        buku_id = peminjaman[3]
        update_status_buku(buku_id, "tersedia", cursor)

       
        if terlambat > 0:
            cursor.execute("""
                insert into denda (peminjaman_id, jumlah_hari, total_denda)
                values (%s, %s, %s)
            """, (peminjaman_id, terlambat, total_denda))
            print(f"\n Pengembalian dicatat. Denda Rp{total_denda:,} harap segera dilunasi.")
        else:
            print(f"\n Pengembalian dicatat. Terima kasih!")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def lihat_riwayat_pengembalian():
    print("\n Riwayat Pengembalian ")

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            select kembali.id, a.nama, b.judul, kembali.tgl_dikembalikan,
                   pm.tgl_kembali, pt.nama,
                   case when d.total_denda is not null
                        then d.total_denda else 0 end as denda
            from pengembalian kembali
            join peminjaman pm on kembali.peminjaman_id = pm.id
            join anggota a     on pm.anggota_id         = a.id
            join buku b        on pm.buku_id            = b.id
            join petugas pt    on kembali.petugas_id    = pt.id
            left join denda d  on pm.id                 = d.peminjaman_id
        """)
        rows = cursor.fetchall()

        if not rows:
            print("Belum ada riwayat pengembalian.")
            return

        print(f"{'ID':<5} {'Anggota':<20} {'Judul Buku':<25} {'Tgl Kembali':<13} {'Seharusnya':<13} {'Petugas':<15} {'Denda'}")
    
        for row in rows:
            denda_str = f"Rp{row[6]:,}" if row[6] > 0 else "-"
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<25} {str(row[3]):<13} {str(row[4]):<13} {row[5]:<15} {denda_str}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()



def menu_pengembalian():
    while True:
        print("\n Pengembalian Buku ")
        print("1. Catat Pengembalian")
        print("2. Lihat Riwayat Pengembalian")
        print("0. Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            catat_pengembalian()
        elif pilihan == "2":
            lihat_riwayat_pengembalian()
        elif pilihan == "0":
            break
        else:
            print(" Pilihan tidak valid.")