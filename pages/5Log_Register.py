import streamlit as st
from Home import face_rec
import redis

st.set_page_config(page_title='Reporting', layout='wide')
st.subheader('Kontrol / Log')

name = 'attendance:logs'

def load_logs(name, end=-1):
    logs_list = face_rec.r.lrange(name, start=0, end=end) 
    return logs_list

def clear_logs(name):
    face_rec.r.delete(name)

tab1, tab2 = st.tabs(['Registered Data', 'Logs'])

with tab1:
    if st.button('Refresh Data'):
        with st.spinner('DataBaseden Veriler Çekiliyor ...'):    
            redis_face_db = face_rec.retrive_data(name='academy:register')
            # 
            st.dataframe(redis_face_db[['Name', 'Role', 'facial_features']])

with tab2:
    if st.button('Refresh Logs'):
        logs_list = load_logs(name=name)
        # 
        st.write(logs_list)
        
        # 
        if st.button('Log Tarihçesini Temizle'):
            with st.spinner('Siliniyor...'):
                clear_logs(name)
            st.success('Log Tarihçesi Temizlendi!')
