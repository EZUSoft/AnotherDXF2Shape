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































try:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from qgis.utils import os, sys
    from PyQt5 import QtGui, uic
    from PyQt5.QtWidgets import QApplication,QMessageBox, QDialog, QTableWidgetItem, QDialogButtonBox, QFileDialog
    from PyQt5.QtCore    import QSize, QSettings, QTranslator, qVersion, QCoreApplication, QObject, QEvent

except:
    from PyQt4 import QtGui, uic
    from PyQt4.QtGui import QMessageBox, QDialogButtonBox, QDialog, QTableWidgetItem, QFileDialog
    from PyQt4.QtCore import QSize, QSettings, QTranslator, qVersion, QCoreApplication, QObject, QEvent

import os
import webbrowser
from datetime import date

try:
    from .fnc4all import *
    from .fnc4ADXF2Shape import *
    from .clsDXFTools import DXFImporter
    from .TransformTools import *
except:
    from fnc4all import *
    from fnc4ADXF2Shape import *
    from clsDXFTools import DXFImporter
    from TransformTools import *




try:
   import gdal
except:
   pass
 
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'uiADXF2Shape.ui'))





























class uiADXF2Shape(QDialog, FORM_CLASS):
    charsetList = ["System",
     "ascii",
     "big5",
     "big5hkscs",
     "cp037",
     "cp424",
     "cp437",
     "cp500",
     "cp720",
     "cp737",
     "cp775",
     "cp850",
     "cp852",
     "cp855",
     "cp856",
     "cp857",
     "cp858",
     "cp860",
     "cp861",
     "cp862",
     "cp863",
     "cp864",
     "cp865",
     "cp866",
     "cp869",
     "cp874",
     "cp875",
     "cp932",
     "cp949",
     "cp950",
     "cp1006",
     "cp1026",
     "cp1140",
     "cp1250",
     "cp1251",
     "cp1252",
     "cp1253",
     "cp1254",
     "cp1255",
     "cp1256",
     "cp1257",
     "cp1258",
     "euc_jp",
     "euc_jis_2004",
     "euc_jisx0213",
     "euc_kr",
     "gb2312",
     "gbk",
     "gb18030",
     "hz",
     "iso2022_jp",
     "iso2022_jp_1",
     "iso2022_jp_2",
     "iso2022_jp_2004",
     "iso2022_jp_3",
     "iso2022_jp_ext",
     "iso2022_kr",
     "latin_1",
     "iso8859_2",
     "iso8859_3",
     "iso8859_4",
     "iso8859_5",
     "iso8859_6",
     "iso8859_7",
     "iso8859_8",
     "iso8859_9",
     "iso8859_10",
     "iso8859_13",
     "iso8859_14",
     "iso8859_15",
     "iso8859_16",
     "johab",
     "koi8_r",
     "koi8_u",
     "mac_cyrillic",
     "mac_greek",
     "mac_iceland",
     "mac_latin2",
     "mac_roman",
     "mac_turkish",
     "ptcp154",
     "shift_jis",
     "shift_jis_2004",
     "shift_jisx0213",
     "System",
     "utf_32",
     "utf_32_be",
     "utf_32_le",
     "utf_16",
     "utf_16_be",
     "utf_16_le",
     "utf_7",
     "utf_8",
     "utf_8_sig"]
    def __init__(self, parent=None):

        super(uiADXF2Shape, self).__init__(parent)
        

        self.plugin_dir = os.path.dirname(__file__)

        locale= QSettings().value('locale/userLocale')
        if locale is None or locale == NULL:
            locale = 'en'
        else:
            locale= QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'translation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            translator = QTranslator()
            translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(translator)








        self.setupUi(self)
        self.setWindowTitle (fncCGFensterTitel())
        self.browseDXFDatei.clicked.connect(self.browseDXFDatei_clicked)    
        self.browseZielPfadOrDatei.clicked.connect(self.browseZielPfadOrDatei_clicked) 
        self.chkSHP.clicked.connect(self.chkSHP_clicked)
        self.chkGPKG.clicked.connect(self.chkGPKG_clicked)
        
        self.chk3D.clicked.connect(self.chk3D_clicked)
        

            
        
        self.listDXFDatNam.currentRowChanged.connect(self.wld4listDXFDatNam)
        self.chkTransform.clicked.connect(self.chkTransform_clicked) 
        self.optTParam.clicked.connect(self.ManageTransformSettings) 
        self.optTPoint.clicked.connect(self.ManageTransformSettings) 
        
        self.cbTArt.currentIndexChanged.connect(self.ManageTransformFelder4Kombi) 
        
        self.tabTPoints.cellChanged.connect(self.KorrAktTableValue)
        self.leTXOff.editingFinished.connect(self.KorrAktParam_leTXOff)
        self.leTYOff.editingFinished.connect(self.KorrAktParam_leTYOff)

        
        self.optTWld.clicked.connect(self.ManageTransformSettings) 
        self.optTWld.setChecked (True)
        self.cbTArt.addItem(self.tr("1 point (move)"))
        self.cbTArt.addItem(self.tr("2 point (Helmert)"))
        self.cbTArt.addItem(self.tr("3 point (Georef)"))
        self.cbTArt.addItem(self.tr("4 point (Georef)"))
        
        self.btnStart.clicked.connect(self.btnStart_clicked)          
        self.btnReset.clicked.connect(self.btnReset_clicked)  
 

        LastDay=date(2023, 5, 19)
        if (date.today() > LastDay):
            self.btnDonate.setVisible(False)
            self.lbDonate.setVisible(False)
        else:
            d= LastDay - date.today() 
            if (d.days == 0):
                self.lbDonate.setText ('!! Only today !!')  
            else:
                self.lbDonate.setText ('Only ' + str(d.days) + ' more days')  
            if myqtVersion == 4:
                self.btnDonate.setText('Donate')                
            self.btnDonate.clicked.connect(self.btnDonate_clicked) 

 
        self.StartHeight = self.height()
        self.StartWidth  = self.width()
        
        self.SetzeVoreinstellungen()
        self.TableNone2Empty(self.tabTPoints)
        listEmpty = self.tr("no DXF-file selected")
        self.listDXFDatNam.addItem (listEmpty)
        self.listDXFDatNam.setEnabled(False)  
        self.listEmpty=listEmpty
        self.FormRunning(False)

    
    def tr(self, message):











        return QCoreApplication.translate('uiADXF2Shape', message)
    
    def wld4listDXFDatNam (self):
        if self.chkTransform.isChecked() and self.optTWld.isChecked():

            if self.listDXFDatNam.currentItem() == None:
                AktDxfDatNam = self.listDXFDatNam.item(0).text()
            else:
                AktDxfDatNam = self.listDXFDatNam.currentItem().text()
            if AktDxfDatNam != self.tr("no DXF-file selected"):
                self.FillPoint4Wld (os.path.splitext(AktDxfDatNam)[0] + ".wld")
    

    def TableNone2Empty( self, tw):
        for row in range(tw.rowCount()):
            for col in range(tw.columnCount()):
                if tw.item(row,col) == None:
                    item = QTableWidgetItem('')
                    tw.setItem(row, col, item)
    
    def FillPoint4Wld (self,wldname):
        self.tabTPoints.setVisible(False)
        if os.path.exists(wldname):
            p1, p2, Fehler = ReadWldDat(wldname)
            if Fehler != None:
                self.lbT4Wld.setText (wldname + ": " + Fehler)
            
            if p1 != None:
                if p2 == None:
                    self.tabTPoints.setRowCount(1)
                else:
                    self.tabTPoints.setRowCount(2)
                self.TableNone2Empty(self.tabTPoints)
                
                self.tabTPoints.setVisible(True)
                self.tabTPoints.item(0,0).setText (str(p1[0][0]));self.tabTPoints.item(0,1).setText (str(p1[0][1]))
                self.tabTPoints.item(0,2).setText (str(p1[1][0]));self.tabTPoints.item(0,3).setText (str(p1[1][1]))                
                if p2 != None:
                    self.tabTPoints.item(1,0).setText (str(p2[0][0]));self.tabTPoints.item(1,1).setText (str(p2[0][1]))
                    self.tabTPoints.item(1,2).setText (str(p2[1][0]));self.tabTPoints.item(1,3).setText (str(p2[1][1]))    
        else:
            self.lbT4Wld.setText (wldname + ": " + self.tr("file not found"))
            
        
    def KorrAktTableValue(self):
        if self.tabTPoints.currentItem() != None:
            if self.tabTPoints.currentItem().text() !="":
                try:
                    dblValue=float(self.tabTPoints.currentItem().text().replace(",","."))
                except:
                    msgbox (self.tr("There is no float value"))
                    dblValue=""
                    self.tabTPoints.scrollToItem(self.tabTPoints.currentItem()) 
                self.tabTPoints.currentItem().setText(str(dblValue))

    def KorrAktParam_leTXOff (self):
        if self.leTXOff.text() !="":
            try:
                dblValue=float(self.leTXOff.text().replace(",","."))
            except:
                msgbox (self.tr("There is no float value"))
                dblValue=""
                self.leTXOff.setFocus()
            self.leTXOff.setText(str(dblValue))
    def KorrAktParam_leTYOff (self):
        if self.leTYOff.text() !="":
            try:
                dblValue=float(self.leTYOff.text().replace(",","."))
            except:
                msgbox (self.tr("There is no float value"))
                dblValue=""
                self.leTYOff.setFocus()
            self.leTYOff.setText(str(dblValue))

    
    def CheckKonstTransWerte(self):


        Feh = ""
        p=[[],[],[],[]] 

        if self.optTWld.isChecked():
            return True, None
        

        if  self.optTPoint.isChecked():

            for row in range(self.tabTPoints.rowCount()):
                for col in range(self.tabTPoints.columnCount()): 
                    if self.tabTPoints.item(row,col) == None:
                        Feh = "(" + str(row+1) + "," + str(col+1) + ")" + self.tr(" value missing\n")
                        return False, Feh

                    if self.tabTPoints.item(row,col).text().strip() == "":
                        Feh = "(" + str(row+1) + "," + str(col+1) + ")" + self.tr(" value missing\n")
                        return False, Feh
                p[row]=[[float(self.tabTPoints.item(row,0).text()), \
                         float(self.tabTPoints.item(row,1).text())], \
                        [float(self.tabTPoints.item(row,2).text()),\
                         float(self.tabTPoints.item(row,3).text())]]

            if self.tabTPoints.rowCount() == 1:

                p[0], p[1], p[2] = Helmert4Points(p[0], None)
            if self.tabTPoints.rowCount() == 2:

                p[0], p[1], p[2] = Helmert4Points(p[0],p[1])
            
            if self.tabTPoints.rowCount() != 4:

                p=[p[0], p[1], p[2]]
            return True, p
        

        if  self.optTParam.isChecked():

            if self.leTXOff.text() == "":
                Feh = Feh  + self.tr("X-Offset - value missing\n")
                return False, Feh
            if self.leTYOff.text() == "":
                Feh = Feh  + self.tr("Y-Offset - value missing\n")  
                return False, Feh


            xOffs=float(self.leTXOff.text())
            yOffs=float(self.leTYOff.text())
            p[0]=[[0.0,0.0],[0.0+xOffs,0.0+yOffs]]
            p[1]=[[1000.0,0.0],[1000.0+xOffs,0.0+yOffs]]
            p[2]=[[0.0,1000.0],[0.0+xOffs,1000.0+yOffs]]





            return True, p

        errbox ("Programmierfehler")
    
    def ManageTransformFelder4Kombi(self):
        if  self.optTPoint.isChecked():
            self.tabTPoints.setRowCount(self.cbTArt.currentIndex()+1)
        
        self.lbTScale.setVisible(False) 
        self.leTScale.setVisible(False) 





            
    def ManageTransformSettings(self):
        if self.chkTransform.isChecked():
            self.tabSetting.setTabEnabled(1,True)  
            
            self.tabTPoints.setVisible(self.optTPoint.isChecked() or self.optTWld.isChecked()) 
            self.tabTPoints.setEnabled(self.optTPoint.isChecked())
            
            self.grpTParam.setVisible(self.optTParam.isChecked())  
            self.cbTArt.setVisible(self.optTPoint.isChecked())     
            self.lbT4Wld.setVisible(self.optTWld.isChecked())            
            
            

            if self.optTParam.isChecked():
                pass




            if  self.optTPoint.isChecked():
                self.cbTArt.setCurrentIndex(self.tabTPoints.rowCount()-1)
                
            if  self.optTWld.isChecked():

                self.wld4listDXFDatNam()
        else:

            self.tabSetting.setTabEnabled(1,False) 


    
    def SetzeVoreinstellungen(self):
        self.ManageTransformSettings()
        
	    
        s = QSettings( "EZUSoft", fncProgKennung() )
        

        SaveWidth  = int(s.value("SaveWidth", "0"))
        SaveHeight = int(s.value("SaveHeight", "0"))
        if SaveWidth > self.minimumWidth() and SaveHeight > self.minimumHeight():
            self.resize(SaveWidth,SaveHeight)

        
        bGenCol = True if s.value( "bGenCol", "Nein" ) == "Ja" else False
        self.chkCol.setChecked(bGenCol)

        bGenLay = True if s.value( "bGenLay", "Ja" ) == "Ja" else False
        self.chkLay.setChecked(bGenLay)
        
        bFormatText = True if s.value( "bFormatText", "Ja" ) == "Ja" else False
        self.chkUseTextFormat.setChecked(bFormatText)
        
        bUseColor4Point = True if s.value( "bUseColor4Point", "Ja" ) == "Ja" else False
        self.chkUseColor4Point.setChecked(bUseColor4Point)
        bUseColor4Line = True if s.value( "bUseColor4Line", "Ja" ) == "Ja" else False
        self.chkUseColor4Line.setChecked(bUseColor4Line)
        bUseColor4Poly = True if s.value( "bUseColor4Poly", "Nein" ) == "Ja" else False
        self.chkUseColor4Poly.setChecked(bUseColor4Poly)
        
        bGen3D = True if s.value( "bGen3D", "Nein" ) == "Ja" else False
        self.chk3D.setChecked(bGen3D)
        self.chk3D_clicked()
        
        bGenSHP = True if s.value( "bGenSHP", "Nein" ) == "Ja" else False
        self.chkSHP.setChecked(bGenSHP)
        self.chkSHP_clicked()
        


        if myqtVersion == 5 :
            bGenGPKG = True if s.value( "bGenGPKG", "Nein" ) == "Ja" else False
            self.chkGPKG.setVisible(True)
        else:
            bGenGPKG = False
            self.chkGPKG.setVisible(False)
        
        self.chkGPKG.setChecked(bGenGPKG)
        self.chkGPKG_clicked()
        
        iCodePage=s.value( "iCodePage", 0 ) 
        self.txtFaktor.setText('1.3')
        self.txtErsatz4Tab.setText(' | ')


        self.cbCharSet.addItems(self.charsetList)
        self.cbCharSet.setCurrentIndex(int(iCodePage))
        try:
            self.lbGDAL.setText(gdal.VersionInfo("GDAL_RELEASE_DATE"))
        except:
            self.lbGDAL.setText("-")
			
		










    def chkTransform_clicked(self):
        self.ManageTransformSettings()
        if self.chkTransform.isChecked():
            self.tabSetting.setCurrentIndex(1)
    
    def chk3D_clicked(self):
        s = QSettings( "EZUSoft", fncProgKennung() )    
        bGen3D=self.chk3D.isChecked()
        
    def SHPorGPKG(self):
        s = QSettings( "EZUSoft", fncProgKennung() )
        if self.chkSHP.isChecked() or self.chkGPKG.isChecked():
            self.txtZielPfad.setText( s.value("lastSHPorGPKGDir", "."))
        bGenSHP=self.chkSHP.isChecked()
        bGenGPKG=self.chkGPKG.isChecked()
        self.lbOutput.setEnabled(bGenSHP or bGenGPKG)      
        self.txtZielPfad.setEnabled(bGenSHP or bGenGPKG)      
        self.browseZielPfadOrDatei.setEnabled(bGenSHP or bGenGPKG) 
        if bGenSHP or bGenGPKG:
            self.txtZielPfad.setPlaceholderText(self.tr("Specify destination path")) 
            self.lbOutput.setText(self.tr(u"Output path"))
        else:
            self.txtZielPfad.setPlaceholderText("") 
            self.lbOutput.setText("") 
    
    def chkSHP_clicked(self):
        if self.chkSHP.isChecked() and self.chkGPKG.isChecked():
            self.chkGPKG.setChecked(False) 
        self.SHPorGPKG()
   
    def chkGPKG_clicked(self):
        if self.chkSHP.isChecked() and self.chkGPKG.isChecked():
            self.chkSHP.setChecked(False) 
        self.SHPorGPKG()             
         
    def browseDXFDatei_clicked(self):
        s = QSettings( "EZUSoft", fncProgKennung() )
        lastDXFDir = s.value("lastDXFDir", ".")

        MerkAnz=self.listDXFDatNam.count()
        Anz=0
        if myqtVersion == 5:
            AllDXFDatNames=QFileDialog.getOpenFileNames(self, 'Open File', lastDXFDir, 'DXF  (*.dxf)')[0]
        else:
            AllDXFDatNames=QFileDialog.getOpenFileNames(self, 'Open File', lastDXFDir, 'DXF  (*.dxf)')
        for DXFDatName in AllDXFDatNames:
            DXFDatName=(DXFDatName).replace("\\","/")
            if Anz == 0:

                self.listDXFDatNam.clear()
                self.listDXFDatNam.setEnabled(True)     
                (dxfDir, dxfFile) = os.path.split(DXFDatName)
                if (dxfDir != ""):
                    s.setValue("lastDXFDir", dxfDir) 



            Anz=Anz+1        
            self.listDXFDatNam.addItem(DXFDatName) 
            MerkAnz=Anz
        if Anz > 0:
            self.listDXFDatNam.item(0).setSelected(True)
            self.wld4listDXFDatNam()


    def browseZielPfadOrDatei_clicked(self):
        s = QSettings( "EZUSoft", fncProgKennung() )

        lastSHPorGPKGDir = s.value("lastSHPorGPKGDir", ".")           
        if not os.path.exists(lastSHPorGPKGDir): lastSHPorGPKGDir=os.getcwd() 
        if myqtVersion == 5:
            flags = QtWidgets.QFileDialog.DontResolveSymlinks | QtWidgets.QFileDialog.ShowDirsOnly
            outDirName = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory",lastSHPorGPKGDir,flags)
        else:
            flags = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
            outDirName = QtGui.QFileDialog.getExistingDirectory(self, "Open Directory",lastSHPorGPKGDir,flags)
        outDirName=outDirName.replace("\\","/")
        self.txtZielPfad.setText(outDirName)
        if outDirName != "": s.setValue("lastSHPorGPKGDir", outDirName)


            
    def OptSpeichern(self):        
        s = QSettings( "EZUSoft", fncProgKennung() )
        s.setValue( "bGenCol", "Ja" if self.chkCol.isChecked() == True else "Nein")
        s.setValue( "bGenLay", "Ja" if self.chkLay.isChecked() == True else "Nein")
        s.setValue( "bGenSHP", "Ja" if self.chkSHP.isChecked() == True else "Nein")
        s.setValue( "bGenGPKG", "Ja" if self.chkGPKG.isChecked() == True else "Nein")
        s.setValue( "bGen3D", "Ja" if self.chk3D.isChecked() == True else "Nein")
        s.setValue( "bFormatText", "Ja" if self.chkUseTextFormat.isChecked() == True else "Nein")
        s.setValue( "bUseColor4Point", "Ja" if self.chkUseColor4Point.isChecked() == True else "Nein")
        s.setValue( "bUseColor4Line", "Ja" if self.chkUseColor4Line.isChecked() == True else "Nein")
        s.setValue( "bUseColor4Poly", "Ja" if self.chkUseColor4Poly.isChecked() == True else "Nein")
        
        s.setValue( "iCodePage", self.cbCharSet.currentIndex())
         
    def btnDonate_clicked(self):
        sLink='https://www.makobo.de/links/Donate_AnotherDXF2Shape.php?id=' + fncBrowserID()
        webbrowser.open(sLink)
        
    
    def btnReset_clicked(self):
        result = QMessageBox.question(None,'Another DXF2Shape' , self.tr('Restore default settings'), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)        
        if result == QMessageBox.Yes:
            QSettings( "EZUSoft", fncProgKennung() ).clear()
            self.resize(self.StartWidth,self.StartHeight)
            self.SetzeVoreinstellungen()
    
    def btnStart_clicked(self):

        if self.listDXFDatNam.count() == 0 or (self.listDXFDatNam.count() == 1 and self.listDXFDatNam.item(0).text() == self.listEmpty):
            QMessageBox.critical(None,  self.tr("Please specify a DXF-File"),self.tr(u"DXF-file not selected")) 
            return



        for i in range(self.listDXFDatNam.count()):
            AktDat=self.listDXFDatNam.item(i).text()
            if not os.path.exists(AktDat):
                QMessageBox.critical(None,self.tr(u"DXF-file not found"), AktDat )
                return




        if self.chkSHP.isChecked() or self.chkGPKG.isChecked() :
            ZielPfad=self.txtZielPfad.text()
        else:
            ZielPfad=EZUTempDir()
            
        if ZielPfad == "":
            QMessageBox.critical(None, self.tr("Destination path not selected"), self.tr("Please specify a target path for shapes")) 
            return
       


        if ZielPfad[-1] != "/" and ZielPfad[-1] != "\\":
            ZielPfad=ZielPfad + "/"
        if not os.path.exists(ZielPfad):
            QMessageBox.critical(None, self.tr("Destination path not found"), ZielPfad)
            return
             

        try:
            dblFaktor=float(self.txtFaktor.text().replace(",","."))
            if dblFaktor == 0:
                QMessageBox.critical(None, self.tr("Reset text height"), self.tr("Text correction factor can not assume a zero value") )
                self.txtFaktor.setText("1.3")
                return
        except:
            QMessageBox.critical(None , self.tr("Reset text height"), self.tr("Error converting Text correction factor to numbers"))
            self.txtFaktor.setText("1.3")
            return
            

        if self.chkTransform.isChecked():


            Korrekt, DreiPassPunkte=self.CheckKonstTransWerte()
            if not Korrekt:
                errbox (DreiPassPunkte)
                self.tabSetting.setCurrentIndex(1) 
                return
        else:
            DreiPassPunkte=None
            
        self.OptSpeichern()
        self.tabSetting.setCurrentIndex(0) 
        

        Haupt,Neben,Revision=fncPluginVersion().split(".")
        if myqtVersion == 5 and ( int(Haupt) >= 1 and int(Neben) >= 1): 
            out="GPKG"
        else:
            out = "SHP"
        

        if self.chkGPKG.isChecked(): out="GPKG"
        if self.chkSHP.isChecked():  out="SHP"


        Antw = DXFImporter (self,  out,      self.listDXFDatNam, ZielPfad,        self.chkSHP.isChecked() or self.chkGPKG.isChecked(), self.cbCharSet.currentText(),self.chkCol.isChecked(),self.chkLay.isChecked(), self.chkUseTextFormat.isChecked(), self.chkUseColor4Point.isChecked(), self.chkUseColor4Line.isChecked(), self.chkUseColor4Poly.isChecked(), dblFaktor, self.chkTransform.isChecked(), DreiPassPunkte, self.chk3D.isChecked(), self.txtErsatz4Tab.text())
        self.FormRunning(False) 
          
    def SetAktionText(self,txt):
        self.lbAktion.setText(txt)
        self.repaint()   
    def SetAktionAktSchritt(self,akt):
        self.pgBar.setValue(akt)
        self.repaint()

    def SetAktionGesSchritte(self,ges):
        self.pgBar.setMaximum(ges)
        self.repaint()

    
    def SetDatAktionText(self,txt):
        self.lbDatAktion.setText(txt)
        self.repaint()   
    def SetDatAktionAktSchritt(self,akt):
        self.pgDatBar.setValue(akt)
        self.repaint()

    def SetDatAktionGesSchritte(self,ges):
        self.pgDatBar.setMaximum(ges)
        self.repaint()


    def FormRunning(self,bRun):
        def Anz(ctl):
            if bRun:
                ctl.hide()
            else:
                ctl.show()
        Anz(self.lbFormat); Anz(self.lbColor); Anz(self.lbGDAL); Anz(self.lbDXF); Anz(self.lbOutput); Anz(self.lblCharSet)
        Anz(self.chkUseTextFormat);Anz(self.chkUseColor4Point); Anz(self.chkUseColor4Line); Anz(self.chkUseColor4Poly)
 
        Anz(self.btnStart) 
        Anz(self.btnReset)
        Anz(self.cbCharSet)
        Anz(self.button_box.button(QDialogButtonBox.Close))
        Anz(self.browseDXFDatei);Anz(self.browseZielPfadOrDatei)
        Anz(self.listDXFDatNam);Anz(self.txtZielPfad)
        Anz(self.chkCol); Anz(self.chkLay); Anz(self.chkSHP)
        if myqtVersion == 5: Anz(self.chkGPKG)
        Anz(self.lbFaktor);Anz(self.txtFaktor);Anz(self.txtErsatz4Tab)
        
        Anz(self.chkTransform)
        Anz(self.tabSetting)


        if bRun:
            self.lbIcon.show()
            self.pgBar.show()
            self.lbAktion.show()
            self.pgBar.setValue(0) 
            self.AktSchritt = 0 
            self.pgDatBar.show()
            self.lbDatAktion.show()
            self.pgDatBar.setValue(0) 
            self.AktDatSchritt = 0 

            self.chkSHP_clicked()
            self.chkGPKG_clicked()
        else:
            self.lbIcon.hide()
            self.pgBar.hide()
            self.lbAktion.hide()
            self.pgDatBar.hide()
            self.lbDatAktion.hide()

    def RunMenu(self):
        self.exec_()
        s = QSettings( "EZUSoft", fncProgKennung() )
        s.setValue("SaveWidth", str(self.width()))
        s.setValue("SaveHeight", str(self.height()))
