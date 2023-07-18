import numpy as np
import multiprocessing as mp
from scipy import interpolate
from scipy import ndimage
import matplotlib.pyplot as plt
from abel.tools.polar import reproject_image_into_polar
from scipy.ndimage import gaussian_filter
import math
from multiprocessing import Process, Value, Array, Event, Pool
from matplotlib.path import Path
import os
import cv2
import re
from abel.tools.symmetry import get_image_quadrants
from abel.tools.center import set_center
from abel.tools.symmetry import put_image_quadrants
import numpy
from scipy.ndimage import map_coordinates
import abel
from obspy.imaging.cm import pqlx
import scipy.optimize
from matplotlib.widgets import Slider, Button
from scipy.optimize import curve_fit
from matplotlib.animation import FuncAnimation
import matplotlib.animation as anim
from matplotlib.colors import LogNorm
from scipy.signal import butter, lfilter, freqz
import circle_fit as cf
import tqdm
from scipy import fftpack, ndimage
from scipy.fftpack import rfft, irfft, fftfreq
#Map file number to a phase and then retry.
# Set bounds on the phase fit too
import matplotlib


def centeroidnp(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr)
    return sum_x/length

def running_mean(x, N):
    cumsum = numpy.cumsum(numpy.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

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
    try:
        popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy, p0=guess,bounds=((-np.inf,-np.inf,-np.pi/2,-np.inf),(np.inf,np.inf,np.pi/2,np.inf)), maxfev=50000)
    except RuntimeError or RuntimeWarning:
        print("Error")
        popt = 1,1,0,1
        pcov = 1,1,0,1
    A, w, p, c = popt
    f = w/(2.*numpy.pi)
    fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": numpy.max(pcov), "rawres": (guess,popt,pcov)}

def fit_sin_bound(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = numpy.array(tt)
    yy = numpy.array(yy)
    #ff = numpy.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    #Fyy = abs(numpy.fft.fft(yy))
    #guess_freq = abs(ff[numpy.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    #guess_amp = numpy.std(yy) * 2.**0.5
    #guess_offset = numpy.mean(yy)
    #guess = numpy.array([guess_amp, 2.*numpy.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * numpy.sin(w*t + p) + c
    try:
        popt, pcov = scipy.optimize.curve_fit(sinfunc, tt, yy,bounds=((-np.inf,0.9,-np.pi/2,-np.inf),(np.inf,1.2,np.pi/2,np.inf)), maxfev=50000)
    except RuntimeError:
        print("Error")
        popt = 1,1,0,1
        pcov = 1,1,0,1
    A, w, p, c = popt
    f = w/(2.*numpy.pi)
    fitfunc = lambda t: A * numpy.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": numpy.max(pcov)}

def resize_linear(image_matrix, new_height:int, new_width:int):
    """Perform a pure-numpy linear-resampled resize of an image."""
    output_image = numpy.zeros((new_height, new_width), dtype=image_matrix.dtype)
    original_height, original_width = image_matrix.shape
    inv_scale_factor_y = original_height/new_height
    inv_scale_factor_x = original_width/new_width

    # This is an ugly serial operation.
    for new_y in range(new_height):
        for new_x in range(new_width):
            # If you had a color image, you could repeat this with all channels here.
            # Find sub-pixels data:
            old_x = new_x * inv_scale_factor_x
            old_y = new_y * inv_scale_factor_y
            x_fraction = old_x - math.floor(old_x)
            y_fraction = old_y - math.floor(old_y)

            # Sample four neighboring pixels:
            left_upper = image_matrix[math.floor(old_y), math.floor(old_x)]
            right_upper = image_matrix[math.floor(old_y), min(image_matrix.shape[1] - 1, math.ceil(old_x))]
            left_lower = image_matrix[min(image_matrix.shape[0] - 1, math.ceil(old_y)), math.floor(old_x)]
            right_lower = image_matrix[min(image_matrix.shape[0] - 1, math.ceil(old_y)), min(image_matrix.shape[1] - 1, math.ceil(old_x))]

            # Interpolate horizontally:
            blend_top = (right_upper * x_fraction) + (left_upper * (1.0 - x_fraction))
            blend_bottom = (right_lower * x_fraction) + (left_lower * (1.0 - x_fraction))
            # Interpolate vertically:
            final_blend = (blend_top * y_fraction) + (blend_bottom * (1.0 - y_fraction))
            output_image[new_y, new_x] = final_blend

    return output_image

def polar_linear(img, o=None, r=None, output=None, order=1, cont=0):
    if r is None: r = img.shape[0]
    if output is None:
        output = np.zeros((r*2, r*2), dtype=img.dtype)
    elif isinstance(output, tuple):
        output = np.zeros(output, dtype=img.dtype)
    if o is None: o = np.array(output.shape)/2 - 0.5
    out_h, out_w = output.shape
    ys, xs = np.mgrid[:out_h, :out_w] - o[:,None,None]
    rs = (ys**2+xs**2)**0.5
    ts = np.arccos(xs/rs)
    ts[ys<0] = np.pi*2 - ts[ys<0]
    ts *= (img.shape[1]-1)/(np.pi*2)
    map_coordinates(img, (rs, ts), order=order, output=output)
    return output

def load_function_txt(x):
    data = np.loadtxt(x)
    data = data.reshape(1440,1920)
    data = set_center(data,(861,918),crop='maintain_size')
    data = ndimage.rotate(data,75) #74
    data = set_center(data,(1105,932),crop='maintain_size')
    return data

def interp_img(img_to_interp):
    x = np.arange(0, img_to_interp.shape[1], 1)
    y = np.arange(0, img_to_interp.shape[0], 1)
    f = interpolate.interp2d(x, y, img_to_interp, kind='linear')
    xnew = np.linspace(0,img_to_interp.shape[1],num=int(img_to_interp.shape[1]*4))
    ynew = np.linspace(0,img_to_interp.shape[0],num=int(img_to_interp.shape[0]*4))
    return f(xnew, ynew)

def to_polar(x):
    inverse_abel = reproject_image_into_polar(x,Jacobian=True)[0]
    return inverse_abel

def find_feature(top):#np.arange(int(int(inverse_polar.shape[1]/2) - len(fitpointstwo) / 2), int(int(inverse_polar.shape[1]/2) + len(fitpointstwo) / 2)):
    starttwo = np.where(energycalibration == find_nearest(energycalibration, startsearchrange))[0][0]
    stoptwo = np.where(energycalibration == find_nearest(energycalibration, stopsearchrange))[0][0]
    if top == 1:
        areaofinterest = gaussian_filter(toplineout[starttwo:stoptwo],sigma=30)
    else:
        areaofinterest = gaussian_filter(bottomlineout[starttwo:stoptwo],sigma=30)#np.transpose(np.roll(final, int(inverse_polar.shape[1]/2))[int(0)])[starttwo:stoptwo]
    x0 = np.where(areaofinterest == np.max(areaofinterest))[0][0] + starttwo
    return x0

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point
    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return qx, qy

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
    return ang + 360 if ang < 0 else ang

def make_bins(tupVerts):
    x, y = np.meshgrid(np.arange(tupVerts[1][1]),np.arange(tupVerts[1][0]))  
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    p = Path(tupVerts[0])
    grid = p.contains_points(points)
    topmask = grid.reshape(tupVerts[1][0], tupVerts[1][1])
    sumlocations = np.where(topmask == True)
    #if np.isnan(sumlocations).any()==True:
    #    sumlocations = np.array([[1],[1]])
    return sumlocations

def intensity_calc(wavelength,focallength,pulseduration,beamdiameterbeforefocus,msquared,reprate,averagepower):
    pulseenergy = (averagepower*10**-3)/reprate
    peakpulsepower = pulseenergy/(pulseduration*10**-15)
    fnumber = focallength/beamdiameterbeforefocus
    spotwaist = fnumber*msquared*wavelength*10**-9
    intensity = (2*peakpulsepower)/(3.14159*(spotwaist*100)*(spotwaist*100))
    return intensity

def smooth_ati(image_in):
    counterlimit = 0
    section = 0
    atispace = []
    startingati = []
    nextati = []
    polar = np.transpose(to_polar(image_in))
    atipeaks = np.arange(0,60,1.57)
    for i in atipeaks:
        startingati = np.append(startingati,np.where(energycalibration==find_nearest(energycalibration,i))[0][0])
        nextati = np.append(nextati,np.where(energycalibration==find_nearest(energycalibration,i+1.57))[0][0])
        atispace = np.append(atispace,np.where(energycalibration==find_nearest(energycalibration,i+1.57))[0][0]-np.where(energycalibration==find_nearest(energycalibration,i))[0][0])
    smooth_img = np.zeros((polar.shape[0],polar.shape[1]))
    sectionsigma = atispace[0]
    for i in np.arange(0,polar.shape[0]):
        for j in np.arange(0,polar.shape[1]):
            #if j<=int(atispace[0]/2) or j>=int(atispace[-1]/2):
            #smooth_img[i][j] += gaussian_filter(polar[i][j-int(atispace[section]/2):j+int(atispace[section]/2)],mode='nearest',sigma=sectionsigma)
            #else:
            smooth_img[i][j] += np.average(gaussian_filter(polar[i][j-int(atispace[section]/2):j+int(atispace[section]/2)],mode='nearest',sigma=sectionsigma))
            if section == len(atispace)-1:
                sectionsigma = atispace[section]
            elif j==startingati[section]+atispace[section]:
                section += 1
                sectionsigma = atispace[section]
    return resize_linear(smooth_img,polar.shape[0],polar.shape[1])   

def sum_the_bins(binpoints,img_to_sample):
    dcssum_fx = []
    for q in np.arange(0,len(binpoints)):
        if binpoints[q][0].size>0:
            ypos = binpoints[q][0]
            xpos = binpoints[q][1]
            binvalues = []
            for w in np.arange(0,len(ypos)):
                binvalues =np.append(binvalues, img_to_sample[ypos[w]][xpos[w]])
            binsum = np.average(binvalues)
            dcssum_fx = np.append(dcssum_fx,binsum)
        else:
            dcssum_fx = np.append(dcssum_fx,1)
    return dcssum_fx

def symm_img(asym_img,thresh,alpha):
    sharp_img = asym_img + alpha*(asym_img - ndimage.gaussian_filter(asym_img,1))
    quads = get_image_quadrants(sharp_img)
    Qone = np.flip(quads[1],axis=0)
    Qtwo = np.flip(quads[0],axis=0)
    Qthree = np.flip(quads[2],axis=0)
    Qfour = np.flip(quads[3],axis=0)
    minwidth = np.min(np.array([Qone.shape[1],Qtwo.shape[1],Qthree.shape[1],Qfour.shape[1]]))
    minheight = np.min(np.array([Qone.shape[0],Qtwo.shape[0],Qthree.shape[0],Qfour.shape[0]]))
    newQone = np.zeros((minheight,minwidth))
    newQtwo = np.zeros((minheight,minwidth))
    newQthree = np.zeros((minheight,minwidth))
    newQfour = np.zeros((minheight,minwidth))
    badpointsQ1 = np.zeros((minheight,minwidth))
    badpointsQ2 = np.zeros((minheight,minwidth))
    badpointsQ3 = np.zeros((minheight,minwidth))
    badpointsQ4 = np.zeros((minheight,minwidth))
    #Q1 mask
    Q2mask = np.zeros((minheight,minwidth))
    x, y = np.meshgrid(np.arange(minwidth),np.arange(minheight))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    polypoints = [(540,0),(681,483),(956,0)]
    p = Path(np.array(polypoints))
    grid = p.contains_points(points)
    Q2maskp2 = grid.reshape(minheight, minwidth)
    for i in np.arange(0,minheight):
        for j in np.arange(0,minwidth):
            R,theta = cart2pol(j,i)
            if R>=750:
                Q2mask[i][j] += 1
    region2mask = Q2mask + np.array(Q2maskp2,dtype=int)
    #Q2 mask
    Q1mask = np.zeros((minheight,minwidth))
    for i in np.arange(0,minheight):
        for j in np.arange(0,minwidth):
            R,theta = cart2pol(j,i)
            if R>=750:
                Q1mask[i][j] += 1
    region1mask = Q1mask
    #Q3 mask
    Q3mask = np.zeros((minheight,minwidth))
    for i in np.arange(0,minheight):
        for j in np.arange(0,minwidth):
            R,theta = cart2pol(j,i)
            if R>=750:
                Q3mask[i][j] += 1
    region3mask = Q3mask
    #Q4 mask
    Q4mask = np.zeros((minheight,minwidth))
    x, y = np.meshgrid(np.arange(minwidth),np.arange(minheight))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    polypoints = [(542,0),(267,957),(955,936),(955,0)]
    p = Path(np.array(polypoints))
    grid = p.contains_points(points)
    Q4maskp2 = grid.reshape(minheight, minwidth)
    for i in np.arange(0,minheight):
        for j in np.arange(0,minwidth):
            R,theta = cart2pol(j,i)
            if R>=750:
                Q4mask[i][j] += 1
    region4mask = Q4mask + np.array(Q4maskp2,dtype=int)
    for i in np.arange(0,minheight):
        for j in np.arange(0,minwidth):
            px_one = Qone[i][j]
            px_two = Qtwo[i][j]
            px_three = Qthree[i][j]
            px_four = Qfour[i][j]
            px_values = []
            if region1mask[i][j] == 0:
                px_values = np.append(px_values,px_one)
                usedone = 1
            else:
                usedone = 0
            if region2mask[i][j] == 0:
                px_values = np.append(px_values,px_two)
                usedtwo = 1
            else:
                usedtwo = 0
            if region3mask[i][j] == 0:
                px_values = np.append(px_values,px_three)
                usedthree = 1
            else:
                usedthree = 0
            if region4mask[i][j] == 0:
                px_values = np.append(px_values,px_four)
                usedfour = 1
            else:
                usedfour = 0
            output_px_values = np.array(px_values)
            if len(output_px_values) == 1 or len(output_px_values) == 2 or len(output_px_values) == 3 or len(output_px_values) == 4:
                if thresh >= stats_test(px_one,output_px_values) and usedone == 1:#px_one in output_px_values and usedone == 1: #start of 1
                    newQone[i][j] = px_one
                elif thresh <= stats_test(px_one,output_px_values):#elif px_one is not output_px_values and usedone ==1:
                    newQone[i][j] = np.average(output_px_values)
                    badpointsQ1[i][j] += 1
                if thresh >= stats_test(px_two,output_px_values) and usedtwo == 1:#px_two in output_px_values and usedtwo == 1: #start of 2
                    newQtwo[i][j] = px_two
                elif thresh <= stats_test(px_two,output_px_values):#px_two is not output_px_values and usedtwo == 1:
                    newQtwo[i][j] = np.average(output_px_values)
                    badpointsQ2[i][j] += 1
                if thresh >= stats_test(px_three,output_px_values) and usedthree == 1:#px_three in output_px_values and usedthree == 1: #start of 3
                    newQthree[i][j] = px_three
                elif thresh <= stats_test(px_three,output_px_values):#px_three is not output_px_values and usedthree == 1:
                    newQthree[i][j] = np.average(output_px_values)
                    badpointsQ3[i][j] += 1
                if thresh >= stats_test(px_four,output_px_values) and usedfour ==1:#px_four in output_px_values and usedfour == 1: #start of 4
                    newQfour[i][j] = px_four
                elif thresh <= stats_test(px_four,output_px_values):#px_four is not output_px_values and usedfour == 1:
                    newQfour[i][j] = np.average(output_px_values)
                    badpointsQ4[i][j] += 1
            else:
                if i == Qone.shape[0]-1 or i==0 or j==0 or j == Qone.shape[1]-1:
                    subone = 1#np.average([Qone[i+1][j],Qone[i-1][j],Qone[i][j+1],Qone[i][j-1]])
                    subtwo = 1#np.average([Qtwo[i+1][j],Qtwo[i-1][j],Qtwo[i][j+1],Qtwo[i][j-1]])
                    subthree = 1#np.average([Qthree[i+1][j],Qthree[i-1][j],Qthree[i][j+1],Qthree[i][j-1]])
                    subfour = 1#np.average([Qfour[i+1][j],Qfour[i-1][j],Qfour[i][j+1],Qfour[i][j-1]])
                elif region1mask[i][j]==1 or region2mask[i][j]==1 or region3mask[i][j]==1 or region4mask[i][j]==1:
                    subone = 1#np.average([Qone[i+1][j],Qone[i-1][j],Qone[i][j-1]])
                    subtwo = 1#np.average([Qtwo[i+1][j],Qtwo[i-1][j],Qtwo[i][j-1]])
                    subthree = 1#np.average([Qthree[i+1][j],Qthree[i-1][j],Qthree[i][j-1]])
                    subfour = 1#np.average([Qfour[i+1][j],Qfour[i-1][j],Qfour[i][j-1]])
                else:
                    subone = np.average([Qone[i+1][j],Qone[i-1][j],Qone[i][j+1],Qone[i][j-1]])
                    subtwo = np.average([Qtwo[i+1][j],Qtwo[i-1][j],Qtwo[i][j+1],Qtwo[i][j-1]])
                    subthree = np.average([Qthree[i+1][j],Qthree[i-1][j],Qthree[i][j+1],Qthree[i][j-1]])
                    subfour = np.average([Qfour[i+1][j],Qfour[i-1][j],Qfour[i][j+1],Qfour[i][j-1]])
                newQone[i][j]= subone
                newQtwo[i][j]= subtwo
                newQthree[i][j]= subthree
                newQfour[i][j]= subfour
    newQone = newQone[:950,:950]
    newQtwo = newQtwo[:950,:950]
    newQthree = newQthree[:950,:950]
    newQfour = newQfour[:950,:950]
    return put_image_quadrants([np.flip(newQone,axis=0),np.flip(newQtwo,axis=0),np.flip(newQthree,axis=0),np.flip(newQfour,axis=0)],asym_img.shape)

def isovolume(peakIone,intensitytwo,intensityone):
    peelvolumeone = ((4/3)*np.sqrt(peakIone/intensityone)+(2/9)*(((peakIone/intensityone)-1)**1.5)-(4/3)*np.arctan(np.sqrt((peakIone/intensityone)-1)))
    peelvolumetwo = ((4/3)*np.sqrt(peakIone/intensitytwo)+(2/9)*(((peakIone/intensitytwo)-1)**1.5)-(4/3)*np.arctan(np.sqrt((peakIone/intensitytwo)-1)))
    return peelvolumetwo-peelvolumeone

def scale_factor(directoryin):
    imgintensity = []
    rate = []
    for i in directoryin[:-2]:
        im = load_function_txt(i)
        impower = float(re.findall('\\d+\\.',i)[0])
        signal = np.sum(np.sum(np.transpose(im[200:220])[700:750],axis=0),axis=0)
        imgintensity = np.append(imgintensity,intensity_calc(wavelength,focallength,pulseduration,beamdiameterbeforefocus,msquared,reprate,impower)*10**-13)
    for q in np.arange(0,1):
        for j in np.arange(0,len(imgintensity)-q-1):
            rate = np.append(rate,np.abs(isovolume(imgintensity[q],imgintensity[j+i],imgintensity[j+q+1])))
    return rate

def multi_large(interp_img,quads):
    pool = Pool()
    result = [i for i in pool.map(interp_img,quads)]
    pool.close()
    pool.join()
    return result

def make_areas(poolinputs):
    pool = Pool()
    areasofbins = [i for i in pool.map(make_bins,poolinputs)]
    pool.close()
    pool.join()
    return areasofbins

def gauss(x,A, x0, sigma):
    return A*np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

def line(x,m,b):
    return m*x+b

def asymmetry(imgin):
    imgin = imgin/(np.max(imgin))
    imginpolar = abel.tools.polar.reproject_image_into_polar(imgin,Jacobian=True)[0]
    imgSliceR = np.sum(imginpolar[100:300,55:155])
    imgSliceL = np.sum(imginpolar[100:300,55+3000:155+3000])
    beta = (imgSliceR-imgSliceL)/(imgSliceL+imgSliceR)
    return beta

def fix_img(img,center):
    fixedImg = np.zeros(img.shape)
    Q2mask = np.zeros(img.shape)
    x, y = np.meshgrid(np.arange(img.shape[0]), np.arange(img.shape[1]))
    x, y = x.flatten(), y.flatten()
    points = np.vstack((x, y)).T
    polypoints = [(1396, 388), (1131, 1385), (1500, 1500),(1500,388)]
    p = Path(np.array(polypoints))
    grid = p.contains_points(points)
    Q2maskp2 = grid.reshape(img.shape[0], img.shape[1])
    #first number is the y then second is the x in img[y][x]
    for i in np.arange(0,img.shape[0]):
        for j in np.arange(0,img.shape[1]):
            r,theta = cart2pol(i-center[0],j-center[1])
            if r>=750:
                fixedImg[i][j]=1
            elif r<750 and Q2maskp2[i][j]==True:
                fixedImg[i][j]=1
            else:
                fixedImg[i][j]=img[i][j]
    return fixedImg

def fit_circle(img):
    fixedImg = np.zeros(img.shape)
    for i in np.arange(0,img.shape[0]):
        for j in np.arange(0,img.shape[1]):
            r,theta = cart2pol(i-(img.shape[0]/2),j-(img.shape[0]/2))
            if r<=200:
                fixedImg[i][j]=0
            elif r>=350:
                fixedImg[i][j] = 0
            else:
                fixedImg[i][j]=img[i][j]
    return fixedImg

def betaImg(img):
    beta_img = np.zeros(img.shape)
    for i in np.arange(img.shape[0]):
        for j in np.arange(img.shape[1]):
            beta_img[i][j] = (img[i][j] - np.flipud(img)[i][j])/(img[i][j] + np.flipud(img)[i][j])
    return beta_img

def phase_method(tuple):
    phaseLine = []
    #newx = np.linspace(np.min(tuple[1]), np.max(tuple[1]), 100)
    for i in np.arange(0,len(tuple[0])):
        #print(len(tuple[0][0]))
        if len(tuple[0][i])==49:
            #newy = np.interp(newx,tuple[1],tuple[0][i])
            newyfilter = gaussian_filter(tuple[0][i],8)
            phaseLine = np.append(phaseLine,fit_sin(tuple[1],newyfilter)['phase'])
    return phaseLine

def extract_phase(inarr): #allImgs [img number][y index][x index]
    allImgs = inarr[0]
    phaset = inarr[1]
    lines = [[[allImgs[i][k][j] for i in np.arange(0,allImgs.shape[0])] for j in np.arange(0,allImgs.shape[2])] for k in np.arange(0,allImgs.shape[1])]
    pooltuple = [[i,phaset] for i in lines]
    pool = Pool()
    phaseResult = [i for i in pool.map(phase_method,pooltuple)]
    pool.close()
    pool.join()
    return phaseResult

def rebin(a, shape):
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)

def identify_circle(imgin):
    averagingquad = np.zeros((1000,1000))
    for i in np.arange(0,1000):
        location = np.where(imgin[:500,i]>0)[0]
        avgindx = np.average(np.nan_to_num(location))
        avgindx = np.nan_to_num(avgindx)
        if avgindx != 0 and i>=450:
            averagingquad[int(avgindx),i] = 255
            averagingquad[int(avgindx)-1, i] = 255
            averagingquad[int(avgindx)+1, i] = 255
            if i!=0:
                averagingquad[int(avgindx), i-1] = 255
            if i!=499:
                averagingquad[int(avgindx), i+1] = 255
    return averagingquad

def get_dcs(vmi_img,pr,ar,percent,constant,phases,colorplot):
    top=0
    pxpr = (pr*pr)/2
    pxpr = np.sqrt(pxpr*(27.21*constant))
    pxar = (ar*ar)/2
    pxar = np.sqrt(pxar*(27.21*constant))
    #pxpr = np.sqrt(((pr*pr)/2)*constant)#np.sqrt(pr*constant)
    #pxar = np.sqrt(((ar*ar)/2)*constant)
    delta = pxpr*percent
    thetastep = 1
    if top==0:
        data_image = vmi_img
    else:
        data_image = np.flipud(vmi_img)
    #outputextract = []
    #outputextractx = []
    #outputextracty = []
    #outputupperpointsx = []
    #outputlowerpointsx = []
    #outputupperpointsy = []
    #outputlowerpointsy = []
    #yielderr = []
    #thetaerr = []
    extractimg = data_image[int((data_image.shape[0]/2)):,int(data_image.shape[1]/2):]
    dataimg = np.flipud(gaussian_filter(np.abs(extractimg),4))
    #pxvaluex = []
    #thetabin = []
    #rotatenumbers = []
    #pxvaluey = []
    yerrfinal = []
    xerrfinal = []
    upperpointsx = []
    upperpointsy = []
    lowerpointsx = []
    lowerpointsy = []
    for q in np.arange(90,-90+1,-thetastep):
        theta = (q*np.pi/180)
        upperx,uppery = pol2cart(pxpr+delta/2,theta)
        lowerx,lowery = pol2cart(pxpr-delta/2,theta)
        yshift = extractimg.shape[0] - pxar
        uppery = uppery-5
        lowery = lowery-5
        if q == 90 :
            ycircleshift = uppery-lowery-1 #np.abs(uppery - (extractimg.shape[0]))
            plt.scatter(upperx,uppery+yshift,marker='x')
            print(yshift)
        uppery = uppery + yshift
        lowery = lowery + yshift + ycircleshift
        circle_origin = extractimg.shape[0] - pxar
        thetaslip = getAngle((lowerx, lowery), (0, circle_origin), (upperx, uppery))
        upperrotated = rotate((0, circle_origin), (upperx, uppery), -thetaslip * np.pi / 180)
        upperpointsx = np.append(upperpointsx,upperrotated[0])
        upperpointsy = np.append(upperpointsy,upperrotated[1])
        lowerpointsx = np.append(lowerpointsx,lowerx)
        lowerpointsy = np.append(lowerpointsy,lowery)
    plt.scatter(upperpointsx,upperpointsy)
    plt.scatter(lowerpointsx,lowerpointsy)
    plt.scatter(0,circle_origin) #circle center is not in "center"
    plt.imshow(dataimg,vmin=0,vmax=0.6)
    plt.show()
    #for w in np.arange(0,181,0.1):
    #    theta = (w * np.pi / 180)
    #    extractx,extracty = pol2cart(extractradius,theta)
    #    extracty = extracty + feature/2
    #    extracty = extracty + yshift+delta-1
    #    extractx = extractx
    #    outputextractx = np.append(outputextractx,extractx)
    #    outputextracty = np.append(outputextracty,extracty)
    #for q in np.arange(0,len(outputextractx),1):
    #    pxvaluex = np.append(pxvaluex,dataimg[int(outputextracty[q])][int(outputextractx[q])])
    #    rval,thetaval = cart2pol(outputextractx[q],outputextracty[q]-(extractimg.shape[0]/2))
    #    thetabin = np.append(thetabin,thetaval*180/np.pi)
    #    if len(pxvaluex) == 20:
    #        thetaerr = np.append(thetaerr,np.std(thetabin))
    #        yielderr = np.append(yielderr,np.std(pxvaluex))
    #        outputextract =np.append(outputextract,np.average(pxvaluex))
    #        thetabin = []
    #        pxvaluex = []
    verts = [[(upperpointsx[q], upperpointsy[q]), (upperpointsx[q+1], upperpointsy[q+1]),(lowerpointsx[q+1], lowerpointsy[q+1]), (lowerpointsx[q], lowerpointsy[q])] for q in np.arange(0,len(upperpointsx)-1)]
    poolinputs = [(verts[q],(extractimg.shape[0],extractimg.shape[1])) for q in np.arange(0,len(verts))]
    areasofbins = make_areas(poolinputs)
    dcssum = []
    for q in np.arange(0,len(areasofbins)):
        ypos = areasofbins[q][0]
        xpos = areasofbins[q][1]
        binsum = 0
        yerr = []
        xerr = []
        if len(ypos)!=0:
            for w in np.arange(0,len(ypos)):
                binsum += dataimg[ypos[w]][xpos[w]]
                yerr = np.append(yerr,dataimg[ypos[w]][xpos[w]])
                rval,thetaval = cart2pol(xpos[w],np.abs(ypos[w]-dataimg.shape[0]))
                xerr = np.append(xerr,thetaval)
            binsum=binsum/len(ypos)
            xerrfinal = np.append(xerrfinal,np.std(xerr)/np.sqrt(len(ypos)))
            yerrfinal = np.append(yerrfinal,np.std(yerr)/np.sqrt(len(ypos)))
        else:
            newtheta = np.arange(90,-90+1,-thetastep)
            zeroAreaX, zeroAreaY = pol2cart(pxpr, newtheta[q] * np.pi / 180)
            zeroAreaX = zeroAreaX
            zeroAreaY = zeroAreaY+yshift+ycircleshift#+difference-1
            #binsum = dataimg[int(zeroAreaX),int(zeroAreaY)-2]
            xerrfinal = np.append(xerrfinal,0)
            yerrfinal = np.append(yerrfinal,0)
        dcssum = np.append(dcssum,binsum)
    #minLocation = np.where(gaussian_filter(dcssum,2)==np.min(np.min(gaussian_filter(dcssum,2))))[0][0]
    dcssum=dcssum[60:]
    yerrfinal=yerrfinal[60:]
    xerrfinal=xerrfinal[60:]
    #error bars are not the same length as the plot so its giving error
    plt.errorbar(np.linspace(60,180,len(dcssum)),gaussian_filter(dcssum,2)/np.max(gaussian_filter(dcssum,2)),yerr=yerrfinal,xerr=xerrfinal,label=str(round(phases,3)),color=colorplot)
    plt.xlabel('Theta (deg.)')
    plt.ylabel('Yield')
    plt.legend()
    return dataimg,areasofbins

def linearmethod(nonlinearimgline):
    linearimg = []
    for j in np.arange(0, 200):
        p1y = j
        p2y = j + 2
        squaresx = [i for i in np.arange(p1y, p2y)]
        spread = ((j+1)*(j+1))-(j*j)
        newx = np.linspace(p1y, p2y, spread)
        newlinechunk = np.interp(newx, squaresx, nonlinearimgline[p1y:p2y])
        linearimg = np.append(linearimg, newlinechunk)
    return linearimg

def linearize(img):
    pool = Pool()
    linearizedimg = [i for i in pool.map(linearmethod,np.transpose(img))]
    pool.close()
    pool.join()
    return linearizedimg

def main():
    #intensity calculations
    #wavelength = 800 #nm
    #focallength = 100 #mm
    #beamdiameterbeforefocus = 2 #mm
    #msquared = 1.6
    #reprate = 1000 #Hz
    #pulseduration = 35 #fs
    numberImgs = 50
    path = '/Users/ericmullins/Desktop/'
    directory = np.sort(os.listdir(str(path)))
    os.chdir(str(path))
    olddata = np.load('/Users/ericmullins/Desktop/argon_7_24_21.npy')
    oldimgs = [i[1060-700:1060+700,916-700:916+700] for i in olddata]
    loopcount = 0
    phasespots = []
    allinvimgs = []
    allbetaimgs = []
    loaddata = True
    if loaddata == False:
        for Z in sorted(directory)[1:numberImgs]:
            twenty_rawimg = load_function_txt(Z)
            twenty_rawimg = twenty_rawimg[440:440+1501,246:246+1501]
            cent = np.where(twenty_rawimg==np.max(twenty_rawimg[720:760,720:760]))
            twenty_rawimg = abel.tools.center.set_center(twenty_rawimg,(cent[1][0],cent[0][0]))
            twenty_rawimg = fix_img(twenty_rawimg,(750,750))
            #invout = abel.Transform(twenty_rawimg, direction='inverse', method='basex', verbose=False, symmetry_axis=0).transform
            #for i in np.arange(invout.shape[0]):
            #    for j in np.arange(invout.shape[1]):
            #        radius, rho = cart2pol(j-750,i-750)
            #        if radius>=700:
            #            invout[i][j]=1
            #invout = np.delete(np.abs(invout),slice(740,760),1)
            #quads = get_image_quadrants(twenty_rawimg)
            #result = multi_large(interp_img,quads)
            #new_img = put_image_quadrants(result,twenty_rawimg.shape)
            #new_img = cv2.resize(new_img, (2000, 2000))
            new_img = twenty_rawimg/np.max(twenty_rawimg)
            HIM = abel.Transform(new_img, direction='inverse',method='basex',verbose=False)
            new_imginv = HIM.transform
            new_imginvbeta = betaImg(new_imginv)
            phasespots.append(np.mean(np.nan_to_num(new_imginvbeta)[350:360, 680:690]))
            allinvimgs.append(new_imginv)
            allbetaimgs.append(np.nan_to_num(new_imginvbeta))
            #betaout = asymmetry(new_img)
            #betas = np.append(betas,betaout)
            loopcount+=1
        np.save('allinvimgs.npy',allinvimgs)
        np.save('allbetaimgs.npy',allbetaimgs)
        np.save('phasespots.npy',phasespots)
    elif loaddata=='1':
        for i in oldimgs:
            new_imginvbeta = betaImg(i)
            #plt.imshow(new_imginvbeta,vmin=-np.pi/2,vmax=np.pi/2)#[200:400,600:800]
            #plt.show()

            phasespots.append(np.average(np.nan_to_num(new_imginvbeta)[240:260,640:660]))
            fixingimg = i[:, 350:1050] / np.max(i[:, 350:1050])
            noise = fixingimg[90:130, 20:80]
            noise = np.transpose(cv2.resize(noise, (1400, 350)))
            fixedimg = np.concatenate((noise, fixingimg, noise), axis=1)
            allinvimgs.append(fixedimg)
            allbetaimgs.append(np.nan_to_num(new_imginvbeta))
    else:
        allinvimgs = np.load('allinvimgs.npy')
        allbetaimgs = np.load('allbetaimgs.npy')
        phasespots = np.load('phasespots.npy')

    analysisSize = 500
    dataphaselength = 3*np.pi
    imgphasefit = fit_sin(np.linspace(0,dataphaselength,len(phasespots)),phasespots)
    assignPhase = np.array([imgphasefit['amp']*np.sin(imgphasefit['omega']*i+imgphasefit['phase'])+imgphasefit['offset'] for i in np.linspace(-np.pi/2,np.pi/2,1000)])
    imgphaseAssignmentsIndex = np.array([find_nearest_index(np.abs(assignPhase),np.abs(phasespots[i])) for i in np.arange(0,len(phasespots))])
    phasenumbers = np.linspace(-np.pi/2,np.pi/2,1000)
    imgphasefinal = np.array([phasenumbers[i] for i in imgphaseAssignmentsIndex])
    inds = imgphasefinal.argsort()
    sortedphase = imgphasefinal[inds]
    allinvimgs = np.array(allinvimgs)
    resizedinv = np.array([cv2.resize(i,(analysisSize,analysisSize))[:,:int(analysisSize/2)] for i in allinvimgs])
    resizedbeta = np.array([cv2.resize(i,(analysisSize,analysisSize))[:,:int(analysisSize/2)] for i in allbetaimgs])
    #saveimg = np.concatenate((resizedinv[12],np.fliplr(resizedinv[12])),axis=1)
    #saveimg = saveimg/np.max(saveimg)
    #axiscalPy = np.sqrt(2*((saveimg.shape[0]/2*saveimg.shape[0]/2)/ (27.21*3660)))
    #axiscalPx = np.sqrt(2*((saveimg.shape[1]/2*saveimg.shape[1]/2)/ (27.21*3660)))
    #energycal = (np.arange(0,560)*np.arange(0,560))/3660
    #plt.plot(energycal,np.average(inverse_polarsave[:,505:515],axis=1)/np.max(np.average(inverse_polarsave[:,505:515],axis=1)))
    #plt.plot(energycal,np.average(inverse_polarsave[:,5:15],axis=1)/np.max(np.average(inverse_polarsave[:,5:15],axis=1)))
    #plt.yscale('log')
    #plt.show()
    sortedimgs = resizedinv[inds]
    sortedbetas = resizedbeta[inds]
    #for i in np.arange(0,len(sortedimgs)):
    #    for j in np.arange(0,sortedimgs[i].shape[1]):
    #        for k in np.arange(0,sortedimgs[i].shape[0]):
    #            if j>=25:
    #                sortedimgs[i][k][j] = sortedimgs[i][k][j]
    #            else:
    #                sortedimgs[i][k][j] = 1
    inputarrinv = [sortedbetas,sortedphase]
    phaseanalysis = []
    phaseanalysisoff = []
    dt = np.linspace(0,2*1.33,60)
    '''
    plt.scatter(np.linspace(0,dt[len(phasespots)],len(phasespots)),phasespots)
    betaimgfit = fit_sin(np.linspace(0,dt[len(phasespots)],len(phasespots)),phasespots)
    print(betaimgfit)
    print(np.diag(betaimgfit['rawres'][2]))
    plt.show()
    phaselike = np.zeros((50, 240))
    lineouts = []
    for m in np.arange(0,len(sortedbetas)):
        fullimg = np.concatenate((sortedimgs[m], np.fliplr(sortedimgs[m])), axis=1)
        pol = abel.tools.polar.reproject_image_into_polar(fullimg, Jacobian=True,origin=(analysisSize/2,analysisSize/2))[0]
        #damopimg = [np.average(abel.tools.polar.reproject_image_into_polar((np.concatenate((sortedbetas[i], np.fliplr(sortedbetas[i])), axis=1)), Jacobian=True,origin=(analysisSize/2,analysisSize/2))[0][:,m+10:m+15],axis=1) for i in np.arange(0,len(sortedbetas))]
        #damopimgbg = [np.average(abel.tools.polar.reproject_image_into_polar((np.concatenate((sortedbetas[i], np.fliplr(sortedbetas[i])), axis=1)), Jacobian=True,origin=(analysisSize/2,analysisSize/2))[0][:,m+120:m+125],axis=1) for i in np.arange(0,len(sortedbetas))]
        #plt.imshow(fullimg,norm=LogNorm(vmin=0.000001,vmax=0.02))
        #plt.show()
        #damopimg = np.transpose(np.array(damopimg))
        #damopimgbg = np.transpose(np.array(damopimgbg))
        #plt.imshow(damopimg,norm=LogNorm(vmin=0.000001,vmax=0.4),cmap=pqlx,interpolation='bilinear')
        #plt.show()
        #linearimg = linearize(damopimg)
        #linearimg = np.array(linearimg)
        #linearimg = cv2.resize(linearimg,pol.shape,interpolation=cv2.INTER_LINEAR)
        #linearimg = np.transpose(linearimg)
        #linearimgbg = linearize(damopimgbg)
        #linearimgbg = np.array(linearimgbg)
        #linearimgbg = cv2.resize(linearimgbg, pol.shape, interpolation=cv2.INTER_LINEAR)
        #linearimgbg = np.transpose(linearimgbg)
        linearinv = linearize(pol)
        linearinv = np.array(linearinv)
        linearinv = cv2.resize(linearinv, pol.shape, interpolation=cv2.INTER_LINEAR)
        linearinv = np.transpose(linearinv)
        linearinv = (np.abs(linearinv)/np.max(linearinv))
        #plt.plot((1/8)*np.arange(0,len(linearinv[:,10])),linearinv[:,10])
        #plt.yscale('log')
        #plt.show()
        fft2inv = np.fft.rfft2(linearinv,axes=((0,)))
        fft2invmask = np.abs((np.angle(gaussian_filter(fft2inv,1))))
        fft2invmask[fft2invmask < 0.7] = 100
        fft2invmask[fft2invmask > 2.6] = 100
        fft2invmask[fft2invmask < 99] = 0
        fft2inv[(fft2invmask)<99] = 0
        #plt.imshow(abs(np.fft.irfft2(fft2inv,axes=((0,)))),norm=LogNorm(vmin=0.0001,vmax=0.3),cmap=pqlx)
        #plt.show()
        #plt.plot(np.sum(abs(np.fft.irfft2(fft2inv,axes=((0,))))[170:260,:25],axis=1))
        #plt.show()
        featurelineout = np.sum(abs(np.fft.irfft2(fft2inv,axes=((0,))))[170:260,:25],axis=1)
        featurelineout = gaussian_filter(featurelineout,1)
        featurelineout = featurelineout/np.max(featurelineout)
        lineouts = np.append(lineouts,featurelineout)
        #plt.imshow(linearimg,norm=LogNorm(vmin=0.005,vmax=6),cmap=pqlx,interpolation='bilinear')
        #plt.show()
        #plt.plot(np.average(linearimg[:,0:5],axis=1))
        #plt.show()
        #damopimg = (np.abs(linearimg)/np.max(linearimg))
        #damopimgbg = (np.abs(linearimgbg)/np.max(linearimgbg))#*255
        #damopimg = scipy.ndimage.gaussian_filter1d(damopimg, 20, axis=1)
        #damopimgbg = scipy.ndimage.gaussian_filter1d(damopimgbg, 20, axis=1)
        #damopimg = damopimg[:230,:]
        #damopimgbg = damopimgbg[:230,:]
        #plt.imshow(damopimg,vmin=-0.0005,vmax=0.0005,cmap=pqlx,interpolation='bilinear')
        #plt.show()
        #fft2 = np.fft.rfft2(damopimg,axes=(0,))
        #fft2bg = np.fft.rfft2(damopimgbg,axes=(0,))
        #fft2 = (fft2/np.max(fft2))-(fft2bg/np.max(fft2bg))
        #time = np.linspace(0,fft2.shape[0])
        #W = gaussian_filter(fftfreq(fft2.shape[1], d=time[1] - time[0]),1)
        #Wx = gaussian_filter(fftfreq(fft2.shape[1], d=time[1] - time[0]),1)
        #Wy = fftfreq(fft2.shape[0], d=time[1] - time[0])
        #fft2 = gaussian_filter(fft2,3)
        #fft2[np.abs(Wy) < 0.008,:] = 0
        #fft2[np.abs(Wy) > 0.01,:] = 0
        #print('inverse')
        #fft2 = fft2/np.max(fft2)
        #fft2 = scipy.ndimage.gaussian_filter1d(fft2,5,axis=1)
        #processimg = abs(np.fft.irfft2(fft2,axes=(0,)))
        #processimg = processimg/np.max(processimg)
        #processimg = scipy.ndimage.gaussian_filter1d(processimg, 10, axis=0)
        #processimg = scipy.ndimage.gaussian_filter1d(processimg,5,axis=0)
        #plt.imshow(processimg[120:],norm=LogNorm(vmin=0.1,vmax=1),cmap='twilight',interpolation='bilinear',aspect=0.01,extent=[0,dt[49],230,120])
        #plt.show()
        #plt.plot(np.linspace(0,dt[len(phasespots)],500),gaussian_filter(np.sum(processimg[120:220],axis=0)/np.max(np.sum(processimg[120:220],axis=0)),30))
        #plt.show()
        #processimg = np.transpose(processimg)/np.max(processimg)
        #for i in np.arange(0,len(sortedbetas)):
        #    scaledlineout = np.exp(0.01*np.linspace(120,250,len(processimg[i,120:250])))*processimg[i,120:250]
        #    plt.plot(np.linspace(120,250,len(scaledlineout)),scaledlineout)
        #plt.show()
        for n in np.arange(0,1):
            try:
                parameters, covariance = curve_fit(gauss,np.linspace(170,260,len(featurelineout)),featurelineout,p0=[1,200,20],bounds=((0,170,-np.inf),(1.5,260,np.inf)),maxfev = 50000)
            except RuntimeError or RuntimeWarning:
                print("Error")
                parameters = [1, 1, 1]
                covariance = [1, 1, 1]
            #plt.plot(np.linspace(150,250,80),(np.exp(0.01*np.linspace(150,250,len(processimg[n,150:250])))*processimg[n,150:250])/np.max(np.exp(0.01*np.linspace(150,250,len(processimg[n,150:250])))*processimg[n,150:250]))
            #plt.show()
            #print(parameters)
            phaseanalysis = np.append(phaseanalysis, parameters[1])
            #phaseanalysisoff = np.append(phaseanalysisoff,find_nearest_index(processimg[n,:50],np.max(np.exp(0.01*np.linspace(0,50,len(processimg[n,0:50])))*processimg[n,:50])))

    #correctshift = (phaseanalysis[-1]-phaseanalysis[0])/len(phaseanalysis)
    #phaseanalysis = phaseanalysis-correctshift*np.arange(0,len(phaseanalysis))
    #correctshiftoff = (phaseanalysisoff[-1]-phaseanalysisoff[0])/len(phaseanalysisoff)
    #phaseanalysisoff = phaseanalysisoff-correctshiftoff*np.arange(0,len(phaseanalysis))

    #plt.plot(dt[:len(phasespots)],(phasespots/np.max(phasespots))*0.5)
    lineouts = lineouts.reshape((len(sortedbetas),int(len(lineouts)/len(sortedbetas))))
    oscsin = fit_sin(np.linspace(0,dt[49],len(phaseanalysis)),(1/8)*(phaseanalysis))
    plt.imshow(np.transpose(lineouts),extent=[0,dt[49],(1/8)*260,(1/8)*170])
    plt.scatter(np.linspace(0,dt[49],len(phaseanalysis)),(1/8)*(phaseanalysis))
    plt.plot(np.linspace(0,dt[49],len(phaseanalysis)),oscsin['amp'] * numpy.sin(oscsin['omega']*np.linspace(0,dt[49],len(phaseanalysis)) + oscsin['phase']) + oscsin['offset'])
    plt.show()
    print(oscsin)
    print(np.diag(oscsin['rawres'][2]))
    plt.plot(np.linspace(0,dt[len(sortedbetas)],len(phaseanalysis)),(1/8)*phaseanalysis,label='res')
    #phaseanalysis= phaseanalysis/np.max(phaseanalysis)
    #phaseanalysisoff = phaseanalysisoff/np.max(phaseanalysisoff)
    #plt.plot(dt[:len(phaseanalysis)], (phaseanalysisoff),label='off res')
    #plt.plot(dt[:len(phaseanalysis)], (np.abs(phaseanalysisoff-phaseanalysis) / np.max(np.abs(phaseanalysisoff-phaseanalysis)))-0.5,label='difference')
    plt.legend()
    plt.show()
    '''
    '''
    phaselike = np.transpose(phaselike)
    phaselike = np.concatenate((phaselike, np.fliplr(phaselike)), axis=1)
    phaselike = cv2.resize(phaselike, pol.shape )
    plt.imshow(phaselike,extent=[0,360,170,0],interpolation='bilinear')
    #plt.plot(np.linspace(0, 180, len(phaseanalysisoff)), phaseanalysisoff/np.max(phaseanalysisoff))
    plt.show()
    xyphaselike = cv2.resize(polar_linear(phaselike),(500,500))
    plt.imshow(xyphaselike,norm=LogNorm(vmin=0.00001,vmax=0.8),interpolation='bilinear')
    plt.show()
    #plt.imshow(oscimg,vmin=0.5,vmax=1.8,cmap=pqlx,aspect=0.005,extent=[np.min(sortedphase),np.max(sortedphase),np.array(damopimg).shape[1],0],interpolation='bilinear')
    #plt.colorbar()
    #plt.show()
    #axs[0].set_xlabel('Phase')
    #axs[0].set_ylabel('Momentum')
    #axs[1].plot(sortedphase,np.average(np.transpose(damopimg)[160-5:160+5],axis=0))
    #plt.show()
    #plt.plot(damopimg[0])
    #plt.show()
    #fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    #thetavsphase = [abel.tools.polar.reproject_image_into_polar(sortedbetas[i], origin=(analysisSize/2,analysisSize/2),Jacobian=True)[0][160]/np.max(abel.tools.polar.reproject_image_into_polar(sortedbetas[i],origin=(analysisSize/2,analysisSize/2), Jacobian=True)[0]) for i in np.arange(0,len(sortedimgs))]
    #axs[0].imshow(np.transpose(thetavsphase),vmin=-0.00003,vmax=0.00003,cmap=pqlx,aspect=0.005,extent=[np.min(sortedphase),np.max(sortedphase),360,0])
    #axs[0].set_xlabel('Phase')
    #axs[0].set_ylabel('Theta')
    #axs[1].plot(np.linspace(0,360,analysisSize),np.average(thetavsphase[17-1:17+1],axis=0))
    #plt.show()
    phasemap = extract_phase(inputarrinv)
    fullphaseimg = np.concatenate((phasemap,np.fliplr(phasemap)),axis=1)
    #plt.imshow(fullphaseimg,cmap='bwr',vmin=-np.pi/2,vmax=np.pi/2,extent=[-axiscalPx,axiscalPx,-axiscalPy,axiscalPy])
    #plt.colorbar()
    #plt.show()
    #plt.imshow(np.abs(fullphaseimg)-np.abs(fullphaseimg)[250,397],cmap='bwr',vmin=-0.5,vmax=0.5,extent=[-axiscalPx,axiscalPx,-axiscalPy,axiscalPy])
    #plt.show()
    plt.imshow(fullphaseimg,vmin=-0.25,vmax=0.25,cmap='bwr')
    plt.show()
    symmimgphasequads = abel.tools.symmetry.get_image_quadrants(fullphaseimg)
    symmimgphasequads = np.array([symmimgphasequads[0],symmimgphasequads[1],symmimgphasequads[2],symmimgphasequads[3]])
    symmimgphase = np.flipud(abel.tools.symmetry.put_image_quadrants(symmimgphasequads,(analysisSize,analysisSize),symmetry_axis=0))
    #plt.imshow(symmimgphase,cmap='bwr',vmin=0,vmax=np.pi/2)
    #plt.show()
    #plt.imshow(np.abs(symmimgphase)-np.abs(symmimgphase)[int(analysisSize/2),int(794/2)],cmap='bwr',vmin=-1,vmax=1)
    #plt.show()
    polarphase = abel.tools.polar.reproject_image_into_polar(np.abs(symmimgphase)-np.abs(symmimgphase)[int(analysisSize/2),int(794/2)],origin=(analysisSize/2,analysisSize/2), Jacobian=True)[0]
    polarphase = polarphase[:int(analysisSize/2),:]
    #plt.imshow(polarphase)
    #plt.show()
    findingpoints = [np.where(gaussian_filter(polarphase[:,i],8)==np.max(gaussian_filter(polarphase[:,i],8)[130:180]))[0][0] for i in np.arange(5,15)]
    findingpointstwo = [np.where(gaussian_filter(polarphase[:,i],8)==np.max(gaussian_filter(polarphase[:,i],8)[130:180]))[0][0] for i in np.arange(analysisSize-15,analysisSize-5)]
    findingpointsthree = [np.where(gaussian_filter(polarphase[:,i],8)==np.max(gaussian_filter(polarphase[:,i],8)[130:180]))[0][0] for i in np.arange(int(analysisSize/2)-15,int(analysisSize/2)-5)]
    findingpointsfour = [np.where(gaussian_filter(polarphase[:, i], 8) == np.max(gaussian_filter(polarphase[:, i], 8)[130:180]))[0][0]for i in np.arange(int(analysisSize / 2) + 5, int(analysisSize / 2) + 15)]
    thetas = np.linspace(0,360,analysisSize)
    plt.scatter(thetas[5:15],findingpoints,color='r')
    plt.scatter(thetas[analysisSize-15:analysisSize-5],findingpointstwo,color='r')
    plt.scatter(thetas[int(analysisSize/2)-15:int(analysisSize/2)-5],findingpointsthree,color='r')
    plt.scatter(thetas[int(analysisSize / 2) + 5:int(analysisSize / 2) + 15], findingpointsfour, color='r')
    plt.imshow(polarphase/np.max(polarphase),vmin=0,vmax=0.5,extent=[0,360,polarphase.shape[0],0])
    plt.show()
    #filter = np.abs(symmimgphase)
    #filterimg2 = filter
    #filter = fit_circle(filter)
    #filter[filter<=0.7]=0
    #filter[filter>=0.9]=0
    #filterimg2[filterimg2<=0.9]=0
    #filterimg2[filterimg2>=1.1]=0
    #quad1 = identify_circle(filter)
    #quad2 = identify_circle(filterimg2)
    #averageingquad = quad2+quad1
    #circlequads = np.array([np.fliplr(averageingquad),np.fliplr(averageingquad),np.fliplr(averageingquad),np.fliplr(averageingquad)])
    #circleimg = abel.tools.symmetry.put_image_quadrants(circlequads,(1000,1000))
    #plt.imshow(circleimg)
    #plt.show()
    coord = pol2cart(findingpoints,thetas[5:15]*np.pi/180)
    coordtwo = pol2cart(findingpointstwo,thetas[analysisSize-15:analysisSize-5]*np.pi/180) #np.where(circleimg>=100)
    coordthree = pol2cart(findingpointsthree, thetas[int(analysisSize/2)-15:int(analysisSize/2)-5] * np.pi / 180)
    coordfour = pol2cart(findingpointsfour, thetas[int(analysisSize / 2) + 5:int(analysisSize / 2) + 15] * np.pi / 180)

    bgimg = cv2.resize(allinvimgs[0],(analysisSize,analysisSize))
    bgimg = np.concatenate((bgimg[:,:int(analysisSize/2)],np.fliplr(bgimg[:,:int(analysisSize/2)])),axis=1)
    bgimg = bgimg/np.max(bgimg)
    xfit = coord[1]
    yfit = coord[0]
    xfit = np.append(xfit,coordtwo[1])
    yfit = np.append(yfit,coordtwo[0])
    #xfit = np.append(xfit,coordthree[1])
    #yfit = np.append(yfit,coordthree[0])
    #xfit = np.append(xfit,coordfour[1])
    #yfit = np.append(yfit,coordfour[0])
    #xfit = np.array([i for i in xfit if i+analysisSize/2 <= analysisSize-30])
    #yfit = np.array([i for i in yfit if i+analysisSize/2 <= analysisSize-30])
    xfit = np.append(xfit,0)
    yfit = np.append(yfit,0)
    plt.scatter(xfit+analysisSize/2,yfit+analysisSize/2,color='r')
    plt.imshow(bgimg,norm=LogNorm(vmin=0.001, vmax=0.3))
    plt.show()
    newxfit = []
    newyfit = []
    for i in np.arange(0,len(xfit)):
        if yfit[i]<=260:
            newxfit = np.append(newxfit,xfit[i])
            newyfit = np.append(newyfit,yfit[i])
    xyindx = newxfit.argsort()
    sortedx = newxfit[xyindx]
    sortedy = newyfit[xyindx]
    averagedx = []
    averagedy = []
    storagebin=[]
    for i in np.arange(1,len(newxfit)):
        if sortedx[i-1]==sortedx[i]:
            storagebin = np.append(storagebin,sortedy[i-1])
        if sortedx[i-1]!=sortedx[i]:
            averagedx=np.append(averagedx,sortedx[i-1])
            averagedy = np.append(averagedy,np.average(storagebin))
            storagebin=[]
    fitinput = [xfit,yfit]
    xc,yc,rfit,_ = cf.hyper_fit(np.transpose(fitinput))
    '''
    analysisSize = 500
    bgimg = cv2.resize(allinvimgs[0],(analysisSize,analysisSize))
    bgimg = np.concatenate((bgimg[:,:int(analysisSize/2)],np.fliplr(bgimg[:,:int(analysisSize/2)])),axis=1)
    bgimg = bgimg/np.max(bgimg)
    inverse_polar = abel.tools.polar.reproject_image_into_polar(np.abs(bgimg),Jacobian=True)[0]
    #dcspolar = abel.tools.polar.reproject_image_into_polar(np.abs(bgimg),origin=(yc+500,500),Jacobian=True)[0]
    #plt.imshow(dcspolar/np.max(dcspolar),norm=LogNorm(vmin=0.00001, vmax=0.3))
    #plt.show()
    #normdcs = gaussian_filter(dcspolar/np.max(dcspolar),4)
    #plt.plot(np.linspace(0,180,500),np.average(normdcs[int(rfit-(rfit*0.03)):int(rfit+(rfit*0.03))],axis=0)[:500])
    #plt.yscale('log')
    #plt.show()
    cut = int(analysisSize/2)
    x = np.arange(1, cut+1)
    def display_function(val):
        cut = int(analysisSize/2)
        constant = slider.val
        squares = (x * x) / (constant)
        slice_one_plot.set_ydata(
            np.average(np.transpose(inverse_polar)[int(slidertwo.val):int(slidertwo.val) + 10], axis=0)[:cut])
        slice_one_plot.set_xdata(squares[:cut])
        slice_two_plot.set_xdata(squares[:cut])
        slice_two_plot.set_ydata(np.average(np.transpose(inverse_polar)[
                                            int(slidertwo.val + int(inverse_polar.shape[1] / 2)):int(
                                                slidertwo.val + int(inverse_polar.shape[1] / 2) + 10)], axis=0)[:cut])
        slice_one_plot.axes.set_xbound(np.min(squares[:cut]), np.max(squares[:cut]) + 1)
        slice_two_plot.axes.set_xbound(np.min(squares[:cut]), np.max(squares[:cut]) + 1)
        lineout_line.set_xdata(int(slidertwo.val))
        lineout_line_two.set_xdata(int(slidertwo.val + int(inverse_polar.shape[1] / 2)))
        axs[1].set_yscale('log')
        fig.canvas.draw_idle()
        return
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    # CALIBRATION PLOTS
    inverted_image_disp = axs[0].imshow(inverse_polar, cmap=pqlx, vmin=0, vmax=10)
    lineout_line = axs[0].axvline(x=0, color='red')
    lineout_line_two = axs[0].axvline(x=int(inverse_polar.shape[1] / 2), color='red')
    slice_one_plot, = axs[1].plot(np.average(np.transpose(inverse_polar)[1:11][:cut], axis=0))
    slice_two_plot, = axs[1].plot(np.average(np.transpose(inverse_polar)[int(inverse_polar.shape[1] / 2):int(inverse_polar.shape[1] / 2) + 10][:cut],axis=0))
    xcoords = np.arange(1.57 / 2, 80, 1.57)
    axs[1].set_yscale('log')
    axs[1].autoscale('both')
    for xc in xcoords:
        axs[1].axvline(x=xc, color='red')
    # CREATE SLIDERS
    slider_ax = plt.axes([0.20, 0.0025, 0.60, 0.02])
    slider = Slider(slider_ax, "Constant", 500, 2000, valinit=1)
    slidertwo_ax = plt.axes([0.20, 0.025, 0.60, 0.02])
    slidertwo = Slider(slidertwo_ax, "Slice", 0, int(inverse_polar.shape[1] / 2), valinit=1)
    slider.on_changed(display_function)
    slidertwo.on_changed(display_function)
    plt.show()
    constant = slider.val

    #FORCE FIT
    rfit = (0.671*0.671)/2
    rfit = np.sqrt(rfit*(27.21*constant))
    print(rfit)
    yc= (0.631*0.631)/2
    yc = np.sqrt(yc*(27.21*constant))
    print(yc)
    xc=0

    plt.imshow(bgimg,cmap=pqlx, norm=LogNorm(vmin=0.001, vmax=0.3))
    #plt.scatter(xfit+analysisSize/2,yfit+analysisSize/2,color='green')
    circle1 = plt.Circle((analysisSize/2,yc+analysisSize/2),rfit, color='k', fill=False)
    plt.gca().add_patch(circle1)
    plt.colorbar()
    plt.show()
    print('in eV')
    print('r')
    print(rfit*rfit/constant)
    print('offset')
    print(yc*yc/constant)
    print('in momentum a.u.')
    print('Pr')
    prenergyau=((rfit * rfit) / (27.21*constant))
    prmomentumau = np.sqrt(2*prenergyau)
    print(prmomentumau)
    print('Ar')
    arenergyau=((yc) * (yc) / (27.21*constant))
    armomentumau= np.sqrt(2*arenergyau)
    print(armomentumau)
    Pr = np.sqrt(2*(rfit*rfit/constant))
    Ar = np.sqrt(2*(yc*yc/constant))
    #betas = np.array(betas)
    #inds = betas.argsort()
    #sortedimgs = allinvimgs[inds]
    #sortedbetas = np.sort(betas)
    phi = np.linspace(0, np.pi, len(sortedbetas))
    #plt.imshow(allbetaimgs[0],vmin=0,vmax=3)
    #plt.show()
    #plt.imshow(allinvimgs[0],vmin=100,vmax=10000)
    #plt.show()
    #np.save('phasemap030623.npy',phasemap)
    #phasemap = np.load('phasemap2.npy')
    #np.save('phasemap2.npy',phasemap)
    #fig, (ax1,ax2) = plt.subplots(1,2, figsize=(10, 10))
    #def animation(i):
    #    plt.style.use("ggplot")
    #    left = (allbetaimgs[i][:,:1000])
    #    right = (allinvimgs[i][:,:1000]/np.max(allinvimgs[i][:,:1000]))
    #    ax1.imshow(left,vmin=-0.4,vmax=0.4,cmap='seismic')
    #    ax1.axis('off')
    #    ax2.imshow(np.flip(right,axis=1),norm=LogNorm(vmin=0.001, vmax=1),cmap=pqlx)
    #    ax2.axis('off')
    #    fig.tight_layout()
    #constant = 133000
    #alpha = 0.004# slider.val #117067
    #energycalibration = x * x / constant
    #leftPoints = []
    #rightPoints = []
    #sigma = 1
    '''
    for i in np.arange(0, len(sortedbetas)):
        axs[0].scatter(phi[i], (sortedbetas[i]), color="red")
        daimg = sortedimgs[i]/np.max(sortedimgs[i])
        lineoutpolar = abel.tools.polar.reproject_image_into_polar(daimg,Jacobian=True)[0]
        averagelineR = np.average(np.transpose(lineoutpolar)[25:75],axis=0)
        averagelineL = np.average(np.transpose(lineoutpolar)[25+3000:75+3000],axis=0)
        filteredR = gaussian_filter((np.exp(x*alpha)*((averagelineR))),sigma)
        filteredL = gaussian_filter((np.exp(x*alpha)*((averagelineL))),sigma)
        if i==1 or i==len(betas)-1 or i == int(len(betas)/2):
            axs[1].plot(filteredR[:2800],label=str(np.round((sortedbetas[i]),3)))
            axs[2].plot(energycalibration[:2800],filteredL[:2800],label=str(np.round((sortedbetas[i]),3)))
        parametersR, covarianceR = curve_fit(gauss, np.arange(1500,2000),filteredR[1500:2000],p0=[15000,1800,500],bounds=((0,0,0),(30000,3000,2000)), maxfev=50000,method='trf')
        parametersL, covarianceL = curve_fit(gauss, np.arange(1500,2000),filteredL[1500:2000],p0=[15000,1800,500],bounds=((0,0,0),(30000,3000,2000)), maxfev=50000,method='trf')
        errorpercentR = np.diag(covarianceR)[1]/parametersR[1]
        errorpercentL = np.diag(covarianceL)[1]/parametersL[1]
        axs[3].errorbar(phi[i],energycalibration[int(parametersR[1])],color='blue',yerr=energycalibration[int(parametersR[1])]*errorpercentR,capsize=2,capthick=1)
        axs[3].errorbar(phi[i],energycalibration[int(parametersL[1])],color='green',yerr=energycalibration[int(parametersL[1])]*errorpercentL,capsize=2,capthick=1)
        axs[4].scatter(phi[i],np.diag(covarianceR)[1],color='blue')
        axs[4].scatter(phi[i],np.diag(covarianceL)[1],color='green')
        rightPoints.append(energycalibration[int(parametersR[1])])
        leftPoints.append(energycalibration[int(parametersL[1])])
        axs[0].set_ylabel('Phase')
        axs[0].set_xlabel('Image number')
        axs[3].set_ylim([25,35])
        axs[1].set_ylim([0,25000])
        axs[2].set_ylim([0,25000])
        axs[1].legend()
    paramL, covL = curve_fit(line,np.arange(0,len(leftPoints)),leftPoints)
    paramR, covR = curve_fit(line,np.arange(0,len(rightPoints)),rightPoints)

    axs[3].plot(np.linspace(0,np.pi,len(rightPoints)),rightPoints)
    axs[3].plot(np.linspace(0,np.pi,len(leftPoints)),leftPoints)
    print("left fit")
    print(paramL)
    print(np.diag(covL))
    print("right fit")
    print(paramR)
    print(np.diag(covR))
    plt.show(block=True)
    plt.close()
    '''

    axisshapeP = np.sqrt(2*((bgimg.shape[0]/2*bgimg.shape[0]/2)/ (27.21*constant)))
    axisshapePx = np.sqrt(2*((bgimg.shape[1]/2*bgimg.shape[1]/2)/ (27.21*constant)))
    plt.imshow(bgimg,cmap=pqlx, norm=LogNorm(vmin=0.001, vmax=0.3),extent=[-axisshapeP,axisshapeP,-axisshapeP,axisshapeP])
    #plt.scatter((averagedx-500),(500-averagedy),alpha = 0.5,s=4,color='green')
    circle1 = plt.Circle((0, armomentumau), prmomentumau, color='k', fill=False)
    plt.gca().add_patch(circle1)
    plt.colorbar()
    plt.show()
    Pr = 0.671
    Ar = 0.631
    listcolors = ['b','g','r','c','m','y','k','b','g','r','c','m','y','k','b','g','r','c','m','y','k','b','g','r','c','m','y','k','b','g','r','c','m','y','k','b','g','r','c','m','y','k','b','g','r','c','m','y','k']
    for i in np.arange(0,1):
        bgimg = cv2.resize(allinvimgs[i],(analysisSize,analysisSize))
        bgimg = np.concatenate((bgimg[:,:int(analysisSize/2)],np.fliplr(bgimg[:,:int(analysisSize/2)])),axis=1)
        bgimg = bgimg/np.max(bgimg)
        outimg,areasofbins = get_dcs(bgimg,Pr,Ar,0.03,constant,imgphasefinal[i],listcolors[i])
        #outimg,areasofbins = get_dcs(np.flipud(bgimg),Pr,Ar,0.03,constant,imgphasefinal[i],listcolors[i])#input values in eV
    plt.yscale('log')
    plt.show()

    plt.imshow(outimg,vmin=0,vmax=0.6, cmap=pqlx)
    for i in np.arange(2,len(areasofbins)):
        plt.scatter(areasofbins[i][1],areasofbins[i][0])
    #plt.scatter(outputextractx,outputextracty)
    #plt.scatter(outputupperpointsx,outputupperpointsy,color='black');plt.scatter(outputlowerpointsx,outputlowerpointsy,color='w');plt.scatter(outputextractx,outputextracty,color='r');plt.show()
    plt.show()
if __name__ == '__main__':
    main()
