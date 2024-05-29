import streamlit as st
from Home import face_rec
import av
import time
import cv2
import os
import tempfile

# Sayfa yapılandırması
st.set_page_config(page_title='Tahmin', layout='wide')

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
    .spinner {
        text-align: center;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık ve Alt Başlık
st.markdown("<div class='main-header'>Tahmin</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Video Yüz Tanıma Sistemi</div>", unsafe_allow_html=True)

# Logo Ekleme
#st.image("C:/Users/Muhammed Kartal/Desktop/Codes/WebApp/4_attendance_app/Logo/images.png", width=120, use_column_width='auto')

# Redis Veritabanından veri alınıyor
st.markdown("<div class='spinner'>", unsafe_allow_html=True)
with st.spinner('Redis Veritabanından veri alınıyor ...'):    
    redis_face_db = face_rec.retrive_data(name='academy:register')
    st.dataframe(redis_face_db)
st.markdown("</div>", unsafe_allow_html=True)

st.success("Veriler başarılı bir şekilde sisteme entegre edildi")

# Streamlit dosya yükleyici
uploaded_file = st.file_uploader("Bir video dosyası seçin", type=["mp4", "avi", "mkv"], accept_multiple_files=False)

# Video işlemek için geri çağırma işlevi
def process_video(video_file, redis_db):
    realtimepred = face_rec.RealTimePred()  # Gerçek zamanlı tahmin sınıfı
    waitTime = 30  # saniye cinsinden bekleme süresi
    setTime = time.time()

    if video_file is not None:
        # Yüklenen dosyayı geçici bir dizine kaydet
        with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
            temp_file.write(video_file.read())
            temp_file.seek(0)

            # OpenCV ile video dosyasını açın
            video_capture = cv2.VideoCapture(temp_file.name)

            # Video özelliklerini alın
            fps = int(video_capture.get(cv2.CAP_PROP_FPS))
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Başarılı eşleşmeleri saklamak için liste
            successful_frames = []

            # Video oynatıcıyı başlatın
            while video_capture.isOpened():
                ret, frame = video_capture.read()

                if not ret:
                    break

                # Yüz tanıma yapma
                pred_img = realtimepred.face_prediction(frame, redis_db, 'facial_features', ['Name', 'Role'], thresh=0.5)

                if pred_img is not None:
                    successful_frames.append(pred_img)

            video_capture.release()

            # Başarılı eşleşmeleri göstermek 
            for frame in successful_frames:
                # Başarılı eşleşmeleri göstermek için BGR görüntüyü Streamlit için RGB'ye dönüştür
                rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Video karesini göster
                st.image(rgb_img, channels='RGB', use_column_width=True)

            # Verileri veritabanına kaydet
            realtimepred.saveLogs_redis()
            st.success('Veriler Redis veritabanına kaydedildi')

if uploaded_file is not None:
    # Yüz tanıma ile işlenmiş videoyu göster
    process_video(uploaded_file, redis_face_db)

# Alt bilgi
st.markdown("<div class='footer'>© 2024 Haliç Üniversitesi Bilgi İşlem Daire Başkanlığı. Tüm hakları saklıdır.</div>", unsafe_allow_html=True)
