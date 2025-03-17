# QGIS Geom From Attribute

This plugin allows users to create layer (with geometry) using attributes from tables(CSV, excel, parquet etc.). It creates GPKG, SHP, KML, GML or GEOJSON file from QGIS compatible table based layers. There are two options to create geometry. First one is using columns, that contain X(longitude) and Y(latitude) values of Points. This method can be used only for Points. Other option is using single column, that contains Well Known Text(WKT) values of geometry. This method is used for Points, MultiPoints, Lines, MultiLines, Polygons and MultiPolygons.

If input table contains WKT values for multiple geometry types (such as Polygon, Point, Line etc.) each type is saved seperately.

<br/>
<br/>

<table>
  <tr>
    <td ><img width="500" src="./images/img.png"></td>
    <td>
      1-) Download the example data - <a href="./sample_data"/>Download<a><br/>
      2-) Open data by dragging to QGIS<br/>
      3-) Select the layer<br/>
      4-) Select the method (WKT or Point Coordinates)<br/>
      5-) Select SRS <br/>
      6-) Select output path or leave blank to create temporary data<br/>
    </td>
  </tr>
</table>

