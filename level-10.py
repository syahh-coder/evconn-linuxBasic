#!/usr/bin/env python3
"""Generator challenge Level 10 - EVCONN Cloud Wargame.

Challenge: The Hidden Endpoint

Fungsi utama:
    create_level10(password_level10, final_flag, home_root="/home")

Script membuat akun Linux level10, README.md, hint.md, dan layanan HTTP
lokal yang hanya listen pada 127.0.0.1. Peserta mencari port layanan
menggunakan `ss -tuln`, lalu mengaksesnya menggunakan `curl`.

Layanan didaftarkan sebagai systemd service agar otomatis aktif kembali
setelah Ubuntu Server reboot, termasuk ketika VM dibagikan sebagai OVA.

Jalankan secara mandiri di Ubuntu Server:
    sudo python3 level-10.py

Password Level 10 harus sama dengan password yang ditemukan peserta
pada Level 9.

Prasyarat pada Ubuntu Server:
    sudo apt update
    sudo apt install -y iproute2 curl
"""

from __future__ import annotations

import getpass
import os
import pwd
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

USERNAME = "level10"
DEFAULT_HOME_ROOT = Path("/home")
HELPER_BASE = Path("/var/lib/evconn-wargame")
HELPER_DIR_NAME = "level10"
SERVER_FILENAME = "evconn-endpoint.py"
SERVICE_NAME = "evconn-level10.service"
SERVICE_PATH = Path("/etc/systemd/system") / SERVICE_NAME

README_CONTENT = """# EVCONN CLOUD WARGAME
## LEVEL 10 — THE HIDDEN ENDPOINT

### CERITA

Ini level terakhir. Tim Cloud Operations EVCONN menjalankan sebuah
layanan internal di virtual machine ini, dan layanan itu menyimpan pesan
terakhir dari administrator.

Masalahnya, nomor port-nya nggak tercatat di dokumentasi mana pun.

Admin yang sama meninggalkan pesan:

    "Servernya sudah nyala. Port-nya saya lupa, cek aja port mana yang
    lagi dipakai. Layanannya internal, jadi nggak bisa dibuka dari luar.
    Semoga kali ini tagihan cloud nggak ikut muncul di responsnya."

Layanan itu hanya bisa dihubungi dari dalam server ini, lewat alamat
lokal `127.0.0.1`. Kamu sudah ada di dalamnya. Yang belum kamu tahu
tinggal pintu mana yang harus diketuk.
### TUJUAN

1. Baca `cloud/service-status.txt` untuk mengetahui alamat layanan.
2. Periksa port yang sedang listening pada server.
3. Temukan layanan EVCONN yang menggunakan alamat `127.0.0.1`.
4. Akses layanan tersebut menggunakan `curl`.
5. Temukan Final Flag sebagai bukti bahwa seluruh level berhasil diselesaikan.

### PETUNJUK

1. Gunakan `ss -tuln` untuk melihat port yang sedang listening.
2. Perhatikan kolom `Local Address:Port`.
3. Cari alamat yang diawali `127.0.0.1`.
4. Gunakan `curl` untuk mengakses alamat tersebut.

Selamat! Ini adalah tantangan terakhir EVCONN Cloud Wargame.

**EVCONN STUDY GROUP — Cloud & Linux Fundamentals Lab**
"""

HINT_CONTENT = """# HINT — LEVEL 10
## THE HIDDEN ENDPOINT

Command yang mungkin kamu butuhkan:

- `pwd`      : melihat lokasi direktori saat ini.
- `ls`       : melihat isi direktori.
- `cat`      : membaca file.
- `ss -tuln` : melihat port yang sedang listening.
- `curl`     : mengakses layanan melalui HTTP.

Petunjuk:

1. Baca informasi layanan:

       cat cloud/service-status.txt

2. Jalankan:

       ss -tuln

3. Cari port dengan alamat lokal `127.0.0.1`.
4. Gunakan port yang ditemukan untuk mengakses layanan.

Contoh pola:

    curl http://127.0.0.1:PORT

Ganti `PORT` dengan nomor port yang kamu temukan.

Layanan ini hanya tersedia dari dalam server.
"""


def _require_root() -> None:
    """Pastikan generator dijalankan dengan hak akses root."""
    if os.geteuid() != 0:
        raise PermissionError(
            "Script harus dijalankan sebagai root. Gunakan: sudo python3 level-10.py"
        )


def _require_commands() -> None:
    """Pastikan command yang dibutuhkan tersedia."""
    required = ("ss", "curl", "systemctl")
    missing = [command for command in required if shutil.which(command) is None]
    if missing:
        packages = []
        if "ss" in missing:
            packages.append("iproute2")
        if "curl" in missing:
            packages.append("curl")
        package_note = (
            " Pasang dengan: sudo apt update && sudo apt install -y "
            + " ".join(packages)
            if packages
            else ""
        )
        raise RuntimeError(
            "Command berikut belum tersedia: " + ", ".join(missing) + "." + package_note
        )


def _validate_password(password: str, label: str) -> None:
    """Validasi password untuk chpasswd."""
    if not isinstance(password, str) or not password:
        raise ValueError(f"{label} tidak boleh kosong.")
    if any(char in password for char in ("\n", "\r", ":")):
        raise ValueError(
            f"{label} tidak boleh mengandung baris baru atau tanda titik dua (:)."
        )


def _validate_flag(final_flag: str) -> None:
    """Validasi Final Flag agar aman ditulis ke script server."""
    if not isinstance(final_flag, str) or not final_flag.strip():
        raise ValueError("Final Flag tidak boleh kosong.")
    if "\n" in final_flag or "\r" in final_flag:
        raise ValueError("Final Flag tidak boleh mengandung baris baru.")


def _set_linux_password(username: str, password: str) -> None:
    """Atur password akun melalui stdin."""
    subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}\n",
        text=True,
        check=True,
    )


def _find_available_port() -> int:
    """Pilih port lokal yang tersedia untuk endpoint final."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _build_server_script(
    final_flag: str,
    target_uid: int,
    target_gid: int,
    port: int,
) -> str:
    """Buat script endpoint root-only yang menurunkan privilege ke level10."""
    return f"""#!/usr/bin/env python3
# EVCONN final endpoint. File ini hanya dapat dibaca oleh root.

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TARGET_UID = {target_uid}
TARGET_GID = {target_gid}
PORT = {port}
FINAL_FLAG = {final_flag!r}


class EVCONNHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/flag"):
            body = b"Endpoint not found.\\n"
            self.send_response(404)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        response = (
            "EVCONN CLOUD WARGAME - FINAL ENDPOINT\\n"
            "status=success\\n"
            "message=Selamat! Kamu berhasil menyelesaikan seluruh level.\\n"
            "final_flag=" + FINAL_FLAG + "\\n"
        )
        body = response.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Tidak menampilkan access log agar terminal peserta tetap rapi.
        return


# systemd menjalankan script sebagai root. Setelah konfigurasi dimuat,
# proses menurunkan hak akses menjadi akun level10 sebelum membuka port.
os.setgroups([])
os.setgid(TARGET_GID)
os.setuid(TARGET_UID)

server = ThreadingHTTPServer(("127.0.0.1", PORT), EVCONNHandler)
server.daemon_threads = True
server.serve_forever(poll_interval=0.5)
"""


def _build_systemd_unit(server_script: Path) -> str:
    """Buat unit systemd agar endpoint otomatis aktif setelah reboot."""
    return f"""[Unit]
Description=EVCONN Level 10 Hidden Endpoint
After=network.target

[Service]
Type=simple
ExecStart={sys.executable} {server_script}
Restart=on-failure
RestartSec=2
KillSignal=SIGTERM
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
"""


def _verify_endpoint(port: int, final_flag: str) -> None:
    """Pastikan endpoint merespons dan mengirim flag yang benar."""
    url = f"http://127.0.0.1:{port}/"
    deadline = time.monotonic() + 8
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1) as response:
                body = response.read().decode("utf-8", errors="replace")
            if final_flag not in body:
                raise RuntimeError("Endpoint aktif, tetapi respons Final Flag tidak sesuai.")
            return
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
            time.sleep(0.2)

    raise RuntimeError(
        f"Endpoint tidak merespons pada 127.0.0.1:{port}. "
        f"Periksa service dengan: systemctl status {SERVICE_NAME}. "
        f"Detail: {last_error}"
    )


def create_level10(
    password_level10: str,
    final_flag: str,
    home_root: str | Path = DEFAULT_HOME_ROOT,
) -> Path:
    """Buat akun dan final challenge Level 10.

    Args:
        password_level10: Password untuk login ke akun Linux `level10`.
                          Password ini berasal dari Level 9.
        final_flag: Flag akhir yang akan ditampilkan oleh endpoint HTTP.
        home_root: Direktori induk home akun. Default: `/home`.

    Returns:
        Path menuju home directory akun `level10`.
    """
    _require_root()
    _require_commands()
    _validate_password(password_level10, "Password Level 10")
    _validate_flag(final_flag)

    home_root = Path(home_root).expanduser().resolve()
    home_root.mkdir(parents=True, exist_ok=True)
    home_dir = home_root / USERNAME
    helper_dir = HELPER_BASE / HELPER_DIR_NAME

    try:
        pwd.getpwnam(USERNAME)
    except KeyError:
        pass
    else:
        raise RuntimeError(
            f"Akun '{USERNAME}' sudah ada. Periksa VM terlebih dahulu."
        )

    if home_dir.exists():
        raise RuntimeError(
            f"Direktori '{home_dir}' sudah ada. Tidak ada file yang ditimpa."
        )

    if helper_dir.exists():
        raise RuntimeError(
            f"Direktori helper '{helper_dir}' sudah ada. "
            "Periksa sisa instalasi Level 10 sebelum mencoba lagi."
        )

    if SERVICE_PATH.exists():
        raise RuntimeError(
            f"Unit '{SERVICE_PATH}' sudah ada. Periksa service lama sebelum mencoba lagi."
        )

    user_created = False
    helper_created = False
    unit_created = False
    service_enable_attempted = False

    try:
        subprocess.run(
            [
                "useradd",
                "--create-home",
                "--home-dir",
                str(home_dir),
                "--shell",
                "/bin/bash",
                USERNAME,
            ],
            check=True,
        )
        user_created = True

        _set_linux_password(USERNAME, password_level10)
        account = pwd.getpwnam(USERNAME)

        cloud_dir = home_dir / "cloud"
        cloud_dir.mkdir(parents=True, exist_ok=True)

        (home_dir / "README.md").write_text(README_CONTENT, encoding="utf-8")
        (home_dir / "hint.md").write_text(HINT_CONTENT, encoding="utf-8")
        (cloud_dir / "service-status.txt").write_text(
            "EVCONN INTERNAL SERVICE\n"
            "service=evconn-final-endpoint\n"
            "bind_address=127.0.0.1\n"
            "port=discover-with-ss\n"
            "status=running\n",
            encoding="utf-8",
        )

        # Atur kepemilikan seluruh konten home kepada akun level10.
        os.chown(home_dir, account.pw_uid, account.pw_gid)
        for item in home_dir.rglob("*"):
            os.chown(item, account.pw_uid, account.pw_gid)

        os.chmod(home_dir, 0o700)
        for directory in [p for p in home_dir.rglob("*") if p.is_dir()]:
            os.chmod(directory, 0o700)

        for file_path in [p for p in home_dir.rglob("*") if p.is_file()]:
            os.chmod(file_path, 0o400)

        # Siapkan script server pada direktori yang hanya dapat diakses root.
        HELPER_BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(HELPER_BASE, 0o700)
        helper_dir.mkdir(mode=0o700)
        helper_created = True
        os.chmod(helper_dir, 0o700)

        port = _find_available_port()
        server_script = helper_dir / SERVER_FILENAME
        server_script.write_text(
            _build_server_script(
                final_flag,
                account.pw_uid,
                account.pw_gid,
                port,
            ),
            encoding="utf-8",
        )
        os.chmod(server_script, 0o700)

        # Script endpoint dan flag hanya dapat dibaca oleh root.
        unit_content = _build_systemd_unit(server_script)
        SERVICE_PATH.write_text(unit_content, encoding="utf-8")
        os.chown(SERVICE_PATH, 0, 0)
        os.chmod(SERVICE_PATH, 0o644)
        unit_created = True

        subprocess.run(["systemctl", "daemon-reload"], check=True)
        service_enable_attempted = True
        subprocess.run(
            ["systemctl", "enable", "--now", SERVICE_NAME],
            check=True,
        )

        _verify_endpoint(port, final_flag)
        return home_dir

    except Exception:
        if service_enable_attempted:
            subprocess.run(
                ["systemctl", "disable", "--now", SERVICE_NAME],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if unit_created and SERVICE_PATH.exists():
            SERVICE_PATH.unlink(missing_ok=True)
            subprocess.run(
                ["systemctl", "daemon-reload"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if helper_created and helper_dir.exists():
            shutil.rmtree(helper_dir, ignore_errors=True)

        if user_created:
            subprocess.run(
                ["userdel", "--remove", USERNAME],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if home_dir.exists():
                shutil.rmtree(home_dir, ignore_errors=True)

        raise


def main() -> None:
    """Mode mandiri untuk menguji generator Level 10."""
    _require_root()

    print("=== EVCONN CLOUD WARGAME: GENERATOR LEVEL 10 ===")
    print("Challenge: The Hidden Endpoint\n")

    print("Masukkan password untuk login ke akun level10.")
    password_level10 = getpass.getpass("Password Level 10: ")
    password_level10_confirm = getpass.getpass("Ulangi Password Level 10: ")

    if password_level10 != password_level10_confirm:
        raise SystemExit("Password Level 10 tidak cocok. Tidak ada akun yang dibuat.")

    print("\nMasukkan Final Flag EVCONN.")
    final_flag = getpass.getpass("Final Flag: ")
    final_flag_confirm = getpass.getpass("Ulangi Final Flag: ")

    if final_flag != final_flag_confirm:
        raise SystemExit("Final Flag tidak cocok. Tidak ada akun yang dibuat.")

    created_home = create_level10(password_level10, final_flag)

    print("\n[BERHASIL] Final Challenge Level 10 berhasil dibuat.")
    print(f"Akun Linux : {USERNAME}")
    print(f"Home       : {created_home}")
    print(f"Service    : {SERVICE_NAME}")
    print("Endpoint   : aktif pada 127.0.0.1")
    print("Persistence: otomatis aktif kembali setelah VM reboot")
    print("\nUntuk menguji sebagai peserta, jalankan:")
    print("  su - level10")
    print("  cat README.md")
    print("  cat hint.md")
    print("  cat cloud/service-status.txt")
    print("  ss -tuln")
    print("\nCari port layanan pada alamat 127.0.0.1, lalu jalankan:")
    print("  curl http://127.0.0.1:PORT")
    print("\nSimpan Final Flag di catatan operator. Jangan bagikan kepada peserta.")


if __name__ == "__main__":
    main()
