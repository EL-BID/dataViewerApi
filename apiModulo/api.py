'''
Wrapper genérico para todos os imports
e para funções utilitárias
'''

from apiModulo.globals import *
from apiModulo.api_insercao import ApiIns
from apiModulo.api_consulta import ApiConsulta
from apiModulo.api_visualizacao import ApiVis

#imports genéricos
import warnings
warnings.filterwarnings('ignore')
import geopandas as gpd
import pandas as pd
import fiona

#acesso globais
vis = ApiVis(host=HOST, user=USER, database=DATABASE, p=PASS)
cons = ApiConsulta(host=HOST, user=USER, database=DATABASE, p=PASS)
ins = ApiIns(host=HOST, user=USER, database=DATABASE, p=PASS)

#CONSULTA
def lstIndicador(filtro='', tema='', assunto=''):
    return cons.lstIndicador(filtro=filtro, tema=tema, assunto=assunto)

def lstTema(filtro=''):
    return cons.lstTema(filtro=filtro)

def lstCamadas(filtro=''):
    return cons.lstCamadas(filtro=filtro) 

def obterMetadados(tema='', indexes=''):
    return cons.obterMetadados(tema=tema, indexes=indexes)

def obterTema(tema='', indexes=''):
    return cons.obterTema(tema=tema, indexes=indexes)

def obterTemaSoma(tema='', indexes=''):
    return cons.obterTemaSoma(tema=tema, indexes=indexes)

def limparDados(dados):
    return cons.limparDados(dados=dados)

def obterIndicador(index=-1, tabela='', definicao='', ):
    return cons.obterIndicador(index=index, tabela=tabela, definicao=definicao)

def obterTabela(nome_tabela=''):
    return cons.obterTabela(nome_tabela=nome_tabela)

def obterCamada(nome_tabela='', simples=False, campo='', filtro=''):
    return cons.obterCamada(nome_tabela=nome_tabela, simples=simples, campo=campo, filtro=filtro)

#INSERCAO
def inserirDados(data, nome_tabela, indice='', camada='', campo_camada='',delimiter = ";"):
    ins.inserirDados(data, nome_tabela, indice=indice,camada =camada, campo_camada=campo_camada, delimiter = delimiter)

def inserirCamada(dado, tabela, tipo='MULTIPOLYGON', campo_chave=None, nome='', descricao=''):
    ins.inserirCamada(dado, tabela, tipo=tipo, campo_chave=campo_chave, nome=nome, descricao=descricao)

def inserirIndicador(tema, assunto, tabela, definicao, descricao, fonte, ano, camada = 1, id_indicador = None):
    ins.inserirIndicador(tema, assunto, tabela, definicao, descricao, fonte, ano, camada = camada, id_indicador = id_indicador)

def removerIndicador(id):
    ins.removerIndicador(id)

#VISUALIZACAO
def visMapaIndicador(indicador, height=1200, width=600, MAPA_ZOOM=14.5):
    return vis.visMapaIndicador(indicador=indicador, height=height, width=width, MAPA_ZOOM=MAPA_ZOOM)

def visMapaDados(df, metadados, height=1200, width=600, MAPA_ZOOM=14.5):
    return vis.visMapaDados(df, metadados, height=height, width=width, MAPA_ZOOM=MAPA_ZOOM)

def visMultiMapa(map=None, tipo=None, dado=None,  variavel=None, alias=None, height=1200, width=600, MAPA_ZOOM=14.5, style=None):
    return vis.visMultiMapa(map=map, tipo=tipo, dado=dado, variavel=variavel, alias=alias, height=height, width=width, MAPA_ZOOM=MAPA_ZOOM, style=style)

def visMapaGJson(gdf, variavel, descricao, height=1200, width=600, MAPA_ZOOM=14.5):
    return vis.visMapaGJson(gdf, variavel=variavel, descricao=descricao, height=height, width=width, MAPA_ZOOM=MAPA_ZOOM)

def visMapaSemIndicador(dados=None, coluna_geom=None):
    return vis.visMapaSemIndicador(dados=dados, coluna_geom=coluna_geom)

#Utils GEOPandas
def lerArquivo(arquivo):
    return gpd.read_file(arquivo)

def juncaoEspacial(A, B, tipo='inner', predicado='contains'):
    return A.sjoin(B, how=tipo, predicate=predicado)

def salvar(gdf, arquivo):
    gdf.to_file(arquivo)

def limparDados(dados):
    """
    Remover caracteres em dados que deveriam ser numéricos
    
    :param dados: dataframe/geodataframe com os dados        
    :return: Dados pós-processados
    :rtype: geopandas
            
    """ 
    df = dados
    df = df.replace('X', '0')
    df = df.replace('XX', '0')
    for val in df.columns:
        if val != 'index' and val != 'geometria':
            df[val] = df[val].astype('float')
    return df


def somarColunas(dados):
    lst= list(dados)
    lst.remove('geometria')
    lst.remove('index')

    dados['soma'] = dados[lst].sum(axis=1)
    dados.drop(lst, axis=1, inplace=True)
    return dados