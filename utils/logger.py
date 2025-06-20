#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de configuração de logging
"""

import logging
import os
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """
    Configura o sistema de logging
    
    Args:
        log_level: Nível de log (default: INFO)
        
    Returns:
        logging.Logger: Logger configurado
    """
    # Criar diretório de logs se não existir
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar nome do arquivo de log com timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_filename = os.path.join(log_dir, f"face_recognition_{timestamp}.log")
    
    # Configurar formato de log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Para mostrar no console também
        ]
    )
    
    logger = logging.getLogger("FaceRecognition")
    logger.info("Sistema de logging configurado")
    
    return logger

def get_logger(name):
    """
    Retorna um logger com o nome especificado
    
    Args:
        name: Nome do logger
        
    Returns:
        logging.Logger: Logger
    """
    return logging.getLogger(name) 