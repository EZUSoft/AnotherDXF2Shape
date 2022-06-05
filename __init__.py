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









def classFactory(iface):  






    from .clsADXF2Shape import clsADXF2Shape
    return clsADXF2Shape(iface)
