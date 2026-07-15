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

    def hacerPregunta(self, consulta: str) -> str:
        if not self._estaInicializada:
            return "Operacion denegada. Inicialice la base de conocimiento primero."
        
        recuperador = self.almacenVectorial.obtenerRecuperador()
        return self.llm.generarRespuesta(consulta, recuperador)