import streamlit as st
from Home import face_rec

import cv2
import numpy as np
import redis
from streamlit_webrtc import webrtc_streamer
import av

# Sayfa yapılandırması
st.set_page_config(page_title='Kayıt Formu', layout='wide')

# CSS ile stil iyileştirmeleri
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .main-header {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        margin-top: 20px;
    }
    .sub-header {
        text-align: center;
        font-size: 1.5em;
        color: gray;
        margin-bottom: 20px;
    }
    .form-section {
        text-align: center;
        margin-top: 30px;
    }
    .divider {
        margin: 20px 0;
    }
    .footer {
        text-align: center;
        font-size: 0.8em;
        color: gray;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık ve Alt Başlık
st.markdown("<div class='main-header'>Kayıt Formu</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Lütfen bilgilerinizi girin ve yüz tanıma için video akışını başlatın</div>", unsafe_allow_html=True)

# Redis DB data setine bağlanma
hostname = 'redis-12142.c328.europe-west3-1.gce.redns.redis-cloud.com'
portnumber = 12142
password = '4u4Una8wpymqKW0TnpLIMGinEsH5TXBu'

r = redis.StrictRedis(host=hostname, port=portnumber, password=password)

# Kayıt formunu başlatma
registration_form = face_rec.RegistrationForm()

# Kişi adını ve rolünü alın
st.markdown("<div class='form-section'>", unsafe_allow_html=True)
person_name = st.text_input(label='İsim', placeholder='İsim & Soyisim')
role = st.selectbox(label='Rol Seçin', options=('Zanlı', 'Şüpheli'))
st.markdown("</div>", unsafe_allow_html=True)

# Video akışı için callback fonksiyonu
def video_callback_func(frame):
    img = frame.to_ndarray(format='bgr24') # 3 boyutlu bgr formatında dizi
    reg_img, embedding = registration_form.get_embedding(img)
    
    # 1. Adım: Gömüt verilerini yerel bilgisayara metin dosyasına kaydetme
    if embedding is not None:
        with open('face_embedding.txt', mode='ab') as f:
            np.savetxt(f, embedding)

    return av.VideoFrame.from_ndarray(reg_img, format='bgr24')

# Video akışını başlat
webrtc_streamer(key='registration', video_frame_callback=video_callback_func)

# Verileri Redis veritabanında kaydetme
st.markdown("<div class='form-section'>", unsafe_allow_html=True)
if st.button('Kayıt et'):
    return_val = registration_form.save_data_in_redis_db(person_name, role)
    if return_val == True:
        st.success(f"{person_name} başarıyla kayıt edildi")
    elif return_val == 'name_false':
        st.error('Lütfen ismi boş bırakmadan girin')
    elif return_val == 'file_false':
        st.error('face_embedding.txt bulunamadı, sayfayı yenileyin.')
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Redis veritabanından kişi silme
st.markdown("<div class='form-section'>", unsafe_allow_html=True)
persons_list = [name_role.decode() for name_role in r.hkeys('academy:register')]
selected_person = st.selectbox("Silinecek kişiyi seçin:", persons_list)
if st.button('Kişiyi Sil'):
    if selected_person:
        key = selected_person
        deleted = r.hdel('academy:register', key)
        if deleted:
            st.success(f"{selected_person} başarıyla silindi.")
        else:
            st.error(f"{selected_person} silinirken bir hata oluştu.")
    else:
        st.warning("Lütfen silmek istediğiniz kişiyi seçin.")
st.markdown("</div>", unsafe_allow_html=True)

# Alt bilgi
st.markdown("<div class='footer'>© 2024 Haliç Üniversitesi Bilgi İşlem Daire Başkanlığı. Tüm hakları saklıdır.</div>", unsafe_allow_html=True)
