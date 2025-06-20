#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de detecção facial para Raspberry Pi
Versão simplificada usando apenas OpenCV (sem dlib/face_recognition)
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import os
import pickle
from utils.logger import get_logger

class FaceDetectorRPi:
    """Classe responsável pela detecção facial no Raspberry Pi usando OpenCV"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.video_capture = None
        self.known_faces = []
        self.known_names = []
        self.face_cascade = None
        self.face_recognizer = None
        
        # Inicializar classificadores OpenCV
        self.initialize_opencv_classifiers()
        
    def initialize_opencv_classifiers(self):
        """Inicializa os classificadores do OpenCV"""
        try:
            # Carregar classificador Haar Cascade para detecção de rostos
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                self.logger.error("Erro ao carregar classificador Haar Cascade")
                return False
            
            # Inicializar reconhecedor LBPH (Local Binary Patterns Histograms)
            self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            self.logger.info("Classificadores OpenCV inicializados com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar classificadores OpenCV: {e}")
            return False
    
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
                
            # Configurar resolução menor para melhor performance no RPi
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            
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
            
            # Verificar se existe arquivo de treinamento
            model_path = os.path.join(faces_dir, "trained_model.yml")
            labels_path = os.path.join(faces_dir, "labels.pkl")
            
            if os.path.exists(model_path) and os.path.exists(labels_path):
                # Carregar modelo treinado
                self.face_recognizer.read(model_path)
                
                with open(labels_path, 'rb') as f:
                    self.known_names = pickle.load(f)
                
                self.logger.info(f"Modelo treinado carregado: {len(self.known_names)} rostos")
                return len(self.known_names)
            else:
                # Treinar novo modelo
                return self.train_model(faces_dir)
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar rostos conhecidos: {e}")
            return 0
    
    def train_model(self, faces_dir: str) -> int:
        """
        Treina o modelo de reconhecimento com as imagens disponíveis
        
        Args:
            faces_dir: Diretório com as imagens
            
        Returns:
            int: Número de faces treinadas
        """
        try:
            faces = []
            labels = []
            names = []
            label_id = 0
            
            for filename in os.listdir(faces_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        name = os.path.splitext(filename)[0]
                        image_path = os.path.join(faces_dir, filename)
                        
                        # Carregar e processar imagem
                        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                        
                        if image is None:
                            continue
                            
                        # Detectar rosto na imagem
                        detected_faces = self.face_cascade.detectMultiScale(
                            image, 
                            scaleFactor=1.1, 
                            minNeighbors=5,
                            minSize=(30, 30)
                        )
                        
                        if len(detected_faces) > 0:
                            # Usar o primeiro rosto detectado
                            (x, y, w, h) = detected_faces[0]
                            face_roi = image[y:y+h, x:x+w]
                            
                            # Redimensionar para tamanho padrão
                            face_roi = cv2.resize(face_roi, (100, 100))
                            
                            faces.append(face_roi)
                            labels.append(label_id)
                            names.append(name)
                            
                            self.logger.debug(f"Rosto processado: {name}")
                        
                        label_id += 1
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar {filename}: {e}")
            
            if len(faces) > 0:
                # Treinar o reconhecedor
                self.face_recognizer.train(faces, np.array(labels))
                
                # Salvar modelo treinado
                model_path = os.path.join(faces_dir, "trained_model.yml")
                labels_path = os.path.join(faces_dir, "labels.pkl")
                
                self.face_recognizer.save(model_path)
                
                with open(labels_path, 'wb') as f:
                    pickle.dump(names, f)
                
                self.known_names = names
                self.logger.info(f"Modelo treinado com {len(faces)} rostos")
                return len(faces)
            else:
                self.logger.warning("Nenhum rosto válido encontrado para treinamento")
                return 0
                
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo: {e}")
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
            # Converter para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostos
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_locations = []
            face_names = []
            
            for (x, y, w, h) in faces:
                # Converter coordenadas para formato compatível
                face_locations.append((y, x + w, y + h, x))
                
                # Reconhecer rosto se modelo estiver treinado
                if self.face_recognizer is not None and len(self.known_names) > 0:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    
                    # Predizer
                    label, confidence = self.face_recognizer.predict(face_roi)
                    
                    # Verificar confiança (menor é melhor no LBPH)
                    if confidence < 100:  # Threshold ajustável
                        if label < len(self.known_names):
                            name = self.known_names[label]
                        else:
                            name = "Desconhecido"
                    else:
                        name = "Desconhecido"
                else:
                    name = "Desconhecido"
                
                face_names.append(name)
            
            return face_locations, face_names
            
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
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.4, (255, 255, 255), 1)
            
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
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostos
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                self.logger.warning("Nenhum rosto detectado para captura")
                return False
            
            # Usar o primeiro rosto detectado
            (x, y, w, h) = faces[0]
            
            # Adicionar margem
            margin = 20
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(frame.shape[1] - x, w + 2 * margin)
            h = min(frame.shape[0] - y, h + 2 * margin)
            
            # Extrair região do rosto
            face_image = frame[y:y+h, x:x+w]
            
            # Criar diretório se não existir
            if not os.path.exists(faces_dir):
                os.makedirs(faces_dir)
            
            # Salvar imagem
            filename = os.path.join(faces_dir, f"{name}.jpg")
            success = cv2.imwrite(filename, face_image)
            
            if success:
                self.logger.info(f"Rosto de '{name}' salvo em {filename}")
                # Retreinar modelo
                self.train_model(faces_dir)
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
                
                # Remover modelo antigo e retreinar
                model_path = os.path.join(faces_dir, "trained_model.yml")
                labels_path = os.path.join(faces_dir, "labels.pkl")
                
                if os.path.exists(model_path):
                    os.remove(model_path)
                if os.path.exists(labels_path):
                    os.remove(labels_path)
                
                # Retreinar modelo
                self.train_model(faces_dir)
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