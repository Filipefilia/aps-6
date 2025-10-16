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

* **Python 3.10+**
* **OpenCV (`opencv-python`):** Para captura e manipulação de imagem e vídeo em tempo real.
* **face\_recognition:** Para detecção de rostos e extração das características faciais (encodings).
* **dlib:** A biblioteca base para o `face_recognition`, contendo os modelos de Machine Learning.
* **Pillow:** Para manipulação de objetos de imagem na interface gráfica.
* **Tkinter:** Para a criação da interface gráfica (GUI) da aplicação.

## 📂 Estrutura do Projeto

O projeto está organizado da seguinte forma para garantir modularidade e clareza:

. ├── config/ # Módulo de configuração centralizado │ ├── init.py │ └── config.py ├── controller/ # Módulo para a lógica de negócio │ ├── init.py │ └── register_user.py ├── dataset/ # Diretório onde as imagens dos usuários são salvas ├── venv/ # Ambiente virtual do Python (ignorado pelo Git) ├── .gitignore # Arquivo para ignorar o venv e outros arquivos ├── main.py # Ponto de entrada principal da aplicação ├── requirements.txt # Lista de dependências do projeto └── README.md # Documentação do projeto


## 🚀 Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto em sua máquina local.

**1. Clone o repositório**

```bash
git clone <https://github.com/Filipefilia/aps-6.git>
cd aps-6
2. Crie o Ambiente Virtual

É uma boa prática usar um ambiente virtual para isolar as dependências do projeto.

Bash

python -m venv venv
3. Ative o Ambiente Virtual

A ativação é necessária para garantir que as bibliotecas sejam instaladas no local correto.

No Windows (PowerShell/CMD):

Bash

.\venv\Scripts\activate
No Linux ou macOS:

Bash

source venv/bin/activate
4. Instale as Dependências

O arquivo requirements.txt contém todas as bibliotecas necessárias. Instale-as com um único comando:

Bash

pip install -r requirements.txt
▶️ Como Executar
O sistema opera em etapas. A aplicação principal é controlada pelo main.py, que exibirá um menu de opções.

Etapa 1: Cadastrar Novos Usuários

Execute a aplicação principal e escolha a opção para cadastrar usuários. O programa pedirá o nome e o nível de acesso (1, 2 ou 3).

Bash

python main.py 

Bash

[UNDER DEVELOPMENT]

👥 Autores
Nome do Aluno 1 - RA

Nome do Aluno 2 - RA

Nome do Aluno 3 - RA

Pedro Ferreira - T202FE7

Nome do Aluno 5 - RA