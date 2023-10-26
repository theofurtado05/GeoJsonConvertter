from flask import Flask, request, jsonify
import os
import tempfile
import shapefile
import json
import geopandas as gpd
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
from osgeo import ogr
import fiona
from fiona.crs import from_epsg
import simplekml
from shapely.geometry import mapping
from pykml import parser
import os
import pyproj
from geo2kml import to_kml
import subprocess
from os.path import splitext
from os.path import basename
from main import GeoJsonToDxf, GeoJsonToSHP, SHPToGeoJson, DxFToGeoJson, GeoJsonToKML, KMLToGeoJson

app = Flask(__name__)

@app.route('/')
def home():
    return "Converter API is up and running!"

@app.route('/geojson-to-shp', methods=['POST'])
def geojson_to_shp():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_geojson = os.path.join(temp_dir, 'input.geojson')
        file.save(temp_geojson)
        shp_file = GeoJsonToSHP(temp_geojson)
        return jsonify({'result': shp_file})

@app.route('/shp-to-geojson', methods=['POST'])
def shp_to_geojson():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_shp = os.path.join(temp_dir, 'input.shp')
        file.save(temp_shp)
        geojson_file = SHPToGeoJson(temp_shp)
        return jsonify({'result': geojson_file})

@app.route('/geojson-to-dxf', methods=['POST'])
def geojson_to_dxf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_geojson = os.path.join(temp_dir, 'input.geojson')
        file.save(temp_geojson)
        dxf_file = GeoJsonToDxf(temp_geojson)
        return jsonify({'result': dxf_file})

@app.route('/dxf-to-geojson', methods=['POST'])
def dxf_to_geojson():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_dxf = os.path.join(temp_dir, 'input.dxf')
        file.save(temp_dxf)
        geojson_file = DxFToGeoJson(temp_dxf)
        return jsonify({'result': geojson_file})

@app.route('/geojson-to-kml', methods=['POST'])
def geojson_to_kml():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_geojson = os.path.join(temp_dir, 'input.geojson')
        file.save(temp_geojson)
        kml_file = GeoJsonToKML(temp_geojson)
        return jsonify({'result': kml_file})

@app.route('/kml-to-geojson', methods=['POST'])
def kml_to_geojson():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_kml = os.path.join(temp_dir, 'input.kml')
        file.save(temp_kml)
        geojson_file = KMLToGeoJson(temp_kml)
        return jsonify({'result': geojson_file})

if __name__ == '__main__':
    app.run(debug=True)
