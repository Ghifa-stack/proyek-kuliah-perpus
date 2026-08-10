from db import menghubungkan_koneksi


def laporan_peminjaman_aktif():
    print("\n Laporan Peminjaman Aktif ")

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            select pm.id, a.nama, b.judul, pm.tgl_pinjam, pm.tgl_kembali,
                   datediff(curdate(), pm.tgl_kembali) as keterlambatan
            from peminjaman pm
            join anggota a on pm.anggota_id = a.id
            join buku b    on pm.buku_id    = b.id
            where pm.status = 'dipinjam'
            order by pm.tgl_kembali asc
        """)
        rows = cursor.fetchall()

        if not rows:
            print("Tidak ada peminjaman aktif saat ini.")
            return

        print(f"{'ID':<5} {'Anggota':<20} {'Judul Buku':<30} {'Tgl Pinjam':<13} {'Tgl Kembali':<13} {'Ket.'}")
        
        for row in rows:
            keterlambatan = row[5]
            if keterlambatan and keterlambatan > 0:
                ket_str = f"Terlambat {keterlambatan} hari"
            else:
                ket_str = "Tepat waktu"
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {str(row[3]):<13} {str(row[4]):<13} {ket_str}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def laporan_denda_belum_lunas():
    print("\n Laporan Denda Belum Lunas ")

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            select d.id, a.nama, b.judul, d.jumlah_hari,
                   d.total_denda, d.status_bayar
            from denda d
            join peminjaman pm on d.peminjaman_id = pm.id
            join anggota a     on pm.anggota_id   = a.id
            join buku b        on pm.buku_id       = b.id
            where d.status_bayar = 'belum_lunas'
        """)
        rows = cursor.fetchall()

        if not rows:
            print("Tidak ada denda yang belum lunas.")
            return

        total_keseluruhan = 0
        print(f"{'ID':<5} {'Anggota':<20} {'Judul Buku':<30} {'Terlambat':<12} {'Total Denda':<15} {'Status'}")
        
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {str(row[3])+' hari':<12} Rp{row[4]:,}{'':<5} {row[5]}")
            total_keseluruhan += row[4]

        print(f"Total denda belum lunas: Rp{total_keseluruhan:,}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def laporan_riwayat_anggota():
    print("\n Riwayat Peminjaman per Anggota ")

    try:
        anggota_id = int(input("Masukkan ID Anggota: "))
    except ValueError:
        print("[!] ID harus berupa angka.")
        return

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        cursor.execute("select nama from anggota where id = %s", (anggota_id,))
        anggota = cursor.fetchone()
        if not anggota:
            print(f" Anggota dengan ID {anggota_id} tidak ditemukan.")
            return

        print(f"\nRiwayat peminjaman untuk: {anggota[0]}")

        cursor.execute("""
            select pm.id, b.judul, pm.tgl_pinjam, pm.tgl_kembali,
                   pm.status,
                   case when d.total_denda is not null
                        then d.total_denda else 0 end as denda
            from peminjaman pm
            join buku b       on pm.buku_id      = b.id
            left join denda d on pm.id            = d.peminjaman_id
            where pm.anggota_id = %s
            order by pm.tgl_pinjam desc
        """, (anggota_id,))
        rows = cursor.fetchall()

        if not rows:
            print("Anggota ini belum pernah meminjam buku.")
            return

        print(f"{'ID':<5} {'Judul Buku':<30} {'Tgl Pinjam':<13} {'Tgl Kembali':<13} {'Status':<15} {'Denda'}")
    
        for row in rows:
            denda_str = f"Rp{row[5]:,}" if row[5] > 0 else "-"
            print(f"{row[0]:<5} {row[1]:<30} {str(row[2]):<13} {str(row[3]):<13} {row[4]:<15} {denda_str}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def bayar_denda():
    print("\n Bayar Denda ")

    try:
        denda_id = int(input("Masukkan ID Denda: "))
    except ValueError:
        print("ID harus berupa angka.")
        return

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
            select d.id, a.nama, d.total_denda, d.status_bayar
            from denda d
            join peminjaman pm on d.peminjaman_id = pm.id
            join anggota a     on pm.anggota_id   = a.id
            where d.id = %s
        """, (denda_id,))
        denda = cursor.fetchone()

        if not denda:
            print(f"[!] Denda dengan ID {denda_id} tidak ditemukan.")
            return
        if denda[3] == "lunas":
            print(f"[!] Denda ini sudah lunas.")
            return

        print(f"    Anggota     : {denda[1]}")
        print(f"    Total denda : Rp{denda[2]:,}")

        konfirmasi = input("Konfirmasi pembayaran? (y/n): ").strip().lower()
        if konfirmasi != "y":
            print("Pembayaran dibatalkan.")
            return

        cursor.execute(
            "update denda set status_bayar = 'lunas' where id = %s",
            (denda_id,)
        )
        conn.commit()
        print(f"[✓] Denda berhasil dilunasi.")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()



def menu_laporan():
    while True:
        print("\n Laporan ")
        print("1. Peminjaman Aktif")
        print("2. Denda Belum Lunas")
        print("3. Riwayat per Anggota")
        print("4. Bayar Denda")
        print("0. Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            laporan_peminjaman_aktif()
        elif pilihan == "2":
            laporan_denda_belum_lunas()
        elif pilihan == "3":
            laporan_riwayat_anggota()
        elif pilihan == "4":
            bayar_denda()
        elif pilihan == "0":
            break
        else:
            print("[!] Pilihan tidak valid.")