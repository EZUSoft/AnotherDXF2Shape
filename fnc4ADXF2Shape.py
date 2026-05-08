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









import sys

try:

    from .fnc4all import *
    from .qt_compat import (
        QUrl, QByteArray,
        QNetworkAccessManager, QNetworkRequest, QNetworkReply,
        HttpStatusCodeAttribute, RedirectionTargetAttribute,
        exec_dialog, QTimer
    )
except ImportError:

    from fnc4all import *
    from qt_compat import (
        QUrl, QByteArray,
        QNetworkAccessManager, QNetworkRequest, QNetworkReply,
        HttpStatusCodeAttribute, RedirectionTargetAttribute,
        exec_dialog, QTimer
    )

from qgis.PyQt.QtCore import QEventLoop
from urllib.parse import quote


def fncProgKennung():
    return "ADXF2Shape|" + fncPluginVersion() + '|' + Qgis.QGIS_VERSION

def CheckVersion(zeit=0, debug=False):
    url = 'https://makobo.de/links/AnotherDXF2Shape.php?id=' + quote(fncProgKennung() + '|' + str(zeit))

    try:
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", b"QGIS-Plugin-ADXF2Shape")

        manager = QNetworkAccessManager()

        reply = manager.get(request)

        loop = QEventLoop()
        reply.finished.connect(loop.quit)


        timer = QTimer()
        timer.setSingleShot(True)

        def _on_timeout():
            if debug:
                print("CheckVersion: Timeout")
            if reply.isRunning():
                reply.abort()

        timer.timeout.connect(_on_timeout)
        timer.start(3000)   


        exec_dialog(loop)

        timer.stop()


        error_code = reply.error()

        if hasattr(QNetworkReply, 'NetworkError'):
            no_error = QNetworkReply.NetworkError.NoError   
        else:
            no_error = QNetworkReply.NoError                

        if error_code != no_error:
            if debug:
                print("CheckVersion Fehler:", reply.errorString())
        else:
            if debug:
                print("Request erfolgreich")

        reply.deleteLater()

    except Exception as e:
        if debug:
            print("CheckVersion Fehler:", e)


def fncProgVersion():
    return "V " + fncPluginVersion()


def fncDebugMode(): 
    if (os.path.exists(os.path.dirname(__file__) + '/00-debug.txt')):  
        return True
    else:
        return False


def fncBrowserID():
    s = QSettings("EZUSoft", fncProgKennung())
    s.setValue("-id-", fncXOR((fncProgKennung() + "ID=%02i%02i%02i%02i%02i%02i") % (time.localtime()[0:6])))
    return s.value("–id–", "")


def tr(message):
    return message  


def fncCGFensterTitel(intCG=None):
    s = QSettings("EZUSoft", fncProgKennung())
    sVersion = "-"
    return u"Another DXF Import/Converter " + sVersion + "   (PlugIn Version: " + fncProgVersion() + ")"


def DecodeDXFUTF(aktText):


    a = ""
    s = aktText
    while (s.upper().find('\\U+') != -1):
        p = s.upper().find('\\U+')
        a = a + s[0:p]
        u = s[p+3:p+7]
        b = bytearray.fromhex(u)
        a = a + b.decode("UTF-16-BE")
        s = s[s.upper().find('\\U+')+7:]
    return (a + s)


