# 🌊 MIRISDA — Mifzal & Riska Intelligent Sea-Dashboard

Dashboard interaktif untuk analisis sebaran sampah laut (marine debris) di perairan pesisir Indonesia, dilengkapi visualisasi oseanografi (wind rose, wave rose) untuk memahami pengaruh angin dan gelombang terhadap pola akumulasi sampah.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red)

---

## 📋 Daftar Isi

- [Tampilan Dashboard](#-tampilan-dashboard)
- [Fitur Utama](#-fitur-utama)
- [Instalasi](#-instalasi)
- [Cara Menjalankan](#-cara-menjalankan)
- [Struktur Data](#-struktur-data)
- [Upload Dataset Baru](#-upload-dataset-baru)
- [Menambahkan Data Oseanografi](#-menambahkan-data-oseanografi)
- [Referensi Dataset](#-referensi-dataset)
- [Batasan & Asumsi](#-batasan--asumsi)
- [Kontributor](#-kontributor)
- [Lisensi](#-lisensi)

---

## 🖼️ Tampilan Dashboard

Dashboard menampilkan:
- Peta interaktif sebaran lokasi survei dengan color-coding densitas debris
- 5 KPI utama (total item, densitas rata-rata, berat total, jumlah lokasi, jumlah ekspedisi)
- Komposisi jenis sampah per kategori (pie chart) dan top 10 item terbanyak (bar chart)
- Tren tahunan dan pola musiman (heatmap)
- Tabel hotspot lokasi dengan status risiko
- Tab khusus oseanografi: wind rose, wave rose, dan korelasi debris × faktor lingkungan
- Insight otomatis berbasis analisis statistik

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|---|---|
| 📂 Upload data debris | Ganti dataset dengan file `.xlsx`/`.csv` baru tanpa ubah kode |
| 🌬️ Upload data ERA5 | Tambahkan data oseanografi aktual (opsional) |
| 🔬 Mode demo oseanografi | Simulasi realistis untuk presentasi tanpa perlu download ERA5 |
| 🗺️ Peta interaktif | Folium + CartoDB Dark Matter, marker & circle berwarna sesuai risiko |
| 🧠 Insight otomatis | 5+ insight dihasilkan otomatis dari data yang difilter |
| 📊 Filter dinamis | Tahun, lokasi, ekspedisi, kategori debris |

---

## 🛠️ Instalasi

### Prasyarat
- Python 3.10 atau lebih baru
- pip

### Langkah instalasi

```bash
# 1. Clone repository ini
git clone https://github.com/USERNAME/mirisda-dashboard.git
cd mirisda-dashboard

# 2. (Opsional tapi disarankan) buat virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Install semua dependencies
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan

Pastikan file dataset `Marine Debris-Data-UoP.xlsx` sudah ada di folder yang sama dengan script, lalu jalankan:

```bash
streamlit run mirisda_dashboard.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

> Jika file dataset belum ada di folder, dashboard tetap bisa dijalankan — gunakan fitur **upload dataset** di sidebar untuk memuat data secara manual.

---

## 📊 Struktur Data

Dataset debris harus mengikuti format UoP (multi-header Excel), dengan kolom minimal berikut di sheet bernama `Dataset`:

| Kolom | Tipe | Keterangan |
|---|---|---|
| `Expedition` | string | Nama ekspedisi/survei |
| `Month`, `Year` | string, int | Waktu survei |
| `Places` | string | Nama lokasi |
| `Lon`, `Lat` | float | Koordinat |
| `A1`–`A18` | int | Kategori "Most Likely Items" |
| `B1`–`B4` | int | Kategori "Fishing Gear" |
| `C1`–`C5` | int | Kategori "Packaging Materials" |
| `D1`–`D4` | int | Kategori "Personal Hygiene" |
| `E1`–`E7` | int | Kategori "Other Trash" |
| `F1`–`F3` | int | Kategori "Tiny Trash (<2.5cm)" |
| `Weight (kilos)` | float | Berat total sampah |
| `Distance (meter)` | float | Panjang transek survei |
| `Total Items` | int | Total item debris |

Lihat dataset asli `Marine Debris-Data-UoP.xlsx` sebagai contoh format yang valid.

---

## 📂 Upload Dataset Baru

1. Buka dashboard, lihat sidebar bagian **"📂 Upload Dataset Debris"**
2. Klik area upload, pilih file `.xlsx` atau `.csv` dengan format yang sama seperti di atas
3. Dashboard otomatis memparsing dan memperbarui seluruh visualisasi

Tidak perlu mengubah kode apapun — parser sudah dirancang untuk mendeteksi struktur multi-header secara otomatis.

---

## 🌬️ Menambahkan Data Oseanografi

Ada dua cara mengaktifkan tab **Oseanografi**:

### Opsi A — Mode demo (cepat, untuk presentasi)
Aktifkan toggle **"Gunakan data oseanografi simulasi"** di sidebar. Data simulasi dibuat berdasarkan pola musiman realistis (musim barat/timur Indonesia).

### Opsi B — Data ERA5 aktual (untuk analisis serius)
1. Unduh data Angin dan Gelombang di ERA5
2. Gabungkan kedua file yang sudah diunduh dalam bentuk .nc
3. Buka dashboard marine debris nya
4. Upload file hasil ke dashboard via sidebar **"🌬️ Upload Data Oseanografi (ERA5)"**

---

## 📚 Referensi Dataset

**Dataset debris:**
Purba, Noir; Faizal, Ibnu; Martasuganda, Marine (2021), "Marine Debris Dataset in Coastal Areas in Indonesia", Mendeley Data, V2, doi: [10.17632/r3y43cdd3x.2](https://doi.org/10.17632/r3y43cdd3x.2)

**Data oseanografi (opsional):**
Hersbach, H. et al. (2023). ERA5 hourly data on single levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI: [10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47)

---

## ⚠️ Batasan & Asumsi

- Status risiko (Low/Medium/High) dihitung berdasarkan **persentil relatif** dari data yang sedang difilter, bukan ambang baku mutu resmi dari pemerintah/lembaga lingkungan
- Data oseanografi mode demo bersifat **simulasi**, bukan data aktual — selalu cek apakah toggle demo aktif sebelum menggunakan untuk analisis/laporan resmi
- Korelasi yang ditampilkan (Pearson r) bersifat deskriptif, belum tentu menunjukkan hubungan sebab-akibat
- Dataset UoP mencakup periode 2013–2018; tidak merepresentasikan kondisi terkini tanpa data tambahan

---

## 👥 Kontributor

Dikembangkan oleh **Mifzal & Riska** sebagai bagian dari proyek MIRISDA.

---

## 📄 Lisensi

Lihat file [LICENSE](LICENSE) untuk detail. Dataset pihak ketiga (UoP, ERA5) tunduk pada lisensi masing-masing sumber.
