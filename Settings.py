#===============================================================================
# 
#  License: GPL
# 
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License 2
#  as published by the Free Software Foundation.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
#===============================================================================
import wx

class SiftSettings():

    def __init__(self,contrastThreshold=.05,numFeatures=1000):
    
        self.contrastThreshold=contrastThreshold
        self.numFeatures=numFeatures
        
    def save_settings(self,cfg):
        cfg.WriteInt('numFeatures',self.numFeatures)
        cfg.WriteFloat('contrastThreshold',self.contrastThreshold)
    
    def load_settings(self,cfg):
        self.numFeatures=cfg.ReadInt('numFeatures',1000)
        self.contrastThreshold=cfg.ReadFloat('contrastThreshold',0.5)
        
class ChangeSiftSettings(wx.Dialog):
    def __init__(self, parent, id, title, settings,style):
        wx.Dialog.__init__(self, parent, id, title,style=wx.DEFAULT_DIALOG_STYLE, size=(420, -1))   
        vbox =wx.BoxSizer(wx.VERTICAL)
        
        self.settings=settings
        self.numFeatureTxt=wx.StaticText(self,label="max features")
        self.numFeatureIntCtrl = wx.lib.intctrl.IntCtrl( self, value=settings.numFeatures,size=(50,-1))
        
        self.contrastThresholdTxt = wx.StaticText(self,label="contrast threshold")
        self.contrastThresholdFloatCtrl = wx.lib.agw.floatspin.FloatSpin(self, 
                                       value=settings.contrastThreshold,
                                       min_val=0,
                                       max_val=12.0,
                                       increment=.01,
                                       digits=2,
                                       name='',
                                       size=(95,-1)) 
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        hbox1.Add(self.numFeatureTxt)
        hbox1.Add(self.numFeatureIntCtrl)
        
        hbox2.Add(self.contrastThresholdTxt)
        hbox2.Add(self.contrastThresholdFloatCtrl)
        
       

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)      
        ok_button = wx.Button(self,wx.ID_OK,'OK')
        cancel_button = wx.Button(self,wx.ID_CANCEL,'Cancel')
        hbox3.Add(ok_button)
        hbox3.Add(cancel_button)
        
        vbox.Add(hbox1)
        vbox.Add(hbox2)
        vbox.Add(hbox3)

        self.SetSizer(vbox)
        
    def GetSettings(self):
        numFeatures = self.numFeatureIntCtrl.GetValue()
        contrastThreshold = self.contrastThresholdFloatCtrl.GetValue()
        
        return SiftSettings(contrastThreshold,numFeatures)
        
        
class CameraSettings():
    """simple struct for containing the parameters for the camera"""
    def __init__(self,sensor_height=2048,sensor_width=2048,pix_width=6.5,pix_height=6.5):
        #in pixels        
        self.sensor_height=sensor_height
        self.sensor_width=sensor_width
        #in microns
        self.pix_width=pix_width
        self.pix_height=pix_height
    def save_settings(self,cfg):
        cfg.WriteInt('sensor_height',self.sensor_height)
        cfg.WriteInt('sensor_width',self.sensor_width)
        cfg.WriteFloat('pix_width',self.pix_width)
        cfg.WriteFloat('pix_height',self.pix_height)
    def load_settings(self,cfg):
        self.sensor_height=cfg.ReadInt('sensor_height',2048)
        self.sensor_width=cfg.ReadInt('sensor_width',2048)
        self.pix_width=cfg.ReadFloat('pix_width',6.5)
        self.pix_height=cfg.ReadFloat('pix_height',6.5)

class ChannelSettings():
    """simple struct for containing the parameters for the microscope"""
    def __init__(self,channels,exposure_times=dict([]),zoffsets=dict([]),usechannels=dict([]),prot_names=dict([]),map_chan=None,def_exposure=100,def_offset=0.0):
        #def_exposure is default exposure time in msec
       
        
        self.channels= channels
        self.def_exposure=def_exposure
        self.def_offset=0.0
        
        self.exposure_times=exposure_times
        self.zoffsets=zoffsets
        self.usechannels=usechannels
        self.prot_names=prot_names
        
        if map_chan is None:
            for ch in self.channels:
                if 'dapi' in ch.lower():
                    map_chan = ch
        if map_chan is None:
            map_chan = channels[0]
            
        self.map_chan = map_chan
        
    def save_settings(self,cfg):    
        
        cfg.Write('map_chan',self.map_chan)
        for ch in self.channels:
            cfg.WriteInt('Exposures/'+ch,self.exposure_times[ch])
            cfg.WriteFloat('ZOffsets/'+ch,self.zoffsets[ch])
            cfg.WriteBool('UseChannel/'+ch,self.usechannels[ch])
            cfg.Write('ProteinNames/'+ch,self.prot_names[ch])
            
    def load_settings(self,cfg):
        for ch in self.channels:
            self.exposure_times[ch]=cfg.ReadInt('Exposures/'+ch, self.def_exposure)
            self.zoffsets[ch]=cfg.ReadFloat('ZOffsets/'+ch,self.def_offset)
            self.usechannels[ch]=cfg.ReadBool('UseChannel/'+ch,True)
            self.prot_names[ch]=cfg.Read('ProteinNames/'+ch,ch)
        self.map_chan=str(cfg.Read('map_chan','DAPI'))

class ChangeChannelSettings(wx.Dialog):
    """simple dialog for changing the channel settings"""
    def __init__(self, parent, id, title, settings,style):
        wx.Dialog.__init__(self, parent, id, title,style=wx.DEFAULT_DIALOG_STYLE, size=(420, -1))
        
        self.settings=settings
        vbox = wx.BoxSizer(wx.VERTICAL)   
        Nch=len(settings.channels)
        print Nch
        
        gridSizer=wx.FlexGridSizer(rows=Nch+1,cols=6,vgap=5,hgap=5)
        
      
        gridSizer.Add(wx.StaticText(self,id=wx.ID_ANY,label="chan"),border=5)
        gridSizer.Add(wx.StaticText(self,id=wx.ID_ANY,label="protein"),border=5)     
        gridSizer.Add(wx.StaticText(self,id=wx.ID_ANY,label="use?"),border=5)
        gridSizer.Add(wx.StaticText(self,id=wx.ID_ANY,label="exposure"),border=5)
        gridSizer.Add(wx.StaticText(self,id=wx.ID_ANY,label="map?"),border=5)
        gridSizer.Add(wx.StaticText(self,id=wx.ID_ANY,label="zoffset     "),border=5)
        
        
        self.ProtNameCtrls=[]
        self.UseCtrls=[]
        self.ExposureCtrls=[]
        self.MapRadCtrls=[]
        self.ZOffCtrls=[]
        
        for ch in settings.channels:
            hbox =wx.BoxSizer(wx.HORIZONTAL)
            Txt=wx.StaticText(self,label=ch)
            ProtText=wx.TextCtrl(self,value=settings.prot_names[ch])
            ChBox = wx.CheckBox(self)
            ChBox.SetValue(settings.usechannels[ch])
            IntCtrl=wx.lib.intctrl.IntCtrl( self, value=settings.exposure_times[ch],size=(50,-1))
            FloatCtrl=wx.lib.agw.floatspin.FloatSpin(self, 
                                       value=settings.zoffsets[ch],
                                       min_val=-3.0,
                                       max_val=3.0,
                                       increment=.1,
                                       digits=2,
                                       name='',
                                       size=(95,-1)) 
               
            if ch is settings.channels[0]:
                RadBut = wx.RadioButton(self,-1,'',style=wx.RB_GROUP)
            else:
                RadBut = wx.RadioButton(self,-1,'')
            if ch == settings.map_chan:
                RadBut.SetValue(True)
                
            gridSizer.Add(Txt,0,flag=wx.ALL|wx.EXPAND,border=5)
            gridSizer.Add(ProtText,1,flag=wx.ALL|wx.EXPAND,border=5)
            gridSizer.Add(ChBox,0,flag=wx.ALL|wx.EXPAND,border=5)
            gridSizer.Add(IntCtrl,0,border=5)
            gridSizer.Add(RadBut,0,flag=wx.ALL|wx.EXPAND,border=5)
            gridSizer.Add(FloatCtrl,0,flag=wx.ALL|wx.EXPAND,border=5)
            
            self.ProtNameCtrls.append(ProtText)
            self.UseCtrls.append(ChBox)
            self.ExposureCtrls.append(IntCtrl)
            self.MapRadCtrls.append(RadBut)
            self.ZOffCtrls.append(FloatCtrl)
        
           
        hbox = wx.BoxSizer(wx.HORIZONTAL)      
        ok_button = wx.Button(self,wx.ID_OK,'OK')
        cancel_button = wx.Button(self,wx.ID_CANCEL,'Cancel')
        hbox.Add(ok_button)
        hbox.Add(cancel_button)
        
        vbox.Add(gridSizer)
        vbox.Add(hbox)
        
        self.SetSizer(vbox)
    
        
    def GetSettings(self):
        prot_names=dict([])
        usechannels=dict([])
        exposure_times=dict([])
        zoffsets=dict([])
        
        for i,ch in enumerate(self.settings.channels):
            prot_names[ch]=self.ProtNameCtrls[i].GetValue()
            usechannels[ch]=self.UseCtrls[i].GetValue()
            exposure_times[ch]=self.ExposureCtrls[i].GetValue()
            if self.MapRadCtrls[i].GetValue():
                map_chan=ch
            zoffsets[ch]=self.ZOffCtrls[i].GetValue()
        return ChannelSettings(self.settings.channels,exposure_times=exposure_times,zoffsets=zoffsets,usechannels=usechannels,prot_names=prot_names,map_chan=map_chan)
        
 
class MosaicSettings:
    def __init__(self,mag=65.486,mx=1,my=1,overlap=10,show_box=False,show_frames=False):
        """a simple struct class for encoding settings about mosaics
        
        keywords)
        mag=magnification of objective
        mx=integer number of columns in a rectangular mosaic
        my=integer number of rows in a rectangular mosaic
        overlap=percentage overlap of individual frames (0-100)
        show_box=boolean as to whether to display the box
        show_frames=Boolean as to whether to display the individual frames
        
        """
        self.mx=mx
        self.my=my
        self.overlap=overlap
        self.show_box=show_box
        self.show_frames=show_frames
        self.mag=mag
    def save_settings(self,cfg):
        cfg.WriteFloat('mosaic_mag',self.mag)
        cfg.WriteInt('mosaic_mx',self.mx)
        cfg.WriteInt('mosaic_my',self.my)
        cfg.WriteInt('mosaic_overlap',self.overlap)
        cfg.WriteBool('mosaic_show_box',self.show_box)
        cfg.WriteBool('mosaic_show_frames',self.show_frames)
        
    def load_settings(self,cfg):
        self.mag=cfg.ReadFloat('mosaic_mag',65.486)
        self.mx=cfg.ReadInt('mosaic_mx',1)
        self.my=cfg.ReadInt('mosaic_my',1)
        self.overlap=cfg.ReadInt('mosaic_overlap',10)
        self.show_box=cfg.WriteBool('mosaic_show_box',False)
        self.show_frames=cfg.WriteBool('mosaic_show_frames',False)
        
  
class ChangeCameraSettings(wx.Dialog):
    """simple dialog for changing the camera settings"""
    def __init__(self, parent, id, title, settings):
        wx.Dialog.__init__(self, parent, id, title, size=(230, 210))
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)       
        self.widthIntCtrl=wx.lib.intctrl.IntCtrl( panel, value=settings.sensor_width,pos=(95,5),size=( 90, -1 ) )
        self.heightIntCtrl=wx.lib.intctrl.IntCtrl( panel, value=settings.sensor_height,pos=(95,35),size=( 90, -1 ) )
        self.pixwidthFloatCtrl=wx.lib.agw.floatspin.FloatSpin(panel, pos=(95,65),size=( 90, -1 ),
                                       value=settings.pix_width,
                                       min_val=0.1,
                                       max_val=100,
                                       increment=.1,
                                       digits=2,
                                       name='pix_width')
        self.pixheightFloatCtrl=wx.lib.agw.floatspin.FloatSpin(panel, pos=(95,95),size=( 90, -1 ),
                                       value=settings.pix_height,
                                       min_val=0.1,
                                       max_val=100,
                                       increment=.1,
                                       digits=2,
                                       name='pix_height')                             
                                         
        wx.StaticText(panel,id=wx.ID_ANY,label="Width (pixels)",pos=(5,8))
        wx.StaticText(panel,id=wx.ID_ANY,label="Height (pixels)",pos=(5,38))  
        wx.StaticText(panel,id=wx.ID_ANY,label="Pixel Width (um)",pos=(5,68))  
        wx.StaticText(panel,id=wx.ID_ANY,label="Pixel Height (um)",pos=(5,98)) 
                                         
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(70, 30))
       # closeButton = wx.Button(self, wx.ID_CLOSE, 'Close', size=(70, 30))
        hbox.Add(okButton, 1)
        #hbox.Add(closeButton, 1, wx.LEFT, 5)
        vbox.Add(panel)
        vbox.Add(hbox, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(vbox)
    def GetSettings(self):
        """extracts the Camera Settings from the controls"""
        return CameraSettings(sensor_width=self.widthIntCtrl.GetValue(),
                              sensor_height=self.heightIntCtrl.GetValue(),
                              pix_width=self.pixwidthFloatCtrl.GetValue(),
                              pix_height=self.pixheightFloatCtrl.GetValue())
        
class ImageSettings():
    def __init__(self,extent=[0,10,10,0]):
        self.extent=extent
        
class ChangeImageMetadata(wx.Dialog):
    """simple dialog for edchanging the camera settings"""
    def __init__(self, parent, id, title, settings=ImageSettings()):
        wx.Dialog.__init__(self, parent, id, title, size=(230, 210))
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)       
        self.minXIntCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.extent[0],pos=(125,5),size=( 90, -1 ),increment=1,digits=2 )
        self.maxXIntCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.extent[1],pos=(125,35),size=( 90, -1 ),increment=1,digits=2 )
        self.minYIntCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.extent[3],pos=(125,65),size=( 90, -1 ),increment=1,digits=2 )
        self.maxYIntCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.extent[2],pos=(125,95),size=( 90, -1 ),increment=1,digits=2 )
                                                           
        wx.StaticText(panel,id=wx.ID_ANY,label="Minimum X (um)",pos=(5,8))
        wx.StaticText(panel,id=wx.ID_ANY,label="Maximum X (um)",pos=(5,38))  
        wx.StaticText(panel,id=wx.ID_ANY,label="Minimum Y (um) (bottom)",pos=(5,68))  
        wx.StaticText(panel,id=wx.ID_ANY,label="Maximum Y (um) (top)",pos=(5,98)) 
                                         
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(70, 30))
       # closeButton = wx.Button(self, wx.ID_CLOSE, 'Close', size=(70, 30))
        hbox.Add(okButton, 1)
        #hbox.Add(closeButton, 1, wx.LEFT, 5)
        vbox.Add(panel)
        vbox.Add(hbox, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(vbox)
    def GetSettings(self):
        """extracts the Camera Settings from the controls"""
        return ImageSettings(extent=[self.minXIntCtrl.GetValue(),
                                     self.maxXIntCtrl.GetValue(),
                                     self.maxYIntCtrl.GetValue(),
                                     self.minYIntCtrl.GetValue()])
        

class SmartSEMSettings():
    def __init__(self,mag=1200,tilt=0.33,rot=0,Z=0.0125,WD=0.00632568):
        self.mag=mag
        self.tilt=tilt
        self.rot=rot
        self.Z=Z
        self.WD=WD
    def save_settings(self,cfg):
        cfg.WriteInt('SEM_mag',self.mag)
        cfg.WriteFloat('SEM_tilt',self.tilt)
        cfg.WriteFloat('SEM_rot',self.rot)
        cfg.WriteFloat('SEM_Z',self.Z)
        cfg.WriteFloat('SEM_WD',self.WD)
    def load_settings(self,cfg):
        self.mag=cfg.ReadInt('SEM_mag',1200)
        self.tilt=cfg.ReadFloat('SEM_tilt',0.33)
        self.rot=cfg.ReadFloat('SEM_rot',0)
        self.Z=cfg.ReadFloat('SEM_Z',0.0125)
        self.WD=cfg.ReadFloat('SEM_WD',0.00632568)
        
class ChangeSEMSettings(wx.Dialog):
    """simple dialog for edchanging the camera settings"""
    def __init__(self, parent, id, title, settings=SmartSEMSettings()):
        wx.Dialog.__init__(self, parent, id, title, size=(230, 210))
        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)       
        self.magCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.mag,pos=(125,5),size=( 90, -1 ),increment=100,digits=2 )
        self.tiltCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.tilt,pos=(125,35),size=( 90, -1 ),increment=1,digits=4 )
        self.rotCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.rot,pos=(125,65),size=( 90, -1 ),increment=1,digits=4 )
        self.ZCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.Z,pos=(125,95),size=( 90, -1 ),increment=1,digits=4 )
        self.WDCtrl=wx.lib.agw.floatspin.FloatSpin( panel, value=settings.WD,pos=(125,125),size=( 90, -1 ),increment=1,digits=4 )
        
        wx.StaticText(panel,id=wx.ID_ANY,label="magnification (prop. area)",pos=(5,8))
        wx.StaticText(panel,id=wx.ID_ANY,label="tilt (radians)",pos=(5,38))  
        wx.StaticText(panel,id=wx.ID_ANY,label="rotation (radians)",pos=(5,68))  
        wx.StaticText(panel,id=wx.ID_ANY,label="Z location (mm)",pos=(5,98))
        wx.StaticText(panel,id=wx.ID_ANY,label="WD working distance? (mm)",pos=(5,128))
                                         
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, wx.ID_OK, 'Ok', size=(70, 30))
       # closeButton = wx.Button(self, wx.ID_CLOSE, 'Close', size=(70, 30))
        hbox.Add(okButton, 1)
        #hbox.Add(closeButton, 1, wx.LEFT, 5)
        vbox.Add(panel)
        vbox.Add(hbox, 1, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        self.SetSizer(vbox)
    def GetSettings(self):
        """extracts the Camera Settings from the controls"""
        return SmartSEMSettings(mag=self.magCtrl.GetValue(),
                                     tilt=self.tiltCtrl.GetValue(),
                                     rot=self.rotCtrl.GetValue(),
                                     Z=self.ZCtrl.GetValue(),
                                     WD=self.WDCtrl)
                                     