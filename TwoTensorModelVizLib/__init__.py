#! /usr/bin/env python
#coding=utf-8

'''
Here is the package for
Two-tensor Model Visualization Extension Module for 3D Slicer.

Wenyao Zhang
School of Computer Science, Beijing Institute of Technology
zhwenyao@bit.edu.cn
2014.9-2015.6
'''

import sys

try:
    import OpenGL 
except ImportError:
    print 'PyOpenGL is required, please install it and try again.'

# Add the required path for PyOpenGL. 
# It should be changed for different installations of Slicer.
sys.path.append('D:\SL4\S4BD\python-install\DLLs')

# Set the path for vtkPyOpenGLActor
# It is not necessary, if vtkPyOpenGLActor hsa been installed in Slicer.
# sys.path.append('.\TwoTensorModelVizLib\Dlls')

print "PyOpenGL and vtkPyOpenGLActor have been enabled!"

__all__=["PolyDataLib","LineRenderLib","TensorRenderLib","TubeRenderLib"]