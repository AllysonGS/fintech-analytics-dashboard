"""
Gerador de dados sintéticos para o sistema de análise de pagamentos
Cria dados realistas de clientes, merchants e transações
"""

import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Inicializa Faker com locale brasileiro
fake = Faker('pt_BR')

# Configurações
NUM_CUSTOMERS = 500
NUM_MERCHANTS = 50
NUM_TRANSACTIONS = 10000

# Categorias de merchants
CATEGORIES = [
    'Supermercado', 'Restaurante', 'Farmácia', 'Posto de Gasolina',
    'Loja de Roupas', 'Eletrônicos', 'Padaria', 'Livraria',
    'Academia', 'Pet Shop', 'Cosméticos', 'Material de Construção'
]

# Métodos de pagamento
PAYMENT_METHODS = ['pix', 'credit_card', 'debit_card', 'boleto']

# Status das transações
STATUSES = ['approved', 'declined', 'pending', 'refunded']

# Pesos para distribuição realista
STATUS_WEIGHTS = [0.85, 0.10, 0.03, 0.02]  # 85% aprovado, 10% recusado, etc.
METHOD_WEIGHTS = [0.40, 0.35, 0.20, 0.05]  # PIX mais usado

def generate_customers(cursor):
    """Gera clientes sintéticos"""
    print(f"Gerando {NUM_CUSTOMERS} clientes...")
    
    customers = []
    for i in range(NUM_CUSTOMERS):
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        document = fake.cpf()
        
        try:
            cursor.execute('''
                INSERT INTO customers (name, email, phone, document)
                VALUES (?, ?, ?, ?)
            ''', (name, email, phone, document))
            customers.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            # Se houver duplicata, tenta novamente
            continue
    
    print(f"✓ {len(customers)} clientes criados")
    return customers

def generate_merchants(cursor):
    """Gera estabelecimentos comerciais sintéticos"""
    print(f"Gerando {NUM_MERCHANTS} merchants...")
    
    merchants = []
    for i in range(NUM_MERCHANTS):
        name = fake.company()
        category = random.choice(CATEGORIES)
        document = fake.cnpj()
        
        try:
            cursor.execute('''
                INSERT INTO merchants (name, category, document)
                VALUES (?, ?, ?)
            ''', (name, category, document))
            merchants.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            continue
    
    print(f"✓ {len(merchants)} merchants criados")
    return merchants

def generate_transactions(cursor, customer_ids, merchant_ids):
    """Gera transações sintéticas realistas"""
    print(f"Gerando {NUM_TRANSACTIONS} transações...")
    
    # Data de início (90 dias atrás)
    start_date = datetime.now() - timedelta(days=90)
    
    transactions_created = 0
    
    for i in range(NUM_TRANSACTIONS):
        customer_id = random.choice(customer_ids)
        merchant_id = random.choice(merchant_ids)
        
        # Gera valor realista (R$ 10 a R$ 5000)
        # Distribuição mais concentrada em valores menores
        if random.random() < 0.7:
            amount = round(random.uniform(10, 200), 2)
        elif random.random() < 0.9:
            amount = round(random.uniform(200, 1000), 2)
        else:
            amount = round(random.uniform(1000, 5000), 2)
        
        # Método de pagamento (com pesos realistas)
        payment_method = random.choices(PAYMENT_METHODS, weights=METHOD_WEIGHTS)[0]
        
        # Status (com pesos realistas)
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        
        # Data da transação (distribuída nos últimos 90 dias)
        # Mais transações em dias recentes
        days_ago = int(random.triangular(0, 90, 0))
        transaction_date = start_date + timedelta(
            days=days_ago,
            hours=random.randint(6, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        # Descrição
        descriptions = [
            'Compra em estabelecimento',
            'Pagamento de serviço',
            'Compra online',
            'Assinatura mensal',
            'Recarga',
            'Transferência'
        ]
        description = random.choice(descriptions)
        
        cursor.execute('''
            INSERT INTO transactions 
            (customer_id, merchant_id, amount, payment_method, status, transaction_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, merchant_id, amount, payment_method, status, transaction_date, description))
        
        transactions_created += 1
        
        # Progresso
        if (i + 1) % 1000 == 0:
            print(f"  → {i + 1}/{NUM_TRANSACTIONS} transações criadas...")
    
    print(f"✓ {transactions_created} transações criadas")

def generate_anomalies(cursor, customer_ids, merchant_ids):
    """Gera algumas transações suspeitas/anômalas para demonstrar detecção"""
    print("\nGerando transações anômalas para demonstração...")
    
    # Transação de valor muito alto
    cursor.execute('''
        INSERT INTO transactions 
        (customer_id, merchant_id, amount, payment_method, status, transaction_date, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        random.choice(customer_ids),
        random.choice(merchant_ids),
        25000.00,  # Valor suspeito
        'credit_card',
        'approved',
        datetime.now() - timedelta(hours=2),
        'Compra de alto valor'
    ))
    
    # Múltiplas transações do mesmo cliente em curto período
    customer_id = random.choice(customer_ids)
    base_time = datetime.now() - timedelta(hours=1)
    
    for i in range(10):
        cursor.execute('''
            INSERT INTO transactions 
            (customer_id, merchant_id, amount, payment_method, status, transaction_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id,
            random.choice(merchant_ids),
            round(random.uniform(100, 500), 2),
            random.choice(PAYMENT_METHODS),
            'approved',
            base_time + timedelta(minutes=i*2),
            'Compra suspeita - múltiplas transações'
        ))
    
    print("✓ Anomalias geradas para demonstração")

def print_statistics(cursor):
    """Imprime estatísticas dos dados gerados"""
    print("\n" + "="*50)
    print("📊 ESTATÍSTICAS DOS DADOS GERADOS")
    print("="*50)
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"\n👥 Clientes: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM merchants")
    print(f"🏪 Merchants: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    print(f"💳 Transações: {cursor.fetchone()[0]}")
    
    # Volume total
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE status = 'approved'")
    total_volume = cursor.fetchone()[0]
    print(f"💰 Volume Total Aprovado: R$ {total_volume:,.2f}")
    
    # Por método de pagamento
    print("\n📱 Transações por método:")
    cursor.execute('''
        SELECT payment_method, COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 1)
        FROM transactions
        GROUP BY payment_method
        ORDER BY COUNT(*) DESC
    ''')
    for method, count, pct in cursor.fetchall():
        print(f"  • {method}: {count} ({pct}%)")
    
    # Por status
    print("\n✅ Transações por status:")
    cursor.execute('''
        SELECT status, COUNT(*), ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 1)
        FROM transactions
        GROUP BY status
        ORDER BY COUNT(*) DESC
    ''')
    for status, count, pct in cursor.fetchall():
        print(f"  • {status}: {count} ({pct}%)")
    
    print("\n" + "="*50)

def main():
    """Função principal"""
    print("🚀 Iniciando geração de dados sintéticos...\n")
    
    # Conecta ao banco
    conn = sqlite3.connect('fintech_data.db')
    cursor = conn.cursor()
    
    try:
        # Limpa dados antigos
        print("Limpando dados antigos...")
        cursor.execute('DELETE FROM transactions')
        cursor.execute('DELETE FROM merchants')
        cursor.execute('DELETE FROM customers')
        conn.commit()
        print("✓ Dados antigos removidos\n")
        
        # Gera novos dados
        customer_ids = generate_customers(cursor)
        merchant_ids = generate_merchants(cursor)
        generate_transactions(cursor, customer_ids, merchant_ids)
        generate_anomalies(cursor, customer_ids, merchant_ids)
        
        # Commit final
        conn.commit()
        
        # Mostra estatísticas
        print_statistics(cursor)
        
        print("\n✅ Dados gerados com sucesso!")
        print("\n🎯 Próximo passo: Execute 'streamlit run dashboard.py' para visualizar o dashboard")
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar dados: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()