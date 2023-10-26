import tkinter as tk
from tkinter import filedialog
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
import tempfile
from flask import Flask, send_from_directory

def download_file(filename, caminho):
    directory = caminho
    return send_from_directory(directory, filename, as_attachment=True)


def GeoJsonToSHP(arquivo_geojson):
    # arquivo_geojson = filedialog.askopenfilename(filetypes=[("Arquivos GeoJSON", "*.geojson")])
    if arquivo_geojson:
        print("Arquivo selecionado:", arquivo_geojson)
        gdf = gpd.read_file(arquivo_geojson)

        # Definir a projeção EPSG 31983
        crs = pyproj.CRS.from_epsg(31983)
        gdf.crs = crs

        # Salvar como Shapefile
        # arquivo_shp = filedialog.asksaveasfilename(defaultextension=".shp", filetypes=[("Arquivos Shapefile", "*.shp")])
        temp_dir = tempfile.mkdtemp()
        arquivo_shp = os.path.join(temp_dir, 'output.shp')
        gdf.to_file(arquivo_shp, driver='ESRI Shapefile')
        return arquivo_shp

def SHPToGeoJson(arquivo_shp):
    # Solicitar o arquivo Shapefile
    # arquivo_shp = filedialog.askopenfilename(filetypes=[("Arquivos Shapefile", "*.shp")])

    if arquivo_shp:
        print("Arquivo selecionado:", arquivo_shp)
        gdf = gpd.read_file(arquivo_shp)

        # Solicitar o local para salvar o GeoJSON
        # arquivo_geojson = filedialog.asksaveasfilename(defaultextension=".geojson", filetypes=[("Arquivos GeoJSON", "*.geojson")])
        temp_dir = tempfile.mkdtemp()
        arquivo_geojson = os.path.join(temp_dir, 'output.geojson')

        if arquivo_geojson:
            gdf.to_file(arquivo_geojson, driver='GeoJSON')
            print("Arquivo GeoJSON salvo em:", arquivo_geojson)
            return arquivo_geojson

def GeoJsonToDxf(arquivo_geojson):
    # arquivo_geojson = filedialog.askopenfilename(filetypes=[("Arquivos GeoJSON", "*.geojson")])
    if arquivo_geojson:
        print("Arquivo GeoJSON selecionado:", arquivo_geojson)

        # Solicitar o local para salvar o DXF
        # arquivo_dxf = filedialog.asksaveasfilename(defaultextension=".dxf", filetypes=[("Arquivos DXF", "*.dxf")])

        temp_dir = tempfile.mkdtemp()
        arquivo_dxf = os.path.join(temp_dir, 'output.dxf')

        if arquivo_dxf:
            try:
                with fiona.open(arquivo_geojson, 'r') as src:
                    # Determinar o tipo de geometria a partir do primeiro recurso
                    first_feature = next(iter(src))
                    geometry_type = first_feature['geometry']['type']

                    # Cria um novo arquivo DXF com base no tipo de geometria do GeoJSON
                    schema = {'geometry': geometry_type, 'properties': {}}
                    with fiona.open(arquivo_dxf, 'w', 'DXF', schema, crs=from_epsg(4326)) as dst:
                        for feature in src:
                            if feature['geometry'] is not None:
                                # Copia os recursos do GeoJSON para o DXF
                                dst.write({'geometry': feature['geometry'], 'properties': {}})

                print("Arquivo DXF salvo em:", arquivo_dxf)
                return arquivo_dxf
            except Exception as e:
                print(f"Erro durante a conversão: {str(e)}")

def DxFToGeoJson(arquivo_dxf):
    # arquivo_dxf = filedialog.askopenfilename(filetypes=[("Arquivos DXF", "*.dxf")])
    if arquivo_dxf:
        print("Arquivo DXF selecionado:", arquivo_dxf)

        # Solicitar o local para salvar o GeoJSON
        # arquivo_geojson = filedialog.asksaveasfilename(defaultextension=".geojson", filetypes=[("Arquivos GeoJSON", "*.geojson")])

        temp_dir = tempfile.mkdtemp()
        arquivo_geojson = os.path.join(temp_dir, 'output.geojson')

        

        if arquivo_geojson:
            try:
                with fiona.open(arquivo_dxf, 'r', layer='entities') as src:
                    # Determinar o tipo de geometria a partir do primeiro recurso
                    first_feature = next(iter(src))
                    geometry_type = first_feature['geometry']['type']

                    # Cria um novo arquivo GeoJSON com base no tipo de geometria do DXF
                    schema = {'geometry': geometry_type, 'properties': {}}
                    with fiona.open(arquivo_geojson, 'w', 'GeoJSON', schema) as dst:
                        for feature in src:
                            if feature['geometry'] is not None:
                                # Copia os recursos do DXF para o GeoJSON
                                dst.write({'geometry': feature['geometry'], 'properties': {}})

                print("Arquivo GeoJSON salvo em:", arquivo_geojson)
                return arquivo_geojson
            except Exception as e:
                print(f"Erro durante a conversão: {str(e)}")

def GeoJsonToKML(arquivo_geojson):
    # arquivo_geojson = filedialog.askopenfilename(filetypes=[("Arquivos GeoJSON", "*.geojson")])
    if arquivo_geojson:
        print(arquivo_geojson)
        with open(arquivo_geojson) as f:
            data = json.load(f)
            kml = simplekml.Kml()
            for feature in data['features']:
                geom = feature['geometry']
                geom_type = geom['type']
                if geom_type == 'Polygon':
                    # Handle Polygon
                    kml.newpolygon(name='test',
                                    description='test',
                                    outerboundaryis=geom['coordinates'][0])
                elif geom_type == 'MultiPolygon':
                    # Handle MultiPolygon
                    for polygon in geom['coordinates']:
                        kml.newpolygon(name='test',
                                        description='test',
                                        outerboundaryis=polygon[0])
                elif geom_type == 'LineString':
                    # Handle LineString
                    kml.newlinestring(name='test',
                                      description='test',
                                      coords=geom['coordinates'])
                elif geom_type == 'Point':
                    # Handle Point
                    kml.newpoint(name='test',
                                 description='test',
                                 coords=geom['coordinates'])
                else:
                    print("ERROR: unknown type:", geom_type)
            # arquivo_kml = filedialog.asksaveasfilename(defaultextension=".kml", filetypes=[("Arquivos KML", "*.kml")])
            temp_dir = tempfile.mkdtemp()             
            arquivo_kml = os.path.join(temp_dir, 'output.kml')

            if arquivo_kml:
                kml.save(arquivo_kml)    
                print("KML salvo em:", arquivo_kml)
                return arquivo_kml
            return "Nenhum arquvio salvo"
            
            

def KMLToGeoJson(arquivo_kml):
    if arquivo_kml:
        print("Arquivo KML selecionado:", arquivo_kml)

        temp_dir = tempfile.mkdtemp()
        
        arquivo_geojson = ConvertKMLtoGeoJson(arquivo_kml, "output.geojson")
        
        # endereco_arquivo = os.path.join(temp_dir, arquivo_geojson)
        endereco_arquivo = os.path.join(temp_dir, arquivo_geojson)
        os.rename(arquivo_geojson, endereco_arquivo)

        # print('123')
        return endereco_arquivo

def ConvertKMLtoGeoJson(input_kml, output_geojson):
    command = [
        'ogr2ogr',
        '-f', 'GeoJSON',
        output_geojson,
        input_kml
    ]
    subprocess.run(command, check=True)
    return output_geojson
    
    
