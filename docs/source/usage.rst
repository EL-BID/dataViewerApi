Como Usar
==========


Instalação
------------

Para a instalação do módulo, recomenda-se o uso de Python 3.8 ou superior.
Recomenda-se o uso de um gerenciador de envs.

.. code-block:: console
   
   $ pip install virtualenv
   $ virtualenv ENV_NOME
   (.ENV_NOME) $ source bin/activate

Em seguida, clonar o projeto no Github:

.. code-block:: console

   (.ENV_NOME) $ git clone https://github.com/EL-BID/dataViewerApi.git
   (.ENV_NOME) $ cd dataViewerApi

O arquivo requirements.txt possui todos as dependências necessárias e que devem ser 
instaladas para o funcionamento da PDC.

.. code-block:: console

   (.ENV_NOME) $ pip install -r requirements.txt


Configurando banco de dados: Postgres
--------------------------------------

Essa solução utiliza o banco de dados Postgres com a extensão Postgis. Após a instalação do mesmo, 
disponibilizamos um dump inicial da base de dados com dados no IBGE (feito com o PGAdmin). Para restaurar o dump, siga os passo:

 * Crie um database chamado "pdc" com owner "postgres" [se preferir crie com outro usuário, mas este deve ser owner do database]
 * Adicione a extensão espacial ao database. Abra um psql e digite:
 
 .. code-block:: sql  
 
   create extension postgis;
 
 * Abra o PGAdmin e selecione a opção "restore", selecionando o aruqivo do pdc.dump


Configurar Globals.py
-------------------------

Para o funcionamento de ambas PDCs, é necessário configurar os parâmetros de
conexão com o banco de dados.
As configurações estão no arquivo ``globals.py`` na pasta ``apiModulo``. 
As seguintes informações devem ser preenchidas:

.. code-block::
   
   HOST = 'Endereço.Ip.Do.Banco'
   USER = '<nome do usuário>'
   PASS = '<senha do usuário>'
   DATABASE = '<nome do database>'

Como usar PDC-API
---------------------

Este módulo pode ser usado diretamente no python ou no Jupyter Notebook.
Para tanto, recomenda-se adicionar o path do módulo ao ambiente de execução.

.. code-block:: 

   import os
   import sys

   sys.path.append(“/path/to/dir/apiModulo”)

   ...


Como executar PDC-Vis
----------------------

Após a configuração do módulo (veja :ref:`PDC-Visualização`), estando na pasta do projeto, executar:

.. code-block:: console

   (.ENV_NOME) $ streamlit run app.py
