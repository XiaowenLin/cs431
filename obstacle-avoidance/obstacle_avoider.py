# Things we need installed:
#
# 1. OpenCV, along with Python wrapper for OpenCV
# 2. NumPy (because the OpenCV Python wrapper uses it)
# 3. SciPy (for Delaunay triangulation)
#
# On Debian/Ubuntu, run the following (as root) to install the above packages:
#
#   apt-get install python-numpy python-scipy python-opencv

from threading import Thread
import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial.qhull import QhullError
import cv2
from generic_camera import GenericCamera
import time

# Based on a combination of code from
# http://docs.opencv.org/master/d7/d8b/tutorial_py_lucas_kanade.html#gsc.tab=0
# and
# http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
#
# TTC computation based on
# http://teyvoniathomas.com/index.php/projects/55-opticalflow.html

class ObstacleAvoiderThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        
        # Initialize camera
        self.camera = GenericCamera() # Once we're ready to test on the Pi, we just change this initialization to ThePiCamera()

        # params for ShiTomasi corner detection
        self.feature_params = dict( maxCorners = 100,
                                    qualityLevel = 0.3,
                                    minDistance = 7,
                                    blockSize = 7 )
        
        # Parameters for lucas kanade optical flow
        self.lk_params = dict( winSize = (15,15),
                               maxLevel = 2,
                               criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03) )
        
        # Create some random colors
        self.color = np.random.randint(0, 255, (100, 3))
        
        # Create array for line equations
        self.lines = np.zeros((100, 3))
        self.local_scales = np.zeros((100, 1))
        
        # Median filtering for smoother TTC computations
        self.median_filter_state = 0
        self.median_filter_size = 5
        self.scale_array = []
        
        self.old_gray = None
        self.p0 = None
        self.mask = None
    
    @staticmethod
    def find_neighborhoods(delaunay_triangles):
        neighbor_dict = {}
        for triangle_point_indices in delaunay_triangles:
            index_set = set(triangle_point_indices)
            for index in index_set:
                index_set_2 = index_set - set([index])
                if len(index_set_2) != 0:
                    if neighbor_dict.get(index):
                        neighbor_dict[index] = neighbor_dict[index] | index_set_2
                    else:
                        neighbor_dict[index] = index_set_2
        return neighbor_dict

    def run(self):
        print("")
        start = None
        for frame in self.camera.get_iterator():
            the_frame = self.camera.get_frame(frame)
            
            if self.old_gray is None:
                # Take first frame and find corners in it
                self.old_gray = cv2.cvtColor(the_frame, cv2.COLOR_BGR2GRAY)
                self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask = None, **self.feature_params)
                
                # Create a mask image for drawing purposes
                self.mask = np.zeros_like(the_frame)
                
                # Move on to next frame capture
                start = time.time()
                self.median_filter_state = 0
                self.scale_array = []
                continue
                
            frame_gray = cv2.cvtColor(the_frame, cv2.COLOR_BGR2GRAY)
            
            # calculate optical flow
            p1, st, _ = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)
            if p1 is None:
                # We lost all tracking at this point; reinitialize the obstacle avoider
                self.old_gray = None
                cv2.imshow('frame', the_frame)
                k = cv2.waitKey(30) & 0xff
                if k == 27: # Was escape pressed?
                    break
                continue
            
            # Select good points
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]
            
            # Find local scales consisting of computation of feature points and
            # any other feature points in their Delaunay neighborhoods.  I'm
            # hoping this is the right way to compute the local scales.  The
            # numbers looked reasonable when I ran this.
            num_localscales = 0
            if len(good_old) >= 4:
                try:
                    old_triangles = Delaunay(good_old).simplices
                    neighborhoods = ObstacleAvoiderThread.find_neighborhoods(old_triangles)
                    for (k, v) in neighborhoods.items():
                        index_arr = np.array(list(v))
                        
                        # target point
                        new_point = good_new[k]
                        old_point = good_old[k]
                        
                        # neighborhood points
                        new_neighborhood = good_new[index_arr]
                        old_neighborhood = good_old[index_arr]
                        
                        sum2 = np.sum(np.linalg.norm(new_point - new_neighborhood, axis=1))
                        if sum2 != 0:
                            sum1 = np.sum(np.linalg.norm(old_point - old_neighborhood, axis=1))
                            self.local_scales[num_localscales] = (sum1 - sum2) / sum2                            
                            num_localscales += 1
                except (QhullError, ValueError):
                    pass
            
            # draw the tracks
            for i,(new, old) in enumerate(zip(good_new,good_old)):
                # draw the optical flow vector
                a,b = new.ravel()
                c,d = old.ravel()
                
                # original Python code is misusing the cv2.line() and
                # cv2.circle() calls
                cv2.line(self.mask, (a,b),(c,d), self.color[i].tolist(), 2)
                cv2.circle(the_frame, (a,b),5,self.color[i].tolist(),-1)
            
            thresh_scales = self.local_scales[:num_localscales]
            
            if len(thresh_scales) != 0:
                thresh_scales = thresh_scales[thresh_scales > 0.1 * thresh_scales.max()]
                
            if len(thresh_scales) == 0:
                # We lost sufficient information at this point; reinitialize the obstacle avoider
                self.old_gray = None
            else:
                # Find maximum of all thresholded local scales
                median_scale = np.max(thresh_scales)
                self.scale_array.append(median_scale)
                self.median_filter_state += 1
                
                if self.median_filter_state == self.median_filter_size:
                    self.median_filter_state = 0
                    
                    # Find median of the maximum local scale
                    median_scale = np.median(self.scale_array)
                    self.scale_array = []
                
                    # Find change in time, keeping in mind that we must
                    # compensate for median filtering.
                    end = time.time()
                    delta = (end - start) / self.median_filter_size
                    start = end
                    
                    if median_scale == 0:
                        print("\033[A\033[KMinimum TTC = infinity")
                    else:
                        median_ttc = 1.0 / median_scale
                        print("\033[A\033[KMinimum TTC = %g sec"%(median_ttc * delta))
            
            img = cv2.add(the_frame, self.mask)
            cv2.imshow('frame', img)
            
            k = cv2.waitKey(30) & 0xff
            if k == 27: # Was escape pressed?
                break
            
            # Now update the previous frame and previous points
            if self.old_gray is not None:
                self.old_gray = frame_gray.copy()
                self.p0 = good_new.reshape(-1,1,2)
        
        cv2.destroyAllWindows()
        self.camera.destroy()

class ObstacleAvoider:
    def __init__(self):
        self.thread = ObstacleAvoiderThread()
        self.thread.start()
        
    def join(self):
        self.thread.join()
    
