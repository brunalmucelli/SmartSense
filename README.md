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

### data_processor.py


### data_collector.py

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

## Dashboard


## Como rodar o projeto


## Conclusão

