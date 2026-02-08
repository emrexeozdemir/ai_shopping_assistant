# 🛍️ Trendyol AI Shopping Assistant

Bu proje, kullanıcıların doğal dilde ilettiği alışveriş isteklerini analiz eden ve **Google Gemini AI** ile **Selenium** otomasyonunu birleştirerek Trendyol üzerinde otomatik arama yapan akıllı bir asistandır.

## ✨ Özellikler

* **🧠 Akıllı Analiz:** Gemini 2.0 Flash modellerini kullanarak karmaşık cümlelerden ürün, marka, bütçe ve beden bilgilerini JSON formatında ayıklar.
* **🤖 Otomatik Filtreleme:** Selenium kullanarak Trendyol'un arama kutularına yazar; marka, renk ve beden filtrelerini otomatik olarak seçer.
* **📊 Modern Arayüz:** Streamlit ile geliştirilmiş kullanıcı dostu ve hızlı web arayüzü.
* **🛡️ Güvenli Yapı:** `.env` desteği ile API anahtarlarınızı kodun dışında, güvenle saklar.

---

## 🛠️ Kurulum

1. **Depoyu Klonlayın:**

   ```bash
   git clone [https://github.com/kullaniciadi/trendyol-ai-asistan.git](https://github.com/kullaniciadi/trendyol-ai-asistan.git)
   cd trendyol-ai-asistan
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
streamlit run app.py
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
