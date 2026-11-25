#!/usr/bin/env python3
"""EVCONN Linux Wargame - Master Generator.

Password akun dan Final Flag dibaca dari password.txt.

Pemakaian:
    sudo python3 main.py

Perilaku:
- Jika lab belum dibuat: membuat Level 0 sampai Level 10.
- Jika lab sudah lengkap: menawarkan update password dari password.txt.
- Jika password.txt belum ada: membuatnya dari password.example.txt.

Format password.txt:
    password0=...   # password akun player
    password1=...   # password akun level1
    ...
    password10=...  # password akun level10
    final_flag=...

password.txt adalah file rahasia operator dan tidak boleh di-commit ke Git.
"""

from __future__ import annotations

import importlib.util
import os
import pwd
import re
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from types import ModuleType

BASE_DIR = Path(__file__).resolve().parent
HOME_ROOT = Path("/home")
PASSWORD_FILE = BASE_DIR / "password.txt"
PASSWORD_EXAMPLE = BASE_DIR / "password.example.txt"
LEVEL_FILES = {level: BASE_DIR / f"level-{level}.py" for level in range(11)}

USERNAMES = ["player"] + [f"level{level}" for level in range(1, 11)]
ACCOUNT_PASSWORD_KEYS = {
    "player": "password0",
    **{f"level{level}": f"password{level}" for level in range(1, 11)},
}
REQUIRED_COMMANDS = [
    "useradd", "userdel", "chpasswd", "systemctl", "ss", "curl",
    "ps", "grep", "find", "head", "tail", "wc", "chmod", "cat", "ls", "pwd",
]

LEVEL9_SERVICE = Path("/etc/systemd/system/evconn-level9.service")
LEVEL9_HELPER = Path("/var/lib/evconn-wargame/level9")
LEVEL9_WORKER = LEVEL9_HELPER / "backup-worker.py"
LEVEL10_SERVICE = Path("/etc/systemd/system/evconn-level10.service")
LEVEL10_HELPER = Path("/var/lib/evconn-wargame/level10")
LEVEL10_SERVER = LEVEL10_HELPER / "evconn-endpoint.py"

PASSWORD_KEYS = [f"password{level}" for level in range(11)]
CONFIG_KEYS = PASSWORD_KEYS + ["final_flag"]


class SetupError(Exception):
    """Kesalahan pemeriksaan atau konfigurasi lab."""


def print_banner() -> None:
    print("=" * 62)
    print("             EVCONN LINUX WARGAME")
    print("                  MASTER GENERATOR")
    print("=" * 62)
    print("Password dikelola melalui password.txt.")
    print("Gunakan hanya pada Ubuntu Server VM khusus untuk lab ini.\n")


def require_root() -> None:
    if os.geteuid() != 0:
        raise SetupError(
            "Master generator harus dijalankan sebagai root.\n"
            "Jalankan dengan: sudo python3 main.py"
        )


def check_python_version() -> None:
    if sys.version_info < (3, 10):
        raise SetupError(
            "EVCONN membutuhkan Python 3.10 atau lebih baru. "
            f"Versi saat ini: {sys.version.split()[0]}"
        )


def check_systemd() -> None:
    if not Path("/run/systemd/system").exists():
        raise SetupError(
            "systemd tidak terdeteksi sebagai init system aktif. "
            "Gunakan Ubuntu Server VM dengan systemd aktif."
        )


def check_commands() -> None:
    missing = [command for command in REQUIRED_COMMANDS if shutil.which(command) is None]
    if missing:
        package_map = {
            "ss": "iproute2", "curl": "curl", "ps": "procps",
            "grep": "grep", "find": "findutils", "head": "coreutils",
            "tail": "coreutils", "wc": "coreutils", "chmod": "coreutils",
            "cat": "coreutils", "ls": "coreutils", "pwd": "coreutils",
            "useradd": "passwd", "userdel": "passwd",
            "chpasswd": "passwd", "systemctl": "systemd",
        }
        packages = sorted({package_map[c] for c in missing if c in package_map})
        raise SetupError(
            "Command belum tersedia: " + ", ".join(missing) +
            "\nPasang dengan: sudo apt update && sudo apt install -y " +
            " ".join(packages)
        )


def check_generator_files() -> None:
    missing = [path.name for path in LEVEL_FILES.values() if not path.is_file()]
    if missing:
        raise SetupError(
            "Generator berikut tidak ditemukan: " + ", ".join(missing) +
            "\nPastikan main.py dan level-0.py sampai level-10.py satu folder."
        )


def ensure_password_file() -> None:
    """Buat password.txt dari template jika belum tersedia."""
    if PASSWORD_FILE.is_symlink():
        raise SetupError("password.txt tidak boleh berupa symbolic link.")

    if not PASSWORD_FILE.exists():
        if not PASSWORD_EXAMPLE.is_file():
            raise SetupError(
                "password.txt dan password.example.txt tidak ditemukan."
            )
        shutil.copyfile(PASSWORD_EXAMPLE, PASSWORD_FILE)
        os.chmod(PASSWORD_FILE, 0o600)
        raise SetupError(
            "password.txt baru saja dibuat dari template.\n"
            "Edit semua nilai placeholder terlebih dahulu:\n"
            "  sudo nano password.txt\n"
            "Setelah selesai, jalankan kembali:\n"
            "  sudo python3 main.py"
        )

    if not PASSWORD_FILE.is_file():
        raise SetupError("password.txt harus berupa file biasa.")

    # Hilangkan izin group/other jika file pernah dibuat dengan permission longgar.
    os.chmod(PASSWORD_FILE, 0o600)


def load_password_config() -> dict[str, str]:
    """Baca format key=value dan validasi semua password."""
    ensure_password_file()

    config: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        PASSWORD_FILE.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SetupError(
                f"Format password.txt salah pada baris {line_number}. "
                "Gunakan format key=value."
            )

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key not in CONFIG_KEYS:
            raise SetupError(
                f"Key '{key}' tidak dikenal pada baris {line_number}."
            )
        if key in config:
            raise SetupError(f"Key '{key}' ditulis lebih dari satu kali.")
        if not value:
            raise SetupError(f"Nilai '{key}' tidak boleh kosong.")
        if value.startswith(("GANTI_", "CHANGE_ME", "ISI_")):
            raise SetupError(
                f"Nilai '{key}' masih berupa placeholder. Edit password.txt."
            )
        if key.startswith("password"):
            if any(char in value for char in ("\n", "\r", ":")):
                raise SetupError(
                    f"{key} tidak boleh mengandung baris baru atau tanda titik dua (:)."
                )
        elif "\n" in value or "\r" in value:
            raise SetupError("Final Flag tidak boleh mengandung baris baru.")

        config[key] = value

    missing = [key for key in CONFIG_KEYS if key not in config]
    if missing:
        raise SetupError("Key berikut belum ada di password.txt: " + ", ".join(missing))

    return config


def load_generators() -> dict[int, ModuleType]:
    """Import generator Level 0 sampai Level 10."""
    modules: dict[int, ModuleType] = {}
    for level, path in LEVEL_FILES.items():
        spec = importlib.util.spec_from_file_location(
            f"evconn_level_{level}", path
        )
        if spec is None or spec.loader is None:
            raise SetupError(f"Tidak dapat memuat {path.name}.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        if not callable(getattr(module, f"create_level{level}", None)):
            raise SetupError(
                f"Fungsi create_level{level}() tidak ditemukan di {path.name}."
            )
        modules[level] = module
    return modules


def detect_installation_state() -> str:
    """Return clean, installed, atau partial berdasarkan akun dan file lab."""
    account_states = []
    for username in USERNAMES:
        try:
            pwd.getpwnam(username)
            account_states.append(True)
        except KeyError:
            account_states.append(False)

    home_states = [(HOME_ROOT / username).exists() for username in USERNAMES]
    service_states = [
        LEVEL9_SERVICE.exists(), LEVEL9_HELPER.exists(), LEVEL10_SERVICE.exists(),
        LEVEL10_HELPER.exists(),
    ]

    all_present = all(account_states) and all(home_states) and all(service_states)
    all_absent = not any(account_states) and not any(home_states) and not any(service_states)

    if all_present:
        return "installed"
    if all_absent:
        return "clean"
    return "partial"


def validate_passwords(config: dict[str, str]) -> None:
    """Validasi password menggunakan aturan generator tiap level."""
    for level in range(11):
        password = config[f"password{level}"]
        if not password:
            raise SetupError(f"password{level} tidak boleh kosong.")
        if ":" in password or "\n" in password or "\r" in password:
            raise SetupError(
                f"password{level} tidak boleh mengandung ':' atau baris baru."
            )


def set_all_account_passwords(config: dict[str, str]) -> None:
    """Perbarui seluruh password akun dalam satu pemanggilan chpasswd."""
    lines = []
    for username, key in ACCOUNT_PASSWORD_KEYS.items():
        lines.append(f"{username}:{config[key]}")
    subprocess.run(
        ["chpasswd"],
        input="\n".join(lines) + "\n",
        text=True,
        check=True,
    )


def write_secret_file(path: Path, content: str, uid: int, gid: int, mode: int = 0o400) -> None:
    """Tulis ulang file rahasia dan pulihkan owner/permission."""
    if not path.parent.is_dir():
        raise SetupError(f"Direktori target tidak ditemukan: {path.parent}")
    path.write_text(content, encoding="utf-8")
    os.chown(path, uid, gid)
    os.chmod(path, mode)


def restore_home_permissions(home_dir: Path, uid: int, gid: int) -> None:
    """Pastikan direktori challenge dimiliki user level terkait."""
    os.chown(home_dir, uid, gid)
    os.chmod(home_dir, 0o700)
    for item in home_dir.rglob("*"):
        os.chown(item, uid, gid)
        os.chmod(item, 0o700 if item.is_dir() else 0o400)


def account_ids(username: str) -> tuple[int, int]:
    account = pwd.getpwnam(username)
    return account.pw_uid, account.pw_gid


def preflight_update(modules: dict[int, ModuleType]) -> int:
    """Pastikan seluruh target update ada sebelum mengubah apa pun."""
    required_paths = [
        HOME_ROOT / "player" / "pw-evconn.md",
        HOME_ROOT / "level1" / "-",
        HOME_ROOT / "level2" / ".secret",
        HOME_ROOT / "level3" / "cloud-audit.log",
        HOME_ROOT / "level4" / "cloud",
        HOME_ROOT / "level5" / "cloud",
        HOME_ROOT / "level6" / "deployment.log",
        HOME_ROOT / "level7" / "cloud" / "reports",
        HOME_ROOT / "level8" / "cloud" / "credentials.txt",
        HOME_ROOT / "level9" / "cloud",
        LEVEL9_WORKER,
        LEVEL10_SERVER,
    ]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise SetupError(
            "Instalasi terlihat belum lengkap. Target update tidak ditemukan:\n  - "
            + "\n  - ".join(missing)
        )

    # Pastikan service Level 9 dan Level 10 dikenali oleh systemd.
    for service in ("evconn-level9.service", "evconn-level10.service"):
        result = subprocess.run(
            ["systemctl", "cat", service],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            raise SetupError(f"Service {service} tidak ditemukan oleh systemd.")

    # Ambil port endpoint lama agar port Level 10 tidak berubah saat update.
    server_source = LEVEL10_SERVER.read_text(encoding="utf-8")
    match = re.search(r"^PORT\s*=\s*(\d+)\s*$", server_source, re.MULTILINE)
    if not match:
        raise SetupError(
            "Nomor port pada script Level 10 tidak ditemukan. "
            "Pulihkan instalasi Level 10 sebelum update."
        )
    return int(match.group(1))


def update_challenge_secrets(
    config: dict[str, str],
    modules: dict[int, ModuleType],
    port_level10: int,
) -> None:
    """Perbarui semua password yang ditanam di challenge tanpa membuat ulang akun."""
    # Level 0: password1 di pw-evconn.md.
    uid, gid = account_ids("player")
    write_secret_file(
        HOME_ROOT / "player" / "pw-evconn.md",
        modules[0].PASSWORD_FILE_HEADER + config["password1"] + "\n",
        uid, gid,
    )

    # Level 1: password2 di file bernama '-'.
    uid, gid = account_ids("level1")
    write_secret_file(HOME_ROOT / "level1" / "-", config["password2"] + "\n", uid, gid)

    # Level 2: password3 di hidden file.
    uid, gid = account_ids("level2")
    write_secret_file(HOME_ROOT / "level2" / ".secret", config["password3"] + "\n", uid, gid)

    # Level 3: password4 di cloud audit log.
    uid, gid = account_ids("level3")
    write_secret_file(
        HOME_ROOT / "level3" / "cloud-audit.log",
        modules[3]._build_system_log(config["password4"]),
        uid, gid,
    )

    # Level 4: recovery token.
    uid, gid = account_ids("level4")
    modules[4]._build_cloud_directories(HOME_ROOT / "level4", config["password5"])
    restore_home_permissions(HOME_ROOT / "level4", uid, gid)

    # Level 5: file log berukuran besar.
    uid, gid = account_ids("level5")
    modules[5]._build_cloud_logs(HOME_ROOT / "level5", config["password6"])
    restore_home_permissions(HOME_ROOT / "level5", uid, gid)

    # Level 6: deployment log.
    uid, gid = account_ids("level6")
    write_secret_file(
        HOME_ROOT / "level6" / "deployment.log",
        modules[6]._build_deployment_log(config["password7"]),
        uid, gid,
    )

    # Level 7: laporan yang memiliki jumlah baris tertentu.
    uid, gid = account_ids("level7")
    modules[7]._build_reports(HOME_ROOT / "level7", config["password8"])
    restore_home_permissions(HOME_ROOT / "level7", uid, gid)

    # Level 8: credentials file tetap sengaja memiliki permission 000.
    uid, gid = account_ids("level8")
    write_secret_file(
        HOME_ROOT / "level8" / "cloud" / "credentials.txt",
        "EVCONN CLOUD ACCESS\n"
        "account=level9\n"
        f"password={config['password9']}\n",
        uid, gid, mode=0o000,
    )

    # Level 9: stop service sebelum mengganti worker yang membawa password10.
    subprocess.run(["systemctl", "stop", "evconn-level9.service"], check=True)
    uid, gid = account_ids("level9")
    worker_source = modules[9]._build_worker_script(
        config["password10"], uid, gid, HOME_ROOT / "level9"
    )
    LEVEL9_WORKER.write_text(worker_source, encoding="utf-8")
    os.chown(LEVEL9_WORKER, 0, 0)
    os.chmod(LEVEL9_WORKER, 0o700)

    # Level 10: ganti Final Flag, pertahankan port yang sudah ditemukan peserta.
    subprocess.run(["systemctl", "stop", "evconn-level10.service"], check=True)
    uid, gid = account_ids("level10")
    server_source = modules[10]._build_server_script(
        config["final_flag"], uid, gid, port_level10
    )
    LEVEL10_SERVER.write_text(server_source, encoding="utf-8")
    os.chown(LEVEL10_SERVER, 0, 0)
    os.chmod(LEVEL10_SERVER, 0o700)


def restart_and_verify_services(
    config: dict[str, str],
    modules: dict[int, ModuleType],
) -> None:
    """Aktifkan ulang worker dan endpoint setelah secret diperbarui."""
    subprocess.run(["systemctl", "restart", "evconn-level9.service"], check=True)
    modules[9]._wait_until_worker_ready(HOME_ROOT / "level9")

    subprocess.run(["systemctl", "restart", "evconn-level10.service"], check=True)

    server_source = LEVEL10_SERVER.read_text(encoding="utf-8")
    match = re.search(r"^PORT\s*=\s*(\d+)\s*$", server_source, re.MULTILINE)
    if not match:
        raise SetupError("Port endpoint Level 10 tidak ditemukan setelah update.")
    modules[10]._verify_endpoint(int(match.group(1)), config["final_flag"])


def update_existing_lab(config: dict[str, str], modules: dict[int, ModuleType]) -> None:
    """Terapkan password.txt ke akun dan seluruh challenge yang sudah terpasang."""
    port = preflight_update(modules)
    print("\n[1/4] Memperbarui password akun Linux...")
    set_all_account_passwords(config)

    print("[2/4] Memperbarui password yang tertanam di challenge...")
    update_challenge_secrets(config, modules, port)

    print("[3/4] Mengaktifkan ulang service Level 9 dan Level 10...")
    restart_and_verify_services(config, modules)

    print("[4/4] Update selesai.")
    print("Semua password akun dan password jawaban challenge sudah mengikuti password.txt.")


def create_all_levels(config: dict[str, str], modules: dict[int, ModuleType]) -> None:
    """Buat seluruh akun dan challenge dari konfigurasi password.txt."""
    print("\n=== PEMBUATAN CHALLENGE ===")

    modules[0].create_level0(
        config["password0"], config["password1"], home_root=HOME_ROOT
    )
    print("[OK] Level 0 dibuat — akun player")

    for level in range(1, 10):
        function = getattr(modules[level], f"create_level{level}")
        function(
            config[f"password{level}"],
            config[f"password{level + 1}"],
            home_root=HOME_ROOT,
        )
        print(f"[OK] Level {level} dibuat — akun level{level}")

    modules[10].create_level10(
        config["password10"], config["final_flag"], home_root=HOME_ROOT
    )
    print("[OK] Level 10 dibuat — final endpoint aktif")


def main() -> int:
    print_banner()

    try:
        require_root()
        check_python_version()
        check_systemd()
        check_commands()
        check_generator_files()

        config = load_password_config()
        validate_passwords(config)
        modules = load_generators()

        state = detect_installation_state()

        if state == "clean":
            print("Instalasi belum ditemukan. Mode: PEMBUATAN BARU.")
            create_all_levels(config, modules)
            print("\n[BERHASIL] EVCONN Linux Wargame Level 0–10 berhasil dibuat.")
            print("Akun awal peserta: player")
            print("Mulai dengan: su - player")
            return 0

        if state == "installed":
            print("Instalasi EVCONN sudah ditemukan. Mode: UPDATE PASSWORD.")
            print("Akun Linux dan password jawaban challenge akan diperbarui")
            print("mengikuti nilai terbaru di password.txt.")
            answer = input("\nLanjutkan update? [y/N]: ").strip().lower()
            if answer not in ("y", "yes"):
                print("Update dibatalkan. Tidak ada perubahan.")
                return 0

            update_existing_lab(config, modules)
            print("\n[BERHASIL] Password EVCONN berhasil diperbarui.")
            return 0

        raise SetupError(
            "Instalasi EVCONN terdeteksi dalam kondisi tidak lengkap (partial).\n"
            "Untuk mencegah akun atau challenge tertimpa, main.py tidak melanjutkan.\n"
            "Pulihkan snapshot VM bersih atau periksa instalasi yang belum selesai."
        )

    except KeyboardInterrupt:
        print("\n[DIHENTIKAN] Proses dibatalkan oleh operator.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
