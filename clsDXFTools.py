# -*- coding: utf-8 -*-
"""
/***************************************************************************
 A QGIS plugin
AnotherDXF2Shape: Add DXF to QGIS , optional georeferencing, optional convert DXF to Shape/GeoPackage
        copyright            : (C) 2020 by EZUSoft
        email                : qgis (at) makobo.de
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""





































































from random import randrange
from shutil import copyfile
import uuid
import sys
import os
import locale
from glob import glob
from shutil import copyfile, move

from qgis.core import *
from qgis.utils import *


try:

    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtCore import Qt
    from PyQt5 import QtGui, uic
    from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
    myqtVersion = 5
except:

    from PyQt4.QtCore import Qt
    from PyQt4 import QtGui, uic
    from PyQt4.QtSql import QSqlDatabase, QSqlQuery, QSqlError
    myqtVersion = 4


try:
    from .fnc4all  import *
    from .fnc4ADXF2Shape import *
    from .clsDBase import *
    from .TransformTools import *
except:
    from fnc4all  import *
    from fnc4ADXF2Shape import *
    from clsDBase import *
    from TransformTools import *
    







def tr( message):











    return QCoreApplication.translate('clsDXFTools', message)















def EditQML (datname):

    with open(datname, 'r') as file :
      filedata = file.read()


    filedata = filedata.replace('labelsEnabled="0"', 'labelsEnabled="1"')


    with open(datname, 'w') as file:
      file.write(filedata)



def labelingDXF (qLayer, bFormatText, bUseColor4Point, dblFaktor):       




    qLayer.setCustomProperty("labeling","pal")
    qLayer.setCustomProperty("labeling/displayAll","true")
    qLayer.setCustomProperty("labeling/enabled","true")
    if bFormatText:

        qLayer.setCustomProperty("labeling/fieldName","plaintext")
        qLayer.setCustomProperty("labeling/dataDefined/Underline","1~~1~~\"underline\"~~")
        qLayer.setCustomProperty("labeling/dataDefined/Bold","1~~1~~\"bold\"~~")  
        qLayer.setCustomProperty("labeling/dataDefined/Italic","1~~1~~\"italic\"~~")          
 
    else:
        qLayer.setCustomProperty("labeling/fieldName","Text")
    
    if bUseColor4Point:
        qLayer.setCustomProperty("labeling/dataDefined/Color","1~~1~~\"color\"~~") 
        


    sf = "%.1f" % dblFaktor
    sf = "1~~1~~" + sf + " * \"size\"~~"
    qLayer.setCustomProperty("labeling/dataDefined/Size",sf) 

    qLayer.setCustomProperty("labeling/dataDefined/Family","1~~1~~\"font\"~~")   
    qLayer.setCustomProperty("labeling/fontSizeInMapUnits","True")
    if myqtVersion == 5:
        qLayer.setCustomProperty("labeling/fontSizeUnit","MapUnit") 
    qLayer.setCustomProperty("labeling/dataDefined/Rotation","1~~1~~\"angle\"~~")
    qLayer.setCustomProperty("labeling/dataDefined/OffsetQuad", "1~~1~~\"anchor\"~~")


    qLayer.setCustomProperty("labeling/obstacle","false")
    qLayer.setCustomProperty("labeling/placement","1")
    qLayer.setCustomProperty("labeling/placementFlags","0")

    qLayer.setCustomProperty("labeling/textTransp","0")
    qLayer.setCustomProperty("labeling/upsidedownLabels","2")
    if myqtVersion == 5:
        qLayer.removeCustomProperty("labeling/ddProperties")

def kat4Layer(layer, bUseColor4Line,bUseColor4Poly):

    if myqtVersion == 4:
        fni = layer.fieldNameIndex('Layer')
        unique_values = layer.dataProvider().uniqueValues(fni)
    else:
        fni = layer.dataProvider().fieldNameIndex('Layer')
        unique_values = layer.dataProvider().uniqueValues(fni)

    symbol_layer = None

    categories = []
    for AktLayerNam in unique_values:
        if AktLayerNam == NULL:
            AktLayerNam = "" 

        if myqtVersion == 4:
            symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        else:
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())

        layer_style = {}
        if layer.geometryType() == 1 and bUseColor4Line:
            layer_style["color_dd_active"]="1"
            layer_style["color_dd_expression"]="\"color\""
            layer_style["color_dd_field"]="color"
            layer_style["color_dd_useexpr"]="0"
            if myqtVersion == 4:
                symbol_layer = QgsSimpleLineSymbolLayerV2.create(layer_style)
            else:
                symbol_layer = QgsSimpleLineSymbolLayer.create(layer_style)
        if layer.geometryType() == 2 and bUseColor4Poly:
            layer_style["color_dd_active"]="1"
            layer_style["color_dd_expression"]="\"fcolor\""
            layer_style["color_dd_field"]="fcolor"
            layer_style["color_dd_useexpr"]="0"
            layer_style['outline'] = '1, 234, 3'
            if myqtVersion == 4:
                symbol_layer = QgsSimpleFillSymbolLayerV2.create(layer_style)
            else:
                symbol_layer = QgsSimpleFillSymbolLayer.create(layer_style)
        
        if myqtVersion == 4:
            layer.setLayerTransparency(50)
        else:
            layer.setOpacity(0.5)

		




        



        if symbol_layer is not None:
            symbol.changeSymbolLayer(0, symbol_layer)
        

        if layer.geometryType() == 0:
           symbol.setSize( 0.1 )


        if myqtVersion == 4:
            category = QgsRendererCategoryV2(AktLayerNam, symbol, AktLayerNam)
        else:
            category = QgsRendererCategory(AktLayerNam, symbol, AktLayerNam)

        categories.append(category)


    if myqtVersion == 4:
        renderer = QgsCategorizedSymbolRendererV2('Layer', categories)
    else:
        renderer = QgsCategorizedSymbolRenderer('Layer', categories)

    return renderer

def DelShapeDatBlock (shpDat):

    try:
        rest=shpDat 
        os.remove(shpDat)
        for rest in glob(shpDat[0:-4] + '.*'):
            os.remove(rest)
        return True
    except OSError as e:  
        pass


    

def DelZielDateien (delDatArr,sOutForm):
    if len(delDatArr) > 0:
        s=("\n".join(delDatArr))
        antw=QMessageBox.question(None, tr("Overwriting the following files"), s, QMessageBox.Yes, QMessageBox.Cancel)
        if antw != QMessageBox.Yes:
            return None
        else:
            for dat in delDatArr:
                try:
                    rest=dat 
                    os.remove(dat)
                    if sOutForm == "SHP":
                        for rest in glob(dat[0:-4] + '.*'):
                            os.remove(rest)
                except OSError as e:  
                    QMessageBox.critical(None, tr("DZD:file remove error"),"Error: %s - %s." % (e.filename,e.strerror)) 
                    return None
    return True

def ProjDaten4Dat(AktDXFDatNam, bCol, bLayer, bZielSave, sOutForm):
    pList1=("P:POINT:LIKE \'%POINT%\'",
    "L:LINESTRING:LIKE '%LINE%'",
    "F:POLYGON:LIKE \'%POLYGON%\'")
    

    o1=" --config DXF_TRANSLATE_ESCAPE_SEQUENCES FALSE --config DXF_MERGE_BLOCK_GEOMETRIES FALSE --config DXF_INLINE_BLOCKS TRUE "
    
    pList2=("eP:POINT:LIKE \'%POINT%\'",
            "eL:LINESTRING:LIKE \'%LINE%\'",
            "eF:POLYGON:LIKE \'%POLYGON%\'",
            "cP:POINT:= 'GEOMETRYCOLLECTION'",
            "cL:LINESTRING:= 'GEOMETRYCOLLECTION'",
            "cF:POLYGON:= 'GEOMETRYCOLLECTION'")

    o2=" --config DXF_TRANSLATE_ESCAPE_SEQUENCES FALSE --config DXF_MERGE_BLOCK_GEOMETRIES TRUE --config DXF_INLINE_BLOCKS TRUE -dim 2 "
    
    (dummy,ProjektName) = os.path.split(AktDXFDatNam)
    ProjektName=ProjektName + '_' + sOutForm
    if bCol:
        AktList=pList2
        AktOpt=o2
        ProjektName=ProjektName + '(GC-'
    else:
        AktList=pList1
        AktOpt=o1
        ProjektName=ProjektName + '('
    if bLayer:
        ProjektName=ProjektName + 'byLay)'
    else:
        ProjektName=ProjektName + 'byKat)'
    if bZielSave:
        if ProjektName[-4:]==".dxf":
            Kern=ProjektName[0:-4]
        else:    
            Kern=ProjektName
    else:
        Kern=str(uuid.uuid4())    
        
    
    return AktList,AktOpt,ProjektName, Kern

def DXFImporter(uiParent, sOutForm, listDXFDatNam, zielPfadOrDatei, bZielSave, sCharSet,  bCol, bLayer, bFormatText, bUseColor4Point, bUseColor4Line, bUseColor4Poly, dblFaktor, chkTransform, DreiPassPunkte, bGen3D ):    



    import processing
    from processing.core.Processing import Processing

    


    delZielDat=[]
    for i in range(listDXFDatNam.count()):
        AktDXFDatNam=listDXFDatNam.item(i).text()

        AktList,AktOpt,ProjektName, Kern =ProjDaten4Dat(AktDXFDatNam, bCol, bLayer, bZielSave, sOutForm)
        

        rNode=QgsProject.instance().layerTreeRoot()
        for node in rNode.children():
            if str(type(node))  == "<class 'qgis._core.QgsLayerTreeGroup'>":
                if node.name() == ProjektName:
                        rNode.removeChildNode(node)
      

        if bZielSave:
            if sOutForm == "SHP":
                for p in AktList:
                    v = p.split(":")
                    shpdat=zielPfadOrDatei+Kern+v[0]+'.shp'
                    if os.path.exists(shpdat):
                        delZielDat.append (shpdat)
            if sOutForm == "GPKG":
                gpkgdat=zielPfadOrDatei+Kern+'.gpkg'
                if os.path.exists(gpkgdat):
                    delZielDat.append (gpkgdat)
    
    if not DelZielDateien (delZielDat, sOutForm):
        QMessageBox.information(None, tr("Cancel"), tr("Please set target"))
        return None
    





    
    

    


    mLay=QgsVectorLayer('LineString?crs=EPSG:4326','' , 'memory')

    mem0Dat=EZUTempDir() + str(uuid.uuid4()) + '.shp'
    

    if myQGIS_VERSION_INT() < 31003:
        Antw=QgsVectorFileWriter.writeAsVectorFormat(mLay,mem0Dat,  None, mLay.crs(), "ESRI Shapefile")
    else:
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        Antw=QgsVectorFileWriter.writeAsVectorFormatV2(mLay,mem0Dat, QgsCoordinateTransformContext(), options)

   

    if type(Antw) != tuple:
        Antw = Antw , "error by creating memorylayer" 
    
    
    



    if Antw[0] != 0:
        addFehler(tr("Error create memorylayer: " + Antw[1]))
    else:

        try:

            os.remove(mem0Dat[0:-3] + 'qpj')
        except:
            pass
        try:
            os.remove(mem0Dat[0:-3] + 'prj')

            mLay=QgsVectorLayer(mem0Dat, '' , 'ogr')
        except OSError as e: 
            addFehler("delete memorylayer: %s - %s." % (e.filename,e.strerror)) 


    memDat=EZUTempDir() + str(uuid.uuid4()) + '.shp'

    if myQGIS_VERSION_INT() < 31003:
        Antw=QgsVectorFileWriter.writeAsVectorFormat(mLay,memDat,  None, mLay.crs(), "ESRI Shapefile")
    else:
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        Antw=QgsVectorFileWriter.writeAsVectorFormatV2(mLay,memDat, QgsCoordinateTransformContext(), options)

    
    qPrjDatName=memDat[0:-3] + 'qpj'

    if not (os.path.exists(qPrjDatName)):
        qPrjDatName=memDat[0:-3] + 'prj'




    if myqtVersion == 4:
        crsArtQ2=QSettings().value('/Projections/defaultBehaviour')
        QSettings().setValue('/Projections/defaultBehaviour','useGlobal')
    else:




        crsArtQ3_1=QSettings().value('/Projections/defaultBehavior')
        crsArtQ3_2=QSettings().value('/app/projections/unknownCrsBehavior')
        QSettings().setValue('/Projections/defaultBehavior','useGlobal')
        QSettings().setValue('/app/projections/unknownCrsBehavior','UseDefaultCrs')
    crsDefWert = QSettings().value('/Projections/layerDefaultCrs')
    QSettings().setValue('/Projections/layerDefaultCrs',mLay.crs().authid())  
    
    

    try:





        uiParent.FormRunning(True)
        uiParent.SetDatAktionGesSchritte(8)    
        uiParent.SetAktionText("")
        uiParent.SetDatAktionText(tr("process init - please wait"))
        uiParent.SetDatAktionAktSchritt(1)

        Processing.initialize()




        uiParent.SetDatAktionGesSchritte(listDXFDatNam.count())
        for i in range(listDXFDatNam.count()):
            AktDXFDatNam=listDXFDatNam.item(i).text()
            if myqtVersion == 5:
                uiParent.SetDatAktionText(tr("Import: " + AktDXFDatNam ))
            else:
                uiParent.SetDatAktionText(tr("Import: " + AktDXFDatNam.encode("utf8") ))
            uiParent.SetDatAktionAktSchritt(i+1)
            
            AktList,AktOpt,ProjektName, Kern = ProjDaten4Dat(AktDXFDatNam,bCol,bLayer, bZielSave, sOutForm)

            
            iface.mapCanvas().setRenderFlag( False )    

                  

            root = QgsProject.instance().layerTreeRoot()
            grpProjekt = root.addGroup( ProjektName)

            grpProjekt.setExpanded(True)

           

            okTransform=chkTransform
            if chkTransform and DreiPassPunkte == None:

                wldDat=os.path.splitext(AktDXFDatNam)[0] + ".wld"
                if os.path.exists(wldDat):
                    p=[[],[],[]]
                    p[0], p[1], Fehler = ReadWldDat(wldDat)
                    if Fehler == None:

                        if p[1] == None:

                            p[0], p[1], p[2] = Helmert4Points(p[0], None)

                        p[0], p[1], p[2] = Helmert4Points(p[0],p[1])
                        DreiPassPunkte = p
                    else:
                        okTransform=False
                        addFehler (wldDat + ": " + Fehler)
                else:
                    okTransform=False
                    addFehler(wldDat + ": " + tr("file not found"))
            Antw = EineDXF (uiParent, mLay.crs(), bZielSave, sOutForm, grpProjekt, AktList, Kern, AktOpt, AktDXFDatNam, zielPfadOrDatei, qPrjDatName, sCharSet, bLayer, bFormatText, bUseColor4Point,bUseColor4Line,bUseColor4Poly, dblFaktor, okTransform, DreiPassPunkte, bGen3D)            
    except:
        subLZF ()
    
    



    
    if myqtVersion == 4:
        QSettings().setValue('/Projections/defaultBehaviour',crsArtQ2)
    else:
        QSettings().setValue('/Projections/defaultBehavior',crsArtQ3_1)
        QSettings().setValue('/app/projections/unknownCrsBehavior',crsArtQ3_2)
    QSettings().setValue('/Projections/layerDefaultCrs',crsDefWert)
    

    if len(getFehler()) > 0:
        errbox("\n\n".join(getFehler()))
        resetFehler()
    if len(getHinweis()) > 0:
        hinweislog("\n\n".join(getHinweis()))
        resetHinweis()        
    
    uiParent.FormRunning(False)
        
def EineDXF(uiParent, mLay_crs, bZielSave, sOutForm, grpProjekt,AktList, Kern, AktOpt, DXFDatNam, zielPfadOrDatei, qPrjDatName, sOrgCharSet, bLayer, bFormatText, bUseColor4Point,bUseColor4Line,bUseColor4Poly, dblFaktor,chkTransform, DreiPassPunkte, bGen3D):



    import processing
    from processing.core.Processing import Processing
   

    if sOutForm != "SHP" and sOutForm != "GPKG":
        errbox("Formatfehler: '" + sOutForm + "'")
        return False
        
 
    sCharSet=sOrgCharSet
    myGroups={}
    








    


    if ifAscii(DXFDatNam):
        korrDXFDatNam=DXFDatNam
    else:
        uiParent.SetAktionGesSchritte(2)
        uiParent.SetAktionText(tr("Copy DXF-File"))
        uiParent.SetAktionAktSchritt(1)
        korrDXFDatNam=(EZUTempDir() + str(uuid.uuid4()) + '.dxf')
        copyfile(DXFDatNam, korrDXFDatNam)

    
    optGCP = ""
    if chkTransform:
        for p in range(len(DreiPassPunkte)):
            optGCP = optGCP + " -gcp "
            for k in range(len(DreiPassPunkte[p])):
                optGCP = optGCP + str(DreiPassPunkte[p][k][0]) + " " +  str(DreiPassPunkte[p][k][1]) + " "

        if optGCP[-5:]=="-gcp ":
            optGCP=optGCP[:-5]

    zE=0
    uiParent.SetAktionGesSchritte(len(AktList))
    

    if sOutForm == "GPKG":
        gpkgdat=zielPfadOrDatei+Kern+'.gpkg'
        

        if bZielSave:
            korrGPKGDatNam=gpkgdat    
        else:
            korrGPKGDatNam=(EZUTempDir() + str(uuid.uuid4()) + '.gpkg') 
        
                
    for p in AktList:
        zE=zE+1       
        v = p.split(":")
        if myqtVersion == 5:
            uiParent.SetAktionText(tr("Edit Entity: " + Kern+v[0] ))
        else:
            uiParent.SetAktionText(tr("Edit Entity: " + Kern.encode("utf8")+v[0] ))
        
        uiParent.SetAktionAktSchritt(zE)
        if sOutForm == "SHP":
            iOutForm = 0 
            shpdat=zielPfadOrDatei+Kern+v[0]+'.shp'
            qmldat=zielPfadOrDatei+Kern+v[0]+'.qml'
        
        if sOutForm == "GPKG":
            qmldat =  EZUTempDir() + str(uuid.uuid4()) + '.qml'
            gpkgTable=Kern+v[0]

        








        if sOutForm == "SHP":
            if bZielSave:
                korrSHPDatNam=(EZUTempDir() + str(uuid.uuid4()) + '.shp') 
            else:
                korrSHPDatNam=shpdat            

        bKonvOK=False

        try:
            if sOutForm == "SHP":
                opt = ('-skipfailure %s -nlt %s %s -sql "select *, ogr_style from entities where OGR_GEOMETRY %s"') % (AktOpt,v[1],optGCP,v[2])      
                if bGen3D:
                    opt = opt +  ' -dim 3 '

                if myqtVersion == 4:
                    pAntw=processing.runalg('gdalogr:convertformat',korrDXFDatNam , 0, opt , korrSHPDatNam)
                else:

                    pList={'INPUT':korrDXFDatNam,'OPTIONS':opt,'OUTPUT': korrSHPDatNam}
                    pAntw=processing.run('gdal:convertformat',pList) 

                if os.path.exists(korrSHPDatNam): bKonvOK = True
            
            if sOutForm == "GPKG":

                if sCharSet == "System":
                    ogrCharSet=locale.getdefaultlocale()[1]
                else:
                    ogrCharSet=sCharSet
                ogrCharSet=ogrCharSet.upper()              
 
                opt = '-append -update --config DXF_ENCODING "' + ogrCharSet + '" '
                

                opt = opt + '--config DXF_INCLUDE_RAW_CODE_VALUES TRUE '
                opt = opt + ('%s -nlt %s %s -sql "select *, ogr_style from entities where OGR_GEOMETRY %s" -nln "%s"') % (AktOpt,v[1],optGCP,v[2], gpkgTable)      
                if bGen3D:
                    opt = opt +  ' -dim 3 '
                


                pList={'INPUT':korrDXFDatNam,'OPTIONS':opt,'OUTPUT': korrGPKGDatNam}
                pAntw=processing.run('gdal:convertformat',pList) 


                if os.path.exists(korrGPKGDatNam):bKonvOK = True 
               
        except:
            addFehler(tr("Error processing: " + DXFDatNam))
            return False

        if pAntw is None:
            addFehler(tr("process 'gdalogr:convertformat' could not start please restart QGIS"))
        else:
            if sOutForm == "SHP":
                if myqtVersion == 5:


                    aktShapeName=korrSHPDatNam
                    korrSHPDatNam=(EZUTempDir() + str(uuid.uuid4()) + '.shp') 

                    

                    if os.path.exists(qPrjDatName) : 
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"qpj")
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"prj")

                    ShapeCodepage2Utf8 (aktShapeName, korrSHPDatNam,  sOrgCharSet) 
                    sCharSet="utf-8"
                else:
                    aktShapeName=korrSHPDatNam
                
            if bKonvOK:
                if sOutForm == "SHP":
                    attTableEdit(sOutForm,korrSHPDatNam,bFormatText,sCharSet)
                    if korrSHPDatNam != shpdat:


                        move(korrSHPDatNam,shpdat)
                        for rest in glob(korrSHPDatNam[0:-4] + '.*'):

                            move(rest,shpdat[0:-4] + rest[-4:])




                    

                    if os.path.exists(qPrjDatName) : 
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"qpj")
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"prj")
                    Layer = QgsVectorLayer(shpdat, "entities"+v[0],"ogr") 

                 


                    Layer.setProviderEncoding(sCharSet)
                    Layer.dataProvider().setEncoding(sCharSet) 
                
                if sOutForm == "GPKG":
                    attTableEdit(sOutForm,korrGPKGDatNam,bFormatText,sCharSet,gpkgTable)
                    sLayer="%s|layername=%s" %(korrGPKGDatNam,gpkgTable) 
                    Layer = QgsVectorLayer(sLayer, "entities"+v[0],"ogr") 
                    Layer.setCrs(mLay_crs)
                    if Layer.featureCount() < 0: Layer=None 





                if Layer:

                    bLayerMitDaten = False
                    if Layer.featureCount() > 0:
                        koo=Layer.extent()
                        if koo.xMinimum() == 0 and koo.yMinimum() == 0 and koo.xMaximum() == 0 and koo.yMaximum() == 0:

                            addHinweis("Empty coordinates for " + opt )
                        else:
                            bLayerMitDaten  = True
                    else:
                        addHinweis("No entities for " + opt )


                    if bLayerMitDaten:
                        if not bLayer:



                            if myqtVersion == 4:
                                QgsMapLayerRegistry.instance().addMapLayer(Layer, False)
                            else:
                                Layer = QgsProject.instance().addMapLayer(Layer, False) 

                            ml=grpProjekt.addLayer(Layer)
                            ml.setExpanded(False)


                            Rend=kat4Layer(Layer, bUseColor4Line, bUseColor4Poly)
                            if Rend is not None:
                                if myqtVersion == 4:
                                    Layer.setRendererV2(Rend)
                                else:
                                    Layer.setRenderer(Rend)
                            else:
                                addFehler ("Categorization for  " + opt + " could not be executed")
                            
                            if Layer.geometryType() == 0:
                                labelingDXF (Layer,bFormatText, bUseColor4Point, dblFaktor)                               
                                if Layer.geometryType() == 0 and myqtVersion == 5:
                                    Layer.saveNamedStyle (qmldat)
                                    EditQML (qmldat)
                                    Layer.loadNamedStyle(qmldat)

                        else:

                            if myqtVersion == 4:
                                fni = Layer.fieldNameIndex('Layer')
                            else:
                                fni = Layer.dataProvider().fieldNameIndex('Layer')
                            unique_values = Layer.dataProvider().uniqueValues(fni)
                            zL=0
                            for AktLayerNam in unique_values:
                                OrgLayerNam = AktLayerNam
                                if AktLayerNam == NULL:
                                    AktLayerNam = "NULL" 
                                else:                                  
                                    AktLayerNam = DecodeDXFUTF(AktLayerNam)
                                uiParent.SetAktionGesSchritte(len(unique_values))
                                uiParent.SetAktionText("Edit Layer: " + AktLayerNam )
                                uiParent.SetAktionAktSchritt(zL)
                                zL=zL+1
                                if sOutForm == "SHP":
                                    Layer = QgsVectorLayer(shpdat, AktLayerNam+'('+v[0]+')',"ogr")


                                    Layer.setProviderEncoding(sCharSet)
                                    Layer.dataProvider().setEncoding(sCharSet)   
                                    if OrgLayerNam == NULL:
                                        Layer.setSubsetString( "Layer is Null" )
                                    else:
                                        Layer.setSubsetString( "Layer = '" + OrgLayerNam + "'" )
                                else:
                                    Layer = QgsVectorLayer(sLayer, AktLayerNam+'('+v[0]+')',"ogr") 
                                    Layer.setCrs(mLay_crs)
                                    if OrgLayerNam == NULL:
                                        Layer.setSubsetString( "Layer is Null" )
                                    else:
                                        Layer.setSubsetString( "Layer = '" + OrgLayerNam + "'" )
                                    if Layer.featureCount() < 0: Layer=None 

                                if myqtVersion == 4:
                                    QgsMapLayerRegistry.instance().addMapLayer(Layer, False)
                                else:
                                    Layer = QgsProject.instance().addMapLayer(Layer, False) 


                                if AktLayerNam not in myGroups:

                                    gL = grpProjekt.addGroup( AktLayerNam)
                                    myGroups[AktLayerNam]=gL



                                    gL.addLayer(Layer)
                                    gL.setExpanded(False)

                                else:

                                    myGroups[AktLayerNam].addLayer(Layer)
                                    
                                if Layer.geometryType() == 0:
                                    if myqtVersion == 4:
                                        symbol = QgsSymbolV2.defaultSymbol(Layer.geometryType())
                                        Layer.setRendererV2(QgsSingleSymbolRendererV2( symbol ) )  
                                    else:
                                        symbol = QgsSymbol.defaultSymbol(Layer.geometryType())
                                        Layer.setRenderer(QgsSingleSymbolRenderer( symbol ) )
                                                                            
                                    symbol.setSize( 0.1 )
                                    labelingDXF (Layer, bFormatText, bUseColor4Point, dblFaktor)
                                    if Layer.geometryType() == 0 and myqtVersion == 5:
                                        Layer.saveNamedStyle (qmldat)
                                        EditQML (qmldat)
                                        Layer.loadNamedStyle(qmldat)

                                if Layer.geometryType() == 1 and bUseColor4Line:
                                    if myqtVersion == 4:
                                        lineMeta = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleLine")
                                        symbol = QgsSymbolV2.defaultSymbol(Layer.geometryType())
                                        renderer = QgsRuleBasedRendererV2(symbol)
                                    else:
                                        registry = QgsSymbolLayerRegistry()
                                        lineMeta = registry.symbolLayerMetadata("SimpleLine")
                                        symbol = QgsSymbol.defaultSymbol(Layer.geometryType())
                                        renderer = QgsRuleBasedRenderer(symbol)
                                        
                                    root_rule = renderer.rootRule()
                                    rule = root_rule.children()[0].clone()
                                    symbol.deleteSymbolLayer(0)
                                    qmap={}
                                    qmap["color_dd_active"]="1"
                                    qmap["color_dd_expression"]="\"color\""
                                    qmap["color_dd_field"]="color"
                                    qmap["color_dd_useexpr"]="0"
                                    lineLayer = lineMeta.createSymbolLayer(qmap)
                                    symbol.appendSymbolLayer(lineLayer)
                                    rule.setSymbol(symbol)
                                    rule.appendChild(rule) 
                                    if myqtVersion == 4:
                                        Layer.setRendererV2(renderer) 
                                    else:
                                        Layer.setRenderer(renderer)
                                if Layer.geometryType() == 2 and bUseColor4Poly:
                                    if myqtVersion == 4:
                                        fillMeta = QgsSymbolLayerV2Registry.instance().symbolLayerMetadata("SimpleFill")
                                        symbol = QgsSymbolV2.defaultSymbol(Layer.geometryType())
                                        renderer = QgsRuleBasedRendererV2(symbol)
                                    else:
                                        registry = QgsSymbolLayerRegistry()
                                        fillMeta = registry.symbolLayerMetadata("SimpleFill")
                                        symbol = QgsSymbol.defaultSymbol(Layer.geometryType())
                                        renderer = QgsRuleBasedRenderer(symbol)
                                    root_rule = renderer.rootRule()
                                    rule = root_rule.children()[0].clone()
                                    symbol.deleteSymbolLayer(0)
                                    qmap={}
                                    qmap["color_dd_active"]="1"
                                    qmap["color_dd_expression"]="\"fccolor\""
                                    qmap["color_dd_field"]="fcolor"
                                    qmap["color_dd_useexpr"]="0"
                                    lineLayer = fillMeta.createSymbolLayer(qmap)
                                    symbol.appendSymbolLayer(lineLayer)
                                    rule.setSymbol(symbol)
                                    rule.appendChild(rule) 
                                    if myqtVersion == 4:
                                        Layer.setRendererV2(renderer)
                                        Layer.setLayerTransparency(50)                                        
                                    else:
                                        Layer.setRenderer(renderer)
                                        Layer.setOpacity(0.5)
                        

                        if sOutForm == "SHP":
                            Layer.saveNamedStyle (qmldat)
                        else:
                            Layer.saveStyleToDatabase(gpkgTable, gpkgTable, True, "")

                    else:
                        Layer=None 
                        if sOutForm == "SHP":
                            if not DelShapeDatBlock(shpdat):
                                DelShapeDatBlock(shpdat)
                    

                else:
                    addHinweis (tr("Option '%s' could not be executed")%  opt )
            else:
                if sOutForm == "SHP":
                    addFehler(tr("Creation '%s' failed. Please look to the QGIS log message panel (OGR)") % shpdat )
                else:
                    addFehler(tr("Creation '%s' failed. Please look to the QGIS log message panel (OGR)") % korrGPKGDatNam )


    uiParent.SetAktionGesSchritte(2)
    uiParent.SetAktionText(tr("Switch on the display") )
    uiParent.SetAktionAktSchritt(1)
    iface.mapCanvas().setRenderFlag( True )
    
    return True
       








if __name__ == "__main__":
    import os
    try:
        os.kill(1234, 0)
    except OSError as e:  
        print( "Fehler: %s - %s." % (e.filename,e.strerror)) 


        
        









