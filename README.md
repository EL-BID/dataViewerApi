# Seja bem vindo à prova de conceito - SLZ - BID

A cidade de São Luís, com 1,1 milhão de habitantes, é a capital do estado do Maranhão. Está considerando uma segunda operação urbana com o Banco para migrar São Luís para um modelo de Cidade Inteligente, aproveitando soluções de dados para apoiar o planejamento urbano, projetos especiais e inovação da cidade.

As consultorias são totalmente interligadas uma vez que a primeira promove a coleta, análise e diagnóstico de dados abertos e restritos e a segunda consultoria deve orientar o processo de diagnóstico que deve incluir mecanismos de curadoria, qualidade, pré-processamento e limpeza de dados, para que estes possam ser adequadamente em provas de conceito a serem construídas como um dos objetivos da segunda consultoria. 

Como forma de subsidiar o processo de diagnóstico dos dados fornecidos pela prefeitura e coletados em base de dados abertos, esta prova de conceito tem como finalidade apresentar uma solução para auxílio neste processo, especificamente no cenário do Programa Vem pro Centro.

## Programa Vem pro Centro


O Programa Vem pro Centro busca, por meio de ações de reabilitação, restauro e construção em imóveis ociosos, produzir unidades habitacionais, equipamentos públicos e pequenos comércios, que garantam o adensamento populacional, a conservação integrada, a sustentabilidade e a inclusão socioeconômica da população e dos usuários da região central de São Luís.


## Instalação

> Para a instalação do módulo, recomenda-se o uso de Python 3.8 ou superior. Recomenda-se o uso de um gerenciador de envs.

```
   
   $ pip install virtualenv
   $ virtualenv ENV_NOME
   (.ENV_NOME) $ source bin/activate

```

Em seguida, clonar o projeto no Github:

```
   (.ENV_NOME) $ git clone https://github.com/gebraz/pdcbid2.git
   (.ENV_NOME) $ cd pdcbid2
```

O arquivo requirements.txt possui todos as dependências necessárias e que devem ser 
instaladas para o funcionamento da PDC.

```

   (.ENV_NOME) $ pip install -r requirements.txt
```

### Configurando banco de dados: Postgres


Essa solução utiliza o banco de dados Postgres com a extensão Postgis. Após a instalação do mesmo, 
disponibilizamos um dump inicial da base de dados com dados no IBGE (feito com o PGAdmin). Para restaurar o dump, siga os passo:

 - Crie um database chamado "pdc" com owner "postgres" [se preferir crie com outro usuário, mas este deve ser owner do database]
 - Adicione a extensão espacial ao database. Abra um psql e digite:
 
 ```
   create extension postgis;
 ```

- Abra o PGAdmin e selecione a opção "restore", selecionando o aruqivo do pdc.dump


### Configurar Globals.py

Para o funcionamento de ambas PDCs, é necessário configurar os parâmetros de
conexão com o banco de dados.
As configurações estão no arquivo ``globals.py`` na pasta ``apiModulo``. 
As seguintes informações devem ser preenchidas:

```   
   HOST = 'Endereço.Ip.Do.Banco'
   USER = '<nome do usuário>'
   PASS = '<senha do usuário>'
   DATABASE = '<nome do database>'
```

### Como usar PDC-API

Este módulo pode ser usado diretamente no python ou no Jupyter Notebook.
Para tanto, recomenda-se adicionar o path do módulo ao ambiente de execução.

```
   import os
   import sys

   sys.path.append(“/path/to/dir/apiModulo”)

   ...
```

### Como executar PDC-Vis


Após a configuração do módulo (veja :ref:`PDC-Visualização`), estando na pasta do projeto, executar:

```
   (.ENV_NOME) $ streamlit run app.py
```