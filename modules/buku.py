from db import menghubungkan_koneksi


def tambah_buku():
    print("Tambah Buku Baru")
    judul = input("Judul buku   : ")
    kategori = input("Kategori     : ")
    tahun_terbit = input("Tahun terbit : ")
    stok = input("Stok         : ")

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        cursor.execute(
            "insert into buku (judul, kategori, tahun_terbit, stok) values (%s, %s, %s, %s)",
            (judul, kategori, tahun_terbit, stok)
        )
        buku_id = cursor.lastrowid

        print("Masukkan penulis buku (boleh lebih dari satu).")
        while True:
            nama_penulis = input("Nama penulis (Enter untuk selesai): ").strip()
            if not nama_penulis:
                break

            cursor.execute("select id from penulis where nama = %s", (nama_penulis,))
            penulis = cursor.fetchone()

            if penulis:
                penulis_id = penulis[0]
                print(f"  Penulis '{nama_penulis}' sudah ada, langsung dihubungkan.")
            else:
                negara = input(f"  Negara asal '{nama_penulis}': ")
                cursor.execute(
                    "insert into penulis (nama, negara) values (%s, %s)",
                    (nama_penulis, negara)
                )
                penulis_id = cursor.lastrowid
                print(f"  Penulis '{nama_penulis}' berhasil ditambahkan.")

            cursor.execute(
                "insert into buku_penulis (buku_id, penulis_id) values (%s, %s)",
                (buku_id, penulis_id)
            )

        conn.commit()
        print(f"\n Buku '{judul}' berhasil ditambahkan dengan ID: {buku_id}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def lihat_semua_buku():
    print("\n Daftar Buku ")

    conn = menghubungkan_koneksi()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
            select b.id, b.judul, b.kategori, b.tahun_terbit, b.stok, b.status,
                   group_concat(p.nama separator ', ') as penulis
            from buku b
            left join buku_penulis bp on b.id = bp.buku_id
            left join penulis p on bp.penulis_id = p.id
            group by b.id
        """)
        rows = cursor.fetchall()

        if not rows:
            print("Belum ada data buku.")
            return

        print(f"{'ID':<5} {'Judul':<30} {'Kategori':<15} {'Tahun':<7} {'Stok':<6} {'Status':<12} {'Penulis'}")
        
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<30} {row[2]:<15} {row[3]:<7} {row[4]:<6} {row[5]:<12} {row[6]}")

    except Exception as e:
        print(f"[error] {e}")
    finally:
        cursor.close()
        conn.close()


def cari_buku_by_id(buku_id):
    
    conn = menghubungkan_koneksi()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            "select id, judul, stok, status from buku where id = %s",
            (buku_id,)
        )
        return cursor.fetchone()

    except Exception as e:
        print(f"[error] {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def update_status_buku(buku_id, status, cursor):
    
    cursor.execute(
        "update buku set status = %s where id = %s",
        (status, buku_id)
    )


def menu_buku():
    while True:
        print("\n Manajemen Buku ")
        print("1. Tambah Buku Baru")
        print("2. Lihat Semua Buku")
        print("0. Kembali")

        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            tambah_buku()
        elif pilihan == "2":
            lihat_semua_buku()
        elif pilihan == "0":
            break
        else:
            print("[!] Pilihan tidak valid.")