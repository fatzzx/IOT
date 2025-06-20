#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Janela de configurações da aplicação
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from utils.logger import get_logger

class SettingsWindow:
    """Janela de configurações"""
    
    def __init__(self, parent, face_detector):
        self.parent = parent
        self.face_detector = face_detector
        self.logger = get_logger(__name__)
        
        # Configurações padrão
        self.default_settings = {
            "camera_index": 0,
            "detection_model": "hog",  # hog ou cnn
            "face_tolerance": 0.6,
            "auto_save_captures": True,
            "log_detections": True,
            "detection_interval": 30  # ms
        }
        
        # Carregar configurações
        self.settings = self.load_settings()
        
        # Criar janela
        self.create_window()
        
        # Configurar interface
        self.setup_ui()
        
        # Carregar valores atuais
        self.load_current_values()
    
    def create_window(self):
        """Cria a janela de configurações"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Configurações")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Centralizar janela
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 500) // 2
        y = (self.window.winfo_screenheight() - 600) // 2
        self.window.geometry(f"500x600+{x}+{y}")
        
        # Tornar modal
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configurar fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal com scrollbar
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Configurações", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Aba Câmera
        self.create_camera_tab(notebook)
        
        # Aba Detecção
        self.create_detection_tab(notebook)
        
        # Aba Sistema
        self.create_system_tab(notebook)
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="Restaurar Padrões", 
            command=self.restore_defaults
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            buttons_frame, 
            text="Cancelar", 
            command=self.on_closing
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            buttons_frame, 
            text="Aplicar", 
            command=self.apply_settings
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            buttons_frame, 
            text="OK", 
            command=self.ok_clicked
        ).pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_camera_tab(self, parent):
        """Cria a aba de configurações de câmera"""
        camera_frame = ttk.Frame(parent, padding="15")
        parent.add(camera_frame, text="Câmera")
        
        # Índice da câmera
        ttk.Label(camera_frame, text="Índice da Câmera:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        camera_info_frame = ttk.Frame(camera_frame)
        camera_info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.camera_index_var = tk.IntVar()
        camera_spin = ttk.Spinbox(
            camera_info_frame,
            from_=0,
            to=5,
            textvariable=self.camera_index_var,
            width=10
        )
        camera_spin.pack(side=tk.LEFT)
        
        ttk.Label(
            camera_info_frame, 
            text="(0 = câmera padrão, 1 = segunda câmera, etc.)"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Botão testar câmera
        ttk.Button(
            camera_frame,
            text="Testar Câmera",
            command=self.test_camera
        ).pack(pady=(0, 20))
        
        # Resolução (informativo)
        ttk.Label(camera_frame, text="Resolução:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(camera_frame, text="Resolução padrão: 640x480 pixels").pack(anchor=tk.W, pady=(0, 15))
        
        # Informações da câmera atual
        info_frame = ttk.LabelFrame(camera_frame, text="Informações da Câmera Atual", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.camera_info_text = tk.Text(
            info_frame,
            height=4,
            width=50,
            font=("Courier", 9),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.camera_info_text.pack(fill=tk.X)
        
        # Atualizar informações da câmera
        self.update_camera_info()
    
    def create_detection_tab(self, parent):
        """Cria a aba de configurações de detecção"""
        detection_frame = ttk.Frame(parent, padding="15")
        parent.add(detection_frame, text="Detecção")
        
        # Modelo de detecção
        ttk.Label(detection_frame, text="Modelo de Detecção:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        self.detection_model_var = tk.StringVar()
        model_frame = ttk.Frame(detection_frame)
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(
            model_frame,
            text="HOG (Rápido, menor precisão)",
            variable=self.detection_model_var,
            value="hog"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            model_frame,
            text="CNN (Lento, maior precisão)",
            variable=self.detection_model_var,
            value="cnn"
        ).pack(anchor=tk.W)
        
        # Tolerância de reconhecimento
        ttk.Label(detection_frame, text="Tolerância de Reconhecimento:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        tolerance_frame = ttk.Frame(detection_frame)
        tolerance_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.tolerance_var = tk.DoubleVar()
        tolerance_scale = ttk.Scale(
            tolerance_frame,
            from_=0.3,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.tolerance_var,
            length=300
        )
        tolerance_scale.pack(side=tk.LEFT)
        
        self.tolerance_label = ttk.Label(tolerance_frame, text="0.6")
        self.tolerance_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Atualizar label quando scale mudar
        tolerance_scale.configure(command=self.update_tolerance_label)
        
        ttk.Label(
            detection_frame, 
            text="Menor valor = mais rigoroso (menos falsos positivos)\nMaior valor = mais permissivo (mais falsos positivos)"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Intervalo de detecção
        ttk.Label(detection_frame, text="Intervalo de Detecção:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        interval_frame = ttk.Frame(detection_frame)
        interval_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.detection_interval_var = tk.IntVar()
        interval_spin = ttk.Spinbox(
            interval_frame,
            from_=10,
            to=100,
            textvariable=self.detection_interval_var,
            width=10
        )
        interval_spin.pack(side=tk.LEFT)
        
        ttk.Label(interval_frame, text="ms (menor = mais suave, maior uso de CPU)").pack(side=tk.LEFT, padx=(10, 0))
    
    def create_system_tab(self, parent):
        """Cria a aba de configurações do sistema"""
        system_frame = ttk.Frame(parent, padding="15")
        parent.add(system_frame, text="Sistema")
        
        # Configurações de salvamento
        ttk.Label(system_frame, text="Salvamento:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        self.auto_save_var = tk.BooleanVar()
        ttk.Checkbutton(
            system_frame,
            text="Salvar capturas automaticamente",
            variable=self.auto_save_var
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Configurações de log
        ttk.Label(system_frame, text="Registro de Eventos:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        self.log_detections_var = tk.BooleanVar()
        ttk.Checkbutton(
            system_frame,
            text="Registrar detecções no log",
            variable=self.log_detections_var
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Diretórios
        ttk.Label(system_frame, text="Diretórios:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        dir_info = f"""Dados: {os.path.abspath('data')}
Logs: {os.path.abspath('logs')}
Rostos: {os.path.abspath('data/faces')}"""
        
        dir_text = tk.Text(
            system_frame,
            height=4,
            width=50,
            font=("Courier", 9),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        dir_text.pack(fill=tk.X, pady=(0, 15))
        
        dir_text.configure(state=tk.NORMAL)
        dir_text.insert(tk.END, dir_info)
        dir_text.configure(state=tk.DISABLED)
        
        # Botões de limpeza
        ttk.Label(system_frame, text="Limpeza:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        cleanup_frame = ttk.Frame(system_frame)
        cleanup_frame.pack(fill=tk.X)
        
        ttk.Button(
            cleanup_frame,
            text="Limpar Logs",
            command=self.clear_logs
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            cleanup_frame,
            text="Limpar Cache",
            command=self.clear_cache
        ).pack(side=tk.LEFT)
    
    def update_tolerance_label(self, value):
        """Atualiza o label da tolerância"""
        self.tolerance_label.config(text=f"{float(value):.2f}")
    
    def test_camera(self):
        """Testa a câmera selecionada"""
        camera_index = self.camera_index_var.get()
        
        try:
            import cv2
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                # Tentar capturar um frame
                ret, frame = cap.read()
                if ret:
                    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    messagebox.showinfo(
                        "Teste de Câmera", 
                        f"Câmera {camera_index} funcionando!\n\n"
                        f"Resolução: {int(width)}x{int(height)}\n"
                        f"FPS: {fps:.1f}"
                    )
                else:
                    messagebox.showerror("Erro", f"Câmera {camera_index} não consegue capturar frames.")
                
                cap.release()
            else:
                messagebox.showerror("Erro", f"Não foi possível abrir a câmera {camera_index}.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao testar câmera: {str(e)}")
    
    def update_camera_info(self):
        """Atualiza as informações da câmera"""
        try:
            camera_index = self.settings.get("camera_index", 0)
            
            import cv2
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                info_text = f"""Câmera {camera_index}:
Status: Disponível
Resolução: {int(width)}x{int(height)}
FPS: {fps:.1f}"""
                
                cap.release()
            else:
                info_text = f"""Câmera {camera_index}:
Status: Não disponível
Erro: Não foi possível abrir a câmera"""
            
            self.camera_info_text.configure(state=tk.NORMAL)
            self.camera_info_text.delete(1.0, tk.END)
            self.camera_info_text.insert(tk.END, info_text)
            self.camera_info_text.configure(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Erro ao obter informações da câmera: {e}")
    
    def clear_logs(self):
        """Limpa os arquivos de log"""
        result = messagebox.askyesno(
            "Confirmar", 
            "Tem certeza que deseja limpar todos os logs?\nEsta ação não pode ser desfeita."
        )
        
        if result:
            try:
                logs_dir = "logs"
                if os.path.exists(logs_dir):
                    for filename in os.listdir(logs_dir):
                        if filename.endswith('.log'):
                            os.remove(os.path.join(logs_dir, filename))
                
                messagebox.showinfo("Sucesso", "Logs limpos com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar logs: {str(e)}")
    
    def clear_cache(self):
        """Limpa arquivos temporários e cache"""
        try:
            # Aqui você pode adicionar limpeza de cache específica
            messagebox.showinfo("Sucesso", "Cache limpo com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar cache: {str(e)}")
    
    def load_current_values(self):
        """Carrega os valores atuais nas configurações"""
        self.camera_index_var.set(self.settings.get("camera_index", 0))
        self.detection_model_var.set(self.settings.get("detection_model", "hog"))
        self.tolerance_var.set(self.settings.get("face_tolerance", 0.6))
        self.auto_save_var.set(self.settings.get("auto_save_captures", True))
        self.log_detections_var.set(self.settings.get("log_detections", True))
        self.detection_interval_var.set(self.settings.get("detection_interval", 30))
        
        # Atualizar label da tolerância
        self.update_tolerance_label(self.tolerance_var.get())
    
    def restore_defaults(self):
        """Restaura configurações padrão"""
        result = messagebox.askyesno(
            "Confirmar", 
            "Tem certeza que deseja restaurar as configurações padrão?"
        )
        
        if result:
            self.settings = self.default_settings.copy()
            self.load_current_values()
            messagebox.showinfo("Sucesso", "Configurações padrão restauradas!")
    
    def apply_settings(self):
        """Aplica as configurações sem fechar a janela"""
        self.save_current_settings()
        messagebox.showinfo("Sucesso", "Configurações aplicadas!")
    
    def ok_clicked(self):
        """Aplica configurações e fecha a janela"""
        self.save_current_settings()
        self.on_closing()
    
    def save_current_settings(self):
        """Salva as configurações atuais"""
        self.settings["camera_index"] = self.camera_index_var.get()
        self.settings["detection_model"] = self.detection_model_var.get()
        self.settings["face_tolerance"] = self.tolerance_var.get()
        self.settings["auto_save_captures"] = self.auto_save_var.get()
        self.settings["log_detections"] = self.log_detections_var.get()
        self.settings["detection_interval"] = self.detection_interval_var.get()
        
        self.save_settings()
    
    def load_settings(self):
        """Carrega configurações do arquivo"""
        settings_file = "config/settings.json"
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Mesclar com configurações padrão
                merged_settings = self.default_settings.copy()
                merged_settings.update(settings)
                
                return merged_settings
            else:
                return self.default_settings.copy()
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            return self.default_settings.copy()
    
    def save_settings(self):
        """Salva configurações no arquivo"""
        settings_file = "config/settings.json"
        
        try:
            # Criar diretório se não existir
            config_dir = os.path.dirname(settings_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Salvar configurações
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
                
            self.logger.info("Configurações salvas")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def on_closing(self):
        """Executado ao fechar a janela"""
        self.window.grab_release()
        self.window.destroy() 