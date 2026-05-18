# Carona Access Monitoring

Estudo de caso público para monitoramento de acesso carona/tailgating por câmeras.

Este repositório modela uma versão sanitizada de um fluxo de monitoramento de acesso: uma câmera observa o portão dentro de um contexto operacional Dahua/Intelbras, agrupa detecções em sessões curtas, conta objetos cruzando zonas configuradas e abre um evento para operação quando a quantidade de objetos não corresponde à regra esperada.

## Problema Operacional

Em operações de controle de acesso, o evento relevante muitas vezes não é uma detecção isolada. É uma sequência curta: uma abertura de portão, um veículo ou pessoa esperada, e depois outra pessoa, moto, bicicleta ou veículo entrando na mesma janela. O sistema precisa de lógica de sessão, ROI, zonas de detecção, cooldown e um payload claro para operadores.

## O Que Este Projeto Demonstra

- API FastAPI para um módulo de monitoramento de acesso por câmera usando uma família operacional Dahua/Intelbras.
- Agrupamento de sessões com conceitos de `session_gap_s` e `session_max_s`.
- Tratamento de classes como pessoa, carro, moto, bicicleta, caminhão e ônibus.
- Configuração de zona de detecção e zona proibida com pontos normalizados.
- Payload público e seguro para possível evento de acesso carona/tailgating.

## Arquitetura

```text
detecções da câmera -> sessão curta de acesso -> regra de contagem de objetos -> evento operacional
                                                    -> runtime da câmera -> endpoint de saúde
```

Esta versão pública começa na fronteira da detecção de objetos. Em produção, a mesma lógica seria conectada a frames VMS, detecção de objetos, tracking, alertas WebSocket e telas de operação.

## Rodar Localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8012
```

Abra:

- `http://127.0.0.1:8012/`
- `http://127.0.0.1:8012/api/carona/cameras`
- `http://127.0.0.1:8012/api/carona/runtime`

Crie um evento sintético:

```bash
curl -X POST http://127.0.0.1:8012/api/demo/carona-access
curl http://127.0.0.1:8012/api/carona/events
```

## Escopo Público e Seguro

Todos os sites, IDs de câmeras, eventos, zonas e detecções são sintéticos. Não há dados de clientes, IPs privados, gravações de portão, credenciais, SDKs proprietários ou payloads reais de alerta.

## Competências Representadas

Python, FastAPI, modelagem de domínio de controle de acesso, lógica de sessão, desenho de eventos de video analytics, operações VMS e engenharia de portfólio com dados públicos e seguros.
