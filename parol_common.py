#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parol Repair - ortak motor (dil, katalog, calistirici)
Copyright (C) 2026 Ermedsoft - Eren Baytak Yazılım
GNU GPL v3 or later. Bu program HICBIR GARANTI icermez.
"""
import os
import pwd
import shutil
import subprocess
from datetime import datetime

APP_NAME      = "Parol Repair"
VERSION       = "4.0.0"
COPYRIGHT     = "© 2026 Ermedsoft - Eren Baytak Yazılım"
LICENSE_LINE  = "GNU GPL v3 Lisansı | Açık Kaynak Yazılım"
LICENSE_LINE_EN = "GNU GPL v3 License | Open Source Software"
LOG_FILE      = "/var/log/parol_repair.log"
GPL_URL       = "https://www.gnu.org/licenses/gpl-3.0.html"


# ---------------------------------------------------------------- dil algilama
def detect_lang():
    ov = os.environ.get("PAROL_LANG", "").strip().lower()
    if ov in ("tr", "en"):
        return ov
    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        val = os.environ.get(var, "")
        if val:
            return "tr" if val.lower().startswith("tr") else "en"
    return "en"


LANG = detect_lang()

_ASCII_MAP = str.maketrans({
    "ş": "s", "Ş": "S", "ı": "i", "İ": "I", "ğ": "g", "Ğ": "G",
    "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C",
    "©": "(c)", "→": "->", "←": "<-", "•": "-", "—": "-", "–": "-",
})


def ascii_tr(s):
    """curses icin guvenli ASCII donusumu."""
    return str(s).translate(_ASCII_MAP).encode("ascii", "replace").decode("ascii")


UI = {
    "tr": {
        "title": "Parol Repair",
        "subtitle": "Sisteminiz bir sorunla karşılaştı ve onarılması gerekiyor.",
        "tui_sub": "Tam Sistem Onarım Aracı - Debian/Ubuntu",
        "troubleshoot": "Sorun Gider",
        "advanced": "Gelişmiş Seçenekler",
        "cont_exit": "Devam Et (Çıkış)",
        "reboot": "Sistemi Yeniden Başlat",
        "reboot_q": "Sistem şimdi yeniden başlatılacak. Onaylıyor musunuz?",
        "back": "Geri Dön",
        "exit": "Çıkış",
        "exit_q": "Parol Repair'dan çıkmak istiyor musunuz?",
        "select_cat": "Onarmak istediğiniz kategoriyi seçin",
        "auto": "Otomatik Onarım",
        "auto_desc": "Tüm güvenli onarımları sırayla çalıştırır",
        "run_cat": "Bu kategorideki tüm güvenli işlemleri çalıştır",
        "terminal": "Komut İstemi",
        "view_log": "Günlüğü Görüntüle",
        "repairing": "Onarılıyor",
        "wait": "Lütfen bekleyin... İşlem devam ediyor.",
        "done": "Onarım Tamamlandı",
        "ok": "BAŞARILI",
        "fail": "HATA",
        "skip": "ATLANDI",
        "timeout": "ZAMAN AŞIMI",
        "success": "Başarılı",
        "details": "Ayrıntılı günlük",
        "confirm": "Onay Gerekli",
        "high": "Bu işlem YÜKSEK RİSKLİ! Oturumunuz veya cihazlarınız etkilenebilir.",
        "ask": "Devam edilsin mi?",
        "press": "Devam etmek için bir tuşa basın...",
        "running": "Çalıştırılıyor",
        "command": "Komut",
        "result": "Sonuç",
        "risk_low": "GÜVENLİ",
        "risk_med": "ORTA",
        "risk_high": "YÜKSEK",
        "nav_main": "OK: Gezin   ENTER: Seç   ESC/Q: Çıkış",
        "nav_cat": "OK: Gezin   ENTER: Çalıştır   B/ESC: Geri   Q: Çıkış",
        "nav_gui": "Enter=Seç  ↑↓=Gezin  Esc=Geri  F11=Tam Ekran",
        "small": "Terminal çok küçük! En az 80x24 gerekli.",
        "log_empty": "Günlük dosyası boş veya yok.",
        "root_needed": "Bu araç root yetkisi gerektirir: sudo parol",
        "no_user": "Masaüstü kullanıcısı bulunamadı (sudo ile çalıştırın).",
        "no_tool": "Gerekli araç yok",
        "abort": "İşlem kullanıcı tarafından durduruldu.",
        "term_fail": "Terminal açılamadı.",
        "license": LICENSE_LINE,
        "version_line": "Parol Repair v" + VERSION + " - Debian/Ubuntu Recovery",
    },
    "en": {
        "title": "Parol Repair",
        "subtitle": "Your system ran into a problem and needs to be repaired.",
        "tui_sub": "Full System Repair Tool - Debian/Ubuntu",
        "troubleshoot": "Troubleshoot",
        "advanced": "Advanced options",
        "cont_exit": "Continue (Exit)",
        "reboot": "Restart the system",
        "reboot_q": "The system will restart now. Do you approve?",
        "back": "Go back",
        "exit": "Exit",
        "exit_q": "Do you want to exit Parol Repair?",
        "select_cat": "Choose a category to repair",
        "auto": "Automatic Repair",
        "auto_desc": "Runs all safe repairs in sequence",
        "run_cat": "Run all safe actions in this category",
        "terminal": "Command Prompt",
        "view_log": "View log",
        "repairing": "Repairing",
        "wait": "Please wait... Operation in progress.",
        "done": "Repair Completed",
        "ok": "SUCCESS",
        "fail": "ERROR",
        "skip": "SKIPPED",
        "timeout": "TIMEOUT",
        "success": "Successful",
        "details": "Detailed log",
        "confirm": "Confirmation required",
        "high": "This action is HIGH RISK! Your session or devices may be affected.",
        "ask": "Continue?",
        "press": "Press any key to continue...",
        "running": "Running",
        "command": "Command",
        "result": "Result",
        "risk_low": "SAFE",
        "risk_med": "MEDIUM",
        "risk_high": "HIGH",
        "nav_main": "ARROWS: Move   ENTER: Select   ESC/Q: Exit",
        "nav_cat": "ARROWS: Move   ENTER: Run   B/ESC: Back   Q: Exit",
        "nav_gui": "Enter=Select  Up/Down=Move  Esc=Back  F11=Fullscreen",
        "small": "Terminal too small! At least 80x24 required.",
        "log_empty": "Log file is empty or missing.",
        "root_needed": "This tool requires root: sudo parol",
        "no_user": "Desktop user not found (run with sudo).",
        "no_tool": "Required tool missing",
        "abort": "Operation aborted by user.",
        "term_fail": "Could not open a terminal.",
        "license": LICENSE_LINE_EN,
        "version_line": "Parol Repair v" + VERSION + " - Debian/Ubuntu Recovery",
    },
}


def t(key):
    return UI[LANG].get(key, UI["en"].get(key, key))


# ------------------------------------------------------------------- yardimci
def is_root():
    return os.geteuid() == 0


def desktop_user():
    u = os.environ.get("SUDO_USER", "").strip()
    if u and u != "root":
        return u
    pk = os.environ.get("PKEXEC_UID", "").strip()
    if pk.isdigit():
        try:
            name = pwd.getpwuid(int(pk)).pw_name
            if name != "root":
                return name
        except KeyError:
            pass
    return None


def log(message, level="INFO"):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write("[%s] [%s] %s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message))
    except OSError:
        pass


def _session_prefix(user):
    uid = pwd.getpwnam(user).pw_uid
    return ("sudo -u %s XDG_RUNTIME_DIR=/run/user/%d "
            "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/%d/bus " % (user, uid, uid))


def resolve_cmd(cmd):
    """@ ile basan sanal komutlari gercek komuta cevirir. None -> atla."""
    user = desktop_user()
    if cmd.startswith("@user-systemctl "):
        units = cmd.split(" ", 1)[1]
        if not user:
            return None
        return _session_prefix(user) + "systemctl --user restart " + units
    if cmd.startswith("@user "):
        rest = cmd.split(" ", 1)[1]
        return (_session_prefix(user) if user else "") + rest
    if cmd == "@fixhome":
        if not user:
            return None
        home = pwd.getpwnam(user).pw_dir
        return ("for d in .cache .config .local; do "
                "p='%s/'$d; [ -e \"$p\" ] && chown -R %s:%s \"$p\"; done; true" % (home, user, user))
    if cmd == "@fixssh":
        if not user:
            return None
        home = pwd.getpwnam(user).pw_dir
        return ("[ -d '%s/.ssh' ] && find '%s/.ssh' -type d -exec chmod 700 {} + "
                "&& find '%s/.ssh' -type f -exec chmod 600 {} +; true" % (home, home, home))
    if cmd == "@fixtmp":
        return "chmod 1777 /tmp /var/tmp"
    if cmd == "@keymap":
        return "localectl set-x11-keymap " + ("tr" if LANG == "tr" else "us")
    return cmd


def execute(action, timeout=None):
    """(durum, cikti) dondurur. durum: ok | fail | skip | timeout"""
    needs = action.get("needs")
    if needs and not shutil.which(needs.split()[0]):
        return "skip", "%s: %s" % (t("no_tool"), needs)
    cmd = resolve_cmd(action["cmd"])
    if not cmd:
        return "skip", t("no_user")
    limit = timeout or action.get("to", 240)
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True,
                              text=True, timeout=limit, errors="replace")
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        body = "$ %s\n%s\n[exit %d]" % (cmd, out, proc.returncode)
        return ("ok" if proc.returncode == 0 else "fail"), body
    except subprocess.TimeoutExpired:
        return "timeout", "$ %s\n%s (%ss)" % (cmd, t("timeout"), limit)
    except Exception as exc:                                  # noqa: BLE001
        return "fail", "$ %s\n%s" % (cmd, exc)


# -------------------------------------------------------------------- katalog
def A(cmd, tr, en, risk="low", needs=None, to=240):
    act = {"cmd": cmd, "tr": tr, "en": en, "risk": risk, "to": to}
    if needs:
        act["needs"] = needs
    return act


def CAT(key, icon, ntr, nen, dtr, den, actions):
    return {"key": key, "icon": icon, "name": {"tr": ntr, "en": nen},
            "desc": {"tr": dtr, "en": den}, "actions": actions}


CATALOG = [
    CAT("pkg", "PKG", "Paket Sistemi (APT/DPKG)", "Package System (APT/DPKG)",
        "Kırık paketler, bağımlılıklar, önbellek", "Broken packages, dependencies, cache", [
        A("dpkg --configure -a", "Yarım kalan kurulumları tamamla", "Finish interrupted installs"),
        A("apt-get --fix-broken install -y", "Kırık bağımlılıkları onar", "Fix broken dependencies", to=900),
        A("apt-get update", "Paket listelerini güncelle", "Refresh package lists", to=600),
        A("apt-get -y upgrade", "Sistemi güncelle", "Upgrade the system", "med", to=3600),
        A("apt-get -y autoremove", "Gereksiz paketleri kaldır", "Remove unneeded packages", "med", to=900),
        A("apt-get clean", "Paket önbelleğini temizle", "Clean package cache"),
        A("dpkg --audit", "Paket veritabanını denetle", "Audit package database"),
    ]),
    CAT("net", "NET", "Ağ ve Wi-Fi", "Network and Wi-Fi",
        "NetworkManager, DNS, bağlantı", "NetworkManager, DNS, connectivity", [
        A("nmcli device status", "Ağ cihazlarını listele", "List network devices", needs="nmcli"),
        A("nmcli networking on", "Ağı etkinleştir", "Enable networking", needs="nmcli"),
        A("nmcli radio wifi on", "Wi-Fi radyosunu aç", "Turn Wi-Fi radio on", needs="nmcli"),
        A("systemctl restart NetworkManager", "NetworkManager'ı yeniden başlat", "Restart NetworkManager", "med"),
        A("systemctl restart systemd-resolved", "DNS çözümleyiciyi yeniden başlat", "Restart DNS resolver", "med"),
        A("resolvectl flush-caches", "DNS önbelleğini boşalt", "Flush DNS cache", needs="resolvectl"),
        A("ping -c 2 -W 3 deb.debian.org", "İnternet erişimini test et", "Test internet access"),
    ]),
    CAT("bt", "BT", "Bluetooth", "Bluetooth",
        "Servis, rfkill, adaptör", "Service, rfkill, adapter", [
        A("rfkill unblock bluetooth", "Bluetooth kilidini aç", "Unblock Bluetooth", needs="rfkill"),
        A("systemctl enable bluetooth", "Bluetooth'u başlangıçta etkinleştir", "Enable Bluetooth at boot"),
        A("systemctl restart bluetooth", "Bluetooth servisini yeniden başlat", "Restart Bluetooth service", "med"),
        A("bluetoothctl power on", "Adaptörü aç", "Power the adapter on", needs="bluetoothctl"),
        A("bluetoothctl show", "Adaptör bilgisini göster", "Show adapter info", needs="bluetoothctl"),
    ]),
    CAT("audio", "SND", "Ses Sistemi", "Audio System",
        "PipeWire, PulseAudio, ALSA", "PipeWire, PulseAudio, ALSA", [
        A("@user-systemctl pipewire pipewire-pulse wireplumber", "PipeWire oturumunu yeniden başlat",
          "Restart PipeWire session", "med"),
        A("@user pulseaudio -k", "PulseAudio'yu yeniden başlat", "Restart PulseAudio", "med"),
        A("alsactl init", "ALSA durumunu sıfırla", "Reset ALSA state", needs="alsactl"),
        A("amixer sset Master unmute 80%", "Ana sesi aç ve %80 yap", "Unmute master at 80%", needs="amixer"),
        A("@user pactl info", "Ses sunucusu bilgisi", "Sound server info"),
    ]),
    CAT("gpu", "GPU", "Grafik ve Ekran", "Graphics and Display",
        "Sürücüler, ekran yöneticisi", "Drivers, display manager", [
        A("lspci -k | grep -A 3 -E 'VGA|3D'", "Ekran kartı ve sürücü bilgisi", "GPU and driver info", needs="lspci"),
        A("nvidia-smi", "NVIDIA sürücü durumu", "NVIDIA driver status", needs="nvidia-smi"),
        A("@user xrandr --listmonitors", "Bağlı ekranları listele", "List connected monitors"),
        A("systemctl restart display-manager", "Ekran yöneticisini yeniden başlat (oturum kapanır)",
          "Restart display manager (kills session)", "high"),
    ]),
    CAT("disk", "DSK", "Disk ve Dosya Sistemi", "Disk and File System",
        "Alan, bölüm, SMART, TRIM", "Space, partitions, SMART, TRIM", [
        A("df -h", "Disk kullanımını göster", "Show disk usage"),
        A("lsblk -f", "Bölümleri ve dosya sistemlerini listele", "List partitions and filesystems"),
        A("smartctl --scan", "SMART destekli diskleri tara", "Scan SMART capable disks", needs="smartctl"),
        A("fstrim -av", "SSD TRIM çalıştır", "Run SSD TRIM", "med", to=900),
        A("journalctl -p err -b -n 20 --no-pager", "Bu açılıştaki disk/sistem hataları",
          "Errors from this boot"),
    ]),
    CAT("svc", "SVC", "Sistem Servisleri", "System Services",
        "systemd, başarısız birimler, günlük", "systemd, failed units, journal", [
        A("systemctl --failed --no-pager", "Başarısız servisleri listele", "List failed services"),
        A("systemctl daemon-reload", "systemd yapılandırmasını yeniden yükle", "Reload systemd"),
        A("systemctl reset-failed", "Başarısız durumlarını temizle", "Clear failed state", "med"),
        A("journalctl --vacuum-time=7d", "7 günden eski günlükleri sil", "Vacuum logs older than 7d", "med"),
        A("journalctl -p err -b -n 30 --no-pager", "Son hata kayıtları", "Recent error records"),
    ]),
    CAT("kernel", "KRN", "Kernel ve Modüller", "Kernel and Modules",
        "Çekirdek, initramfs, GRUB", "Kernel, initramfs, GRUB", [
        A("uname -a", "Çekirdek bilgisi", "Kernel information"),
        A("dkms status", "DKMS modül durumu", "DKMS module status", needs="dkms"),
        A("depmod -a", "Modül bağımlılıklarını yeniden kur", "Rebuild module dependencies", "med"),
        A("update-initramfs -u", "initramfs'i güncelle", "Update initramfs", "high", to=900),
        A("update-grub", "GRUB menüsünü güncelle", "Update GRUB menu", "high", to=600),
    ]),
    CAT("usb", "USB", "USB Cihazlar", "USB Devices",
        "udev, USB denetleyicisi", "udev, USB controller", [
        A("lsusb", "USB cihazlarını listele", "List USB devices", needs="lsusb"),
        A("udevadm control --reload-rules && udevadm trigger", "udev kurallarını yeniden yükle",
          "Reload udev rules", "med"),
        A("modprobe -r xhci_hcd && modprobe xhci_hcd", "USB denetleyicisini yeniden yükle (klavye kopabilir)",
          "Reload USB controller (input may drop)", "high"),
    ]),
    CAT("printer", "PRN", "Yazıcı ve Tarayıcı", "Printer and Scanner",
        "CUPS ve kuyruk", "CUPS and queue", [
        A("lpstat -p", "Yazıcıları listele", "List printers", needs="lpstat"),
        A("systemctl restart cups", "CUPS servisini yeniden başlat", "Restart CUPS", "med"),
        A("systemctl restart cups-browsed", "Yazıcı keşif servisini yeniden başlat", "Restart cups-browsed", "med"),
        A("cancel -a", "Tüm yazdırma kuyruğunu temizle", "Clear all print jobs", "med", needs="cancel"),
    ]),
    CAT("perms", "USR", "Kullanıcı ve İzinler", "User and Permissions",
        "Ev dizini, SSH, /tmp izinleri", "Home, SSH, /tmp permissions", [
        A("@fixhome", "~/.cache ~/.config ~/.local sahipliğini düzelt",
          "Fix ownership of ~/.cache ~/.config ~/.local", "med", to=900),
        A("@fixssh", "~/.ssh izinlerini güvenli hale getir", "Harden ~/.ssh permissions"),
        A("@fixtmp", "/tmp ve /var/tmp izinlerini düzelt (1777)", "Fix /tmp and /var/tmp modes", "med"),
        A("getent passwd $(id -un)", "Geçerli kullanıcı kaydı", "Current user record"),
    ]),
    CAT("fw", "FW", "Güvenlik Duvarı", "Firewall",
        "UFW kuralları", "UFW rules", [
        A("ufw status verbose", "Güvenlik duvarı durumu", "Firewall status", needs="ufw"),
        A("ufw enable", "Güvenlik duvarını etkinleştir", "Enable firewall", "med", needs="ufw"),
        A("ufw disable", "Güvenlik duvarını kapat", "Disable firewall", "med", needs="ufw"),
        A("ufw --force reset", "Tüm kuralları sıfırla", "Reset all rules", "high", needs="ufw"),
    ]),
    CAT("boot", "BOT", "Boot ve Başlangıç", "Boot and Startup",
        "EFI, GRUB, açılış süresi", "EFI, GRUB, boot time", [
        A("bootctl status --no-pager", "systemd-boot durumu", "systemd-boot status"),
        A("efibootmgr -v", "EFI boot girdileri", "EFI boot entries", needs="efibootmgr"),
        A("systemd-analyze blame | head -15", "Açılışı yavaşlatan servisler", "Slowest boot units"),
        A("update-grub", "GRUB yapılandırmasını yenile", "Regenerate GRUB config", "high", to=600),
    ]),
    CAT("power", "PWR", "Güç Yönetimi", "Power Management",
        "UPower, TLP, profil", "UPower, TLP, profile", [
        A("upower -i /org/freedesktop/UPower/devices/DisplayDevice", "Pil durumu", "Battery status", needs="upower"),
        A("systemctl restart upower", "UPower servisini yeniden başlat", "Restart UPower", "med"),
        A("systemctl restart power-profiles-daemon", "Güç profili servisini yeniden başlat",
          "Restart power-profiles-daemon", "med"),
        A("tlp-stat -s", "TLP durumu", "TLP status", needs="tlp-stat"),
    ]),
    CAT("input", "KBD", "Klavye ve Fare", "Keyboard and Mouse",
        "Giriş cihazları, düzen", "Input devices, layout", [
        A("@user xinput list", "Giriş cihazlarını listele", "List input devices"),
        A("localectl status", "Klavye/dil yapılandırması", "Keyboard/locale config"),
        A("@keymap", "X11 klavye düzenini sistem diline ayarla", "Set X11 layout from system language", "med"),
        A("udevadm trigger --subsystem-match=input", "Giriş cihazlarını yeniden tetikle", "Re-trigger input devices", "med"),
        A("modprobe -r psmouse && modprobe psmouse", "Touchpad sürücüsünü yeniden yükle",
          "Reload touchpad driver", "high"),
    ]),
    CAT("cam", "CAM", "Webcam ve Kamera", "Webcam and Camera",
        "V4L2 ve uvcvideo", "V4L2 and uvcvideo", [
        A("v4l2-ctl --list-devices", "Video cihazlarını listele", "List video devices", needs="v4l2-ctl"),
        A("ls -l /dev/video* 2>/dev/null || true", "Kamera düğümleri", "Camera device nodes"),
        A("modprobe -r uvcvideo && modprobe uvcvideo", "UVC sürücüsünü yeniden yükle", "Reload UVC driver", "med"),
    ]),
    CAT("virt", "VM", "Sanallaştırma", "Virtualization",
        "Docker, libvirt, VirtualBox", "Docker, libvirt, VirtualBox", [
        A("systemctl restart docker", "Docker servisini yeniden başlat", "Restart Docker", "med"),
        A("docker system prune -f", "Kullanılmayan Docker verilerini temizle", "Prune unused Docker data",
          "med", needs="docker", to=900),
        A("systemctl restart libvirtd", "libvirt servisini yeniden başlat", "Restart libvirt", "med"),
        A("@user VBoxManage list vms", "VirtualBox makinelerini listele", "List VirtualBox VMs"),
    ]),
    CAT("time", "TIM", "Saat ve Zaman", "Time and Date",
        "NTP ve donanım saati", "NTP and hardware clock", [
        A("timedatectl status", "Zaman durumu", "Time status"),
        A("timedatectl set-ntp true", "NTP senkronizasyonunu aç", "Enable NTP sync"),
        A("systemctl restart systemd-timesyncd", "Zaman servisini yeniden başlat", "Restart timesyncd", "med"),
        A("hwclock --systohc", "Sistem saatini donanıma yaz", "Write system time to RTC", "med"),
    ]),
    CAT("mem", "MEM", "Bellek ve Swap", "Memory and Swap",
        "RAM, swap, önbellek", "RAM, swap, caches", [
        A("free -h", "Bellek kullanımı", "Memory usage"),
        A("swapon --show", "Swap alanları", "Swap areas"),
        A("swapon -a", "Tüm swap alanlarını etkinleştir", "Enable all swap", "med"),
        A("sync && sysctl -w vm.drop_caches=3", "Sayfa önbelleğini boşalt", "Drop page caches", "med"),
        A("sysctl vm.swappiness", "Swappiness değeri", "Swappiness value"),
    ]),
]


def cname(cat):
    return cat["name"][LANG]


def cdesc(cat):
    return cat["desc"][LANG]


def adesc(act):
    return act[LANG]


def risk_label(act):
    return t("risk_" + act["risk"])


def by_key(key):
    for cat in CATALOG:
        if cat["key"] == key:
            return cat
    return None


def auto_actions():
    """Otomatik onarim: yalnizca dusuk ve orta riskli isler."""
    out = []
    for cat in CATALOG:
        for act in cat["actions"]:
            if act["risk"] in ("low", "med"):
                out.append((cat, act))
    return out


def safe_actions(cat):
    return [a for a in cat["actions"] if a["risk"] in ("low", "med")]
