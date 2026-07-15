from core.dominio.puertos import PuertoCargadorDocumentos, PuertoAlmacenVectorial, PuertoLLM

class AplicacionRAG:
    def __init__(self, cargador: PuertoCargadorDocumentos, almacenVectorial: PuertoAlmacenVectorial, llm:PuertoLLM):
        self.cargador = cargador
        self.almacenVectorial = almacenVectorial
        self.llm = llm
        self._estaInicializada = False

    def inicializarBaseConocimiento(self, rutaArchivo: str) -> None:
        print("Iniciando extraccion y vectorizacion de datos...")
        documentos = self.cargador.cargarDividir(rutaArchivo)
        self.almacenVectorial.almacenar(documentos)
        self._estaInicializada = True
        print("Base de conocimiento indexada en memoria de forma exitosa.")

    def _esPreguntaDirecta(self, consulta: str) -> bool:
        palabrasClave = ["cuál es el porcentaje", "cuántos", "fecha", "total", "cantidad exacta"]
        return any(palabra in consulta.lower() for palabra in palabrasClave)

    def hacerPregunta(self, consulta: str) -> str:
        if not self._estaInicializada:
            return "Operacion denegada. Inicialice la base de conocimiento primero."
        
        recuperador = self.almacenVectorial.obtenerRecuperador()

        if self._esPreguntaDirecta(consulta):
            print("\n[Enrutador] Pregunta directa detectada. Solicitando extraccion de dato duro...")
            consultaModificada = consulta + " (Responde únicamente con el dato exacto o número, sin explicaciones ni texto adicional)."
            return self.llm.generarRespuesta(consultaModificada, recuperador)
        else:
            print("\n[Enrutador] Pregunta analitica detectada. Usando generación de lenguaje natural...")
            return self.llm.generarRespuesta(consulta, recuperador)