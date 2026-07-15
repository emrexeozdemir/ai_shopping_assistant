import streamlit as st
from styles import apply_styles
from functions import *
# Sayfaları import et
from views.home_page import show_home
from views.search_page import show_search
from views.favorites_page import show_favorites
from views.about_page import show_about

st.set_page_config(page_title="AI Shopping Assistant", layout="wide")
apply_styles()
db_baslat()

if 'page' not in st.session_state: st.session_state['page'] = "Home"
if 'urunler_listesi' not in st.session_state: st.session_state['urunler_listesi'] = []
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'username' not in st.session_state: st.session_state['username'] = ""
if 'ai_tavsiyesi' not in st.session_state: st.session_state['ai_tavsiyesi'] = None
   
nav_col = st.columns([1, 1, 1, 1, 1])
with nav_col[0]:
    if st.button("🏠 Ana Sayfa", use_container_width=True): st.session_state['page'] = "Home"; st.rerun()
with nav_col[1]:
    if st.button("🔍 AI Arama", use_container_width=True): st.session_state['page'] = "Search"; st.rerun()
with nav_col[2]:
    if st.button("❤️ Favoriler", use_container_width=True): st.session_state['page'] = "Favorites"; st.rerun()
with nav_col[3]:
    if st.button("ℹ️ Hakkımızda", use_container_width=True): st.session_state['page'] = "About"; st.rerun()
with nav_col[4]:
    if not st.session_state['logged_in']:
        with st.popover("👤 Giriş", width='stretch'):
            auth_choice = st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"], horizontal=True, label_visibility="collapsed")
            u_name = st.text_input("Kullanıcı Adı")
            u_pass = st.text_input("Şifre", type="password")
            
            if st.button("Onayla", width='stretch'):
                if auth_choice == "Giriş Yap":
                    if giris_kontrol(u_name, u_pass):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = u_name
                        st.rerun()
                    else:
                        st.error("Kullanıcı adı veya şifre hatalı!")
                else:
                    if kullanici_kaydet(u_name, u_pass):
                        st.success("Kayıt başarılı, giriş yapabilirsiniz!")
                    else:
                        st.error("Bu kullanıcı adı zaten alınmış.")
    else:
        # GİRİŞ YAPILDIYSA KULLANICI MENÜSÜ (POP-UP)
        with st.popover(f"👋 Hoş geldin, {st.session_state['username']}", width='stretch'):
            st.info("Hesap ayarlarınız yakında eklenecektir.")
            if st.button("🚪 Güvenli Çıkış", width='stretch'):
                st.session_state['logged_in'] = False
                st.session_state['username'] = ""
                st.rerun()

st.divider()

if st.session_state['page'] == "Home":
    show_home()
elif st.session_state['page'] == "Search":
    show_search()
elif st.session_state['page'] == "Favorites":
    show_favorites()
elif st.session_state['page'] == "About":
    show_about()