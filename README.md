# Sistema de Autenticação Biométrica Facial

> **UNIP - Universidade Paulista**
>
> **Projeto:** Desenvolvimento de Sistema de Identificação e Autenticação Biométrica (Facial)
>
> **Curso:** 5º/6º semestre de Ciência da Computação
>
> **Disciplina:** Atividade Prática Supervisionada - Processamento de Imagens e Visão Computacional

## 📖 Sobre o Projeto

Este projeto consiste no desenvolvimento de uma solução de segurança de alta tecnologia para um cofre fictício de segurança máxima. O sistema utiliza reconhecimento facial em tempo real para identificar e autenticar usuários, garantindo que apenas pessoas autorizadas tenham acesso.

O acesso é controlado por um esquema de três níveis de permissão, simulando um ambiente real onde diferentes usuários possuem diferentes privilégios de acesso.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **OpenCV (`opencv-python`):** Para captura e manipulação de imagem e vídeo em tempo real.
- **face_recognition:** Para detecção de rostos e extração das características faciais (encodings).
- **dlib:** A biblioteca base para o `face_recognition`, contendo os modelos de Machine Learning.
- **Pillow:** Para manipulação de objetos de imagem na interface gráfica.
- **Tkinter:** Para a criação da interface gráfica (GUI) da aplicação.

## 📂 Estrutura do Projeto

O projeto está organizado da seguinte forma para garantir modularidade e clareza:

. ├── config/ # Módulo de configuração centralizado │ ├── init.py │ └── config.py ├── controller/ # Módulo para a lógica de negócio │ ├── init.py │ └── register_user.py ├── dataset/ # Diretório onde as imagens dos usuários são salvas ├── venv/ # Ambiente virtual do Python (ignorado pelo Git) ├── .gitignore # Arquivo para ignorar o venv e outros arquivos ├── main.py # Ponto de entrada principal da aplicação ├── requirements.txt # Lista de dependências do projeto └── README.md # Documentação do projeto

## 🚀 Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto em sua máquina local.

**1. Clone o repositório**

```bash
git clone https://github.com/Filipefilia/aps-6.git
cd aps-6
```

**2. Instale as Dependências de Sistema**

Para que a biblioteca `face_recognition` funcione, é necessário instalar algumas dependências no nível do sistema operacional.

<br>

**_Para Linux (Debian/Ubuntu)_**

```bash
sudo apt-get update && sudo apt-get install -y build-essential cmake python3-dev
```

***Para macOS***

A instalação requer as **Ferramentas de Linha de Comando do Xcode** (para o compilador C++) e o `cmake`.

1.  **Instale as Ferramentas de Linha de Comando do Xcode:**
    ```bash
    xcode-select --install
    ```

2.  **Instale o Homebrew e o CMake:**
    Se você não tiver o [Homebrew](https://brew.sh/), instale-o e depois use-o para instalar o `cmake`.
    ```bash
    # Instala o Homebrew
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Instala o cmake
    brew install cmake
    ```

A biblioteca `dlib` será instalada automaticamente pelo `pip` na próxima etapa. O `cmake` e as ferramentas do Xcode são pré-requisitos para que essa instalação funcione.


**_Para Windows_**

A instalação no Windows é mais complexa e requer um compilador C++ e o CMake.

1.  **Instale o Microsoft C++ Build Tools:**

    - Acesse a [página de downloads do Visual Studio](https://visualstudio.microsoft.com/downloads/).
    - Na seção "Ferramentas para Visual Studio", encontre e baixe o **"Build Tools for Visual Studio"**.
    - Ao executar o instalador, selecione a carga de trabalho **"Desenvolvimento para desktop com C++"** e prossiga com a instalação.

2.  **Instale o CMake:**
    - Baixe o instalador na [página oficial do CMake](https://cmake.org/download/).
    - Durante a instalação, marque a opção **"Add CMake to the system PATH"** para que ele possa ser encontrado pelo `pip`.

Após instalar essas dependências, a instalação dos pacotes Python na próxima etapa deve funcionar corretamente.

**3. Crie e Ative o Ambiente Virtual**

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

_No Linux ou macOS:_

```bash
python3 -m venv venv
source venv/bin/activate
```

_No Windows (PowerShell/CMD):_

```bash
python -m venv venv
.\venv\Scripts\activate
```

**4. Instale as Dependências do Python**

Finalmente, instale todas as bibliotecas Python listadas no `requirements.txt` com um único comando:

```bash
pip install -r requirements.txt
```

▶️ Como Executar
O sistema opera em etapas. A aplicação principal é controlada pelo main.py, que exibirá um menu de opções.

Etapa 1: Cadastrar Novos Usuários

Execute a aplicação principal e escolha a opção para cadastrar usuários. O programa pedirá o nome e o nível de acesso (1, 2 ou 3).

Bash

python main.py

Bash

[UNDER DEVELOPMENT]

```

## 👥 Autores

Nome do Aluno 1 - RA

Nome do Aluno 2 - RA

Nome do Aluno 3 - RA

Pedro Ferreira - T202FE7

Nome do Aluno 5 - RA
```
