import streamlit as st
def apply_styles():
    st.markdown("""
    <style>
        /* 1. TÜM SAYFAYI KAPLAYAN ARKA PLAN */
        [data-testid="stAppViewContainer"] {
            background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
            url("https://i.imgur.com/X7rQ0iE.jpeg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed; /* Sayfa kaysa da resim sabit durur */
            z-index: 0 !important;
        }

        /* 2. STREAMLIT VARSAYILAN KATMANLARI ŞEFFAF YAP (Resmin görünmesi için) */            
        [data-testid="stHeader"] {
            background-color: transparent !important;
            height: 0px !important;
            background: transparent !important;
            pointer-events: none !important; /* Tıklamalar alt katmana geçsin */
        }
        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem !important; /* 1 yerine 0 yaparsan tamamen yapışır */
            padding-left: 2rem;
            padding-right: 2rem;
            background-color: transparent !important;
            z-index: 10 !important; /* Arka plandan daha yukarıda */
            pointer-events: auto !important; /* Tıklamaları kabul et */
        }

        /* 3. ORTADAKİ DİKDÖRTGENİ ŞEFFAF YAP (Sadece metinler kalsın) */
        .hero-content {
            background: transparent !important; /* Arka plan resmini ve rengini sildik */
            border: none !important;            /* Çerçeveyi kaldırdık */
            box-shadow: none !important;        /* Gölgeyi kaldırdık */
            text-align: center;
            padding: 40px 10px;
            margin-bottom: 20px;
        }

        /* 4. FOOTER YAZILARININ RENGİ */
        .footer-links {
            color: #94a3b8;
            text-align: center;
            padding: 20px;
            font-size: 14px;
        }        

        
        div.stButton > button {
            background: linear-gradient(90deg, #0061ff, #60efff) !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 2rem !important; /* Streamlit'in kendi padding'ine yakın tutalım */
            border-radius: 10px !important;
            font-weight: 700 !important;
            transition: all 0.2s ease-in-out !important;
            outline: none !important;
            /* Genişliği Streamlit'e bırakıyoruz (use_container_width parametresiyle yöneteceğiz) */
            position: relative !important; /* Katmanlandırmayı aktif et */
            z-index: 9999 !important;      /* Butonu tüm katmanların en üstüne çıkar */
            pointer-events: auto !important; /* Tıklama olaylarını butonun kendisine çek */
                
            transition: all 0.3s ease !important;
            animation: breathingGlow 4s ease-in-out infinite;
        }

        /* Hover Efekti */
        div.stButton > button:hover {
            animation: none !important;
            box-shadow: 0 5px 15px rgba(96, 239, 255, 0.6) !important;
            transform: scale(1.02) !important;
            color: white !important;
        }

        /* Tıklama Efekti */
        div.stButton > button:active {
            transform: scale(0.98) !important;
        }
        
        div.stButton > button * {
        pointer-events: none; /* İçindeki öğeler tıklamayı engellemesin, butonun kendisi alsın */
        }
                

        /* Dinamik Mesh Gradient Arka Plan (Yeni Nesil) */
        .stApp {
            background: linear-gradient(125deg, #0f172a, #1e1b4b, #312e81, #1e1b4b);
            background-size: 400% 400%;
            animation: meshGradient 15s ease infinite;
            pointer-events: none !important;
        }
        @keyframes meshGradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* --- ORİJİNAL KART TASARIMI (İLK HALİ) --- */
        .product-card {
            background: linear-gradient(145deg, #181b21, #222631); /* Orijinal koyu gradyan */
            border: 1px solid #2d3139; /* Orijinal sınır çizgisi */
            border-radius: 16px; /* Orijinal yuvarlatma */
            padding: 15px;
            margin: 8px;
            height: 420px; 
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .product-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 25px rgba(0, 255, 136, 0.15);
            border-color: #00ff88;
        }

        .img-container {
            width: 100%;
            height: 180px;
            background-color: #ffffff; /* Orijinal beyaz arka plan */
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            margin-bottom: 10px;
            border: 2px solid #e0e0e0; /* Orijinal çerçeve */
        }

        .img-container img {
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }

        .brand-text { 
            color: #60efff; /* Orijinal turuncu */
            font-weight: 800;
            text-transform: uppercase;
            margin: 5px 0 0 0;
        }
        
        .name-text { 
            color: #d1d5db; /* Orijinal gri metin */
            height: 40px; 
            overflow: hidden; 
            line-height: 1.4; 
        }
        
        .price-text { 
            color: #00ff88;
            font-weight: 900; 
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        }

        /* --- CHAT VE LOGO ÖĞELERİ --- */
        .logo-container {
            display: flex; align-items: center; background: rgba(255, 255, 255, 0.03);
            padding: 10px 20px; border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px); width: fit-content;
        }
        
        @keyframes breathingGlow {
        0% {
            /* Başlangıç hali (Normal Gölge) */
            box-shadow: 0 4px 15px rgba(0, 97, 255, 0.3);
            transform: scale(1); /* Normal boyut */
        }
        50% {
            /* Nefes aldığı an (Parlak ve Hafif Büyük) */
            /* Mavi ve turkuaz karışımı güçlü bir parlama */
            box-shadow: 0 0 25px rgba(96, 239, 255, 0.6), 0 0 10px rgba(0, 97, 255, 0.4);
            transform: scale(1.01); /* Çok hafif büyüme, organik his için */
        }
        100% {
            /* Nefes verdiği an (Başlangıca Dönüş) */
            box-shadow: 0 4px 15px rgba(0, 97, 255, 0.3);
            transform: scale(1);
        }
        }
                
        
        @keyframes flowGradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
        }
        
        .flowing-text {
        /* Mavi ve turkuaz tonlarında, akışın belli olması için 3 renkli bir gradyan */
        background: linear-gradient(90deg, #0061ff, #60efff, #0061ff);
        background-size: 200% auto; /* Gradyanı genişletiyoruz ki hareket alanı kalsın */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        
        /* Animasyon ayarları: 3 saniyede akıp gitsin */
        animation: flowGradient 3s linear infinite;
        
        font-weight: 900;
        }
    </style>
    """, unsafe_allow_html=True)

