import streamlit as st
from Home import face_rec
import numpy as np
import io
from PIL import Image
import cv2

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
st.markdown("<div class='sub-header'>Lütfen bilgilerinizi girin ve yüz tanıma için resim yükleyin</div>", unsafe_allow_html=True)

# Gerekli kütüphaneleri içe aktarın
import streamlit as st
from Home import face_rec
import numpy as np
import io
from PIL import Image
import cv2

# Session State başlatma
def init_session_state():
    if 'uploaded_images' not in st.session_state:
        st.session_state.uploaded_images = []

init_session_state()

# Kişi adını ve rolünü alın
st.markdown("<div class='form-section'>", unsafe_allow_html=True)
person_name = st.text_input(label='İsim', placeholder='İsim & Soyisim')
role = st.selectbox(label='Rol Seçin', options=('Zanlı', 'Şüpheli'))
st.markdown("</div>", unsafe_allow_html=True)

# Kamera girişi ve resim gösterimi
picture = st.camera_input("Fotoğraf çek")
if picture:
    st.image(picture)

# Yüklenen görüntüleri ve yerleştirmeleri görüntülemek için yardımcı işlev
def display_uploaded_images(images):
    for img_data in images:
        reg_img, embedding = img_data
        st.image(reg_img, channels='BGR')

# Yüz tanıma için resim yükleme
st.markdown("<div class='form-section'>", unsafe_allow_html=True)
uploaded_image_files = st.file_uploader("Yüz tanıma için resimleri yükleyin", type=["jpg", "png"], accept_multiple_files=True)

# Resim Yüklemeye devam
if st.button('Yükle'):
    if uploaded_image_files:
        for uploaded_image_file in uploaded_image_files:
            image_bytes = uploaded_image_file.read()
            img = np.array(cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR))
            reg_img, embedding = face_rec.RegistrationForm().get_embedding(img)

            if embedding is not None:
                st.session_state.uploaded_images.append((reg_img, embedding))

        # Yüklenen tüm resimleri görüntüleme
        display_uploaded_images(st.session_state.uploaded_images)
st.markdown("</div>", unsafe_allow_html=True)

# Verileri redis veritabanında kaydetme
st.markdown("<div class='form-section'>", unsafe_allow_html=True)
if st.button('Kayıt et'):
    if person_name.strip() == '':
        st.error('Lütfen ismi boş bırakmayın')
    else:
        # Verileri Redis veritabanına kaydet
        for reg_img, embedding in st.session_state.uploaded_images:
            with open('face_embedding.txt', mode='ab') as f:
                np.savetxt(f, embedding)
        face_rec.RegistrationForm().save_data_in_redis_db(person_name, role)
        st.success(f"{person_name} başarıyla kaydedildi")
st.markdown("</div>", unsafe_allow_html=True)

# Alt bilgi
st.markdown("<div class='footer'>© 2024 Haliç Üniversitesi Bilgi İşlem Daire Başkanlığı. Tüm hakları saklıdır.</div>", unsafe_allow_html=True)
