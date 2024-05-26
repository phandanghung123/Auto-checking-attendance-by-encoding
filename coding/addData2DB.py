import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("automatic-attendance.json")
firebase_admin.initialize_app(cred,{
    "databaseURL":'https://automatic-attendance-94b58-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
ref=db.reference('People')
data={
     "24680753":
        {"name": "Elon Musk",
         "job" : 'CEO',
         "total_attendance": 1,
         "last_time_attendance": "2024-04-07 00:00:00"
        }
}
def add_entry(data, id, name, job, total_attendance, last_time_attendance):
    data[id] = {
        "name": name,
        "job": job,
        "total_attendance": total_attendance,
        "last_time_attendance": last_time_attendance
    }
add_entry(data,"123456111",'Ronaldinho','Football Player','1','2024-04-07 00:00:0')    
add_entry(data,"987654321",'Donald Trump','America President','1','2024-04-07 00:00:0')   
add_entry(data,"2011903012002",'Phan Dang Hung','Student','1','2024-04-07 00:00:0')   
for key,value in data.items():
    ref.child(key).set(value)
