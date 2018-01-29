#!/usr/bin/env python

from pypyueye import Camera, FrameThread, SaveThread, RecordThread, \
    PyuEyeQtApp, PyuEyeQtView, UselessThread
from PyQt4 import QtGui
from pyueye import ueye
import cv2
import numpy as np


class CircleDetector(object):
    def __init__(self, nmb_circ, min_dist=100):
        """

        """
        self.nmb_circ = nmb_circ
        try:
            nmb_circ[0]
        except TypeError:
            self.nmb_circ = [nmb_circ, nmb_circ]
        self.dp = 1.5
        self.min_dist = min_dist
        self.xy_center = []

    def process(self, image_data):
        """
        Detect circles and draw them on the image
        """
        # Find circles on the given image
        image = image_data.as_1d_image()
        image_bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(image_bw, cv2.HOUGH_GRADIENT, self.dp,
                                   self.min_dist)
        # Adapt circle detector parameter to reach the right number of circles
        if circles is None:
            self.dp *= 1.1
        elif len(circles[0]) < self.nmb_circ[1] \
             and len(circles[0]) > self.nmb_circ[0]:
            pass
        elif len(circles[0]) < self.nmb_circ[0]:
            self.dp /= len(circles[0])/self.nmb_circ[0]
        elif len(circles[0]) > self.nmb_circ[1]:
            self.dp /= len(circles[0])/self.nmb_circ[1]
        else:
            self.dp /= len(circles[0])/np.mean(self.nmb_circ)
        # Add circles on the image
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(image, (x, y), r, (0, 200, 0), 4)
                cv2.circle(image, (x, y), 0, (200, 0, 0), 10)
            if len(circles) == 1:
                self.xy_center.append([circles[0][0],
                                       circles[0][1]])
        # Add the main circle trajectory on the image
        if len(self.xy_center) > 2:
            ind0 = len(self.xy_center) - 20
            if ind0 < 0:
                ind0 = 0
            for i in np.arange(ind0, len(self.xy_center) - 1):
                cv2.line(image,
                         tuple(self.xy_center[i]),
                         tuple(self.xy_center[i + 1]),
                         (200, 0, 0), 4)
        # Return the image to Qt for display
        return QtGui.QImage(image.data,
                            image_data.mem_info.width,
                            image_data.mem_info.height,
                            QtGui.QImage.Format_RGB888)


if __name__ == "__main__":
    with Camera(device_id=0, buffer_count=10) as cam:
        #======================================================================
        # Camera settings
        #======================================================================
        # TODO: Add more config properties (fps, gain, ...)
        cam.set_colormode(ueye.IS_CM_BGR8_PACKED)  # TODO: Make this Grayscale
        cam.set_aoi(0, 0, 1280, 1024)
        cam.set_fps(24)

        # #======================================================================
        # # Live video
        # #======================================================================
        # # we need a QApplication, that runs our QT Gui Framework
        # app = PyuEyeQtApp()
        # # a basic qt window
        # view = PyuEyeQtView()
        # view.show()
        # # a thread that waits for new images and processes all connected views
        # thread = FrameThread(cam, view)
        # thread.start()
        # app.exit_connect(thread.stop)
        # # Run and wait for the app to quit
        # app.exec_()

        #======================================================================
        # Live video with circle detection
        #======================================================================
        # we need a QApplication, that runs our QT Gui Framework
        app = PyuEyeQtApp()
        # a basic qt window
        view = PyuEyeQtView()
        # Create a circle detector and associate it to the view
        cd = CircleDetector(nmb_circ=1)
        view.user_callback = cd.process
        # Show the view
        view.show()
        # a thread that waits for new images and processes all connected views
        thread = FrameThread(cam, view)
        thread.start()
        app.exit_connect(thread.stop)
        # Run and wait for the app to quit
        app.exec_()

        # #======================================================================
        # # Save an image
        # #======================================================================
        # # Create a thread to save just one image
        # thread = SaveThread(cam, path="/home/muahah/tmp/ueye_image.png")
        # thread.start()
        # # Wait for the thread to end
        # thread.join()

        # #======================================================================
        # # Save a video
        # #======================================================================
        # # Create a thread to save a video
        # thread = RecordThread(cam, path="/home/muahah/tmp/ueye_image.avi",
        #                       nmb_frame=10)
        # thread.start()
        # # Wait for the thread to edn
        # thread.join()

        # #======================================================================
        # # Debugging
        # #======================================================================
        # import time
        # # a thread that do nearly nothing
        # thread = UselessThread(cam)
        # thread.start()
        # time.sleep(10)
        # thread.stop()
        # # Run and wait for the app to quit
