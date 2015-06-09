#! /usr/bin/env python
#coding=utf-8

'''
This is a support library for 
Two-tensor Model Visualization Extension Module for 3D Slicer.

It processes the access of poly data object.

Wenyao Zhang
School of Computer Science, Beijing Institute of Technology
zhwenyao@bit.edu.cn
2014.9-2015.6
'''

import numpy as np
import vtk

#==============================================================================
# LoadPolyData(filename, showFileInfo=0)
#    Load the poly data from the file, and
#    return a inpd (vtkPolyData) object
#==============================================================================
def LoadPolyData(filename, showFileInfo=0):
    loc=filename.rfind(".");
    extension = filename[loc:filename.__len__()];
    extension =extension.upper();
    # print loc, extension
    if extension==".VTK":
        polyDataReader=vtk.vtkPolyDataReader();
        polyDataReader.SetFileName( filename );
        polyDataReader.Update();
        inpd= polyDataReader.GetOutput()
        
    elif extension==".VTP":
        polyDataReader = vtk.vtkXMLPolyDataReader()
        polyDataReader.SetFileName( filename );
        polyDataReader.Update();
        inpd = polyDataReader.GetOutput();
    
    if showFileInfo==1:
        print "Polydata File:",filename
        ShowPolyDataInfo(inpd)

    return inpd

#==============================================================================
# ShowPolyDataInfo(inpd)
#     inpd: input polydata (vtkPolyData)
#     Show the data infor. contained in the polydata structure.  
#==============================================================================
def ShowPolyDataInfo(inpd):
    # Get points contained in the Polydata [geometrical struct]
    print inpd.GetClassName()
    inpoints = inpd.GetPoints();
    num_points = inpoints.GetNumberOfPoints()
    #num_points = inpd.GetNumberOfPoints()
    print "Number of points:",num_points
    
    # Get lines [topological struct]
    inlines = inpd.GetLines();
    num_lines = inpd.GetNumberOfLines();
    num_lines = inlines.GetNumberOfCells(); 
    print "Number of lines:",num_lines
    
    # Get PointData [attributes associated with points]
    inpointdata = inpd.GetPointData()
    if inpointdata.GetNumberOfArrays() > 0:
        point_data_array_indices = range(inpointdata.GetNumberOfArrays())            
        for idx in point_data_array_indices:
            array = inpointdata.GetArray(idx)
            print "Point data array found:", idx,array.GetName()
            print "    Tuples:", array.GetNumberOfTuples()
            print "    Components:", array.GetNumberOfComponents()
            print "    Size:", array.GetSize()
    
    # Get CellData [attributes associated with cells(lines)]
    incelldata = inpd.GetCellData()
    if incelldata.GetNumberOfArrays() > 0:
        cell_data_array_indices = range(incelldata.GetNumberOfArrays())            
        for idx in cell_data_array_indices:
            array = incelldata.GetArray(idx)
            print "Cell data array found:",idx, array.GetName()
            print "    Tuples:", array.GetNumberOfTuples()
            print "    Components:", array.GetNumberOfComponents()
            print "    Size:", array.GetSize()


#==============================================================================
# GetPointArrayByName(inpd,name)
#==============================================================================
def GetPointArrayByName(inpd,name):
    inpointdata = inpd.GetPointData()
    for ia in range(0,inpointdata.GetNumberOfArrays()):
        #print inpointdata.GetArrayName(ia)
        if str.upper(inpointdata.GetArrayName(ia))==str.upper(name):
            retArray=inpointdata.GetArray(ia)
            #print 'True return'
            return retArray
    # print 'No array named ',name    
    return None

#==============================================================================
# GetCellArrayByName(inpd,name)
#==============================================================================
def GetCellArrayByName(inpd,name):
    incelldata = inpd.GetCellData()
    for ia in range(0,incelldata.GetNumberOfArrays()):
        print incelldata.GetArrayName(ia)
        if str.upper(incelldata.GetArrayName(ia))==str.upper(name):
            retArray=incelldata.GetArray(ia)
            print 'Found'
            return retArray
        
    print 'No'
    return None

#==============================================================================
# GetMinMaxInArray(array)
#==============================================================================
def GetMinMaxInArray(array):
    if array.GetNumberOfComponents()>1:
        min=None
        max=None
        return min,max
    
    min=array.GetComponent(0,0)
    max=array.GetComponent(0,0)
    for i in range(0,array.GetNumberOfTuples()):
        if array.GetComponent(i,0)>max:
            max=array.GetComponent(i,0)
        if array.GetComponent(i,0)<min:
            min=array.GetComponent(i,0)
    return min,max

#==============================================================================
# GetLinePointList(inpd,lineNum)
#    lineNum=1,2,...
#==============================================================================
def GetLinePointList(inpd,lineNum):
    if lineNum>inpd.GetNumberOfLines:
        lineNum=inpd.GetNumberOfLines
    ptids = vtk.vtkIdList()
    inlines = inpd.GetLines()
    inlines.InitTraversal();
    for lidx in range(0,lineNum):
        # fetch a line into ptids
        inlines.GetNextCell(ptids)
    return ptids

#==============================================================================
# GetPointTensor(inpd,pid,tensorname)
#    inpd: input polydata
#    pid: point ID
# return a numpy array with 9 elements
#==============================================================================
def GetPointTensor(inpd,pid,tensorname):
    array=GetPointArrayByName(inpd,tensorname);
    t=array.GetTuple9(pid);
    tensor=np.array([t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8]]);
    return tensor

#==============================================================================
# GetPointValue(inpd,pid,valuename)
#    inpd: input polydata
#    pid: point ID
# return a scale float value
#==============================================================================
def GetPointValue(inpd,pid,valuename):
    array=GetPointArrayByName(inpd,valuename)
    value=array.GetComponent(pid,0)
    return value
    
#==============================================================================
# GetPointPos(inpd,pid)
#    inpd: input polydata
#    pid: point ID
# return a tuple with 3 components
#==============================================================================
def GetPointPos(inpd,pid):
    point=inpd.GetPoints().GetPoint(pid)
    return point

#==============================================================================
# CalTensorEigs(tensor)
#    tensor is a numpy array with 9 elements
#    return eigen vectors and eigen values without sorting
#==============================================================================
def CalTensorEigs(tensor):
    dataMat=np.mat(tensor.reshape(3,3));
    #print np.linalg.det(dataMat);
    eigVals,eigVects=np.linalg.eig(dataMat);
    #eigValIndice=np.argsort(eigVals);# in ascending order
    #eigVals=eigVals[eigValIndice]
    #eigVects=eigVects[:,eigValIndice]
    #print eigVals
    return eigVects,eigVals 

def GetMaxEigs(eigVects,eigVals):
    if (eigVals[0]>eigVals[1]) and eigVals[0]>eigVals[2] :
        retvec=[eigVects[0,0],eigVects[1,0],eigVects[2,0]]
        return retvec, eigVals[0]
    if (eigVals[1]>eigVals[0]) and eigVals[1]>eigVals[2] :
        retvec=[eigVects[0,1],eigVects[1,1],eigVects[2,1]]
        return retvec, eigVals[1]
    if (eigVals[2]>eigVals[0]) and eigVals[2]>eigVals[0] :
        retvec=[eigVects[0,2],eigVects[1,2],eigVects[2,2]]
        return retvec, eigVals[2]

#==============================================================================
# ExistTensor1(inpd)
# Check if Tensor1 is existed in inpd.
# If existed, return True, else False
#==============================================================================
def ExistTensor1(inpd):
    inpointdata = inpd.GetPointData()
    for ia in range(0,inpointdata.GetNumberOfArrays()):
        if str.upper(inpointdata.GetArrayName(ia))==str.upper('tensor1'):
           return True
    
    return False

#==============================================================================
# ExistTensor2(inpd)
# Check if Tensor1 is existed in inpd.
# If existed, return True, else False
#==============================================================================
def ExistTensor2(inpd):
    inpointdata = inpd.GetPointData()
    for ia in range(0,inpointdata.GetNumberOfArrays()):
        if str.upper(inpointdata.GetArrayName(ia))==str.upper('tensor2'):
           return True
    
    return False

#==============================================================================
# For Test
#==============================================================================
def PolyDataTest():
    # Load the polydata
    #filename="E:\WorkInSPL\Proj-Lauren\FiberViz\MyTestFibers.vtp"
    filename="D:\TractsWork\TestData\Lipeng\GS_cc_caudalmiddlefrontal.vtp"
    inpd=LoadPolyData(filename,0)
    ShowPolyDataInfo(inpd)
    ta=GetPointArrayByName(inpd,'tensor1')
    print 'ta:',ta
    fa=GetPointArrayByName(inpd,'FA1')
    print 'fa:',fa
    ca=GetCellArrayByName(inpd,'EmbeddingColor')
    print 'ca:',ca
    min,max=GetMinMaxInArray(ta)
    print 'ta min max:',min,max
    min,max=GetMinMaxInArray(fa)
    print 'fa min max:',min,max
    min,max=GetMinMaxInArray(ca)
    print 'ca min max:',min,max
    
    linePointList=GetLinePointList(inpd,1)
    
    for i in range(0,linePointList.GetNumberOfIds()):
        point=inpd.GetPoints().GetPoint(i)
        print point
        tensor=ta.GetTuple9(linePointList.GetId(i))
        print tensor
        tmp1=fa.GetComponent(linePointList.GetId(i),0)
        tmp2=fa.GetTuple(linePointList.GetId(i))
        print tmp1,tmp2
        if i>2:
            break

    for i in range(0,linePointList.GetNumberOfIds()):
        point=GetPointPos(inpd,i)
        print point
        tensor=GetPointTensor(inpd,i,'tensor1')
        print tensor
        vects,vals=CalTensorEigs(tensor)
        print vects,vals
        value=GetPointValue(inpd,i,'Trace1')
        print value
        if i>2:
            break
    

if __name__ == "__main()__":
    PolyDataTest()

'''
execfile('.\TwoTensorModeVizLib\PolyDataLib.py')
'''
