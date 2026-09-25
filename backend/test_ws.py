import asyncio
import json
import websockets

URI = "ws://127.0.0.1:8000/ws/session"
SESSION_ID = "11111111-2222-3333-4444-555555555555"


async def main():
    print(f"Conectando ao WebSocket: {URI} ...")
    async with websockets.connect(URI) as ws:
        # 1. Enviar SESSION_START -> Deve ir para FOCUS
        start_payload = {
            "event": "SESSION_START",
            "session_id": SESSION_ID,
            "timestamp": "2026-09-24T20:00:00Z",
            "payload": {
                "topic": "Estruturas de Dados: Árvores Rubro-Negras",
                "persona_id": "socratic_mentor",
                "focus_duration_minutes": 25,
                "break_duration_minutes": 5,
                "max_checkin_turns": 3
            }
        }
        await ws.send(json.dumps(start_payload))
        resp1 = json.loads(await ws.recv())
        print("\n[RESPOSTA 1] ->", resp1["event"], "| Estado atual:", resp1["payload"]["current_state"])
        assert resp1["payload"]["current_state"] == "FOCUS"

        # 2. Timer zerou no cliente -> Deve ir para CHECKIN_CONNECTING
        expire_payload = {
            "event": "TIMER_EXPIRED",
            "session_id": SESSION_ID,
            "timestamp": "2026-09-24T20:25:00Z",
            "payload": {"completed_focus_minutes": 25}
        }
        await ws.send(json.dumps(expire_payload))
        resp2 = json.loads(await ws.recv())
        print("[RESPOSTA 2] ->", resp2["event"], "| Estado atual:", resp2["payload"]["current_state"])
        assert resp2["payload"]["current_state"] == "CHECKIN_CONNECTING"

        # 3. Simulação de transição para discussão ativa (GEMINI_READY)
        ready_payload = {
            "event": "GEMINI_READY",
            "session_id": SESSION_ID,
            "timestamp": "2026-09-24T20:25:02Z",
            "payload": {}
        }
        await ws.send(json.dumps(ready_payload))
        resp_ready = json.loads(await ws.recv())
        print("[RESPOSTA 2.1] ->", resp_ready["event"], "| Estado atual:", resp_ready["payload"]["current_state"])
        assert resp_ready["payload"]["current_state"] == "ACTIVE_DISCUSSION"

        # 4. Agora sim: com estado em ACTIVE_DISCUSSION, finaliza e grava no SQLite
        complete_payload = {
            "event": "CHECKIN_COMPLETE_MANUAL",
            "session_id": SESSION_ID,
            "timestamp": "2026-09-24T20:28:00Z",
            "payload": {}
        }
        await ws.send(json.dumps(complete_payload))
        resp3 = json.loads(await ws.recv())
        
        if resp3.get("event") == "ERROR":
            print("Erro retornado pelo servidor:", resp3["payload"])
            return

        print("[RESPOSTA 3] ->", resp3["event"], "| Gravado no Banco com ID:", resp3["payload"]["db_id"])
        assert resp3["event"] == "SESSION_SAVED"
        assert resp3["payload"]["db_id"] is not None

        print("\n✅ Fluxo de WebSocket e Persistência SQLite validado com sucesso!")


if __name__ == "__main__":
    asyncio.run(main())