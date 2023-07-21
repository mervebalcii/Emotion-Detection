import cv2
import settings
import numpy as np
import time

import matplotlib.pyplot as plt
import os

from keras_preprocessing.image import img_to_array
from tensorflow.keras.models import load_model


class FaceDetect:



    options = {
        'emotions': [],
    }



    def __init__(self):
        self.dc = 0
        self.mc =0


        # Yüz tespiti için gerekli XML verisi
        self.face_cascade = cv2.CascadeClassifier(settings.DATA['cascades']['face'])

        # Göz tespiti için gerekli XML verisi
        self.eye_cascade = cv2.CascadeClassifier(settings.DATA['cascades']['eye'])

        # Gülümseme tespiti için gerekli XML verisi
        self.smile_cascade = cv2.CascadeClassifier(settings.DATA['cascades']['smile'])

        # Duygu durum modeli
        self.emotion_model = load_model(settings.DATA['models']['emotion'], compile=False)

       

    def run(self, frame, textfile = {"Notr": 0, "Mutlu": 0,"Sinirli": 0, "Korkmus": 0,"Saskin": 0, "Uzgun": 0,"Igrenmis": 0,"kisi":0},flip=False, options=None, _eyes=False, _smiles=False):
        dc=0
        mc=0

        if options is None:


            options = self.options

        if flip is True:

            frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        label = {}
        


        if len(faces) > 0:


            for (x, y, w, h) in faces:
                

                roi_gray = gray[y:y + h, x:x + w]

                roi_color = frame[y:y + h, x:x + w]
                roi_gray = cv2.resize(roi_gray, (64, 64))
                roi_gray = roi_gray.astype('float') / 255.0
                roi_gray = img_to_array(roi_gray)
                roi_gray = np.expand_dims(roi_gray, axis=0)


                # Duygu durumunu analiz ediyoruz
                emotion_predict = self.emotion_model.predict(roi_gray)[0]
                # En yüksek skoru alan duygu durumu
                emotion_probability = np.max(emotion_predict)
                # Tüm duygu durum verileri
                emotions = []
                for (i, (emotion, probability)) in enumerate(zip(settings.EMOTIONS, emotion_predict)):
                    emotions.append({
                        'title': emotion,
                        'percent': round(probability * 100, 2),
                    })

                # Elde edilen skorları bir nesneye atıyoruz
                label = {
                    'emotion': {
                        'title': settings.EMOTIONS[emotion_predict.argmax()],
                        'percent': round(emotion_probability * 100, 2),
                    },
                    'emotions': emotions,
                }


                if emotion_predict.argmax() in options['emotions']:
                    if(w >= 100 and h >=100):

                        cv2.putText(frame, str(label['emotion']['title']) + ' (%' + str(label['emotion']['percent']) + ')',
                                    (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2)
                        num_people = len(faces)
                        cv2.putText(frame, f'        {num_people}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                      #  time.sleep(2)
                        if num_people == 1:
                            self.dc = self.dc + 1
                            if self.dc == 1:
                                textfile["kisi"] += 1



                        if label['emotion']['percent'] > 40 :
                            if str(label['emotion']['title'])== "Mutlu":
                                textfile["Mutlu"] += 1
                            elif str(label['emotion']['title'])== "Notr":
                                textfile["Notr"] += 1
                            elif str(label['emotion']['title']) == "Uzgun":
                                textfile["Uzgun"] += 1
                            elif str(label['emotion']['title']) == "Saskin":
                                textfile["Saskin"] += 1
                            elif str(label['emotion']['title'])== "Sinirli":
                                textfile["Sinirli"] += 1
                            elif str(label['emotion']['title'])== "Korkmus":
                                textfile["Korkmus"] += 1
                            elif str(label['emotion']['title']) == "Igrenmis":
                                textfile["Igrenmis"] += 1

                if _eyes:
                    # Bulunan yüzdeki gözleri tespit ediyoruz
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    # Bulunan gözlerde işlem yapmak için bir döngü kullanıyoruz
                    for (ex, ey, ew, eh) in eyes:
                        # Bulunan gözleri çerçeve içine alıyoruz
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

                if _smiles:
                    # Bulunan yüzde gülücük arıyoruz
                    smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.7, 22)
                    # Bulunan gülücük verisininde işlem yapmak için bir döngü kullanıyoruz
                    for (sx, sy, sw, sh) in smiles:
                        # Bulunan gülücüği çerçeve içine alıyoruz
                        cv2.rectangle(roi_color, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)
        
            
        
        else:

            print("yok")
            self.dc = 0
        emotions = ['Mutlu', 'Notr', 'Uzgun', 'Saskin', 'Sinirli', 'Korkmus', 'Igrenmis']
        percentages = [textfile[emotion] for emotion in emotions]
        num_people = textfile["kisi"]
        
        fig, ax = plt.subplots(1, 3, figsize=(12, 4))
        ax[0].bar(emotions, percentages)
        ax[0].set_ylabel("Yüzdelik")
        ax[0].set_title("Duygu Durumu Yüzdelikleri")

    # Pasta dilimi grafiğini oluşturun
        ax[1].pie(percentages, labels=emotions, autopct='%1.1f%%', startangle=90)
        ax[1].set_title("Duygu Durumu Dağılımı")

    # Kişi sayısını gösteren metni oluşturun
        text = f"Kişi Sayısı: {num_people}"
        ax[2].text(0.5, 0.5, text, fontsize=12, ha='center')
        ax[2].axis("off")
        #ax[2].set_title("Kişi Sayısı")

    # Grafikleri birleştirin
        plt.tight_layout()

    # Şekli PNG dosyası olarak kaydedin
        plt.savefig("combined_chart.png")
        plt.close()

        a = textfile["Mutlu"] + textfile["Notr"] + textfile["Uzgun"] + textfile["Saskin"] + textfile["Sinirli"] + \
            textfile["Korkmus"] + textfile["Igrenmis"]
        if a != 0:
            MutluY =int((100 * textfile["Mutlu"]) / a)
            NotrY = int((100 * textfile["Notr"]) / a)
            UzgunY = int((100 * textfile["Uzgun"]) / a)
            SaskinY =int( (100 * textfile["Saskin"]) / a)
            SinirliY =int( (100 * textfile["Sinirli"]) / a)
            KorkmusY = int((100 * textfile["Korkmus"]) / a)
            IgrenmisY =int( (100 * textfile["Igrenmis"]) / a)
            Kisi = int( textfile["kisi"])
        else:
            MutluY = 1
            NotrY = 1
            UzgunY = 1
            SaskinY = 1
            SinirliY = 1
            KorkmusY = 1
            IgrenmisY = 1
            Kisi = 1
        f = open("textfile.txt", "w")
        f.write(str(textfile) + "\n\n\n" +
                    "Mutlu Yuzdelik" +"  -->  "+ str(MutluY) + "%\n" +
                    "Notr Yuzdelik" +"  -->  "+ str(NotrY) + "%\n" +
                    "Uzgun Yuzdelik" +"  -->  "+str(UzgunY) + "%\n" +
                    "Saskin Yuzdelik" +"  -->  "+ str(SaskinY) + "%\n" +
                    "Sinirli Yuzdelik" +"  -->  "+ str(SinirliY) + "%\n" +
                    "Korkmus Yuzdelik" +"  -->  "+ str(KorkmusY) + "%\n" +
                    "Igrenmiş Yuzdelik" +"  -->  "+ str(IgrenmisY) + "%\n"+
                     "Kişi Sayısı Total "+"  -->  "+ str(Kisi) + "\n")

        
        return {

            'frame': frame,
            'label': label


        }
  