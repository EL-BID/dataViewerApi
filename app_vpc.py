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
#path para a biblioteca do apiModulo. Ajuste de acordo com a necessidade
from apiModulo.api_consulta import ApiConsulta
from apiModulo.api_visualizacao import ApiVis
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
"lightred", "darkblue", "darkgreen", "cadetblue", "darkpurple", "pink", "lightblue", "lightgreen", "black"]


@st.cache(allow_output_mutation=True)
def loadData():    
    apiCons = ApiConsulta(host=HOST, user=USER, database=DATABASE, p=PASS)

    #obtendo lotes
    lotes = apiCons.obterCamada('lotes')

    #obtendo lotes por ponto
    lotes['centroid'] =  lotes['geometria'].centroid

    #obtendo zonas de interesse social
    zis = apiCons.obterCamada('zis')

    #obtendo linhas de onibus
    linhas = apiCons.obterCamada('linhas_onibus')    
    
    #obtendo tombamento estadual
    tomb_estadual = apiCons.obterCamada('tombamento_estadual')

    #obtendo tombamento federal
    tomb_federal = apiCons.obterCamada('tombamento_federal')

    #obtendo hex de densidade populacional
    hdx = apiCons.obterCamada('hdx_populacao_2020')

    #adicionando equipamentos informados pela prefeitura
    equipamentos = apiCons.obterCamada('equipamento_publico', simples=False)

    #adicionando dados do ibge, em setor censitário, quanto a domicilio01, v018-v022 - esgotamento
    domicilios, m = apiCons.obterIndicador(tabela='ibge_domicilio01', definicao="""'v018', 'v019', 'v020', 'v021', 'v022'""")
    domicilios = apiCons.limparDados(domicilios)

    #limpando dados
    lotes['ocupacao'].fillna(value='ND', inplace=True)
    lotes['conservacao'].fillna(value='ND', inplace=True)
    lotes['tipologia_semfaz'].fillna(value='ND', inplace=True)

    return lotes,  zis, linhas, tomb_estadual, tomb_federal, hdx, equipamentos, domicilios
 
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

def main():
    st.markdown(style,unsafe_allow_html=True)

    #sidebar()
    header("""Vem Pro Centro""")

    #tela principal
    #obtem todos os tópicos informados

    #monta os temas
    #tabs = st.tabs(topicos)
    tabs = st.radio('Escolha:', topicos, horizontal=True, index=2)
    
    if tabs == topicos[0]:
        i = 0
    elif tabs == topicos[1]:
        i = 1
    else:        
        i = 2
        
    with st.form(key=f"tab{i}"):
        #st.title(topicos[0])
        st.write(valores[f"topico{i+1}"]["criterio"] + " --- Lotes em azul, ZIS em vermelho. Use os controles para ativar as demais opções.")
        

        ocu, con, ar = st.columns(3)
        with ocu:              
            ocupacoes_sel = st.multiselect("Ocupação",
                        options=['Edificação Subutilizada', 'Estacionamento', 'Edificação sem uso', 'Terreno não edificado', 'TODAS'], 
                        default=valores[f"topico{i+1}"]["ocupacao"])
        with con:
            conservacao_sel = st.multiselect("Conservação",
                        options=['Regular', 'Ótimo', 'Bom', 'Péssimo ou em Risco', 'Perda', 'TODAS'], 
                        default=valores[f"topico{i+1}"]["conservacao"])
        with ar:
            area_slides = st.slider('Área', 0.0, valores[f"topico{i+1}"]["max"], valores[f"topico{i+1}"]["area"])

        ind, mapa = st.columns([1, 4])

        with ind:
            tipologia_sel = st.multiselect("Tipologia",
                        options=['apto frente','apto fundos','apto terreo','barraco','casa','cob metalica','com c/ residencia','deposito','edificação complementar','galpao','garagem','loja/sala/conjunto','predial','sobrado','sobrado colonial','telheiro','templo','TODAS'],
                        default=valores[f"topico{i+1}"]["tipologia"])
            divida_chk = st.checkbox('Exibir lotes com dívida?', value=valores[f"topico{i+1}"]["divida"])
            distancia_slider = st.text_input("Distancia ônibus", value=valores[f"topico{i+1}"]["distancia"])
            indicador_sel = st.selectbox('Indicadores', 
                                    options=['Selecione', 'População Total (densidade)', 'Esg. fossa séptica', 'Esg. fossa rudimentar', 'Esg. vala', 'Esg. rio, lago ou mar', 'Esg. outro'],
                                    index=valores[f"topico{i+1}"]["indicador"])    
            equipamento_sel = st.selectbox('Equipamentos', 
                                    options=['Assistência Social', 'Educação', 'Equipamento Cultural', 'Saúde', 'Segurança'], 
                                    index=valores[f"topico{i+1}"]["equipamento"]) 

            submit_button = st.form_submit_button(label='Pesquisar', on_click=refresh)
            
        with mapa:            
            addMapEsp(ocupacoes_sel, conservacao_sel, area_slides, tipologia_sel, indicador_sel, equipamento_sel, divida_chk, distancia_slider)

        addGraficoEsp(ocupacoes_sel, conservacao_sel, area_slides, tipologia_sel, indicador_sel, equipamento_sel, divida_chk)

def refresh():
    print("refresh")

def addMapEsp(ocupacoes_sel, conservacao_sel, area_slides, tipologia_sel, indicador_sel, equipamento_sel, divida_chk, distancia_slider):
    apiVis = ApiVis(host=HOST, user=USER, database=DATABASE, p=PASS)
    
    #ação quando selecionar itens
    filtrado = lotes
    if distancia_slider != "":
        apiCons = ApiConsulta(host=HOST, user=USER, database=DATABASE, p=PASS)
        linhas_buffer = apiCons.obterCamada('linhas_onibus')
        linhas_buffer = linhas_buffer.to_crs(3857)
        lotes_buffer = apiCons.obterCamada('lotes')
        lotes_buffer = lotes_buffer.to_crs(3857)
        
        distancia = int(distancia_slider)     
        linhas_buffer = linhas_buffer.buffer(distance=distancia*2)    
        filtrado = lotes_buffer[lotes_buffer.intersects(linhas_buffer)]     
        filtrado.to_crs(4326)   
        #print(filtrado.shape[0])
   
    filtrado = filtrado[(filtrado['AREA_HTL']>=area_slides[0]) & (filtrado['AREA_HTL']<=area_slides[1])]    
    #print(filtrado.shape[0])
    if not "TODAS" in ocupacoes_sel:
        filtrado = filtrado[filtrado['ocupacao'].isin(ocupacoes_sel)]    
    if not "TODAS" in conservacao_sel:    
        filtrado = filtrado[filtrado['conservacao'].isin(conservacao_sel)]
    if not "TODAS" in tipologia_sel:
        filtrado = filtrado[filtrado['tipologia_semfaz'].isin(tipologia_sel)]

    
    equip_filtrado = equipamentos[ (equipamentos['tipo'] == equipamento_sel) ]
        
    m = apiVis.visMultiMapa(width='90%', MAPA_ZOOM=15)
    
    #plot dos lotes
    m = apiVis.visMultiMapa(m, tipo='layer', 
                dado=filtrado,                         
                variavel='ocupacao',
                alias=f"Lotes com  Ocupação: {ocupacoes_sel}, área mínima: {area_slides} e estado de conservação: {conservacao_sel}" )   

    #filtro de dívida
    if divida_chk:
        divida = filtrado[~filtrado['divida_ipt'].isnull()]
        divida = divida[(divida['divida_ipt']!='s/ divida') & (divida['divida_ipt']!='s/divida') ]
        divida['geometria'] = divida['geometria'].centroid
        
        style_function = lambda x: {'fillColor': '#C0392B', "color": "#641E16"}
        m = apiVis.visMultiMapa(m, tipo='marcador', dado=divida, variavel='divida_ipt', alias=f"Dívida" )   

    m = apiVis.visMultiMapa(m, tipo='calor', dado=equip_filtrado, alias=equipamento_sel, variavel='tipo')     

    #camadas fixas
    style_function = lambda x: {'fillColor': '#B22222', "color": "#800000"}
    m = apiVis.visMultiMapa(m, tipo='layer', alias='Zona de Interesse Social', dado = zis, style=style_function)

    style_function = lambda x: {'fillColor': '#8E44AD', "color": "#8E44AD"}
    m = apiVis.visMultiMapa(m, tipo='layer', alias='Linhas de ônibus', dado = linhas, style=style_function, visible=True)

    style_function = lambda x: {'fillColor': '#FDFEFE', "color": "#52BE80"}
    m = apiVis.visMultiMapa(m, tipo='layer', alias='Limites Tombamento Estadual', dado = tomb_estadual, style=style_function, visible=False)

    style_function = lambda x: {'fillColor': '#FDFEFE', "color": "#CD6155"}
    m = apiVis.visMultiMapa(m, tipo='layer', alias='Limites Tombamento Federal', dado = tomb_federal, style=style_function, visible=False)

    if indicador_sel != 'Selecione':
        index = alias_var.index(indicador_sel)
        if index == 1:
            m = apiVis.visMultiMapa(m, tipo='choro', dado=hdx, variavel='population_2020', alias=alias_var[index]) 
        else:
            m = apiVis.visMultiMapa(m, tipo='choro', dado=domicilios, variavel=indicador_var[index], alias=alias_var[index]) 

    folium.LayerControl().add_to(m)
    output = st_folium(m, width=1000, height=600,     
            labels=[],       
            colors=['#440154', '#3B528B', '#21918C', '#5CC863', '#FDE725'])

def addGraficoEsp(ocupacoes_sel, conservacao_sel, area_slides, tipologia_sel, indicador_sel, equipamento_sel, divida_chk):
    #ação quando selecionar itens
    
    filtrado = lotes[(lotes['AREA_HTL']>=area_slides[0]) & (lotes['AREA_HTL']<=area_slides[1])]    
    if not "TODAS" in ocupacoes_sel:
        filtrado = filtrado[filtrado['ocupacao'].isin(ocupacoes_sel)]    
    if not "TODAS" in conservacao_sel:    
        filtrado = filtrado[filtrado['conservacao'].isin(conservacao_sel)]
    if not "TODAS" in tipologia_sel:
        filtrado = filtrado[filtrado['tipologia_semfaz'].isin(tipologia_sel)]    

    col1, col2 = st.columns(2)
    with col1:        
        #gráfico estado de ocupacao
        fig = px.pie(filtrado['ocupacao'].value_counts().T, values='ocupacao', names=filtrado['ocupacao'].unique(), 
                    title='Lotes x Tipo Ocupação')
        st.plotly_chart(fig, use_container_width=True)
    with col2: 
        #gráfico estado de conservação
        fig = px.pie(filtrado['conservacao'].value_counts().T, values='conservacao', names=filtrado['conservacao'].unique(), 
                    title='Lotes x Tipo Conservacao')
        st.plotly_chart(fig, use_container_width=True)

    #gráfico de área
    fig = px.histogram(filtrado['AREA_HTL'], x='AREA_HTL', nbins=20, title='Distribuição de Lotes por Área')
    st.plotly_chart(fig, use_container_width=True)

    #gráfico de tipologia
    fig = px.histogram(filtrado['tipologia_semfaz'], x='tipologia_semfaz', title='Distribuição de Lotes por Tipologia')
    st.plotly_chart(fig, use_container_width=True)


######MAIN######
    
#carrega todos os dados necessários
indicador_var = ['', 'População Total (densidade)', 'ibge_domicilio01_v018', 'ibge_domicilio01_v019', 'ibge_domicilio01_v019', 'ibge_domicilio01_v020', 'ibge_domicilio01_v021', 'ibge_domicilio01_v022']
alias_var = ['Selecione', 'População Total (densidade)', 'Esg. fossa séptica', 'Esg. fossa rudimentar', 'Esg. vala', 'Esg. rio, lago ou mar', 'Esg. outro']


#config
topicos = []
topicos.append('Lotes para serem usado para habitação')
topicos.append('Lotes para melhorias habitacionais')
topicos.append('Lotes para serem usados como equipamento público')

#config topico 0

lotes, zis, linhas, tomb_estadual, tomb_federal, hdx, equipamentos, domicilios = loadData()

valores = {
    "topico1":
        {
            "criterio": 'Critérios: Lots em desuso, maior que 200m2 sendo casas ou sobrados.',
            "ocupacao" : ['Edificação Subutilizada', 'Edificação sem uso'],
            "conservacao" : ['TODAS'],
            "area" :(200., 1000.0),
            "max" : 1000.0,
            "tipologia": ['sobrado', 'sobrado colonial', 'casa'],
            "divida" : False,
            "indicador": 0,
            "equipamento" : 1,
            "distancia":""
        },
    "topico2":
        {
            "criterio": 'Critérios: Lotes menores que 125m2',
            "ocupacao" : ['TODAS'],
            "conservacao" : ['TODAS'],
            "area" :(0.0, 125.0),
            "max" : 500.0,
            "tipologia": ['TODAS'],
            "divida" : False,
            "indicador": 0,
            "equipamento" : 1,
            "distancia":""
        },
    "topico3":
        {
            "criterio": 'Critérios: Lotes maiores que 250m2 até 400m de uma linha de ônibus',
            "ocupacao" : ['TODAS'],
            "conservacao" : ['TODAS'],
            "area" :(250.0, 10000.0),
            "max" : float(lotes['AREA_HTL'].max()),
            "tipologia": ['TODAS'],
            "divida" : True,
            "indicador": 0,
            "equipamento" : 1,
            "distancia":"800"
        }
}

main()