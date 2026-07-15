import streamlit as st
from google import genai
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sqlite3
import hashlib
from dotenv import load_dotenv

load_dotenv()
IS_DEBUG = 0

FILTRE_HARITASI = {
    "beden": "Size",
    "renk": "WebColor",
    "marka": "WebBrand",
    "cinsiyet" : "WebGender",
    "materyal": "Material",
    "kumas_tipi": "Fabric Type",
    "ram": "Ram (System Memory)",
    "dahili_hafiza": "Internal Memory",
    "ssd_kapasite":"Ssd Capacity",
    "ekran_boyutu": "Screen Size",
    "pil_gucu": "Battery Power (Mah)",
    "kamera": "Camera Resolution",
    "urun_puani": "ProductRating",
}

HB_WHITELIST = [
    "beden", "renk", "marka", "cinsiyet", "materyal", 
    "kalip", "ram", "dahili_hafiza", "ssd_kapasite", "ekran_boyutu"
]

HB_CONFIG = {
    "beden": "bedenler",
    "renk": "renk",
    "marka": "markalar",
    "cinsiyet": "cinsiyet",
    "materyal": "malzeme",
    "kalip": "kesimkalibi",
    "ram": "ramsistembellegi",
    "dahili_hafiza": "harddiskkapasitesi1",
    "ssd_kapasite": "ssdkapasitesi",
    "ekran_boyutu": "ekranboyutu"
}

def db_baslat():
    conn = sqlite3.connect('shopping_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, marka TEXT, ad TEXT, fiyat TEXT, link TEXT, gorsel TEXT, kaynak TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS price_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  link TEXT, fiyat_sayisal REAL, tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS price_history 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              link TEXT, 
              fiyat_sayisal REAL, 
              tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def sifre_hashle(sifre):
    return hashlib.sha256(str.encode(sifre)).hexdigest()

def kullanici_kaydet(kullanici, sifre):
    conn = sqlite3.connect('shopping_app.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?,?)", (kullanici, sifre_hashle(sifre)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def giris_kontrol(kullanici, sifre):
    conn = sqlite3.connect('shopping_app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (kullanici, sifre_hashle(sifre)))
    result = c.fetchone()
    conn.close()
    return result

def favori_ekle(username, urun):
    conn = sqlite3.connect('shopping_app.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO favorites (username, marka, ad, fiyat, link, gorsel, kaynak) VALUES (?,?,?,?,?,?,?)",
                  (username, urun['marka'], urun['ad'], urun['fiyat'], urun['link'], urun['gorsel'], urun.get('kaynak', 'TY')))
        
        fiyat_sayi = fiyat_temizle_sayi(urun['fiyat'])
        if fiyat_sayi > 0:
            c.execute("INSERT INTO price_history (link, fiyat_sayisal) VALUES (?, ?)", 
                      (urun['link'], fiyat_sayi))
        
        conn.commit()
        terminal_log("INFO","Database","Favori ve fiyat kaydedildi")
    except Exception as e:
        terminal_log("ERROR","Database",f"Kayıt Hatası: {e}")
        conn.rollback() 
    finally:
        conn.close()

def favori_sil(username, urun_link):
    conn = sqlite3.connect('shopping_app.db')
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE username = ? AND link = ?", (username, urun_link))
    conn.commit()
    conn.close()


def favorileri_getir(username):
    conn = sqlite3.connect('shopping_app.db')
    c = conn.cursor()
    c.execute("SELECT marka, ad, fiyat, link, gorsel FROM favorites WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def driver_kur():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def baslat_ve_ara(driver, urun, fiyat=None):
    search_query = f"{urun}"
    url = f"https://www.trendyol.com/sr?q={search_query}"
    if fiyat:
        url += f"&prc=0-{fiyat}"
    driver.get(url)
    time.sleep(3)

def filtre_ara_ve_sec(driver, agg_type, hedef_metin):
    hedef_metin = str(hedef_metin).strip().lower() 
    terminal_log("INFO","filtre_ara_ve_sec",f"İşlem: {agg_type} -> {hedef_metin}")

    try:
        xpath_container = f"//*[translate(@data-aggregationtype, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = '{agg_type.lower()}']"
        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_container)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
        time.sleep(1)

        # Kapalıysa Aç
        is_collapsed = driver.execute_script("return arguments[0].classList.contains('collapsed') || arguments[0].offsetHeight < 60;", container)
        if is_collapsed:
            header = container.find_element(By.CSS_SELECTOR, ".fltr-cntnr-ttl, h3")
            driver.execute_script("arguments[0].click();", header)
            time.sleep(1)

        try:
            search_input = container.find_element(By.CSS_SELECTOR, "input[data-testid='search-input']")
            search_input.clear()
            search_input.send_keys(hedef_metin)
            time.sleep(1.5) 
        except:
            pass

        script_akilli_tikla = """
        var container = arguments[0];
        var input = arguments[1].toLowerCase().trim(); // Input'u küçült
        
        // Ondalık düzeltmeleri
        var inputVirgul = input.replace('.', ',');
        var inputNokta = input.replace(',', '.');

        // Filtre seçeneklerini tara
        var items = container.querySelectorAll('.checkbox-label, .fltr-item-text, span, label');
        
        for (var i = 0; i < items.length; i++) {
            // Listedeki metni küçült ve temizle
            var itemRaw = items[i].textContent.toLowerCase().trim();
            var itemClean = itemRaw.split('(')[0].trim(); // "Siyah (120)" -> "siyah"

            // --- KONTROLLER ---
            
            // 1. Tam Eşleşme (siyah === siyah)
            if (itemClean === input || itemClean === inputVirgul || itemClean === inputNokta) {
                items[i].click(); return "TAM_ESLESME";
            }

            // 2. Sayısal Başlangıç (16 === 16 gb)
            var ilkKelime = itemClean.split(' ')[0];
            if (ilkKelime === input || ilkKelime === inputVirgul || ilkKelime === inputNokta) {
                items[i].click(); return "BASLANGIC_ESLESMESI";
            }

            // 3. Kısmi İçerme (4,5 === 4,5 puan ve üzeri)
            if (itemClean.includes(inputVirgul) || itemClean.includes(inputNokta)) {
                 // Yanlış tıklamayı önlemek için: Eğer girdi sayıysa tam kelime arayalım, 
                 // ama metinse (örn: "apple") içinde geçmesi yeterli.
                 if (isNaN(input) || itemClean.split(' ').includes(inputVirgul) || itemClean.split(' ').includes(inputNokta)) {
                    items[i].click(); return "ICERIK_ESLESMESI";
                 }
            }
        }
        return "NOT_FOUND";
        """
        
        result = driver.execute_script(script_akilli_tikla, container, hedef_metin)
        
        if result != "NOT_FOUND":
            terminal_log("SCRAPER","Filtre",f"{hedef_metin} -> {result} yöntemiyle seçildi.")
            time.sleep(2)
            return True
        else:
            terminal_log("ERROR","Filtre",f"{hedef_metin} listede bulunamadı")
            return False

    except Exception as e:
        terminal_log("ERROR","Filtre",f"Hata: {e}")
        return False

def verileri_ayikla(driver):
    cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")
    liste = []
    for card in cards[:12]:
        try:
            link = card.get_attribute("href")
            brand = card.find_element(By.CLASS_NAME, "product-brand").text
            name = card.find_element(By.CLASS_NAME, "product-name").text
            
            try:
                price = fiyat_bul(card)
            except:
                price = "Fiyat bulunamadı"

            try:
                img_el = card.find_element(By.TAG_NAME, "img")
                img_url = img_el.get_attribute("data-src") or img_el.get_attribute("src")
            except:
                img_url = ""

            liste.append({"marka": brand, "ad": name, "fiyat": price, "link": link, "gorsel": img_url,"kaynak": "TY"})
        except:
            continue
    return liste

def fiyat_bul(card):
    fiyat_siniflari = [
        "price-value",
        "price-section",         
        "prc-box-dscntd",        
        "prc-box-sllng",         
        "product-price",
        "sale-price"          
    ]
    
    for sinif in fiyat_siniflari:
        try:
            fiyat_elementi = card.find_element(By.CLASS_NAME, sinif)
            if fiyat_elementi.text:
                return fiyat_elementi.text
        except:
            continue
            
    return "Fiyat bilgisi alınamadı"

def gemini_filtre_uret(user_prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    alanlar = ", ".join(FILTRE_HARITASI.keys())
    sistem_mesaji = f"""
    Kullanıcı mesajındaki bilgileri ayıkla ve SADECE JSON formatında döndür. 

    **KRİTİK TALİMATLAR:**

    1. **Yazım ve Mantık Düzenleme:** Yazım hatalarını düzelt. 
       Örn: "ayfon" -> "iPhone", "terobülü" -> "1 TB", "santimkaremetre" -> "inç".

    2. **Saf Sayısal Çıktı (Numeric Only):** ram, dahili_hafiza, ekran_boyutu, pil_gucu, kamera, urun_puani, bütçe alanlarından birimleri (GB, TL vb.) kaldır.
       - **ÖNEMLİ:** Sayısal değerlerde mutlaka NOKTA (.) kullan (Örn: 15.6). JSON virgülü sayı içinde kabul etmez.

    3. **Veri Yapısı:**
       - Mesajda olmayan alanları `null` (string olmayan null) veya "belirtilmemiş" olarak işaretle.
       - "ürün" ve "bütçe" alanlarını mutlaka ekle.
       - Diğer alanlar: {alanlar}
    """

    try:
        terminal_log("INFO","FILTRE API","İstek atıldı.")
        
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=[sistem_mesaji, user_prompt]
        )
        
        terminal_log("AI","FILTRE API","Cevap geldi.")
        raw_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_json)
        
        sayisal_alanlar = ["ram", "dahili_hafiza", "ssd_kapasite", "ekran_boyutu", "bütçe"]
        if data:
            for alan in sayisal_alanlar:
                val = data.get(alan)
                if val and val != "belirtilmemiş":
                    try:
                        num = float(str(val).replace(',', '.'))
                        data[alan] = str(int(num)) if num.is_integer() else str(num).replace('.', ',')
                    except:
                        continue
                        
        return data

    except Exception as e:
        terminal_log("ERROR","Gemini",f"Filtre API Hata: {e}") 
        return None

def ai_tavsiyesi_uret(urunler):
    if not urunler or len(urunler) < 3:
        return "Karşılaştırma yapabilmek için yeterli ürün bulunamadı."
    
    urun_havuzu = ""
    for u in urunler[:20]:
        id_no = u.get('sabit_id', '?')
        urun_havuzu += f"[{id_no}] {u['marka']} {u['ad']} - {u['fiyat']}\n"
    
    prompt = f"""
    Aşağıdaki ürün listesinden en mantıklı 3 seçeneği belirle.
    
    **KURALLAR:**
    1. Maksimum 80 kelime kullan.
    2. Sadece madde işaretleri kullan (Bullet points).
    3. Uzun cümleler kurma, teknik nedenini söyle ve geç.
    4. Hangi sitenin daha avantajlı olduğunu tek cümleyle belirt.
    5. Yanıtına 'AI Tavsiyesi:' başlığıyla başla.
    6. Ürünlerin numarasını da ekle örneğin: [1],[2].

    Ürünler:
    {urun_havuzu}
    """
    
    try:
        api_key_recommendation = os.getenv("GEMINI_RECOMMENDATION_KEY") or os.getenv("GEMINI_API_KEY")
        
        client = genai.Client(
            api_key=api_key_recommendation,
        )
        
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt
        )
        return response.text
    except Exception as e:
        terminal_log("ERROR","Gemini",f"Tavsiye API Hata: {e}") 
        return "Analiz şu an yapılamıyor."

def hb_karakter_duzelt(metin):
    """Türkçe karakterleri HB formatına çevirir (sarı -> sari)"""
    char_map = str.maketrans("çğıöşüİ", "cgiosuI")
    return str(metin).translate(char_map).lower()

def hb_birim_formatla(deger, tip):
    """Sayıları HB'nin €20 ve €2C içeren teknik formatına çevirir."""
    try:
        sayi = float(str(deger).replace(',', '.'))
    except:
        return str(deger)

    # RAM ve Depolama Kuralları (1 ve altı TB, üstü GB)
    if tip in ["ram", "dahili_hafiza", "ssd_kapasite"]:
        birim = "TB" if sayi <= 1 else "GB"
        # Sayı tam sayı ise .0'ı at, değilse noktayı €2C (virgül) yap
        fmt_sayi = str(int(sayi)) if sayi.is_integer() else str(sayi).replace('.', '€2C')
        return f"{fmt_sayi}€20{birim}"
    
    # Ekran Boyutu (15,6 inç -> 15€2C6€20in€C3€A7)
    if tip == "ekran_boyutu":
        fmt_sayi = str(int(sayi)) if sayi.is_integer() else str(sayi).replace('.', '€2C')
        return f"{fmt_sayi}€20in€C3€A7"
        
    return str(deger)

def hepsiburada_url_olustur(gemini_json):
    """Gemini JSON'u alıp tam uyumlu HB URL'si üretir."""
    base_url = "https://www.hepsiburada.com/ara?"
    urun = gemini_json.get('ürün', '')
    
    HB_MAPPING = {
        "beden": "bedenler",
        "renk": "renk",
        "marka": "markalar",
        "cinsiyet": "cinsiyet",
        "materyal": "malzeme",
        "kalip": "kesimkalibi",
        "ram": "ramsistembellegi",
        "dahili_hafiza": "harddiskkapasitesi1",
        "ssd_kapasite": "ssdkapasitesi",
        "ekran_boyutu": "ekranboyutu"
    }
    
    # Whitelist dışındakiler query'ye (q=) eklenecek
    whitelist = list(HB_MAPPING.keys())
    q_ekstra = []
    filtreler_url = []
    marka_param = ""

    for key, val in gemini_json.items():
        if not val or val == "belirtilmemiş" or key == "ürün":
            continue

        if key not in whitelist:
            q_ekstra.append(str(val))
            continue

        hb_key = HB_MAPPING[key]
        
        if key == "marka":
            marka_param = f"&markalar={hb_karakter_duzelt(val)}"
        elif key in ["ram", "dahili_hafiza", "ssd_kapasite", "ekran_boyutu"]:
            filtreler_url.append(f"{hb_key}:{hb_birim_formatla(val, key)}")
        elif key == "renk":
            # Renk: İlk harf büyük, karakterler temiz (Gumus, Sari)
            filtreler_url.append(f"{hb_key}:{hb_karakter_duzelt(val).capitalize()}")
        else:
            # Diğerleri (Beden, Cinsiyet vb.): İlk harf büyük
            filtreler_url.append(f"{hb_key}:{str(val).capitalize()}")

    search_q = "+".join([urun] + q_ekstra)
    final_url = f"{base_url}q={search_q}"
    
    if filtreler_url:
        final_url += f"&filtreler={';'.join(filtreler_url)}"
    
    final_url += marka_param
    
    if gemini_json.get('bütçe'):
        final_url += f"&fiyat=0-{gemini_json['bütçe']}"
        
    return final_url

def hb_verileri_ayikla(driver):
    liste = []
    cards = driver.find_elements(By.CSS_SELECTOR, "article[class*='productCard-']")
    
    terminal_log("INFO","HEPSİBURADA SCRAPPER",f"{len(cards)} kart inceleniyor.")

    for card in cards:
        try:
            try:
                link_el = card.find_element(By.TAG_NAME, "a")
                link = link_el.get_attribute("href")
                full_name = link_el.get_attribute("title")
                
                if not full_name:
                    full_name = card.find_element(By.CSS_SELECTOR, "h2, h3, [class*='title']").text
            except:
                continue

            price = "Fiyat bulunamadı"
            price_selectors = [
                "[data-test-id='final-price-1']",
                "[class*='finalPrice']",
                "[class*='price-current-price']",
                "div[class*='price-module_priceArea']"
            ]
            for sel in price_selectors:
                try:
                    p_el = card.find_element(By.CSS_SELECTOR, sel)
                    if p_el.text:
                        price = p_el.text.replace('\n', ' ').strip()
                        break
                except:
                    continue

            img_url = ""
            try:
                img_el = card.find_element(By.CSS_SELECTOR, "img[class*='hbImageView-module_hbImage']")
                img_url = (img_el.get_attribute("srcset") or 
                        img_el.get_attribute("data-src") or 
                        img_el.get_attribute("src"))
                
                if img_url and "," in img_url:
                    img_url = img_url.split(",")[0].split(" ")[0]

                if any(x in img_url.lower() for x in ["badge", "banner", "taksit", "kargo"]):
                    all_imgs = card.find_elements(By.TAG_NAME, "img")
                    for im in all_imgs:
                        src = im.get_attribute("src") or ""
                        if "productimages.hepsiburada.net" in src:
                            img_url = src
                            break
            except:
                img_url = "https://via.placeholder.com/200?text=Resim+Yok"



            if full_name and link and "HBCV" in link:
                liste.append({
                    "marka": full_name.split()[0] if full_name else "Hepsiburada",
                    "ad": full_name,
                    "fiyat": price,
                    "link": link,
                    "gorsel": img_url,
                    "kaynak": "HB"
                })
                
            if len(liste) >= 12:
                break

        except Exception:
            continue
            
    return liste

def fiyat_temizle_sayi(fiyat_metni):
    try:
        temiz = fiyat_metni.replace("TL", "").replace(".", "").replace(",", ".").replace(" ", "").strip()
        return float(temiz)
    except:
        return 0.0

def fiyat_kaydet(link, fiyat_metni):
    fiyat_sayi = fiyat_temizle_sayi(fiyat_metni)
    terminal_log("INFO","fiyat_kaydet",f"Sayi temizlendi: {fiyat_sayi}")
    if fiyat_sayi > 0:
        conn = sqlite3.connect('shopping_app.db')
        c = conn.cursor()
        c.execute("INSERT INTO price_history (link, fiyat_sayisal) VALUES (?, ?)", (link, fiyat_sayi))
        conn.commit()
        conn.close()

def fiyat_sayisala_cevir(fiyat_str):
    try:
        temiz = fiyat_str.replace("TL", "").replace(".", "").replace(",", ".").replace(" ", "").strip()
        if temiz.count('.') > 1:
            parcalar = temiz.split('.')
            temiz = "".join(parcalar[:-1]) + "." + parcalar[-1]
        return float(temiz)
    except:
        return 0.0

def bugun_fiyat_kaydi_var_mi(link):
    conn = sqlite3.connect('shopping_app.db', timeout=10)
    c = conn.cursor()
    c.execute("SELECT 1 FROM price_history WHERE link = ? AND date(tarih) = date('now')", (link,))
    result = c.fetchone()
    conn.close()
    return result is not None

def tekil_urun_fiyat_cek(driver,link, kaynak):
    try:
        driver.get(link)

        time.sleep(3)
        
        if kaynak == "TY":
            terminal_log("INFO","TRENDYOL","Ürün fiyat güncelleme, kaynak doğrulandı.")
            try:
                el= driver.find_element(By.XPATH,'//*[@id="envoy"]/div/div[6]/div/div[2]/div/p[2]')
                if el.text:
                    terminal_log("AI","Fiyat",f"Trendyol sepette fiyat: {el.text.strip()}")
                    return el.text.strip()
            except:pass
            try:
                el=driver.find_element(By.XPATH,'//*[@id="envoy"]/div/div[4]/div/div[2]/div/p[2]')
                if el.text:
                    terminal_log("AI","Fiyat",f"Trendyol normal fiyat: {el.text.strip()}")
                    return el.text.strip()
            except:pass


        else: # Hepsiburada
            try:
                el = driver.find_element(By.XPATH,'//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div[1]/div[2]')
                if el.text:
                    terminal_log("AI","Fiyat",f"Hepsiburada sepete özel fiyat: {el.text.strip()}")
                    return el.text.strip()
            except:pass
            try:
                el = driver.find_element(By.XPATH,'//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div/div/div[1]')
                if el.text: return el.text.strip()
            except: pass
            try:
                el = driver.find_element(By.XPATH,'//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div[1]/div[2]')
                if el.text: return el.text.strip()
            except: pass
            try:
                el = driver.find_element(By.XPATH,'//*[@id="container"]/main/div/div[2]/section[1]/div[2]/div[3]/div[1]/div[2]')
                if el.text: return el.text.strip()
            except: pass
                
    except Exception as e:
        terminal_log("ERROR","tekil_urun_fiyat_cek",f"Fiyat çekilemedi: ({link}): {e}")
    
    return None

def favori_takip_sistemi(username, fav_listesi):

    guncellenecekler = [f for f in fav_listesi if not bugun_fiyat_kaydi_var_mi(f[3])]
    
    if not guncellenecekler:
        return

    with st.spinner(f"{len(guncellenecekler)} ürünün fiyatı güncelleniyor..."):
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        driver_fiyat = webdriver.Chrome(options=chrome_options)
        
        for item in guncellenecekler:
            f_marka, f_ad, f_fiyat, f_link, f_gorsel, f_kaynak = item[0], item[1], item[2], item[3], item[4], item[6]
            
            yeni_fiyat_metni = tekil_urun_fiyat_cek(driver_fiyat,f_link, f_kaynak)
            
            if yeni_fiyat_metni:
                fiyat_kaydet(f_link, yeni_fiyat_metni)
        
        driver_fiyat.quit()
        st.toast("Fiyat geçmişi güncellendi!", icon="📈")
        st.rerun()

def gemini_sohbet_et(mesaj_gecmisi):
    """
    mesaj_gecmisi: [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
    yapısındaki listeyi alır ve bağlamı koruyarak yanıt döner.
    """
    try:
        api_key_popover = os.getenv("GEMINI_POPOVER_KEY")
        
        client = genai.Client(api_key=api_key_popover)

        gemini_contents = []
        for m in mesaj_gecmisi:
            role = "user" if m["role"] == "user" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": m["content"]}]
            })

        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=gemini_contents
        )
        
        return response.text

    except Exception as e:
        terminal_log("ERROR","DEEP DIVE API",f"{e}")
        return "Bu ürünle ilgili şu an teknik bir sorun yaşıyorum, daha sonra tekrar sorabilir misin?"

def deep_dive_islem(chat_key, input_key, urun_verisi):
    soru = st.session_state.get(input_key, "")
    
    if soru:
        if not st.session_state[chat_key]:
            prompt = f"Ürün Bilgisi: {urun_verisi['marka']} {urun_verisi['ad']}. Fiyat: {urun_verisi['fiyat']}. Sorum: {soru}"
        else:
            prompt = soru

        st.session_state[chat_key].append({"role": "user", "content": prompt})
        
        try:
            cevap = gemini_sohbet_et(st.session_state[chat_key])
            st.session_state[chat_key].append({"role": "assistant", "content": cevap})
        except Exception as e:
            st.session_state[chat_key].append({"role": "assistant", "content": f"Hata: {e}"})
        
        st.session_state[input_key] = ""

import datetime

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def terminal_log(seviye, modul, mesaj):
    zaman = datetime.datetime.now().strftime("%H:%M:%S")
    
    if seviye == "AI":
        renk = Colors.CYAN
    elif seviye == "SCRAPER":
        renk = Colors.GREEN
    elif seviye == "ERROR":
        renk = Colors.RED
    elif seviye == "INFO":
        renk = Colors.YELLOW
    else:
        renk = Colors.END

    print(f"{renk}{Colors.BOLD}[{zaman}] [{seviye}] @{modul}: {mesaj}{Colors.END}")