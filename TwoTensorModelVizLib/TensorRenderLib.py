#! /usr/bin/env python
#coding=utf-8

'''
This is a support library for 
Two-tensor Model Visualization Extension Module for 3D Slicer.

It processes the rendering of tensors defined on line points.

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
# RenderTensorWithCustomColors(inpd,lineNum,params,tname='tensor2',mode=0)
# params: contains the color infor to render tensor glyphs.
# mode: 0 uses the specified color contained in params
#       1 uses the complementary color 
#==============================================================================
def RenderTensorWithCustomColors(inpd,lineNum,params,tname='tensor2',mode=0):
    
    # print params
    space=int(params['glyphSpace'])
    scale=int(params['glyphScale'])
    
    pidList = vtk.vtkIdList()
    if lineNum>inpd.GetNumberOfLines:
        lineNum=inpd.GetNumberOfLines
        
    inlines = inpd.GetLines()
    inlines.InitTraversal();
    for lidx in range(0,lineNum):
        inlines.GetNextCell(pidList)
     
    if pidList.GetNumberOfIds() < 2:
        return
    
    tensorArray=GetPointArrayByName(inpd,tname)

    points=inpd.GetPoints()
    
    rgbaTop=[128,128,128,255]
    rgbaBody=[0,255,0,255]
    rgbaBottom=[128,128,128,255]
    
    bodRArray=GetPointArrayByName(inpd,params['bodRName'])
    bodGArray=GetPointArrayByName(inpd,params['bodGName'])
    bodBArray=GetPointArrayByName(inpd,params['bodBName'])
    bodAArray=GetPointArrayByName(inpd,params['bodAName'])
    
    bodRmin,bodRmax=GetMinMaxInArray(bodRArray)
    bodGmin,bodGmax=GetMinMaxInArray(bodGArray)
    bodBmin,bodBmax=GetMinMaxInArray(bodBArray)
    bodAmin,bodAmax=GetMinMaxInArray(bodAArray)
    
    for i in range(space,pidList.GetNumberOfIds(),space):
        
        pid=pidList.GetId(i)
        pos=points.GetPoint(pid)
        
        t=tensorArray.GetTuple9(pid)
        tensor=np.array([t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8]]);
        
        # cal the color of cylinder body
        if params['bodRFlag']==0:
            rgbaBody[0]=params['bodRValue']
        else:
            value=bodRArray.GetComponent(pid,0)
            rgbaBody[0]=255*(value-bodRmin)/(bodRmax-bodRmin)
        
        if params['bodGFlag']==0:
            rgbaBody[1]=params['bodGValue']
        else:
            value=bodGArray.GetComponent(pid,0)
            rgbaBody[1]=255*(value-bodGmin)/(bodGmax-bodGmin)
        
        if params['bodBFlag']==0:
            rgbaBody[2]=params['bodBValue']
        else:
            value=bodBArray.GetComponent(pid,0)
            rgbaBody[2]=255*(value-bodBmin)/(bodBmax-bodBmin)
        
        if params['bodAFlag']==0:
            rgbaBody[3]=params['bodAValue']
        else:
            value=bodAArray.GetComponent(pid,0)
            rgbaBody[3]=255*(value-bodAmin)/(bodAmax-bodAmin)
        
        # cal the complementary color
        if mode==1:
            rgbaTop[0]=255-rgbaTop[0]
            rgbaTop[1]=255-rgbaTop[1]
            rgbaTop[2]=255-rgbaTop[2]
            rgbaBody[0]=255-rgbaBody[0]
            rgbaBody[1]=255-rgbaBody[1]
            rgbaBody[2]=255-rgbaBody[2]
            rgbaBottom[0]=255-rgbaBottom[0]
            rgbaBottom[1]=255-rgbaBottom[1]
            rgbaBottom[2]=255-rgbaBottom[2]
        
        slices=int(params['cylinderSlices'])
        stacks=int(params['cylinderStacks'])    
        RenderTensorAsCylinder(pos,tensor,scale,rgbaTop,rgbaBody,rgbaBottom, \
            slices,stacks)

    return
#==============================================================================
# RenderTensorAsCylinder(pos,tensor,scale,rgbaTop,rgbaBody,rgbaBottom,
#                         slices,stacks)
# Visualize a tensor using a clylinder glyph
#==============================================================================
def RenderTensorAsCylinder(pos,tensor,scale,rgbaTop,rgbaBody,rgbaBottom, \
                           slices=20,stacks=2):
    glPushMatrix()
    
    eigVec,eigVal=CalTensorEigs(tensor)
    
    # traslate 
    mat=np.array([[1.0, 0.0, 0.0, 0.0],\
               [0.0, 1.0, 0.0, 0.0],\
               [0.0, 0.0, 1.0, 0.0],\
               [0.0, 0.0, 0.0, 1.0]]);
    mat[3,0] =pos[0];
    mat[3,1] =pos[1];
    mat[3,2] =pos[2];
    glMultMatrixf(mat);
    
    # rotate    
    matr=np.array([[0.0, 0.0, 0.0, 0.0],\
               [0.0, 0.0, 0.0, 0.0],\
               [0.0, 0.0, 0.0, 0.0],\
               [0.0, 0.0, 0.0, 1.0]]);
    # scale
    mats=np.array([[0.0, 0.0, 0.0, 0.0],\
               [0.0, 0.0, 0.0, 0.0],\
               [0.0, 0.0, 0.0, 0.0],\
               [0.0, 0.0, 0.0, 1.0]]);
    
    if (eigVal[0]>eigVal[1] and eigVal[0]>eigVal[2]):
        matr[0,0]=eigVec[0,1];
        matr[0,1]=eigVec[1,1];
        matr[0,2]=eigVec[2,1];
        matr[1,0]=eigVec[0,2];
        matr[1,1]=eigVec[1,2];
        matr[1,2]=eigVec[2,2];
        matr[2,0]=eigVec[0,0];
        matr[2,1]=eigVec[1,0];
        matr[2,2]=eigVec[2,0];
        
        mats[0,0] =eigVal[1]*scale; 
        mats[1,1] =eigVal[2]*scale;
        mats[2,2] =eigVal[0]*scale;  
    
    if(eigVal[1]>eigVal[0] and eigVal[1]>eigVal[2]):
        matr[0,0]=eigVec[0,2];
        matr[0,1]=eigVec[1,2];
        matr[0,2]=eigVec[2,2];
        matr[1,0]=eigVec[0,0];
        matr[1,1]=eigVec[1,0];
        matr[1,2]=eigVec[2,0];
        matr[2,0]=eigVec[0,1];
        matr[2,1]=eigVec[1,1];
        matr[2,2]=eigVec[2,1];
        
        mats[0,0] =eigVal[2]*scale; 
        mats[1,1] =eigVal[0]*scale;
        mats[2,2] =eigVal[1]*scale;
                
    if(eigVal[2]>eigVal[0] and eigVal[2]>eigVal[1]):
        matr[0,0]=eigVec[0,0];
        matr[0,1]=eigVec[1,0];
        matr[0,2]=eigVec[2,0];
        matr[1,0]=eigVec[0,1];
        matr[1,1]=eigVec[1,1];
        matr[1,2]=eigVec[2,1];
        matr[2,0]=eigVec[0,2];
        matr[2,1]=eigVec[1,2];
        matr[2,2]=eigVec[2,2];
        
        mats[0,0] =eigVal[0]*scale; 
        mats[1,1] =eigVal[1]*scale;
        mats[2,2] =eigVal[2]*scale; 

    # Check for the special case where  two big eigen values occurs. 
    if np.fabs(mats[2,2]-mats[1,1])<10e-10*scale:
        tmp0=matr[0,0]
        tmp1=matr[0,1]
        tmp2=matr[0,2]
        matr[0,0]=matr[1,0];
        matr[0,1]=matr[1,1];
        matr[0,2]=matr[1,2];
        matr[1,0]=matr[2,0];
        matr[1,1]=matr[2,1];
        matr[1,2]=matr[2,2];
        matr[2,0]=tmp0 
        matr[2,1]=tmp1 
        matr[2,2]=tmp2 
        
        tmp=mats[0,0]
        mats[0,0] =mats[1,1] 
        mats[1,1] =mats[2,2] 
        mats[2,2] =tmp 
        
    elif np.fabs(mats[2,2]-mats[0,0])<10e-10*scale:
        tmp0=matr[1,0]
        tmp1=matr[1,1]
        tmp2=matr[1,2]
        matr[1,0]=matr[0,0];
        matr[1,1]=matr[0,1];
        matr[1,2]=matr[0,2];
        matr[0,0]=matr[2,0];
        matr[0,1]=matr[2,1];
        matr[0,2]=matr[2,2];
        matr[2,0]=tmp0 
        matr[2,1]=tmp1 
        matr[2,2]=tmp2 
        
        tmp=mats[1,1]
        mats[1,1] =mats[0,0] 
        mats[0,0] =mats[2,2]
        mats[2,2] =tmp 
        
    if np.linalg.det(matr) < 0:
        # +/- the eigenvector is still an eigenvector
        # so if we have the set of eigenvectors that
        # give a negative determinant (not a rotation matrix)
        # multiply our eigenvectors by -1 to choose 
        # the other valid set of eigenvectors.
        matr=np.multiply(matr,-1);
        # fix the final entry that must be 1.0 for a valid transformation matrix
        matr[3,3] = 1.0
        
    glMultMatrixf(matr)

    glMultMatrixf(mats)
    
    drawCylinderWithTextColors(rgbaTop,rgbaBody,rgbaBottom,slices,stacks)
    
    glPopMatrix()
    return

#==============================================================================
# drawCylinderWithTextColors(rgbaTop,rgbaBody,rgbaBottom,slices=20,stacks=2)
#==============================================================================
def drawCylinderWithTextColors(rgbaTop,rgbaBody,rgbaBottom,slices=20,stacks=2):
    # Generate Textures
    tex=glGenTextures(3)
    
    radius=0.5;
    vlen=1;
    
    ix=4
    iy=4
    image = bytearray(ix*iy*4)
    
    # Set texture for top disk
    for i in range(0,ix):
        for j in range(0,iy):
            image[(i*ix+j)*4]=int(rgbaTop[0])
            image[(i*ix+j)*4+1]=int(rgbaTop[1])
            image[(i*ix+j)*4+2]=int(rgbaTop[2])
            image[(i*ix+j)*4+3]=int(rgbaTop[3])
    
    glBindTexture(GL_TEXTURE_2D, tex[0])   
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    # Set texture for body
    for i in range(0,ix):
        for j in range(0,iy):
            image[(i*ix+j)*4]=int(rgbaBody[0])
            image[(i*ix+j)*4+1]=int(rgbaBody[1])
            image[(i*ix+j)*4+2]=int(rgbaBody[2])
            image[(i*ix+j)*4+3]=int(rgbaBody[3])
    
    glBindTexture(GL_TEXTURE_2D, tex[1])   
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    # Set texture for bottom disk
    for i in range(0,ix):
        for j in range(0,iy):
            image[(i*ix+j)*4]=int(rgbaBottom[0])
            image[(i*ix+j)*4+1]=int(rgbaBottom[1])
            image[(i*ix+j)*4+2]=int(rgbaBottom[2])
            image[(i*ix+j)*4+3]=int(rgbaBottom[3])
    
    glBindTexture(GL_TEXTURE_2D, tex[2])   
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    # begin to draw objects
    glPushMatrix()

    quadric=gluNewQuadric(); 
    gluQuadricNormals(quadric, GLU_SMOOTH);   
    gluQuadricTexture(quadric, GL_TRUE)
    
    glEnable(GL_TEXTURE_2D)
    
    # traslate
    glTranslatef( 0,0,-0.5 )
    
    # draw the first cap
    glBindTexture(GL_TEXTURE_2D, tex[0])
    gluQuadricOrientation(quadric,GLU_INSIDE);
    gluDisk( quadric, 0.0, radius, slices, stacks);
    
    # draw the body
    glBindTexture(GL_TEXTURE_2D, tex[1])
    gluQuadricOrientation(quadric,GLU_OUTSIDE);
    gluCylinder(quadric, radius, radius, vlen, slices, stacks);
    
    # draw the second cap
    glBindTexture(GL_TEXTURE_2D, tex[2])
    glTranslatef( 0,0,vlen);
    gluQuadricOrientation(quadric,GLU_OUTSIDE);
    gluDisk( quadric, 0.0, radius, slices, stacks);
    
    glDisable(GL_TEXTURE_2D)
    
    gluDeleteQuadric(quadric)
    
    glPopMatrix()
    
    # Delete texture, release display memory
    glDeleteTextures(tex)
    return

#==============================================================================
