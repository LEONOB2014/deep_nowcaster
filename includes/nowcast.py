# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 14:49:37 2015

@author: adityanagarajan
"""



import os
import numpy as np
from matplotlib import pyplot as plt
import re
import matplotlib.cm as cm

class BuildNowcaster():
    def __init__(self):
        self.base_dir = 'data/dataset/'
        self.domain_points = (range(17,83),range(17,83))
        self.reflectivity_scale = np.linspace(0.,90.,256)
        self.ipw_scale = np.linspace(-5.,5.,256)
        
    def sort_filter_files(self,PixelX,PixelY,doy_set):
        file_list = os.listdir(self.base_dir)
        file_list = filter(lambda x: x[-4:] == '.npy',file_list)


        PixelPoints = [(x,y) for x in PixelX for y in PixelY]

        PixelPoints = np.array(PixelPoints)

        # Filter top left of the domain
        domain_list = filter(lambda x: int(re.findall('\d+',x)[0]) in np.unique(PixelPoints[:,0]) and int(re.findall('\d+',x)[1]) in np.unique(PixelPoints[:,1]),file_list)
        domain_list.sort(key = lambda x: int(x[-7:-4]))

        ipw_files = filter(lambda x: x[:3] == 'IPW',domain_list)

        radar_files = filter(lambda x: x[:5] == 'Radar',domain_list)
    
        ipw_files = filter(lambda x: x[-7:-4] == doy_set,ipw_files)

        radar_files = filter(lambda x: x[-7:-4] == doy_set,radar_files)
    
        return ipw_files,radar_files
    
    def plot_domain(self,PixelPoints,marker = 'r*'):
        PixelPoints = PixelPoints.reshape(-1,2)
        gridX = np.arange(-150.0,151.0,300.0/(100-1))
        gridY = np.arange(-150.0,151.0,300.0/(100-1))
        # Loop through each pair to plot on the grod
        for p in PixelPoints:
            plt.plot(gridX[p[0]],gridY[p[1]],marker)

        plt.xlabel('Easting')
    
        plt.ylabel('Northing')

        plt.xlim((-150.0,150.0))

        plt.ylim((-150.0,150.0))
        plt.grid()
    
    def plot_fields_side(self,ipw_file,refl_file,PixelPoints):
        PixelPoints = PixelPoints.reshape(-1,2)
        m = 100
        gridIPW = np.load(ipw_file)
        gridZ = np.load(refl_file)
        gridX = np.arange(-150.0,151.0,300.0/(m-1))
        gridY = np.arange(-150.0,151.0,300.0/(m-1))
#        gridZ[gridZ < 20.0] = np.nan
        gridZ = np.ma.array(gridZ, mask=np.isnan(gridZ))
        plt.figure()
        plt.subplot(1,2,1)
        plt.pcolor(gridX,gridY,gridZ,cmap='jet', vmin=0, vmax=60)
        for p in PixelPoints:
            plt.plot(gridX[p[0]],gridY[p[1]],'r*')
        plt.grid()
        plt.xlim((-150.0,150.0))
        plt.ylim((-150.0,150.0))
        plt.subplot(1,2,2)
        plt.pcolor(gridX,gridY,gridIPW,cmap='gist_ncar', vmin=-3.0, vmax=3.0)
        for p in PixelPoints:
            plt.plot(gridX[p[0]],gridY[p[1]],'r*')
        plt.grid()
        plt.xlim((-150.0,150.0))
        plt.ylim((-150.0,150.0))
    
    def plot_field_slices(self,ipws_img,refls_img,ipws,refls,grid_point):
        x_ = grid_point[0]
        y_ = grid_point[1]
        gridX = np.arange(-150.0,151.0,300.0/(100-1))
        gridY = np.arange(-150.0,151.0,300.0/(100-1))
        gridIPW = np.zeros((100,100))
#        i_start = x_ -16
#        i_end = x_ + 17
#        j_start = y_ -16
#        j_end = y_ + 17
        
        x_range_start = gridX[x_] - 16.0*(300.0/99.0)
        y_range_start = gridY[y_] - 16.0*(300.0/99.0)
        x_range_end = gridX[x_] + 17.0*(300.0/99.0)
        y_range_end = gridY[y_] + 17.0*(300.0/99.0)
        
        gridX_ = np.arange(x_range_start,x_range_end,300./99.)
        gridY_ = np.arange(y_range_start,y_range_end,300./99.)
        plt.figure()
        for pl in range(1,5):
            plt.subplot(2,4,pl)
            plt.pcolor(gridX_,gridY_,ipws[pl-1,...],cmap='gist_ncar', vmin=-3.0, vmax=3.0)
            plt.xlim((-150.0,150.0))
            plt.ylim((-150.0,150.0))
            plt.grid()
            plt.subplot(2,4,pl + 4)
            plt.pcolor(gridX_,gridY_,refls[pl-1,...],cmap='jet', vmin=0, vmax=60)
            plt.xlim((-150.0,150.0))
            plt.ylim((-150.0,150.0))
            plt.grid()
        plt.figure()
        for pl in range(1,5):
            plt.subplot(2,4,pl)
            plt.imshow(ipws_img[pl-1,...], cmap = cm.Greys_r)
            plt.subplot(2,4,pl+4)
            plt.imshow(refls_img[pl-1,...], cmap = cm.Greys_r)
    
    def plot_predictions(self,movie_points,save_fige=True):
        gridX = np.arange(-150.0,151.0,300.0/(100-1))
        gridY = np.arange(-150.0,151.0,300.0/(100-1))
        # Define center point of the domain
        x_ = 49.0
        y_ = 49.0
        # Slice the central 66x66 grid
        x_range_start = gridX[x_] - 33.0*(300.0/99.0)
        y_range_start = gridY[y_] - 33.0*(300.0/99.0)
        x_range_end = gridX[x_] + 33.0*(300.0/99.0)
        y_range_end = gridY[y_] + 33.0*(300.0/99.0)
        
        gridX_ = np.arange(x_range_start,x_range_end,300./99.)
        gridY_ = np.arange(y_range_start,y_range_end,300./99.)
        
        time_index = ['{0}{1}'.format(str(x).zfill(2),str(y).zfill(2)) for x in range(24) for y in [0,30]]
        
        for x_ in range(91):
            plt.figure()
            plt.subplots(1,2)
            plt.subplot(121)
            real_ = movie_points[:,:,x_,0]
            predicted_ = movie_points[:,:,x_,1]
            real_[real_ < 20.0] = np.nan
            predicted_[predicted_ < 20.0] = np.nan
            real_ = np.ma.array(real_, mask=np.isnan(real_))
            predicted_ = np.ma.array(predicted_, mask=np.isnan(predicted_))
            plt.pcolor(gridX_,gridY_,real_.T,cmap='jet', vmin=0.0, vmax=50.0)
            plt.xlim((-150.0,150.0))
            plt.ylim((-150.0,150.0))
            plt.grid()
            plt.subplot(122)
            plt.pcolor(gridX_,gridY_,predicted_.T,cmap='jet', vmin=0.0, vmax=50.0)
            plt.xlim((-150.0,150.0))
            plt.ylim((-150.0,150.0))
            plt.grid()
    
            plt.suptitle('Actual and predicted fields for may 9th ' + time_index[x_ - 43] + ' UTC')
            if save_fige:
                plt.savefig('output/prediction_movies/Plot_' + str(x_) + '.png')


    def plot_ipw_refl_fields_overlap(self,gridIPW,gridZ):
        m = 100
        gridX = np.arange(-150.0,151.0,300.0/(m-1))
        gridY = np.arange(-150.0,151.0,300.0/(m-1))
        xMesh,yMesh = np.meshgrid(gridX,gridY)
        gridZ = np.ma.array(gridZ, mask=np.isnan(gridZ))
        plt.figure()
        plt.pcolor(gridX,gridY,gridIPW,cmap='gist_ncar', vmin=-4.0, vmax=4.0)
        cbar = plt.colorbar()
        cbar.set_label('Normalized IPW vals')
        
        plt.pcolor(gridX,gridY,gridZ,cmap='jet', vmin=10, vmax=60)
        cbar = plt.colorbar()
        cbar.set_label('Radar reflectivity')
        plt.grid()
        plt.xlim((-150.0,150.0))
        plt.ylim((-150.0,150.0))
        plt.xlabel('Easting (km)')
        plt.ylabel('Northing (km)')
        plt.show()



'''
raw_data_base_dir = '/Users/adityanagarajan/Summer_2015/ConvectiveInitiation/data/TrainTest/'


movie_points = np.load('data/NB_real_predictions.npy')


ipw = np.load(raw_data_base_dir + 'IPWdata128_9.npy')
refl = np.load(raw_data_base_dir + 'RadarRefl128_9.npy')


refl[refl < 24.0] = np.nan

refl = np.ma.array(refl, mask=np.isnan(refl))

movie_points = movie_points.reshape(4356,91,2)

print movie_points.shape

movie_points = movie_points.reshape(66,66,91,2)

gridX = np.arange(-150.0,151.0,300.0/(100-1))
gridY = np.arange(-150.0,151.0,300.0/(100-1))

plt.figure()
plt.pcolor(gridX,gridY,ipw,cmap='jet', vmin=-3.0, vmax=3.0)

plt.pcolor(gridX,gridY,refl,cmap='jet', vmin=10, vmax=60)

plt.grid()
plt.xlim((-150.0,150.0))

plt.ylim((-150.0,150.0))
plt.show()

gridIPW = np.zeros((66,66))
gridZ = np.zeros((66,66))
out_point = np.zeros((100,100))


gridIPW[:] = np.nan
gridZ[:] = np.nan



x_ = 49.0
y_ = 49.0

x_range_start = gridX[x_] - 33.0*(300.0/99.0)
y_range_start = gridY[y_] - 33.0*(300.0/99.0)

x_range_end = gridX[x_] + 33.0*(300.0/99.0)
y_range_end = gridY[y_] + 33.0*(300.0/99.0)

gridX_ = np.arange(x_range_start,x_range_end,300./99.)
gridY_ = np.arange(y_range_start,y_range_end,300./99.)

plt.figure()

i_start = x_ -33
i_end = x_ + 33
j_start = y_ - 33
j_end = y_ + 33


gridIPW[:] = ipw[j_start:j_end,i_start:i_end]

gridZ[:] = refl[j_start:j_end,i_start:i_end]

gridZ = np.ma.array(gridZ, mask=np.isnan(gridZ))

#plt.pcolor(gridX_,gridY_,gridIPW,cmap='jet', vmin=-3.0, vmax=3.0)
#plt.pcolor(gridX_,gridY_,gridZ,cmap='jet', vmin=10.0, vmax=60.0)
#
#
#plt.grid()
#plt.xlim((-150.0,150.0))
#plt.ylim((-150.0,150.0))
#plt.show()
time_index = ['{0}{1}'.format(str(x).zfill(2),str(y).zfill(2)) for x in range(24) for y in [0,30]]


for x_ in range(43,91):
    plt.figure()
    plt.subplots(1,2)
    plt.subplot(121)
    real_ = np.ma.array(movie_points[:,:,x_,0], mask=movie_points[:,:,x_,0] == 0.)
#    plt.pcolor(gridX_,gridY_,real_[:,:,x_,0].T,cmap='jet', vmin=0.0, vmax=1.0)
    plt.pcolor(gridX_,gridY_,real_.T,cmap='RdGy', vmin=0.0, vmax=1.0)
    plt.xlim((-150.0,150.0))
    plt.ylim((-150.0,150.0))
    plt.grid()
    plt.subplot(122)
    predicted_ = np.ma.array(movie_points[:,:,x_,1], mask=movie_points[:,:,x_,1] == 0.)
#    plt.pcolor(gridX_,gridY_,predicted_[:,:,x_,1].T,cmap='jet', vmin=0.0, vmax=1.0)
    plt.pcolor(gridX_,gridY_,predicted_.T,cmap='RdGy', vmin=0.0, vmax=1.0)
    plt.xlim((-150.0,150.0))
    plt.ylim((-150.0,150.0))
    plt.grid()
    
    plt.suptitle('Actual and predicted fields for may 9th ' + time_index[x_ - 43] + ' UTC')
    
    plt.savefig('output/prediction_movies/Naive_Bayes/Plot_' + str(x_) + '.png')
    


'''

        
        



