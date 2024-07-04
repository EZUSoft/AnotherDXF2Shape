# -*- coding: utf-8 -*-
"""
/***************************************************************************
 A QGIS plugin
AnotherDXF2Shape: Convert DXF to shape and add to QGIS
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







































from osgeo import ogr

try:
    from PyQt5.QtCore import  QCoreApplication
except:
    from PyQt4.QtCore import  QCoreApplication

try:
    from .fnc4all import *
    from .fnc4ADXF2Shape import *
except:
    from fnc4all  import *
    from fnc4ADXF2Shape import *

import locale

    
def tr( message):











    return QCoreApplication.translate('clsDXFTools', message)
    
def ZahlTextSplit(zt):
    try:
        z="";t="";f=-1
        isText = False
        for c in zt:
            if not c in "01234567890.-":
                isText=True
            if isText:
                t=t+c
            else:
                z=z+c
        f=float(z)
    except:

        pass
    return f,t  

def fnctxtOGRtoQGIS(cArt):
    if cArt == 1:
        return 2
    if cArt == 2:
        return 1
    if cArt == 3:
        return 0
    if cArt == 4:
        return 5
    if cArt == 5:
        return 4
    if cArt == 6:
        return 3
    if cArt == 7:
        return 8
    if cArt == 8:
        return 7 
    if cArt == 9:
        return 6 

    if cArt == 10:
        return 2 
    if cArt == 11:
        return 1 
    if cArt == 12:
        return 0  
        
def trennArtDaten(ArtDaten):


    sDaten = ""
    sArt = ""
    inDaten = False
    for c in ArtDaten[:-1]:
        if c == '(' and not inDaten:
            inDaten = True
            c = ''
        if inDaten:
            sDaten = sDaten + c
        else:
            sArt = sArt + c
    return sArt, sDaten
    
def csvSplit(csvZeile, trenn=',', tKenn='"', tKennDel = True, bOnlyFirst = False):



    


    inString = False
    mask = ""
    s = ''
    sb = False
    for c in csvZeile: 

        if c == tKenn and not sb:
            inString = not inString
        if c == trenn and inString  and not sb:
            if mask == "":
                mask = "$$"
                while mask in csvZeile:
                    mask = mask + '$'
            s=s+mask
        else:
            if not (tKennDel and (not sb) and c == tKenn): 
                s=s+c
        if c == "\\":
            sb = True
        else:
            sb = False
            
    arr = s.split(trenn)
    if mask != "":
        for i in range(0,len(arr)):
            arr[i] = arr[i].replace(mask,trenn)
    if bOnlyFirst and len(arr)>2:
        arr=[arr[0],trenn.join(arr[1:])]
    return arr


        
def splitText (fText,TxtType):












    underline = False
    bs = False
    uText = r""
    ignor = False
    font = ""
    color = ""
    delSemi = False
    inFont = False
    inColor = False
    inIngnorieren = False
    inHText = False
    aktText=fText
    FlNum = False
    aktSize = None
    
    if TxtType == "TEXT" or TxtType == "UNDEF":




        if "%%u".upper() in aktText.upper():
            underline=True
            aktText = aktText.replace('%%u','').replace('%%U','')
        


        aktText = aktText.replace('%%d','°') 
        aktText = aktText.replace('%%p','±')
        aktText = aktText.replace('%%c','Ø')
        aktText = aktText.replace('%%D','°') 
        aktText = aktText.replace('%%P','±')
        aktText = aktText.replace('%%C','Ø')
    
    if TxtType == "MTEXT" or TxtType == "UNDEF":
        aktText=DecodeDXFUTF(aktText)

        aktText = aktText.replace('%%d','°') 
        aktText = aktText.replace('%%p','±')
        aktText = aktText.replace('%%c','Ø')
        aktText = aktText.replace('%%D','°') 
        aktText = aktText.replace('%%P','±')
        aktText = aktText.replace('%%C','Ø')
        

        


        for c in aktText:

            if bs and c.upper() == 'H': 
                c=''
                ignor = True
                inHText = True 
                delSemi = True
            if bs and c.upper() == 'O': 
                c=''
                ignor = True
            if bs and c.upper() == 'L': 
                c=''
                underline = True
                ignor = True
            if bs and c == 'S': 
                c=''
                ignor = True
                delSemi = True
                FlNum = True

            if bs and c.upper() == 'F': 
                ignor = True
                inFont = True 
                delSemi = True
            
            if bs and c.upper() == 'C': 
                ignor = True
                inColor = True 
                delSemi = True
            
            if bs and c == 'p': 
                ignor = True
                inIngnorieren = True 
                delSemi = True

            if bs and c == 'A': 
                ignor = True
                inIngnorieren = True 
                delSemi = True
                
            if bs and c == 'W': 
                ignor = True
                inIngnorieren = True 
                delSemi = True
                



            if bs and c == 'P': 
                ignor = True
                c="\n"  
                
            if c == ';' and delSemi:
                c= ''
                inFont=False
                inColor=False
                inIngnorieren=False
                inHText=False
                delSemi = False
            
            if not bs and (c == '{' or c == '}'): 
                c = ''
            else:
                ignor = True
            if c == '\\':
                if bs:

                    uText = uText + '\\\\'
                    bs=False
                else:
                    bs = True
            else:
                if not ignor:
                    if bs:
                        uText = uText + '\\'
                if inFont:
                    font = font + c
                else:
                    if inColor:
                        color = color + c
                    else:
                        if inHText:
                            if aktSize is None:
                                aktSize = c
                            else:
                                aktSize = aktSize + c
                        else:
                            if not inIngnorieren:
                                uText = uText  + c
                bs = False
            ignor = False
        aktText = uText
    return aktText, underline, font, FlNum, aktSize, color
 

def ShapeCodepage2Utf8 (OrgShpDat, TargetShpDat, OrgCodePage):
    TargetCodePage="utf8"
    if OrgCodePage == "System":
        OrgCodePage=locale.getdefaultlocale()[1]
 
    oLayer=QgsVectorLayer(OrgShpDat,'', 'ogr')
    oLayer.setProviderEncoding(OrgCodePage)
    oLayer.dataProvider().setEncoding(OrgCodePage)
    

    if myQGIS_VERSION_INT() < 31003:
        zLayer=QgsVectorFileWriter.writeAsVectorFormat(oLayer,TargetShpDat,TargetCodePage, oLayer.crs(), "ESRI Shapefile")
    else:
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = TargetCodePage
        zLayer=QgsVectorFileWriter.writeAsVectorFormatV2(oLayer,TargetShpDat, QgsCoordinateTransformContext(), options)
    






def attTableEdit (sOutForm, inpDat,bFormat,sCharSet,gpkgTable=None, txtErsatz4Tab = ' '):


    if sCharSet == "System":
        sCharSet=locale.getdefaultlocale()[1]

    source = ogr.Open(inpDat, update=True)
    if source is None:
        addFehler(tr('ogr: can not open: ') + inpDat)
        return
    
    if sOutForm=="SHP":
        layer = source.GetLayer()
        if layer is None:
            source.Destroy()
            addFehler(tr('ogr: layer not found: ') + inpDat)
            return
    else:
        layer = source.GetLayerByName( gpkgTable )
        if layer is None:
            source.Destroy()


            hinweislog(tr('ogr: layer not found: ') + inpDat + '(' + gpkgTable + ')')
            return
    

        
    laydef = layer.GetLayerDefn()
    if laydef is None:
        source.Destroy()
        addFehler(tr('ogr: laydef not found: ') + inpDat)
        return

    Found = False
    for i in range(laydef.GetFieldCount()):
        if laydef.GetFieldDefn(i).GetName() == 'ogr_style':
            Found = True

    if not Found:
        addFehler(tr("missing field 'ogr_style': ") + inpDat)
        return
    


    layer.CreateField(ogr.FieldDefn('font', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('angle', ogr.OFTReal))    
    layer.CreateField(ogr.FieldDefn('size', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('size_u', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('anchor', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('color', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('underline', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('plaintext', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('fcolor', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('flnum', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('bold', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('italic', ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn('dx', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('dx_u', ogr.OFTString))
    layer.CreateField(ogr.FieldDefn('dy', ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn('dy_u', ogr.OFTString)) 

    i=1
    layer.StartTransaction()
    feature = layer.GetNextFeature()
    while feature:
        try:
            TxtType = "UNDEF"
            SubClass = feature.GetField('SubClasses')
            if SubClass is None:

                if sOutForm=="SHP":
                    addHinweis(tr("missing field 'SubClasses' in: ") + inpDat)
            else:


                if SubClass.find("AcDbMText")>=0:
                    TxtType = "MTEXT" 
                if SubClass.find("AcDbText")>=0:
                    TxtType = "TEXT"
            att=feature.GetField('ogr_style') 
          
            try:
                aktHandle=feature.GetField('EntityHand') 
            except:
                aktHandle=feature.GetField('EntityHandle') 
                
            if att is None:
                addHinweis(tr("missing field 'ogr_style' in: ") + inpDat)
            
            elif att[-1] != ')':
                if aktHandle == None:
                    addHinweis(tr("incomplete field 'ogr_style' at EntityHandle: ") )
                else:
                    addHinweis(tr("incomplete field 'ogr_style' at EntityHandle: ") + str(aktHandle)) 

            else:
                sArt,sDaten = trennArtDaten(att)




                params = csvSplit (sDaten)
                for param in params:

                    arr=csvSplit(param,":",None,None,True)

                    if len(arr) == 2:
                        f = arr[0] 
                        w = arr[1]


                        if f == "c":

                            if w == "#ffffff": w="#f0f0f0"
                            feature.SetField('color', w)
                        if f == "fc":


                            if w == "#000000": w="#f0f0f0"
                            feature.SetField('fcolor', w)
                        if f == "f":
                            feature.SetField('font', w)
                        if f == "a":
                            dWin = float(w)
                            if dWin >=360:
                                dWin = dWin - 360 
                            feature.SetField('angle', dWin)
                        if f == "p":
                            if sArt == "LABEL":
                                feature.SetField('anchor', fnctxtOGRtoQGIS(int(w)))
                        if f == "s":
                            z,t=ZahlTextSplit(w)

                            feature.SetField('size', z)
                            feature.SetField('size_u', t)
                            

                        if f == "dx":
                            z,t=ZahlTextSplit(w)

                            feature.SetField('dx', z)
                            feature.SetField('dx_u', t)                       
                        if f == "dy":
                            z,t=ZahlTextSplit(w)

                            feature.SetField('dy', z)
                            feature.SetField('dy_u', t)                                         
                        
                        if f == "t":




                            dummy = 1

                    else:



                        addFehler(tr("incomplete field 'ogr_style': ") + tryDecode(param,sCharSet))
                    
                    if sArt == "LABEL":

                        AktText = feature.GetField('Text')
                        if AktText is None:
                            addHinweis(tr('missing Text: ') + inpDat)
                        else:
                            dummy=AktText
                            AktText="";bDecodeError=False

                            for c in dummy:
                                if ord(c) > 54000:
                                    c="?"; bDecodeError=True
                                AktText=AktText + c
                            if bDecodeError:
                                if aktHandle == None:
                                    addFehler(tr("Wrong char in  'ogr_style' at EntityHandle: ") +  tr(" (Check your choose charset)") + tryDecode(dummy,sCharSet)) 
                                else:
                                    addFehler(tr("Wrong char in  'ogr_style' at EntityHandle: ") + aktHandle + tr(" (Check your choose charset)") + tryDecode(dummy,sCharSet)) 


                            if bFormat:
                                t,underline,font, FlNum, aktSize, color = splitText(AktText,TxtType)
                                t = t.replace('^I',txtErsatz4Tab)

                                feature.SetField('plaintext', t)
                               
                                if not aktSize is None:
                                    feature.SetField('size', aktSize)
                                

                                if (color != ""):
                                    try:
                                        color=hex(int(color[1:])).replace('0x','#') 

                                        if color == "#ffffff": color="#f0f0f0"                                        
                                        feature.SetField('color',color)
                                    except:
                                        feature.SetField('color','#FEHLER#')
                                


                                if (font != ""):
                                    afont = font.split('|')
                                    for p in afont:
                                        if p[:1] == 'f':
                                            feature.SetField('font', p[1:])
                                        if p[:1] == 'b':
                                            feature.SetField('bold', p[1:])
                                        if p[:1] == 'i':
                                            feature.SetField('italic', p[1:])
                                feature.SetField('underline', underline)
                                feature.SetField('flnum', FlNum)
                            else:
                                feature.SetField('plaintext', AktText)
                                feature.SetField('underline', False)
                layer.SetFeature(feature)
            feature = layer.GetNextFeature()
        except:
            if att is None:
                subLZF ()
            else:
                subLZF ('ogr_style:' + att)
                
            feature = layer.GetNextFeature()
    layer.CommitTransaction()
    source.Destroy()

