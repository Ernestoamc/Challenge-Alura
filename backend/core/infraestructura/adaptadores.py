from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from core.dominio.puertos import PuertoCargadorDocumentos, PuertoAlmacenVectorial, PuertoLLM

class AdaptadorPyPDF(PuertoCargadorDocumentos):
    def cargarDividir(self, rutaArchivo: str):
        print(f"[Sistema]: Escaneando directorio '{rutaArchivo}' en busca de documentos PDF...")
        cargador = PyPDFDirectoryLoader(rutaArchivo)
        documentos = cargador.load()

        if not documentos:
            raise ValueError(f"Error: No se encontraron PDFs legibles en la {rutaArchivo}.")
        print(f"Se han cargado {len(documentos)} paginas en total.")
        divisor = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return divisor.split_documents(documentos)
    
class AdaptadorFaissCohere(PuertoAlmacenVectorial):
    def __init__(self):
        self.incrustaciones = CohereEmbeddings(model="embed-multilingual-v3.0")
        self.almacenVectorial = None
    
    def almacenar(self, documentos):
        self.almacenVectorial = FAISS.from_documents(documentos, self.incrustaciones)

    def obtenerRecuperador(self):
        if not self.almacenVectorial:
            raise ValueError("Error : El almacen vectorial no ha sido inicializado.")
        return self.almacenVectorial.as_retriever(search_kwargs={"k": 3})

class AdaptadorCohereLLM(PuertoLLM):
    def __init__(self):
        self.llm = ChatCohere()

    def generarRespuesta(self, consulta: str, recuperador):
        cadena = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=recuperador
        )
        respuesta = cadena.invoke({"query": consulta})
        return respuesta["result"]