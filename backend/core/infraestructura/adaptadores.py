import os
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
#from langchain_classic.chains import RetrievalQA
from core.dominio.puertos import PuertoCargadorDocumentos, PuertoAlmacenVectorial, PuertoLLM
from langchain_core.prompts import PromptTemplate
import re


class AdaptadorPyPDF(PuertoCargadorDocumentos):
    def cargarDividir(self, rutaArchivo: str):
        print(f"[Sistema]: Escaneando directorio '{rutaArchivo}' en busca de documentos PDF...")
        cargador = PyPDFDirectoryLoader(rutaArchivo)
        paginas = cargador.load()

        if not paginas:
            raise ValueError(f"Error: No se encontraron PDFs legibles en la {rutaArchivo}.")
        print(f"Se han cargado {len(paginas)} paginas en total.")

        agrupado = {}
        for pagina in paginas:
            origen = pagina.metadata.get("source", "desconocido")
            agrupado.setdefault(origen, []).append(pagina)

        divisor = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunksFinal = []

        for origen, listaPaginas in agrupado.items():
            listaPaginas.sort(key=lambda p: p.metadata.get("page", 0))

            textoCompleto = ""
            offsetsPorPagina = []

            for pagina in listaPaginas:
                offsetsPorPagina.append((len(textoCompleto), pagina.metadata.get("page", 0)))
                textoCompleto += pagina.page_content + "\n"

            fragmentos = divisor.split_text(textoCompleto)

            cursor = 0
            for fragmento in fragmentos:
                puntoBusqueda = max(0, cursor - 200)
                posicion = textoCompleto.find(fragmento, puntoBusqueda)
                if posicion == -1:
                    posicion = cursor

                inicioChunk = posicion
                finChunk = posicion + len(fragmento)
                cursor = finChunk

                paginaInicio = offsetsPorPagina[0][1]
                paginaFin = offsetsPorPagina[0][1]
                for offsetInicio, numPagina in offsetsPorPagina:
                    if offsetInicio <= inicioChunk:
                        paginaInicio = numPagina
                    if offsetInicio < finChunk:
                        paginaFin = numPagina

                chunksFinal.append(Document(
                    page_content=fragmento,
                    metadata={
                        "source": origen,
                        "pagina_inicio": paginaInicio,
                        "pagina_fin": paginaFin,
                    }
                ))

        return chunksFinal
    
class AdaptadorFaissCohere(PuertoAlmacenVectorial):
    def __init__(self):
        self.incrustaciones = CohereEmbeddings(model="embed-multilingual-v3.0")
        self.almacenVectorial = None
    
    def almacenar(self, documentos):
        self.almacenVectorial = FAISS.from_documents(documentos, self.incrustaciones)

    def obtenerRecuperador(self):
        if not self.almacenVectorial:
            raise ValueError("Error : El almacen vectorial no ha sido inicializado.")
        return self.almacenVectorial.as_retriever(search_kwargs={"k": 5})

class AdaptadorCohereLLM(PuertoLLM):
    def __init__(self):
        self.llm = ChatCohere(temperature=0)
        self.promptTemplate = PromptTemplate(
            input_variables=["context", "question"],
            template="""
Eres un asistente que responde preguntas usando ÚNICAMENTE los fragmentos de contexto numerados a continuación.

Reglas OBLIGATORIAS de citación:
- Cada vez que uses información de un fragmento, marca al final de esa frase u oración su número entre corchetes, así: [1], [2], etc.
- Si combinas información de varios fragmentos en una misma idea, incluye todos los números correspondientes: [1][3].
- NO marques un fragmento si no lo usaste. No cites fragmentos "por si acaso".

Reglas OBLIGATORIAS de formato y contenido:
- Si la respuesta menciona 2 o más elementos, reglas, requisitos o pasos: SIEMPRE usa una lista con viñetas (-), un elemento por línea.
- Cada punto de la lista debe tener: el concepto clave en **negrita** (solo 2-4 palabras, NUNCA la oración completa), seguido de dos puntos y una explicación breve de una frase.
- Ejemplo del formato correcto para un punto de lista:
  - **Afirmar precios no vigentes**: no se permite promocionar ofertas o descuentos que ya expiraron [1].
- Ejemplo de formato INCORRECTO (no hagas esto):
  - **Afirmar precios o beneficios no vigentes** [1]   ← mal, toda la línea en negrita y sin explicación
- Si la respuesta es un solo dato puntual (una fecha, un número, un sí/no): responde en una sola frase, sin lista y sin negrita.
- Nunca uses encabezados (#, ##).

Si la información no está en el contexto, dilo explícitamente y no cites nada.

Fragmentos:
{context}

Pregunta: {question}

Respuesta (con citas [n] donde corresponda):"""
        )

    def _formatearContexto(self, documentos):
        bloques = []
        for i, doc in enumerate(documentos, start=1):
            bloques.append(f"[{i}] {doc.page_content}")
        return "\n\n".join(bloques)

    def generarRespuesta(self, consulta: str, recuperador):
        documentos = recuperador.invoke(consulta)

        contexto = self._formatearContexto(documentos)
        prompt = self.promptTemplate.format(context=contexto, question=consulta)
        respuestaLLM = self.llm.invoke(prompt)
        textoRespuesta = respuestaLLM.content

        numerosCitados = set(int(n) for n in re.findall(r"\[(\d+)\]", textoRespuesta))

        fuentes = []
        vistos = set()
        for i, doc in enumerate(documentos, start=1):
            if i not in numerosCitados:
                continue  

            archivo = os.path.basename(doc.metadata.get("source", "desconocido"))
            pIni = doc.metadata.get("pagina_inicio", "N/A")
            pFin = doc.metadata.get("pagina_fin", "N/A")

            if isinstance(pIni, int):
                pIni += 1
            if isinstance(pFin, int):
                pFin += 1

            pagina = f"{pIni}-{pFin}" if pIni != pFin else str(pIni)

            clave = (archivo, pagina)
            if clave in vistos:
                continue
            vistos.add(clave)
            fuentes.append({"archivo": archivo, "pagina": pagina})

        return {"respuesta": textoRespuesta, "fuentes": fuentes}