#! /usr/bin/env python
#coding=utf-8
'''
This is a support library for 
Two-tensor Model Visualization Extension Module for 3D Slicer.

It draws tubes using fiber tracts data.

Wenyao Zhang
School of Computer Science, Beijing Institute of Technology
zhwenyao@bit.edu.cn
2014.9-2015.6
'''

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np

from PolyDataLib import *

#==============================================================================
# crossProduct(a,b) 
# calculate the cross product of two 3D vectors.
#==============================================================================
def crossProduct(a,b):
    c=[0,0,0]
    c[0] = b[2]*a[1] - b[1]*a[2]
    c[1] = b[0]*a[2] - b[2]*a[0]
    c[2] = b[1]*a[0] - b[0]*a[1]
    return c

#==============================================================================
# RenderTubeWithCustomColors(inpd,lineNum,params)
# params: contains the required tube color and tube size information.
# Here it shares the color settings with the cylinder body.
#==============================================================================
def RenderTubeWithCustomColors(inpd,lineNum,params):
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    slices=int(params['tubeSlices'])
    
    pidList = vtk.vtkIdList()
    if lineNum>inpd.GetNumberOfLines:
        lineNum=inpd.GetNumberOfLines
        
    inlines = inpd.GetLines()
    inlines.InitTraversal();
    for lidx in range(0,lineNum):
        inlines.GetNextCell(pidList)
     
    if pidList.GetNumberOfIds() < 2:
        return
    
    # obtain color infor
    bodRArray=GetPointArrayByName(inpd,params['bodRName'])
    bodGArray=GetPointArrayByName(inpd,params['bodGName'])
    bodBArray=GetPointArrayByName(inpd,params['bodBName'])
    bodAArray=GetPointArrayByName(inpd,params['bodAName'])
    
    bodRmin,bodRmax=GetMinMaxInArray(bodRArray)
    bodGmin,bodGmax=GetMinMaxInArray(bodGArray)
    bodBmin,bodBmax=GetMinMaxInArray(bodBArray)
    bodAmin,bodAmax=GetMinMaxInArray(bodAArray)
    
    # obtain size info
    sizeArray=GetPointArrayByName(inpd,params['tubeMappedToName'])
    sizeMin,sizeMax=GetMinMaxInArray(sizeArray)
    
    # Initial for the first point
    # build the unitnormal for the first point
    p0=GetPointPos(inpd,pidList.GetId(0))
    p1=GetPointPos(inpd,pidList.GetId(1))
    
    a = np.array(p1)-np.array(p0)
    b = [0,0,1]
    c = crossProduct(a,b);
    if c[0]==0.0 and c[1]==0.0 and c[2]==0.0:
       b = [1,0,0];
       c = crossProduct(a,b);
    
    b = crossProduct(c,a)
    norm = np.linalg.norm(b)
    if norm<>0:
       b[0] = b[0]/ norm
       b[1] = b[1]/ norm
       b[2] = b[2]/ norm
    
    N0=b # unitnormal
    T0=np.array(p1)-np.array(p0)
    norm = np.linalg.norm(T0)
    if norm<>0:
       T0[0] = T0[0]/norm
       T0[1] = T0[1]/norm
       T0[2] = T0[2]/norm
    B0=crossProduct(T0,N0)
    
    for i in range(1,pidList.GetNumberOfIds()):
        # cal the uninormal and binormal based on its tangent
        if i==pidList.GetNumberOfIds()-1:
            p0=GetPointPos(inpd,pidList.GetId(i-1))
            p1=GetPointPos(inpd,pidList.GetId(i))
        else:
            p0=GetPointPos(inpd,pidList.GetId(i))
            p1=GetPointPos(inpd,pidList.GetId(i+1))
        T1=np.array(p1)-np.array(p0)
        norm = np.linalg.norm(T1)
        if norm<>0:
           T1[0] = T1[0]/norm
           T1[1] = T1[1]/norm
           T1[2] = T1[2]/norm
        
        c=crossProduct(T0,N0)
        N1=crossProduct(c,T0)
        norm = np.linalg.norm(N1)
        if norm<>0:
           N1[0] = N1[0]/norm
           N1[1] = N1[1]/norm
           N1[2] = N1[2]/norm
        
        B1=crossProduct(T1,N1)            
        
        # cal outer-ring points 
        p0=GetPointPos(inpd,pidList.GetId(i-1))
        p1=GetPointPos(inpd,pidList.GetId(i))

        # determine the tube size
        r0=0.0
        r1=0.0
        if params['tubeSizeFlag']==0:
            r0=float(params['tubeFixedSize'])
            r1=r0
        else:
            r0=sizeArray.GetComponent(pidList.GetId(i-1),0)
            r1=sizeArray.GetComponent(pidList.GetId(i),0) 
            r0=(r0-sizeMin)/(sizeMax-sizeMin)
            r1=(r1-sizeMin)/(sizeMax-sizeMin)
        
        r0=r0*float(params['tubeScale'])
        r1=r1*float(params['tubeScale'])
        
        # determine the tube color
        rgbaBody=[0,0,0,255]
        if params['bodRFlag']==0:
            rgbaBody[0]=params['bodRValue']
        else:
            value=bodRArray.GetComponent(pidList.GetId(i),0)
            rgbaBody[0]=255*(value-bodRmin)/(bodRmax-bodRmin)
        
        if params['bodGFlag']==0:
            rgbaBody[1]=params['bodGValue']
        else:
            value=bodGArray.GetComponent(pidList.GetId(i),0)
            rgbaBody[1]=255*(value-bodGmin)/(bodGmax-bodGmin)
        
        if params['bodBFlag']==0:
            rgbaBody[2]=params['bodBValue']
        else:
            value=bodBArray.GetComponent(pidList.GetId(i),0)
            rgbaBody[2]=255*(value-bodBmin)/(bodBmax-bodBmin)
        
        if params['bodAFlag']==0:
            rgbaBody[3]=params['bodAValue']
        else:
            value=bodAArray.GetComponent(pidList.GetId(i),0)
            rgbaBody[3]=255*(value-bodAmin)/(bodAmax-bodAmin)
       
        # Generate Textures
        tex=glGenTextures(1)
        ix=4
        iy=4
        image = bytearray(ix*iy*4)
            
        # Set texture for tube segment, no transparency
        for i in range(0,ix):
            for j in range(0,iy):
                image[(i*ix+j)*4]=int(rgbaBody[0])
                image[(i*ix+j)*4+1]=int(rgbaBody[1])
                image[(i*ix+j)*4+2]=int(rgbaBody[2])
                image[(i*ix+j)*4+3]=int(rgbaBody[3])
            
        glBindTexture(GL_TEXTURE_2D, tex)   
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex)
        
        # Render a tube segment
        glBegin(GL_QUAD_STRIP)
        for k in range(0,slices+1):
            s=2*np.pi*k/slices
            x0 = p0[0] + r0*(np.cos(s)*N0[0] + np.sin(s)*B0[0]);
            y0 = p0[1] + r0*(np.cos(s)*N0[1] + np.sin(s)*B0[1]);
            z0 = p0[2] + r0*(np.cos(s)*N0[2] + np.sin(s)*B0[2]);
            
            x1 = p1[0] + r1*(np.cos(s)*N1[0] + np.sin(s)*B1[0]);
            y1 = p1[1] + r1*(np.cos(s)*N1[1] + np.sin(s)*B1[1]);
            z1 = p1[2] + r1*(np.cos(s)*N1[2] + np.sin(s)*B1[2]);
            
            glNormal3f(-(x0-p0[0]),-(y0-p0[1]),-(z0-p0[2]))
            glTexCoord2f(0, 0)
            glVertex3f(x0,y0,z0)
            glNormal3f(-(x1-p1[0]),-(y1-p1[1]),-(z1-p1[2]))
            glTexCoord2f(1, 1)
            glVertex3f(x1,y1,z1)
            
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(tex)
        
        # proceed to the next segment
        T0=T1
        N0=N1
        B0=B1
        
    return

#==============================================================================
# RenderTubeWithOrientation(inpd,lineNum,params)
# params: contains the required tube size information.
# tube color is determined by tube orientation.
#==============================================================================
def RenderTubeWithOrientation(inpd,lineNum,params):
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    slices=int(params['tubeSlices'])

    pidList = vtk.vtkIdList()
    if lineNum>inpd.GetNumberOfLines:
        lineNum=inpd.GetNumberOfLines
        
    inlines = inpd.GetLines()
    inlines.InitTraversal();
    for lidx in range(0,lineNum):
        inlines.GetNextCell(pidList)
     
    if pidList.GetNumberOfIds() < 2:
        return
    
    # get tube size info.
    sizeArray=GetPointArrayByName(inpd,params['tubeMappedToName'])
    sizeMin,sizeMax=GetMinMaxInArray(sizeArray)
    
    # Initial for the first point
    p0=GetPointPos(inpd,pidList.GetId(0))
    p1=GetPointPos(inpd,pidList.GetId(1))
    
    a = np.array(p1)-np.array(p0)
    b = [0,0,1]
    c = crossProduct(a,b);
    if c[0]==0.0 and c[1]==0.0 and c[2]==0.0:
       b = [1,0,0];
       c = crossProduct(a,b);
    
    b = crossProduct(c,a)
    norm = np.linalg.norm(b)
    if norm<>0:
       b[0] = b[0]/ norm
       b[1] = b[1]/ norm
       b[2] = b[2]/ norm
    
    N0=b 
    T0=np.array(p1)-np.array(p0)
    norm = np.linalg.norm(T0)
    if norm<>0:
       T0[0] = T0[0]/norm
       T0[1] = T0[1]/norm
       T0[2] = T0[2]/norm
    B0=crossProduct(T0,N0)
    
    for i in range(1,pidList.GetNumberOfIds()):
        # calculate unitnormal and binormal based on the tangent
        if i==pidList.GetNumberOfIds()-1:
            p0=GetPointPos(inpd,pidList.GetId(i-1))
            p1=GetPointPos(inpd,pidList.GetId(i))
        else:
            p0=GetPointPos(inpd,pidList.GetId(i))
            p1=GetPointPos(inpd,pidList.GetId(i+1))
            
        T1=np.array(p1)-np.array(p0)
        norm = np.linalg.norm(T1)
        if norm<>0:
           T1[0] = T1[0]/norm
           T1[1] = T1[1]/norm
           T1[2] = T1[2]/norm
        
        c=crossProduct(T0,N0)
        N1=crossProduct(c,T0)
        norm = np.linalg.norm(N1)
        if norm<>0:
           N1[0] = N1[0]/norm
           N1[1] = N1[1]/norm
           N1[2] = N1[2]/norm
        
        B1=crossProduct(T1,N1)            
        
        #Calculate outer-ring points to draw a tube segment
        p0=GetPointPos(inpd,pidList.GetId(i-1))
        p1=GetPointPos(inpd,pidList.GetId(i))

        # determine the tube size
        r0=0.0
        r1=0.0
        if params['tubeSizeFlag']==0:
            r0=float(params['tubeFixedSize'])
            r1=r0
        else:
            r0=sizeArray.GetComponent(pidList.GetId(i-1),0)
            r1=sizeArray.GetComponent(pidList.GetId(i),0) 
            r0=(r0-sizeMin)/(sizeMax-sizeMin)
            r1=(r1-sizeMin)/(sizeMax-sizeMin)
        
        r0=r0*float(params['tubeScale'])
        r1=r1*float(params['tubeScale'])
        
        # get tube color
        color=np.array(p1)-np.array(p0)
        norm=np.linalg.norm(color)
        color=np.fabs(color/norm)
        
        # Generate Textures
        tex=glGenTextures(1)
        ix=4
        iy=4
        image = bytearray(ix*iy*4)
            
        # Set texture for tube segment, no transparency
        for i in range(0,ix):
            for j in range(0,iy):
                image[(i*ix+j)*4]=int(color[0]*255)
                image[(i*ix+j)*4+1]=int(color[1]*255)
                image[(i*ix+j)*4+2]=int(color[2]*255)
                image[(i*ix+j)*4+3]=255
            
        glBindTexture(GL_TEXTURE_2D, tex)   
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex)

        # Render a tube segment
        glBegin(GL_QUAD_STRIP)
        for k in range(0,slices+1):
            s=2*np.pi*k/slices
            x0 = p0[0] + r0*(np.cos(s)*N0[0] + np.sin(s)*B0[0]);
            y0 = p0[1] + r0*(np.cos(s)*N0[1] + np.sin(s)*B0[1]);
            z0 = p0[2] + r0*(np.cos(s)*N0[2] + np.sin(s)*B0[2]);
            
            x1 = p1[0] + r1*(np.cos(s)*N1[0] + np.sin(s)*B1[0]);
            y1 = p1[1] + r1*(np.cos(s)*N1[1] + np.sin(s)*B1[1]);
            z1 = p1[2] + r1*(np.cos(s)*N1[2] + np.sin(s)*B1[2]);
            
            glNormal3f(-(x0-p0[0]),-(y0-p0[1]),-(z0-p0[2]))
            glTexCoord2f(0, 0)
            glVertex3f(x0,y0,z0)
            glNormal3f(-(x1-p1[0]),-(y1-p1[1]),-(z1-p1[2]))
            glTexCoord2f(1, 1)
            glVertex3f(x1,y1,z1)
            
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(tex)
        
        # proceed to the next segment
        T0=T1
        N0=N1
        B0=B1
        
    return
#==============================================================================
# RenderTubeWithFixedColor(inpd,lineNum,params)
# params: contains the fixed color without alpha information
#==============================================================================
def RenderTubeWithFixedColor(inpd,lineNum,params):
    
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
    
    slices=int(params['tubeSlices'])
    
    pidList = vtk.vtkIdList()
    if lineNum>inpd.GetNumberOfLines:
        lineNum=inpd.GetNumberOfLines
        
    inlines = inpd.GetLines()
    inlines.InitTraversal();
    for lidx in range(0,lineNum):
        inlines.GetNextCell(pidList)
     
    if pidList.GetNumberOfIds() < 2:
        return
    
    # Get the tube size
    sizeArray=GetPointArrayByName(inpd,params['tubeMappedToName'])
    sizeMin,sizeMax=GetMinMaxInArray(sizeArray)
    
    # Get the fixed color
    qColor=params['tubeFixedColor']

    # Generate Textures
    tex=glGenTextures(1)
    ix=4
    iy=4
    image = bytearray(ix*iy*4)
    # Set texture for tube segment, no transparency
    for i in range(0,ix):
        for j in range(0,iy):
            image[(i*ix+j)*4]=qColor.red()
            image[(i*ix+j)*4+1]=qColor.green()
            image[(i*ix+j)*4+2]=qColor.blue()
            image[(i*ix+j)*4+3]=qColor.alpha()
    
    glBindTexture(GL_TEXTURE_2D, tex)   
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex)
    
    # Initial for the first point
    p0=GetPointPos(inpd,pidList.GetId(0))
    p1=GetPointPos(inpd,pidList.GetId(1))
    
    a = np.array(p1)-np.array(p0)
    b = [0,0,1]
    c = crossProduct(a,b);
    if c[0]==0.0 and c[1]==0.0 and c[2]==0.0:
       b = [1,0,0];
       c = crossProduct(a,b);
    
    b = crossProduct(c,a)
    norm = np.linalg.norm(b)
    if norm<>0:
       b[0] = b[0]/ norm
       b[1] = b[1]/ norm
       b[2] = b[2]/ norm
    
    N0=b 
    T0=np.array(p1)-np.array(p0)
    norm = np.linalg.norm(T0)
    if norm<>0:
       T0[0] = T0[0]/norm
       T0[1] = T0[1]/norm
       T0[2] = T0[2]/norm
    B0=crossProduct(T0,N0)
    
    for i in range(1,pidList.GetNumberOfIds()):
        # Cal unitnormal and binormal based on the tangent
        if i==pidList.GetNumberOfIds()-1:
            p0=GetPointPos(inpd,pidList.GetId(i-1))
            p1=GetPointPos(inpd,pidList.GetId(i))
        else:
            p0=GetPointPos(inpd,pidList.GetId(i))
            p1=GetPointPos(inpd,pidList.GetId(i+1))
        T1=np.array(p1)-np.array(p0)
        norm = np.linalg.norm(T1)
        if norm<>0:
           T1[0] = T1[0]/norm
           T1[1] = T1[1]/norm
           T1[2] = T1[2]/norm
        
        c=crossProduct(T0,N0)
        N1=crossProduct(c,T0)
        norm = np.linalg.norm(N1)
        if norm<>0:
           N1[0] = N1[0]/norm
           N1[1] = N1[1]/norm
           N1[2] = N1[2]/norm
        
        B1=crossProduct(T1,N1)            
        
        # To get outer-ring points
        p0=GetPointPos(inpd,pidList.GetId(i-1))
        p1=GetPointPos(inpd,pidList.GetId(i))
        
        # To get tube size
        r0=0.0
        r1=0.0
        if params['tubeSizeFlag']==0:
            r0=float(params['tubeFixedSize'])
            r1=r0
        else:
            r0=sizeArray.GetComponent(pidList.GetId(i-1),0)
            r1=sizeArray.GetComponent(pidList.GetId(i),0) 
            r0=(r0-sizeMin)/(sizeMax-sizeMin)
            r1=(r1-sizeMin)/(sizeMax-sizeMin)
        
        r0=r0*float(params['tubeScale'])
        r1=r1*float(params['tubeScale'])
                
        # Render a tube segment
        glBegin(GL_QUAD_STRIP)
        for k in range(0,slices+1):
            s=2*np.pi*k/slices
            x0 = p0[0] + r0*(np.cos(s)*N0[0] + np.sin(s)*B0[0]);
            y0 = p0[1] + r0*(np.cos(s)*N0[1] + np.sin(s)*B0[1]);
            z0 = p0[2] + r0*(np.cos(s)*N0[2] + np.sin(s)*B0[2]);
            
            x1 = p1[0] + r1*(np.cos(s)*N1[0] + np.sin(s)*B1[0]);
            y1 = p1[1] + r1*(np.cos(s)*N1[1] + np.sin(s)*B1[1]);
            z1 = p1[2] + r1*(np.cos(s)*N1[2] + np.sin(s)*B1[2]);
            
            glNormal3f(-(x0-p0[0]),-(y0-p0[1]),-(z0-p0[2]))
            glTexCoord2f(0, 0)
            glVertex3f(x0,y0,z0)
            glNormal3f(-(x1-p1[0]),-(y1-p1[1]),-(z1-p1[2]))
            glTexCoord2f(1, 1)
            glVertex3f(x1,y1,z1)
            
        glEnd()
        
        # proceed to the next segment
        T0=T1
        N0=N1
        B0=B1
    
    glEnable(GL_TEXTURE_2D)   
    glDeleteTextures(tex)
    return
