# Growtopia AutoFarm

Aplikasi desktop berbasis Python yang dirancang untuk membantu mengotomatisasi aktivitas farming pada game Growtopia melalui sistem pengelolaan input, pengenalan visual, dan antarmuka grafis.

Project ini dikembangkan menggunakan pendekatan modular dengan GUI berbasis CustomTkinter sehingga setiap fitur dapat dikelola dan dikembangkan secara terpisah.

> **Status Project:** Dalam tahap pengembangan dan pengujian. Beberapa fitur, khususnya deteksi visual dan interaksi langsung di dalam game, masih memerlukan validasi lebih lanjut.

## Fitur Utama

- **Auto Punch** — Simulasi aktivitas punch dengan koordinat, interval, durasi, dan batas jumlah aksi yang dapat dikonfigurasi.
- **Auto Put** — Simulasi aktivitas put berdasarkan daftar posisi koordinat.
- **Auto Farm Loop** — Mengatur urutan proses Auto Punch dan Auto Put berdasarkan jumlah siklus.
- **Pause & Resume** — Menjeda dan melanjutkan proses farming.
- **Stop Control** — Menghentikan proses farming.
- **Vision System** — Mengambil screenshot layar dan mendeteksi template menggunakan OpenCV.
- **Reconnect Monitor** — Memantau indikasi status koneksi berdasarkan template visual.
- **Farm Settings** — Mengatur koordinat, interval, durasi, jumlah aksi, dan siklus.
- **Vision Settings** — Mengatur monitor, threshold, serta lokasi template.
- **Reconnect Settings** — Mengatur interval dan jumlah konfirmasi deteksi.
- **Vision Testing** — Menguji kecocokan template dengan tampilan layar.
- **Activity Logs** — Melihat catatan aktivitas aplikasi.
- **Configuration Management** — Menyimpan pengaturan aplikasi dalam format JSON.

## Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python 3.11+ | Bahasa pemrograman utama |
| CustomTkinter | Antarmuka grafis |
| OpenCV | Pengolahan citra dan template matching |
| MSS | Pengambilan screenshot layar |
| PyAutoGUI | Pengelolaan input keyboard dan mouse |
| NumPy | Pengolahan data gambar |
| Pillow | Pemrosesan gambar |
| Threading | Menjalankan proses di background |
| JSON | Penyimpanan konfigurasi |

## Struktur Project

```text
Growtopia-AutoFarm/
│
├── assets/
│   ├── icons/
│   └── templates/
│
├── core/
│   ├── controller.py
│   ├── farm_loop.py
│   ├── input_manager.py
│   ├── reconnect.py
│   ├── state_manager.py
│   └── vision.py
│
├── data/
│   └── config.json
│
├── features/
│   ├── auto_punch.py
│   └── auto_put.py
│
├── gui/
│   ├── activity_logs.py
│   ├── components.py
│   ├── dashboard.py
│   ├── farm_settings.py
│   ├── reconnect_settings.py
│   ├── settings.py
│   ├── vision_settings.py
│   └── vision_testing.py
│
├── utils/
│   ├── logger.py
│   ├── safety.py
│   └── validation.py
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

*Struktur di atas merupakan gambaran modul project. Sesuaikan dengan file aktual yang tersedia di repository.*

## Persyaratan Sistem

Sebelum menjalankan aplikasi, pastikan perangkat telah memiliki:

- Windows 10 atau Windows 11.
- Python 3.11 atau versi lebih baru yang kompatibel dengan dependensi.
- Visual Studio Code (disarankan).
- Game Growtopia untuk pengujian in-game.
- Resolusi layar yang mendukung pengaturan koordinat aplikasi.

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/Entongg/Growtopia-AutoFarm.git
```

### 2. Masuk ke Folder Project

```bash
cd Growtopia-AutoFarm
```

### 3. Buat Virtual Environment

```bash
python -m venv venv
```

### 4. Aktifkan Virtual Environment

Untuk Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 5. Instal Dependensi

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

Pastikan virtual environment sudah aktif, kemudian jalankan:

```bash
python main.py
```

Aplikasi akan membuka dashboard Growtopia AutoFarm.

## Konfigurasi

Pengaturan aplikasi dapat disesuaikan melalui menu dashboard.

| Pengaturan | Keterangan |
|---|---|
| Auto Punch | Mengatur koordinat, interval, durasi, dan jumlah aksi |
| Auto Put | Mengatur posisi dan interval aktivitas |
| Farm Loop | Mengatur jumlah siklus farming |
| Vision | Mengatur monitor dan threshold deteksi |
| Reconnect | Mengatur interval dan konfirmasi monitoring |

Konfigurasi aplikasi disimpan menggunakan format JSON.

## Keamanan dan Batasan

Project ini menggunakan beberapa mekanisme pengamanan:

- Mode simulasi (`dry_run=True`) aktif secara default.
- Proses farming memiliki batas durasi dan jumlah aksi.
- Tersedia kontrol Pause, Resume, dan Stop.
- Validasi konfigurasi dilakukan sebelum proses farming dimulai.
- PyAutoGUI Failsafe digunakan untuk membantu menghentikan input ketika diperlukan.
- Reconnect Monitor hanya mendeteksi indikasi status koneksi berdasarkan tampilan visual.
- Aplikasi tidak melakukan login otomatis atau melewati CAPTCHA.

**Penting:** Fitur Auto Punch dan Auto Put masih menggunakan mode simulasi secara default. Keberhasilan inisialisasi modul tidak berarti interaksi langsung di dalam game telah tervalidasi. Lakukan pengujian secara bertahap sebelum menggunakan fitur yang melibatkan input aktual.

## Status Pengembangan

| Komponen | Status |
|---|---|
| Struktur Project | Selesai |
| Dashboard GUI | Selesai |
| Farm Settings | Selesai |
| Vision Settings | Selesai |
| Reconnect Settings | Selesai |
| Auto Punch | Simulasi |
| Auto Put | Simulasi |
| Auto Farm Loop | Simulasi |
| Pause & Resume | Diuji |
| Stop Control | Diuji |
| Configuration Management | Diuji |
| Vision Detection | Perlu validasi in-game |
| Reconnect Detection | Perlu validasi in-game |
| Input Aktual di Game | Belum divalidasi |

## Pengembangan Selanjutnya

Beberapa pengembangan yang dapat dilakukan:

- Meningkatkan akurasi deteksi template.
- Mengoptimalkan proses pengambilan screenshot.
- Mengembangkan sistem monitoring koneksi.
- Melakukan pengujian koordinat dan input pada lingkungan game.
- Meningkatkan stabilitas proses background.
- Menambahkan dokumentasi dan pengujian otomatis.

## Lisensi

Project ini dikembangkan untuk tujuan pembelajaran dan eksperimen pemrograman Python.

Pengguna bertanggung jawab untuk memastikan penggunaan aplikasi mematuhi ketentuan layanan game dan peraturan yang berlaku.

---

**Growtopia AutoFarm**  
Developed with Python.
