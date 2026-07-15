import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.infraestructura.adaptadores import AdaptadorPyPDF, AdaptadorFaissCohere, AdaptadorCohereLLM
from core.dominio.casosDU import AplicacionRAG

load_dotenv()

class ConsultaWeb(BaseModel):
    pregunta:str

app = FastAPI(title="API del Agente BIMBAM Buy")

origenes_raw = os.getenv("FRONTEND_URLS")

if not origenes_raw:
    origenes_permitidos = []
    print("No se han definido orígenes CORS.")
else:
    origenes_permitidos = origenes_raw.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agenteGlobal = None

@app.on_event("startup")
def arrancarMotorIa():
    global agenteGlobal
    print("[Servidor]: Inicializando motor RAG para entorno web...")

    agenteGlobal = AplicacionRAG(
        cargador=AdaptadorPyPDF(),
        almacenVectorial=AdaptadorFaissCohere(),
        llm=AdaptadorCohereLLM()
    )

    rutaArchivo = "./data"
    if not os.path.exists(rutaArchivo):
        raise RuntimeError(f"El archivo no existe en la ruta {rutaArchivo}.")
    
    agenteGlobal.inicializarBaseConocimiento(rutaArchivo)
    print("[Servidor]: Agente IA listo para recibir peticiones HTTP.")

@app.post("/preguntar")
def endpointPreguntar(consulta: ConsultaWeb):
    if not agenteGlobal:
        raise HTTPException(status_code=503, detail="El agente no está inicializado.")
    
    try:
        respuesta = agenteGlobal.hacerPregunta(consulta.pregunta)
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo en inferencia: {str(e)}")