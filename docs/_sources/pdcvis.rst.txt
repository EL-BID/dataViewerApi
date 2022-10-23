PDC-Visualização
=================

Esta seção apresenta as funcionalidades construídas para o módulo de Visualização 
construída nesse PDC. Esse módulo faz uso da API para a construção de visualizações de mapa e gráficos 
via Streamlit.

Definição do ``config.yaml``
--------------------------------

Para o funcionamento do módulo, é necessário configura o arquivo ``config.yaml``.
Esse arquivo é organizado em blocos explicados a seguir:

.. note::
    O arquivo ``config.yaml`` se encontra na raiz do projeto


* Bloco base, ``app`` deve sempre estar no início do arquivo.

* Bloco ``area_shape_basico``: representa camadas do mapa que poderão ser selecionados para apresentação
    * info: nome indicativo para a camada
    * tabela: origem dos dados na base de dados
    * tipo: tipo de geometria dos dados

Exemplo: 

.. code-block:: yaml

    - area_shape_basico: 
          info: 'Limites São Luís'
          tabela: limites_sao_luis
          tipo: poligono
    
* Bloco ``camada_padrao``: representa informações a serem adicionadas como filtros nos mapas    
    * tipo: tipo de geometria dos dados
    * info: nome indicativo para a camada
    * tabela: origem dos dados na base de dados
    * campos: lista de campos separada por ``#`` que serão consumidos da tabela
    * descricao: nome formatado dos campos informados, separados por ``#``
    * popup: campos a serem inseridos no popup, separados por ``#``
    * desc_popup: nome formatado dos campos informados no popup, separados por ``#``

.. code-block::  yaml

    - camada_padrao:
          tipo: ponto
          info: 'Equipamentos Público'
          tabela: equipamento_publico
          campos: educacao#saude#seguranca#cultural#assistencia_social
          descricao: 'Educação#Saúde#Segurança#Cultural#Assistência Social'
          popup: tipo#name
          desc_popup: 'Tipo#Nome'

Os conteúdos (ou páginas) estão organizados em ``topico``. Cada um pode possuir ``mapa`` e ``grafico``
de acordo com a necessidade de visualização.

Um tópico é definido por um ``título`` e uma ``descrição``. O conteúdo dentro é feito pelas 
declarações de mapas e gráficos.

.. code-block:: yaml

    - topico: 
          titulo: 'Restauro para Habitação'          
          descricao: '' 
          
          mapa1:
          grafico1: 
          mapa2:
          grafico2: 

.. note::
    Você pode inserir quantos mapas forem necessários, mas precisam ser numerados
    em seguência: 1, 2, 3     

Um mapa é definido por um título, uma descrição, e:
    * tabela: tabela com os dados
    * camada: referência espacial na base
    * variavel: colunas da tabela, separadas por ``#``
    * alias: nome formatado das colunas, separado por ``#``
    * camada_extra: referência a uma camada padrão declarada anteriormente
    * camada_interna: referência a uma camada padrão declarada anteriomente
    * camada_base: referência a uma camada padrão declarada anteriomente

.. code-block:: yaml

    mapa1:
        titulo: '**Distribuição de Mulheres por Setor censitario**'
        descricao: ''
        tabela: pdc_bid_ibge
        camada: setor_censitario                
        variavel: 'mulheres_14_anos_ou_mais#mulheres_resp_pelo_dom'
        alias: 'Mulheres (14 anos ou mais):#Mulheres responsáveis pelo domicílio'                                 
        camada_extra: 'lotes_por_ponto' 
        camada_interna: tombamento   
        camada_base: anel_viario   

Um mapa é definido por um título, uma descrição, e:
    * tabela: tabela com os dados
    * x: lista de colunas utilizadas das tabelas
    * x_alias: nomes formatados das colunas
    * y: referencial do valor apresentado no eixo y
    * tipo: barra_vertical - barra_horizontal - pizza - scatter - linha

.. code-block:: yaml

    grafico1:
        titulo: '**Distribuição da população**'
        descricao: ''         
        tabela: pdc_bid_ibge
        x:
            - mulheres_14_anos_ou_mais
            - mulher_responsavel
            - idosos_65_anos_ou_mais
            - crianca_13_ou_menos
        x_alias:
            - Mulheres de 14 anos ou mais
            - Mulher Responsável
            - Idosos de 65 anos ou mais
            - Crianças de 13 anos ou menos
        y:
            - Quantidade
        tipo: barra_vertical
                
Exemplo do arquivo ``config.yaml``
------------------------------------

.. code-block:: yaml
    
    app:    
     - area_shape_basico: 
          info: 'Limites São Luís'
          tabela: limites_sao_luis
          tipo: poligono
     - area_shape_basico: 
          info: 'Anél Viário'
          tabela: anel_viario
          tipo: poligono
     - camada_padrao:
          tipo: ponto
          info: 'Informações de lotes'
          tabela: lotes_por_ponto
          campos: finais_prior#finais_divida#finais_estado_de_
          descricao: 'Prioridade#Divida#Estado de Conservação'
          popup: finais_de_uso#finais_prior#finais_divida#finais_estado_de_
          desc_popup: 'Uso#Prioridade#Divida#Estado de Conservação'
     - camada_padrao:
          tipo: ponto
          info: 'Equipamentos Público'
          tabela: equipamento_publico
          campos: educacao#saude#seguranca#cultural#assistencia_social
          descricao: 'Educação#Saúde#Segurança#Cultural#Assistência Social'
          popup: tipo#name
          desc_popup: 'Tipo#Nome'
     - camada_padrao:
          tipo: poligono
          info: 'Tombamento'
          tabela: tombamento
          campos: name
          descricao: 'Nome'
          popup: name
          desc_popup: 'Nome'  
     - topico: 
          titulo: 'Restauro para Habitação'          
          descricao: ''          
          mapa1:
               titulo: '**Distribuição de Mulheres por Setor censitario**'
               tabela: pdc_bid_ibge
               camada: setor_censitario                
               variavel: 'mulheres_14_anos_ou_mais#mulheres_resp_pelo_dom'
               alias: 'Mulheres (14 anos ou mais):#Mulheres responsáveis pelo domicílio'  
               descricao: ''                       
               camada_extra: 'lotes_por_ponto' 
               camada_interna: tombamento   
               camada_base: anel_viario                     
          grafico1:
               titulo: '**Distribuição da população**'
               tabela: pdc_bid_ibge
               x:
                    - mulheres_14_anos_ou_mais
                    - mulher_responsavel
                    - idosos_65_anos_ou_mais
                    - crianca_13_ou_menos
               x_alias:
                    - Mulheres de 14 anos ou mais
                    - Mulher Responsável
                    - Idosos de 65 anos ou mais
                    - Crianças de 13 anos ou menos
               y:
                    - Quantidade
               tipo: barra_vertical
               descricao: ''
          mapa2:
               titulo: '**Lotes**'
               tabela: pdc_bid_lotes
               camada: lotes                
               variavel: 'tipologia_finais#conservacao_finais#uso_finais#prioridade_finais#divida'
               alias: 'Tipologia#Estado de Conservação#Uso#Prioridade#Divida'  
               descricao: ''
               camada_extra: 'equipamento_publico'   
               camada_interna: '' 
               camada_base: 'anel_viario'                                                           
     - topico:  
          titulo: 'Habitações Precárias'          
          descricao: ''          
          mapa1:
               titulo: '**Distribruição de banheiros nas habitações**'
               tabela: pdc_bid_ibge
               camada: setor_censitario                
               variavel: 'dom_sem_banheiro_nem_sanitario#dom_sem_banheiro#dom_com_1_banheiro#dom_com_2_banheiro#dom_com_3_banheiro'
               alias: 'Dom. sem banheiro nem sanitário#Dom. sem banheiro#Dom. com até 1 banheiro#Dom. com até 2 banheiros#Dom. com até 3 banheiros'  
               descricao: ''     
               camada_extra: 'equipamento_publico'
               camada_interna: ''    
               camada_base: 'anel_viario'                    
          grafico1:
               titulo: '**Distribuição da população**'
               tabela: pdc_bid_ibge
               x:
                    - mulheres_14_anos_ou_mais
                    - mulher_responsavel
                    - idosos_65_anos_ou_mais
                    - crianca_13_ou_menos
               x_alias:
                    - Mulheres de 14 anos ou mais
                    - Mulher Responsável
                    - Idosos de 65 anos ou mais
                    - Crianças de 13 anos ou menos
               y:
                    - Quantidade
               tipo: barra_vertical
               descricao: ''          
          grafico2:
               titulo: '**Distribuição de Esgoto**'
               tabela: pdc_bid_ibge
               x:
                    - dom_banh_excl_rede_geral
                    - dom_banh_excl_fossa_septica
                    - dom_banh_excl_fossa_rud
                    - dom_banh_excl_vala
                    - dom_banh_excl_rio_lago_mar
                    - dom_banh_excl_outro
               x_alias:
                    - Rede Geral
                    - Fossa Séptica
                    - Fossa Rudimentar
                    - Vala
                    - Rio, Lago ou Mar
                    - Outro
               y:
                    - Quantidade
               tipo: pizza
               descricao: ''
          grafico3:
               titulo: '**Distribuição de banheiros**'
               tabela: pdc_bid_ibge
               x:
                    - dom_sem_banheiro_nem_sanitario
                    - dom_com_1_banheiro
                    - dom_com_2_banheiro
                    - dom_com_3_banheiro
               x_alias:
                    - Dom. sem banheiro nem sanitário
                    - Dom. com 1 banheiro
                    - Dom. com 2 banheiros
                    - Dom. com 3 banheiros
               y:
                    - Quantidade
               tipo: barra_vertical
               descricao: ''
          grafico4:
               titulo: '**Distribuição de Água**'
               tabela: pdc_bid_ibge
               x:
                    - dom_abastecimento_agua_rede_geral
                    - dom_abastecimento_agua_poco_nascente
                    - dom_abastecimento_agua_chuva_cisterna
                    - dom_abastecimento_agua_outra
               x_alias:
                    - Rede Geral
                    - Poço ou Nascente
                    - Chuva ou Cisterna
                    - Outro
               y:
                    - Quantidade
               tipo: barra_horizontal
               descricao: ''
          grafico5:
               titulo: '**Distribuição de Lixo**'
               tabela: pdc_bid_ibge
               x:
                    - dom_part_lixo_coletado_servico
                    - dom_part_lixo_coletado_cacamba_servico
                    - dom_part_lixo_queimado_propriedade
                    - dom_part_lixo_enterrado_propriedade
                    - dom_part_lixo_terreno_baldio
                    - dom_part_lixo_rio_lago_mar
                    - dom_part_lixo_outro
               x_alias:
                    - Serviço de Coleta
                    - Caçamba 
                    - Lixo Queimado
                    - Enterrado na Propriedade
                    - Terreno Baldio
                    - Rio, Lago ou Mar
                    - Outro
               y:   
                    - Quantidade
               tipo: pizza
               descricao: ''
     - topico: 
          titulo: 'Equipamentos Públicos'          
          descricao: ''        
     - topico: 
          titulo: 'Imóveis Ociosos'          
          descricao: ''     
     - topico: 
          titulo: 'Regularização Fundiária'          
          descricao: ''           

Implementação 
----------------   

.. automodule:: app
    :members:

    .. autosummary::
        app.loadData
        app.addMapMarcador
        app.addMapHeat
        app.addMapVoronoi
        app.addMap
        app.addGrafico
    
   