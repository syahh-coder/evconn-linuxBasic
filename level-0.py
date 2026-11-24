#!/usr/bin/env python3
"""Generator Level 0 - EVCONN Linux Wargame.

Level 0 adalah titik awal peserta. Script ini membuat akun `player`,
README.md, dan pw-evconn.md yang berisi password untuk masuk ke level1.

Fungsi utama:
    create_level0(player_password, password_level1, home_root="/home")

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-0.py

Script ini dirancang agar nantinya dapat dipanggil oleh main.py.
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import subprocess
from pathlib import Path

USERNAME = "player"
DEFAULT_HOME_ROOT = Path("/home")

README_CONTENT = """# EVCONN LINUX WARGAME
## SELAMAT DATANG DI LEVEL 0!

Selamat datang di EVCONN Linux Wargame!

Dalam lab ini, kamu akan mempelajari dasar-dasar Linux
melalui serangkaian tantangan yang harus diselesaikan
secara bertahap menggunakan terminal.

Setiap level memiliki tantangan yang berbeda. Untuk
melanjutkan ke level berikutnya, kamu harus menemukan
password yang disediakan di dalam tantangan tersebut.

Password yang ditemukan digunakan untuk masuk ke akun
Linux pada level selanjutnya.

### TUJUAN PEMBELAJARAN

Setelah menyelesaikan seluruh tantangan, kamu diharapkan mampu:

1. Mengenal lingkungan Linux dan penggunaan terminal.
2. Menavigasi direktori dan mengelola file.
3. Menggunakan perintah-perintah dasar Linux.
4. Memahami file, direktori, permission, dan ownership.
5. Menggabungkan beberapa perintah untuk menyelesaikan masalah.

### ATURAN PERMAINAN

1. Mulai permainan dari Level 0 dan lanjutkan secara berurutan.
2. Setiap level memiliki password untuk masuk ke level berikutnya.
3. Baca README.md pada setiap level sebelum mengerjakan tantangan.
4. Gunakan perintah Linux yang tersedia untuk menyelesaikan misi.
5. Jangan melewati level. Cobalah menyelesaikan setiap tantangan sendiri.

### MEMULAI PERMAINAN

Saat ini kamu berada di Level 0.

Level 0 merupakan tahap pengenalan. Belum ada tantangan
yang perlu diselesaikan.

Untuk mendapatkan password masuk ke Level 1, baca file
yang telah disediakan menggunakan perintah berikut:

    cat pw-evconn.md

Simpan password tersebut. Password itu digunakan untuk
masuk ke akun Linux `level1`.

### MASUK KE LEVEL 1

Setelah mendapatkan password, jalankan perintah:

    su - level1

Masukkan password yang telah kamu temukan ketika diminta.

Jika berhasil, kamu akan masuk ke lingkungan Level 1.
Baca petunjuk tantangan dengan perintah:

    cat README.md

### SELAMAT BERMAIN!

Explore, Learn, and Hack Responsibly.

EVCONN STUDY GROUP
Linux Fundamentals Lab
"""