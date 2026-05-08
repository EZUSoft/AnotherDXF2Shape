# -*- coding: utf-8 -*-
"""
/***************************************************************************
 A QGIS plugin
AnotherDXF2Shape: Convert DXF to shape and add to QGIS
        copyright            : (C) 2026 by EZUSoft
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
























from qgis.core import QgsProject, QgsMessageLog, Qgis

try:

    from qgis.utils import os, sys
    from qgis.PyQt.QtCore import QSettings
    from qgis.PyQt.QtWidgets import QApplication, QMessageBox
except ImportError:

    import os
    import sys
    QSettings = None
    QApplication = None
    QMessageBox = None

from itertools import cycle
from configparser import ConfigParser

import re
import time
import getpass
import traceback
import tempfile
import codecs
from glob import glob




def myQGIS_VERSION_INT():
    try:
        return Qgis.QGIS_VERSION_INT
    except Exception:
        return 0





def NodeFindByFullName(FullNode, Start=None):
    if Start is None:
        Start = QgsProject.instance().layerTreeRoot()

    sNode = FullNode if isinstance(FullNode, list) else FullNode.split("\t")
    Gefunden = None

    for node in Start.children():
        if node.__class__.__name__ == "QgsLayerTreeGroup":
            if node.name() == sNode[0]:
                if len(sNode) > 1:
                    Gefunden = NodeFindByFullName(sNode[1:], node)
                else:
                    Gefunden = node
    return Gefunden


def NodeCreateByFullName(FullNode, Start=None):



    ToDo = 0
    if Start is None:
        Start = QgsProject.instance().layerTreeRoot()

    sNode = FullNode if isinstance(FullNode, list) else FullNode.split("\t")
    Found = False

    for node in Start.children():
        if node.__class__.__name__ == "QgsLayerTreeGroup":
            if node.name() == sNode[0]:
                Found = True
                break

    if not Found:
        node = Start.addGroup(sNode[0])
        ToDo += 1

    if len(sNode) > 1:
        node, ReToDo = NodeCreateByFullName(sNode[1:], node)
        ToDo += ReToDo

    return node, ToDo


def NodeRemoveByFullName(FullNode, Start=None):
    if Start is None:
        Start = QgsProject.instance().layerTreeRoot()

    sNode = FullNode if isinstance(FullNode, list) else FullNode.split("\t")
    delNodeName = sNode[-1]

    parent = NodeFindByFullName(sNode[:-1], Start) if len(sNode) > 1 else Start
    if not parent:
        return False

    for node in parent.children():
        if node.__class__.__name__ == "QgsLayerTreeGroup":
            if node.name() == delNodeName:
                parent.removeChildNode(node)
                return True
    return False





def toUnicode(text):
    if text is None:
        return ""
    return str(text)





glFehlerListe = []
glHinweisListe = []

def addFehler(Fehler):
    glFehlerListe.append(toUnicode(Fehler))

def getFehler():
    return glFehlerListe

def resetFehler():
    global glFehlerListe
    glFehlerListe = []

def addHinweis(Hinweis):
    glHinweisListe.append(toUnicode(Hinweis))

def getHinweis():
    return glHinweisListe

def getHinweis2String():
    return "\n".join(glHinweisListe)

def resetHinweis():
    global glHinweisListe
    glHinweisListe = []





def fncPluginVersion():
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'metadata.txt'))
    return config.get('general', 'version')





def subLZF(Sonstiges=None):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    try:
        QgsMessageLog.logMessage(
            traceback.format_exc().replace("\n", "\t") +
            ("\t" + Sonstiges if Sonstiges else ""),
            'EZUSoft:Error'
        )
    except Exception:
        pass

    addFehler(
        "LZF:" + traceback.format_exc().replace("\n", "\t") +
        ("\t" + Sonstiges if Sonstiges else "")
    )


def cut4view(fulltext, zeichen=1500, zeilen=15,
             anhang='\n\n............. and many more .........\n'):
    cut = False
    ctext = fulltext[:zeichen] if len(fulltext) > zeichen else fulltext
    if len(fulltext) > zeichen:
        cut = True

    arr = ctext.split('\n')
    if len(arr) > zeilen:
        cut = True
        ctext = '\n'.join(arr[:zeilen])

    return ctext + anhang if cut else ctext


def errbox (text,p=None):
    su= toUnicode(text)

    QMessageBox.critical(None, "PlugIn Error", cut4view(su))
    try:
        QgsMessageLog.logMessage( su, u'EZUSoft:Error' )
    except:
        pass


def msgbox (text):
    su= toUnicode(text)

    QMessageBox.information(None, "PlugIn Hinweis", cut4view(su))
    try:
        QgsMessageLog.logMessage( su, u'EZUSoft:Hinweise' )
    except:
        pass

def errlog(text, DebugMode = False):
    su= toUnicode(text)   
    if DebugMode:
        QMessageBox.information(None, "DEBUG:", su)
    
    try:
        QgsMessageLog.logMessage( su, u'EZUSoft:Fehler' )
    except:
        pass

def EZUTempClear(All=None):
    Feh=0
    Loe=0
    tmp=EZUTempDir()
    if All:
        for dat in glob(tmp +'*.*'):
            try:
                os.remove(dat)
                Loe+=1
            except:
                Feh+=1
    else:
        for shp in glob(tmp +'*.shp'):
            try:
                os.remove(shp)
                Loe+=1
                for rest in glob(shp[0:-4] + '.*'):
                    os.remove(rest)
                    Loe+=1
            except:
                Feh+=1
                
    return Loe, Feh


def EZUTempDir():

    tmp=(tempfile.gettempdir()).replace("\\","/") + "/{D5E6A1F8-392F-4241-A0BD-5CED09CFABC7}/"
    if not os.path.exists(tmp):
        os.makedirs(tmp) 
    if os.path.exists(tmp):
        return tmp
    else:
        QMessageBox.critical(None,tr("Program termination"), tr("Temporary directory\n%s\ncan not be created")%tmp)
        return None

def debuglog(text,DebugMode=False):
    if DebugMode:
        su= toUnicode(text)   
        try:
            QgsMessageLog.logMessage( su, 'EZUSoft:Debug' )
        except:
            pass

def hinweislog(text,p=None):
        su= toUnicode(text)   
        try:
            QgsMessageLog.logMessage( su, 'EZUSoft:Comments' )
        except:
            pass
    
def printlog(text,p=None):
    su= toUnicode(text)        
    try:
        print (su)
    except:
        try:
            print (su.encode("utf-8"))
        except:
            print (tr("printlog:Tip can not view"))

def fncKorrDateiName (OrgName,Ersatz="_"):
    NeuTex=""
    for i in range(len(OrgName)):
        if re.search("[/\\\[\]:*?|!=]",OrgName[i]):
            NeuTex=NeuTex+Ersatz
        else:
            NeuTex=NeuTex+OrgName[i]
    return NeuTex      
    
def fncDateCode():
    lt = time.localtime()
    return ("%02i%02i%02i") % (lt[0:3])  

def fncXOR(message, key=None):
    if key==None:
        key=fncDateCode()
    return  ''.join(("%0.1X" % (ord(c)^ord(k))).zfill(2) for c,k in zip(message, cycle(key)))


def ifAscii(uText):
    try:
        for char in uText:
            if(ord(char))> 128:
              return False   
        return True
    except:
        return False 
    
def toUTF8(uText):








    try:
        a=""
        for char in uText:
            a= a + chr(ord(char))
        return a.decode("utf8")
    except:
        return uText    
        
def tryDecode(txt,sCharset):
    try:
        return str(bytes(txt,"utf8").decode(sCharset) )
    except:
        return txt


def ClearDir(Verz):
    for dat in glob(Verz +'*.*'):
        try:
            os.remove(dat)
        except:
            return False
    return True
    
def fncMakeDatName (OrgName):
    v=OrgName.replace("\\","/")
    return v.replace("//","/")

def qXDatAbsolute2Relativ(tmpDat, qlrDat, PathAbsolute):


        subPath=fncMakeDatName(PathAbsolute + "/") 
        iDatNum = open(tmpDat)
        oDatNum = open(qlrDat,"w")
        for iZeile in iDatNum:
            s1=iZeile.replace('source="' + subPath,'source="./') 
            s1=s1.replace('k="name" v="' + subPath,'k="name" v="./') 
            s1=s1.replace('<datasource>' + subPath,'<datasource>./') 
            oDatNum.write(s1)
        iDatNum.close()
        oDatNum.close()
        os.remove(tmpDat)

def fncUniDatReadAll23(DatName,sEncode):




    tmp = open(DatName, "r", encoding=sEncode)

    tmpArray =tmp.readlines()
    tmp.close()
    return tmpArray

def subUniDatWriteAll23(DatName, Art, zArray,sEncode):





    tmp = open(DatName, Art, encoding=sEncode)

    tmp.writelines(zArray)
    tmp.close()
    
def fncUniDatOpen23 (DatName, Art, sEncode):
    tmp = open(DatName, Art, encoding=sEncode)

    return tmp
        
