import re
import folium
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import mapclassify

from apiModulo.globals import *
from apiModulo.api_consulta import ApiConsulta
from custom_packages.streamlit_folium import st_folium

import warnings
warnings.filterwarnings('ignore')

import lorem
from PIL import Image
from config import getConfig
import pyproj
from geovoronoi import voronoi_regions_from_coords, points_to_region, points_to_coords

st.set_page_config(layout="wide")

style = """
    <style>
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
        #MainMenu {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }             
    </style>
"""
 
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
        
#Arredonda para 1 casa decimal e converte para string
def round_str(value):
    return str(round(value, 1))

#Gera legenda numerica
def legend_labels(array_bins, lower_value):
  labels = list()
  label = round_str(lower_value) + " - " + round_str(array_bins[0])
  labels.append(label)
  for i in range(1, len(array_bins)):
    label = round_str(array_bins[i-1]) + " - " + round_str(array_bins[i])
    labels.append(label)
  return labels

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
    if(geo[variavel].dtype == 'float'):
        # Separa os bins
        bins = mapclassify.Quantiles(geo[variavel], k=5).bins
        #Gera a leganda para os bins numericos
        labels = legend_labels(bins, geo[variavel].min())
        
        geo.explore(                
            m=m,
            column=variavel,
            scheme="UserDefined", 
            cmap="viridis",
            classification_kwds= dict(bins=bins),
            legend=True, 
            legend_kwds=dict(colorbar=False, labels=labels), 
            tooltip=[variavel]
            )

        folium.LayerControl().add_to(m)

        # #Gera o mapa com a versão alterada do st_folium passando as labels e cores da legenda
        output = st_folium(m, width=1000, height=600,
            labels=labels,
            colors=['#440154', '#3B528B', '#21918C', '#5CC863', '#FDE725'],
            title=str(variavel)
        )
    else:
        geo.explore(                
            m=m,
            column=variavel,
            categorical=True,
            categories=geo[variavel].unique(),
            cmap=colors, #Passa as cores para mapa categorico
            legend=True, 
            tooltip=[variavel]
            )

        folium.LayerControl().add_to(m)
        #Gera o mapa com legendas
        output = st_folium(m, width=1000, height=600, 
            labels= geo[variavel].unique(),
            colors= colors[:len(geo[variavel].unique())], #Passa as cores até o tamanho do numero de labels
            title=str(variavel)
            )
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

def footer():

    col1, col2, col3 = st.columns([1, 1, 4])

    slz = Image.open('assets/logo.png')
    with col1:
        st.image(slz, width=140)
    bid = Image.open('assets/logo_bid.png')
    with col2:
        st.image(bid, width=140)
    with col3:
        st.text("Implementação de PDC para análise e visualização de dados")        
        st.text("Contato: [GitHub](<https://github.com/gebraz/pdcbid>)")        
        
def header(content):
    
    st.title(f"Data Viewer - PDC - {content}")
    #st.markdown(f'<img src="assets/logo.png"/><span class="css-10trblm e16nr0p30">Pdc Viewer - {content} </span>', unsafe_allow_html=True)

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""        
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            #del st.session_state["password"]  # don't store username + password
            #del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

if True: #check_password():

    st.markdown(style,unsafe_allow_html=True)

    #configurações gerais
    #try:
    conf = getConfig()

    #sidebar()
    header("""Vem Pro Centro""")

    #tela principal
    #obtem todos os tópicos informados

    topicos = []
    for item in conf['app']:    
        for key, value in item.items():        
            if key == 'topico':
                topicos.append(value['titulo'])
    
    #monta os temas
    tabs = st.tabs(topicos)
    
    
    #carrega todos os dados necessários
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
                    
                    for elemento, valores in topico.items():                    
                        
                        #codigo para mapa
                        if elemento.startswith("mapa"):   
                            #montando combo para variáveis no mapa
                            lvariaveis = valores['variavel'].split('#')       
                            lalias = valores['alias'].split('#')

                            if valores['descricao']== '':           
                                st.write(lorem.get_sentence())
                            else:
                                st.write(valores['descricao'])
                                        
                            if valores['camada_extra'] != '':                            
                                col1, col2 = st.columns([1, 4])
                                with col1:                                      
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

    footer()                                    
    #except:
    #    print('Erro de execução')