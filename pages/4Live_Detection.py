import streamlit as st
import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time

st.set_page_config(page_title='Tahminler')
st.subheader('Gerçek Zamanlı Yüz Tanıma Sistemi')

# Redis Veritabanından veri alınıyor
with st.spinner('Redis Veritabanından veri alınıyor ...'):    
    redis_face_db = face_rec.retrive_data(name='academy:register')
    st.dataframe(redis_face_db)
    
st.success("Veriler başarıyla Redis Veritabanından alındı")

# Zaman
waitTime = 30 # saniye cinsinden bekleme süresi
setTime = time.time()
realtimepred = face_rec.RealTimePred() # gerçek zamanlı tahmin sınıfı

# Gerçek Zamanlı Yüz Tanıma
# streamlit webrtc
# geri çağırma işlevi
def video_frame_callback(frame):
    global setTime
    
    img = frame.to_ndarray(format="bgr24") # 3 boyutlu numpy dizisi
    # dizide yapılacak işlem
    pred_img = realtimepred.face_prediction(img, redis_face_db,
                                            'facial_features', ['Name', 'Role'], thresh=0.5)
    
    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waitTime:
        realtimepred.saveLogs_redis()
        setTime = time.time() # zamanı sıfırla        
        print('Redis veritabanına kaydedildi')
    
    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")

webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback)
