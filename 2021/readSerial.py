#!/usr/bin/env python3
import serial
import json
from influxdb import InfluxDBClient
client = InfluxDBClient(host='192.168.0.20', port=8086)
client.switch_database('zap')
print('Started zap')
#Serial takes two parameters: serial device and baudrate
ser = serial.Serial('/dev/ttyS0', 115200)
ser.reset_input_buffer()
data=b''
val=0
values=[]

# https://stackoverflow.com/questions/16716302/how-do-i-fit-a-sine-curve-to-my-data-with-pylab-and-numpy
import numpy
import scipy.optimize #import leastsq
#import plotly.express as px
import os

def parseToList(dataLine):
    # v1 behaviour:
    # each line is a list of current data, for eaxmple
    # [1,2,3,4,5]
    # v2 behaviour
    # expect each line to be a list of 2 lists
    # current data then voltage data
    # e.g [[1,2,3,4,5],[6,5,4,2,1]]
    valuesList=[]
    if len(dataLine) > 0:
        try:
            valuesList = eval(dataLine)
            #print("len=%d" %len(valuesList))
        except:
            #print("oh no", data.decode("utf-8"))
            pass
    return valuesList

def calculate(adcValue, inPhase, phaseAngle):
    #convert adc levels to A
    # 2000 turn transformer. 50ohm shunt resistor. mains current is limited to 100A.
    # adc is 12bit (0-1023) 5v. midpoint 2.5 is 0A.
    # full scale = 2.5v/50ohm = 50mA. 50mA * 2000 = 100A
    # 1 bit = 2.5v/512/50*2000 = 0.1953125A

    #A = (measured/adc_range*adc_scale-adc_offset)/resistance * turns * rms
    if not inPhase:
        adcValue = -adcValue
    max_a = adcValue * 0.1953125 * 0.7070
    max_w = (max_a*230)
    return {'adcValue':int(adcValue),'A':(max_a), 'W':(max_w), "angle":(phaseAngle)}

# def fixSignPhase(fittedValues):
#     # fix negative measurements by adjusting phase (-1 is same as 1 plus phase shift)
#     if (fittedValues["amp"])<1:
#         fittedValues["amp"] = -fittedValues["amp"]
#         fittedValues["phase"] = fittedValues["phase"] + fittedValues["period"]/2
#     return fittedValues


def writeToInflux(clientConn, dataDict):
    updated = {"measurement":"netPower","fields":dataDict}
    if not clientConn.write_points([updated]):
        print ("Writing to Influx failed")
    pass

# def writeSampleSetToInflux(clientConn, dataDict):
#     updated = {"measurement":"errors","fields":dataDict}
#     if not clientConn.write_points([updated]):
#         print ("Writing to Influx failed")
#     pass

# for sine fit image
if not os.path.exists("images"):
    os.mkdir("images")

#https://stackoverflow.com/a/42322656/643210
def fit_sin(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = numpy.array(tt)
    yy = numpy.array(yy)
    ff = numpy.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(numpy.fft.fft(yy))
    guess_freq = abs(ff[numpy.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    guess_amp = numpy.std(yy) * 2.**0.5
    guess_offset = numpy.mean(yy)
    guess = numpy.array([guess_amp, 2.*numpy.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * numpy.sin(w*t + p) + c
    popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    f = w/(2.*numpy.pi)
    fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": numpy.max(pcov), "rawres": (guess,popt,pcov)}

def drawSinefit(points, fitted, t):
    lines = dict(raw=points, fitted=fitted["fitfunc"](t))
    fig = px.line(lines)
    fig.write_image("images/fig1.png")

def InPhase(wave1, wave2):
    import math
    if(wave1["amp"])<0:
        wave1["amp"] = -wave1["amp"]
        wave1["phase"] = wave1["phase"]+math.pi
    if(wave2["amp"])<0:
        wave2["amp"] = -wave2["amp"]
        wave2["phase"] = wave2["phase"]+math.pi
    wave1["phase"] = wave1["phase"] % (2*math.pi)
    wave2["phase"] = wave2["phase"] % (2*math.pi)
    phase=wave1["phase"]-wave2["phase"]
    if(phase<0):
        phase = phase+2*math.pi
    inPhase = phase<math.pi/1.7 or phase>(3*math.pi/2) #should be pi/2 but use 1.7 as fudge factorf
    #print (inPhase)
    #print (absPhase)
    return (inPhase, phase * 360.0/(2.0*math.pi))

while 1:
    ser.reset_input_buffer()
    data = ser.readline()
    if len(data) > 0:
        values=parseToList(data) # single array
        if len(values)==2:
            current = values[0]
            voltage = values[1]
        elif len(values) > 0:
            current = values
            voltage = []
        else:
            continue # bad data, skip the loop
        
        if False: #print the data, TODO use a signal here instead
            print("voltage data")
            counter=0
            for num in voltage:
                print("%d,%d," %(counter,num))
                counter += 1
        if False: #print the data, TODO use a signal here instead
            print("current data")
            counter=0
            for num in current:
                print("%d,%d," %(counter,num))
                counter += 1

        # use the phase of the voltage and current to determine direction
        # in phase = consumption (positive quantity)
        # out of phase = generation (negative quantity)
        # voltage data may not be present (e.g v1 arduino code)
        inPhase = True # assume for now
        phaseAngle = float()
        voltageFit = False # overwrite inside
        if len(voltage) > 0:
            t = numpy.linspace(0, len(voltage)-1, len(voltage))
            try:
                voltageFit = fit_sin(t, voltage)
                #print( "VOLTAGE Amplitude=%(amp)s, phase=%(phase)s, period=%(period)s, offset=%(offset)s, Max. Cov.=%(maxcov)s" % voltageFit )
                #voltageFit = fixSignPhase(voltageFit)
            except:
                pass
        
        t = numpy.linspace(0, len(current)-1, len(current))
        try:
            currentFit = fit_sin(t, current)
            #print( "CURRENT Amplitude=%(amp)s, phase=%(phase)s, period=%(period)s, offset=%(offset)s, Max. Cov.=%(maxcov)s" % currentFit )
            #currentFit = fixSignPhase(currentFit)
            
            if abs(currentFit["amp"]) < 500:
                if (voltageFit != False): # compare phase
                    (inPhase, phaseAngle) = InPhase(currentFit, voltageFit)
                    #print("inPhase = %f, angle = %f" % (inPhase, phaseAngle))
                #convert adc levels to A and W
                valuesToSend = calculate(abs(currentFit["amp"]),inPhase, phaseAngle)
                #print(valuesToSend)
                writeToInflux(client,valuesToSend)
            else:
                print("Data error max of samples is %f but fit is %f. maxcov = %f " %(max(current),currentFit["amp"], currentFit["maxcov"]))
        except:
#              writeToInflux(client,{'samples':values})
            pass

        data=b''
ser.close()
