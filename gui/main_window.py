#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Janela principal da aplicação
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time

from core.face_detector import FaceDetector
from gui.profile_manager import ProfileManager
from gui.settings_window import SettingsWindow
from utils.logger import get_logger

class MainWindow:
    """Janela principal da aplicação"""
    
    def __init__(self, root):
        self.root = root
        self.logger = get_logger(__name__)
        
        # Inicializar detector facial
        self.face_detector = FaceDetector()
        
        # Variáveis de controle
        self.camera_active = False
        self.video_thread = None
        
        # Configurar interface
        self.setup_ui()
        
        # Inicializar câmera
        self.initialize_camera()
        
        # Carregar rostos conhecidos
        self.refresh_known_faces()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Criar menu
        self.create_menu()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Painel esquerdo - Controles
        self.create_control_panel(main_frame)
        
        # Painel central - Vídeo
        self.create_video_panel(main_frame)
        
        # Painel direito - Status
        self.create_status_panel(main_frame)
    
    def create_menu(self):
        """Cria o menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Gerenciar Perfis", command=self.open_profile_manager)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Câmera
        camera_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Câmera", menu=camera_menu)
        camera_menu.add_command(label="Iniciar Câmera", command=self.start_camera)
        camera_menu.add_command(label="Parar Câmera", command=self.stop_camera)
        camera_menu.add_separator()
        camera_menu.add_command(label="Configurações", command=self.open_settings)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def create_control_panel(self, parent):
        """Cria o painel de controles"""
        control_frame = ttk.LabelFrame(parent, text="Controles", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Botão iniciar/parar câmera
        self.camera_button = ttk.Button(
            control_frame, 
            text="Iniciar Câmera", 
            command=self.toggle_camera
        )
        self.camera_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=10
        )
        
        # Seção de cadastro
        ttk.Label(control_frame, text="Cadastrar Novo Rosto:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        # Campo nome
        ttk.Label(control_frame, text="Nome:").grid(row=3, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(control_frame, font=("Arial", 10))
        self.name_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botão capturar
        self.capture_button = ttk.Button(
            control_frame, 
            text="Capturar Rosto", 
            command=self.capture_face,
            state=tk.DISABLED
        )
        self.capture_button.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(
            row=6, column=0, sticky=(tk.W, tk.E), pady=10
        )
        
        # Botões de ação
        ttk.Button(
            control_frame, 
            text="Gerenciar Perfis", 
            command=self.open_profile_manager
        ).grid(row=7, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Button(
            control_frame, 
            text="Atualizar Lista", 
            command=self.refresh_known_faces
        ).grid(row=8, column=0, sticky=(tk.W, tk.E), pady=2)
    
    def create_video_panel(self, parent):
        """Cria o painel de vídeo"""
        video_frame = ttk.LabelFrame(parent, text="Câmera", padding="10")
        video_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
        
        # Canvas para o vídeo
        self.video_canvas = tk.Canvas(
            video_frame, 
            width=640, 
            height=480, 
            bg='black',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.video_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Texto placeholder
        self.video_canvas.create_text(
            320, 240, 
            text="Câmera Desligada\nClique em 'Iniciar Câmera' para começar", 
            fill="white",
            font=("Arial", 14),
            justify=tk.CENTER
        )
    
    def create_status_panel(self, parent):
        """Cria o painel de status"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Status da câmera
        ttk.Label(status_frame, text="Status da Câmera:", font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.camera_status = ttk.Label(status_frame, text="Desligada", foreground="red")
        self.camera_status.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Rostos conhecidos
        ttk.Label(status_frame, text="Rostos Conhecidos:", font=("Arial", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.faces_count = ttk.Label(status_frame, text="0 rostos")
        self.faces_count.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Lista de rostos conhecidos
        ttk.Label(status_frame, text="Lista:", font=("Arial", 9, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        
        # Frame para lista com scrollbar
        list_frame = ttk.Frame(status_frame)
        list_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Listbox
        self.faces_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set,
            height=8,
            font=("Arial", 9)
        )
        self.faces_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.faces_listbox.yview)
        
        # Configurar redimensionamento
        status_frame.rowconfigure(5, weight=1)
        
        # Log de eventos
        ttk.Label(status_frame, text="Eventos:", font=("Arial", 9, "bold")).grid(
            row=6, column=0, sticky=tk.W, pady=(10, 5)
        )
        
        # Frame para log
        log_frame = ttk.Frame(status_frame)
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Scrollbar para log
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Text widget para log
        self.log_text = tk.Text(
            log_frame,
            yscrollcommand=log_scrollbar.set,
            height=6,
            width=25,
            font=("Courier", 8),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.config(command=self.log_text.yview)
        
        status_frame.rowconfigure(7, weight=1)
    
    def initialize_camera(self):
        """Inicializa a câmera"""
        success = self.face_detector.initialize_camera()
        if not success:
            self.log_event("Erro: Não foi possível inicializar a câmera")
            messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
    
    def toggle_camera(self):
        """Alterna entre ligar/desligar câmera"""
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()
    
    def start_camera(self):
        """Inicia o feed da câmera"""
        if not self.camera_active:
            success = self.face_detector.initialize_camera()
            if success:
                self.camera_active = True
                self.camera_button.config(text="Parar Câmera")
                self.capture_button.config(state=tk.NORMAL)
                self.camera_status.config(text="Ligada", foreground="green")
                
                # Iniciar thread de vídeo
                self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
                self.video_thread.start()
                
                self.log_event("Câmera iniciada")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar a câmera.")
    
    def stop_camera(self):
        """Para o feed da câmera"""
        if self.camera_active:
            self.camera_active = False
            self.camera_button.config(text="Iniciar Câmera")
            self.capture_button.config(state=tk.DISABLED)
            self.camera_status.config(text="Desligada", foreground="red")
            
            # Limpar canvas
            self.video_canvas.delete("all")
            self.video_canvas.create_text(
                320, 240, 
                text="Câmera Desligada\nClique em 'Iniciar Câmera' para começar", 
                fill="white",
                font=("Arial", 14),
                justify=tk.CENTER
            )
            
            self.log_event("Câmera parada")
    
    def video_loop(self):
        """Loop principal do vídeo"""
        while self.camera_active:
            try:
                frame = self.face_detector.get_frame()
                if frame is not None:
                    # Detectar rostos
                    face_locations, face_names = self.face_detector.detect_faces(frame)
                    
                    # Desenhar retângulos
                    frame_with_faces = self.face_detector.draw_face_rectangles(
                        frame, face_locations, face_names
                    )
                    
                    # Converter para Tkinter
                    self.update_video_display(frame_with_faces)
                    
                    # Log de detecções
                    for name in face_names:
                        if name != "Desconhecido":
                            self.log_event(f"Detectado: {name}")
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                self.logger.error(f"Erro no loop de vídeo: {e}")
                break
    
    def update_video_display(self, frame):
        """Atualiza a exibição do vídeo"""
        try:
            # Converter BGR para RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Redimensionar se necessário
            height, width = rgb_frame.shape[:2]
            if width > 640 or height > 480:
                scale = min(640/width, 480/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                rgb_frame = cv2.resize(rgb_frame, (new_width, new_height))
            
            # Converter para PIL Image
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=pil_image)
            
            # Atualizar canvas
            self.video_canvas.delete("all")
            self.video_canvas.create_image(320, 240, image=photo)
            self.video_canvas.image = photo  # Manter referência
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar display: {e}")
    
    def capture_face(self):
        """Captura um rosto"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Digite um nome para o rosto.")
            return
        
        # Verificar se já existe
        if name in self.face_detector.known_names:
            result = messagebox.askyesno(
                "Confirmar", 
                f"Já existe um rosto cadastrado com o nome '{name}'.\nDeseja substituir?"
            )
            if not result:
                return
        
        success = self.face_detector.capture_face(name)
        if success:
            self.name_entry.delete(0, tk.END)
            self.refresh_known_faces()
            self.log_event(f"Rosto capturado: {name}")
            messagebox.showinfo("Sucesso", f"Rosto de '{name}' cadastrado com sucesso!")
        else:
            messagebox.showerror("Erro", "Não foi possível capturar o rosto. Certifique-se de que há um rosto visível na câmera.")
    
    def refresh_known_faces(self):
        """Atualiza a lista de rostos conhecidos"""
        count = self.face_detector.load_known_faces()
        self.faces_count.config(text=f"{count} rostos")
        
        # Atualizar listbox
        self.faces_listbox.delete(0, tk.END)
        for name in self.face_detector.known_names:
            self.faces_listbox.insert(tk.END, name)
        
        self.log_event(f"Lista atualizada: {count} rostos")
    
    def log_event(self, message):
        """Adiciona evento ao log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def open_profile_manager(self):
        """Abre o gerenciador de perfis"""
        ProfileManager(self.root, self.face_detector, self.refresh_known_faces)
    
    def open_settings(self):
        """Abre as configurações"""
        SettingsWindow(self.root, self.face_detector)
    
    def show_about(self):
        """Mostra informações sobre a aplicação"""
        about_text = """Sistema de Reconhecimento Facial
Versão 2.0

Desenvolvido com:
• OpenCV
• face_recognition
• tkinter
• PIL/Pillow

Funcionalidades:
• Detecção em tempo real
• Cadastro de rostos
• Gerenciamento de perfis
• Interface moderna

© 2024"""
        messagebox.showinfo("Sobre", about_text)
    
    def cleanup(self):
        """Limpa recursos antes de fechar"""
        self.stop_camera()
        self.face_detector.cleanup()
        self.logger.info("Recursos liberados") 