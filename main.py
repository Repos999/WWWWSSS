from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

conexoes_ativas: list[WebSocket] = []
ultima_mensagem_salva = {"usuario": "Sistema", "mensagem": "Conectado à Nuvem via WebSocket!"}

@app.get("/")
def home():
    return {"status": "Servidor WebSocket Ativo"}

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conexoes_ativas.append(websocket)
    await websocket.send_text(json.dumps(ultima_mensagem_salva))
    try:
        while True:
            dados_recebidos = await websocket.receive_text()
            dados_json = json.loads(dados_recebidos)
            
            # Corrigido: Declaramos o global ANTES de mexer na variável
            global ultima_mensagem_salva
            ultima_mensagem_salva = {
                "usuario": str(dados_json.get("usuario", "Anônimo")),
                "mensagem": str(dados_json.get("mensagem", ""))
            }
            
            for conexao in conexoes_ativas:
                try:
                    await conexao.send_text(json.dumps(ultima_mensagem_salva))
                except Exception:
                    pass
    except WebSocketDisconnect:
        conexoes_ativas.remove(websocket)
