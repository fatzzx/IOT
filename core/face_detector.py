#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de detecção e reconhecimento facial
"""

import cv2
import face_recognition
import numpy as np
from typing import List, Tuple, Optional
import os
from utils.logger import get_logger

class FaceDetector:
    """Classe responsável pela detecção e reconhecimento facial"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.video_capture = None
        self.known_faces = []
        self.known_names = []
        self.face_locations = []
        self.face_names = []
        self.process_frame = True
        
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """
        Inicializa a câmera
        
        Args:
            camera_index: Índice da câmera (padrão 0)
            
        Returns:
            bool: True se a câmera foi inicializada com sucesso
        """
        try:
            if self.video_capture is not None:
                self.video_capture.release()
                
            self.video_capture = cv2.VideoCapture(camera_index)
            
            if not self.video_capture.isOpened():
                self.logger.error(f"Não foi possível abrir a câmera {camera_index}")
                return False
                
            # Configurar resolução
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.logger.info(f"Câmera {camera_index} inicializada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar câmera: {e}")
            return False
    
    def load_known_faces(self, faces_dir: str = "data/faces") -> int:
        """
        Carrega rostos conhecidos do diretório
        
        Args:
            faces_dir: Diretório contendo as imagens dos rostos
            
        Returns:
            int: Número de rostos carregados
        """
        try:
            self.known_faces.clear()
            self.known_names.clear()
            
            if not os.path.exists(faces_dir):
                os.makedirs(faces_dir)
                self.logger.info(f"Diretório {faces_dir} criado")
                return 0
            
            loaded_count = 0
            for filename in os.listdir(faces_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        image_path = os.path.join(faces_dir, filename)
                        image = face_recognition.load_image_file(image_path)
                        encodings = face_recognition.face_encodings(image)
                        
                        if encodings:
                            self.known_faces.append(encodings[0])
                            name = os.path.splitext(filename)[0]
                            self.known_names.append(name)
                            loaded_count += 1
                            self.logger.debug(f"Rosto carregado: {name}")
                        else:
                            self.logger.warning(f"Nenhum rosto encontrado em {filename}")
                            
                    except Exception as e:
                        self.logger.error(f"Erro ao carregar {filename}: {e}")
            
            self.logger.info(f"{loaded_count} rostos carregados com sucesso")
            return loaded_count
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar rostos conhecidos: {e}")
            return 0
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Captura um frame da câmera
        
        Returns:
            np.ndarray ou None: Frame capturado ou None se houver erro
        """
        if self.video_capture is None or not self.video_capture.isOpened():
            return None
            
        ret, frame = self.video_capture.read()
        return frame if ret else None
    
    def detect_faces(self, frame: np.ndarray) -> Tuple[List, List]:
        """
        Detecta e reconhece rostos em um frame
        
        Args:
            frame: Frame da imagem
            
        Returns:
            Tuple: (localizações dos rostos, nomes identificados)
        """
        try:
            # Redimensionar frame para processamento mais rápido
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            if self.process_frame:
                # Detectar localizações dos rostos
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                
                self.face_names = []
                
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(self.known_faces, face_encoding)
                    name = "Desconhecido"
                    
                    # Usar distância para encontrar melhor match
                    if True in matches:
                        face_distances = face_recognition.face_distance(self.known_faces, face_encoding)
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.known_names[best_match_index]
                    
                    self.face_names.append(name)
            
            # Alternar processamento para melhorar performance
            self.process_frame = not self.process_frame
            
            # Ajustar coordenadas para o frame original
            adjusted_locations = []
            for (top, right, bottom, left) in self.face_locations:
                adjusted_locations.append((top * 2, right * 2, bottom * 2, left * 2))
            
            return adjusted_locations, self.face_names
            
        except Exception as e:
            self.logger.error(f"Erro na detecção de rostos: {e}")
            return [], []
    
    def draw_face_rectangles(self, frame: np.ndarray, face_locations: List, face_names: List) -> np.ndarray:
        """
        Desenha retângulos e nomes nos rostos detectados
        
        Args:
            frame: Frame da imagem
            face_locations: Lista de localizações dos rostos
            face_names: Lista de nomes dos rostos
            
        Returns:
            np.ndarray: Frame com retângulos desenhados
        """
        try:
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Cor verde para conhecidos, vermelha para desconhecidos
                color = (0, 255, 0) if name != "Desconhecido" else (0, 0, 255)
                
                # Desenhar retângulo
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Desenhar fundo para o texto
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                
                # Desenhar texto
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Erro ao desenhar retângulos: {e}")
            return frame
    
    def capture_face(self, name: str, faces_dir: str = "data/faces") -> bool:
        """
        Captura e salva um rosto
        
        Args:
            name: Nome da pessoa
            faces_dir: Diretório para salvar a imagem
            
        Returns:
            bool: True se o rosto foi capturado com sucesso
        """
        try:
            frame = self.get_frame()
            if frame is None:
                self.logger.error("Não foi possível capturar frame da câmera")
                return False
            
            # Converter para RGB para face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if not face_locations:
                self.logger.warning("Nenhum rosto detectado para captura")
                return False
            
            # Usar o primeiro rosto detectado
            top, right, bottom, left = face_locations[0]
            
            # Adicionar margem ao rosto
            margin = 20
            top = max(0, top - margin)
            left = max(0, left - margin)
            bottom = min(frame.shape[0], bottom + margin)
            right = min(frame.shape[1], right + margin)
            
            # Extrair região do rosto
            face_image = frame[top:bottom, left:right]
            
            # Criar diretório se não existir
            if not os.path.exists(faces_dir):
                os.makedirs(faces_dir)
            
            # Salvar imagem
            filename = os.path.join(faces_dir, f"{name}.jpg")
            success = cv2.imwrite(filename, face_image)
            
            if success:
                self.logger.info(f"Rosto de '{name}' salvo em {filename}")
                # Recarregar rostos conhecidos
                self.load_known_faces(faces_dir)
                return True
            else:
                self.logger.error(f"Erro ao salvar imagem de '{name}'")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao capturar rosto: {e}")
            return False
    
    def get_known_faces_info(self) -> List[Tuple[str, str]]:
        """
        Retorna informações dos rostos conhecidos
        
        Returns:
            List: Lista de tuplas (nome, caminho_da_imagem)
        """
        faces_info = []
        faces_dir = "data/faces"
        
        for name in self.known_names:
            image_path = os.path.join(faces_dir, f"{name}.jpg")
            if os.path.exists(image_path):
                faces_info.append((name, image_path))
        
        return faces_info
    
    def delete_face(self, name: str, faces_dir: str = "data/faces") -> bool:
        """
        Remove um rosto conhecido
        
        Args:
            name: Nome da pessoa a ser removida
            faces_dir: Diretório das imagens
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            image_path = os.path.join(faces_dir, f"{name}.jpg")
            
            if os.path.exists(image_path):
                os.remove(image_path)
                self.logger.info(f"Rosto de '{name}' removido")
                # Recarregar rostos conhecidos
                self.load_known_faces(faces_dir)
                return True
            else:
                self.logger.warning(f"Arquivo de '{name}' não encontrado")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao remover rosto de '{name}': {e}")
            return False
    
    def cleanup(self):
        """Libera recursos da câmera"""
        try:
            if self.video_capture is not None:
                self.video_capture.release()
                self.video_capture = None
                self.logger.info("Câmera liberada")
        except Exception as e:
            self.logger.error(f"Erro ao liberar câmera: {e}") 