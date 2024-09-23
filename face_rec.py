import numpy as np
import pandas as pd
import cv2

import redis

# insight face
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise
# time
import time
from datetime import datetime

import os


# Redis Sunucusuna Bağlan
# Redis sunucusuna bağlanma işlemi
hostname = 'your-hostname'
portnumber = your-portnumber
password = 'your-pass'

r = redis.StrictRedis(host=hostname,
                      port=portnumber,  
                      password=password)

# Veritabanından Veri Getir
# Veritabanından veri almak için işlev
def retrive_data(name):
    retrive_dict= r.hgetall(name)
    retrive_series = pd.Series(retrive_dict)
    retrive_series = retrive_series.apply(lambda x: np.frombuffer(x,dtype=np.float32))
    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))
    retrive_series.index = index
    retrive_df =  retrive_series.to_frame().reset_index()
    retrive_df.columns = ['name_role','facial_features']
    retrive_df[['Name','Role']] = retrive_df['name_role'].apply(lambda x: x.split('@')).apply(pd.Series)
    return retrive_df[['Name','Role','facial_features']]


# Yüz Analizini Yapılandır
# Yüz analizini yapılandırmak için işlev
faceapp = FaceAnalysis(name='buffalo_sc',root='insightface_model', providers = ['CPUExecutionProvider'])
faceapp.prepare(ctx_id = 0, det_size=(640,640), det_thresh = 0.5)

# ML Arama Algoritması
def ml_search_algorithm(dataframe,feature_column,test_vector,
                        name_role=['Name','Role'],thresh=0.5):
    """
    kosinüs benzerliğine dayalı arama algoritması
    """
    # adım-1: veri çerçevesini (veri koleksiyonunu) al
    dataframe = dataframe.copy()
    # adım-2: Veri çerçevesinden yüz gömme dizinini al ve diziye dönüştür
    X_list = dataframe[feature_column].tolist()
    x = np.asarray(X_list)
    
    # adım-3: Kosinüs benzerliğini hesapla
    similar = pairwise.cosine_similarity(x,test_vector.reshape(1,-1))
    similar_arr = np.array(similar).flatten()
    dataframe['cosine'] = similar_arr

    # adım-4: verileri filtrele
    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        # adım-5: kişinin adını al
        data_filter.reset_index(drop=True,inplace=True)
        argmax = data_filter['cosine'].argmax()
        person_name, person_role = data_filter.loc[argmax][name_role]
        
    else:
        person_name = 'Zanli'
        person_role = 'Zanli'
        
    return person_name, person_role


### Gerçek Zamanlı Tahmin
# Her 1 dakikada bir günlük kaydetmemiz gerekiyor
class RealTimePred:
    def __init__(self):
        self.logs = dict(name=[],role=[],current_time=[])
        
    def reset_dict(self):
        self.logs = dict(name=[],role=[],current_time=[])
        
    def saveLogs_redis(self):
        # adım-1: bir günlük veri çerçevesi oluştur
        dataframe = pd.DataFrame(self.logs)        
        # adım-2: tekrarlayan bilgileri düşür (farklı isim)
        dataframe.drop_duplicates('name',inplace=True) 
        # adım-3: veriyi redis veritabanına gönder (liste)
        # veriyi kodla
        name_list = dataframe['name'].tolist()
        role_list = dataframe['role'].tolist()
        ctime_list = dataframe['current_time'].tolist()
        encoded_data = []
        for name, role, ctime in zip(name_list, role_list, ctime_list):
            if name != 'Zanli':
                concat_string = f"{name}@{role}@{ctime}"
                encoded_data.append(concat_string)
                
        if len(encoded_data) >0:
            r.lpush('attendance:logs',*encoded_data)
        
                    
        self.reset_dict()     

    def get_successful_matches(self):
        successful_matches = []
        for i in range(len(self.logs['name'])):
            if self.logs['name'][i] != 'Zanli':
                match = {
                    'Name': self.logs['name'][i],
                    'Role': self.logs['role'][i],
                    'Timestamp': self.logs['current_time'][i]
                }
                successful_matches.append(match)
        return successful_matches
    
        
    def face_prediction(self,test_image, dataframe,feature_column,
                            name_role=['Name','Role'],thresh=0.5):
        # adım-1: zamanı bul
        current_time = str(datetime.now())
        
        # adım-1: test görüntüsünü al ve insight face'e uygula
        results = faceapp.get(test_image)
        test_copy = test_image.copy()
        # adım-2: for döngüsünü kullan ve her bir gömme çıkart ve ml_search_algorithm'a geçir

        for res in results:
            x1, y1, x2, y2 = res['bbox'].astype(int)
            embeddings = res['embedding']
            person_name, person_role = ml_search_algorithm(dataframe,
                                                        feature_column,
                                                        test_vector=embeddings,
                                                        name_role=name_role,
                                                        thresh=thresh)
            if person_name == 'Zanli':
                color =(0,0,255) # bgr
            else:
                color = (0,255,0)

            cv2.rectangle(test_copy,(x1,y1),(x2,y2),color)

            text_gen = person_name
            cv2.putText(test_copy,text_gen,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
            cv2.putText(test_copy,current_time,(x1,y2+10),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
            # günlük sözlüğüne bilgileri kaydet
            self.logs['name'].append(person_name)
            self.logs['role'].append(person_role)
            self.logs['current_time'].append(current_time)
            

        return test_copy


#### Kayıt Formu
class RegistrationForm:
    def __init__(self):
        self.sample = 0
    def reset(self):
        self.sample = 0
        
    def get_embedding(self,frame):
        # insightface modelinden sonuçları al
        results = faceapp.get(frame,max_num=1)
        embeddings = None
        for res in results:
            self.sample += 1
            x1, y1, x2, y2 = res['bbox'].astype(int)
            cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),1)
            # metin örnekleri bilgisini yerleştir
            text = f"örnekler = {self.sample}"
            cv2.putText(frame,text,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.6,(255,255,0),2)
            
            # yüz özellikleri
            embeddings = res['embedding']
            
        return frame, embeddings
    
    def save_data_in_redis_db(self,name,role):
        # adım-1: ismi doğrula
        if name is not None:
            if name.strip() != '':
                key = f'{name}@{role}'
            else:
                return 'name_false'
        else:
            return 'name_false'
        
        # eğer face_embedding.txt mevcutsa
        if 'face_embedding.txt' not in os.listdir():
            return 'file_false'
        
        
        # adım-1: "face_embedding.txt" dosyasını yükle
        x_array = np.loadtxt('face_embedding.txt',dtype=np.float32) # düzleştirilmiş dizi            
        
        # adım-2: diziye dönüştür (uygun şekil)
        received_samples = int(x_array.size/512)
        x_array = x_array.reshape(received_samples,512)
        x_array = np.asarray(x_array)       
        
        # adım-3: ortalama gömmeleri hesapla
        x_mean = x_array.mean(axis=0)
        x_mean = x_mean.astype(np.float32)
        x_mean_bytes = x_mean.tobytes()
        
        # adım-4: bunu redis veritabanına kaydet
        # redis karmaları
        r.hset(name='academy:register',key=key,value=x_mean_bytes)
        
        # 
        os.remove('face_embedding.txt')
        self.reset()
        
        return True
