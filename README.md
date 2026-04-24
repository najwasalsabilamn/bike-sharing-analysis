# 🚴 Proyek Analisis Data: Bike Sharing Dataset

Proyek ini merupakan submission akhir kelas **Belajar Fundamental Analisis Data** di Dicoding Indonesia.

## 📁 Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv       # Dataset yang digunakan dashboard
│   └── dashboard.py        # Aplikasi Streamlit
├── data/
│   ├── day.csv             # Dataset harian (raw)
│   └── hour.csv            # Dataset per jam (raw)
├── notebook.ipynb          # Jupyter Notebook analisis lengkap
├── README.md               # Panduan ini
├── requirements.txt        # Daftar library Python
└── url.txt                 # URL deploy dashboard (Streamlit Cloud)
```

## 📊 Pertanyaan Bisnis

1. Bagaimana pengaruh kondisi cuaca dan musim terhadap rata-rata jumlah penyewaan sepeda harian selama 2011–2012?
2. Pada jam berapa penyewaan sepeda mencapai puncaknya, dan bagaimana pola berbeda antara hari kerja dan akhir pekan?
3. *(Analisis Lanjutan)* Bagaimana segmentasi hari berdasarkan tingkat penggunaan (Low/Medium/High Usage)?

## 🛠️ Setup Environment

### 1. Buat virtual environment (opsional tapi disarankan)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Siapkan data untuk dashboard
Setelah menjalankan `notebook.ipynb` hingga selesai, copy atau simpan `day.csv` yang sudah dibersihkan ke folder `dashboard/` dengan nama `main_data.csv`:
```bash
cp data/day.csv dashboard/main_data.csv
```

## 🚀 Menjalankan Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada alamat `http://localhost:8501`.

## 🌐 Dashboard Online

Akses dashboard yang sudah di-deploy di Streamlit Cloud:
> Lihat `url.txt` untuk tautan lengkap.

## 📦 Dataset

**Bike Sharing Dataset** – Capital Bikeshare System, Washington D.C.
- Sumber: [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset)
- Periode: 1 Januari 2011 – 31 Desember 2012
- Lisensi: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## 👤 Penulis

- **Nama:** Budi Santoso  
- **Email:** budi.santoso@email.com  
- **ID Dicoding:** budisantoso_dicoding
