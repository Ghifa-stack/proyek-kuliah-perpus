from db import test_koneksi
from modules.petugas import menu_petugas
from modules.anggota import menu_anggota
from modules.buku import menu_buku
from modules.peminjaman import menu_peminjaman
from modules.pengembalian import menu_pengembalian
from modules.laporan import menu_laporan


def tampilkan_menu():
    print("SISTEM MANAJEMEN PERPUSTAKAAN")
    print("1. Manajemen Petugas")
    print("2. Manajemen Anggota")
    print("3. Manajemen Buku")
    print("4. Peminjaman Buku")
    print("5. Pengembalian Buku")
    print("6. Laporan")
    print("0. Keluar")



def main():
    print("\nSelamat datang di Sistem Manajemen Perpustakaan")
    test_koneksi()

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu: ").strip()

        if pilihan == "1":
            menu_petugas()
        elif pilihan == "2":
            menu_anggota()
        elif pilihan == "3":
            menu_buku()
        elif pilihan == "4":
            menu_peminjaman()
        elif pilihan == "5":
            menu_pengembalian()
        elif pilihan == "6":
            menu_laporan()
        elif pilihan == "0":
            print("Terima kasih, sampai jumpa.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    main()
