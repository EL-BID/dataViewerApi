
<h1 align="center">VemProCentro - Data Viewer</h1>
<p align="center"> Logo e imagem ou gif da interface principal da ferramenta</p>
<p align="center"><img src="https://www.webdevelopersnotes.com/wp-content/uploads/create-a-simple-home-page.png"/></p>

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=EL-BID_guia-de-publicacion&metric=alert_status)](https://sonarcloud.io/dashboard?id=EL-BID_guia-de-publicacion)

*Esta ferramenta digital faz parte do catálogo de ferramentas do **Banco Interamericano de Desenvolvimento**. Você pode saber mais sobre a iniciativa do BID em [code.iadb.org](https://code.iadb.org)*


## Tabela de conteúdos:
---
- [Descrição](#Descrição)
- [Guia do usuário](#Guia-do-usuário)
- [Guia de instalação](#Guia-de-instalação)
- [Autor/es](#Autor(es))
- [Licença](#Licença)
- [Isenção de responsabilidade - Somente BID](#Isenção-de-responsabilidade)

## Descrição e contexto
---

A cidade de São Luís, com 1,1 milhão de habitantes, é a capital do estado do Maranhão. Este repositório apresenta a implementação de PDC com foco de migrar São Luís para um modelo de Cidade Inteligente, aproveitando soluções de dados para apoiar o planejamento urbano, projetos especiais e inovação da cidade.

A solução se concentra na construção de bases de dados e na visualização destes com flexibildiade. Como forma de subsidiar o processo de diagnóstico dos dados fornecidos pela prefeitura e coletados em base de dados abertos, esta prova de conceito tem como finalidade apresentar uma solução para auxílio neste processo, especificamente no cenário do Programa Vem pro Centro.

O Programa Vem pro Centro busca, por meio de ações de reabilitação, restauro e construção em imóveis ociosos, produzir unidades habitacionais, equipamentos públicos e pequenos comércios, que garantam o adensamento populacional, a conservação integrada, a sustentabilidade e a inclusão socioeconômica da população e dos usuários da região central de São Luís.


## Guia do usuário
---

Toda a documentação das implementações podem ser obtidas no link: https://gebraz.github.io/pdcbid/

## Guia de instalação
---

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

## Autor(es)
---

Desenvolvido por
 - Geraldo Braz Junior
 - Anselmo Cardoso de Paiva

## Licença
---

Esta ferramenta é resultado da iniciativa Código para o Desenvolvimento, financiada pelo BID, com Licença AM-331-A3.

## Isenção de responsabilidade

O BID não será responsável, em hipótese alguma, por danos ou indenizações, morais ou patrimoniais; direto ou indireto; acessório ou especial; ou por consequência, prevista ou imprevista, que possa surgir:

i. Sob qualquer teoria de responsabilidade, seja em contrato, violação de direitos de propriedade intelectual, negligência, ou sob qualquer outra teoria; 

ii. Como resultado do uso da Ferramenta Digital, incluindo, mas não limitado a, possíveis defeitos na Ferramenta Digital, ou perda ou imprecisão de dados de qualquer tipo. O anterior inclui despesas ou danos associados a falhas de comunicação e/ou mau funcionamento do computador, vinculados ao uso da Ferramenta Digital.