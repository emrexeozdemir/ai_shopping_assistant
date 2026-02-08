import streamlit as st
import google.generativeai as genai
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os


from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def gemini_analiz(user_text):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    prompt = f"Kullanıcı mesajındaki ürün, bütçe, marka, renk, beden, cinsiyet bilgilerini ayıkla ve sadece JSON döndür: {user_text}"
    # Not: Buradaki promptu daha önce konuştuğumuz detaylı versiyonla değiştirebilirsin.
    response = model.generate_content(prompt)
    return json.loads(response.text.replace('```json', '').replace('```', '').strip())

# --- 2. SELENIUM AYARLARI ---
def driver_kur():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Arka planda çalışsın istersen bunu aç (ama bazen yakalanır)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def baslat_ve_ara(driver, urun, fiyat=None):
    search_query = f"{urun}&qt={urun}&st={urun}&=os=1"
    if fiyat:
        url = f"https://www.trendyol.com/sr?q={search_query}&prc=0-{fiyat}"
    else:
        url = f"https://www.trendyol.com/sr?q={search_query}"
    driver.get(url)
    time.sleep(3)

def filtre_ara_ve_sec(driver, agg_type, hedef_metin):
    """
    agg_type: 'WebBrand' veya 'Size'
    hedef_metin: 'Derby' veya '42'
    """
    print(f"\n>>> İşlem: {agg_type} -> {hedef_metin}")
    try:
        # 1. Filtre Grubunu Bul ve Oraya Git
        xpath_container = f"//*[translate(@data-aggregationtype, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = '{agg_type.lower()}']"
        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_container)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
        time.sleep(1)

        # 2. Kapalıysa Aç (Collapsed Kontrolü)
        is_collapsed = driver.execute_script("return arguments[0].classList.contains('collapsed') || arguments[0].offsetHeight < 60;", container)
        if is_collapsed:
            # Konteyner içindeki başlığa tıkla
            header = container.find_element(By.CSS_SELECTOR, ".fltr-cntnr-ttl, h3")
            driver.execute_script("arguments[0].click();", header)
            time.sleep(1)

        # 3. SENİN VERDİĞİN HTML: Arama Kutusunu Bul ve Yaz
        # data-testid="search-input" kullanarak nokta atışı yapıyoruz
        try:
            search_input = container.find_element(By.CSS_SELECTOR, "input[data-testid='search-input']")
            search_input.clear()
            search_input.send_keys(hedef_metin)
            print(f"Kutuya '{hedef_metin}' yazıldı, liste güncelleniyor...")
            time.sleep(2) # Sanal listenin (Virtual List) tazelenmesi için şart
        except Exception as e:
            print(f"Bilgi: Bu grupta arama kutusu bulunamadı, mevcut listeden aranacak. ({e})")

        # 4. JavaScript ile Tam Eşleşen Seçeneği Tıkla
        # '42' ararken '42.5'i seçmemek için tam metin kontrolü yapıyoruz.
        script_tikla = f"""
        var container = arguments[0];
        var hedef = '{hedef_metin.lower().strip()}';
        var items = container.querySelectorAll('.checkbox-label, .fltr-item-text, span, label');
        
        for (var i = 0; i < items.length; i++) {{
            var rawText = items[i].textContent.trim().toLowerCase();
            // Parantez içindeki sayıları (stok miktarı) atıp sadece ana metne bak
            var cleanText = rawText.split('(')[0].trim();
            
            if (cleanText === hedef) {{
                items[i].click();
                return "OK";
            }}
        }}
        return "NOT_FOUND";
        """
        
        result = driver.execute_script(script_tikla, container)
        
        if result == "OK":
            print(f"✅ Başarıyla seçildi: {hedef_metin}")
            time.sleep(3) # Filtrenin sayfaya yansıması için
            return True
        else:
            print(f"❌ Hata: '{hedef_metin}' listede bulunamadı.")
            return False

    except Exception as e:
        print(f"Sistem Hatası: {e}")
        return False

def fiyat_bul(card):
    # Denenecek sınıflar (En ucuzdan en pahalıya doğru sıralı)
    fiyat_siniflari = [
        "price-value",
        "price-section",           # Genelde "Sepette" yazan en son fiyat
        "prc-box-dscntd",        # İndirimli ana fiyat
        "prc-box-sllng",         # Normal satış fiyatı
        "product-price"          # Genel yedek sınıf
    ]
    
    for sinif in fiyat_siniflari:
        try:
            fiyat_elementi = card.find_element(By.CLASS_NAME, sinif)
            if fiyat_elementi.text:
                return fiyat_elementi.text
        except:
            continue # Bu sınıf yoksa bir sonrakini dene
            
    return "Fiyat bilgisi alınamadı"

def verileri_ayikla(driver):
    # Tüm ürün kartlarını bulalım
    # data-testid="product-card" kullanmak en garantisidir çünkü Trendyol test ekipleri de bunu kullanır
    cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")
    
    liste = []
    
    for card in cards[:10]: # İlk 10 ürünü alalım
        try:
            # 1. Link (href özniteliğini alıyoruz)
            link = card.get_attribute("href")
            
            # 2. Marka
            brand = card.find_element(By.CLASS_NAME, "product-brand").text
            
            # 3. İsim
            name = card.find_element(By.CLASS_NAME, "product-name").text
            
            # 4. Fiyat
            try:
                price = fiyat_bul(card)
            except:
                price = "Fiyat bulunamadı"  

            # 5. Görsel Linki
            try:
                img_url = card.find_element(By.CLASS_NAME, "image").get_attribute("src")
            except:
                img_url = ""

            liste.append({
                "marka": brand,
                "ad": name,
                "fiyat": price,
                "link": link,
                "gorsel": img_url
            })
            
            print(f"Buldum: {brand} {name} - {price} ")
            #- \n{link}\n{img_url}
            
        except Exception as e:
            print(f"Bir kart ayıklanırken hata oluştu: {e}")
            continue
            
    return liste


st.set_page_config(page_title="AI Alışveriş Botu", layout="wide")

st.title("🛍️ Trendyol AI Alışveriş Asistanı")
st.markdown("""
    <style>
    /* Ürün görsellerini küçült ve ortala */
    [data-testid="stImage"] img {
        max-height: 180px;
        object-fit: contain;
    }
    /* Ürün başlığını küçült */
    .product-name-text {
        font-size: 14px !important;
        line-height: 1.2 !important;
        height: 40px; /* İsimlerin hizalı durması için sabit yükseklik */
        overflow: hidden;
    }
    /* Fiyat yazısını küçült */
    .price-text {
        font-size: 18px !important;
        color: #f27a1a; /* Trendyol turuncusu */
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
input_text = st.text_input("Ne aramıştınız?", placeholder="Örn: 2000 TL altı siyah 42 numara Derby ayakkabı")

if st.button("Asistanı Çalıştır"):
    if input_text:
        with st.status("🤖 Gemini isteği analiz ediyor...", expanded=True):
            params = gemini_analiz(input_text)
            st.write("Analiz Sonucu:", params)
        
        with st.status("🕷️ Trendyol'da ürünler aranıyor...", expanded=True):
            driver = driver_kur()
            try:
                # 1. Başlat
                baslat_ve_ara(driver, params.get('ürün'), params.get('bütçe'))
                
                # 2. Filtreleri Sırayla Uygula
                if params.get('marka'): filtre_ara_ve_sec(driver, "WebBrand", params['marka'])
                if params.get('renk'): filtre_ara_ve_sec(driver, "WebColor", params['renk'])
                if params.get('beden'): filtre_ara_ve_sec(driver, "Size", params['beden'])
                if params.get('cinsiyet'): filtre_ara_ve_sec(driver, "WebGender", params['cinsiyet'])
                
                # 3. Verileri Çek
                urunler = verileri_ayikla(driver)
                st.success(f"{len(urunler)} ürün başarıyla toplandı!")
            except:
                print("hata")
            #finally:
                #driver.quit()

        if urunler:
            cols = st.columns(3) # 3'lü ızgara yapısı
            for idx, urun in enumerate(urunler):
                with cols[idx % 3]:
                    if urun.get('gorsel'):
                        st.image(urun['gorsel'], use_container_width=True)
                    st.subheader(urun['fiyat'])
                    st.write(f"**{urun['ad']}**")
                    st.link_button("Ürünü Gör", urun['link'])
                    st.write("---")
    else:
        st.error("Lütfen bir istek girin.")