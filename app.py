#from cProfile import label
#from re import X
import re
#from tkinter import Y
#from turtle import fillcolor
#from types import NoneType
#from attr import field
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from apiModulo.globals import *
from apiModulo.api_consulta import ApiConsulta
import warnings
warnings.filterwarnings('ignore')

import lorem
from PIL import Image
from config import getConfig
import pyproj
from geovoronoi import voronoi_regions_from_coords, points_to_region, points_to_coords


st.set_page_config(layout="wide")
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    print("Style não encontrado")

#globals
colors = ["red", "blue", "green", "purple", "orange", "darkred",
"lightred", "beige", "darkblue", "darkgreen", "cadetblue", "darkpurple", "white", "pink", "lightblue", "lightgreen", "gray", "black", "lightgray"]
id =1 #id sequencial para componentes visual do streamlit

@st.cache(allow_output_mutation=True)
def loadData(conf):
    """
        Load de todos os dados informados no YAML

        :param conf: dicionário vindo da leitura do YAML
        :return data, georet: dados e camadas espaciais
    """
    tlist = []
    clist = []
    apiCons = ApiConsulta(host=HOST, user=USER, database=DATABASE, p=PASS)

    #tabela e camada precisam ser 1 para 1 por conta do merge
    for item in conf['app']:
        for key, value in item.items():                        
            if 'topico' in key:                     
                for elemento, valor in value.items():
                    if elemento.startswith("mapa"):     
                        if valor['tabela'] not in tlist:
                            tlist.append(valor['tabela'])
                        if valor['camada'] not in clist:
                            clist.append(valor['camada'])  
                    elif elemento.startswith("grafico"):
                        if valor['tabela'] not in tlist:
                            tlist.append(valor['tabela'])  
    data = {}
    georet  = {} 

    #obtendo os dados
    for i in range(0, len(tlist)):
        
        df = apiCons.obterTabela(tlist[i])
        df['id'] = df['cod_camada']    
        df['cod_camada'] = df['cod_camada'].apply(lambda x: str(x))
        df['id'] = df['id'].apply(lambda x: str(x))
        df.set_index('cod_camada', inplace=True)            
        
        geo = apiCons.obterCamada(clist[i], simples=True)
        geo['cod_camada'] = geo['cod_camada'].apply(lambda x: str(x))
        geo.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        
        merged = geo.merge(df, on='cod_camada').drop_duplicates(subset=['cod_camada'])
        geo_final = merged.set_index('cod_camada')            

        data[tlist[i]]  = {'df':df}        
        georet[clist[i]]= {'geo':geo_final}

    #Para obter camadas extras    
    for item in conf['app']:
        for key, value in item.items():                        
            if 'camada_padrao' in key:    
                tabela = value['tabela']
                lcampos_padrao = value['campos'].split('#')
                ldescr_padrao = value['descricao'].split('#')
                lpopup_padrao = value['popup'].split('#')
                ldescpopup_padrao = value['desc_popup'].split('#')
                info = value['info']                
                tipo = value['tipo']                
                                
                dados = apiCons.obterCamada(tabela, simples=False)                            
                dados.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
                dados = dados.set_index('cod_camada')

                georet[tabela]= {'dados':dados, 
                                 'info': info, 
                                 'tipo':tipo, 
                                 'campos':lcampos_padrao, 
                                 'descricao':ldescr_padrao,
                                 'popup': lpopup_padrao, 
                                 'desc_popup': ldescpopup_padrao}            

            if 'area_shape_basico' in key:
                tabela = value['tabela']
                info = value['info']                
                tipo = value['tipo']  

                dados = apiCons.obterCamada(tabela, simples=False)                            
                dados.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
                dados = dados.set_index('cod_camada')

                georet[tabela]= {'dados':dados, 
                                 'info': info, 
                                 'tipo': tipo}
    return data, georet

def addMapMarcador(m, camada, camada_sel):
    """
        Adiciona marcados (pontos) num mapa

        :param camada: camada previamente informada com os pontos
        :param camada_sel: filtro selecionado na interface gráfica        
    """
    listCampos = camada['descricao']
    listVariaveis = camada['campos']
    listPopup = camada['popup']
    listDescPopup = camada['desc_popup']
    dados = camada['dados']

    for campo in camada_sel:
        i = listCampos.index(campo)        
        dados = dados[dados[listVariaveis[i]].notnull()]                

        fg = folium.FeatureGroup(name=campo).add_to(m)
        for index, row in dados.iterrows():
            popup = ''
            for j in range(len(listPopup)):
                popup += str(listDescPopup[j]) + ": " + str(row[listPopup[j]]) + "</br>" 
                folium.Marker(location=[row['geometria'].y, row['geometria'].x],
                            icon=folium.Icon(color=colors[i]), 
                            popup=popup).add_to(fg)
        
def addMapHeat(m, camada, camada_sel): 
    """
        A partir dos pontos selecionados, cria um mapa de calor

        :param camada: camada previamente informada com os pontos
        :param camada_sel: filtro selecionado na interface gráfica        
    """
    listCampos = camada['descricao']
    listVariaveis = camada['campos']
    dados = camada['dados']

    for campo in camada_sel:
        i = listCampos.index(campo)
        dados = dados[dados[listVariaveis[i]].notnull()]  
        coords = []
        for index, row in dados.iterrows():
            coords.append([row['geometria'].y, row['geometria'].x])

        folium.plugins.HeatMap(coords, min_opacity=0.4, blur = 18).add_to(folium.FeatureGroup(name=campo + 'Heat Map').add_to(m))        

def addMapVoronoi(m, camada, area_base, camada_sel): 
    """
        A partir dos pontos selecionados, cria um mapa de Voronoi

        :param camada: camada previamente informada com os pontos
        :param area_base: geometria base para filtrar os limites do voronoi
        :param camada_sel: filtro selecionado na interface gráfica        
    """                      
    listCampos = camada['descricao']
    listVariaveis = camada['campos']
    dados = camada['dados']
    area_shape = area_base['dados']
    area_shape = area_shape.iloc[0].geometria

    coords = []
    for campo in camada_sel:
        i = listCampos.index(campo)
        dados = dados[dados[listVariaveis[i]].notnull()]  #filtro não nulos
        dados = dados[dados.intersects(area_shape)] #filtro pela área base            
                
        for index, row in dados.iterrows():
            coords.append([row['geometria'].x, row['geometria'].y])
        
        fg = folium.FeatureGroup(name=campo + " voronoi").add_to(m)        
        
        polys, pts = voronoi_regions_from_coords(np.array(coords), area_shape)
        index = points_to_region(pts)

        N = len(polys)
        geometries = [polys[index[k]] for k in range(N)]
        data = gpd.GeoDataFrame(crs=4326, geometry=geometries)
        #data.geometry = geometries

        folium.GeoJson(data=data,style_function=lambda x: {'color': colors[i],  'fillColor': 'darkred'}).add_to(fg)
        
def addMap(geo, variavel, alias, 
            camadas_extra=None, 
            camada_interna=None, 
            camada_base=None, 
            ponto_tipo='Marcador'): 
    """
        Função básica para inclusão de mapas

        :param geo: camada geográfica e dados
        :param variavel: informação que deve ser exibida no mapa, numa escala de cor
        :param alias: nome formatado da variável
        :param camadas_extra: informação de camada adicional a ser inserida por seleção
        :param camadas_interna: informação de camada adicional a ser inserida por padrão
        :param camadas_base: limites da área de interesse, usado pelo voronoi
        :param ponto_tipo: Marcador - Calor ou Voronoi
    """ 

    m = folium.Map(location=[-2.533346622539987, -44.298776278787074],
                    zoom_start=15,
                    overlay=False, max_bounds=True)
    
    #incluindo camadas obrigatórias: modo = interna no YAML
    if camada_interna is not None:
        dados = camada_interna['dados']
        folium.GeoJson(data=dados["geometria"], 
                tooltip=dados[camada_interna['popup']], name=camada_interna['info']).add_to(m)
        

    #havendo seleçao em camadas extras
    #tipos de camadas de pontos: ['Marcador', 'Calor', 'Voronoi']
    if camada_sel and camadas_extra is not None:
        #descobrir a camada da seleção                    

        if camadas_extra['tipo'] == 'ponto':
            if ponto_tipo == 'Marcador':
                addMapMarcador(m, camada=camadas_extra, camada_sel=camada_sel)
            elif ponto_tipo == 'Calor':
                addMapHeat(m, camada=camadas_extra, camada_sel=camada_sel)
            else:
                addMapMarcador(m, camada=camadas_extra, camada_sel=camada_sel)
                addMapVoronoi(m, camada=camadas_extra, area_base=camada_base, camada_sel=camada_sel )

    #mapa de cores para uma determinada variável             
    geo =  geo[geo[variavel].notnull()]
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

    output = st_folium(m, width = 1000, height=500)
    #st.write(output)

    global last_layer_id_clicked
    last_layer_id_clicked = output['last_active_drawing']
    #print(last_layer_id_clicked)
    if(last_layer_id_clicked is not None):
        #print(last_layer_id_clicked)
        try:
            last_layer_id_clicked = output['last_active_drawing']['properties']['cod_camada']
        except:
            print()
    
def addGrafico(data, variaveis, variaveis_alias, alias, tipo, agg='sum'):
    """
        Gera gráficos de acordo com a configuração informada no YAML

        :param data: dados para construção do gráfico
        :param variaveis: colunas a serem coletadas de data
        :param variaveis_alias: nome formatado das variáveis
        :param alias: filtro selecionado na interface gráfica
        :param tipo: tipo do mapa, configurado no YAML
        :param agg: 

    """     

    cdata = []
    for i in variaveis:
        cdata.append(data[i].sum(axis=0))

    chart_data = pd.DataFrame(cdata, columns=alias)
    chart_data['Variaveis'] = variaveis_alias
    
    if tipo == 'barra_vertical':
        fig = px.bar(chart_data, x='Variaveis', y=alias[0])
    
    elif tipo == 'barra_horizontal':
        fig = px.bar(chart_data, x=alias[0], y='Variaveis', orientation='h')

    elif tipo == 'pizza':
        fig = px.pie(chart_data, values= alias[0], names='Variaveis')

    elif tipo == 'scatter':
        fig = px.scatter(chart_data, x='Variaveis', y=alias[0])
    
    elif tipo == 'linha':
        fig = px.line(chart_data, x='Variaveis', y=alias[0], color='Variaveis')
        
    # elif tipo == 'histograma':
    #     fig = px.histogram(chart_data, x= alias[0])

    else:
        fig = go.Figure()

    st.plotly_chart(fig, use_container_width=True)

def sidebar():
    #sidebar
    slz = Image.open('assets/logo.png')
    st.sidebar.image(slz)

    st.sidebar.title("Sobre")
    st.sidebar.info(
        """Implementação de PDC para análise e visualização de dados. Parceria BID - Banco Interamericano de Desenvolvimento / Prefeitura de São Luís - MA"""
    )

    st.sidebar.title("Contato")
    st.sidebar.info(
        """
        SEMISPE / NCA
        [GitHub](<https://github.com/gebraz/...>)
        """
    )

    bid = Image.open('assets/logo_bid.png')
    st.sidebar.image(bid)


#configurações gerais

#try:
conf = getConfig()

sidebar()

#tela principal
#obtem todos os tópicos informados

topicos = []
for item in conf['app']:    
    for key, value in item.items():        
        if key == 'topico':
            topicos.append(value['titulo'])
    
tabs = st.tabs(topicos)
#carrega todos os dados necessários
#TODO: provavel que tenhamos que colocar os shapes em um WMS
data, geo = loadData(conf)

i=-1
for item in conf['app']:
    for key, value in item.items():        
        if key == 'topico':
            topico = value            
            i = i+1
            with tabs[i]:
                st.title(topico['titulo'])
                if topico['descricao']== '':           
                    st.write(lorem.get_sentence())
                else:
                    st.write(topico['descricao'])
                st.subheader(topico['descricao'])

                for elemento, valores in topico.items():                    
                    #codigo para mapa
                    if elemento.startswith("mapa"):   
                        #montando combo para variáveis no mapa
                        lvariaveis = valores['variavel'].split('#')       
                        lalias = valores['alias'].split('#')

                        if valores['camada_extra'] != '':                            
                            col1, col2 = st.columns([1, 3])
                            with col1:  
                                
                                if topico['descricao']== '':           
                                    st.write(lorem.get_sentence())
                                else:
                                    st.write(topico['descricao'])
                
                                var_sel = st.selectbox('Variáveis disponíveis', 
                                                    options=lalias, 
                                                    key=id)
                                id = id+1    
                                camada_sel = st.multiselect(geo[valores['camada_extra']]['info'],
                                                    options=geo[valores['camada_extra']]['descricao'], 
                                                    key=id)
                                id=id+1
                            
                                ponto_tipo = st.selectbox('Tipo Mapa Ponto', 
                                                    options=['Marcador', 'Calor', 'Voronoi'], 
                                                    key=id)
                                id = id+1
                                
                            with col2:  
                                index = lalias.index(var_sel) 
                                if valores['camada_extra'] != '':
                                    addMap(geo[valores['camada']]['geo'],                                  
                                            lvariaveis[index],                                
                                            lalias[index], 
                                            geo[valores['camada_extra']] if valores['camada_extra']!='' else None,
                                            geo[valores['camada_interna']] if valores['camada_interna']!='' else None,                            
                                            geo[valores['camada_base']] if valores['camada_base']!='' else None,                            
                                            ponto_tipo) 
                        else:
                            var_sel = st.selectbox('Variáveis disponíveis', 
                                                    options=lalias, 
                                                    key=id)
                            id = id+1

                            index = lalias.index(var_sel) 
                            if valores['camada_extra'] != '':
                                addMap(geo[valores['camada']]['geo'],                                  
                                        lvariaveis[index],                                
                                        lalias[index], 
                                        geo[valores['camada_extra']] if valores['camada_extra']!='' else None,
                                        geo[valores['camada_interna']] if valores['camada_interna']!='' else None,                            
                                        ponto_tipo)    

                    if re.search("^grafico.*$", elemento) != None:
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.write(valores['titulo'])                
                            if valores['descricao']=='':
                                st.write(lorem.get_paragraph())
                            else:
                                st.write(valores['descricao'])
                        with col2:
                            df = data[valores['tabela']]['df']
                            if last_layer_id_clicked != None:
                                df = df.loc[df['id'] == last_layer_id_clicked]
                            addGrafico(df, 
                                valores['x'],
                                valores['x_alias'],
                                valores['y'],
                                valores['tipo'])
#except:
#    print('Erro de execução')