#from curses import meta
#from json import tool
#import psycopg2 
#import pandas as pd
#import pandas.io.sql as sqlio
import geopandas as gpd
from sqlalchemy import create_engine
#from pathlib import Path

#from IPython.display import IFrame
from IPython.display import display, HTML
from datauri import DataURI #TODO: pip install python-datauri
import plotly.express as px #TODO: pip install plotly

from apiModulo.acesso import Acesso
from apiModulo.globals import * 
from apiModulo.api_consulta import ApiConsulta
import random
import numpy as np
import pyproj

import folium
from folium import plugins
from folium.plugins import HeatMap


#TODO melhorar as informações globais e deixá-las parametrizáveis
MAPA_CENTRO = [-2.533346622539987, -44.298776278787074] # São Luís
MAPA_ZOOM = 14.5
#globals
colors = ["red", "blue", "green", "purple", "orange", "darkred",
"lightred", "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple", "white", "pink", "lightblue", "lightgreen", "gray", "black", "lightgray"]
tabela_shape_base = 'anel_viario'


class ApiVis:
    """Classe com métodos auxiliares para visualização no Jupyter        
    """
    def __init__(self):
        """
        Construtor: responsável por estabelecer uma conexão com a fonte de dados.
        Este construtor está usando as variáveis em globais.     
        """
        #self.acessobd = Acesso(HOST, USER, DATABASE, PASS)
        #self.connection = self.acessobd.getConnection()
        #self.apiConsulta = ApiConsulta(HOST, USER, DATABASE, PASS)
    
    def __init__(self, host, user, database, p):
        """
        Construtor: responsável por estabelecer uma conexão com a fonte de dados

        :param host: endereço ip do host do banco de dados
        :param user: nome do usuario no banco de dados
        :param database: nome do database
        :param p: senha do usuário
        
        """
        self.acessobd = Acesso(host, user, database, p)
        self.connection = self.acessobd.getConnection()
        self.apiConsulta = ApiConsulta(host, user, database, p)


    def visMultiMapa(self, map=None, tipo=None, dado=None,  variavel=None, alias=None, height=1200, width=600, MAPA_ZOOM=14.5):
        
        if map is None:
            m = folium.Map(location=MAPA_CENTRO,
                        zoom_start=MAPA_ZOOM,
                        overlay=False, max_bounds=True)                        
            
            return m
        else:
            m = map

        if dado is None:
            return None

        if tipo == 'choro': 
            geo =  dado[dado[variavel].notnull()]
            try:
                geo[variavel] = geo[variavel].astype('float')     
                choropleth = geo.explore(                
                            m=m,
                            column=variavel,  # make choropleth based on "BoroName" column
                            scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
                            legend=True, # show legend
                            k=5, # use 5 bins
                            tooltip=[variavel],                
                            legend_kwds={'loc': 'center left', 'bbox_to_anchor':(1,0.5),'fmt': "{:.0f}"}, # fmt is ignored for categorical data
                            #legend_kwds=dict(colorbar=False), # do not use colorbar
                            name=alias # name of the layer in the map
                        )                
            except:
                choropleth = geo.explore(                
                            m=m,
                            column=variavel,  # make choropleth based on "BoroName" column
                            scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
                            legend=True, # show legend
                            k=5, # use 5 bins
                            tooltip=[variavel],                
                            #legend_kwds={'loc': 'center left', 'bbox_to_anchor':(1,0.5),'fmt': "{:.0f}"}, # fmt is ignored for categorical data
                            #legend_kwds=dict(colorbar=False), # do not use colorbar
                            name=alias # name of the layer in the map
                        )
            folium.LayerControl().add_to(m)

        if tipo == 'layer':            
            fg = folium.FeatureGroup(name=alias).add_to(m)
            folium.GeoJson(data=dado["geometria"]).add_to(fg)

        if tipo == 'marcador':
            geo =  dado[dado[variavel].notnull()]
            fg = folium.FeatureGroup(name=alias).add_to(m)

            cor = random.randint(0, len(colors)-1)
            for index, row in geo.iterrows():                                
                folium.Marker(location=[row['geometria'].y, row['geometria'].x],
                                icon=folium.Icon(color=colors[ cor ])).add_to(fg)
            
        if tipo == 'calor':
            geo =  dado[dado[variavel].notnull()]
            coords = []
            for index, row in geo.iterrows():
                coords.append([row['geometria'].y, row['geometria'].x])

            HeatMap(coords, min_opacity=0.4, blur = 18).add_to(folium.FeatureGroup(name=variavel + ' Heat Map').add_to(m))                
            
        return m

    #TODO: deveria receber indicardor como uma lista
    def visMapaIndicador(self, indicador, height=1200, width=600, MAPA_ZOOM=14.5):
        """
        Constroi visualização em mapa de um indicador específico
        Obrigatório que o indicador tenha suporte espacial        

        :param indicador: id do indicador no banco. Precisa consultar usando o método lstIndicador - lista separada por vírugula
        :param height: Altura de cada mapa. Por padrão 1200
        :param width: Largura de cada mapa. Por padrão 600
        :param MAPA_ZOOM: Zoom inicial do mapa. Por padrão 14.5        
        """
        # obtem indicador com dados (aqui somente com o índice, apenas 1)
        df, metadados = self.apiConsulta.obterTema(indexes=indicador)
        
        # Cabeçalho do html
        html = f"""<html>
        <body>
        """
        
        for indicador in metadados:
            m = folium.Map(location = MAPA_CENTRO, tiles = "CartoDB positron", zoom_start = MAPA_ZOOM)        
            variavel = indicador['variável']
            descricao = indicador['descrição']            
            
            df = df.replace('X', '0')
            df[variavel] = df[variavel].astype('float')
        
            #desenhando camada
            df.explore(
                m=m,
                column=variavel,  # make choropleth based on "BoroName" column
                scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
                legend=True, # show legend
                k=5, # use 10 bins
                legend_kwds=dict(colorbar=False), # do not use colorbar
                name=descricao # name of the layer in the map
            )
            #except:
            #    print("Erro com indicador: {0}".format(variavel))

            folium.LayerControl().add_to(m)
            html +=f"""
                <div style="display:inline-block;width:{width};height:{height}">
                    {descricao}
                    {m._repr_html_()}
                </div>
            """

        # Rodapé do html
        html += f"""</body>
        </html>
        """
        return HTML(html)

    def visMapaDados(self, df, metadados, height=1200, width=600, MAPA_ZOOM=14.5):
        """
        Constroi visualização em mapa de um indicador específico
        Obrigatório que o indicador tenha suporte espacial        

        :param df: GeoDataframe carregado com os dados
        :param meta: metadados das variáveis presentes no geodataframe
        :param height: Altura de cada mapa. Por padrão 1200
        :param width: Largura de cada mapa. Por padrão 600
        :param MAPA_ZOOM: Zoom inicial do mapa. Por padrão 14.5        
        """
        
        # Cabeçalho do html
        html = f"""<html>
        <body>
        """
        
        for indicador in metadados:
            m = folium.Map(location = MAPA_CENTRO, tiles = "CartoDB positron", zoom_start = MAPA_ZOOM)        
            variavel = indicador['variável']
            descricao = indicador['descrição']            
            
            df = df.replace('X', '0')
            df[variavel] = df[variavel].astype('float')
        
            #desenhando camada
            df.explore(
                m=m,
                column=variavel,  # make choropleth based on "BoroName" column
                scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
                legend=True, # show legend
                k=5, # use 10 bins
                legend_kwds=dict(colorbar=False), # do not use colorbar
                name=descricao # name of the layer in the map
            )
            #except:
            #    print("Erro com indicador: {0}".format(variavel))

            folium.LayerControl().add_to(m)
            html +=f"""
                <div style="display:inline-block;width:{width};height:{height}">
                    {descricao}
                    {m._repr_html_()}
                </div>
            """

        # Rodapé do html
        html += f"""</body>
        </html>
        """
        return HTML(html)    

    def visMapaGJson(self, gdf, variavel, descricao, height=1200, width=600, MAPA_ZOOM=14.5):
        """
        Constroi visualização em mapa de um valor específico presente em um geopandas              

        :param gdf: geopandas com os dados
        :param variavel: coluna do geopandas a ser visualizado
        :param descricao: breve descrição dos dados, a servir como legenda
        :param height: Altura de cada mapa. Por padrão 1200
        :param width: Largura de cada mapa. Por padrão 600
        :param MAPA_ZOOM: Zoom inicial do mapa. Por padrão 14.5        
        """        
        df = gdf
        
        # Cabeçalho do html
        html = f"""<html>
        <body>
        """

        m = folium.Map(location = MAPA_CENTRO, tiles = "CartoDB positron", zoom_start = MAPA_ZOOM)        

        #df = df.replace('X', '0')
        #df = df.replace('XX', '0')
        #df[variavel] = df[variavel].astype('float')
    
        #desenhando camada
        df.explore(
            m=m,
            column=variavel,  # make choropleth based on "BoroName" column
            scheme="naturalbreaks",  # use mapclassify's natural breaks scheme
            legend=True, # show legend
            tooltip=[variavel],            
            k=5, # use 10 bins
            legend_kwds=dict(colorbar=False), # do not use colorbar
            name=descricao # name of the layer in the map
        )
        #except:
        #    print("Erro com indicador: {0}".format(variavel))

        folium.LayerControl().add_to(m)
        html +=f"""
            <div style="display:inline-block;width:{width};height:{height}">
                {descricao}
                {m._repr_html_()}
            </div>
        """

        # Rodapé do html
        html += f"""</body>
        </html>
        """
        return HTML(html)    

    def visMapaSemIndicador(self, dados=None, coluna_geom=None):
        """"
            Constroi visualização em mapa sem nenhum indicador
        """
        # mapa centralizado no centro de são luís
        m = folium.Map(location = MAPA_CENTRO, tiles = "CartoDB positron", zoom_start = MAPA_ZOOM)      
        if dados is not None:
            folium.GeoJson(data=dados[coluna_geom]).add_to(m)
        return m 
