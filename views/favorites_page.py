import streamlit as st 
from functions import *

def show_favorites():
    if st.session_state['logged_in']:
        # Veritabanından favorileri çek (Sütun sırasına dikkat: marka, ad, fiyat, link, gorsel, kaynak)
        conn = sqlite3.connect('shopping_app.db')
        c = conn.cursor()
        sorgu = """
            SELECT f.marka, f.ad, 
                (SELECT p.fiyat_sayisal FROM price_history p WHERE p.link = f.link ORDER BY p.tarih DESC LIMIT 1) as guncel_fiyat,
                f.link, f.gorsel, f.id, f.kaynak,
                (SELECT p.fiyat_sayisal FROM price_history p WHERE p.link = f.link ORDER BY p.tarih ASC LIMIT 1) as ilk_fiyat
            FROM favorites f 
            WHERE f.username = ?
        """
        c.execute(sorgu, (st.session_state['username'],))
        favs = c.fetchall()
        conn.close()
        
        if favs:
            st.subheader(f"❤️ {st.session_state['username']} Kullanıcısının Favorileri")
            #favori_takip_sistemi(st.session_state['username'], favs)
            # Listeyi 3'erli gruplara bölüyoruz (Arama sayfasıyla aynı mantık)
            for i in range(0, len(favs), 4):
                cols = st.columns(4)
                current_batch = favs[i : i + 4]
                
                for idx, f in enumerate(current_batch):
                    # Veritabanından gelen f yapısı: (marka, ad, fiyat, link, gorsel)
                    f_marka, f_ad, f_fiyat, f_link, f_gorsel, f_id, f_kaynak, f_ilk_fiyat = f
                    global_fav_idx = i + idx
                    
                    fiyat_gorunumu = f"{f_fiyat:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".") if f_fiyat else "Fiyat Bilgisi Yok"
                    
                    fiyat_satiri_html = f'<p class="price-text" style="margin: 0;">{fiyat_gorunumu}</p>'

                    if f_fiyat and f_ilk_fiyat and f_fiyat != f_ilk_fiyat:
                        fark = float(f_fiyat) - float(f_ilk_fiyat)
                        if fark < 0:
                            yuzde = int(abs(fark / f_ilk_fiyat) * 100)
                            fiyat_satiri_html += f'<span style="color: #00ff88; font-size: 16px; font-weight: bold; margin-left: 8px;"> ↓ %{yuzde}</span>'
                        elif fark > 0:
                            fiyat_satiri_html += f'<span style="color: #ff4b4b; font-size: 16px; font-weight: bold; margin-left: 8px;"> ↑</span>'

                    with cols[idx]:
                        # Arama sayfasıyla aynı HTML Kart Yapısı
                        st.markdown(f"""
                            <div class="product-card">
                                <div class="img-container">
                                    <img src="{f_gorsel if f_gorsel else 'https://ih1.redbubble.net/image.4905811447.8675/flat,750x,075,f-pad,750x1000,f8f8f8.jpg'}">
                                </div>
                                <p class="brand-text" style="font-size: 24px">{f_marka}</p>
                                <p class="name-text" style="font-size: 15px">{f_ad[:100]}</p>
                                <div style="display: flex; align-items: baseline;">
                                    {fiyat_satiri_html}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Butonlar
                        c1, c2, c3 = st.columns([1, 2, 1]) # 3 kolon yaptık
                        with c1:
                            st.link_button("🛒", f_link, width='stretch')
                        with c2:
                            with st.popover("📊 Fiyat Analizi",width='stretch'):
                                st.write("### Fiyat Değişim Geçmişi")
                                
                                # Veritabanı bağlantısını timeout ile açıyoruz (Locked hatasını önlemek için)
                                conn = sqlite3.connect('shopping_app.db', timeout=10)
                                import pandas as pd
                                
                                # Verileri çekiyoruz
                                query = "SELECT tarih as Tarih, fiyat_sayisal as Fiyat FROM price_history WHERE link = ? ORDER BY tarih DESC"
                                df = pd.read_sql_query(query, conn, params=(f_link,))
                                conn.close()

                                if not df.empty:
                                    # Tarih formatını güzelleştirelim (Örn: 24.05.2024 14:30)
                                    df['Tarih'] = pd.to_datetime(df['Tarih']).dt.strftime('%d.%m.%Y %H:%M')
                                    
                                    # Fiyatın yanına TL ekleyerek şık bir tablo gösterelim
                                    df['Fiyat'] = df['Fiyat'].apply(lambda x: f"{x:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", "."))
                                    
                                    # 2 Sütunlu tabloyu basıyoruz
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                                    
                                    if len(df) > 1:
                                        ilk_fiyat = float(df['Fiyat'].iloc[-1].replace(" TL", "").replace(".", "").replace(",", "."))
                                        son_fiyat = float(df['Fiyat'].iloc[0].replace(" TL", "").replace(".", "").replace(",", "."))
                                        fark = son_fiyat - ilk_fiyat
                                        if fark < 0:
                                            st.success(f"İndirim: Ürün ilk eklediğinizden beri {abs(fark):.2f} TL ucuzlamış!")
                                        elif fark > 0:
                                            st.warning(f"Zam: Ürün ilk eklediğinizden beri {fark:.2f} TL pahalanmış.")
                                else:
                                    st.info("Bu ürün için henüz geçmiş fiyat kaydı bulunmuyor.")
                        with c3:
                            # FAVORİDEN ÇIKARMA BUTONU
                            if st.button("🗑️", key=f"del_fav_{global_fav_idx}", help="Favorilerden Kaldır",width='stretch'):
                                favori_sil(st.session_state['username'], f_link)
                                st.toast("Ürün favorilerden kaldırıldı!")
                                time.sleep(0.5) # Kullanıcının toast mesajını görmesi için kısa bir bekleme
                                st.rerun() # Sayfayı yenileyerek listeyi güncelliyoruz
        else:
            st.info("Henüz favorilere eklenmiş bir ürününüz bulunmuyor.")
    else:
        st.warning("Favorilerinizi görmek için lütfen giriş yapın.")
