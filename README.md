# Sistema de Reconhecimento Facial

Um sistema completo de reconhecimento facial desenvolvido em Python com interface gráfica moderna e funcionalidades avançadas.

## 🚀 Funcionalidades

### ✨ Principais Recursos

- **Detecção em tempo real**: Reconhecimento facial via webcam
- **Cadastro de rostos**: Captura e armazenamento de novos perfis
- **Gerenciamento de perfis**: Interface completa para editar, excluir e organizar rostos
- **Configurações avançadas**: Personalização de parâmetros de detecção
- **Interface moderna**: Design intuitivo e responsivo
- **Logs detalhados**: Sistema de logging para debug e monitoramento

### 🛠️ Funcionalidades Técnicas

- Separação de responsabilidades em módulos
- Tratamento robusto de erros
- Sistema de configuração persistente
- Suporte a múltiplas câmeras
- Importação/exportação de perfis
- Otimização de performance

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Webcam funcionando
- Windows 10/11 (testado)

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd sistema-reconhecimento-facial
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
venv\\Scripts\\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
python main.py
```

## 📁 Estrutura do Projeto

```
sistema-reconhecimento-facial/
├── main.py                    # Ponto de entrada da aplicação
├── requirements.txt           # Dependências
├── README.md                 # Este arquivo
│
├── core/                     # Módulos principais
│   ├── __init__.py
│   └── face_detector.py      # Lógica de detecção facial
│
├── gui/                      # Interface gráfica
│   ├── __init__.py
│   ├── main_window.py        # Janela principal
│   ├── profile_manager.py    # Gerenciador de perfis
│   └── settings_window.py    # Configurações
│
├── utils/                    # Utilitários
│   ├── __init__.py
│   └── logger.py             # Sistema de logging
│
├── data/                     # Dados da aplicação
│   └── faces/                # Imagens dos rostos
│
├── logs/                     # Arquivos de log
│
└── config/                   # Configurações
    └── settings.json         # Configurações da aplicação
```

## 🎯 Como Usar

### 1. Iniciando a Aplicação

- Execute `python main.py`
- A janela principal será aberta
- Clique em "Iniciar Câmera" para começar

### 2. Cadastrando Rostos

- Digite um nome no campo "Nome"
- Posicione o rosto na frente da câmera
- Clique em "Capturar Rosto"
- O rosto será automaticamente salvo e reconhecido

### 3. Gerenciando Perfis

- Acesse "Arquivo" → "Gerenciar Perfis"
- Visualize todos os rostos cadastrados
- Edite nomes, exclua perfis ou adicione novos
- Importe/exporte perfis conforme necessário

### 4. Configurações

- Acesse "Câmera" → "Configurações"
- Ajuste parâmetros de detecção
- Configure câmera e tolerância
- Personalize comportamento do sistema

## ⚙️ Configurações Disponíveis

### Câmera

- **Índice da câmera**: Escolha qual câmera usar (0, 1, 2...)
- **Teste de câmera**: Verificar se a câmera está funcionando

### Detecção

- **Modelo de detecção**: HOG (rápido) ou CNN (preciso)
- **Tolerância**: Ajusta sensibilidade do reconhecimento
- **Intervalo**: Controla frequência de processamento

### Sistema

- **Auto-salvamento**: Salvar capturas automaticamente
- **Logs**: Registrar eventos e detecções
- **Limpeza**: Gerenciar arquivos temporários

## 🔍 Solução de Problemas

### Câmera não funciona

- Verifique se a câmera está conectada
- Teste diferentes índices de câmera (0, 1, 2...)
- Feche outros aplicativos que possam estar usando a câmera

### Detecção imprecisa

- Ajuste a tolerância de reconhecimento
- Verifique iluminação do ambiente
- Recadastre rostos com melhor qualidade

### Erro de dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Performance lenta

- Use modelo HOG ao invés de CNN
- Aumente o intervalo de detecção
- Feche outros aplicativos pesados

## 📊 Especificações Técnicas

### Dependências Principais

- **OpenCV 4.8.1**: Processamento de imagem
- **face_recognition 1.3.0**: Algoritmos de reconhecimento
- **dlib 19.24.2**: Detecção de características faciais
- **Pillow 10.0.1**: Manipulação de imagens
- **tkinter**: Interface gráfica (built-in Python)

### Formato de Dados

- **Imagens**: JPEG, PNG (convertidas para JPEG)
- **Configurações**: JSON
- **Logs**: Arquivos de texto com timestamp

### Performance

- **Resolução**: 640x480 pixels (padrão)
- **FPS**: ~30 fps (dependendo do hardware)
- **Modelos**: HOG (~10ms/frame), CNN (~100ms/frame)

## 🛡️ Segurança e Privacidade

- Todas as imagens são armazenadas localmente
- Nenhum dado é enviado para servidores externos
- Logs não contêm informações pessoais sensíveis
- Configurações podem ser resetadas a qualquer momento

## 🔄 Versionamento

### Versão 2.0 - Atual

- Arquitetura modular completamente reescrita
- Interface gráfica moderna
- Gerenciamento avançado de perfis
- Sistema de configurações robusto
- Logs detalhados e debugging

### Versão 1.0 - Legada

- Código monolítico original
- Interface básica
- Funcionalidades limitadas

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👥 Autor

Desenvolvido como uma aplicação de reconhecimento facial moderna e robusta.

## 📞 Suporte

Para suporte e dúvidas:

- Abra uma issue no repositório
- Consulte a documentação técnica
- Verifique os logs da aplicação

---

**Nota**: Este sistema é destinado para uso educacional e de desenvolvimento. Para uso comercial ou em ambientes de produção, considere implementar medidas adicionais de segurança e compliance.
