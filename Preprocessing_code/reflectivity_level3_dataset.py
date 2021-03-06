# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 13:19:09 2016

@author: adityanagarajan
This script makes the radar data set for the nowcasting experiments. 
After downloading the files thru bulk order from the NCDC (http://www.ncdc.noaa.gov/nexradinv/)
archive onto a folder, this file will take all the relevent files and DELETE the 
rest. 
"""

import numpy as np
import os
import DFWnet
import subprocess
import ftplib
from netCDF4 import Dataset
import BuildDataSet

DFW = DFWnet.CommonData()
Months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

def GetNEXRADfile(mon,day,yr,order_id = 'HAS010640668'):
    file_to_get = 'NWS_NEXRAD_NXL3_KFWS_20' +yr + mon + day + '000000_20' + yr + mon + day + '235959.tar.gz'
    ftp_NEXRAD = ftplib.FTP('ftp.ncdc.noaa.gov','anonymous','adi@gmail.com')  
    ftp_NEXRAD.cwd('pub/has' + os.sep + order_id + os.sep)
    file_list = ftp_NEXRAD.nlst()
    if file_to_get in file_list:
        print 'We Going to get that file: ' + file_to_get
        gfile = open(file_to_get,'wb')
        ftp_NEXRAD.retrbinary('RETR ' + file_to_get,gfile.write)
        gfile.close()
    else:
        print 'FATAL: File not found ' +  file_to_get
    ftp_NEXRAD.close()
    subprocess.call(['tar','-xvzf',file_to_get])
    subprocess.call(['rm',file_to_get])
    
def extract_reflectivity_files(doy,yr):
    ''' This function moves the relevant files and untars them to the 
    specific directiry YYYY/MONDD'''
    # common name of Level 3 reflectivity products at 0.5 VCP
    # KFWD_SDUS54_N0RFWS_201405230003.nc --> may 23rd 2014
    # NWS_NEXRAD_NXL3_KFWS_20140501000000_20140501235959.tar.gz
    # /Users/adityanagarajan/projects/nowcaster/data/RadarData/NEXRAD/2014/raw_files/
    base_path = '../data/RadarData/NEXRAD/20' + str(yr) + '/raw_files/'
    DFW.doytodate(int(yr),doy)
#    print '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day
    new_dir = '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day
    if not os.path.exists(new_dir):
        file_token = '20' + str(yr) + DFW.mon + DFW.day
        file_list = os.listdir(base_path)
        file_list = filter(lambda x: x[-7:] == '.tar.gz',file_list)
        print file_token
        temp_file = filter(lambda x: file_token in x,file_list)
        print temp_file
        os.mkdir('../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day)
        subprocess.call(['cp',base_path + temp_file[0],new_dir])
        # Get the initial directory that we were in
        initial = os.getcwd()
        # Move into the directory of the day folder to extract the level3 products
        os.chdir('../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day + os.sep)
        subprocess.call(['tar','-xzvf',temp_file[0]])
        print os.getcwd()        
        print temp_file[0]
        os.chdir(initial)

def find_closest_radar_data(t,files):
    '''This function finds the closest file to that particular hour'''
    hr = t[:2]
    mn = t[-2:]
    # If there is a .nc extension in the end strip it
    if files[0][-3:] == '.nc':
        files = map(lambda x: x.strip('.nc'), files)
    temp_file = filter(lambda x: x[27:29] == hr,files)
    # Find the closest file to the given time stame (up to 5 minutes ahead is fine)
    if mn == '30':
        the_file = filter(lambda x: int(x[-4:][-2:])  >= int(mn) -13  and int(x[-4:][-2:]) <= int(mn) + 13,temp_file)
        the_file.sort(key = lambda x: abs(int(x[-4:][-2:]) - int(mn)))
        
    else:
        temp_file = filter(lambda x: x[-4:][:2] == hr or x[-4:][:2] == str(int(hr) -1).zfill(2),files)       
        the_file = filter(lambda x: 
            int(x[-4:][:2] == str(int(hr) -1).zfill(2) and int(x[-4:][-2:]) >= 50  or (x[-4:][:2] == hr and int(x[-4:][-2:])  >= int(mn)  and int(x[-4:][-2:]) <= int(mn) + 20)),
                temp_file)
        the_file.sort(key = lambda x: abs((float(x[-4:][:2]) + float(x[-4:][-2:])/60.0) - int(hr) ))
    file_to_return = []
    if len(the_file) > 0:
        file_to_return = the_file[0]
    else:
        print 'WARNING: Missing File for time --> '  + t
    return file_to_return

def find_closest_radar_data_averages(t,files):
    '''This function returns the the set of files from the first 30 minutes and 
    second 30 minutes for each hour'''
    hr = t[:2]
    # If there is a .nc extension in the end strip it
    if files[0][-3:] == '.nc':
        files = map(lambda x: x.strip('.nc'), files)
    temp_file = filter(lambda x: x[27:29] == hr,files)
    # Find the closest file to the given time stame (up to 5 minutes ahead is fine)
    temp_file_first30 = filter(lambda x: int(x[-2:]) < 30,temp_file)
    temp_file_last30 = filter(lambda x: int(x[-2:]) > 30,temp_file)
    return temp_file_first30,temp_file_last30


def KeepRequiredFiles(doy,yr):
    DFW.doytodate(int(yr),doy)
    file_path = '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day
    file_list = os.listdir(file_path)
    files_to_keep = []
    time_index = ['{0}{1}'.format(str(x).zfill(2),str(y).zfill(2)) for x in range(24) for y in [0,30]]
    delete_files = filter(lambda x: x[:18] != 'KFWD_SDUS54_N0RFWS',file_list)
    # We only want the scan at the 0.5deg VCP, thus we are goint to delete the rest
    for df in delete_files:
        os.remove(file_path + os.sep + df)
    file_list = filter(lambda x: x[:18] == 'KFWD_SDUS54_N0RFWS',file_list)
    # We are noe going to find the closest file to 00 and 30 and obtain 48 such 
    # nexrad files
    
    for t in range(48):
        files_to_keep.append(find_closest_radar_data(time_index[t],file_list))
    return files_to_keep

def Deletefiles(doy,yr,keep_files):
    '''Delete all the files which are not required'''
    DFW.doytodate(int(yr),doy)
    file_path = '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day + os.sep
    file_list = os.listdir(file_path)
    for f in file_list:
        if f not in keep_files:
            print file_path + f
            os.remove(file_path + f)

def ConvertToNETCDF(doy,yr,keep_files):
    '''Use the java toolsUI-4.6.jar to convert to .nc files'''
    DFW.doytodate(int(yr),doy)
    java_script = 'toolsUI-4.6.jar'
    ucar = 'ucar.nc2.FileWriter'
    file_path = '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day + os.sep
    for raw_file in keep_files:
        temp_in = file_path + raw_file
        temp_out = file_path + raw_file + '.nc'
        subprocess.call(['java','-classpath',java_script,ucar,'-in',temp_in,'-out',temp_out,])
        # remove the raw file we only need .nc
        os.remove(file_path + raw_file)


def cart2pol(x,y):
    r = np.sqrt(np.power(x,2) + np.power(y,2))
    theta = np.degrees(np.arctan2(y,x))
    return theta,r

def reflectivity_polar_to_cartesian(rad):
    m = 100
    # Initialize an empty array to hold the reflectivity values in the cartesian coordinates
    gridZ = np.empty((m,m))
    gridZ.fill(np.nan)

    # Make the 150x150 km2 grid
    gridX = np.arange(-150.0,151.0,300.0/(m-1))
    gridY = np.arange(-150.0,151.0,300.0/(m-1))

    xMesh,yMesh = np.meshgrid(gridX,gridY)
    xMesh,yMesh = np.meshgrid(gridX,gridY)
    
    gridA,gridR = cart2pol(xMesh,yMesh)
    gridA[gridA < 0.0] = 360.0 + gridA[gridA < 0.0]
    
    # Get the vector of azimuth angles
    azimuthVector = rad.variables['azimuth'][:]

    # Get the range gates
    rangeVector = rad.variables['gate'][:]

    startRange = rangeVector[0]

    gateWidth = np.median(np.diff(rangeVector))

    startRange = startRange /1000.0
    gateWidth = gateWidth / 1000.0

    # Get the level 3 products
    Z = rad.variables['BaseReflectivity'][:]
    
    for a in range(azimuthVector.size):
        
        I = np.less(np.abs(gridA - azimuthVector[a]),1.0)
    
        J = np.floor(((gridR[np.abs(gridA - azimuthVector[a]) < 1.0] - startRange)/gateWidth ))
    
        gridZ[I] = Z[a,tuple(J)]
    
    return gridZ.T


def getNEXRADFile(doy,yr):
    '''Returns net cdf object for a particular year and day'''
    DFW.doytodate(yr,int(doy))
    NEXRAD_Folder = '../data/RadarData/NEXRAD/20'+ str(yr) + os.sep  + Months[int(DFW.mon) - 1] + DFW.day
    files = os.listdir(NEXRAD_Folder)
    files = filter(lambda x: x[-3:] == '.nc',files)
    files.sort(key = lambda x: int(x[-7:-3]))
    temp_list = []
    time_index = ['{0}{1}'.format(str(x).zfill(2),str(y).zfill(2)) for x in range(24) for y in [0,30]]
    for t in range(48):
        temp_file = find_closest_radar_data_averages(time_index[t],files)
        print temp_file[1]
#    for f in files:
#        rad = Dataset(NEXRAD_Folder  + os.sep + f)
#        Z = reflectivity_polar_to_cartesian(rad)
#        print Z.shape
#    print min(temp_list),max(temp_list)
#    return files[t],rad

def get30minuteaverages(doy,yr):
    '''Returns the average reflectivity for each 30 minute interval'''
    DFW.doytodate(yr,int(doy))
    half_hour_means = np.zeros((48,100,100))
    
    NEXRAD_Folder = '../data/RadarData/NEXRAD/20'+ str(yr) + os.sep  + Months[int(DFW.mon) - 1] + DFW.day
    files = os.listdir(NEXRAD_Folder)
    files = filter(lambda x: x[-3:] == '.nc',files)
    files.sort(key = lambda x: int(x[-7:-3]))
#    time_index = ['{0}{1}'.format(str(x).zfill(2),str(y).zfill(2)) for x in range(24) for y in [0,30]]
    time_index = ['{0}00'.format(str(x).zfill(2)) for x in range(24)]
    hour_ctr = 0
    for t in range(24):
        temp_files = find_closest_radar_data_averages(time_index[t],files)
    
        for bl in range(len(temp_files)):
            half_hour_array = np.zeros((len(temp_files[bl]),100,100))
            for ctr,fl in enumerate(temp_files[bl]):
                rad = Dataset(NEXRAD_Folder  + os.sep + fl + '.nc')
                Z = reflectivity_polar_to_cartesian(rad)
                half_hour_array[ctr] = Z
            half_hour_array[np.isnan(half_hour_array)] = 0.
            half_hour_array[half_hour_array < 0.0] = 0.0
            half_hour_means[hour_ctr,...] = np.mean(half_hour_array,axis = 0)
            hour_ctr+=1
    return half_hour_means

def det30minuteDecimated(doy,yr):
    '''Returns net cdf object for a particular year and day'''
    DFW.doytodate(yr,int(doy))
    day_array = np.zeros((48,100,100))
    NEXRAD_Folder = '../data/RadarData/NEXRAD/20'+ str(yr) + os.sep  + Months[int(DFW.mon) - 1] + DFW.day
    files = os.listdir(NEXRAD_Folder)
    files = filter(lambda x: x[-3:] == '.nc',files)
    files.sort(key = lambda x: int(x[-7:-3]))
    temp_list = []
    time_index = ['{0}{1}'.format(str(x).zfill(2),str(y).zfill(2)) for x in range(24) for y in [0,30]]
    for t in range(48):
        temp_file = find_closest_radar_data(time_index[t],files)
        rad = Dataset(NEXRAD_Folder  + os.sep + temp_file + '.nc')
        Z = reflectivity_polar_to_cartesian(rad)
        Z[np.isnan(Z)] = 0.
        Z[Z < 0.] = 0.
        day_array[t,...] = Z
    return day_array

    

def check_refl_files(new_dir):
    file_list = os.listdir(new_dir)
    file_list = filter(lambda x: x[-3:] == '.nc',file_list)
    print 'The number of files in dir: %s = %d'%(new_dir,len(file_list))
    
def main(yr):
    initial = os.getcwd()
    order_dict = {}
    order_dict[14] = 'HAS010799558'
    order_dict[15] = 'HAS010798151'
    order_dict[16] = 'HAS010796528'
    if yr == 14:
        storm_dates = np.load('../data/storm_dates_2014.npy').astype('int')
        # The following 3 dates are going to be removed because we do not
        # have NEXRAD files for the entire day            
        idx1 = np.where(np.all(storm_dates == [205,  14,   7,  24],axis=1))[0][0]
        storm_dates = np.delete(storm_dates,idx1,axis = 0)
        idx2 = np.where(np.all(storm_dates == [176,  14,   6,  25],axis=1))[0][0]
        storm_dates = np.delete(storm_dates,idx2,axis = 0)
        idx3 = np.where(np.all(storm_dates == [204 , 14 ,  7 , 23],axis=1))[0][0]
        storm_dates = np.delete(storm_dates,idx3,axis = 0)
        idx4 = np.where(np.all(storm_dates == [142 , 14 ,  5 , 22],axis=1))[0][0]
        storm_dates = np.delete(storm_dates,idx4,axis = 0)
    elif yr == 15:
        storm_dates = np.load('../data/storm_dates_2015.npy').astype('int')
        storm_dates = storm_dates
    elif yr == 16:
        storm_dates = np.load('../data/storm_dates_2016.npy').astype('int')
    for d in storm_dates:
        print d
        DFW.doytodate(int(yr),d[0])
        new_dir = '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        os.chdir(new_dir)
        GetNEXRADfile(DFW.mon,DFW.day,DFW.yr,order_id = order_dict[yr])
        os.chdir(initial)
        nexrad_files = KeepRequiredFiles(d[0],yr)
        # This commented code here delets the files which are inbetween 
        # 00 and 30. 
        Deletefiles(d[0],yr,nexrad_files)
##        DFW.doytodate(int(yr),d[0])
##        file_path = '../data/RadarData/NEXRAD/20' + str(yr) + os.sep + Months[int(DFW.mon) -1] + DFW.day + os.sep
##        nexrad_files = os.listdir(file_path)
        ConvertToNETCDF(d[0],yr,nexrad_files)
#        check_refl_files(new_dir)
#        decimated = det30minuteDecimated(d[0],yr)        
#        averages = get30minuteaverages(d[0],yr)
#        np.save('../data/RadarData/Decimated/' +str(d[1]) + str(d[0]) + 'refl_decimated.npy',decimated)
#        np.save('../data/RadarData/Averages/' + str(d[1]) + str(d[0]) + 'refl_averages.npy',averages)

if __name__ == '__main__':
    yr = [16]
    data_builder = BuildDataSet.dataset(num_points = 500)
    pixels = data_builder.sample_random_pixels()
    for y in yr:
        main(y)