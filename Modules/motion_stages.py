#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 22:10:08 2020
@author: jgollub
"""
import serial
from time import sleep
import math
# from zaber_motion.ascii import Connection
# from zaber_motion import Units, MotionLibException

# configure the serial connection
#check for usb rs232 serial connection using command line: ls /dev/cu.*

class SyringePump:
    '''
    syringe commands for infusion or withdraw
    syringe_command(ser,0, 'DIR INF', print_to_screen=True)
    syringe_command(ser,0, 'DIR WDR', print_to_screen=True)
    
    start/stop commands
    syringe_command(ser,0, 'RUN', print_to_screen=True)
    syringe_command(ser,0, 'STP', print_to_screen=True)
    '''
    def __init__(self, port: str = 'COM5'):
        self.connection = serial.Serial(
                                     port= port,
                                     baudrate=19200,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=.1
                                     )
         
    def __enter__(self):

        return self

    def syringe_command(self, pump_number: float, command, print_to_screen: bool=False):
        self.connection.write(((f'{pump_number:02d}' + command + '\r')).encode('utf-8'))

        response=self.connection.readline() 
        (address, status, data)=(response.decode('utf-8')[1:-1][:2],
                                 response.decode('utf-8')[1:-1][2:3],
                                 response.decode('utf-8')[1:-1][3:])
        
        if print_to_screen is True:
            print(f'Syringe [{address}], (status: {status}), Response: {data}')
            
    def wait_for_stage(self, pump_number: float, print_to_screen: bool=True):
        
        while True:
            self.connection.write(((f'{pump_number:02d}' + '' + '\r')).encode('utf-8'))
             
            response=self.connection.readline() 
            (address, status, data)=(response.decode('utf-8')[1:-1][:2],
                                     response.decode('utf-8')[1:-1][2:3],
                                     response.decode('utf-8')[1:-1][3:])
        
            if print_to_screen is True:
                print(f'Syringe [{address}], (status: {status}), Response: {data}')
           
            if status is 'S':
                break
            
    def setup(self, pump_number: float, syringe_diameter: float, volume_step: float, rate: float):
         
        self.syringe_command(pump_number, ('DIA ' + str(syringe_diameter))) #set diameter
        self.syringe_command(pump_number, 'DIA ', print_to_screen=True)
        
        self.syringe_command(pump_number, 'VOL ML') #set volume units 
        self.syringe_command(pump_number, 'VOL ' + str(volume_step)) #set volume step size
        self.syringe_command(pump_number, 'VOL ', print_to_screen=True)

        self.syringe_command(pump_number, 'RAT ' + str(rate)) #set rate 
        self.syringe_command(pump_number, 'RAT ', print_to_screen=True)
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.connection.close()
        
class ZaberMultistaticStage:
    def __init__(self, port: str = 'COM6'):
        self.port = Connection.open_serial_port(port)
        
        device_list = self.port.detect_devices()
        print("Found {} devices".format(len(device_list)))
             
        self.maxHomingX_Sat1 = 20000 #steps/sec
        self.maxHomingY_Sat1 = 40000 #steps/sec 
        self.maxVelocity=10000
        # self.maxVelocity=100000
             
        device1 = device_list[0] # Device number 1  
    
        self.sat1_X_stage = device1.get_axis(2)   
        self.sat1_Y_stage = device1.get_axis(1)
            
        try:
        #set max axes speed for homing
            self.sat1_X_stage.settings.set('maxspeed', self.maxHomingX_Sat1)
            self.sat1_Y_stage.settings.set('maxspeed', self.maxHomingY_Sat1)  

        except MotionLibException as err:
            print(err) 

        try:
            # Home the device and check the result.
            self.sat1_X_stage.home()
            self.sat1_Y_stage.home()
      
        except MotionLibException as err:
            print(err)
            
        try:
            #set maxspeed for stage movement
            self.sat1_X_stage.settings.set('maxspeed', self.maxVelocity)
            self.sat1_Y_stage.settings.set('maxspeed', self.maxVelocity)    
        except MotionLibException as err:
            print(err) 
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.port.close() 

class Zaber_2axis_LST1500D:
    def __init__(self, port: str = 'COM8', maxspeed=150):
        self.ser=serial.Serial()
        self.ser.port=port
        self.maxspeed = maxspeed
        if self.maxspeed > 150:
            print('Max speed cannot exceed 150 mm/s, setting to 150 mm/s.')
            self.maxspeed = 150
        self.ser.timeout = 1
        self.ser.baudrate=115200
        self.ser.open()
                     
        # device1 = [0] # Device number 1  
        self.axes = '0'
        self.x_axis = '1'    
        self.y_axis = '2'
        
        self.step_size = 1.984375 *10**(-3) #convert to mm units
        self.velocity_conversion = 1.6384   #conversion factor for velocity, in seconds
        velocity_in_motor_speed = int(round(self.maxspeed * self.velocity_conversion/self.step_size, 0))
        self.ser.write(f'/{self.x_axis} set maxspeed {velocity_in_motor_speed}\r'.encode())
        dummy_reply=self.ser.read_until()
        self.ser.write(f'/{self.y_axis} set maxspeed {velocity_in_motor_speed}\r'.encode())
        dummy_reply=self.ser.read_until()

    def set_maxspeed(self, maxspeed):
        self.maxspeed = maxspeed
        if self.maxspeed > 150:
            print('Max speed cannot exceed 150 mm/s, setting to 150 mm/s.')
            self.maxspeed = 150
        velocity_in_motor_speed = int(round(self.maxspeed * self.velocity_conversion/self.step_size, 0))
        self.ser.write(f'/{self.x_axis} set maxspeed {velocity_in_motor_speed}\r'.encode())
        dummy_reply=self.ser.read_until()
        self.ser.write(f'/{self.y_axis} set maxspeed {velocity_in_motor_speed}\r'.encode())
        dummy_reply=self.ser.read_until()

    def wait_for_idle_status(self):
        
        #test that x-axis has finished moving
        testx=-1
        while testx == -1:
            sleep(.02)
            self.ser.write(f'/{self.x_axis}\r'.encode())            
            reply_x=self.ser.read_until()
            testx=reply_x.decode().find('IDLE')
            # print(f'{reply_x.decode()}, and test is {testx}')
            if reply_x.decode().find('WR') != -1:
                print('x axis not homed')
            sleep(.1)
        
        #test that y-axis has finished moving
        testy=-1
        while testy== -1:
            sleep(.02)
            self.ser.write(f'/{self.y_axis}\r'.encode())
            reply_y=self.ser.read_until()            
            testy=reply_y.decode().find('IDLE')
            # print(f'{reply_y.decode()}, and test is {testy}')
            if reply_y.decode().find('WR') != -1:
                print('y axis not homed')
            sleep(.1) #set for long settle time
        
    def home_axes(self):
        self.ser.write('/0 home\r'.encode())
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        self.wait_for_idle_status()

    def move_x_absolute(self, position, quiet=True): #input in mm
        position_in_motor_steps =int(round(position/self.step_size, 0))
        self.ser.write(f'/{self.x_axis} move abs {position_in_motor_steps}\r'.encode() )
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        if not quiet:
            print(f'set x_position= {position:.6g}')
            print(f'set x_position in steps= {position_in_motor_steps:.12g}')
        self.wait_for_idle_status()
        
    def move_y_absolute(self, position, quiet=True): #input in mm
        #note accounting for negative axis by subtracting 1500 mm
        position_in_motor_steps =int(round(position/self.step_size, 0))
        self.ser.write(f'/{self.y_axis} move abs {position_in_motor_steps}\r'.encode())
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        if not quiet:
            print(f'set y_position= {position:.6g}')
            print(f'set y_position in steps= {position_in_motor_steps:.12g}')
        self.wait_for_idle_status()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.ser.close()     

class Newmark_NSC_G2:
    def __init__(self, port: str = '169.254.225.173', speedmms = 25, **kwargs):
        import gclib

        self.quiet = kwargs.get('quiet', False)
        self.steptomm = 5000
        self.speedmms = speedmms
        self.port = port
        self.stage_object = gclib.py()
        self.stage_object.GOpen(self.port)
        self.home_axes()
        self.zero_axes()
    
    def stop(self): # stop the stage
        self.stage_object.GCommand('ST')

    def zero_axes(self): # zero the x,y axes
        self.ZeroInXsteps = float(self.stage_object.GCommand('MG _RPA'))
        self.ZeroInYsteps = float(self.stage_object.GCommand('MG _RPB'))
    
    def get_position(self): # get current position
        xposSteps = float(self.stage_object.GCommand('MG _RPA'))
        yposSteps = float(self.stage_object.GCommand('MG _RPB'))
        
        # note negative sign to match NFS coord Sys
        xUserPos = -(xposSteps - self.ZeroInXsteps) / self.steptomm 
        yUserPos = -(yposSteps - self.ZeroInYsteps) / self.steptomm

        return xUserPos, yUserPos
    
    def get_step_position(self): # get current position in steps
        xposSteps = float(self.stage_object.GCommand('MG _RPA'))
        yposSteps = float(self.stage_object.GCommand('MG _RPB'))

        return xposSteps, yposSteps
    
    def home_axes(self):
        stepperspeed = round(self.speedmms * self.steptomm)  # speed in cts/sec
        stepperaccel = round(10*stepperspeed)  # acceleration in cts/sec^2
        
        stagehome = (
            # set acceleration, deceleration of motors A,B
            'AC {},{};'.format(stepperaccel, stepperaccel) +
            'DC {},{};'.format(stepperaccel, stepperaccel) +

            # jog until you hit limits
            'JG {},{};'.format(-stepperspeed, -stepperspeed) + # set jog speeds and directions
            'BG;' +

            # after motion, move 1mm step back from edge
            'AM;'+ 
            'PR 10000,10000;' + 
            'BG;' +

            # after motion, define current positions of A,B as 0,0
            'AM;' + 
            'DP 0,0;' + 

            # capture min x,y step values
            'minx=_RPA;' + # _RPa is the "commanded position generated by the profiler for the 'a' axis"
            'miny=_RPB;' +  # _RPb is the "commanded position generated by the profiler for the 'b' axis"

            # set slew speeds of A,B and end program
            'SP 125000,125000;' +
            'EN;'
        ) 

        # download and execute the program
        self.stage_object.GProgramDownload(stagehome, '')
        self.stage_object.GCommand('XQ')

        # wait until test is done (?)
        testdone = 1
        while(testdone > -1 or math.isnan(testdone)):
            sleep(.01)
            testdone = float(self.stage_object.GCommand('MG _XQ'))
        
        # get values of minx,miny and return
        self.xminstepVal = float(self.stage_object.GCommand('MG minx'))
        self.yminstepVal = float(self.stage_object.GCommand('MG miny'))

    def move_relative(self, moveXmm, moveYmm):
        stepperspeed = round(self.speedmms * self.steptomm)  # speed in cts/sec
        stepperaccel = round(10*stepperspeed)  # acceleration in cts/sec^2

        stagemove = (
            # set accelerations, decelerations, slew speeds of motors A,B
            'AC {},{};'.format(stepperaccel, stepperaccel) +
            'DC {},{};'.format(stepperaccel, stepperaccel) +
            'SP {},{};'.format(stepperspeed, stepperspeed) +

            # set distances for A,B to move and begin motion
            'PR {},{};'.format(-moveXmm*self.steptomm,-moveYmm*self.steptomm) + 
            'BG;' + 

            # after motion, set value of variables posx, posy to _RPa, _RPb
            'AM;' + 
            'posx=_RPA'+ 
            'posy=_RPB' + 

            # end program
            'EN;'
        ) 

        # download and execute the program
        self.stage_object.GProgramDownload(stagemove, '')
        self.stage_object.GCommand('XQ')

        # wait until test is done (?)
        testdone = 1
        while(testdone > -1 or math.isnan(testdone)):
            sleep(.01)
            testdone = float(self.stage_object.GCommand('MG _XQ'))

        # get values of variables
        xposSteps = float(self.stage_object.GCommand('MG posx'))
        yposSteps = float(self.stage_object.GCommand('MG posy'))
        
        # calculate and return current x,y position
        xUserPos = -(xposSteps - self.ZeroInXsteps) / self.steptomm
        yUserPos = -(yposSteps - self.ZeroInYsteps) / self.steptomm
        
        if not self.quiet:
            return xUserPos, yUserPos
        
    def move_absolute(self, moveToUserXmm, moveToUserYmm):
        stepperspeed = round(self.speedmms * self.steptomm) # speed in cts/sec
        stepperaccel = round(10*stepperspeed) # acceleration in cts/sec^2
        
        stagemove = (
            # set accelerations, decelerations, slew speeds of motors A,B
            'AC {},{};'.format(stepperaccel, stepperaccel) +  # set accelerations of motors A,B
            'DC {},{};'.format(stepperaccel, stepperaccel) + # set decelerations of A,B
            'SP {},{};'.format(stepperspeed, stepperspeed) + # set slew speeds of A,B

            # set desired absolute positions and begin motion
            'PA {},{};'.format(-moveToUserXmm*self.steptomm+self.ZeroInXsteps,
                               -moveToUserYmm*self.steptomm+self.ZeroInYsteps) +
            'BG;' + 

            # after motion, capture posx,posy values
            'AM;' +
            'posx=_RPA;' +
            'posy=_RPB;' + 

            # end program
            'EN;'
        ) 

        # download and execute the program
        self.stage_object.GProgramDownload(stagemove, '')
        self.stage_object.GCommand('XQ')

        # wait until test is done (?)
        testdone = 1
        while(testdone > -1 or math.isnan(testdone)):
            sleep(.01)
            testdone = float(self.stage_object.GCommand('MG _XQ'))
        
        # get values of variables posx, posy
        xposSteps = float(self.stage_object.GCommand('MG posx'))
        yposSteps = float(self.stage_object.GCommand('MG posy'))
        
        # calculate and return current x,y positions
        xUserPos = -(xposSteps - self.ZeroInXsteps) / self.steptomm
        yUserPos = -(yposSteps - self.ZeroInYsteps) / self.steptomm
        
        if not self.quiet:
            return xUserPos, yUserPos
        
    def close(self):
        self.stage_object.GClose()
        print('Controller connection stopped.')
        
