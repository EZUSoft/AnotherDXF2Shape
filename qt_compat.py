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








from qgis.PyQt import QtCore, QtWidgets, QtNetwork
from qgis.core import QgsProject
import qgis




QT_VERSION_STR = QtCore.QT_VERSION_STR
QT6 = QT_VERSION_STR.startswith("6")




AlignLeft = QtCore.Qt.AlignmentFlag.AlignLeft if QT6 else QtCore.Qt.AlignLeft
AlignRight = QtCore.Qt.AlignmentFlag.AlignRight if QT6 else QtCore.Qt.AlignRight
AlignCenter = QtCore.Qt.AlignmentFlag.AlignCenter if QT6 else QtCore.Qt.AlignCenter


Horizontal = QtCore.Qt.Orientation.Horizontal if QT6 else QtCore.Qt.Horizontal
Vertical = QtCore.Qt.Orientation.Vertical if QT6 else QtCore.Qt.Vertical


Checked = QtCore.Qt.CheckState.Checked if QT6 else QtCore.Qt.Checked
Unchecked = QtCore.Qt.CheckState.Unchecked if QT6 else QtCore.Qt.Unchecked


Close = QtWidgets.QDialogButtonBox.StandardButton.Close if QT6 else QtWidgets.QDialogButtonBox.Close
Ok = QtWidgets.QDialogButtonBox.StandardButton.Ok if QT6 else QtWidgets.QDialogButtonBox.Ok
Cancel = QtWidgets.QDialogButtonBox.StandardButton.Cancel if QT6 else QtWidgets.QDialogButtonBox.Cancel
Yes = QtWidgets.QDialogButtonBox.StandardButton.Yes if QT6 else QtWidgets.QDialogButtonBox.Yes
No = QtWidgets.QDialogButtonBox.StandardButton.No if QT6 else QtWidgets.QDialogButtonBox.No
Apply = QtWidgets.QDialogButtonBox.StandardButton.Apply if QT6 else QtWidgets.QDialogButtonBox.Apply
Reset = QtWidgets.QDialogButtonBox.StandardButton.Reset if QT6 else QtWidgets.QDialogButtonBox.Reset
Help = QtWidgets.QDialogButtonBox.StandardButton.Help if QT6 else QtWidgets.QDialogButtonBox.Help




if QT6:

    ItemFlags = QtCore.Qt.ItemFlags
    ItemIsSelectable = QtCore.Qt.ItemFlag.ItemIsSelectable
    ItemIsEnabled = QtCore.Qt.ItemFlag.ItemIsEnabled
    ItemIsUserCheckable = QtCore.Qt.ItemFlag.ItemIsUserCheckable
    ItemIsTristate = QtCore.Qt.ItemFlag.ItemIsAutoTristate  
    WindowContextHelpButtonHint = QtCore.Qt.WindowType.WindowContextHelpButtonHint
    WaitCursor = QtCore.Qt.CursorShape.WaitCursor
else:

    ItemFlags = QtCore.Qt.ItemFlags
    ItemIsSelectable = QtCore.Qt.ItemIsSelectable
    ItemIsEnabled = QtCore.Qt.ItemIsEnabled
    ItemIsUserCheckable = QtCore.Qt.ItemIsUserCheckable
    ItemIsTristate = QtCore.Qt.ItemIsTristate  
    WindowContextHelpButtonHint = QtCore.Qt.WindowContextHelpButtonHint
    WaitCursor = QtCore.Qt.WaitCursor

def flags_with_checks(flags, *checks):


    result = flags
    for _ in checks:
        result |= ItemIsUserCheckable
    return result




QGIS_VERSION_INT = int(getattr(qgis.core.Qgis, "QGIS_VERSION_INT", 0))
QGIS3 = QGIS_VERSION_INT < 40000
QGIS4 = QGIS_VERSION_INT >= 40000




def run_processing(alg, params, legacy=False):
    import processing
    if legacy:
        return processing.runalg(alg, **params)
    else:
        return processing.run(alg, params)




def add_layer(layer, addToLegend=False):
    QgsProject.instance().addMapLayer(layer, addToLegend)




def exec_dialog(dialog):
    if QT6:
        return dialog.exec()
    else:
        return dialog.exec_()




QNetworkAccessManager = QtNetwork.QNetworkAccessManager
QNetworkRequest = QtNetwork.QNetworkRequest
QNetworkReply = QtNetwork.QNetworkReply

QUrl = QtCore.QUrl
QByteArray = QtCore.QByteArray
QTimer = QtCore.QTimer   


if hasattr(QNetworkRequest, "HttpStatusCodeAttribute"):

    HttpStatusCodeAttribute = QNetworkRequest.HttpStatusCodeAttribute
else:
    try:

        HttpStatusCodeAttribute = QNetworkRequest.Attribute.HttpStatusCodeAttribute
    except AttributeError:
        HttpStatusCodeAttribute = None

if hasattr(QNetworkRequest, "RedirectionTargetAttribute"):

    RedirectionTargetAttribute = QNetworkRequest.RedirectionTargetAttribute
else:
    try:

        RedirectionTargetAttribute = QNetworkRequest.Attribute.RedirectionTargetAttribute
    except AttributeError:
        RedirectionTargetAttribute = None





def is_qgis3_qt6():
    return QGIS3 and QT6




if QT6:
    DontResolveSymlinks = QtWidgets.QFileDialog.Option.DontResolveSymlinks
    ShowDirsOnly = QtWidgets.QFileDialog.Option.ShowDirsOnly
else:
    DontResolveSymlinks = QtWidgets.QFileDialog.DontResolveSymlinks
    ShowDirsOnly = QtWidgets.QFileDialog.ShowDirsOnly
    


if QT6:
    MsgBox_Yes = QtWidgets.QMessageBox.StandardButton.Yes
    MsgBox_No = QtWidgets.QMessageBox.StandardButton.No
    MsgBox_Cancel = QtWidgets.QMessageBox.StandardButton.Cancel
else:
    MsgBox_Yes = QtWidgets.QMessageBox.Yes
    MsgBox_No = QtWidgets.QMessageBox.No
    MsgBox_Cancel = QtWidgets.QMessageBox.Cancel
