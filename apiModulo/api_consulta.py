from operator import index
import pandas as pd
import pandas.io.sql as sqlio
import geopandas as gpd
import pyproj

from apiModulo.acesso import Acesso
from apiModulo.globals import * 

class ApiConsulta:
    """
    Classe com as especificações de acesso e manipulação dos dados          
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
    
    """
    Grupo de funçoes para consulta
    """
    def lstIndicador(self, filtro='', tema='', assunto=''):
        """
        Obtem os Indicadores presentes na base, filtrando por qualquer termo, tema ou assunto

        :param filtro: campo de texto que deve ser utilizado como filtro nos campos de tema, assunto e descrição
        :param tema: filtra especificamente por tema
        :param assunto: filtra especificamente por assunto
        :return: Resultados organizados como tema, assunto, descrição, fonte, tabela, definição, tabela
        :rtype: dataframe - pandas
            
        """
        
        sql = """select i.id_indicador as index, 
                        i.tema, 
                        i.assunto, 
                        i.descricao, 
                        i.fonte, 
                        i.ano, 
                        i.tabela, 
                        i.definicao, 
                        c.tabela 
                from indicadores i, camadas c 
                where i.fk_camada = c.id_camada """
        if tema != '': 
            sql += 'and '
            sql += '    lower(i.tema) like \'%{0}%\''.format(tema.lower())
            sql += ' '
        elif assunto != '':
            sql += 'and '
            sql += ' lower(i.assunto) like \'%{0}%\''.format(assunto.lower())
            sql += ' '
        elif filtro != '':
            sql += 'and ( '
            sql += '    lower(i.tema) like \'%{0}%\''.format(filtro.lower())
            sql += ' or lower(i.assunto) like \'%{0}%\''.format(filtro.lower())
            sql += ' or lower(i.descricao) like \'%{0}%\''.format(filtro.lower())
            sql += ') '
                  
        #print(sql)
        df = sqlio.read_sql_query(sql, self.connection)
        df.index = df['index']    
        #print(sql)
        return df

    
    def lstTema(self, filtro=''):
        """
        Obtem lista de temas cadastrados em Indicadores

        :param filtro: filtro sobre o campo tema
        :return: Lista de temas presentes na base
        :rtype: dataframe - pandas
            
        """
        sql = """select distinct tema from indicadores """
        if filtro != '':
            sql += 'where '
            sql += '    lower(tema) like \'%{0}%\''.format(filtro.lower())
            sql += ''
                  
        df = sqlio.read_sql_query(sql, self.connection)
        return df

    def lstCamadas(self, filtro=''):
        """
        Obtem lista das camadas presentes na Base

        :param filtro: filtro de nome
        :return: Lista de camadas presentes na base
        :rtype: dataframe - pandas
            
        """
        sql = """select id_camada, nome, tabela from camadas """
        if filtro != '':
            sql += 'where '
            sql += '    lower(nome) like \'%{0}%\''.format(filtro.lower())
            sql += ''
                  
        df = sqlio.read_sql_query(sql, self.connection)
        return df    

    def obterMetadados(self, tema='', indexes=''):
        """
        Obtem as descrições dos indicadores, contendo definição e camada

        :param filtro: filtro de nome
        :param indexes: lista de ids de Indicadores no formato de string, Ex. [1, 2, 3, 4]
        :return: Dicionário com o metadados da base
        :rtype: dict
            
        """
        filtro_ids = ''
        if indexes != '':
            if tema == '':
                filtro_ids = ' where id_indicador in({0})'.format(indexes)
            else:
                filtro_ids = ' where tema = \'{0}\' and id_indicador in({1})'.format(tema, indexes)
        else: 
            filtro_ids = """ where tema like \'%{0}%\'
                             or descricao like \'%{0}%\'
                             or assunto like \'%{0}%\'""".format(tema)

        sql = """
            select i.tabela as tabela,
            i.tabela || '_' || i.definicao as coluna,
            (select tabela from camadas where id_camada = i.fk_camada) as camada,
            i.descricao
            from indicadores i 
            {0}            
            order by i.tabela, i.definicao 
            """.format(filtro_ids)    
        

        #obtem indicadores
        cur = self.connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()    
        metadados = []

        for row in result:
            #forma metadados das variáveis
            
            metadados.append({
                'tabela':row[0],
                'variável':row[1],
                'descrição':row[3],
                'suporte espacial':row[2]
            })
            
        cur.close()
        return metadados        

    def obterTema(self, tema='', indexes=''):
        """
        Obtem os dados na forma de um pandas/geopandas. Os Indicadores precisam compartilhar o mesmo suporte espacial
        
        :param tema: utilizado para filtrar os campos de tema, assunto e descrição
        :param indexes: lista de ids de Indicadores no formato de string, Ex. [1, 2, 3, 4]        
        :return: Dados obtidos no banco. Se houver campo espacial, geopandas. Se não, um pandas. Os metadados são também devolvidos.
        :rtype: geopandas, dict
              
        """               

        filtro_ids = ''
        if indexes != '':
            if tema == '':
                filtro_ids = ' where id_indicador in ({0})'.format(indexes)
            else:
                filtro_ids = ' where tema = \'{0}\' and id_indicador in({1})'.format(tema, indexes)
        else: 
            filtro_ids = """ where tema like \'%{0}%\'
                             or descricao like \'%{0}%\'
                             or assunto like \'%{0}%\'""".format(tema)

        sql = """select i.tabela as tabela,
	             string_agg(i.tabela || '.' || i.definicao || ' as ' || i.tabela || '_' || i.definicao, ',') as coluna,
	             (select tabela from camadas where id_camada = i.fk_camada) as camada
                 from indicadores i 
                 {0}
                 group by i.tabela, i.fk_camada                  
            """.format(filtro_ids)            

        #obtem indicadores
        cur = self.connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()        

        df = None #vai guardar o resultado final

        #obtem dados    
        if result is not None:
            #para cada linha, tem que montar o pandas de resposta baseado no sql
                        
            for row in result:
                #para cada tabela
                tabela = row[0]
                colunas =  '{0}.cod_camada as index, {1} '.format(tabela, row[1])
                camada = row[2]
                where  = ''

                #se tiver campo espacial
                
                if (camada is not None):
                    colunas += ', geo.geometria '
                    where  = ' where {0}.cod_camada = geo.cod_camada'.format(tabela)
                    tabela += ', {0} geo '.format(camada)                                        
                
                sql = """
                        select {0}
                        from {1}                                                    
                        {2}
                       """.format (colunas, tabela, where)                
                
                if (camada is not None):
                    temp = gpd.GeoDataFrame.from_postgis(sql, self.connection, geom_col='geometria')                    
                else:                            
                    temp = sqlio.read_sql_query(sql, self.connection) 
                    
                if df is not None:
                    df = df.merge(temp, on=['index', 'geometria'])
                else: 
                    df = temp
        
        metadados = self.obterMetadados(tema=tema, indexes=indexes)

        cur.close()
        return df, metadados

    def obterTemaSoma(self, tema='', indexes=''):
        """
        Obtém os dados dos indicadores e soma seus resultados.
        Garanta que todos os indicadores são do tipo numérico.
        
        :param tema: utilizado para filtrar os campos de tema, assunto e descrição
        :param indexes: lista de ids de Indicadores no formato de string, Ex. [1, 2, 3, 4]
        :return: Dados obtidos no banco. Se houver campo espacial, geopandas. Se não, um pandas. Os metadados são também devolvidos.
        :rtype: geopandas, dict
              
        """            
        
        df, metadados = self.obterTema(tema, indexes)
        lst= list(df)
        lst.remove('geometria')
        novo=df[lst].sum(axis=1)
        novo['geometria'] = df['geometria']
        
        return novo, metadados        
  
    def limparDados(self, dados):
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

    def obterIndicador(self, index=-1, tabela='', definicao='', ):
        """
        Obtém dados de um Indicador
        
        :param index: ID do indicador na base
        :param tabela: Nome da tabela com dados no banco (presente no Indicador)
        :param definicao: Nome da coluna com dados no banco (presente no Indicador)
        :return: Dados
        :rtype: pandas/geopandas
              
        """      
        sql = """select string_agg(i.id_indicador::text, ',')               
                 from indicadores i where  """
        indicador = []
        if index >= 0:
            sql += ' i.id_indicador={0}'.format(index)            
        elif tabela != '' and definicao != '':
            sql += ' i.tabela=\'{0}\' and i.definicao=\'{1}\''.format(tabela, definicao)
        else:
            return
        
        #obtem indicador
        cur = self.connection.cursor()
        cur.execute(sql)
        indicador = cur.fetchone()
                
        return self.obterTema(indexes=indicador[0])

    def obterTabela(self, nome_tabela=''):
        """
        Obtém todos os dados de uma tabela. 
        Não deve ser usado para camadas.
        
        :param nome_tabela: nome da tabela no banco
        :return: Dados, na forma de pandas
        :rtype: pandas
              
        """ 
        sql = f"""select * from {nome_tabela}"""
        
        # obtem tabela
        dataframe = pd.read_sql(sql, self.connection)
        return dataframe

    def obterCamada(self, nome_tabela='', simples=False, campo='', filtro=''):
        """
        Obtém todos os dados de uma tabela do tipo camada (tem suporte espacial). 
        Não deve ser usado para dados de indicadores.
        
        :param nome_tabela: nome da tabela no banco
        :param simples: quando True retorna apenas cod_camada e geometria
        :param campo: quando filtro != '', especifica qual campo adicional da tabela deve ser obtido
        :param filtro: usado na cláusula where
        :return: Dados, na forma de geopandas
        :rtype: geopandas
              
        """ 
        if simples:
            sql = f"""select cod_camada, geometria from {nome_tabela}"""    
        elif filtro == '':
            sql = f"""select * from {nome_tabela}"""
        else:
            sql = f"""select cod_camada, {campo}, geometria from {nome_tabela}
                      where {campo} {filtro}
                    """        
        # obtem camada
        dataframe = gpd.GeoDataFrame.from_postgis(sql, self.connection, geom_col='geometria')
        dataframe.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
        dataframe = dataframe.set_index('cod_camada')
        return dataframe        

