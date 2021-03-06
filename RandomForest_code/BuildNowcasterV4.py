# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 11:06:36 2015

@author: adityanagarajan

Notes: Build the nowcaster such that we are making predictions using both radar fields and IPW fields(2 experiments)
1 hour in advanced.

"""


import os
import numpy as np
import DFWnet

from matplotlib import pyplot as plt

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import LeavePOut

from sklearn.cross_validation import KFold


def plotExperimentPoints(PixelPoints):
    gridX = np.arange(-150.0,151.0,300.0/(100-1))
    gridY = np.arange(-150.0,151.0,300.0/(100-1))
    tempMtx = np.zeros((100,100))
    tempMtx[PixelPoints] = 1.0
    tempMtx[tempMtx < 1.0] = np.nan
    xMesh,yMesh = np.meshgrid(gridX,gridY)
    
    tempMtx = np.ma.array(tempMtx, mask=np.isnan(tempMtx))
    
    print tempMtx

    plt.pcolor(xMesh,yMesh,tempMtx,cmap='jet',vmin=0.0, vmax=1.0)
    
    
    
DFW = DFWnet.CommonData()

TrainTestdir = 'data/TrainTest'

files = os.listdir(TrainTestdir)


IPWfiles = filter(lambda x: x[:7] == 'IPWdata' ,files)

Radarfiles = filter(lambda x: x[:9] == 'RadarRefl',files)

#Sort files DOY.hh
IPWfiles.sort(key = lambda x: float(x[7:10]) + float(x[x.index('_') + 1: x.index('.')]) * 0.01)

Radarfiles.sort(key = lambda x: float(x[9:12]) + float(x[x.index('_') + 1: x.index('.')])* 0.01)


# Pull out june data for now
IPWfiles = filter(lambda x: int(x[7:10]) < 152 or int(x[7:10]) > 181,IPWfiles)

Radarfiles = filter(lambda x: int(x[9:12]) < 152 or int(x[9:12]) > 181,Radarfiles)

# Pull out 205 >> 07/24
IPWfiles = filter(lambda x: int(x[7:10]) != 205, IPWfiles)

Radarfiles = filter(lambda x: int(x[9:12]) != 205,Radarfiles)


temp_list = []
for f in IPWfiles:
    if f[7:10] not in temp_list:
        temp_list.append(f[7:10])
        
print temp_list


for t in temp_list:
    DFW.doytodate(14,int(t))
    print t + ' >> ' + DFW.mon + '/' + DFW.day
    
thisList = ['IPWdata{0}_{1}.npy'.format(x,y) for x in temp_list for y in range(48)]

for L in thisList:
    if L not in IPWfiles:
        print L

# Set the thrashold for rain or not
Thrashold = 30.0


np.random.seed(12345)

# Enter the numper of test points -1 
nPoints = 19 
PixelX = np.random.uniform(20,80,size=(nPoints,)).astype(int)

PixelY = np.random.uniform(20,80,size=(nPoints,)).astype(int)


print PixelX[0]

print PixelY[0]

# Define the center
PixelPoints = np.array([49,49])

PixelPoints = PixelPoints.reshape(1,2)


print np.vstack((PixelX,PixelY)).T.shape

PixelPoints = np.concatenate((PixelPoints,np.vstack((PixelX,PixelY)).T))

plotExperimentPoints(PixelPoints)


# Generate the output vactor

Basefile = 'data/TrainTest/'

# Initialize the output matrix for each pixel for each time step in the 23 days
OutputMatrix = np.zeros((20,1104))

# Generate the matrix for the 20 points for all time steps (1104)
for f in range(len(Radarfiles)):
    
    RadarMatrix = np.load(Basefile + Radarfiles[f])
    
    RadarMatrix[np.isnan(RadarMatrix)] = 0.0
    
    RadarMatrix[RadarMatrix < Thrashold] = 0.0
    
    RadarMatrix[RadarMatrix >= Thrashold] = 1.0
    
    # Determine ground truth for each of the 20 pixel points
    for point in range(PixelPoints.shape[0]):
        OutputMatrix[point,f] = RadarMatrix[PixelPoints[point,:][0],PixelPoints[point,:][1]]

TrainTestDOY = []
for i in range(len(Radarfiles)):
    if IPWfiles[i][7:10] not in TrainTestDOY:
        TrainTestDOY.append(IPWfiles[i][7:10])

print TrainTestDOY



# 2. Use only IPW to for train and test

FeatureImportance = []
FeatureMatrix = np.zeros((1104,10000))

for i in range(len(Radarfiles)):
    
    RadarMatrix = np.load(Basefile + Radarfiles[i])
    
    RadarMatrix[np.isnan(RadarMatrix)] = 0.0
    
    IPWMatrix = np.load(Basefile + IPWfiles[i])
    
    
    FeatureMatrix[i,:] = IPWMatrix.reshape(-1,)

np.save('data/TrainTest/FeatureMatrix.npy',FeatureMatrix)
np.save('data/TrainTest/OutputMatrix.npy',)
#
#
#kf = KFold(1104, n_folds=6)
#
#rocScores = np.zeros((6,20))
#
#ctr1 = 0
#
#for train_index, test_index in kf:
#    ctr = 0
##    print("TRAIN:", train_index.shape, "TEST:", test_index.shape)
#
#    for px in range(OutputMatrix.shape[0]):
#        x = FeatureMatrix[:,:]
#    
#        y = OutputMatrix[3,:]
#        
#        x_train,x_test = x[train_index],x[test_index]
#        y_train,y_test = y[train_index],y[test_index]
#        
#        print x_train.shape,x_test.shape
#        print y_train.shape,y_test.shape
#        
#        mdl = RandomForestClassifier(n_estimators = 100,max_features = 5000,n_jobs=-1)
#        
#        mdl.fit(x_train,y_train)
#        
#        y_cap = mdl.predict_proba(x_test)
#        
#        FeatureImportance.append(mdl.feature_importances_)
#        
#        fpr,tpr,thrsh = roc_curve(y_test,y_cap[:,1])
#        if np.where(np.isnan(fpr))[0].size > 0 or np.where(np.isnan(tpr))[0].size > 0:
#            print 'No rain at all in this pixel (%d,%d) '%(PixelPoints[px,0],PixelPoints[px,1])
#            
#            roc_auc = np.nan
#        else:
#            roc_auc = auc(fpr,tpr)
#            print 'Train Test Split Number: %d %d) Area Under the curve for pixel point %d,%d = %f'%(ctr1,ctr,PixelPoints[px,0],PixelPoints[px,1],roc_auc)
#        rocScores[ctr1,ctr] = roc_auc
#        ctr+=1
#        
#    ctr1+=1


