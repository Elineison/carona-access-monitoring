# Carona Access Monitoring

Módulo FastAPI que representa a detecção de possível acesso carona/tailgating em uma operação VMS de controle de acesso por câmeras.

## O Que Significa VMS Aqui

VMS significa Sistema de Gerenciamento de Vídeo: a camada que centraliza câmeras, DVRs/NVRs, streams ao vivo, gravações, eventos, alertas e integrações. Neste repositório, o VMS é a base operacional que fornece o stream da câmera de acesso e recebe eventos, runtime e health checks do módulo.

## O Que o Sistema Faz

- Recebe objetos detectados em uma câmera de acesso.
- Agrupa detecções em sessões curtas de passagem pelo portão.
- Conta pessoas, veículos, motos, bicicletas, ônibus e caminhões dentro da mesma sessão.
- Usa ROI, zona de detecção e zona proibida para compor o contexto operacional.
- Gera evento quando a sessão indica mais objetos do que o esperado para uma passagem.
- Expõe runtime e health check para suporte.

## Contexto Representado

- Intelbras em controle de acesso.
- Stream de vídeo em tempo real, vindo da operação VMS, processado por worker de detecção.
- Integração entre câmera, módulo de analytics, API operacional e alertas.

## Endpoints

- `GET /` - página simples com links do módulo.
- `GET /api/carona/cameras` - câmeras configuradas e runtime.
- `GET /api/carona/runtime` - snapshot operacional do módulo.
- `POST /api/carona/cameras/{camera_id}/objects` - ingere objeto detectado.
- `POST /api/demo/carona-access` - cria evento sintético de possível carona.
- `GET /api/carona/sessions` - lista sessões de acesso.
- `GET /api/carona/events` - lista eventos gerados.
- `GET /api/system/health` - saúde do módulo.

## Rodar Localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8012
```

## Testar

```bash
curl http://127.0.0.1:8012/api/carona/cameras
curl -X POST http://127.0.0.1:8012/api/demo/carona-access
curl http://127.0.0.1:8012/api/carona/sessions
curl http://127.0.0.1:8012/api/carona/events
curl http://127.0.0.1:8012/api/system/health
```

## Escopo Público

Todos os dados são sintéticos. Não há nomes de clientes, IPs privados, gravações de portão, credenciais, SDKs proprietários ou endpoints reais de alerta.
