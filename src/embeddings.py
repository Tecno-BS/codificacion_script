import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Optional
import warnings
from .config import EMBEDDING_MODEL
warnings.filterwarnings("ignore")



class GenerateEmebeddings:
    def __init__(self, model: str = EMBEDDING_MODEL):
        self.model_name = model
        self.tokenizer = None
        self.model = None
        self.device = self._device_config()
        self._load_model()
    
    def _device_config(self) -> torch.device:
        if torch.cuda.is_available():
            return torch.device('cuda')
        else:
            return torch.device('cpu')
    
    def _load_model(self) -> None:
        try:
            print(f"Cargando modelo { self.model_name }")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"Modelo cargado en {self.device}")
        except Exception as e:
            raise Exception(f"Error al cargar el modelo {self.model_name}: {e}")

    
    def generate_embeddings(self, text: List[str]) -> np.ndarray:
        if not text: 
            return np.array([])
        
        #Limpiar textos vacios 
        clean_text = [text for text in text if text and text.strip()]

        if not clean_text:
            return np.array([])
        
        embeddings = []

        #procesar en lotes para eficiencia
        batch_size = 32
        for i in range(0, len(clean_text), batch_size):
            batch = clean_text[i:i + batch_size]

            #Tokenizacion
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length = 512,
                return_tensors='pt'
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.extend(batch_embeddings)   

        return np.array(embeddings)


    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        if embedding1.shape != embedding2.shape:
            raise ValueError("Las dimensiones de los embeddings no coinciden")
        
        #Reshape para skLearn

        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)

        #Calcular similitud 
        similitud = cosine_similarity(emb1, emb2)[0][0]
        return float(similitud)


    def find_similaritys(self, consult_embedding: np.ndarray, base_embeddings: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if base_embeddings.shape[0] == 0:
            return []
        
        similarities = cosine_similarity(consult_embedding.reshape(1, -1), base_embeddings)[0]

        indices_top = np.argsort(similarities)[::-1][:top_k]

        result = [(int(idx), float(similarities[idx])) for idx in indices_top]

        return result

        