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














from qgis.utils import os
from qgis.PyQt import uic, QtWidgets, QtCore





try:
    from .fnc4ADXF2Shape import fncBrowserID
    from .qt_compat import QT6
except ImportError:
    from fnc4ADXF2Shape import fncBrowserID
    from qt_compat import QT6





d = os.path.dirname(__file__)



QtCore.QDir.addSearchPath("AnotherDXF2Shape", d)


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(d, 'uiAbout.ui')
)


class uiAbout(QtWidgets.QDialog, FORM_CLASS):







    def __init__(self, parent=None):

        super(uiAbout, self).__init__(parent)





        self.setupUi(self)





        s = self.lblLink.text()
        browser_id = fncBrowserID()

        s = s.replace(
            "$$HomepageEN$$",
            "https://makobo.de/links/Home_AnotherDXF2Shape.php?lang=EN&id=" + browser_id
        )
        s = s.replace(
            "$$HomepageDE$$",
            "https://makobo.de/links/Home_AnotherDXF2Shape.php?lang=DE&id=" + browser_id
        )

        s = s.replace(
            "$$ForumEN$$",
            "https://makobo.de/links/Forum_AnotherDXF2Shape.php?lang=EN&id=" + browser_id
        )
        s = s.replace(
            "$$ForumDE$$",
            "https://makobo.de/links/Forum_AnotherDXF2Shape.php?lang=DE&id=" + browser_id
        )

        s = s.replace(
            "$$DokuEN$$",
            "https://makobo.de/links/Dokumentation_AnotherDXF2Shape?lang=EN&id=" + browser_id
        )
        s = s.replace(
            "$$DokuDE$$",
            "https://makobo.de/links/Dokumentation_AnotherDXF2Shape?lang=DE&id=" + browser_id
        )

        self.lblLink.setText(s)





