from django.db import models

# Create your models here.
class Data():
    """
    มี 2 attribute 
        - Video : file รับข้อมูลวีดีโอจาก Class Video
        - Vehicle : Object รับข้อมูลจาก Class Vehicle 
        
    Method 
        summary สรุปผลโดยรวม 
    """
class Video():
    """
    มี 2 attribute รับข้อมูลจาก AI
        - Weather :String
        - Video : file  
        - video_length : time
    Method 
        - Edit_video อัพโหลดวีดีโอใหม่

    """
class Loop():
    """
    มี 7 Attribute  รับข้อมูลจาก  User  
        - loop_name : string
        - width : float
        - height : float
        - angle : float
        - color : string
        - x_axis : float
        - y_axis : float    
    มี 3 method 
        - edit_loop ปรับ loop เช่น rotate, width of loop
        - add_loop เพิ่ม loop สำหรับ detect 
        - delete_loop ลบ loop
    """
class Vehicle(): 
    """
    3 Attribute รับข้อมูลจาก class AI
        - car_type : string
        - speed : float
        - direction : string
    """

class AI():
    """
    1 Attribute รับข้อมูลจาก class Loop มาวิเคราห์
    - ref_loop : Loop
    
    3 method
    - car_speed :float return speed
    - Detect_type :String return type of car
    - Detect_direction : String return direction of car
    - Detect_weather : String return weather of day
    
    """