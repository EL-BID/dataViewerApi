import pandas as pd
import geopandas as gpd

from sqlalchemy import create_engine, inspect
from geoalchemy2.types import Geometry, WKTElement
from os.path import exists
from shapely.geometry import MultiPolygon
from shapely import wkb
from pandas.core.frame import DataFrame
from numpy import int64, float64

from apiModulo.acesso import Acesso
from apiModulo.globals import * 

class ApiIns:
    """Classe com as especificações para criação de indicadores e inserção de informação        
    """
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
        self.engine = create_engine("postgresql://{0}:{1}@{2}:5432/{3}".format(user, p, host, database)) 
        # Verifica se a conexão foi concluída e cria um inspetor
        self.inspector = inspect(self.engine) 
        

    def inserirDados(self, data, nome_tabela, indice='', camada='', campo_camada='',delimiter = ";"):
        """
            Insere dados no banco de dados, baseado numa entrada e especificação de camada quando por o caso
           
            :param data: Path do arquivo(csv) ou objeto pandas                
            :param indice: Coluna a ser usada como chave primária. Quando não informado usa o index sequencial do pandas
            :param nome_tabela: Nome da tabela destino no banco de dados
            :param delimiter: Delimitador de coluna se carregar de csv. Padrão ';'
                
        """

        # CSV ou pandas?
        if isinstance(data, DataFrame):
            dataframe = data
        else:
            # Carregamento e processamento do csv ou shp
            if not exists(data):
                raise FileNotFoundError(f"Arquivo {data} não existe")

            dataframe = pd.read_csv(data, delimiter=delimiter)
        
        # Checando se a coluna_indice existe
        #if not indice:
        #    raise SyntaxError(f"O índice não pode estar vazio")

        # Todas as colunas são minúsculas
        for column in dataframe.columns:
            dataframe = dataframe.rename(columns={column : column.lower()})

        # Checa se a coluna_indice(pk) escolhida existe
        indice = indice.lower()
        if indice in dataframe.columns :
            dataframe = dataframe.set_index(indice)
        elif indice != "index":
            indice = 'id_' + nome_tabela
            dataframe.index.names = [indice]            
            #raise ValueError(f"O índice {indice} não existe no dataframe. As colunas disponíveis são {dataframe.columns}")

        # Checando nome da tabela
        if not nome_tabela:
            raise SyntaxError("O nome da tabela não pode estar vazio")

        # Procura coluna vazia e tipo
        for coluna in dataframe.columns:
            # Procura por linhas vazias
            for linha in dataframe[coluna]:
                if pd.isna(linha):
                    print(f"AVISO: Linha vazia na coluna '{coluna}': {linha}")
                    break

            # Procura o tipo do primeiro item na coluna
            if isinstance(dataframe[coluna].iloc[0], int64) or isinstance(dataframe[coluna].iloc[0], int): # inteiro
                tipo = int
            elif isinstance(dataframe[coluna].iloc[0], float64) or isinstance(dataframe[coluna].iloc[0], float): # Float
                tipo = float
            elif dataframe[coluna].iloc[0].isdigit(): # Str com int dentro
                tipo = int
            else:
                tipo = str

            # Procura por itens inválidos
            for linha in dataframe[coluna]:
                try:
                    if   tipo == int and (isinstance(linha, int64) or isinstance(linha, int) or linha.isdigit()):
                        continue
                    elif tipo == float and (isinstance(linha, float64) or isinstance(linha, float) or linha.isdigit()):
                        continue
                    elif tipo == str and not linha.isdigit():
                        continue
                    else:
                        print(f"AVISO: Tipo inválido encontrado na coluna {coluna}: Esperava {tipo} mas encontrou {type(linha)}({linha}). Substituindo por 0")
                        indexlist = dataframe.loc[dataframe[coluna] == linha][coluna]
                        for index in indexlist.index.values:
                            dataframe.at[index, coluna] = 0
                except:
                    print("AVISO: acesso de tipos divergentes")

        
        # Envia para o db
        dataframe.to_sql(nome_tabela, self.engine)

        # Configura a pk
        self.engine.execute(f'ALTER TABLE public.{nome_tabela} ADD PRIMARY KEY ({indice});')

        #TODO: configura fk. Ajustar para pegar erro quando não houver a fk
        #if camada != '' and campo_camada != '':
        #    #ALTER TABLE public.atlas_vis_udh ADD CONSTRAINT atlas_vis_udh_fk FOREIGN KEY (udh) REFERENCES public.ivs_ipea_sao_luis(cod_camada);
        #    sql="ALTER TABLE public.{0} ADD CONSTRAINT {0}_fk FOREIGN KEY ({1}) REFERENCES public.{2}(cod_camada)".format(nome_tabela, campo_camada, camada)
        #    cur = self.connection.cursor()
        #    cur.execute(sql)  
        #    self.connection.commit()

        print(f"{nome_tabela}: Foram importadas {len(dataframe.columns)} colunas e {len(dataframe)} linhas") 

    def inserirCamada(self, dado, tabela, tipo='MULTIPOLYGON', campo_chave=None, nome='', descricao=''):
        """
            Insere dados geografico no banco de dados, geopandas ou string para o shapefile
           
            :param dado: Path do arquivo(csv) ou objeto geopandas                            
            :param tabela: Nome da tabela a ser criada na base de dados
            :param tipo: Tipo de dado geo, MULTIPOLYGON, POINT, LINE
            :param campo_chave: nome da coluna no geopandas que representa a chave dos dados
            :param nome: nome dado a camada, para referência nos Indicadores
            :param delimiter: Delimitador de coluna se carregar de csv. Padrão ';'
                
        """       
        
        gdf = None
        if type(dado) is str:        
            gdf = gpd.read_file(dado)
        else:
            gdf = dado

        #TODO: colocar numa transação para evitar erros
        #criando fk para camada
        sql = """
                insert into camadas(nome, descricao, tipo, tabela)
                values (\'{0}\', \'{1}\', \'{2}\', \'{3}\') 
                RETURNING id_camada
              """.format(nome, descricao, tipo, tabela)
        cur = self.connection.cursor()
        cur.execute(sql)        
        fk_camada = cur.fetchone()[0]
        self.connection.commit()
        cur.close()

        gdf["fk_camada"] = fk_camada

        #TODO: requer geoalchemy2
        if campo_chave is not None:
            gdf.rename(
                columns={campo_chave : "cod_camada"},
                inplace=True
            )

        gdf = gdf.rename_geometry('geometria')
        gdf.to_postgis(name=tabela, index=True, con=self.engine)  
                        
        self._ajusta_chaves(tabela, campo_chave)
        

    def _ajusta_chaves(self, tabela, campo_chave):        
        cur = self.connection.cursor()

        if campo_chave is None:            
            sql = "ALTER TABLE public.{0} RENAME COLUMN \"index\" TO cod_camada".format(tabela)
            cur.execute(sql) 
            self.connection.commit()

        sql="ALTER TABLE public.{0} ADD CONSTRAINT {0}_pk PRIMARY KEY (cod_camada)".format(tabela)
        cur.execute(sql)  
        self.connection.commit()

        sql="ALTER TABLE public.{0} ADD CONSTRAINT {0}_fk FOREIGN KEY (fk_camada) REFERENCES public.camadas(id_camada)".format(tabela)
        cur.execute(sql)  
        self.connection.commit()

        cur.close()

    def inserirIndicador(self, tema, assunto, tabela, definicao, descricao, fonte, ano, camada = 1, id_indicador = None):
        """
            Inserir indicador no banco de dados
           
            :param tema: Tema do indicador(ex: Responsável, Domicílio, Pessoa)
            :param assunto: Assuntos do indicador, separados por vírgula(ex:Cor ou Raça, idade e gênero)
            :param tabela: Tabela que o indicador está apontando
            :param definicao: Coluna da tabela que o indicador está apontando
            :param descricao: Descrição do indicador que aparece no mapa
            :param fonte: De onde o indicador foi retirado(ex: IBGE Censo Demográfico 2010)
            :param ano: Ano da fonte do indicador
            :param camada: Número da camada que o indicador está apontando. Camada 1 por padrão
            :param id_indicador: Código do ID do indicador. Padrão None.
                
        """          

        # Parse dos argumentos
        if not isinstance(ano, int) or not isinstance(camada, int):
            raise ValueError("Erro nos parâmetros da função")

        cur = self.connection.cursor()

        # Procura se o indicador já existe na tabela
        sql = f"""select * from public.indicadores WHERE 
            tema = '{tema}' and
            assunto = '{assunto}' and
            tabela = '{tabela}' and 
            definicao = '{definicao}' and 
            fonte = '{fonte}' and
            ano = '{ano}'"""
        
        cur.execute(sql)
        resultado = cur.fetchone()

        if resultado:
            cur.close()
            raise ValueError("O indicador já existe na tabela")
        
        # Se o usuário não tiver passado um id, bote o último da tabela + 1
        if not id_indicador:
            sql = "SELECT MAX(id_indicador) FROM public.indicadores"
            cur.execute(sql)
            id_indicador = cur.fetchone()[0] + 1
        
        # Insere na db
        sql = f"""
                insert into indicadores(id_indicador, tema, assunto, tabela, definicao, descricao, fonte, ano, fk_camada)
                values (\'{id_indicador}\', \'{tema}\', \'{assunto}\', \'{tabela}\', \'{definicao}\', \'{descricao}\', \'{fonte}\', \'{ano}\', \'{camada}\' ) 
              """

        cur.execute(sql)
        self.connection.commit()
        cur.close()

    def removerIndicador(self, id):
        """
            Remove indicador no banco de dados
                    
            :param id: Código do ID do indicador.
                        
        """
            
        # Parse dos argumentos
        if not isinstance(id, int):
            raise ValueError("id deve ser um inteiro")

        cur = self.connection.cursor()

        # Procura se o indicador já existe na tabela
        sql = f"""select * from public.indicadores WHERE 
            id_indicador = {id}"""

        cur.execute(sql)
        resultado = cur.fetchone()

        if not resultado:
            cur.close()
            raise ValueError("O indicador não existe na tabela")

        sql = f"""delete from public.indicadores where 
            id_indicador = {id}"""

        cur.execute(sql)
        self.connection.commit()
        cur.close()
