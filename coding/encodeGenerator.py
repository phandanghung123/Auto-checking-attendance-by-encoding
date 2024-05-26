import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
#send to data base
cred = credentials.Certificate("automatic-attendance.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":'https://automatic-attendance-94b58-default-rtdb.asia-southeast1.firebasedatabase.app/',
    "storageBucket":"automatic-attendance-94b58.appspot.com"#copy link from firebase and remove gs://
})
folderPath='images'
listFiles=os.listdir(folderPath)
face=[]
ID=[]
#read local data to encoding 
for i in listFiles:
    face.append(cv2.imread(os.path.join(folderPath,i)))
    simpleFileName=os.path.basename(i)
    # set up bucket and blob in local
    bucket=storage.bucket()
    blob=bucket.blob(simpleFileName)
    #send to storage
    fileName = os.path.join(folderPath, i)
    blob.upload_from_filename(fileName)
    #take the id from file name
    index=i.index('.')
    ID.append(i[:index])
print(ID)   
#encoding all data
def findEncoding(face):
    encodeList=[]
    for i in face:
        i=cv2.cvtColor(i,cv2.COLOR_BGR2RGB)#convert to the color base suitable for encoding
        encode=face_recognition.face_encodings(i)[0] 
        encodeList.append(encode)
    return encodeList
print("Dang xu ly. Vui long doi trong vai giay...")

faceKnown=findEncoding(face)   
face_with_ID=[faceKnown,ID]
file=open("encoder.p","wb")
pickle.dump(face_with_ID,file)
file.close()
print("Hoan Thanh") 