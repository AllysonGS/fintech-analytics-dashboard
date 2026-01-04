# 💰 FinTech Analytics Dashboard

Dashboard de análise de transações financeiras com SQL avançado e visualizações interativas.

## 🎯 Objetivo

Sistema de análise de pagamentos que demonstra:
- SQL avançado (JOINs, CTEs, agregações, window functions)
- Análise de dados em contexto fintech
- Detecção de padrões e anomalias
- Visualizações interativas e KPIs

## 🚀 Funcionalidades

- **Geração de Dados Sintéticos**: 10.000+ transações realistas
- **Análises SQL Avançadas**: Queries complexas para insights
- **Dashboard Interativo**: Interface web com Streamlit
- **Visualizações**: Gráficos de linha, barra, pizza e tabelas
- **Filtros Dinâmicos**: Por data, método de pagamento e status
- **KPIs**: Métricas principais em tempo real
- **Detecção de Anomalias**: Identificação de padrões suspeitos

## 📊 Análises Disponíveis

1. Volume de transações por período
2. Taxa de aprovação por método de pagamento
3. Top merchants por volume
4. Análise de horários de pico
5. Distribuição de valores
6. Padrões de falha/recusa
7. Análise de estornos

## 🛠️ Tecnologias

- **Python 3.8+**
- **SQLite**: Banco de dados
- **Pandas**: Manipulação de dados
- **Streamlit**: Dashboard interativo
- **Plotly**: Visualizações
- **Faker**: Geração de dados sintéticos

## 📦 Instalação

### 1. Clone ou baixe o projeto

### 2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados:
```bash
python setup_database.py
```

### 5. Gere os dados de exemplo:
```bash
python generate_data.py
```

## ▶️ Como Executar

Execute o dashboard:
```bash
streamlit run dashboard.py
```

O dashboard abrirá automaticamente no navegador em `http://localhost:8501`

## 📁 Estrutura do Projeto
```
fintech-analytics-dashboard/
├── README.md              # Documentação
├── requirements.txt       # Dependências Python
├── setup_database.py      # Criação do schema SQL
├── generate_data.py       # Geração de dados sintéticos
├── dashboard.py           # Dashboard Streamlit
├── database.py            # Funções de acesso ao banco
├── queries.sql            # Queries SQL documentadas
└── fintech_data.db        # Banco SQLite (gerado)
```

## 🎓 Conceitos Demonstrados

### SQL Avançado:
- **JOINs**: Relacionamento entre tabelas
- **CTEs (Common Table Expressions)**: Queries organizadas
- **Window Functions**: Análises temporais
- **Agregações**: SUM, AVG, COUNT, GROUP BY
- **Subqueries**: Queries aninhadas
- **Índices**: Otimização de performance

### Análise de Dados:
- Séries temporais
- Estatísticas descritivas
- Detecção de outliers
- Análise de tendências
- Segmentação de dados

### Boas Práticas:
- Código modular e reutilizável
- Documentação clara
- Tratamento de erros
- Queries parametrizadas
- Separação de responsabilidades

## 🔍 Queries SQL Exemplos

### Volume diário de transações:
```sql
SELECT 
    DATE(transaction_date) as date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
    ROUND(AVG(amount), 2) as avg_amount
FROM transactions
GROUP BY DATE(transaction_date)
ORDER BY date DESC;
```

### Top 10 merchants:
```sql
SELECT 
    m.name,
    m.category,
    COUNT(t.id) as total_transactions,
    SUM(t.amount) as total_volume,
    ROUND(AVG(t.amount), 2) as avg_ticket
FROM merchants m
JOIN transactions t ON m.id = t.merchant_id
WHERE t.status = 'approved'
GROUP BY m.id
ORDER BY total_volume DESC
LIMIT 10;
```

## 👨‍💻 Autor

Allyson - [GitHub](https://github.com/AllysonGS)

## 📄 Licença

MIT License - Projeto desenvolvido para fins educacionais e portfólio.
