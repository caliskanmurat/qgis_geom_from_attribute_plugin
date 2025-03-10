# QGIS Geom From Attribute

This plugin allows users to create geometry using attributes from tables. It creates GPKG, SHP, KML, GML or GEOJSON file from QGIS compatible table based layers. There are two options to create geometry. First one is using columns, that contain X(longitude) and Y(latitude) values of Points. This method can be used only for Points. Other option is using single column, that contains Well Known Text(WKT) values of geometry. This method is used for Points, MultiPoints, Lines, MultiLines, Polygons and MultiPolygons.

If input table contains WKT values for multiple geometry types (such as Polygon, Point, Line etc.) each type is saved seperately.

<br/>
<br/>
<p align="left">
  <img width="500" src="./images/img.png">
</p>
