# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeomFromAttribute
                                 A QGIS plugin
 This plugin allows users to create geometry using attributes from table. 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-03-07
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Murat Çalışkan
        email                : caliskan.murat.20@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .geom_from_attribute_dialog import GeomFromAttributeDialog
import os.path

from qgis.gui import QgsProjectionSelectionDialog

from qgis.core import Qgis, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsFields, QgsVectorFileWriter, QgsWkbTypes
from shapely.geometry import Point
from shapely.wkt import loads
from collections import defaultdict
from datetime import date

class GeomFromAttribute:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeomFromAttribute_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geom From Attribute')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeomFromAttribute', message)


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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/geom_from_attribute/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Geometry From Attribute'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Geom From Attribute'),
                action)
            self.iface.removeToolBarIcon(action)
            
    def select_output(self):
        self.dlg.le_outfile.setText("")
        self.shpPath, self._filter = QFileDialog.getSaveFileName(self.dlg, "Select out file", "", 'ESRI Shapefile (*.shp);;\
                                                                                                      Geopackage (*.gpkg);;\
                                                                                                      GeoJSON (*.geojson);;\
                                                                                                      KML (*.kml);;\
                                                                                                      GML (*.gml)')
        
        self.dlg.le_outfile.setText(self.shpPath)
    
    def enableAddLayerButton(self):
        if self.dlg.le_outfile.text():
            self.dlg.chc_add_to_map.setEnabled(True)
        else:
            self.dlg.chc_add_to_map.setEnabled(False)
    
    def checkAvaibility(self):
        if all((self.chc_crs, self.chc_layers, self.chc_fields)):
            self.dlg.btn_run.setEnabled(True)
        else:
            self.dlg.btn_run.setEnabled(False)
        
    
    def getCrs(self):
        dialog = QgsProjectionSelectionDialog()
        dialog.exec_()        
        self.crs = dialog.crs()
        
        authid = self.crs.authid()
        description = self.crs.description()

        crs_txt = f"{authid} - {description}"
        
        self.dlg.lbl_crs.setText(crs_txt)
        
        self.chc_crs = True
        
        self.checkAvaibility()
        
    
    def getFields(self):
        layerName = self.dlg.cb_layers.currentText()
        selected_layer = QgsProject.instance().mapLayersByName(layerName)[0]
        
        field_names_string = [field.name() for field in selected_layer.fields() if field.typeName().lower() in ("string", "varchar", "text")]
        field_names_numeric = [field.name() for field in selected_layer.fields() if (field.typeName().lower() in ("real", "double", "float")) or (field.typeName().lower().startswith("int"))]
        
        if (len(field_names_numeric) > 0) and (self.dlg.rb_pnt.isChecked()):
            self.chc_fields = True
        elif (len(field_names_string) > 0) and (self.dlg.rb_wkt.isChecked()):
            self.chc_fields = True
        else:
            self.chc_fields = False
            
        self.checkAvaibility()
        
        self.dlg.cb_x.clear()
        self.dlg.cb_y.clear()
        self.dlg.cb_wkt.clear()
        
        self.dlg.cb_x.addItems(field_names_numeric)
        self.dlg.cb_y.addItems(field_names_numeric)
        self.dlg.cb_wkt.addItems(field_names_string)
    
    def geomFormat(self):
        sender = self.dlg.sender()
        
        if sender.objectName() == "rb_pnt":
            if self.dlg.rb_pnt.isChecked():
                self.dlg.cb_wkt.setEnabled(False)
                
                self.dlg.cb_x.setEnabled(True)
                self.dlg.cb_y.setEnabled(True)
                self.dlg.label.setEnabled(True)
                self.dlg.label_2.setEnabled(True)
                
                self.chc_fields = True if (self.dlg.cb_x.count() > 0) and (self.dlg.cb_y.count() > 0) else False
            
        elif sender.objectName() == "rb_wkt":
            if self.dlg.rb_wkt.isChecked():
                self.dlg.cb_wkt.setEnabled(True)
                
                self.dlg.cb_x.setEnabled(False)
                self.dlg.cb_y.setEnabled(False)
                self.dlg.label.setEnabled(False)
                self.dlg.label_2.setEnabled(False)
                
                self.chc_fields = True if (self.dlg.cb_wkt.count() > 0) else False
        
        
        self.checkAvaibility()
                
    def createShp(self, layer_name, data, field_schema, srs, dtype, out_path=None, driver="ESRI Shapefile"):            
        if out_path is None:
            new_layer = QgsVectorLayer(dtype, layer_name, "memory")
            pr = new_layer.dataProvider()
            pr.addAttributes(field_schema)
            new_layer.updateFields()
            
            for d in data:
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromWkt(d[-1]))
                feat.setAttributes(d[:-1])
                pr.addFeature(feat)
                
            new_layer.updateExtents()
            new_layer.setCrs(srs)
            QgsProject.instance().addMapLayer(new_layer)
            
        else:
            fields = QgsFields()
            for f in field_schema:
                fields.append(f)
            
            
            if dtype == "Polygon":
                dtype_ = QgsWkbTypes.Polygon
            elif dtype == "MultiPolygon":
                dtype_ = QgsWkbTypes.MultiPolygon
            elif dtype == "Point":
                dtype_ = QgsWkbTypes.Point
            elif dtype == "MultiPoint":
                dtype_ = QgsWkbTypes.MultiPoint
            elif dtype == "LineString":
                dtype_ = QgsWkbTypes.LineString
            elif dtype == "MultiLineString":
                dtype_ = QgsWkbTypes.MultiLineString
            
            writer = QgsVectorFileWriter(out_path, 'UTF-8', fields, dtype_, srs, driver)
            
            for d in data:
                feat = QgsFeature()
                try:                    
                    feat.setGeometry(QgsGeometry.fromWkt(d[-1]))
                    feat.setAttributes(d[:-1])
                    writer.addFeature(feat)
                except:
                    feat = None
                    continue
            
            writer = None
            del(writer)
            
            if self.dlg.chc_add_to_map.isChecked():
                self.iface.addVectorLayer(out_path, '', 'ogr')
        
    def execute(self):
        self.dlg.btn_run.setText("RUNNING...")
        self.dlg.processEvents() 
        
        layer_name = self.dlg.cb_layers.currentText()
        selected_layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        
        feature_list = selected_layer.getFeatures()
        fields = selected_layer.fields()
        
        out_path = self.dlg.le_outfile.text()
        
        ext = out_path.split(".")[-1]
        
        drv_list = {
            "shp" : "ESRI Shapefile",
            "gpkg" : "GPKG",
            "geojson" : "GeoJSON",
            "gml" : "GML",
            "kml" : "KML"
            }
        
        if self.dlg.rb_pnt.isChecked():
            dtype = "Point"
            data = []
            
            x_col = self.dlg.cb_x.currentText()
            y_col = self.dlg.cb_y.currentText()
            
            for feat in feature_list:
                attrs = feat.attributes()
                x = feat.attribute(x_col)
                y = feat.attribute(y_col)
                   
                try:
                    wkt = Point(x,y).wkt
                    data.append([*attrs, wkt])
                except:
                    pass
            
            if out_path:
                self.createShp(layer_name, data, fields, self.crs, dtype, out_path=out_path, driver=drv_list[ext])
            else:
                self.createShp(layer_name, data, fields, self.crs, dtype, out_path=None)
                   
        elif self.dlg.rb_wkt.isChecked():
            geom_types = ["polygon", "multipolygon", "point", "multipoint", "linestring", "multilinestring"]
            wkt_col = self.dlg.cb_wkt.currentText()
            
            data = defaultdict(list)
            
            for feat in feature_list:
                attrs = feat.attributes()
                wkt = feat.attribute(wkt_col)
            
                geom  = loads(wkt)
                geom_type = geom.type
                for gt in geom_types:
                    if geom_type.lower() == gt.lower():
                        data[geom_type].append([*attrs, wkt])
                        
            for dtype, data_ in data.items():
                if out_path:
                    self.createShp(layer_name, data_, fields, self.crs, dtype, out_path=out_path.replace(f".{ext}", f"_{dtype}.{ext}"), driver=drv_list[ext])
                else:
                    self.createShp(layer_name+"_"+dtype, data_, fields, self.crs, dtype, out_path=None)
        
        self.dlg.btn_run.setText("RUN")
        self.dlg.processEvents() 
        self.iface.messageBar().pushMessage("Success", "Features created successfully!" , level=Qgis.Success, duration=5)
        
    def run(self):
        if self.first_start == True:
            self.dlg = GeomFromAttributeDialog()
            
            if any([
                (date.today().day == 23 and date.today().month == 4),
                (date.today().day == 19 and date.today().month == 5),
                (date.today().day == 30 and date.today().month == 8),
                (date.today().day == 29 and date.today().month == 10),
                (date.today().day == 10 and date.today().month == 11)
                ]):                
                self.dlg.setWindowIcon(QIcon(':/plugins/geom_from_attribute/mka.png'))
            else:
                self.dlg.setWindowIcon(QIcon(':/plugins/geom_from_attribute/icon.png'))
                
            
            self.dlg.lbl_info.setText("""<html><head/><body><a href="https://github.com/caliskanmurat/qgis_geom_from_attribute_plugin"><img width="25" height="25" src=":/plugins/geom_from_attribute/info.png"/></a></body></html>""")
            
            self.crs = None
            
            layers = [v.name() for v in QgsProject.instance().mapLayers().values() if v.type() == 0]
            self.dlg.cb_layers.clear()
            
            self.chc_layers = True if len(layers) > 0 else False           
            self.chc_crs = False
            self.chc_fields = False
            
            self.dlg.tb_crs.clicked.connect(self.getCrs)
            self.dlg.cb_layers.currentTextChanged.connect(self.getFields)
            self.dlg.rb_pnt.toggled.connect(self.geomFormat)
            self.dlg.rb_wkt.toggled.connect(self.geomFormat)
            self.dlg.tb_outfile.clicked.connect(self.select_output)
            self.dlg.btn_run.clicked.connect(self.execute)
            self.dlg.le_outfile.textChanged.connect(self.enableAddLayerButton)
            
            
            self.dlg.cb_layers.addItems(layers)
            
        self.dlg.show()
