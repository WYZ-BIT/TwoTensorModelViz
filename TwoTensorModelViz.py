#! /usr/bin/env python
#coding=utf-8

'''
Two-tensor Model Visualization Extension Module for 3D Slicer.

Wenyao Zhang
School of Computer Science, Beijing Institute of Technology
zhwenyao@bit.edu.cn
2014.9-2015.8
'''

#==============================================================================
# Syetem Settings
#==============================================================================
import os
import unittest
from __main__ import vtk, qt, ctk, slicer

import TwoTensorModelVizLib

from TwoTensorModelVizLib.PolyDataLib import *
from TwoTensorModelVizLib.LineRenderLib import *
from TwoTensorModelVizLib.TensorRenderLib import *
from TwoTensorModelVizLib.TubeRenderLib import *

from vtkSlicerPyOpenGLActorPython import *  

#==============================================================================
# Set global variables and functions 
#==============================================================================
inpd=None  # input poly data object
params={}  # dict for parameters

# params to control the precision of glyphs
params['cylinderStacks']=1 
params['cylinderSlices']=10
params['tubeSlices']=10

def InitGL():
    pass
    
def DrawScene(inpd,params):
    
    InitGL()
    
    lineNum=int(params['lineNum'])
    lineSpace=int(params['lineSpace'])
    glyphSpace=int(params['glyphSpace'])
    glyphScale=int(params['glyphScale'])
    tubeScale=int(params['tubeScale'])
    
    tubeColorFlag=params['tubeColorFlag']
    tubeSizeFlag=params['tubeSizeFlag']
        
    onlyOneLine=params['onlyOneLine']
    showLines=params['showLines']
    showTensor1=params['showTensor1']
    showTensor2=params['showTensor2']
    showTubes=params['showTubes']
    
    if onlyOneLine:
        
        if showLines:
            RenderLineWithSegmentOrientation(inpd,lineNum)
            #RenderLineWithTensorOrientation(inpd,lineNum)
            
        if showTensor1:
            #RenderTensorsOnLine(inpd,lineNum,glyphSpace,glyphScale,'tensor1',2)
            #RenderTensorsOnLineDirectly(inpd,lineNum,glyphSpace,glyphScale,'tensor1',2)
            RenderTensorWithCustomColors(inpd,lineNum, params,'tensor1',0)
            
        if showTensor2:
            #RenderTensorsOnLine(inpd,lineNum,glyphSpace,glyphScale,'tensor2',3)
            # RenderTensorsOnLineDirectly(inpd,lineNum,glyphSpace,glyphScale,'tensor2',3)
            RenderTensorWithCustomColors(inpd,lineNum, params,'tensor2',1)
            
        if showTubes:
            if tubeColorFlag==0:
                #color=params['tubeFixedColor']
                #print color
                #ShowWaterWithFixedColor(inpd,lineNum,glyphSpace,tubeScale,color)
                RenderTubeWithFixedColor(inpd,lineNum,params)
            elif tubeColorFlag==1:
                RenderTubeWithOrientation(inpd,lineNum,params)
            elif tubeColorFlag==2:
                RenderTubeWithCustomColors(inpd,lineNum,params)
                #ShowWaterWithCustomColor(inpd,lineNum,glyphSpace,tubeScale,params)
                
    else: # multiple lines
        
        for lidx in range(1,inpd.GetNumberOfLines()+1,lineSpace):
            # Note the num of cells begins with 1 not 0
            # print 'Line No.:', lidx
            if showLines:
                RenderLineWithSegmentOrientation(inpd,lidx)
                #RenderLineWithTensorOrientation(inpd,lidx)
                
            if showTensor1:
                #RenderTensorsOnLine(inpd,lidx,glyphSpace,glyphScale,'tensor1',2)
                #RenderTensorsOnLineDirectly(inpd,lidx,glyphSpace,glyphScale,'tensor1',2)
                RenderTensorWithCustomColors(inpd,lidx, params,'tensor1',0)
                
            if showTensor2:
                #RenderTensorsOnLine(inpd,lidx,glyphSpace,glyphScale,'tensor2',3)
                #RenderTensorsOnLineDirectly(inpd,lidx,glyphSpace,glyphScale,'tensor2',3)
                RenderTensorWithCustomColors(inpd,lidx, params,'tensor2',1)
                
            if showTubes:
                if tubeColorFlag==0:
                    #color=params['tubeFixedColor']
                    #print color
                    #ShowWaterWithFixedColor(inpd,lidx,glyphSpace,tubeScale,color)
                    RenderTubeWithFixedColor(inpd,lidx,params)
                elif tubeColorFlag==1:
                    RenderTubeWithOrientation(inpd,lidx,params)
                elif tubeColorFlag==2:
                    RenderTubeWithCustomColors(inpd,lidx,params)
                    #ShowWaterWithCustomColor(inpd,lidx,glyphSpace,tubeScale,params)
    
    return
#==============================================================================
# TwoTensorModelViz 
#==============================================================================
class TwoTensorModelViz:
  def __init__(self, parent):
    parent.title = "Two-tensor Model Visualization" # Visible in the module menu
    parent.categories = ["Diffusion"]   
    parent.dependencies = []
    parent.contributors = ["Wenyao Zhang (Beijing Institute of Technology)"] 
    parent.helpText = """
    This extension module for 3D Slicer is used to visualize tractography data 
    that were generated by the UKF method with the two-tensor model. For more 
    information, please refer to http://www.wyz.cs.org (github web page).
    """
    parent.acknowledgementText = """
    This module was originally developed by Wenyao Zhang, School of Computer Science,
    Beijing Institute of Technology, China. It was partially funded by China
    Scholarship Council under the grant 201306035016.
    """ 

#==============================================================================
# TwoTensorModelVizWidget -- GUI for the module
#==============================================================================
class TwoTensorModelVizWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

#===========Setup the GUI components=========
  def setup(self):
    # make an instance of the logic 
    self.logic = TwoTensorModelVizLogic()

# 
# Model Selection Area
#
    modelCollapsibleButton = ctk.ctkCollapsibleButton()
    modelCollapsibleButton.text = "Basic"
    self.layout.addWidget(modelCollapsibleButton)
    
    modelFormLayout = qt.QFormLayout(modelCollapsibleButton)
    
    
    # ============Fiber model selector===================
    self.modelSelector = slicer.qMRMLNodeComboBox()
    self.modelSelector.nodeTypes = ( ("vtkMRMLFiberBundleNode"), "" )
    self.modelSelector.selectNodeUponCreation = True
    self.modelSelector.addEnabled = False
    self.modelSelector.removeEnabled = False
    self.modelSelector.noneEnabled = False
    self.modelSelector.showHidden = False
    self.modelSelector.showChildNodeTypes = False
    self.modelSelector.setMRMLScene( slicer.mrmlScene )
    self.modelSelector.setToolTip( "Pick a bundle of fibers." )
    modelFormLayout.addRow("Fiber bundles: ", self.modelSelector)
    self.modelSelector.connect('currentNodeChanged(vtkMRMLNode*)', \
         self.onModelSelect)

    # ============Glyph Space scroller=================
    self.sliderGlyphSpace = ctk.ctkSliderWidget()
    self.sliderGlyphSpace.decimals = 0
    self.sliderGlyphSpace.minimum=1
    self.sliderGlyphSpace.maximum=100
    self.sliderGlyphSpace.value=10
    self.sliderGlyphSpace.enabled = False
    modelFormLayout.addRow("Glyph Space:", self.sliderGlyphSpace)
    self.sliderGlyphSpace.connect('valueChanged(double)', \
         self.onGlyphSpaceChanged)
    
    # ============Glyph Scale scroller=================
    self.sliderGlyphScale = ctk.ctkSliderWidget()
    self.sliderGlyphScale.decimals = 0
    self.sliderGlyphScale.minimum=1
    self.sliderGlyphScale.maximum=10000
    self.sliderGlyphScale.value=2000
    self.sliderGlyphScale.enabled = False
    modelFormLayout.addRow("Glyph Scale:", self.sliderGlyphScale)
    self.sliderGlyphScale.connect('valueChanged(double)', \
         self.onGlyphScaleChanged)

    modelGridLayout=qt.QGridLayout()
    modelFormLayout.addRow("View Items:",modelGridLayout)
    
    # ============Check Box for showing lines==============
    self.checkboxLines=qt.QCheckBox("Lines")
    self.checkboxLines.toolTip="When checked, fiber lines are shown."
    self.checkboxLines.checked=True
    self.checkboxLines.enabled=False
    #modelFormLayout.addRow(self.checkboxLines)
    modelGridLayout.addWidget(self.checkboxLines,0,0)
        

    # ============Check Box for showing tensor 1==============
    self.checkboxTensor1=qt.QCheckBox("Tensor 1")
    self.checkboxTensor1.toolTip="When checked, cylinder glyphs are shown for tensor 1."
    self.checkboxTensor1.checked=True
    self.checkboxTensor1.enabled=False
    modelGridLayout.addWidget(self.checkboxTensor1,0,1)
    
    # ============Check Box for showing tensor 2==============
    self.checkboxTensor2=qt.QCheckBox("Tensor 2")
    self.checkboxTensor2.toolTip="When checked, cylinder glyphs are shown for tensor 2."
    self.checkboxTensor2.checked=True
    self.checkboxTensor2.enabled=False
    modelGridLayout.addWidget(self.checkboxTensor2,0,2)

    # ============Check Box for showing tube==============
    self.checkboxTubes=qt.QCheckBox("Tubes")
    self.checkboxTubes.toolTip="When checked, tubes will be shown."
    self.checkboxTubes.checked=True
    self.checkboxTubes.enabled=False
    modelGridLayout.addWidget(self.checkboxTubes,0,3)
    
# 
# Fiber Filter Area
#
    filterCollapsibleButton = ctk.ctkCollapsibleButton()
    filterCollapsibleButton.text = "Fiber Filter"
    self.layout.addWidget(filterCollapsibleButton)
       
    filterFormLayout = qt.QFormLayout(filterCollapsibleButton)
    
    
    # ============Line Space scroller=================
    self.sliderLineSpace = ctk.ctkSliderWidget()
    self.sliderLineSpace.decimals = 0
    self.sliderLineSpace.minimum=1
    self.sliderLineSpace.maximum=100
    self.sliderLineSpace.value=10
    self.sliderLineSpace.enabled = False
    filterFormLayout.addRow("One of n Fibers:", self.sliderLineSpace)
    self.sliderLineSpace.connect('valueChanged(double)', \
         self.onLineSpaceChanged)
    
    # ============Line Num scroller=================
    self.sliderLineNum = ctk.ctkSliderWidget()
    self.sliderLineNum.decimals = 0
    self.sliderLineNum.minimum=1
    self.sliderLineNum.maximum=100
    self.sliderLineNum.value=1
    self.sliderLineNum.enabled = False
    filterFormLayout.addRow("Specific Fiber No:", self.sliderLineNum)
    self.sliderLineNum.connect('valueChanged(double)', \
         self.onLineNumChanged)
    
    # ============Check Box for showing one fiber==============
    self.checkboxOnlyOneLine=qt.QCheckBox("Only show the specific fiber")
    self.checkboxOnlyOneLine.toolTip="When checked, only the specified fiber is shown."
    self.checkboxOnlyOneLine.checked=False
    self.checkboxOnlyOneLine.enabled=False
    filterFormLayout.addWidget(self.checkboxOnlyOneLine)
   
# 
# Cylinder Color Mapping Area
#
    cylinderColorCollapsibleButton = ctk.ctkCollapsibleButton()
    cylinderColorCollapsibleButton.text = "Cylinder Boby Color"
    self.layout.addWidget(cylinderColorCollapsibleButton)
    
    cylinderVBoxLayOut = qt.QVBoxLayout(cylinderColorCollapsibleButton)
    
    # Add a TabWidget
    cylinderTabWidget=qt.QTabWidget()
    cylinderVBoxLayOut.addWidget(cylinderTabWidget)
    
    # Create four pages and the GridLayOut
    redPage=qt.QWidget()
    redGrid=qt.QGridLayout(redPage)
    cylinderTabWidget.addTab(redPage,'Red')
    
    greenPage=qt.QWidget()
    greenGrid=qt.QGridLayout(greenPage)
    cylinderTabWidget.addTab(greenPage,'Green')

    bluePage=qt.QWidget()
    blueGrid=qt.QGridLayout(bluePage)
    cylinderTabWidget.addTab(bluePage,'Blue')

    alphaPage=qt.QWidget()
    alphaGrid=qt.QGridLayout(alphaPage)
    cylinderTabWidget.addTab(alphaPage,'Alpha')
    
    #========= Set the Red page ==============
    groupBox=qt.QGroupBox()
    grid = qt.QGridLayout(groupBox)
    redGrid.addWidget(groupBox,0,1)
    
    self.bodRadioR1=qt.QRadioButton("Fixed to:")
    self.bodRadioR2=qt.QRadioButton("Mapped to:")
    self.bodRadioR1.checked=True
       
    self.bodSliderR = ctk.ctkSliderWidget()
    self.bodSliderR.decimals = 0
    self.bodSliderR.minimum=0
    self.bodSliderR.maximum=255
    self.bodSliderR.value=1
    self.bodSliderR.enabled = True
    
    self.bodComboR = qt.QComboBox()
    self.bodComboR.duplicatesEnabled= False
    grid.addWidget(self.bodRadioR1,0,0)
    grid.addWidget(self.bodRadioR2,1,0)
    grid.addWidget(self.bodSliderR,0,1)
    grid.addWidget(self.bodComboR,1,1)

    #========= Set the Green page ==============
    groupBox=qt.QGroupBox()
    grid = qt.QGridLayout(groupBox)
    greenGrid.addWidget(groupBox,0,1)
    
    self.bodRadioG1=qt.QRadioButton("Fixed to:")
    self.bodRadioG2=qt.QRadioButton("Mapped to:")
    self.bodRadioG1.checked=True
       
    self.bodSliderG = ctk.ctkSliderWidget()
    self.bodSliderG.decimals = 0
    self.bodSliderG.minimum=0
    self.bodSliderG.maximum=255
    self.bodSliderG.value=1
    self.bodSliderG.enabled = True
    
    self.bodComboG = qt.QComboBox()
    self.bodComboG.duplicatesEnabled= False
    grid.addWidget(self.bodRadioG1,0,0)
    grid.addWidget(self.bodRadioG2,1,0)
    grid.addWidget(self.bodSliderG,0,1)
    grid.addWidget(self.bodComboG,1,1)
    
    #========= Set the Blue page ==============
    groupBox=qt.QGroupBox()
    grid = qt.QGridLayout(groupBox)
    blueGrid.addWidget(groupBox,0,1)
   
    self.bodRadioB1=qt.QRadioButton("Fixed to:")
    self.bodRadioB2=qt.QRadioButton("Mapped to:")
    self.bodRadioB1.checked=True
       
    self.bodSliderB = ctk.ctkSliderWidget()
    self.bodSliderB.decimals = 0
    self.bodSliderB.minimum=0
    self.bodSliderB.maximum=255
    self.bodSliderB.value=1
    self.bodSliderB.enabled = True
    
    self.bodComboB = qt.QComboBox()
    self.bodComboB.duplicatesEnabled= False
    grid.addWidget(self.bodRadioB1,0,0)
    grid.addWidget(self.bodRadioB2,1,0)
    grid.addWidget(self.bodSliderB,0,1)
    grid.addWidget(self.bodComboB,1,1)
    
    #========= Set the Alpha page ==============
    groupBox=qt.QGroupBox()
    grid = qt.QGridLayout(groupBox)
    alphaGrid.addWidget(groupBox,0,1)
    
    self.bodRadioA1=qt.QRadioButton("Fixed to:")
    self.bodRadioA2=qt.QRadioButton("Mapped to:")
    self.bodRadioA1.checked=True
       
    self.bodSliderA = ctk.ctkSliderWidget()
    self.bodSliderA.decimals = 0
    self.bodSliderA.minimum=0
    self.bodSliderA.maximum=255
    self.bodSliderA.value=1
    self.bodSliderA.enabled = True
    
    self.bodComboA = qt.QComboBox()
    self.bodComboA.duplicatesEnabled= False
    grid.addWidget(self.bodRadioA1,0,0)
    grid.addWidget(self.bodRadioA2,1,0)
    grid.addWidget(self.bodSliderA,0,1)
    grid.addWidget(self.bodComboA,1,1)

# 
# Tube Mapping Area
#
    tubeColorCollapsibleButton = ctk.ctkCollapsibleButton()
    tubeColorCollapsibleButton.text = "Tube Mapping"
    self.layout.addWidget(tubeColorCollapsibleButton)
    
    tubeVboxLayOut = qt.QVBoxLayout(tubeColorCollapsibleButton)
    
    # Add a TabWidget
    tubeTabWidget=qt.QTabWidget()
    tubeVboxLayOut.addWidget(tubeTabWidget)

    # Create three pages and the GridLayOut
    tubeColorPage=qt.QWidget()
    tubeColorGrid=qt.QGridLayout(tubeColorPage)
    tubeTabWidget.addTab(tubeColorPage,'Color')

    tubeSizePage=qt.QWidget()
    tubeSizeGrid=qt.QGridLayout(tubeSizePage)
    tubeTabWidget.addTab(tubeSizePage,'Size')

    #========= Set the color page ==============
    groupBox=qt.QGroupBox()
    grid = qt.QGridLayout(groupBox)
    tubeColorGrid.addWidget(groupBox,0,0)
            
    self.tubeRadioFixedTo=qt.QRadioButton("Fixed to")
    self.tubeRadioByOrientation=qt.QRadioButton("Color by orientation")
    self.tubeRadioSameAsCylinderBody=qt.QRadioButton("Same as Cylinder Body")
    
    self.tubeRadioByOrientation.checked=True
    
    grid.addWidget(self.tubeRadioFixedTo,0,0)
    grid.addWidget(self.tubeRadioByOrientation,1,0)
    grid.addWidget(self.tubeRadioSameAsCylinderBody,2,0)
    
    self.tubeColorButton=qt.QPushButton('Specifying Color')
    self.tubeColorButton.setAutoFillBackground(True)
    
    grid.addWidget(self.tubeColorButton,0,1)
    self.tubeColorButton.connect('clicked()', \
        self.onTubeFixedColor)

    #========= Set the size page ==============
    self.tubeSizeRadio1=qt.QRadioButton("Fixed to:")
    self.tubeSizeRadio2=qt.QRadioButton("Mapped to:")
    self.tubeSizeRadio1.checked=True
    self.tubeSizeSlider = ctk.ctkSliderWidget()
    self.tubeSizeSlider.decimals = 2
    self.tubeSizeSlider.minimum=0.0
    self.tubeSizeSlider.maximum=5.0
    self.tubeSizeSlider.value=0.1
    self.tubeSizeSlider.enabled = True
    self.tubeComboBox = qt.QComboBox()
    self.tubeComboBox.duplicatesEnabled= False  
    
    tubeSizeGrid.addWidget(self.tubeSizeRadio1,0,0)
    tubeSizeGrid.addWidget(self.tubeSizeRadio2,1,0)
    tubeSizeGrid.addWidget(self.tubeSizeSlider,0,1)
    tubeSizeGrid.addWidget(self.tubeComboBox,1,1)
    
    # ============Scale scroller=================
    label=qt.QLabel('Tube Scale:')
    self.sliderTubeScale = ctk.ctkSliderWidget()
    self.sliderTubeScale.decimals = 0
    self.sliderTubeScale.minimum=1
    self.sliderTubeScale.maximum=100
    self.sliderTubeScale.value=5
    self.sliderTubeScale.enabled = False
    tubeSizeGrid.addWidget(label,2,0)
    tubeSizeGrid.addWidget(self.sliderTubeScale,2,1)
    self.sliderTubeScale.connect('valueChanged(double)', \
         self.onTubeScaleChanged)

#    
# ============Apply button=================
#
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Apply the visualization."
    self.applyButton.enabled = False
    self.applyButton.setPalette(qt.QPalette(qt.QColor(128,255,128)))
    self.parent.layout().addWidget(self.applyButton) 
    self.applyButton.connect('clicked()', \
         self.onApply)
#
# ============Clear button=================
#
    self.clearButton = qt.QPushButton("Clear")
    self.clearButton.toolTip = "Clear objects rendered in 3D view windows."
    self.clearButton.enabled = False
    self.clearButton.setPalette(qt.QPalette(qt.QColor(255,128,128)))
    self.parent.layout().addWidget(self.clearButton)
    self.clearButton.connect('clicked()', \
        self.onClear)


# ===========Finally, Add vertical spacer================
    self.layout.addStretch(2)


#===========Response to GUI action=============================================
  def updateEnableState(self):
    enabled = bool(self.logic.inputFiberModel)
    self.modelSelector.enabled=enabled
    self.sliderGlyphSpace.enabled = enabled
    self.sliderGlyphScale.enabled = enabled
    self.sliderTubeScale.enabled = enabled
    self.checkboxLines.enabled=enabled
    self.checkboxTensor1.enabled=enabled
    self.checkboxTensor2.enabled=enabled
    self.checkboxTubes.enabled=enabled
    self.checkboxOnlyOneLine.enabled=enabled
    self.sliderLineNum.enabled=enabled
    self.sliderLineSpace.enabled=enabled
    
    self.applyButton.enabled = enabled
    self.clearButton.enabled = enabled
    
    
  def onModelSelect(self, node):  
    self.logic.inputFiberModel = node 
    
    self.updateEnableState()
    
    tmp=self.logic.inputFiberModel.GetPolyData()
    line_count=tmp.GetNumberOfLines()
    self.sliderLineNum.maximum=line_count
    self.sliderLineSpace.maximum=line_count
    
    self.checkboxTensor1.enabled=ExistTensor1(tmp)
    self.checkboxTensor2.enabled=ExistTensor2(tmp)
    
    if not self.checkboxTensor1.enabled:
        self.checkboxTensor1.checked=False
    if not self.checkboxTensor2.enabled:
        self.checkboxTensor2.checked=False
    
    
    dispModel=self.logic.inputFiberModel.GetDisplayNode()    
    dispModel.SetVisibility(False)
    
    inpointdata = tmp.GetPointData()
    
    self.bodComboR.clear()
    self.bodComboG.clear()
    self.bodComboB.clear()
    self.bodComboA.clear()
                
    self.tubeComboBox.clear()
    
    for idx in range(0,inpointdata.GetNumberOfArrays()):
        array = inpointdata.GetArray(idx)
        if array.GetNumberOfComponents()==1:
            self.bodComboR.addItem(array.GetName())
            self.bodComboG.addItem(array.GetName())
            self.bodComboB.addItem(array.GetName())
            self.bodComboA.addItem(array.GetName())
            
            self.tubeComboBox.addItem(array.GetName())
            
    #Initial color settings
    self.bodRadioR1.checked=True    
    self.bodSliderR.value=255
    self.bodRadioG1.checked=True    
    self.bodSliderG.value=0
    self.bodRadioB1.checked=True    
    self.bodSliderB.value=0
    self.bodRadioA1.checked=True    
    self.bodSliderA.value=255
    
  def onGlyphSpaceChanged(self,value):
    self.logic.glyphSpace=value;
    
  def onGlyphScaleChanged(self,value):
    self.logic.glyphScale=value;

  def onTubeScaleChanged(self,value):
    self.logic.tubeScale=value;

  def onLineNumChanged(self,value):
    self.logic.lineNum=value

  def onLineSpaceChanged(self,value):
    self.logic.lineSpace=value

  def onLineColorRChanged(sel,value):
    pass

  def onSelectLineColorR(self,text):
    pass
    
  def onApply(self):  
    if not (self.logic.inputFiberModel):
       qt.QMessageBox.critical( 
          slicer.util.mainWindow(),
          'Two-tensor Model Visualization', 'Input fiber model is required.')
       return False
    
    # Save check boxes status
    self.logic.onlyOneLine=self.checkboxOnlyOneLine.checked 
    self.logic.showLines=self.checkboxLines.checked
    self.logic.showTensor1=self.checkboxTensor1.checked
    self.logic.showTensor2=self.checkboxTensor2.checked
    self.logic.showTubes=self.checkboxTubes.checked 
    
    # save color setting status
    if self.bodRadioR1.checked:
        self.logic.bodRFlag=0
    else:
        self.logic.bodRFlag=1
            
    if self.bodRadioG1.checked:
        self.logic.bodGFlag=0
    else:
        self.logic.bodGFlag=1 
           
    if self.bodRadioB1.checked:
        self.logic.bodBFlag=0
    else:
        self.logic.bodBFlag=1   
         
    if self.bodRadioA1.checked:
        self.logic.bodAFlag=0
    else:
        self.logic.bodAFlag=1    
    
    self.logic.bodRValue=self.bodSliderR.value
    self.logic.bodGValue=self.bodSliderG.value
    self.logic.bodBValue=self.bodSliderB.value
    self.logic.bodAValue=self.bodSliderA.value
    
    self.logic.bodRName=self.bodComboR.currentText.encode('ascii')
    self.logic.bodGName=self.bodComboG.currentText.encode('ascii')
    self.logic.bodBName=self.bodComboB.currentText.encode('ascii')
    self.logic.bodAName=self.bodComboA.currentText.encode('ascii')
    
    # save tube params
    self.logic.tubeMappedToName=self.tubeComboBox.currentText.encode('ascii')
    if self.tubeSizeRadio1.checked:
       self.logic.tubeSizeFlag=0
    else:
       self.logic.tubeSizeFlag=1 
    
    if self.tubeRadioFixedTo.checked:
        self.logic.tubeColorFlag=0
    elif self.tubeRadioByOrientation.checked:
        self.logic.tubeColorFlag=1
    elif self.tubeRadioSameAsCylinderBody:
        self.logic.tubeColorFlag=2
    
    
    self.logic.apply()  

  def onClear(self):
    self.logic.clear()
  
  def onTubeFixedColor(self):
    dlg=qt.QColorDialog()

    color = dlg.getColor( self.logic.tubeFixedColor)
    
    if color.isValid():
        self.logic.tubeFixedColor = color
        self.tubeColorButton.setText(color.name())
        self.tubeColorButton.setPalette(qt.QPalette(color))
        

#==============================================================================
# TwoTensorModelVizLogic -- Logic for the module
#==============================================================================


class TwoTensorModelVizLogic:
  
  def __init__(self): 
    self.inputFiberModel = None
    self.glyphSpace=20
    self.glyphScale=2000
    self.tubeScale=5
    self.lineNum=1
    self.lineSpace=10
    self.showLines=True
    self.showTensor1=True
    self.showTensor2=True
    self.showTubes=False
    
    self.sactorCreated=False
    self.sactor=None;
    self.actor=None;
    self.ren=None;
    self.renWin=None
    self.mapper=None;
    self.onlyOneLine=False

    self.bodRFlag=0
    self.bodGFlag=0
    self.bodBFlag=0
    self.bodAFlag=0
    
    self.bodRValue=0
    self.bodGValue=0
    self.bodBValue=0
    self.bodAValue=0
    
    self.bodRName=""
    self.bodGName=""
    self.bodBName=""
    self.bodAName=""
   
    self.tubeFixedColor=qt.QColor(128,128,128,255)
    self.tubeMappedToName=""
    self.tubeFixedSize=1
    
    self.tubeColorFlag=0
    self.tubeSizeFlag=0
  
  def apply(self):
    if not (self.inputFiberModel):
       return False

    if self.sactorCreated:
        self.clear()
        self.sactorCreated=False
    
    self.Display()
    
    return True

  def clear(self):
    if self.sactorCreated:  
       self.ren.RemoveActor(self.sactor)
       self.renWin.Render()
       del self.sactor
       self.sactorCreated=False

  def Display(self):
    global inpd
    global params
   
    # Hide the original display object
    dispModel=self.inputFiberModel.GetDisplayNode()    
    dispModel.SetVisibility(False)
    
    #=================================================
    # Get the polydata
    inpd=self.inputFiberModel.GetPolyData()
    
    #=================================================
    # Set parameters for the rendering
    params['lineSpace']=self.lineSpace
    params['glyphSpace']=self.glyphSpace
    params['glyphScale']=self.glyphScale
    params['tubeScale']=self.tubeScale
    params['tubeFixedColor']=self.tubeFixedColor
    params['tubeFixedSize']=self.tubeFixedSize
    params['tubeMappedToName']=self.tubeMappedToName
    params['tubeColorFlag']=self.tubeColorFlag
    params['tubeSizeFlag']=self.tubeSizeFlag
    
    params['lineNum']=self.lineNum
    params['onlyOneLine']=self.onlyOneLine
    params['showLines']=self.showLines
    params['showTensor1']=self.showTensor1
    params['showTensor2']=self.showTensor2
    params['showTubes']=self.showTubes
    
    params['bodRFlag']=self.bodRFlag
    params['bodGFlag']=self.bodGFlag
    params['bodBFlag']=self.bodBFlag
    params['bodAFlag']=self.bodAFlag
    
    params['bodRValue']=self.bodRValue
    params['bodGValue']=self.bodGValue
    params['bodBValue']=self.bodBValue
    params['bodAValue']=self.bodAValue
    
    params['bodRName']=self.bodRName
    params['bodGName']=self.bodGName
    params['bodBName']=self.bodBName
    params['bodAName']=self.bodAName
    
    #=================================================
    # Get the rendering objects from Slicer
    self.renWin=slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow()
    self.ren   =self.renWin.GetRenderers().GetFirstRenderer()
    self.actor =self.ren.GetActors().GetLastActor()
    self.mapper=self.actor.GetMapper();
    
    #=================================================
    # Set the vtkPyOpenGLActor
    self.sactor = vtkPyOpenGLActor()
    self.sactor.SetMapper(self.mapper)
    self.sactor.SetScript('DrawScene(inpd,params)') 
    
    #=================================================
    # Update the rendering window
    self.ren.AddActor(self.sactor)
    self.sactorCreated=True
   
    self.renWin.Render()
    