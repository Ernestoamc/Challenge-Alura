from abc import ABC, abstractmethod
from typing import List, Any

class PuertoCargadorDocumentos(ABC):
    @abstractmethod
    def cargarDividir(self, rutaArchivo: str) -> List[Any]:
        pass

class PuertoAlmacenVectorial(ABC):
    @abstractmethod
    def almacenar(self, documentos: List[Any]) -> None:
        pass
    
    @abstractmethod
    def obtenerRecuperador(self) -> Any:
        pass

class PuertoLLM(ABC):
     @abstractmethod
     def generarRespuesta(self, consulta: str, recuperador: Any) -> str:
         pass