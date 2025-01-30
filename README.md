# SmartSense

## Descrição

Este projeto consiste em um sistema de monitoramento de dados climáticos, provenientes da API OpenWeatherMap, que utiliza um broker MQTT para receber dados de sensores, processá-los e armazená-los em um banco de dados PostgreSQL. O sistema também é complementado por um dashboard interativo no Metabase, onde é possível visualizar métricas em tempo real, como temperatura, umidade e velocidade do vento, além de alarmes gerados com base em condições predefinidas.

## Arquitetura

**- Sensores Virtuais:** Coletam dados meteorológicos (temperatura, umidade, velocidade do vento, condições climáticas) a partir da API OpenWeatherMap.

**- DataCollector:** Um módulo em Python que realiza requisições à API, processa os dados e publica em um broker MQTT.

**- MQTT Broker:** Responsável pela comunicação entre os módulos, utilizando o protocolo MQTT para transferência eficiente de mensagens.

**- DataProcessor:** Assina os tópicos MQTT, processa os dados recebidos e gera alertas ou transformações.

**- Banco de Dados Temporal:** Armazena os dados coletados, possibilitando consulta histórica e análises futuras.

**- Ferramenta de Visualização:** Exibe os dados e os alertas em um dashboard interativo.


## Tecnologias utilizadas

**- Python:** Para processamento e persistência dos dados.

**- PostgreSQL + TimeScaleDB:** Para armazenamento de dados de sensores e alarmes.

**- Mosquitto:** Para comunicação entre os módulos DataCollector e DataProcessor.

**- Metabase:** Para visualização e análise dos dados.


## Principais Arquivos

O sistema está dividido em dois  arquivos:

### data_collector.py
Esse código é  responsável por coletar dados meteorológicos e publicá-los em um broker MQTT. Ele utiliza a API OpenWeather para obter informações como temperatura, umidade e velocidade do vento de uma cidade específica (por padrão, Belo Horizonte). Esses dados são organizados em formato JSON e publicados periodicamente em tópicos MQTT.

O funcionamento do código se dá em três etapas principais. Primeiro, ele configura a conexão com o broker MQTT e define uma lista de sensores, cada um com um identificador único, um tipo de dado e uma função de coleta que faz chamadas à API OpenWeather. Em seguida, ao iniciar o coletor de dados, o programa estabelece a conexão com o broker e inicia um loop contínuo onde publica periodicamente uma mensagem inicial contendo a lista de sensores e, logo depois, coleta os dados de cada sensor e os publica nos tópicos MQTT correspondentes. O processo se repete em intervalos configuráveis, nesso caso igual a 60 segundos.

Além disso, o código possui uma função específica para obter os dados da API OpenWeather, enviando uma requisição HTTP à API e extraindo as informações relevantes do JSON retornado. Caso a requisição falhe, um erro é impresso no console.

### data_processor.py

O DataProcessor é responsável por receber, processar e armazenar os dados coletados pelos sensores, garantindo a persistência das informações no banco de dados PostgreSQL. Ele se conecta a um broker MQTT, onde escuta mensagens publicadas pelos sensores e processa as informações recebidas.

Ao receber uma mensagem de um sensor, o DataProcessor extrai os dados, incluindo o ID da máquina, o ID do sensor, o timestamp e o valor da leitura. Esses dados são então armazenados na tabela sensor_metrics, permitindo um registro histórico das medições.

Além disso, o sistema implementa um mecanismo de monitoramento de alarmes. Para sensores de temperatura, umidade e vento, o DataProcessor verifica se os valores ultrapassam limites críticos e gera alarmes quando necessário, registrando-os na tabela alarms. Ele também monitora a frequência das mensagens enviadas pelos sensores, identificando sensores inativos e registrando um alarme caso um sensor não reporte dados por mais de 10 minutos.

O programa opera continuamente, garantindo que os sensores estejam ativos e que os dados sejam armazenados de forma confiável, contribuindo para um sistema robusto de monitoramento.

## Banco de Dados

O banco de dados escolhido foi o PostgreSQL com a extensão TimeScaleDB. Essa extensão torna-se necessária porque adiciona funcionalidades e otimizações para séries temporais e no projeto, todos os valores provenientes dos sensores são armazenados juntamente com a data e horário de coleta.

O banco de dados criado possui o nome sensor_data e possui duas tabelas principais: sensor_metrics (responsável por armazenar a leitura dos sensores) e alarms (responsável por armazenar os alarmes gerados). As colunas e o tipo de dados de cada uma das tabelas está descrito abaixo.

**- Tabela sensor_metrics:**

| Coluna          | Tipo           |   Descrição              |
| -------------   | -------------  | -------------            |
| time            | Timestamp      | Data e hora da leitura   |
| machine_id      | Text           | Identificador da máquina |
| sensor_id       | Text           | Identificador do sensor  |
| value           | Float          | Valor medido             |

**- Tabela alarms:**

| Coluna          | Tipo           |   Descrição              |
| -------------   | -------------  | -------------            |
| time            | Timestamp      | Data e hora em que o alarme foi registrado  |
| machine_id      | Text           | Identificador da máquina |
| sensor_id       | Text           | Identificador do sensor  |
| alarm_type      | Text           | Tipo do alarme           |
| details         | Text           | Descrição do alarme      |

## Geração de alarmes

Para definir a geração de alarmes, alguns critérios foram utilizados e baseados nesses critérios, os respectivos tipos de alarmes foram definidos. A tabela abaixo mostra as condições de disparo dos alarmes.

| Condição                             | alarm_type      |
| -------------                        | -------------   |
| Temperatura abaixo de 5°C            | cold_alert      |
| Temperatura acima de 35°C            | heat_alert      |
| Umidade abaixo de 20%                | dry_alert       |
| Umidade acima de 90%                 | humidity_alert  |
| Velocidade do vento > 17 m/s         | wind_alert      |
| Variação de temperatura >10°C em 1h  | temp_variation  |
| Sensor inativo por 10 min            | inactive        |

## Como rodar o projeto

O primeiro passo é iniciar o MQTT Broker, com o comando:

```
mosquitto -v
```

Após isso, em terminais diferentes, roda-se os arquivos data_processor.py e data_collector.py, com os comandos: 

```
python data_processor.py
```

```
python data_collector.py
```

Desse modo, o projeto já estará funcionando e o mqtt broker realizando corretamente a comunicação entre os módulos.

## Dashboard

Visando facilitar a visualização dos dados adquiridos, criou-se um dashboard usando a ferramenta Metabase. Para rodar esse dashboard basta rodar o seguinte comando no diretório de instalação do Metabase e acessar a página em http://localhost:3000/ .

```
java -jar metabase.jar  
```
O dashboard foi construído usando querys em SQL, como exemplo abaixo tem-se a query utilizada para realizar a média móvel de temperatura nas últimas 24 horas.
```
SELECT
    DATE_TRUNC('hour', time) AS hora,  -- Agrupa por hora corretamente
    AVG(value) AS media_temperatura
FROM sensor_metrics
WHERE 
    sensor_id = 'temp_01'  -- Filtra apenas o sensor de temperatura
    AND time >= NOW() - INTERVAL '24 hours'  -- Considera as últimas 24 horas
GROUP BY hora
ORDER BY hora;
```
Além disso, os recursos visuais disponibilizados pela plataforma foram amplamente explorados, de modo a facilitar a análise e interpretação por parte do usuário.
