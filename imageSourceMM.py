import numpy as np
import MMCorePy
from PIL import Image
import time
from Rectangle import Rectangle

class imageSource():
    
    def __init__(self,configFile,channelGroupName='Channels'):
      #NEED TO IMPLEMENT IF NOT MICROMANAGER
     
        self.configFile=configFile
        self.mmc = MMCorePy.CMMCore() 
        self.mmc.loadSystemConfiguration(self.configFile)

        self.channelGroupName=channelGroupName
       
        #set the exposure to use
    
    def get_max_pixel_value(self):
        bit_depth=self.mmc.getImageBitDepth()
        return np.power(2,bit_depth)
        
    def set_exposure(self,exp_msec):
      #NEED TO IMPLEMENT IF NOT MICROMANAGER
        self.mmc.setExposure(exp_msec)
    
    def reset_focus_offset(self):
        if self.has_hardware_autofocus():
            focusDevice=self.mmc.getAutoFocusDevice()
            self.mmc.setProperty(focusDevice,"CRISP State","Reset Focus Offset")
  
    def get_hardware_autofocus_state(self):
        if self.has_hardware_autofocus():
            return self.mmc.isContinuousFocusLocked()
           
    def set_hardware_autofocus_state(self,state):
        if self.has_hardware_autofocus():
            self.mmc.enableContinuousFocus(state)
        
    def has_hardware_autofocus(self):
       #NEED TO IMPLEMENT IF NOT MICROMANAGER
        #print "need to implement automatic detection of hardware autofocus"
        return True
        
        
    def is_hardware_autofocus_done(self):
      #NEED TO IMPLEMENT IF NOT MICROMANAGER
        #hardware autofocus assumes the focus score is <1 when focused
        score=self.mmc.getCurrentFocusScore()
        if abs(score)<1:
            print "locked on"
            return True
        else:
            print "score %f not locked on"%score
            print '***********************bypassing is_hardware_autofocus_done, imageSource.py line 57***************'
            return True
            #return False
        
        

    
    def take_image(self,x,y):
        #do not need to re-implement
        #moves scope to x,y - focus scope - snap picture
        #using the configured exposure time
    
        #move stage to x,y
        self.move_stage(x,y)
        
        if not self.has_hardware_autofocus():
            self.image_based_autofocus()
        else:
            #make sure hardware autofocus worked
            attempts=0
            failure=False
            while not self.is_hardware_autofocus_done():
                time.sleep(.1)
                attempts+=1
                if attempts>100:
                    failure=True
                    break
                    print "not autofocusing correctly.. giving up after 10 seconds"
            if failure:
                return None

        #get the image data       
        data=self.snap_image()
      
        #fix the image orientation if need be
        (low_X_left,low_Y_up)=self.get_image_orientation()
        if low_X_left == False:
            data=np.fliplr(data)
        if low_Y_up == False:
            data=np.flipud(data)
            
        
        #check whether it is in focus 
        #if not self.meets_focus_spec(data):
        #if not, attempt image based autofocus
        #self.image_based_autofocus()
        #data=self.snap_image()
            
        #check whether it is in focus
        #if not self.meets_focus_spec(data):
        #if not take a small stack around current point
        #and return most in focus image of that
        #data=self.take_best_of_stack()
        
        #calculate bounding box for data
        bbox=self.calc_bbox(x,y)
        
        #print "todo get some real metadata"
        metadata=None
        return data,bbox

    def get_xy(self):
        #NEED TO IMPLEMENT IF NOT MICROMANAGER
        xystg=self.mmc.getXYStageDevice()
        
        x=self.mmc.getXPosition(xystg)
        y=self.mmc.getYPosition(xystg)
        
        return (-x,y)
    def get_z(self):
        focus_stage=self.mmc.getFocusDevice()
        return self.mmc.getPosition(focus_stage)
    def set_z(self,z):
        focus_stage=self.mmc.getFocusDevice()
        self.mmc.setPosition (focus_stage,z)
        self.mmc.waitForDevice(focus_stage)
        
    def get_pixel_size(self):
        #NEED TO IMPLEMENT IF NOT MICROMANAGER
        return self.mmc.getPixelSizeUm()
    
    def get_frame_size_um(self):
        (sensor_width,sensor_height)=self.get_sensor_size()
        print 'sensor_width from mmc = ', sensor_width
        print 'sensor_height from mmc = ', sensor_height
        pixsize = self.get_pixel_size()
        print 'pixsize = ', pixsize
        return (sensor_width*pixsize,sensor_height*pixsize)
        
        
    def calc_bbox(self,x,y):
        #do not need to implement
        (fw,fh)=self.get_frame_size_um()
        
        #we are going to follow the convention of upper left being 0,0 
        #and lower right being X,X where X is positive
        left = x - fw/2.0;
        right = x + fw/2.0;
        
        top = y - fh/2.0;
        bottom = y + fh/2.0;
        
       
        return Rectangle(left,right,top,bottom)
        
    
    def snap_image(self):
        #NEED TO IMPLEMENT IF NOT MICROMANAGER
        #with microscope in current configuration
        #snap a picture, and return the data as a numpy 2d array
        self.mmc.snapImage()
        return self.mmc.getImage()
    
    
    def get_sensor_size(self):
        #NEED TO IMPLEMENT IF NOT MICROMANAGER
        #get the sensor size in pixels
        height = self.mmc.getImageHeight()
        width = self.mmc.getImageWidth()
    
        #return the height and width in pixels
        return (height,width)
        
    def move_stage(self,x,y):
        #need to implement if not MICROMANAGER
        #move the stage to position x,y
        stg=self.mmc.getXYStageDevice()
        self.mmc.setXYPosition(stg,-x,y)
        self.mmc.waitForDevice(stg)
        print self.get_xy()
        
        
    def set_channel(self,channel):
        if channel not in self.get_channels():
            print "no such channel:" + channel
            return False
        
        self.mmc.setConfig(self.channelGroupName,channel)
        self.mmc.waitForConfig(self.channelGroupName,channel)
        self.mmc.setShutterOpen(False)
        
    def get_channels(self):
        return self.mmc.getAvailableConfigs(self.channelGroupName)
        
    def take_best_of_stack(self):
        print "need to implement take best of stack"
        return self.snap_image()  
    def meets_focus_spec(data):
        print "need to implement focus spec check"
        return True
    def get_image_orientation(self):
        #when take_image returns an image
        #which way is up?
        
        cam=self.mmc.getCameraDevice()
        low_X_left = int(self.mmc.getProperty(cam,"TransposeMirrorX"))==0
        low_Y_up = int(self.mmc.getProperty(cam,"TransposeMirrorY"))==0
        
        return (low_X_left,low_Y_up) 