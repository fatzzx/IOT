#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Reconhecimento Facial - Versão Raspberry Pi
Aplicação principal otimizada para ARM64
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adicionar o diretório atual ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window_rpi import MainWindowRPi
from utils.logger import setup_logger

def main():
    """Função principal da aplicação"""
    try:
        # Configurar logging
        logger = setup_logger()
        logger.info("Iniciando aplicação de reconhecimento facial - Versão Raspberry Pi")
        
        # Criar e configurar janela principal
        root = tk.Tk()
        root.title("Sistema de Reconhecimento Facial - Raspberry Pi")
        root.geometry("1000x700")  # Tamanho menor para RPi
        root.minsize(800, 600)
        
        # Centralizar janela na tela
        root.update_idletasks()
        x = (root.winfo_screenwidth() - root.winfo_width()) // 2
        y = (root.winfo_screenheight() - root.winfo_height()) // 2
        root.geometry(f"+{x}+{y}")
        
        # Criar aplicação principal
        app = MainWindowRPi(root)
        
        # Configurar encerramento
        def on_closing():
            try:
                app.cleanup()
                root.destroy()
                logger.info("Aplicação encerrada com sucesso")
            except Exception as e:
                logger.error(f"Erro ao encerrar aplicação: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 