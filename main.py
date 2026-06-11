from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()

# Gerenciador do Estado do Chat (Sem usar variáveis globais problemáticas)
class ChatManager:
    def __init__(self):
        self.conexoes_ativas: list[WebSocket] = []
        self.ultima_mensagem = {
            "usuario": "Sistema", 
            "mensagem": "Conectado à Nuvem via WebSocket!"
        }

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.conexoes_ativas.append(websocket)
        # Envia o histórico/última mensagem assim que o jogador entra
        await websocket.send_text(json.dumps(self.ultima_mensagem))

    def desconectar(self, websocket: WebSocket):
        if websocket in self.conexoes_ativas:
            self.conexoes_ativas.remove(websocket)

    async def transmitir_mensagem(self, dados_json: dict):
        # Atualiza o estado interno de forma segura
        self.ultima_mensagem = {
            "usuario": str(dados_json.get("usuario", "Anônimo")),
            "mensagem": str(dados_json.get("mensagem", ""))
        }
        
        # Envia para todo mundo que está online
        payload = json.dumps(self.ultima_mensagem)
        for conexao in self.conexoes_ativas:
            try:
                await conexao.send_text(payload)
            except Exception:
                # Se uma conexão antiga falhar, o servidor ignora e continua vivo
                pass

# Inicializa o gerenciador
manager = ChatManager()

@app.get("/")
def home():
    return {"status": "Servidor WebSocket Ativo e Saudável"}

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.conectar(websocket)
    try:
        while True:
            # Fica escutando as mensagens vindas do Roblox
            dados_recebidos = await websocket.receive_text()
            try:
                dados_json = json.loads(dados_recebidos)
                await manager.transmitir_mensagem(dados_json)
            except json.JSONDecodeError:
                pass # Ignora mensagens com formato inválido
    except WebSocketDisconnect:
        manager.desconectar(websocket)
