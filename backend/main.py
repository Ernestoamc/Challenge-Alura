import os
from dotenv import load_dotenv
from backend.core.infraestructura.adaptadores import AdaptadorPyPDF, AdaptadorFaissCohere, AdaptadorCohereLLM
from backend.core.dominio.casosDU import AplicacionRAG

def main():
    load_dotenv()

    if not os.getenv("COHERE_API_KEY"):
        print("error de entorno: COHERE_API_KEY no detectada.")
        return
    
    aplicacion = AplicacionRAG(
        cargador=AdaptadorPyPDF(),
        almacenVectorial=AdaptadorFaissCohere(),
        llm=AdaptadorCohereLLM()
    )
    rutaDocumento = "./data"

    if not os.path.exists(rutaDocumento):
        print(f"El archivo no existe en la ruta {rutaDocumento}.")
        return
    
    try:
        aplicacion.inicializarBaseConocimiento(rutaDocumento)
    except Exception as e:
        print(f"Fallo en la inicializacion: {e}")
        return
    
    print("\nCLI del agente IA activo. Escriba 'salir' para terminar el proceso.")

    while True:
        pregunta = input("\nIngrese su consulta: ")

        if pregunta.lower() in ['salir', 'exit', 'quit', 'q']:
            print("Terminando ejecucion...")
            break
        if not pregunta.strip():
            continue

        try:
            respuesta = aplicacion.hacerPregunta(pregunta)
            print("\n[Respuesta]:")
            print(respuesta)
        except Exception as e:
            print(f"\nExcepcion detectada durante la inferencia: {e}")

if __name__ == "__main__":
    main()
    