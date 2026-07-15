### AI-Powered Smart Shopping Assistant 🛒🤖

Bu proje, kullanıcıların doğal dil kullanarak birden fazla e-ticaret platformunda (Trendyol ve Hepsiburada) eşzamanlı arama yapmasına olanak tanıyan yapay zeka destekli bir alışveriş asistanıdır. Serbest metin taleplerini yapılandırılmış arama filtrelerine dönüştürmek için Google Gemini LLM kullanılırken, veriler Selenium tabanlı otonom bir web kazıma (scraping) motoru ile gerçek zamanlı olarak çekilir.

## 🌟 Öne Çıkan Özellikler

* **Doğal Dil ile Arama:** "2000 TL altı, siyah, 42 numara koşu ayakkabısı" gibi günlük dildeki cümleleri anlar ve işler.
* **Akıllı Filtreleme (NLP):** Gemini API, kullanıcı metnindeki yazım hatalarını düzeltir ve marka, fiyat, beden gibi parametreleri otonom olarak JSON formatına çevirir.
* **Çoklu Platform Kazıma (Cross-Platform Scraping):** Selenium WebDriver kullanarak Trendyol ve Hepsiburada üzerinde eşzamanlı ve otonom arama yapar.
* **AI Tavsiye Motoru:** Elde edilen sonuçları fiyata göre sıralar ve Gemini LLM yardımıyla kullanıcıya en uygun 3 ürün için özet bir tavsiye metni sunar.
* **Fiyat Takibi:** Entegre SQLite veritabanı sayesinde kullanıcı favorilerini kaydeder ve ürünlerin fiyat geçmişini takip eder.

## 🏗️ Sistem Mimarisi (Methodology)

Sistem ardışık bir boru hattı (pipeline) şeklinde çalışır:

1. **Kullanıcı Girdisi:** Doğal dil ile arama sorgusu alınır.
2. **LLM Analizi:** Google Gemini, sorguyu ayrıştırıp yapılandırılmış bir JSON filtresi oluşturur.
3. **Otonom Scraping:** Selenium, bu JSON verisini kullanarak hedef sitelerde filtreleme yapar ve ürün (isim, fiyat, görsel, link) verilerini çeker.
4. **Veri İşleme:** Çekilen veriler tek bir havuzda birleştirilir ve fiyat bazlı sıralanır.
5. **Kullanıcı Arayüzü:** Streamlit framework'ü ile oluşturulan modern arayüzde sonuçlar ve yapay zeka analiz raporu kullanıcıya sunulur.

## 💻 Kullanılan Teknolojiler

* **Dil:** Python 3.x
* **Arayüz (UI):** Streamlit
* **Yapay Zeka (LLM):** Google Gemini API
* **Web Scraping:** Selenium WebDriver
* **Veritabanı:** SQLite, Pandas
* **Veri Formatı:** JSON

## 🛠️ Kurulum

1. **Depoyu Klonlayın:**

   ```bash
   git clone [https://github.com/emrexeozdemir/ai_shopping_assistant.git](https://github.com/emrexeozdemir/ai_shopping_assistant.git)
   cd ai_shopping_assistant
   ```
2. **Sanal Ortamı Oluşturun ve Aktif Edin:**

   ```bash
   python -m venv venv
   # Windows için:
   venv\Scripts\activate
   # Mac/Linux için:
   source venv/bin/activate
   ```
3. **Bağımlılıkları Yükleyin:**

   ```bash
   pip install -r requirements.txt
   ```
4. **API Anahtarını Ayarlayın:**
   Projenin ana dizininde `.env` adında bir dosya oluşturun ve Gemini API anahtarınızı ekleyin:

   ```env
   GEMINI_API_KEY=buraya_api_anahtarinizi_yazın
   ```

---

## 🚀 Kullanım

Uygulamayı başlatmak için terminale şu komutu yazın:

```bash
streamlit run main.py
```

Ardından açılan pencerede arama kutusuna isteğinizi yazın. Örnek:

"2000 TL altı siyah 42 numara Derby ayakkabı"

📦 Gereksinimler
Python 3.8+

Chrome Browser (Selenium için)

Google Gemini API Key

📜 Lisans
Bu proje eğitim amaçlı geliştirilmiştir. Kullanılan platformların (Trendyol vb.) kullanım koşullarına uyulması kullanıcının sorumluluğundadır.

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
