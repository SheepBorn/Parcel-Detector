from collections import deque
import statistics
import Telegram
import asyncio
import cv2
import Settings

class Detection_Handler:
    def __init__(self, size=Settings.settings["buffer"]):
        # initialise container for number of parcels
        self.queue = deque(maxlen=size)
        # initialise amount of parcels on screen
        self.curr = -1
        # initialise frame buffer for gifs
        self.images = deque(maxlen=size)
    
    def update(self, new_value, image):
        self.queue.append(new_value)
        self.images.append(image)
        #find most frequent value
        try:
            val = statistics.mode(self.queue)

        #if no mode take median   
        except statistics.StatisticsError:
            val = statistics.median(self.queue)

        if (len(self.queue)==self.queue.maxlen):
            if(self.curr == -1):
                #init
                self.curr = val
            elif(self.curr > val):
                #parcel removed
                self.curr = val
                #check settings for gif or picture
                if(Settings.settings["Gif_notification"]):
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter('gif.mp4', fourcc, 10.0, (Settings.settings["cam_width"], Settings.settings["cam_height"]))
                    for frames in self.images:
                        out.write(frames)
                    out.release()
                    filename = "gif.mp4"
                    asyncio.create_task(Telegram.GIF_notification(filename,"Parcel has been removed!"))
                else:
                    filename = "tmpimage.jpg"
                    cv2.imwrite(filename,image)
                    asyncio.create_task(Telegram.image_notification(filename,"Parcel has been removed!"))

            elif(self.curr < val):
                #parcel added
                self.curr = val
                #check settings for gif or picture
                if(Settings.settings["Gif_notification"]):
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter('gif.mp4', fourcc, 10.0, (Settings.settings["cam_width"], Settings.settings["cam_height"]))
                    for frames in self.images:
                        out.write(frames)
                    out.release()
                    filename = "gif.mp4"
                    asyncio.create_task(Telegram.GIF_notification(filename,"New Parcel Alert!"))
                else:
                    filename = "tmpimage.jpg"
                    cv2.imwrite(filename,image)
                    asyncio.create_task(Telegram.image_notification(filename,"New Parcel Alert!"))
        # picture request from user
        if (Telegram.request):
            filename = "tmpimage.jpg"
            cv2.imwrite(filename,image)
            asyncio.create_task(Telegram.image_notification(filename,"Image Request"))
            Telegram.request = False

        

