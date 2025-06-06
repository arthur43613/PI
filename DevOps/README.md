## Pré-requisitos

* **Docker**: Certifique-se de que o Docker está instalado e em execução no seu sistema.
* **Docker Compose**: Certifique-se de que o Docker Compose está instalado.
* **Git**: Certifique-se de que o Git está instalado.
* **Conexão com a Internet**: Necessária para baixar imagens e clonar repositórios.

├── data/                     # Dados compartilhados (volume para /app/data nos serviços)
│   ├── datalake/
│   │   ├── dim_mililitro.csv
│   │   ├── dim_vazao.csv
│   │   └── fato.csv
│   ├── dadosAlagamentoPI.csv
│   └── dadosCorretosPI.csv
├── dash-app/                 # Contexto de build para o serviço dash-app
│   ├── assets/
│   ├── pages/
│   ├── dash_app.py
│   └── requirements.txt
├── python-generator/         # Contexto de build (se aplicável) para python-generator
│   └── script.py
├── r-cleaner/                # Contexto de build (se aplicável) para r-cleaner
│   └── dadosAlagamento.R
├── PI/                       # Diretório para clone do Git (volume)
├── docker-compose.yml        # Arquivo principal do Docker Compose
└── README.md                 # Este arquivo

---
## Comandos para Configuração e Execução

### 1. Clonar o Repositório do Projeto (Se Necessário)

Se você ainda não tem os arquivos do projeto localmente:
  git clone https://github.com/CarlosEducg11/jenkins-web-pipeline.git
  cd <jenkins-web-pipeline>

### 2. Construir e Enviar Imagens Docker para o Docker Hub (Opcional)

Os serviços são definidos para usar imagens do Docker Hub (ex: educg11/python-generator:latest). Se você modificar os serviços ou quiser usar seu próprio repositório, precisará construir e enviar as imagens. Substitua seunomeusuario pelo seu nome de usuário do Docker Hub.

  docker build -t educg11/python-generator:latest ./python-generator
  docker push  educg11/python-generator:latest

  docker build -t  educg11/r-cleaner:latest ./r-cleaner
  docker push  educg11/r-cleaner:latest

  docker build -t  educg11/dash-app:latest ./dash-app
  docker push educg11/dash-app:latest

  docker compose up --build 

### 3. Comandos para Configuração do Jenkins

  ls -ln /var/run/docker.sock (Anote o GID, em caso de erro altere diretamente no Dockerfile principal)

  docker build -t custom-jenkins:latest .

  docker run -d \
    -p 8080:8080 -p 50000:50000 \
    --name jenkins \
    -v jenkins_home:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --group-add $(stat -c '%g' /var/run/docker.sock) \
    custom-jenkins:latest

  ### Obter Senha Inicial de Admin do Jenkins: 

  docker exec -it jenkins bash
  cat /var/jenkins_home/secrets/initialAdminPassword
  exit

  URL: http://localhost:8080

  ### Crie a pipeline no Jenkins:

  Criar Novo Item:

      No painel do Jenkins, clique em "New Item" (Novo Item) ou "Create a job" (Criar um job).
      Digite um nome para o seu pipeline (ex: pipeline).
      Selecione "Pipeline" como o tipo de projeto e clique em "OK".

  Configurar o Pipeline:

      Na página de configuração do job, vá até a seção "Pipeline".
      Definition (Definição): Escolha "Pipeline script from SCM" (Script de Pipeline do SCM). Esta é a prática recomendada, pois versiona seu pipeline junto com seu código.
          SCM: Selecione "Git".
          Repositories (Repositórios):
              Repository URL (URL do Repositório): Insira a URL do repositório Git. Para este projeto: https://github.com/CarlosEducg11/jenkins-web-pipeline.git (se ele contiver um Jenkinsfile).
              Selecione a branch "Master"

        Salvar: Clique em "Save" (Salvar).

  Após salvar, na página principal do pipeline, clique em "Build Now" (Construir agora) no menu à esquerda.