from langchain_community.document_loader import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from core.dominio.puertos import PuertoCargadorDocumentos, PuertoAlmacenVectorial, PuertoLLM

class AdaptadorPyPDF(PuertoCargadorDocumentos):
    def cargarDividir(self, rutaArchivo: str):
        cargador = PyPDFLoader(rutaArchivo)
        documentos = cargador.load()
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
        self.llm = ChatCohere(model="command-r-plus")

    def generarRespuesta(self, consulta: str, recuperador):
        cadena = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=recuperador
        )
        respuesta = cadena.invoke({"query": consulta})
        return respuesta["result"]