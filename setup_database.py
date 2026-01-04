"""
Setup do banco de dados SQLite
Cria as tabelas necessárias para o sistema de análise de pagamentos
"""

import sqlite3
import os

def create_database():
    """Cria o banco de dados e todas as tabelas necessárias"""
    
    # Remove banco antigo se existir
    if os.path.exists('fintech_data.db'):
        os.remove('fintech_data.db')
        print("✓ Banco de dados antigo removido")
    
    # Conecta ao banco (cria se não existir)
    conn = sqlite3.connect('fintech_data.db')
    cursor = conn.cursor()
    
    # Tabela de clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        document TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ Tabela 'customers' criada")
    
    # Tabela de merchants (estabelecimentos)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS merchants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        document TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✓ Tabela 'merchants' criada")
    
    # Tabela de transações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        merchant_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        status TEXT NOT NULL,
        transaction_date TIMESTAMP NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (merchant_id) REFERENCES merchants(id)
    )
    ''')
    print("✓ Tabela 'transactions' criada")
    
    # Criar índices para otimizar queries
    cursor.execute('CREATE INDEX idx_transaction_date ON transactions(transaction_date)')
    cursor.execute('CREATE INDEX idx_transaction_status ON transactions(status)')
    cursor.execute('CREATE INDEX idx_transaction_method ON transactions(payment_method)')
    cursor.execute('CREATE INDEX idx_customer_id ON transactions(customer_id)')
    cursor.execute('CREATE INDEX idx_merchant_id ON transactions(merchant_id)')
    print("✓ Índices criados para otimização")
    
    # Criar views úteis
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS daily_summary AS
    SELECT 
        DATE(transaction_date) as date,
        COUNT(*) as total_transactions,
        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
        SUM(CASE WHEN status = 'declined' THEN 1 ELSE 0 END) as declined_count,
        SUM(amount) as total_volume,
        ROUND(AVG(amount), 2) as avg_amount
    FROM transactions
    GROUP BY DATE(transaction_date)
    ORDER BY date DESC
    ''')
    print("✓ View 'daily_summary' criada")
    
    cursor.execute('''
    CREATE VIEW IF NOT EXISTS merchant_performance AS
    SELECT 
        m.id,
        m.name,
        m.category,
        COUNT(t.id) as total_transactions,
        SUM(t.amount) as total_volume,
        ROUND(AVG(t.amount), 2) as avg_ticket,
        SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) as approved_count,
        ROUND(100.0 * SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as approval_rate
    FROM merchants m
    LEFT JOIN transactions t ON m.id = t.merchant_id
    GROUP BY m.id
    ''')
    print("✓ View 'merchant_performance' criada")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados configurado com sucesso!")
    print("📁 Arquivo: fintech_data.db")
    print("\n🎯 Próximo passo: Execute 'python generate_data.py' para gerar dados de exemplo")

if __name__ == "__main__":
    create_database()