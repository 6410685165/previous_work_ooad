from abc import abstractmethod
import os
import time
import argparse
from pathlib import Path
from random import randint

from arial_car_track.models.experimental import attempt_load
from arial_car_track.utils.datasets import LoadStreams, LoadImages
from arial_car_track.utils.general import check_img_size, check_requirements, \
                check_imshow, non_max_suppression, apply_classifier, \
                scale_coords, xyxy2xywh, strip_optimizer, set_logging, \
                increment_path
from arial_car_track.utils.plots import plot_one_box
from arial_car_track.utils.torch_utils import select_device, load_classifier, \
                time_synchronized, TracedModel
from arial_car_track.utils.download_weights import download
KMP_DUPLICATE_LIB_OK="TRUE"
#For SORT tracking
import skimage
from arial_car_track.sort import *
from arial_car_track.line_intersect import isIntersect
import json
import glob
import arial_car_track.detect_and_track as detect_and_track
import arial_car_track.detect as detect


    
class Vehicle:
    
    def __init__(self):
        self.path = ""
        
    def read_data(self):
        path = self.path
        with open(glob.glob(path + '/*.txt')[0]) as f:
            data = f.readlines()
            data = [i.split(',') for i in data]
            data = np.array(data)
        return data
    
    def car_type(self):
        return self.read_data()[:,2:4],np.unique(self.read_data()[:,2])
            
    def set_path(self,path:str):
        self.path = path
    
    def direction(self):
        # data[np.any(data[:] == 'ENTERED\n',axis=1)]
        data = self.read_data()
        entered = data[np.any(data[:] == 'ENTERED\n',axis=1)]
        left = data[np.any(data[:] == ' LEFT\n',axis=1)]
        right = data[np.any(data[:] == ' RIGHT\n',axis=1)]
        straight = data[np.any(data[:] == ' STRAIGHT\n',axis=1)]
        return entered,left,right,straight
    
    def count(self):
        all_car = len(self.read_data())
        entered,left,right,straight = self.direction() 
        return len(entered),len(left),len(right),len(straight)
    
    def video(self):
        return self.path + "\\" + os.listdir(self.path)[0]
    
    def set_path(self,path):
        self.path = path
        
class Loop():
    def __init__(self):
        self.loop = {"loops":[]}

    
    def add_loop(self,name:str,orientation:str,point:list,summary_location:list):
        self.loop['loops'].append({
            'name': name,
            "orientation": orientation,
            'id':str(len(self.loop['loops'])),
            'point':    [{"x":point[0],"y":point[1]},
                        {"x":point[2],"y":point[3]},
                        {"x":point[4],"y":point[5]},
                        {"x":point[6],"y":point[7]}],
            'sumary_location':{'x':summary_location[0],'y':str(summary_location[1])}
        })
    
    def remove_loop(self,loop_id:int):
        self.loop['loops'].pop(loop_id)
        
    def edit_loop(self,loop_id:int,point:list):
        self.loop['loops'][loop_id]['point'][0] = {"x":point[0],"y":point[1]}
        self.loop['loops'][loop_id]['point'][1] = {"x":point[2],"y":point[3]}
        self.loop['loops'][loop_id]['point'][2] = {"x":point[4],"y":point[5]}
        self.loop['loops'][loop_id]['point'][3] = {"x":point[6],"y":point[7]}

    def get_loop(self):
        return self.loop
    
class Engine:
    
    def __init__(self):
        self.Loop = Loop()
        self.vehicle = Vehicle()

    def add_loop(self,name:str,orientation:str,point:list,summary_location:list):
        self.Loop.add_loop(name,orientation,point,summary_location)
        
    def remove_loop(self,loop_id:int):
        self.Loop.remove_loop(loop_id)
    
    def edit_loop(self,loop_id:int,point:list):
        self.Loop.edit_loop(loop_id,point)
    
    def count(self):
        return self.vehicle.count()
    
    def set_path(self,path):
        self.vehicle.set_path(path)
        
    def direction(self):
        return self.vehicle.direction()
    
    def car_type(self):
        return self.vehicle.car_type()
    
    def video(self):
        return self.vehicle.video()
    
    def get_loop(self):
        return self.Loop.get_loop()
    
class Yolo(Engine):
    
    def __init__(self,yolo_version='yolov7.pt'):
        self.yolo_version = yolo_version
        # self.opt = detect_and_track.parser()
        super().__init__()
        # f = open('loop.json')
        # self.count_boxes = json.load(f)
        # f.close()
        self.loop_boxes = []
        self.time_stamp = 0
        self.save_dir = ""
        self.names = ""
        print("init")
        
    def detect_and_track(self,cmd = False, custom_arg=None):
        opt = detect_and_track.parser()
        self.save_dir = detect_and_track.run(opt.loop,self.loop_boxes,self.time_stamp,self.save_dir,self.names,opt=opt)
        # print(self.save_dir)
        # self.save_dir = detect_and_track.run(self.get_loop(),self.loop_boxes,self.time_stamp,self.save_dir,self.names,opt=opt)
        self.set_path(self.save_dir)
        # self.set_path
        
    def detect(self):
        opt = detect.parser()
        self.save_dir = detect.run_detect(opt)
        self.set_path(self.save_dir)
    
def mymain(cmd=True,custom_arg=None):
    yolo = Yolo()
    yolo.detect_and_track(cmd,custom_arg)


if __name__ == '__main__':
    mymain(cmd=True)