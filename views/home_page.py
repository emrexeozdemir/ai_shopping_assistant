import streamlit as st
def show_home():
    col_h1, col_h2, col_h3 = st.columns([1, 4, 1])
    with col_h2:
        st.markdown("""
            <div class="hero-content">
            <div style="display: inline-flex; align-items: center; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 15px 30px; border-radius: 100px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.2);">
                <div style="background: linear-gradient(90deg, #0061ff, #60efff); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 900; margin-right: 15px;">AI</div>
                <span style="font-size: 24px; font-weight: 800; color: white; letter-spacing: -1px;">AI Shopping Assistant</span>
            </div>
            
            <h1 style="font-size: 64px; font-weight: 900; color: white; line-height: 1.1; margin-bottom: 25px;">
                Alışverişin <span class="flowing-text"> 
                Yapay Zeka
                </span> Hali.
            </h1>

            <p style="font-size: 20px; color: #cbd5e1; max-width: 800px; margin: 0 auto;">
                Sadece ürünü ve istediğiniz özellikleri yazın, gerisini yapay zeka destekli asistanımıza bırakın.
                Asistan milyonlarca ürünü saniyeler içinde tarar ve istediğiniz özelliklerdeki ürünleri sunar.
            </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_s1,col_s2,col_s3 = st.columns([1,1,1])
        with col_s2:
            if st.button("🔍 Akıllı Aramayı Başlat", use_container_width=True, type="primary"):
                st.session_state['page'] = "Search"
                st.rerun()

    # Footer (En Alt Bilgi Kısmı)
    st.markdown("""
        <div class="footer">
            <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 20px;">
                <a href="#" style="color: #94a3b8; text-decoration: none;">Hakkımızda</a>
                <a href="#" style="color: #94a3b8; text-decoration: none;">Gizlilik</a>
                <a href="#" style="color: #94a3b8; text-decoration: none;">İletişim</a>
            </div>
            <p>© 2026 AI-Powered Smart Assistant. Tüm hakları saklıdır.</p>
            <p style="font-size: 12px; opacity: 0.5;">Powered by Gemini 3.1  & Selenium</p>
        </div>
    """, unsafe_allow_html=True)
