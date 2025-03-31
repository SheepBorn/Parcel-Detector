import cv2

from ultralytics import YOLO
import supervision as sv

from Handler import Detection_Handler
import Telegram

import asyncio

from datetime import datetime
import time
import Settings

async def main():
    await asyncio.gather(
        Telegram.run_bot(),
        detection()
    )

def click_event(event, x, y, flags, params): 
  
    # checking for left mouse clicks 
    if event == cv2.EVENT_LBUTTONDOWN: 
  
        # displaying the coordinates in terminal
        print(x, ' ', y) 

async def detection():
    # initialise
    video = cv2.VideoCapture(0,cv2.CAP_DSHOW)

    # initialise settings for height and width from settings
    frame_height = Settings.settings["cam_height"]
    frame_width = Settings.settings["cam_width"]

    # set camera height and width
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)

    # set dt for video file name
    dt = datetime.now().strftime("%y-%m-%d %H-%M-%S")

    # initialise time for recording intervals
    start = time.time()
    record_interval = Settings.settings["record_interval"]

    # initialise settings for detection zone from settings
    y1 = Settings.settings["zone_y1"]
    y2 = Settings.settings["zone_y2"]
    x1 = Settings.settings["zone_x1"]
    x2 = Settings.settings["zone_x2"]

    # initialising VideoWriter from cv2 to record camera
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(dt +'.mp4', fourcc, 10.0, (frame_width, frame_height))

    # choose yolo model from trained models
    model = YOLO("runs/detect/train9/weights/best.pt")
    
    #model.export(format="openvino")

    #training model
    #ov_model = YOLO("yolov8s")
    #ov_model.train(data="package-at-front-door-2/data.yaml", epochs=20,imgsz=416)

    #initialise box and labels for detection
    box_annotator = sv.BoxAnnotator(
        thickness=2
    )
    label_annotator = sv.LabelAnnotator(
        text_thickness=2,
    )

    # initialise detection handler
    handler = Detection_Handler()
    
    # camera loop
    while True:
        ret, image = video.read()

        # time overlay for recordings
        time_overlay = datetime.now().strftime("%d-%m-%y %H:%M:%S")
        recording = cv2.putText(image.copy(),time_overlay,(10,30),cv2.FONT_ITALIC,1,(0,165,255),2,cv2.LINE_AA)

        # create new recording based on record interval set
        if time.time() - start > record_interval:
            start = time.time()
            dt = datetime.now().strftime("%y-%m-%d %H-%M-%S")
            out = cv2.VideoWriter(dt +'.mp4', fourcc, 10.0, (frame_width, frame_height))

        # write to recording file
        out.write(recording)

        if not ret:
            continue
        
        # flipping image not necessary but for me to not be confused when showing objects on camera
        flipped_image = cv2.flip(image, 1)

        # setting zone for image detection
        zone_image = flipped_image[y1:y2, x1:frame_width]

        # getting results with confidence above a certain value to reduce false positives, verbose false so that the terminal is not flooded
        result = model(zone_image,conf=0.5,verbose=False)[0]
        detections = sv.Detections.from_ultralytics(result)
        labels = [
            f"{class_name} {confidence:.2f}"
            for class_name, confidence
            in zip(detections['class_name'], detections.confidence)
        ]

        # send number of detections and recording image to handler
        handler.update(len(detections), recording)

        # annotate the image with box around object detected
        box_image = box_annotator.annotate(
            scene=zone_image,
            detections=detections,
            )
        
        # annotate the image with label on object detected
        label_image = label_annotator.annotate(
            scene=box_image,
            detections=detections,
            labels=labels
            )

        await asyncio.sleep(0)
        # show processed image
        cv2.imshow('Parcel', label_image)
        # allow user to get coordinates to set detection zone more easily
        cv2.setMouseCallback('Parcel', click_event) 

        # Press 'q' to 'quit'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    out.release()
    cv2.destroyAllWindows()
    #await Telegram.app.stop_running()


if __name__ == "__main__":
    asyncio.run(main())
