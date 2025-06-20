#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de perfis - janela para visualizar e gerenciar rostos cadastrados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import shutil

from utils.logger import get_logger

class ProfileManager:
    """Janela para gerenciar perfis de rostos"""
    
    def __init__(self, parent, face_detector, refresh_callback):
        self.parent = parent
        self.face_detector = face_detector
        self.refresh_callback = refresh_callback
        self.logger = get_logger(__name__)
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciador de Perfis")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Centralizar janela
        self.center_window()
        
        # Configurar interface
        self.setup_ui()
        
        # Carregar perfis
        self.load_profiles()
        
        # Configurar fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Tornar modal
        self.window.transient(parent)
        self.window.grab_set()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 800) // 2
        y = (self.window.winfo_screenheight() - 600) // 2
        self.window.geometry(f"800x600+{x}+{y}")
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Gerenciador de Perfis", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame superior - controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões de ação
        ttk.Button(
            controls_frame, 
            text="Adicionar da Galeria", 
            command=self.add_from_file
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            controls_frame, 
            text="Exportar Perfis", 
            command=self.export_profiles
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            controls_frame, 
            text="Importar Perfis", 
            command=self.import_profiles
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            controls_frame, 
            text="Atualizar", 
            command=self.load_profiles
        ).pack(side=tk.RIGHT)
        
        # Frame principal com scrollbar
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll com mouse
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Frame inferior - estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estatísticas", padding="10")
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="Carregando...")
        self.stats_label.pack()
    
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_profiles(self):
        """Carrega e exibe os perfis"""
        try:
            # Limpar frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Obter informações dos rostos
            faces_info = self.face_detector.get_known_faces_info()
            
            if not faces_info:
                # Nenhum perfil encontrado
                no_profiles_label = ttk.Label(
                    self.scrollable_frame,
                    text="Nenhum perfil encontrado.\nUse 'Adicionar da Galeria' para importar imagens ou capture rostos na tela principal.",
                    font=("Arial", 12),
                    justify=tk.CENTER
                )
                no_profiles_label.pack(pady=50)
            else:
                # Criar grid de perfis
                self.create_profiles_grid(faces_info)
            
            # Atualizar estatísticas
            self.update_statistics(len(faces_info))
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar perfis: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar perfis: {str(e)}")
    
    def create_profiles_grid(self, faces_info):
        """Cria um grid com os perfis"""
        columns = 3  # 3 perfis por linha
        row = 0
        col = 0
        
        for name, image_path in faces_info:
            # Frame para cada perfil
            profile_frame = ttk.LabelFrame(
                self.scrollable_frame, 
                text=name, 
                padding="10"
            )
            profile_frame.grid(
                row=row, 
                column=col, 
                padx=5, 
                pady=5, 
                sticky=(tk.W, tk.E, tk.N, tk.S)
            )
            
            try:
                # Carregar e redimensionar imagem
                pil_image = Image.open(image_path)
                pil_image = pil_image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Label da imagem
                image_label = ttk.Label(profile_frame)
                image_label.configure(image=photo)
                image_label.image = photo  # Manter referência
                image_label.pack(pady=(0, 10))
                
            except Exception as e:
                self.logger.error(f"Erro ao carregar imagem {image_path}: {e}")
                # Placeholder se não conseguir carregar a imagem
                placeholder_label = ttk.Label(
                    profile_frame, 
                    text="Imagem não\ndisponível", 
                    justify=tk.CENTER
                )
                placeholder_label.pack(pady=(0, 10))
            
            # Informações do perfil
            info_text = f"Nome: {name}\nArquivo: {os.path.basename(image_path)}"
            info_label = ttk.Label(
                profile_frame, 
                text=info_text, 
                justify=tk.CENTER,
                font=("Arial", 9)
            )
            info_label.pack(pady=(0, 10))
            
            # Botões de ação
            buttons_frame = ttk.Frame(profile_frame)
            buttons_frame.pack(fill=tk.X)
            
            # Botão editar
            edit_button = ttk.Button(
                buttons_frame,
                text="Editar",
                command=lambda n=name: self.edit_profile(n),
                width=8
            )
            edit_button.pack(side=tk.LEFT, padx=(0, 5))
            
            # Botão excluir
            delete_button = ttk.Button(
                buttons_frame,
                text="Excluir",
                command=lambda n=name: self.delete_profile(n),
                width=8
            )
            delete_button.pack(side=tk.RIGHT)
            
            # Atualizar posição no grid
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Configurar redimensionamento
        for i in range(columns):
            self.scrollable_frame.columnconfigure(i, weight=1)
    
    def update_statistics(self, total_profiles):
        """Atualiza as estatísticas"""
        stats_text = f"Total de perfis: {total_profiles}"
        if total_profiles > 0:
            faces_dir = "data/faces"
            if os.path.exists(faces_dir):
                total_size = sum(
                    os.path.getsize(os.path.join(faces_dir, f))
                    for f in os.listdir(faces_dir)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                )
                size_mb = total_size / (1024 * 1024)
                stats_text += f" | Espaço usado: {size_mb:.2f} MB"
        
        self.stats_label.config(text=stats_text)
    
    def edit_profile(self, name):
        """Edita um perfil"""
        # Criar janela de edição
        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"Editar Perfil - {name}")
        edit_window.geometry("400x200")
        edit_window.resizable(False, False)
        
        # Centralizar
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() - 400) // 2
        y = (edit_window.winfo_screenheight() - 200) // 2
        edit_window.geometry(f"400x200+{x}+{y}")
        
        # Tornar modal
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            main_frame, 
            text=f"Editando: {name}", 
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 20))
        
        # Campo nome
        ttk.Label(main_frame, text="Novo nome:").pack(anchor=tk.W)
        new_name_entry = ttk.Entry(main_frame, font=("Arial", 10))
        new_name_entry.insert(0, name)
        new_name_entry.pack(fill=tk.X, pady=(5, 20))
        new_name_entry.select_range(0, tk.END)
        new_name_entry.focus()
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_changes():
            new_name = new_name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Aviso", "Digite um nome válido.")
                return
            
            if new_name != name:
                success = self.rename_profile(name, new_name)
                if success:
                    edit_window.destroy()
                    self.load_profiles()
                    self.refresh_callback()
            else:
                edit_window.destroy()
        
        ttk.Button(
            buttons_frame, 
            text="Salvar", 
            command=save_changes
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            buttons_frame, 
            text="Cancelar", 
            command=edit_window.destroy
        ).pack(side=tk.RIGHT)
        
        # Enter para salvar
        edit_window.bind('<Return>', lambda e: save_changes())
    
    def rename_profile(self, old_name, new_name):
        """Renomeia um perfil"""
        try:
            faces_dir = "data/faces"
            old_path = os.path.join(faces_dir, f"{old_name}.jpg")
            new_path = os.path.join(faces_dir, f"{new_name}.jpg")
            
            if os.path.exists(new_path) and new_name != old_name:
                result = messagebox.askyesno(
                    "Confirmar", 
                    f"Já existe um perfil com o nome '{new_name}'.\nDeseja substituir?"
                )
                if not result:
                    return False
            
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                self.logger.info(f"Perfil renomeado de '{old_name}' para '{new_name}'")
                messagebox.showinfo("Sucesso", f"Perfil renomeado para '{new_name}' com sucesso!")
                return True
            else:
                messagebox.showerror("Erro", f"Arquivo do perfil '{old_name}' não encontrado.")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao renomear perfil: {e}")
            messagebox.showerror("Erro", f"Erro ao renomear perfil: {str(e)}")
            return False
    
    def delete_profile(self, name):
        """Exclui um perfil"""
        result = messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o perfil '{name}'?\nEsta ação não pode ser desfeita."
        )
        
        if result:
            success = self.face_detector.delete_face(name)
            if success:
                self.load_profiles()
                self.refresh_callback()
                messagebox.showinfo("Sucesso", f"Perfil '{name}' excluído com sucesso!")
    
    def add_from_file(self):
        """Adiciona perfil a partir de arquivo"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem",
            filetypes=[
                ("Imagens", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if file_path:
            # Pedir nome
            name = self.ask_for_name("Adicionar Perfil", "Nome da pessoa:")
            if name:
                success = self.import_image_file(file_path, name)
                if success:
                    self.load_profiles()
                    self.refresh_callback()
    
    def ask_for_name(self, title, prompt):
        """Solicita nome do usuário"""
        # Criar janela simples para entrada de nome
        name_window = tk.Toplevel(self.window)
        name_window.title(title)
        name_window.geometry("300x150")
        name_window.resizable(False, False)
        
        # Centralizar
        name_window.update_idletasks()
        x = (name_window.winfo_screenwidth() - 300) // 2
        y = (name_window.winfo_screenheight() - 150) // 2
        name_window.geometry(f"300x150+{x}+{y}")
        
        # Tornar modal
        name_window.transient(self.window)
        name_window.grab_set()
        
        result = {"name": None}
        
        # Frame principal
        main_frame = ttk.Frame(name_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(main_frame, text=prompt).pack(pady=(0, 10))
        
        # Entry
        name_entry = ttk.Entry(main_frame, font=("Arial", 10))
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus()
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack()
        
        def ok_clicked():
            name = name_entry.get().strip()
            if name:
                result["name"] = name
                name_window.destroy()
            else:
                messagebox.showwarning("Aviso", "Digite um nome válido.")
        
        def cancel_clicked():
            result["name"] = None
            name_window.destroy()
        
        ttk.Button(buttons_frame, text="OK", command=ok_clicked).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=cancel_clicked).pack(side=tk.LEFT)
        
        # Enter para OK
        name_window.bind('<Return>', lambda e: ok_clicked())
        
        # Aguardar fechamento
        name_window.wait_window()
        
        return result["name"]
    
    def import_image_file(self, file_path, name):
        """Importa um arquivo de imagem"""
        try:
            faces_dir = "data/faces"
            if not os.path.exists(faces_dir):
                os.makedirs(faces_dir)
            
            # Verificar se já existe
            dest_path = os.path.join(faces_dir, f"{name}.jpg")
            if os.path.exists(dest_path):
                result = messagebox.askyesno(
                    "Confirmar", 
                    f"Já existe um perfil com o nome '{name}'.\nDeseja substituir?"
                )
                if not result:
                    return False
            
            # Copiar e converter arquivo
            with Image.open(file_path) as img:
                # Converter para RGB se necessário
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar se muito grande
                max_size = 800
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Salvar como JPEG
                img.save(dest_path, 'JPEG', quality=90)
            
            self.logger.info(f"Imagem importada: {name} de {file_path}")
            messagebox.showinfo("Sucesso", f"Perfil '{name}' adicionado com sucesso!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao importar imagem: {e}")
            messagebox.showerror("Erro", f"Erro ao importar imagem: {str(e)}")
            return False
    
    def export_profiles(self):
        """Exporta todos os perfis para um diretório"""
        dest_dir = filedialog.askdirectory(title="Selecionar Diretório de Destino")
        if dest_dir:
            try:
                faces_dir = "data/faces"
                exported_count = 0
                
                if os.path.exists(faces_dir):
                    for filename in os.listdir(faces_dir):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                            src_path = os.path.join(faces_dir, filename)
                            dest_path = os.path.join(dest_dir, filename)
                            shutil.copy2(src_path, dest_path)
                            exported_count += 1
                
                messagebox.showinfo(
                    "Exportação Concluída", 
                    f"{exported_count} perfis exportados para:\n{dest_dir}"
                )
                
            except Exception as e:
                self.logger.error(f"Erro ao exportar perfis: {e}")
                messagebox.showerror("Erro", f"Erro ao exportar perfis: {str(e)}")
    
    def import_profiles(self):
        """Importa perfis de um diretório"""
        source_dir = filedialog.askdirectory(title="Selecionar Diretório com Imagens")
        if source_dir:
            try:
                imported_count = 0
                faces_dir = "data/faces"
                
                if not os.path.exists(faces_dir):
                    os.makedirs(faces_dir)
                
                for filename in os.listdir(source_dir):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        name = os.path.splitext(filename)[0]
                        src_path = os.path.join(source_dir, filename)
                        
                        if self.import_image_file(src_path, name):
                            imported_count += 1
                
                if imported_count > 0:
                    self.load_profiles()
                    self.refresh_callback()
                
                messagebox.showinfo(
                    "Importação Concluída", 
                    f"{imported_count} perfis importados de:\n{source_dir}"
                )
                
            except Exception as e:
                self.logger.error(f"Erro ao importar perfis: {e}")
                messagebox.showerror("Erro", f"Erro ao importar perfis: {str(e)}")
    
    def on_closing(self):
        """Executado ao fechar a janela"""
        self.window.grab_release()
        self.window.destroy() 