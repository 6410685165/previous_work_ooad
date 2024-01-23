import os
import cv2
import time
import torch
import argparse
from pathlib import Path
from numpy import random
from random import randint
import torch.backends.cudnn as cudnn

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, \
                check_imshow, non_max_suppression, apply_classifier, \
                scale_coords, xyxy2xywh, strip_optimizer, set_logging, \
                increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, \
                time_synchronized, TracedModel
from utils.download_weights import download
KMP_DUPLICATE_LIB_OK="TRUE"
#For SORT tracking
import skimage
from sort import *
from line_intersect import isIntersect
import json
import count_table
# from engine import Yolo

#3 point consecutive vect
def check_clock_wise(p1,p2,p3):
    vec1  = (p2[0]-p1[0],p2[1]-p1[1])
    vec2 = (p3[0]-p2[0],p3[1]-p2[1])
    cross = vec2[0] * vec1[1] - vec2[1] * vec1[0]
    if cross>=0:
        return True
    else:
        return False

#count group by type and direction



# straight left right
#car
#pickup
#motorcycle
#cnts = []

#............................... Tracker Functions ............................
""" Random created palette"""
palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

"""" Calculates the relative bounding box from absolute pixel values. """
# class loop():



class detect():
    
    def __init__(self,count_boxes,loop_boxes,time_stamp,save_dir,names):
        self.count_boxes = count_boxes
        self.loop_boxes = loop_boxes
        self.time_stamp = time_stamp
        self.save_dir = save_dir
        self.names = names
        
    def detect(self,opt,save_img=False):

        source, weights, view_img, save_txt, imgsz, trace, colored_trk= opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, not opt.no_trace, opt.colored_trk
        save_img = not opt.nosave and not source.endswith('.txt')  # save inference images
        webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
            ('rtsp://', 'rtmp://', 'http://', 'https://'))


        #.... Initialize SORT .... 
        #......................... 
        sort_max_age = 25 #5 
        sort_min_hits = 5 #2
        sort_iou_thresh = 0.5 #0.2
        sort_tracker = Sort(max_age=sort_max_age,
                        min_hits=sort_min_hits,
                        iou_threshold=sort_iou_thresh) 
        #......................... 
        # Directories
        self.save_dir = Path(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))  # increment run
        (self.save_dir / 'labels' if save_txt else self.save_dir).mkdir(parents=True, exist_ok=True)  # make dir

        # Initialize
        set_logging()
        device = select_device(opt.device)
        half = device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        model = attempt_load(weights, map_location=device)  # load FP32 model
        stride = int(model.stride.max())  # model stride
        imgsz = check_img_size(imgsz, s=stride)  # check img_size

        if trace:
            model = TracedModel(model, device, opt.img_size)

        if half:
            model.half()  # to FP16

        # Second-stage classifier
        classify = False
        if classify:
            modelc = load_classifier(name='resnet101', n=2)  # initialize
            modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

        # Set Dataloader
        vid_path, vid_writer = None, None
        if webcam:
            view_img = check_imshow()
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz, stride=stride)
        else:
            dataset = LoadImages(source, img_size=imgsz, stride=stride)

        # Get names and colors
        self.names = model.module.names if hasattr(model, 'module') else model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        for loop in self.count_boxes["loops"]:
            self.loop_boxes.append(count_table.LoopCount(len(self.names),loop["summary_location"],loop))
    #    for i in range(len(names)):
    #        cnts.append([0,0,0].copy()) #prepare array the same size as class type
    #    print(cnts)

        # Run inference
        if device.type != 'cpu':
            model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
        old_img_w = old_img_h = imgsz
        old_img_b = 1

        t0 = time.time()

        #........Rand Color for every trk.......
        rand_color_list = []
        for i in range(0,5005):
            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            rand_color = (r, g, b)
            rand_color_list.append(rand_color)
        #.........................
        img = None
        counttable = count_table.CountTable(img,None,
                    list(self.names),["Straight","Left","Right"],border_color=(0,255,0),text_color=(0,0,255))
        frame_count = 0
        for path, img, im0s, vid_cap in dataset:
            fps = vid_cap.get(cv2.CAP_PROP_FPS)
            time_stamp = frame_count/fps #calculate time stamp
            frame_count+=1
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Warmup
            if device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
                old_img_b = img.shape[0]
                old_img_h = img.shape[2]
                old_img_w = img.shape[3]
                for i in range(3):
                    model(img, augment=opt.augment)[0]

            # Inference
            t1 = time_synchronized()
            pred = model(img, augment=opt.augment)[0]
            t2 = time_synchronized()

            # Apply NMS
            pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
            t3 = time_synchronized()

            # Apply Classifier
            if classify:
                pred = apply_classifier(pred, modelc, img, im0s)

            # print()
            # print('*************')
            # print(self.names)
            # print('*************')
            # for i,det in enumerate(pred):
            #     print(det)
            #     if(i==1):
            #         break
            # Process detections
            for i, det in enumerate(pred):  # detections per image
                if webcam:  # batch_size >= 1
                    p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
                else:
                    p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

                p = Path(p)  # to Path
                save_path = str(self.save_dir / p.name)  # img.jpg
                txt_path = str(self.save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    #..................USE TRACK FUNCTION....................
                    #pass an empty array to sort
                    dets_to_sort = np.empty((0,6))
                    
                    # NOTE: We send in detected object class too
                    for x1,y1,x2,y2,conf,detclass in det.cpu().detach().numpy():
                        dets_to_sort = np.vstack((dets_to_sort, 
                                    np.array([x1, y1, x2, y2, conf, detclass])))
                    
                    # Run SORT
                    tracked_dets = sort_tracker.update(dets_to_sort)
                    tracks =sort_tracker.getTrackers()

                    #loop over tracks
                    for track in tracks:

                        #tracking object passing line check and update
                        self.check_enter_exit_loop(track)

                        # color = compute_color_for_labels(id)
                        #draw colored tracks
                        if colored_trk:
                            [cv2.line(im0, (int(track.centroidarr[i][0]),
                                        int(track.centroidarr[i][1])), 
                                        (int(track.centroidarr[i+1][0]),
                                        int(track.centroidarr[i+1][1])),
                                        rand_color_list[track.id], thickness=1) 
                                        for i,_ in  enumerate(track.centroidarr) 
                                        if i < len(track.centroidarr)-1 ] 
                        #draw same color tracks
                        else:
                            [cv2.line(im0, (int(track.centroidarr[i][0]),
                                        int(track.centroidarr[i][1])), 
                                        (int(track.centroidarr[i+1][0]),
                                        int(track.centroidarr[i+1][1])),
                                        (255,0,0), thickness=1) 
                                        for i,_ in  enumerate(track.centroidarr) 
                                        if i < len(track.centroidarr)-1 ] 
                    
                    # draw boxes for visualization
                    if len(tracked_dets)>0:
                        bbox_xyxy = tracked_dets[:,:4]
                        identities = tracked_dets[:, 8]
                        categories = tracked_dets[:, 4]
                        self.draw_boxes(im0, bbox_xyxy, identities, categories, self.names)

                    #........................................................
                    
        #     # Print time (inference + NMS)
            print(f'{s}Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')

            counttable.img = im0s
            
            # for lb in self.loop_boxes:
            #     lb.draw(counttable)
                

            self.draw_loops(im0s)
                # Stream results
            if view_img:
                cv2.imshow(str(p), im0)
                if cv2.waitKey(1) == ord('q'):  # q to quit
                    cv2.destroyAllWindows()
                    raise StopIteration

                # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(self.save_dir, im0)
                    print(f" The image with the result is saved in: {save_path}")
                else:  # 'video' or 'stream'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                            save_path += '.mp4'
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer.write(im0)

        if save_txt or save_img:
            s = f"\n{len(list(self.save_dir.glob('labels/*.txt')))} labels saved to {self.save_dir / 'labels'}" if save_txt else ''
            # print(f"Results saved to {self.save_dir}{s}")
            print(f"Results saved to {self.save_dir}{s}")
        # print('this is path of save_dir' + pathsave)
        print()
        print(f'Done. ({time.time() - t0:.3f}s)')
        return str(self.save_dir)

    def bbox_rel(self,*xyxy):
        bbox_left = min([xyxy[0].item(), xyxy[2].item()])
        bbox_top = min([xyxy[1].item(), xyxy[3].item()])
        bbox_w = abs(xyxy[0].item() - xyxy[2].item())
        bbox_h = abs(xyxy[1].item() - xyxy[3].item())
        x_c = (bbox_left + bbox_w / 2)
        y_c = (bbox_top + bbox_h / 2)
        w = bbox_w
        h = bbox_h
        return x_c, y_c, w, h


    """Function to Draw Bounding boxes"""
    def draw_boxes(self,img, bbox, identities=None, categories=None, names=None,offset=(0, 0)):
        for i, box in enumerate(bbox):
            x1, y1, x2, y2 = [int(i) for i in box]
            x1 += offset[0]
            x2 += offset[0]
            y1 += offset[1]
            y2 += offset[1]
            cat = int(categories[i]) if categories is not None else 0
            id = int(identities[i]) if identities is not None else 0
            data = (int((box[0]+box[2])/2),(int((box[1]+box[3])/2)))
            label = str(id) + ":"+ str(cat) + ":"+ names[cat]
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,20), 1)
            cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (255,144,30), -1)
            cv2.putText(img, label, (x1, y1 - 5),cv2.FONT_HERSHEY_SIMPLEX, 
                        0.4, [255, 255, 255], 1)
            # cv2.circle(img, data, 6, color,-1)
        return img
    #..............................................................................
    def append_to_file(self,filename, text):
        with open(filename, "a") as file:
            file.write(text + "\n")
            
    def check_enter_exit_loop(self,track):
        loops = self.count_boxes["loops"]
        for loop in loops:
            #print(loop)
            pt0,pt1,pt2,pt3 = loop["points"]
            #check entering line
            if len(track.centroidarr)>20:
                tp2,tp1 = track.centroidarr[-1], track.centroidarr[-20]            
                #check entering line
                self.line_enter_check_and_set(loop,track,tp1,tp2,pt0,pt1)
                
                #check exit line left straight and right
                self.line_exit_check_and_set(loop,track,tp1,tp2,pt1,pt2,"left")
                self.line_exit_check_and_set(loop,track,tp1,tp2,pt2,pt3,"straight")
                self.line_exit_check_and_set(loop,track,tp1,tp2,pt3,pt0,"right")

    def line_enter_check_and_set(self,loop,track,tp1,tp2,line_start,line_end):
        if isIntersect(tp1,tp2,line_start,line_end):
            # print(track.aoi_entered)
            if loop["id"] not in track.aoi_entered :
                track.aoi_entered.append(loop["id"])
                msg = f'{loop["id"]},{track.id},{self.names[int(track.detclass)]},{self.time_stamp},ENTERED'
                self.append_to_file(str(self.save_dir)+"\\loop.txt",msg)
                print(f'track {track.id} of type {track.detclass} entered loop {loop["id"]} at time ...{self.time_stamp}')

    #check if the object exit the line, if the first time mark it and prevent the re entry by setting the flag 
    def line_exit_check_and_set(self,loop,track,tp1,tp2,line_start,line_end,line_side): #line_side is the left or right border
        if isIntersect(tp1,tp2,line_start,line_end):
            if loop["id"] in track.aoi_entered and loop["id"] not in track.aoi_exited:
                track.aoi_exited.append(loop["id"])  # means already exit
                print(f'track {track.id} of type {track.detclass} exit loop {loop["id"]} at time ...{self.time_stamp}')
                if (loop["orientation"] == "clockwise" and line_side=="left" or 
                    loop["orientation"] == "counterclockwise" and line_side=="right"): #turn left
                    self.loop_boxes[int(loop["id"])].add_left(int(track.detclass))
                    msg = f'{loop["id"]},{track.id},{self.names[int(track.detclass)]},{self.time_stamp}, LEFT'
                    self.append_to_file(str(self.save_dir)+"\\loop.txt",msg)
                    
                if(loop["orientation"] == "clockwise" and line_side=="right" or 
                    loop["orientation"] == "counterclockwise" and line_side=="left"): #turn right
                    self.loop_boxes[int(loop["id"])].add_right(int(track.detclass)) # turn right
                    msg = f'{loop["id"]},{track.id},{self.names[int(track.detclass)]},{self.time_stamp}, RIGHT'
                    self.append_to_file(str(self.save_dir)+"\\loop.txt",msg)

                if line_side == "straight":
                    self.loop_boxes[int(loop["id"])].add_straight(int(track.detclass))
                    msg = f'{loop["id"]},{track.id},{self.names[int(track.detclass)]},{self.time_stamp}, STRAIGHT'
                    self.append_to_file(str(self.save_dir)+"\\loop.txt",msg)


    #check if item entering or exit loop


    #draw bouncing box to loop
    def draw_loops(self,img):
        loops = self.count_boxes["loops"]
        for loop in loops:
            pt0,pt1,pt2,pt3 = loop["points"]
            
            cv2.line(img, (pt0["x"],pt0["y"]),(pt1["x"],pt1["y"]),(255,0,0),2) #entering line
            cv2.line(img, (pt1["x"],pt1["y"]),(pt2["x"],pt2["y"]),(255,255,0),2) #left line
            cv2.line(img, (pt2["x"],pt2["y"]),(pt3["x"],pt3["y"]),(255,255,0),2) #straight
            cv2.line(img, (pt3["x"],pt3["y"]),(pt0["x"],pt0["y"]),(255,255,0),2) #right
            cv2.putText(img,loop["name"],(pt0["x"],pt0["y"]),cv2.FONT_HERSHEY_SIMPLEX, 0.6, [0, 255, 0], 2)
            
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov7.pt', help='model.pt path(s)')
    parser.add_argument('--download', action='store_true', help='download model weights automatically')
    parser.add_argument('--no-download', dest='download', action='store_false')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.6, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default='runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='object_tracking', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--no-trace', action='store_true', help='don`t trace model')
    parser.add_argument('--colored-trk', action='store_true', help='assign different color to every track')
    parser.add_argument('--loop', default="loop.json", type=str, help='loop setting file')
    parser.add_argument('--loop-txt', action='store_true', help='save history for each loop')
    parser.add_argument('--summary-txt', action='store_true', help='save summary for each loop')
    parser.set_defaults(download=True)
    
    return parser.parse_args()
# if __name__ == '__main__':
#  #todo later

#     opt = parser()
#     print(opt)
#     #load loops settings
#     f = open(opt.loop)
#     count_boxes = json.load(f)
#     f.close()

#     #check_requirements(exclude=('pycocotools', 'thop'))
#     if opt.download and not os.path.exists(str(opt.weights)):
#         print('Model weights not found. Attempting to download now...')
#         download('./')

#     with torch.no_grad():
#         if opt.update:  # update all models (to fix SourceChangeWarning)
#             for opt.weights in ['yolov7.pt']:
#                 detect().detect()
#                 strip_optimizer(opt.weights)
#         else:
#             detect().detect()


# f = open(opt.loop)
# count_boxes = json.load(f)
# f.close()
# # count_boxes = []
# loop_boxes = [] #loop statistics
# time_stamp = 0 # time in second
# save_dir = ""
# names = ""


def run(count_boxes,loop_boxes,time_stamp,save_dir,names,opt=None,version='yolov7.pt'):

    print(opt)
    #load loops settings

    print(count_boxes)
    #check_requirements(exclude=('pycocotools', 'thop'))
    if opt.download and not os.path.exists(str(opt.weights)):
        print('Model weights not found. Attempting to download now...')
        download('./')

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in [version]: # 'yolov7.pt'
                result = detect(count_boxes,loop_boxes,time_stamp,save_dir,names).detect(opt=opt)
                strip_optimizer(opt.weights)
        else:
            result = detect(count_boxes,loop_boxes,time_stamp,save_dir,names).detect(opt=opt)
    return str(result)
# if __name__ == '__main__':
#     run(version='yolov7.pt')       
