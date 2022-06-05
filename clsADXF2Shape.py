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








import webbrowser
from  os import getenv, path
import getpass

try:
    from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt5.QtWidgets import QApplication, QAction,QMessageBox
    from PyQt5.QtGui import  QIcon
    myqtVersion = 5

except:
    from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
    from PyQt4.QtGui import QAction, QIcon
    myqtVersion = 4


try:
    if myqtVersion == 4:
        from .resourcesqt4 import *
    else:
        from .resources import *

    from .uiAbout      import *
    from .clsDXFTools  import *
    from .uiADXF2Shape import *
    from .fnc4all      import *
    from .fnc4ADXF2Shape import *
except:
    if myqtVersion == 4:
        from resourcesqt4 import *
    else:
        from resources import *

    from uiAbout      import *
    from clsDXFTools  import *
    from uiADXF2Shape import *
    from fnc4all      import *
    from fnc4ADXF2Shape import *

class clsADXF2Shape:


    def __del__(self):
        EZUTempClear(True)

    
    def __init__(self, iface):







       

        self.iface = iface

        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')

        if locale is None or locale == NULL:
            locale = 'en'
        else:
            locale= QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'translation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        self.dlg = uiADXF2Shape()



        self.actions = []
        self.menu = self.tr('&DXF Import/Convert')
        
        s = QSettings( "EZUSoft", fncProgKennung() )
        try:


            s.setValue( "–id–", fncXOR( str(uuid.uuid4()) + '|' + str(uuid.uuid4()) ))
        except:
            s.setValue( "–id–", fncXOR( str(uuid.uuid4()) + '|' + str(uuid.uuid4()) ))

    def tr(self, message):











        return QCoreApplication.translate('clsADXF2Shape', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):







































        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)




        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):


        icon_path = ':/plugins/AnotherDXF2Shape/m_icon.png'
        self.add_action(
            icon_path,
            text=self.tr('Import or Convert'),
            callback=self.run,
            parent=self.iface.mainWindow())  
        
        self.add_action(
            icon_path,
            text=self.tr('About/Help'),
            callback=self.About,
            parent=self.iface.mainWindow())


    def unload(self):

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr('&DXF Import/Convert'),
                action)
        

    def About(self): 

        cls=uiAbout()
        cls.exec_()
        
    def run(self):
        cls=uiADXF2Shape()
        cls.RunMenu()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    c=clsADXF2Shape(None)
    window = uiAbout()
    window.show()
    sys.exit(app.exec_())
