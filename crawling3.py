import schedule
import time
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# === SETUP MONGODB ===
client = MongoClient("mongodb://localhost:27017/")
db = client["stroke_app"]
collection = db["crawling"]

# === DAFTAR QUERY GOOGLE ===
queries = [
    "gejala stroke",
    "tanda tanda stroke",
    "ciri ciri stroke",
    "cara mengenali stroke",
    "gejala awal stroke",
    "bagaimana tanda stroke"
]

# === Kata kunci untuk filter konten ===
keywords = [
    "gejala stroke",
    "tanda stroke",
    "tanda-tanda stroke",
    "ciri ciri stroke",
    "ciri-ciri stroke",
    "mengenali stroke",
    "awal stroke"
]

# === FUNGSI UNTUK CRAWLING DAN MENYIMPAN DATA ===
def crawl_and_save():
    print(f"\n🕒 Menjalankan crawler pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for q in queries:
        print(f"\n🔍 Mencari dengan query: {q}")
        for url in search(q, num_results=100):
            try:
                print(f"📄 Memeriksa URL: {url}")
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                # === Ambil Judul Artikel ===
                judul = soup.title.string.strip() if soup.title else "Judul tidak ditemukan"

                # === Ambil Tanggal Rilis ===
                meta_date = soup.find("meta", {"property": "article:published_time"}) \
                    or soup.find("meta", {"name": "pubdate"}) \
                    or soup.find("meta", {"name": "date"})
                tanggal_rilis = meta_date["content"] if meta_date and meta_date.get("content") else datetime.now().strftime("%Y-%m-%d")

                # === Ambil Isi Artikel ===
                isi = " ".join([p.get_text().strip().lower() for p in soup.find_all("p")])

                # === Filter berdasarkan kata kunci ===
                if any(kw in isi for kw in keywords):
                    print("✅ Artikel relevan ditemukan.")
                    data = {
                        "url": url,
                        "judul": judul,
                        "konten": isi,
                        "tanggal_rilis": tanggal_rilis
                    }

                    if not collection.find_one({"url": url}):
                        collection.insert_one(data)
                        print("💾 Disimpan ke MongoDB.")
                    else:
                        print("🔁 Artikel sudah ada, dilewati.")
                else:
                    print("⛔ Tidak mengandung kata kunci yang diminta.")
            except Exception as e:
                print(f"❌ Gagal mengambil dari {url}: {e}")

    print("\n✅ Selesai crawling dan menyimpan artikel.")

# === JADWALKAN FUNGSI TIAP HARI PUKUL 08:00 ===
schedule.every().day.at("13:42").do(crawl_and_save)

# === LOOP UNTUK MENJALANKAN PENJADWALAN SECARA TERUS MENERUS ===
print("📅 Scheduler aktif... Tekan Ctrl+C untuk berhenti.")
while True:
    schedule.run_pending()
    time.sleep(1)
