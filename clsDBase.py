# -*- coding: utf-8 -*-

"""
/***************************************************************************
 clsDBase
    Änderungen 11.11.22
        Erweiterung um Textverschiebung dx, dy
    Änderungen 13.08.20
            13.08.2020: Weiß als Darstellung "verwirrend", deshalb Grau
    Änderungen V1.1.1
        14.10.2019: Zeilenumbruch bei MTEXT
 
    Änderungen V1.1.0
    09.09.19 
         support Color-Code in MText
         support interne UTF16 <backslash>U+.... Codierung

    Änderungen V1.0.1
        Erweiterung auf GeoPackage
        05.03.18: Fehler bei ":" in Texten beseitigt
    
    Änderungen V0.81.2:
        18.04.17 
            - Umsetzung: \fMS Shell Dlg 2|i0|b0;\H1.98441;265.0m
              \H1.98441 heraus plaintext und "size" setzen
    
    Änderungen V0.81:
        03.03.17 
            - Untersteichung neben %%u jetzt auch %%U
            - Fehlerbehandlung in attTableEdit wieder aktiviert
    
    Änderungen V0.7:
        21.02.17 
            - Kodierungsprobleme beseitigt
        13.12.16
            - Ersterstellung
            
                                 A QGIS plugin
 Konvert DXF to shape and add to QGIS
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
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
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
        #print ("Fehler:",zt,z,t)
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
    # 10-13 (ganz unten) ist mit QGIS nicht darstellbar, deshalb auf unten setzen
    if cArt == 10:
        return 2 
    if cArt == 11:
        return 1 
    if cArt == 12:
        return 0  
        
def trennArtDaten(ArtDaten):
    #BRUSH(fc:#dcdcdc)
    #LABEL(f:"Arial",t:"{\fArial|b1|i0|c0|p34;VZOG}",s:3.5g,p:8,c:#ff7f7f)
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
    #csvZeile: Datenzeile 
    #trenn:    Feldtrenner
    #tKenn:    Textkennzeichen
    
    #Trenner innerhalb von Freitexten ersetzen

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
    #http://docs.autodesk.com/ACD/2010/ENU/AutoCAD%202010%20User%20Documentation/index.html?url=WS1a9193826455f5ffa23ce210c4a30acaf-63b9.htm,topicNumber=d0e123454
    # V1: %%u1106                                   # TEXT  unterstrichender Text aus Caigos
    # V2: {\fArial|b0|i1|c0|p34;\L151}              # MTEXT unterstrichender Text  vom LVA
    # V3: \fTimes New Roman|i1|b0;Rue Presles       # MTEXT Datei PONT A CELLES 2010.dxf von pierre.mariemont
    # V4: \S558/15;                                 # MTEXT komplette gebrochene Flurstücksnummer (Geograf)
    # V5: \fMS Shell Dlg 2|i0|b0;\H1.98441;265.0m   # MTEXT aus QGIS selbst (Höhenlinien beschritet)
    # V6: \c10789024;FarbigerText                   # MTEXT z.B. aus QCad
    # ob Text oder MTEXT kann im Moment nicht immer unterschieden werden

    underline = False
    bs = False
    uText = r""
    ignor = False
    font = ""
    color = ""
    delSemi = False
    inFont = False
    inColor = False
    inHText = False
    aktText=fText
    FlNum = False
    aktSize = None
    
    if TxtType == "TEXT" or TxtType == "UNDEF":
        # 1. Formatierungen TEXT
        #    Die Codes sind nirgends definiert
        # %%u entfernen und ggf. underline setzen
        # 03.03.17: in Geograf scheint man (auch) ein großes U zu nutzen
        if "%%u".upper() in aktText.upper():
            underline=True
            aktText = aktText.replace('%%u','').replace('%%U','')
        # %%c ist Ø
        aktText = aktText.replace('%%c','Ø') # geht nur bei Unicode als Zeichensatz, hier muss noch irgendwas getan werden
    
    if TxtType == "MTEXT" or TxtType == "UNDEF":
        aktText=DecodeDXFUTF(aktText)
        # 2. Formatierungen MTEXT
        # 05.02.20: Problem: doppeltes Backslash (Maskierung eines einfachen \ im Text)
        for c in aktText:
            # Kennungen mit nachfolgendem Zeichen, welche OGR  nicht auswertet
            if bs and c.upper() == 'H': # 12.04.17 ignorieren Höhe
                c=''
                ignor = True
                inHText = True 
                delSemi = True
            if bs and c.upper() == 'O': # ignorieren Overline on/off
                c=''
                ignor = True
            if bs and c.upper() == 'L': # underline on/off: only for all
                c=''
                underline = True
                ignor = True
            if bs and c == 'S': # Stacks the subsequent text at the /, #, or ^ symbol: aktuell nur \S und Semikolon entfernen
                c=''
                ignor = True
                delSemi = True
                FlNum = True

            if bs and c.upper() == 'F': # \Ffont name; Changes to the specified font file 
                ignor = True
                inFont = True 
                delSemi = True
            
            if bs and c.upper() == 'C': # \cHexcolor; 
                ignor = True
                inColor = True 
                delSemi = True
            # 14.10.2019: Zeilenumbruch bei MTEXT   
            if bs and c.upper() == 'P': # Zeilenumbruch; 
                ignor = True
                c="\n"  
                
            if c == ';' and delSemi:
                c= ''
                inFont=False
                inColor=False
                inHText=False
                delSemi = False
            
            if not bs and (c == '{' or c == '}'): # nur für Formatierung
                c = ''
            else:
                ignor = True
            if c == '\\':
                if bs:
                    # 05.02.2020: maskiertes backslash ignorieren
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
                            uText = uText  + c
                bs = False
            ignor = False
        aktText = uText
    return aktText, underline, font, FlNum, aktSize, color
 
#print splitText(r'%%u1144',"TEXT")    
def ShapeCodepage2Utf8 (OrgShpDat, TargetShpDat, OrgCodePage):
    TargetCodePage="utf8"
    if OrgCodePage == "System":
        OrgCodePage=locale.getdefaultlocale()[1]
 
    oLayer=QgsVectorLayer(OrgShpDat,'', 'ogr')
    oLayer.setProviderEncoding(OrgCodePage)
    oLayer.dataProvider().setEncoding(OrgCodePage)
    
    # 13.08.20: Umstellung auf writeAsVectorFormatV2
    if myQGIS_VERSION_INT() < 31003:
        zLayer=QgsVectorFileWriter.writeAsVectorFormat(oLayer,TargetShpDat,TargetCodePage, oLayer.crs(), "ESRI Shapefile")
    else:
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = TargetCodePage
        zLayer=QgsVectorFileWriter.writeAsVectorFormatV2(oLayer,TargetShpDat, QgsCoordinateTransformContext(), options)
    

    #print ("Von:" + OrgShpDat)
    #print ("Nach:" + TargetShpDat)
    #print ("Mit:" + OrgCodePage)


def attTableEdit (sOutForm, inpDat,bFormat,sCharSet,gpkgTable=None):
    #print (inpDat,bFormat,sCharSet)

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
            # nur als Hinweis logen: bei einer Testdatei wurden alle Konvertierungen mit Geomatriecollektion
            # angemeckert ohne das letztendlich was gefehlt hat
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
    

    # bei Shape nur 10 Zeichen bei Feldnamen erlabt
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
                # 13.08.20: Nur bei Shape
                if sOutForm=="SHP":
                    addHinweis(tr("missing field 'SubClasses' in: ") + inpDat)
            else:
                # AcDbEntity:AcDbMText
                # AcDbEntity:AcDbText:AcDbText
                if SubClass.find("AcDbMText")>=0:
                    TxtType = "MTEXT" 
                if SubClass.find("AcDbText")>=0:
                    TxtType = "TEXT"
            att=feature.GetField('ogr_style') #http://www.gdal.org/ogr_feature_style.html
          
            try:
                aktHandle=feature.GetField('EntityHand') # bei Shape gekürzt
            except:
                aktHandle=feature.GetField('EntityHandle') 
                
            if att is None:
                addHinweis(tr("missing field 'ogr_style' in: ") + inpDat)
            
            elif att[-1] != ')':
                if aktHandle == None:
                    addHinweis(tr("incomplete field 'ogr_style' at EntityHandle: ") )
                else:
                    addHinweis(tr("incomplete field 'ogr_style' at EntityHandle: ") + str(aktHandle)) # +tryDecode(att,sCharSet))

            else:
                sArt,sDaten = trennArtDaten(att)
                #if att[:6] == "LABEL(":
                    #LABEL(f:"Arial",t:"%%c 0,40m",a:11,s:0.5g,c:#000000)
                    #print att
                
                params = csvSplit (sDaten)
                for param in params:
                    #csvSplit(csvZeile, trenn=',', tKenn='"', tKennDel = True, bOnlyFirst = False):
                    arr=csvSplit(param,":",None,None,True)
                    print (arr)
                    if len(arr) == 2:
                        f = arr[0] 
                        w = arr[1]
                        #print str(sArt),str(f),str(w)

                        if f == "c":
                            # 13.08.2020: Weiß als Darstellung "verwirrend", deshalb Grau
                            if w == "#ffffff": w="#f0f0f0"
                            feature.SetField('color', w)
                        if f == "fc":
                            # Schwarz als Füllung mach meist keinen Sinn
                            # 13.08.2020: Weiß als Darstellung "verwirrend", deshalb Grau
                            if w == "#000000": w="#f0f0f0"
                            feature.SetField('fcolor', w)
                        if f == "f":
                            feature.SetField('font', w)
                        if f == "a":
                            dWin = float(w)
                            if dWin >=360:
                                dWin = dWin - 360 # ogr bringt teilweise Winkel von 360 Grad, was funktioniert, aber verwirrt                               
                            feature.SetField('angle', dWin)
                        if f == "p":
                            if sArt == "LABEL":
                                feature.SetField('anchor', fnctxtOGRtoQGIS(int(w)))
                        if f == "s":
                            z,t=ZahlTextSplit(w)
                            # Size_u wird im Moment nicht weiter ausgewertet, da bei DXF wohl nur g = Karteneinheiten möglich
                            feature.SetField('size', z)
                            feature.SetField('size_u', t)
                            
                        # 11.11.22 dx, dy auswerten
                        if f == "dx":
                            z,t=ZahlTextSplit(w)
                            # Size_u wird im Moment nicht weiter ausgewertet, da bei DXF wohl nur g = Karteneinheiten möglich
                            feature.SetField('dx', z)
                            feature.SetField('dx_u', t)                       
                        if f == "dy":
                            z,t=ZahlTextSplit(w)
                            # Size_u wird im Moment nicht weiter ausgewertet, da bei DXF wohl nur g = Karteneinheiten möglich
                            feature.SetField('dy', z)
                            feature.SetField('dy_u', t)                       
                        
                        if f == "t":
                            # den eigentlichen Text, doch besser aus der Textspalte (z.B. wegen 254 Zeichengrenze)
                            #t,underline=splitText(w)
                            #feature.SetField('plaintext', t)
                            #feature.SetField('underline', underline)
                            dummy = 1

                    else:
                        # Text retten
                        #feature.SetField('plaintext', feature.GetField('Text'))
                        # 05.03.18: Hier sollte jetzt nichts mehr ankommen
                        addFehler(tr("incomplete field 'ogr_style': ") + tryDecode(param,sCharSet))
                    
                    if sArt == "LABEL":
                        # der eigentlichen Text
                        AktText = feature.GetField('Text')
                        if AktText is None:
                            addHinweis(tr('missing Text: ') + inpDat)
                        else:
                            dummy=AktText
                            AktText="";bDecodeError=False
                            #https://github.com/OSGeo/gdal/issues/356
                            for c in dummy:
                                if ord(c) > 54000:
                                    c="?"; bDecodeError=True
                                AktText=AktText + c
                            if bDecodeError:
                                if aktHandle == None:
                                    addFehler(tr("Wrong char in  'ogr_style' at EntityHandle: ") +  tr(" (Check your choose charset)") + tryDecode(dummy,sCharSet)) 
                                else:
                                    addFehler(tr("Wrong char in  'ogr_style' at EntityHandle: ") + aktHandle + tr(" (Check your choose charset)") + tryDecode(dummy,sCharSet)) 

                            # evtl. Formtierungen überschreiben
                            if bFormat:
                                t,underline,font, FlNum, aktSize, color = splitText(AktText,TxtType)
                                feature.SetField('plaintext', t)
                               
                                if not aktSize is None:
                                    feature.SetField('size', aktSize)
                                
                                # 05.02.20: Fehler bei Farbermittling in "splitText" beseitigt - trotzdem Fehler abfangen
                                if (color != ""):
                                    try:
                                        color=hex(int(color[1:])).replace('0x','#') 
                                        # 13.08.2020: Weiß als Darstellung "verwirrend", deshalb Grau
                                        if color == "#ffffff": color="#f0f0f0"                                        
                                        feature.SetField('color',color)
                                    except:
                                        feature.SetField('color','#FEHLER#')
                                
                                # 09.09.19: Nach Übergabe leer nicht none
                                #if not font is None:
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

if __name__ == "__main__":
    def DecodeDXFUTF(aktText):
        # Kennung ist "\u+xxxx"
        a=""
        s=aktText
        while (s.upper().find('\\U+') != -1):
            p=s.upper().find('\\U+')
            a = a + s[0:p] #;print (a)
            u=s[p+3:p+7] #;print (u)
            b=bytearray.fromhex(u) #;print(b.decode("UTF-16-BE"))
            a= a + b.decode("UTF-16-BE")
            s=s[s.upper().find('\\U+')+7:]
            #print ("Aktuell:",a)
            #print ("Rest:",s)
        return (a + s)
    print (DecodeDXFUTF (''))
    #b=bytearray.fromhex("00f6")
    #s="s1" + b.decode("UTF-16-BE") + "s2"
