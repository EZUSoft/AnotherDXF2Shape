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








import sys
try:
    from fnc4all import *

except:
    from .fnc4all import *


def fncProgKennung():
    return "ADXF2Shape" + str(myqtVersion)

def fncProgVersion():
    return "V " + fncPluginVersion()
    
def fncDebugMode(): 
    if (os.path.exists(os.path.dirname(__file__) + '/00-debug.txt')): 
        return True
    else:
        return False

def fncBrowserID():
    s = QSettings( "EZUSoft", fncProgKennung() )
    s.setValue( "-id-", fncXOR((fncProgKennung() + "ID=%02i%02i%02i%02i%02i%02i") % (time.localtime()[0:6])) )
    return s.value( "–id–", "" ) 
    
def tr( message):
    return message  
    
def fncCGFensterTitel(intCG = None):
    s = QSettings( "EZUSoft", fncProgKennung() )
    sVersion = "-"

    return u"Another DXF Import/Converter " + sVersion + "   (PlugIn Version: " + fncProgVersion() + ")" 

def DecodeDXFUTF(aktText):
    if sys.version[0] == "2":

        return aktText

    a=""
    s=aktText
    while (s.upper().find('\\U+') != -1):
        p=s.upper().find('\\U+')
        a = a + s[0:p] 
        u=s[p+3:p+7] 
        b=bytearray.fromhex(u) 
        a= a + b.decode("UTF-16-BE")
        s=s[s.upper().find('\\U+')+7:]


    return (a + s)    
