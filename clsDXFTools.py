# -*- coding: utf-8 -*-
"""
/***************************************************************************
 clsDXFTools
    Stand 11.11.2022: Erweiterung um "labeling/dataDefined/OffsetXY"
    Stand 18.03.2021: Fehler GCP 
    Stand 01.03.2021: 3D Option jetzt auch (korrekter Weise) für GeoPackage
    Stand 02.03.2020:
        Korrekturen für QGIS 2.x
    Stand 27.02.2020: 
        ab QGIS 3.10.x wird keine qpj mehr generiert
        Fehler im Zusammenhang mit Memorylayer abfangen/auswerten (Luciano Giliberto)
        
    Stand 23.10.2019: Bei "DelShapeDatBlock" eine Fehlermeldung mehr
    Stand 09.09.2019:
        except (OSError, e): ->  except OSError as e:
    Stand 09.07.2019: Optional 3D
    Stand 27.02.2019: Anpassung an neues GDAL, welches standardmäßig %%-Formatierung schluckt
                      --config DXF_TRANSLATE_ESCAPE_SEQUENCES  FALSE
    Stand 28.03.2018: Umstellung/Erweiterung auf GeoPackage
    
    Stand 28.03.2018: Fehler beim EditQML beseitigt
    Stand 28.03.2018: Fehler beim CharSet-Handling beseitigt
    Stand 19.03.2018: DXF (testweise) nur noch bei Notwendigleit kopieren
    Stand 10.11.2017: Einheitliche Grundlage QT4/QT5
    Änderungen V0.9:
        Georeferenzieruzngsmodul
    Änderungen V0.81.2:
        processing.runalg funktioniert auf einem einzelnen Rechner nicht: Protokoll unter OGR: existiert nicht
        gefixt indem "|layername=entities" ersatzlos gestrichen
    Änderungen V0.8:
        01.03.17
            - Speicherung der Darstellung in einer QML-Datei (Layer.saveNamedStyle (qmldat))
    Änderungen V0.7.1:
        23.02.17
            - Processingbibliothek  erst in den Funktionen selbst laden, um den Start von QGIS zu beschleunigen
              das PlugIn nimmt angeblich fast 45s Startzeit, mit diesem Umbau wird daraus < 1s ohne dass die Zeit
              später "nachgeholt" wird.
        
    Änderungen V0.7:
        21.02.17: Shape grundsätzlich als Kopie, weil auch Leerzeichen im Pfad zu Problemen führt 
    Änderungen V0.5:
        20.12.16 
            - Layer auf transparent 50%
        16.12.16
            - Übernahme Farben aus DXF

    Änderungen V0.4.1:
        25.11.16:
            - Fehlerkorrektur
              line 368, in EineDXF: NameError: global name 'bFormat' is not defined
              line 86: strpos(Text,'\\\\\\L') --> strpos(\"Text\",'\\\\\\\\L')
              regexp_replace(regexp_substr( "text" ,'\\;(.*)\\}' ),'\\L','')

    Änderungen V0.4:
        21.11.16:
            - Kontrolle, ob Shape von Konverter erzeugt wurde
            - Stapelimport integriert
        09.11.16: 
            - Layername NULL abgefangen
    Änderungen V0.3.1:
        07.07.16:
            - Codepage auch bei Layerstruktur
            - shapes ohne Koordinaten aussortieren
            - jede Konvertierungsart mit Einzelprojekt (bisher 2 jetzt 4)
            - Auswahl eines CharSet (codepage)
            - nicht konvertierbare 3D Blöcke in 2D umwandeln
            
                                 A QGIS plugin
 KonverDXF to shape and add to QGIS
                             -------------------
        begin                : 2016-06-20
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Mike Blechschmidt EZUSoft 
        email                : qgis@makobo.de
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
#    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtCore import Qt
    from PyQt5 import QtGui, uic
    from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
    myqtVersion = 5
except:
#    from PyQt4.QtGui import *
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
    
"""
# 23.02.17
# Processing erst in den Funktionen selbst laden, um den Start von QGIS zu beschleunigen
import processing
from processing.core.Processing import Processing
"""

def tr( message):
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate('clsDXFTools', message)

"""
def joinDXFLabel(dxfLayer,csvLayer):
    dxfField='EntityHand'
    csvField='Handle'
    joinObject = QgsVectorJoinInfo()
    joinObject.joinLayerId = csvLayer.id()
    joinObject.joinFieldName = csvField
    joinObject.targetFieldName = dxfField
    dxfLayer.addJoin(joinObject)
    
def addCSVLayer(csvDatNam):
    uri = csvDatNam + '?type=csv&delimiter=%5Ct&spatialIndex=no&subsetIndex=no&watchFile=no'
    return QgsVectorLayer(uri, str(uuid.uuid4()), 'delimitedtext')
"""
def EditQML (datname):
# Read in the file
    with open(datname, 'r') as file :
      filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('labelsEnabled="0"', 'labelsEnabled="1"')

    # Write the file out again
    with open(datname, 'w') as file:
      file.write(filedata)



def labelingDXF (qLayer, bFormatText, bUseColor4Point, dblFaktor):       
    # Textdarstellung über Punktlabel
    #if myqtVersion == 4:
    #    QgsPalLayerSettings().writeToLayer( qLayer )
    # alternative für 5 noch unbekannt
    qLayer.setCustomProperty("labeling","pal")
    qLayer.setCustomProperty("labeling/displayAll","true")
    qLayer.setCustomProperty("labeling/enabled","true")
    if bFormatText:
        # Einstellungen aus Textformatcode
        qLayer.setCustomProperty("labeling/fieldName","plaintext")
        qLayer.setCustomProperty("labeling/dataDefined/Underline","1~~1~~\"underline\"~~")
        qLayer.setCustomProperty("labeling/dataDefined/Bold","1~~1~~\"bold\"~~")  
        qLayer.setCustomProperty("labeling/dataDefined/Italic","1~~1~~\"italic\"~~")          
 
    else:
        qLayer.setCustomProperty("labeling/fieldName","Text")
    
    if bUseColor4Point:
        qLayer.setCustomProperty("labeling/dataDefined/Color","1~~1~~\"color\"~~") 
        
    # Einstellungen aus DXF bzw. aus Textformatcode
    # !!! str(dblFaktor) funktioniert in 2.18 nicht da type 'future.types.newstr.newstr'
    sf = "%.1f" % dblFaktor
    sf = "1~~1~~" + sf + " * \"size\"~~"
    qLayer.setCustomProperty("labeling/dataDefined/Size",sf) 

    qLayer.setCustomProperty("labeling/dataDefined/Family","1~~1~~\"font\"~~")   
    qLayer.setCustomProperty("labeling/fontSizeInMapUnits","True")
    if myqtVersion == 5:
        qLayer.setCustomProperty("labeling/fontSizeUnit","MapUnit") # neu in QGIS 3.0  
    qLayer.setCustomProperty("labeling/dataDefined/Rotation","1~~1~~\"angle\"~~")
    qLayer.setCustomProperty("labeling/dataDefined/OffsetQuad", "1~~1~~\"anchor\"~~")
    
    # 11.11.22
    qLayer.setCustomProperty("labeling/dataDefined/OffsetXY", "1~~1~~array(\"dx\",-\"dy\")~~")

    # allgemeine Standardeinstellungen    
    qLayer.setCustomProperty("labeling/obstacle","false")
    qLayer.setCustomProperty("labeling/placement","1")
    qLayer.setCustomProperty("labeling/placementFlags","0")

    qLayer.setCustomProperty("labeling/textTransp","0")
    qLayer.setCustomProperty("labeling/upsidedownLabels","2")
    if myqtVersion == 5:
        qLayer.removeCustomProperty("labeling/ddProperties")

def kat4Layer(layer, bUseColor4Line,bUseColor4Poly):
    # get unique values 
    if myqtVersion == 4:
        fni = layer.fieldNameIndex('Layer')
        unique_values = layer.dataProvider().uniqueValues(fni)
    else:
        fni = layer.dataProvider().fieldNameIndex('Layer')
        unique_values = layer.dataProvider().uniqueValues(fni)

    symbol_layer = None
    # define categories
    categories = []
    for AktLayerNam in unique_values:
        if AktLayerNam == NULL:
            AktLayerNam = "" # 'Null' nach '' sonst funktioniert der Kategrisierung nicht
        # initialize the default symbol for this geometry type
        if myqtVersion == 4:
            symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
        else:
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        # configure a symbol layer
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

		#else:
        #    layer_style['color'] = '%d, %d, %d' % (randrange(0,256), randrange(0,256), randrange(0,256))
        #layer_style['color'] = '1, 2, 234'
        #layer_style['line_width'] = '12.3'
        #print "hier"
        


        # replace default symbol layer with the configured one
        if symbol_layer is not None:
            symbol.changeSymbolLayer(0, symbol_layer)
        
        # Textlayer
        if layer.geometryType() == 0:
           symbol.setSize( 0.1 )

        # create renderer object
        if myqtVersion == 4:
            category = QgsRendererCategoryV2(AktLayerNam, symbol, AktLayerNam)
        else:
            category = QgsRendererCategory(AktLayerNam, symbol, AktLayerNam)
        # entry for the list of category items
        categories.append(category)

    # create renderer object
    if myqtVersion == 4:
        renderer = QgsCategorizedSymbolRendererV2('Layer', categories)
    else:
        renderer = QgsCategorizedSymbolRenderer('Layer', categories)
    # assign the created renderer to the layer
    return renderer

def DelShapeDatBlock (shpDat):
    # 29.10.19: Keine Fehlermeldung mehr, da unwichtig (nur bei Emil gibt es eine Fehlermeldung?!)
    try:
        rest=shpDat # für Fehlermeldung
        os.remove(shpDat)
        for rest in glob(shpDat[0:-4] + '.*'):
            os.remove(rest)
        return True
    except OSError as e:  ## if failed, report it back to the user ##
        pass
    #    QMessageBox.critical(None, tr("DSDB:file remove error"),"Error: %s - %s." % (e.filename,e.strerror)) 
    #    return None
    

def DelZielDateien (delDatArr,sOutForm):
    if len(delDatArr) > 0:
        s=("\n".join(delDatArr))
        antw=QMessageBox.question(None, tr("Overwriting the following files"), s, QMessageBox.Yes, QMessageBox.Cancel)
        if antw != QMessageBox.Yes:
            return None
        else:
            for dat in delDatArr:
                try:
                    rest=dat # für Fehlermeldung
                    os.remove(dat)
                    if sOutForm == "SHP":
                        for rest in glob(dat[0:-4] + '.*'):
                            os.remove(rest)
                except OSError as e:  ## if failed, report it back to the user ##
                    QMessageBox.critical(None, tr("DZD:file remove error"),"Error: %s - %s." % (e.filename,e.strerror)) 
                    return None
    return True

def ProjDaten4Dat(AktDXFDatNam, bCol, bLayer, bZielSave, sOutForm):
    pList1=("P:POINT:LIKE \'%POINT%\'",
    "L:LINESTRING:LIKE '%LINE%'",
    "F:POLYGON:LIKE \'%POLYGON%\'")
    
    # 27.02.19: --config DXF_TRANSLATE_ESCAPE_SEQUENCES FALSE
    o1=" --config DXF_TRANSLATE_ESCAPE_SEQUENCES FALSE --config DXF_MERGE_BLOCK_GEOMETRIES FALSE --config DXF_INLINE_BLOCKS TRUE "
    
    pList2=("eP:POINT:LIKE \'%POINT%\'",
            "eL:LINESTRING:LIKE \'%LINE%\'",
            "eF:POLYGON:LIKE \'%POLYGON%\'",
            "cP:POINT:= 'GEOMETRYCOLLECTION'",
            "cL:LINESTRING:= 'GEOMETRYCOLLECTION'",
            "cF:POLYGON:= 'GEOMETRYCOLLECTION'")
    # dim 2 (3D->2D): 3D Geometriecollections können nicht konvertiert werden 
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
    #print(sOutForm, listDXFDatNam, zielPfadOrDatei, bZielSave, sCharSet,  bCol, bLayer, bFormatText, bUseColor4Point, bUseColor4Line, bUseColor4Poly, dblFaktor, chkTransform, DreiPassPunkte, bGen3D)
    # 23.02.17
    # Processing erst hier Laden, um den Start von QGIS zu beschleunigen
    import processing
    from processing.core.Processing import Processing

    
    # -----------------------------------------------------------------------------------------------    
    # 1. Löschen der alten Projekte und evtl.if myqtVersion == 4 Ermittlung der zu überschreibenden Dateien
    delZielDat=[]
    for i in range(listDXFDatNam.count()):
        AktDXFDatNam=listDXFDatNam.item(i).text()
        # 13.08.20: Neu jetzt mit Format im Projektname, damit SHP und GPKG parallel eingebunden werden kann
        AktList,AktOpt,ProjektName, Kern =ProjDaten4Dat(AktDXFDatNam, bCol, bLayer, bZielSave, sOutForm)
        
        # evtl. Projektname (-gruppe) in Root löschen
        rNode=QgsProject.instance().layerTreeRoot()
        for node in rNode.children():
            if str(type(node))  == "<class 'qgis._core.QgsLayerTreeGroup'>":
                if node.name() == ProjektName:
                        rNode.removeChildNode(node)
      
        # evtl. Shape/GeoPackage Zieldateien ermitteln und löschen
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
    
    # -----------------------------------------------------------------------------------------------    
    # 2. evtl. Dialog zur CRS-Eingabe aufrufen und Dummylayer schreiben, um eine qprj zu erhalten
    #    Vorteil der qprj: auch UserCRS werden erkannt
    # a) CRS manuell oder automatisch je nach Einstellung
    # es gibt 3 Arten: prompt,useProject,useGlobal 
    
    
    # 10.12.19: In QGIS 3.10 wird bei memory-Layer ungefragt wgs84 gesetzt, bei "ogr"-Layer wird aber gefragt
    
    # 10.12.19: Damit nicht schon hier gefragt wird (QGIS <> 3.10) ein CRS vorgeben
    #dummy_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    mLay=QgsVectorLayer('LineString?crs=EPSG:4326','' , 'memory')
    # 10.12.19: Zwischenspeichern
    mem0Dat=EZUTempDir() + str(uuid.uuid4()) + '.shp'
    
    # 13.08.20: Umstellung auf writeAsVectorFormatV2 ab (3.10.3)
    if myQGIS_VERSION_INT() < 31003:
        Antw=QgsVectorFileWriter.writeAsVectorFormat(mLay,mem0Dat,  None, mLay.crs(), "ESRI Shapefile")
    else:
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        Antw=QgsVectorFileWriter.writeAsVectorFormatV2(mLay,mem0Dat, QgsCoordinateTransformContext(), options)

   
    # QGIS 2.x gibt kein Array zurück
    if type(Antw) != tuple:
        Antw = Antw , "error by creating memorylayer" # ein Dummy-Fehlermeldung schreiben (bei korrekt ist das Feld uninteressant)
    
    
    
    # 27.2.20. wegen gemeldeten Fehler jetzt antwort auswerten
    # (0, '') --> korrekt
    # (2, 'Erzeugung der Datenquelle gescheitert (OGR-Fehler: d:/tar/mytest.shp is not a directory.)') --> z.B. (alte) shp ist schreibgeschützt             
    if Antw[0] != 0:
        addFehler(tr("Error create memorylayer: " + Antw[1]))
    else:
        # 10.12.19: Projektionsdateien löschen
        try:
            # ab QGIS 3.10.x wird keine qpj mehr generiert
            os.remove(mem0Dat[0:-3] + 'qpj')
        except:
            pass
        try:
            os.remove(mem0Dat[0:-3] + 'prj')
            # 10.12.19: jetzt statt dem Menorylayer den ogr Layer laden
            mLay=QgsVectorLayer(mem0Dat, '' , 'ogr')
        except OSError as e: 
            addFehler("delete memorylayer: %s - %s." % (e.filename,e.strerror)) 

    # 10.12.19: weiter wie gehabt
    memDat=EZUTempDir() + str(uuid.uuid4()) + '.shp'
    # 13.08.20: Umstellung auf writeAsVectorFormatV2
    if myQGIS_VERSION_INT() < 31003:
        Antw=QgsVectorFileWriter.writeAsVectorFormat(mLay,memDat,  None, mLay.crs(), "ESRI Shapefile")
    else:
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        Antw=QgsVectorFileWriter.writeAsVectorFormatV2(mLay,memDat, QgsCoordinateTransformContext(), options)

    
    qPrjDatName=memDat[0:-3] + 'qpj'
    # ab QGIS 3.10.x wird keine qpj mehr generiert
    if not (os.path.exists(qPrjDatName)):
        qPrjDatName=memDat[0:-3] + 'prj'

    # es gibt 3 Arten: prompt,useProject,useGlobal (UseDefaultCrs)
    # originale Einstellung merken und für den weiter Verlauf zwingend auf automatisch einstellen 
    # Name der Eigenschaft in 3.0 geändert/korrigiert
    if myqtVersion == 4:
        crsArtQ2=QSettings().value('/Projections/defaultBehaviour')
        QSettings().setValue('/Projections/defaultBehaviour','useGlobal')
    else:
        # 13.08.2020: QGIS.ini
        # KBS-Vorgabe verwenden 
        # /app/projections/unknownCrsBehavior=UseDefaultCrs
        # /Projections/layerDefaultCrs=USER:100028
        crsArtQ3_1=QSettings().value('/Projections/defaultBehavior')
        crsArtQ3_2=QSettings().value('/app/projections/unknownCrsBehavior')
        QSettings().setValue('/Projections/defaultBehavior','useGlobal')
        QSettings().setValue('/app/projections/unknownCrsBehavior','UseDefaultCrs')
    crsDefWert = QSettings().value('/Projections/layerDefaultCrs')
    QSettings().setValue('/Projections/layerDefaultCrs',mLay.crs().authid())  
    
    

    try:
        # -----------------------------------------------------------------------------------------------   
        # 3a. Initialisierung    
        # manchmal bleibt (bei mehrfachnutzung oder bei crash) irgend etwas hängen,
        # die beiden nachfolgenden Zeilen haben bei einem Test das Problem gefixt - konnte aber noch nicht wiederholt werden
        # recht zeitaufwändig
        uiParent.FormRunning(True)
        uiParent.SetDatAktionGesSchritte(8)    
        uiParent.SetAktionText("")
        uiParent.SetDatAktionText(tr("process init - please wait"))
        uiParent.SetDatAktionAktSchritt(1)

        Processing.initialize()
        #Processing.updateAlgsList() # existiert nicht mehr bei 2.99

        # -----------------------------------------------------------------------------------------------    
        # 3. Abarbeitung der Dateien
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
            # 1. Wurzel mit DXF- bzw. Projektname
                  
            # Projektname (-gruppe) in Root (neu) erstellen
            root = QgsProject.instance().layerTreeRoot()
            grpProjekt = root.addGroup( ProjektName)
            #grpProjekt = iface.legendInterface().addGroup( ProjektName, False)
            grpProjekt.setExpanded(True)
            #iface.legendInterface().setGroupExpanded( grpProjekt, True )  
           
            #msgbox ("Bearbeite '" + AktDXFDatNam + "'")
            okTransform=chkTransform
            if chkTransform and DreiPassPunkte == None:
                # Einpassdaten müssen aus wld kommen
                wldDat=os.path.splitext(AktDXFDatNam)[0] + ".wld"
                if os.path.exists(wldDat):
                    p=[[],[],[]]
                    p[0], p[1], Fehler = ReadWldDat(wldDat)
                    if Fehler == None:
                        # restliche Punkte per Helmert ermitteln
                        if p[1] == None:
                            # 2. Punkt ermitteln
                            p[0], p[1], p[2] = Helmert4Points(p[0], None)
                        # (immer) 3. Punkt ermitteln
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
    
    
    # Ausgangswerte crs wieder herstellen
    #QSettings().setValue(crsRegParam4NewLayer,crsArt)
    #QSettings().setValue('/Projections/layerDefaultCrs',crsDefWert)
    
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
    # print (mLay_crs, bZielSave, sOutForm, grpProjekt,AktList, Kern, AktOpt, DXFDatNam, zielPfadOrDatei, qPrjDatName, sOrgCharSet, bLayer, bFormatText, bUseColor4Point,bUseColor4Line,bUseColor4Poly, dblFaktor,chkTransform, DreiPassPunkte, bGen3D)
    # 23.02.17
    # Processing erst hier Laden, um den Start von QGIS zu beschleunigen
    import processing
    from processing.core.Processing import Processing
   
    # Programmierfehler
    if sOutForm != "SHP" and sOutForm != "GPKG":
        errbox("Formatfehler: '" + sOutForm + "'")
        return False
        
 
    sCharSet=sOrgCharSet
    myGroups={}
    
    # ----------------------------------------------------------------------------
    # Dateiquelle anpassen
    # ----------------------------------------------------------------------------
    # (zumindest) unter Windows gibt es Probleme, wenn Umlaute im Dateinamen sind
    # einzige saubere Variante scheint die Bearbeitung einer Dateikopie zu sein
    # um Resourcen zu sparen, zunächst nur kopie, wenn umwandlung des Dateinamens in einen String Fehler bringt
    # 21.11.16: ab 2.18 bringt die Umwandlung in einen String keinen Fehler mehr
    #           deshalb neue Strategie zum Erkennen der Umlaute
    
    # 21.02.17: grundsätzlich mit Kopie, da runalg die Datei sperrt und nicht mehr frei gibt
    # 19.03.18: noch mal überlegen/testen: es gibt dxf's, welche durch dictionary's mehere GByte haben-da ist kopieren nicht so geil
    if ifAscii(DXFDatNam):
        korrDXFDatNam=DXFDatNam
    else:
        uiParent.SetAktionGesSchritte(2)
        uiParent.SetAktionText(tr("Copy DXF-File"))
        uiParent.SetAktionAktSchritt(1)
        korrDXFDatNam=(EZUTempDir() + str(uuid.uuid4()) + '.dxf')
        copyfile(DXFDatNam, korrDXFDatNam)
    #printlog ("Copy" + DXFDatNam + ' --> ' + korrDXFDatNam)
    
    optGCP = ""
    if chkTransform:
        for p in range(len(DreiPassPunkte)):
            optGCP = optGCP + " -gcp "
            for k in range(len(DreiPassPunkte[p])):
                optGCP = optGCP + str(DreiPassPunkte[p][k][0]) + " " +  str(DreiPassPunkte[p][k][1]) + " "
        # -gcp am Ende abschneiden
        if optGCP[-5:]=="-gcp ":
            optGCP=optGCP[:-5]

    zE=0
    uiParent.SetAktionGesSchritte(len(AktList))
    
    # GPKG ist einheitlich für alle Layer 
    if sOutForm == "GPKG":
        gpkgdat=zielPfadOrDatei+Kern+'.gpkg'
        
        # 31.08.2020: Korrigiert->war vertauscht
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
            iOutForm = 0 # •0 — ESRI Shapedatei
            shpdat=zielPfadOrDatei+Kern+v[0]+'.shp'
            qmldat=zielPfadOrDatei+Kern+v[0]+'.qml'
        
        if sOutForm == "GPKG":
            qmldat =  EZUTempDir() + str(uuid.uuid4()) + '.qml'
            gpkgTable=Kern+v[0]

        
        # ----------------------------------------------------------------------------
        # Dateiziel für SHP anpassen (GPKG außerhalb dieser Schleife)
        # ----------------------------------------------------------------------------      
        # ZielPfad bzw. Zielname dürfen keine Umlaute enthalten --> in temporäre Datei konvertieren
        # 21.02.17: Leerzeichen im Pfad funktionieren auch nicht, deshalb grundsätzlich als Kopie
        #if ifAscii(shpdat):
        #    korrSHPDatNam=shpdat
        #else:
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
                    # das zu erzeugende Ausgabeformat wird über die Dateiendung definiert 
                    pList={'INPUT':korrDXFDatNam,'OPTIONS':opt,'OUTPUT': korrSHPDatNam}
                    pAntw=processing.run('gdal:convertformat',pList) 

                if os.path.exists(korrSHPDatNam): bKonvOK = True
            
            if sOutForm == "GPKG":
                # nur für QGIS 3.x definiert
                if sCharSet == "System":
                    ogrCharSet=locale.getdefaultlocale()[1]
                else:
                    ogrCharSet=sCharSet
                ogrCharSet=ogrCharSet.upper()              
 
                opt = '-append -update --config DXF_ENCODING "' + ogrCharSet + '" '
                
                # Erzeugt Spalte RawCodeValues ( A string list containing all group codes and values that are not handled by the DXF reader.)
                opt = opt + '--config DXF_INCLUDE_RAW_CODE_VALUES TRUE '
                opt = opt + ('%s -nlt %s %s -sql "select *, ogr_style from entities where OGR_GEOMETRY %s" -nln "%s"') % (AktOpt,v[1],optGCP,v[2], gpkgTable)      
                if bGen3D:
                    opt = opt +  ' -dim 3 '
                
                #hinweislog ('Convert:' + korrDXFDatNam + '-->' + korrGPKGDatNam) 
                #hinweislog ('-->Options:' + opt) 
                pList={'INPUT':korrDXFDatNam,'OPTIONS':opt,'OUTPUT': korrGPKGDatNam}
                pAntw=processing.run('gdal:convertformat',pList) 
                # macht so bei GPKG wenig Sinn, funktioniert aber zumindest beim ersten mal
                # Fehler kommt dann bei attTableEdit()
                if os.path.exists(korrGPKGDatNam):bKonvOK = True 
               
        except:
            addFehler(tr("Error processing: " + DXFDatNam))
            return False

        if pAntw is None:
            addFehler(tr("process 'gdalogr:convertformat' could not start please restart QGIS"))
        else:
            if sOutForm == "SHP":
                if myqtVersion == 5:
                    # Unter QGIS3.0 gibt es aktuell ein ganz böses Problem: Das Schreiben der DBF crasht, wenn Kodierung cp1252 ist
                    # --> Shape (DBF)  nach UTF8 konvertieren
                    aktShapeName=korrSHPDatNam
                    korrSHPDatNam=(EZUTempDir() + str(uuid.uuid4()) + '.shp') # neuer Dateiname
                    # 10.12.19: Qpj erzeugen übergeben, da sonst u.U. (bei 3.10) abgefragt
                    
                    # ab QGIS 3.10.x wird keine qpj mehr generiert
                    if os.path.exists(qPrjDatName) : 
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"qpj")
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"prj")

                    ShapeCodepage2Utf8 (aktShapeName, korrSHPDatNam,  sOrgCharSet) # 28.03.18 sOrgCharSet 
                    sCharSet="utf-8"
                else:
                    aktShapeName=korrSHPDatNam
                
            if bKonvOK:
                if sOutForm == "SHP":
                    attTableEdit(sOutForm,korrSHPDatNam,bFormatText,sCharSet)
                    if korrSHPDatNam != shpdat:
                        # evtl. korrigierte Dateiname umbenennen
                        #printlog ("move:" + korrSHPDatNam + '-->' + shpdat)
                        move(korrSHPDatNam,shpdat)
                        for rest in glob(korrSHPDatNam[0:-4] + '.*'):
                            #printlog ("move:" + rest + '-->' + shpdat[0:-4] + rest[-4:])
                            move(rest,shpdat[0:-4] + rest[-4:])

                    # ogr2ogr schreibt den EPSG-code nicht in die prj-Datei, dadurch kommt es beim Einbinden
                    # zu anderenen EPSG-Codes -> Nutzung einer qpj
                    #print qPrjDatName,shpdat[0:-3]+"qpj"
                    
                    # ab QGIS 3.10.x wird keine qpj mehr generiert
                    if os.path.exists(qPrjDatName) : 
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"qpj")
                        copyfile (qPrjDatName,aktShapeName[0:-3]+"prj")
                    Layer = QgsVectorLayer(shpdat, "entities"+v[0],"ogr") 

                 
                    # vermutlich reicht einer der beiden Befehle
                    # unbekannte Codepages werden zu "System"
                    Layer.setProviderEncoding(sCharSet)
                    Layer.dataProvider().setEncoding(sCharSet) 
                
                if sOutForm == "GPKG":
                    attTableEdit(sOutForm,korrGPKGDatNam,bFormatText,sCharSet,gpkgTable)
                    sLayer="%s|layername=%s" %(korrGPKGDatNam,gpkgTable) #|geometrytype=Point"
                    Layer = QgsVectorLayer(sLayer, "entities"+v[0],"ogr") 
                    Layer.setCrs(mLay_crs)
                    if Layer.featureCount() < 0: Layer=None # bei QGIS3 wird bei Fehlern -2 zurückgegeben If Layer führt dann zu Fehlern
                ##### !!!!!!!!!! ####
                #iface.mapCanvas().setRenderFlag( True )
                #return False
                ##### !!!!!!!!!! ####

                if Layer:
                    # Kontrolle, ob was sinnvolles im Layer ist. Ogr erzeugt öfters Shapes ohne Koordinaten
                    bLayerMitDaten = False
                    if Layer.featureCount() > 0:
                        koo=Layer.extent()
                        if koo.xMinimum() == 0 and koo.yMinimum() == 0 and koo.xMaximum() == 0 and koo.yMaximum() == 0:
                            # das scheint ein  Ufo zu sein
                            addHinweis("Empty coordinates for " + opt )
                        else:
                            bLayerMitDaten  = True
                    else:
                        addHinweis("No entities for " + opt )

                    # der Layer enthält Daten
                    if bLayerMitDaten:
                        if not bLayer:
                            # Group by Layer ist deaktiviert, für jede Geometrieart wird nur ein Layer geschrieben
                            #   17.01.18: funktioniert bei 2.18 und 2.99
                            # 28.03.17 Diese Zeile ist notwendig, damit das "processing.runalg" sauber läuft !!???
                            if myqtVersion == 4:
                                QgsMapLayerRegistry.instance().addMapLayer(Layer, False)
                            else:
                                Layer = QgsProject.instance().addMapLayer(Layer, False) # nicht in Legende

                            ml=grpProjekt.addLayer(Layer)
                            ml.setExpanded(False)
                            #QgsMapLayerRegistry.instance().addMapLayer(Layer)
                            #iface.legendInterface().moveLayer( Layer, grpProjekt)
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
                            # Group by Layer ist aktiviert, für jeden Layer wird eine extra Gruppe erzeugt
                            if myqtVersion == 4:
                                fni = Layer.fieldNameIndex('Layer')
                            else:
                                fni = Layer.dataProvider().fieldNameIndex('Layer')
                            unique_values = Layer.dataProvider().uniqueValues(fni)
                            zL=0
                            for AktLayerNam in unique_values:
                                OrgLayerNam = AktLayerNam
                                if AktLayerNam == NULL:
                                    AktLayerNam = "NULL" # Anzeige im Baum
                                else:                                  
                                    AktLayerNam = DecodeDXFUTF(AktLayerNam)
                                uiParent.SetAktionGesSchritte(len(unique_values))
                                uiParent.SetAktionText("Edit Layer: " + AktLayerNam )
                                uiParent.SetAktionAktSchritt(zL)
                                zL=zL+1
                                if sOutForm == "SHP":
                                    Layer = QgsVectorLayer(shpdat, AktLayerNam+'('+v[0]+')',"ogr")
                                    # vermutlich reicht einer der beiden Befehle
                                    # unbekannte Codepages werden zu "System"
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
                                    if Layer.featureCount() < 0: Layer=None # bei QGIS3 wird bei Fehlern -2 zurückgegeben If Layer führt dann zu Fehlern

                                if myqtVersion == 4:
                                    QgsMapLayerRegistry.instance().addMapLayer(Layer, False)
                                else:
                                    Layer = QgsProject.instance().addMapLayer(Layer, False) # nicht in Legende
                                #print 'Layer = "' + AktLayerNam + '"'
                                #iface.mapCanvas().setRenderFlag( True )
                                if AktLayerNam not in myGroups:
                                    #gL = iface.legendInterface().addGroup( AktLayerNam, False,grpProjekt)
                                    gL = grpProjekt.addGroup( AktLayerNam)
                                    myGroups[AktLayerNam]=gL
                                    #print myGroups
                                    #iface.legendInterface().setGroupExpanded( gL, False )
                                    #iface.legendInterface().moveLayer( Layer, gL)
                                    gL.addLayer(Layer)
                                    gL.setExpanded(False)

                                else:
                                    #iface.legendInterface().moveLayer( Layer, myGroups[AktLayerNam])
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
                        
                        # 27.02.18: immer speichern und bei Punkt und qt5 reload
                        if sOutForm == "SHP":
                            Layer.saveNamedStyle (qmldat)
                        else:
                            Layer.saveStyleToDatabase(gpkgTable, gpkgTable, True, "")

                    else:
                        Layer=None # um Datei löschen zu ermöglichen
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
       
    """
    fni = layer.fieldNameIndex('Layer')
    unique_values = layer.dataProvider().uniqueValues(fni)
    lList=[]
    for l in unique_values:
        lList.append(l)
    return lList
        """
if __name__ == "__main__":
    import os
    try:
        os.kill(1234, 0)
    except OSError as e:  ## if failed, report it back to the user ##
        print( "Fehler: %s - %s." % (e.filename,e.strerror)) 


        
        
"""    print ("Start: -------------------------------------")
    datNam="x:/dxf2shape/karte2.dxf"
    opt='-sql "select *, ogr_style from entities where OGR_GEOMETRY LIKE ''%POINT%'''
    list={'INPUT':datNam,'OPTIONS':opt,'OUTPUT': datNam}
    print (list)
    print ("Ende: -------------------------------------")
    
    #KorrPrjDat ("d:/tar/x.dxf(GC)L.prj")
"""