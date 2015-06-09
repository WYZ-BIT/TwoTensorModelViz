#! /usr/bin/env python
#coding=utf-8

'''
This is a support library for 
Two-tensor Model Visualization Extension Module for 3D Slicer.

It deals with the rendering of fiber tracts.

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
# RenderLineWithSegmentOrientation(inpd,lineNum)
#==============================================================================
def RenderLineWithSegmentOrientation(inpd,lineNum):
    
    pidList=GetLinePointList(inpd,lineNum)
    
    if pidList.GetNumberOfIds() < 2:
        return
    
    glDisable(GL_LIGHTING) 
    
    point0=GetPointPos(inpd,pidList.GetId(0))
    
    for i in range(1,pidList.GetNumberOfIds()):
        point1 = GetPointPos(inpd,pidList.GetId(i))
        color=np.array(point1)-np.array(point0)
        norm=np.linalg.norm(color)
        color=np.fabs(color/norm)
        glColor3f(color[0],color[1],color[2])
        glBegin(GL_LINES)
        glVertex3f(point0[0],point0[1],point0[2])
        glVertex3f(point1[0],point1[1],point1[2])
        glEnd()    
        point0=point1
            
    glEnable(GL_LIGHTING) 
    
    return


