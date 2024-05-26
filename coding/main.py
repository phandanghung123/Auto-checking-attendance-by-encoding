import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import numpy as np
#send to data base
cred = credentials.Certificate("automatic-attendance.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":'https://automatic-attendance-94b58-default-rtdb.asia-southeast1.firebasedatabase.app/',
    "storageBucket":"automatic-attendance-94b58.appspot.com"#copy link from firebase and remove gs://
})


# Create a video capture object for the default camera (camera index 0)
cap = cv2.VideoCapture(0)
detect=0

# Set the resolution to 1280x720
cap.set(3, 720)
cap.set(4, 320)
img_bg=cv2.imread('resources/attendance_bg.png')
# import list of mode
folderPath='resources/modes'
listFiles=os.listdir(folderPath)
mode=[]
for i in listFiles:
    mode.append(cv2.imread(os.path.join(folderPath,i)))
    #run the UI
for i in range(len(mode)):
    mode[i] = cv2.resize(mode[i], (300, 398))
print(listFiles)  
modeType=mode[0]
#Read encoding file   
file=open("encoder.p","rb")
face_with_ID=pickle.load(file)
face_encoded,ID=face_with_ID
print(ID)
file.close()

while True:
    # Read a frame from the camera
    succ, img = cap.read()
    # Display the frame in a window named "Face attendance"q
    img = cv2.resize(img, (630, 375))
   
    current_face=face_recognition.face_locations(img)
    frameEncoding=face_recognition.face_encodings(img,current_face)
      # Adjusted to match the target space
    img_bg[140:140+398, 800:800+300] = modeType
    img_bg[166:166+375, 121:121+630] = img
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    
    for Encoding,faceLoc in zip(frameEncoding,current_face):
        match_face=face_recognition.compare_faces (face_encoded,Encoding)
        match_dis=face_recognition.face_distance(face_encoded,Encoding)
        match_index=[index for index,value in enumerate(match_face)  if value] 
        if not match_index:
            print("I do not know any face, STRANGERRRRR")
        else:  
            print("Face detected") 
            if detect==0:
               detect=1
               modeType=mode[3] 
            y1,x2,y2,x1=faceLoc
            box=x1+121,y1+166,x2-x1,y2-y1
            img_bg=cvzone.cornerRect(img_bg,box,rt=0)
         #detect and get data from database
    if detect!=0:
        if 0<detect<10:   
            for i in range(len(match_index)):
                match_ID=ID[match_index[i]]
                peopleInfo=db.reference(f'People/{match_ID}').get()
                bucket=storage.bucket()
                blob=bucket.get_blob(f"{match_ID}.jpg")
                #write info into bg
                img_bg[140:140+398, 800:800+300] = modeType 
                cv2.putText(img_bg,str(peopleInfo['name']),(900,455),
                            cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)  
                cv2.putText(img_bg,str(peopleInfo['total_attendance']),(900,480),
                            cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1) 
                cv2.putText(img_bg,str(peopleInfo['job']),(900,505),
                            cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                decoded_image = cv2.imdecode(array, cv2.IMREAD_COLOR)  # Decodes the image
                img_bg[180:180+216, 840:840+216] = decoded_image 
                #update the database
                if detect==1: 
                    ref=db.reference(f'People/{match_ID}')
                    
                   
                    date = datetime.strptime(peopleInfo['last_time_attendance'], '%Y-%m-%d %H:%M:%S')
                    period = (datetime.now() - date).total_seconds()
                    process_start=datetime.now()
                    if period>60:
                        peopleInfo['total_attendance']+=1
                        peopleInfo['last_time_attendance']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ref.child('total_attendance').set(peopleInfo['total_attendance'])
                        ref.child('last_time_attendance').set(peopleInfo['last_time_attendance'])
                    elif period<60:
                        detect=-10
                            
                
                
        elif 10<detect<15:
            modeType=mode[2] 
            img_bg[140:140+398, 800:800+300] = modeType
        elif detect>16:
            modeType=mode[0]
            peopleInfo=[]
            detect=-1
            match_ID=[]
            img_bg[140:140+398, 800:800+300] = modeType
        elif detect<0:
            modeType=mode[1]
            img_bg[140:140+398, 800:800+300] = modeType   
             
        
            
        detect+=1
    cv2.imshow('Face attendance',img_bg)
        
    key = cv2.waitKey(1)

    # If the user presses the 'q' key, exit the loop
    if key == ord('q') or key==ord('Q'):
        break

   