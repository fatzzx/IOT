# Instalação no Raspberry Pi

Este guia mostra como instalar o Sistema de Reconhecimento Facial no Raspberry Pi, evitando os problemas de compilação do `dlib`.

## 🍓 Versão Raspberry Pi

A versão para Raspberry Pi usa uma abordagem diferente:

- **OpenCV** para detecção facial (Haar Cascades)
- **LBPH Face Recognizer** para reconhecimento
- **Sem dlib/face_recognition** (evita problemas de compilação)
- **Otimizada** para ARM64 e recursos limitados

## 📋 Pré-requisitos

### Sistema Operativo

- Raspberry Pi OS (64-bit recomendado)
- Python 3.8 ou superior
- Câmera USB ou Raspberry Pi Camera

### Dependências do Sistema

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências de sistema
sudo apt install -y python3-pip python3-venv
sudo apt install -y python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y python3-dev build-essential

# Para Raspberry Pi Camera (opcional)
sudo apt install -y python3-picamera2
```

## 🔧 Instalação

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd sistema-reconhecimento-facial
```

### 2. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências (versão RPi)

```bash
# Usar o arquivo específico para Raspberry Pi
pip install -r requirements-rpi.txt
```

### 4. Verificar instalação do OpenCV

```bash
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

### 5. Executar a aplicação

```bash
# Versão otimizada para Raspberry Pi
python3 main_rpi.py
```

## ⚙️ Configuração da Câmera

### Câmera USB

- Conecte a câmera USB
- Verifique se aparece em `/dev/video0`
- Use índice 0 nas configurações

### Raspberry Pi Camera

```bash
# Habilitar camera interface
sudo raspi-config
# Interface Options > Camera > Enable

# Testar camera
libcamera-hello --preview-duration 5000
```

## 🔧 Solução de Problemas

### Erro "No module named 'cv2'"

```bash
# Instalar OpenCV via apt (mais estável no RPi)
sudo apt install python3-opencv

# Ou via pip
pip install opencv-python==4.6.0.66
```

### Erro de câmera

```bash
# Verificar dispositivos de vídeo
ls /dev/video*

# Dar permissões ao usuário
sudo usermod -a -G video $USER
# Reiniciar para aplicar
```

### Performance lenta

- Use resolução menor (320x240 já é padrão)
- Feche outros aplicativos
- Considere overclocking:

```bash
sudo nano /boot/config.txt
# Adicionar:
# arm_freq=1750
# gpu_freq=600
```

### Erro de memória

```bash
# Aumentar swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📊 Diferenças da Versão RPi

### Algoritmos Utilizados

- **Detecção**: Haar Cascade Classifiers
- **Reconhecimento**: LBPH (Local Binary Patterns Histograms)
- **Precisão**: Boa para uso geral, menor que dlib
- **Performance**: Otimizada para ARM64

### Limitações

- Menor precisão que face_recognition/dlib
- Mais sensível à iluminação
- Requer retreinamento ao adicionar faces

### Vantagens

- Instalação simples (sem compilação)
- Menor uso de recursos
- Funciona bem no Raspberry Pi
- Interface idêntica à versão completa

## 🎯 Dicas de Uso

### Melhor Qualidade

- Boa iluminação é essencial
- Posicione o rosto de frente para a câmera
- Evite sombras fortes
- Cadastre múltiplas fotos da mesma pessoa

### Performance

- Feche outros aplicativos durante uso
- Use cartão SD rápido (Classe 10+)
- Considere cooling para o RPi

### Backup

```bash
# Backup dos perfis
cp -r data/faces ~/backup_faces_$(date +%Y%m%d)

# Restore
cp -r ~/backup_faces_YYYYMMDD data/faces
```

## 🔄 Atualizações

### Atualizar código

```bash
git pull origin main
pip install -r requirements-rpi.txt --upgrade
```

### Migrar da versão completa

Se você tem perfis da versão completa:

```bash
# Copiar imagens existentes
cp -r data/faces/* ./data/faces/

# Executar retreinamento
python3 main_rpi.py
# Ir em Controles > Retreinar Modelo
```

## 📝 Notas

- Esta versão é otimizada especificamente para Raspberry Pi
- A interface é idêntica à versão completa
- A precisão é suficiente para a maioria dos casos de uso
- Para máxima precisão, use a versão completa em PC

## 🚀 Next Steps

Após a instalação bem-sucedida:

1. Teste a câmera
2. Cadastre alguns rostos
3. Ajuste configurações conforme necessário
4. Configure auto-inicialização se desejado

```bash
# Auto-inicialização (opcional)
nano ~/.bashrc
# Adicionar ao final:
# cd ~/sistema-reconhecimento-facial && source venv/bin/activate && python3 main_rpi.py
```
