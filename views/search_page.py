import streamlit as st
from functions import *

def show_search():
    st.markdown("""
    <style>
    /* AI Mesaj Kabarcığı */
    .chat-bubble-ai {
        background: rgba(255, 255, 255, 0.1) !important; /* Hafif daha belirgin arka plan */
        border-radius: 20px 20px 20px 0;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff !important; /* Saf beyaz metin */
        font-size: 16px;
        line-height: 1.6;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Ürün Kartındaki Ürün Adı Okunabilirliği */
    .name-text { 
        font-size: 14px !important; 
        color: #e5e7eb !important; /* Daha açık gri/beyaz */
        height: 45px; 
        overflow: hidden; 
        line-height: 1.5;
        margin-bottom: 10px;
    }
    .stChatInput textarea {
    color: #ffffff !important;
    }

    /* Status (Analiz ediliyor...) metin rengi */
    .stStatus {
        color: #ffffff !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid #f27a1a !important;
    }

    /* Genel alt başlıkların rengi */
    h3, h2, h1 {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
                
    [data-testid="stChatInput"] {
    z-index: 10000 !important; /* Butonlardan bile daha üstte olmalı */
    }
                
    .footer {
    position: relative;
    z-index: 1; /* Chat input'un altında kalsın */
    pointer-events: none; /* Tıklamaları engellemesin */
    }

    /* Chat input içindeki yazım alanını tıklanabilir ve görünür yap */
    .stChatInput textarea {
        color: white !important;
        cursor: text !important;
        pointer-events: auto !important;
    }
    
    </style>            
    """,unsafe_allow_html=True)
    
    IS_LISTE = st.session_state['urunler_listesi']
    if IS_LISTE:
        st.markdown("""<div class="chat-bubble-ai">Arama sonuçları</div>""",unsafe_allow_html=True)
    # Chat Geçmişi Taklidi (Basit yapı)
    if not IS_LISTE:
        st.markdown("""<div class="chat-bubble-ai">Merhaba! Bugün senin için ne bulmamı istersin? Mesela "1500 TL altı siyah deri ceket" diyebilirsin.</div>""", unsafe_allow_html=True)

    with st.container():
        if not IS_LISTE:
            user_query = st.chat_input("Mesajınızı yazın...")
            if user_query:
                st.session_state['urunler_listesi'] = []
                terminal_log("INFO","Arama Butonu","Butona basıldı")
                with st.status("🔍 Ürünleri analiz ediyorum ve en iyilerini seçiyorum...") as status:
                    filtreler = gemini_filtre_uret(user_query)
                    if filtreler and filtreler.get('ürün'):
                        st.write(f"🔍 Aranan: **{filtreler['ürün']}**")
                        terminal_log("INFO","Selenium","Scraping başlıyor.")
                        if IS_DEBUG:
                            st.json(filtreler) # Debug için filtreleri görebilirsin
                        
                        # 2. Adım: Selenium'u Başlat
                        driver = driver_kur()
                        try:
                            # Ürün ve bütçe ile başlat
                            baslat_ve_ara(driver, filtreler['ürün'], filtreler.get('bütçe'))
                            
                            # Diğer filtreleri uygula
                            for key, web_id in FILTRE_HARITASI.items():
                                if filtreler.get(key):
                                    if IS_DEBUG:
                                        st.write(f"⚙️ {key} uygulanıyor: {filtreler[key]}")
                                    filtre_ara_ve_sec(driver, web_id, filtreler[key])
                            
                            # 3. Adım: Verileri Çek
                            trendyol_urunler = verileri_ayikla(driver)
                            hepsiburada_url = hepsiburada_url_olustur(filtreler)
                            driver.get(hepsiburada_url)
                            time.sleep(3)
                            hepsiburada_urunler = hb_verileri_ayikla(driver)
                            st.session_state['urunler_listesi'] = trendyol_urunler + hepsiburada_urunler
                            if st.session_state['urunler_listesi']:
                                st.session_state['ai_tavsiyesi'] = ai_tavsiyesi_uret(st.session_state['urunler_listesi'])
                            #status.update(label="Arama Tamamlandı!", state="complete")
                        except Exception as e:
                            st.error(f"Hata: {e}")
                        finally:
                            driver.quit()
                    else:
                        st.warning("Ürün anlaşılamadı, lütfen daha net yazın.")
        else:
            if st.button("Yeni ürün Ara"):
                st.session_state['urunler_listesi'] = []
                st.rerun()
           
    # Ürünleri Session State'ten Okuyarak Göster
    if st.session_state['urunler_listesi']:
        st.markdown("""
        <style>
            .ai-recommendation-box {        
            background: rgba(255, 255, 255, 0.07) !important; /* Çok hafif beyaz şeffaf */
            backdrop-filter: blur(15px) !important; /* Arkayı bulanıklaştırarak yazıyı öne çıkarır */
            border-left: 5px solid #00d2ff !important; /* Sol tarafa turuncu bir vurgu çizgisi */
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            color: #ffffff !important; /* Saf beyaz yazı */
            font-size: 16px;
            line-height: 1.6;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }

            /* Tavsiye başlığı için küçük bir stil */
            .ai-recommendation-header {
            color: #f27a1a;
            font-weight: 800;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            }
        </style>
        """,unsafe_allow_html=True)
        if st.session_state['ai_tavsiyesi']:
            st.markdown(f"""
                <div class="ai-recommendation-box">
                    <div class="ai-recommendation-header">
                        <span>✨ AI Sizin İçin Özetledi</span>
                    </div>
                    {st.session_state['ai_tavsiyesi']}
                </div>
            """, unsafe_allow_html=True)
        for index, urun in enumerate(st.session_state['urunler_listesi'], start=1):
            # Ürüne kalıcı bir numara takıyoruz
            urun['sabit_id'] = index
        col_sort1, col_sort2 = st.columns([2, 1])
        with col_sort2:
            sirala = st.selectbox("Sıralama", ["Önerilen", "Fiyata Göre Artan", "Fiyata Göre Azalan"])
            display_list = list(st.session_state['urunler_listesi'])
            if sirala == "Fiyata Göre Artan":
                display_list.sort(key=lambda x: fiyat_sayisala_cevir(x['fiyat']))
            elif sirala == "Fiyata Göre Azalan":
                display_list.sort(key=lambda x: fiyat_sayisala_cevir(x['fiyat']), reverse=True)
        # AI RECOMMENDATION STYLE
        
        
        st.divider()
        for i in range(0, len(display_list), 4):
            cols = st.columns(4)
            current_batch = display_list[i : i + 4]
            
            for idx, urun in enumerate(current_batch):
                numara = urun.get('sabit_id', '!')
                #global_idx = i + idx
                with cols[idx]:
                    kaynak_tipi = urun.get('kaynak', 'TY')
                    bg_color = "#ff6000" if kaynak_tipi == "HB" else "#f27a1a"
                    label_text = "Hepsiburada" if kaynak_tipi == "HB" else "Trendyol"
                    # Kartın görsel ve metin kısmını HTML olarak basıyoruz
                    st.markdown(f"""
                        <div class="product-card">
                            <div style="position: absolute; top: 10px; left: 10px; background: #333; 
                                color: white; font-size: 12px; padding: 2px 8px; border-radius: 50%; 
                                font-weight: bold; z-index: 10; border: 1px solid white;">
                                #{numara}
                            </div>
                            <div style="position: absolute; top: 10px; right: 10px; background: {bg_color}; 
                            color: white; font-size: 10px; padding: 2px 8px; border-radius: 5px; 
                            font-weight: bold; z-index: 10;">
                                {label_text}
                            </div>
                            <div class="img-container">
                                <img src="{urun['gorsel'] if urun['gorsel'] else 'https://via.placeholder.com/200'}">
                            </div>
                            <p class="brand-text" style="font-size: 24px">{urun['marka']}</p>
                            <p class="name-text" style="font-size: 15px">{urun['ad'][:100]}</p>
                            <p class="price-text" style="font-size: 30px">{urun['fiyat']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Butonları Streamlit'in kendi kolon yapısıyla kartın hemen altına koyuyoruz
                    # Kartın içinde buton kullanımı Streamlit'te bazen yerleşimi bozar
                    b_c1, b_c2,b_c3 = st.columns([1, 2, 1])
                    with b_c1:
                        chat_key = f"chat_{hash(urun['link'])}" 
                        input_key = f"input_{chat_key}" # Widget ID'si
                        if chat_key not in st.session_state:
                            st.session_state[chat_key] = []

                        with st.popover("🧠", use_container_width=True):
                            st.write(f"**{urun['marka']}** için detaylı analiz")
                            
                            # Mesaj Geçmişi Alanı
                            chat_display = st.container(height=250)
                            for m in st.session_state[chat_key]:
                                with chat_display.chat_message(m["role"]):
                                    st.markdown(m["content"])

                            # Kullanıcı Girişi
                            # chat_input yerine text_input kullanıyoruz (Tek sayfa sınırı sebebiyle)
                            user_input = st.text_input("Sorunuz...", key=f"input_{chat_key}", label_visibility="collapsed")
                            st.button(
                                "Sor", 
                                key=f"btn_{chat_key}", 
                                use_container_width=True,
                                on_click=deep_dive_islem, # Yukarıdaki fonksiyonu çağırır
                                args=(chat_key, input_key, urun) # Fonksiyona gidecek veriler
                            )
                            
                    with b_c2:
                        st.link_button("🛒 Ürüne Git", urun['link'], use_container_width=True)
                    with b_c3:
                        if st.session_state['logged_in']:
                            # Benzersiz key için linkin son karakterlerini kullan
                            if st.button("❤️", key=f"fav_{numara}"):
                                favori_ekle(st.session_state['username'], urun)
                                st.toast(f"{urun['marka']} favorilere eklendi!")
 