# Pipeline de Automação e Integração de Dados (Intranet)

Este repositório contém a primeira fase de uma solução de engenharia de dados desenvolvida para centralizar a extração, o tratamento e o processamento de relatórios provenientes de múltiplos sistemas web internos (restritos à intranet da empresa). 

O projeto tem como objetivo contornar a fragilidade e a limitação de trabalhar com grandes volumes de dados (*Big Data*) diretamente no Excel, otimizando fluxos analíticos e preparando o terreno para a centralização em um Data Warehouse local.

---

## Tecnologias Utilizadas

* **Python 3.x**: Linguagem principal para os scripts de automação.
* **Selenium**: Automação de navegador web para extração dinâmica de relatórios (*web scraping*).
* **Asyncio**: Orquestração assíncrona para execução concorrente de rotinas.
* **Pandas / Openpyxl / Xlrd**: Manipulação e estruturação de dados tabulares.
* **DuckDB *(Em desenvolvimento)***: Futuro Data Warehouse local de alta performance.

---

## Arquitetura da Solução

```text
[ Sistemas Web da Intranet ]
            │
            ▼  (Extração Concorrente via Asyncio + Selenium)
   [ Scripts Python ]
            │
            ▼  (Limpeza, Padronização e Conversão)
[ Datasets Locais / XLSX ] ──> (Próxima Fase) ──> [ Data Warehouse Local (DuckDB) ]
```

1. **Extração Automatizada (Selenium)**: 
   * `extrair_relatorio_jmj.py`: Automatiza o login, navegação em árvore de menus, aplicação de filtros temporais parametrizados e extração de relatórios de beneficiários.
   * `extrair_relatorio_qlik.py`: Realiza a extração automatizada de relatórios e dados de contas médicas a partir de plataformas corporativas.
2. **Orquestração Assíncrona (`asyncio`)**:
   * `orquestrador_tasks.py`: Gerencia a execução simultânea e controlada dos scripts de extração, registrando logs detalhados de auditoria e desempenho (`orquestrador.log`).
3. **Estruturação de Datasets**:
   * Os dados brutos baixados (`.xls` / `.xml`) são tratados, limpos e convertidos programaticamente para o formato `.xlsx`, ficando prontos para consumo analítico.

---

## 📁 Estrutura do Repositório

```text
├── extrair_relatorio_jmj.py    # Script de extração de dados do sistema JMJ
├── extrair_relatorio_qlik.py   # Script de extração de dados de contas médicas / Qlik
├── orquestrador_tasks.py       # Orquestrador assíncrono para execução dos scripts
├── requirements.txt            # Dependências do projeto Python
└── README.md                   # Documentação do projeto
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python instalado na máquina.
* Google Chrome e ChromeDriver compatíveis instalados.
* Acesso à rede/intranet onde os sistemas alvo estão hospedados.

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Instalar as Dependências
Utilize o arquivo `requirements.txt` para instalar as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

### 3. Configurar as Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (utilizando o `.env` como base) e insira as credenciais de acesso aos sistemas:
```env
JMJ_URL=sua_url_aqui
JMJ_USER=seu_usuario_aqui
JMJ_PASS=sua_senha_aqui

QLIK_URL=sua_url_aqui
QLIK_USER=seu_usuario_aqui
QLIK_PASS=sua_senha_aqui
```

### 4. Executar o Orquestrador
Para rodar todas as extrações de forma automatizada e assíncrona:
```bash
python orquestrador_tasks.py
```

---

## Próximos Passos (Em Andamento)

* **Implementação do DuckDB**: Criação de um Data Warehouse local para centralizar e otimizar as consultas SQL sobre os datasets, eliminando gargalos de processamento.
* **Refinamento de ETL**: Expansão das rotinas de transformação diretamente para o banco analítico local.