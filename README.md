![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)

# PomoLive 🍅🎙️

> Aplicação modular de foco e estudo ativo combinando temporizador Pomodoro customizável e assistente de voz socrático via **Gemini Multimodal Live API**.

---

## 🎯 Visão Geral
O **PomoLive** otimiza o ciclo de retenção de conteúdo integrando sessões de foco silencioso ao método de estudo ativo (Técnica Feynman). Durante o bloco de foco, o tráfego de áudio e as conexões de IA permanecem desligados. Ao término do tempo, a IA interrompe ativamente o silêncio para arguir o usuário sobre o que foi estudado, suportando inclusive extensão de tempo de estudo via comandos de voz (*Tool Calling*).

## 🏗️ Arquitetura do Sistema
O sistema adota desacoplamento estrito entre cliente e servidor orientado a contratos de eventos JSON:

```text
[ React (Vite) + TS ] <--- WebSocket (JSON Events + PCM Audio) ---> [ FastAPI Gateway ] <--- Bidirectional Stream ---> [ Gemini Live API ]
                                                                             │
                                                                       [ SQLite Local ]
