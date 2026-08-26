# 🗑️ Dashboard de Lixeira Inteligente

Um dashboard interativo desenvolvido com Streamlit para visualização e otimização de rotas de coleta de lixo inteligente.

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes Python)
- **git** (para controle de versão)

## 🚀 Como Iniciar o Projeto

### 1. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd Dashboard
```

### 2. Criar um Ambiente Virtual

```bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
Dashboard/
├── app.py                    # Arquivo principal da aplicação Streamlit
├── requirements.txt          # Dependências do projeto
├── README.md                # Este arquivo
├── .gitignore              # Arquivos e pastas a ignorar no Git
├── services/
│   └── mock_api.py         # API mock para dados de teste
└── utils/
    └── route_optimizer.py  # Utilitário para otimização de rotas
```

## 🛠️ Estrutura das Dependências Principais

- **streamlit** - Framework para criar dashboards web interativos
- **pandas** - Manipulação e análise de dados
- **plotly** - Visualizações interativas e gráficos
- **requests** - Cliente HTTP para consumir APIs
- **numpy** - Cálculos numéricos

## 🎯 Funcionalidades

- Visualização de dados em tempo real
- Mapa interativo com rotas de coleta
- Otimização de rotas para coleta de lixo
- Dashboard com múltiplas visualizações
- Integração com API de dados

## 🔧 Variáveis de Ambiente (Opcional)

Se precisar usar variáveis de ambiente, crie um arquivo `.env` na raiz do projeto:

```
# Exemplo de .env
API_URL=http://localhost:8000
DEBUG=True
```

**Nota:** O arquivo `.env` não será versionado no git por segurança.

## 📝 Notas Importantes

- O arquivo `requirements.txt` contém todas as dependências necessárias
- O ambiente virtual (`venv/`) não é versionado no repositório
- Arquivos de configuração sensíveis (`.env`, credenciais) devem ser adicionados ao `.gitignore`

## 📧 Suporte

Para dúvidas ou problemas, entre em contato através da issue tracker do projeto.

---

**Desenvolvido como parte do TCC**
