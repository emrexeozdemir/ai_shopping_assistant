import streamlit as st

def show_about():
    st.markdown("""
        <div style="text-align: center; padding: 50px 0;">
            <h1 class="flowing-text" style="font-size: 50px;">Sistemin Kalbine Hoş Geldiniz</h1>
            <p style="color: #cbd5e1; font-size: 18px; max-width: 800px; margin: 0 auto;">
                Bu proje, alışverişi sadece bir işlem olmaktan çıkarıp, yapay zekanın rehberliğinde teknolojik bir deneyime dönüştürmek için tasarlandı.
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
            <div class="ai-recommendation-box">
                <h3 style="color: #60efff;">🧠 Beyin: Gemini 3.1</h3>
                <p>Milyonlarca veriyi saniyeler içinde analiz eden ve size özel mantıklı çıkarımlar yapan çekirdek yapımız.</p>
            </div>
            <div class="ai-recommendation-box">
                <h3 style="color: #00ff88;">🛡️ Vizyon: Doğruluk</h3>
                <p>Selenium motoru ile gerçek zamanlı piyasa verilerini çekerek, manipüle edilmemiş saf bilgiye ulaşmanızı sağlıyoruz.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.info("Bu proje bir 'Yapay Zeka Destekli Akıllı Asistan' tez çalışması kapsamında geliştirilmiştir.")