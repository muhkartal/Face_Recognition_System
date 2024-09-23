import streamlit as st

# Sayfa yapılandırması
st.set_page_config(page_title='Yüz Tanıma Sistemi Portalı', layout='wide')

# CSS ile stil iyileştirmeleri
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
    }
    .main-header {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-top: 20px;
        color: #005f86;
    }
    .sub-header {
        text-align: center;
        font-size: 1.2em;
        color: gray;
    }
    .content-section {
        text-align: justify;
        margin-top: 50px;
        padding: 0 100px;
        line-height: 1.6;
    }
    .footer {
        text-align: center;
        font-size: 0.8em;
        color: gray;
        margin-top: 50px;
    }
    .divider {
        margin: 20px 0;
        background-color: #005f86;
        height: 2px;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Header ve logo
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Başlık
st.markdown("<div class='main-header'>Yüz Tanıma Sistemi Portalı</div>", unsafe_allow_html=True)

# Yükleme sürecini göstermek için spinner
with st.spinner("Modeller yükleniyor ve Redis veritabanına bağlanıyor ..."):
    import face_rec

# Kontrol Bölgesi
st.success('Model başarıyla yüklendi')
st.success('Redis veritabanına başarıyla bağlandı')

# Bölücü çizgi
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# İçerik sütunları
cols = st.columns(3)

# Ortadaki sütun için resim eklemek (resim yolunu kendinize göre ayarlayın)
#cols[1].image("C:/Users/Muhammed Kartal/Desktop/Fotolar/SS/Insta/a.png", width=300)

# Alt başlık
st.markdown("<div class='sub-header'>Biggest Supporter</div>", unsafe_allow_html=True)

# Bölücü çizgi
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Ek içerik bölgesi
st.markdown("""
    <div class='content-section'>
       
    </div>
""", unsafe_allow_html=True)

# Alt bilgi
st.markdown("<div class='footer'>© 2024 Muhammed İbrahim Kartal. Tüm hakları saklıdır.</div>", unsafe_allow_html=True)
