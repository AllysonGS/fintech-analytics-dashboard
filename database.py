"""
Módulo de acesso ao banco de dados
Funções para queries e análises SQL
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DATABASE = 'fintech_data.db'

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    return sqlite3.connect(DATABASE)

def get_daily_summary(days=30):
    """Retorna resumo diário das transações"""
    conn = get_connection()
    
    query = '''
    SELECT 
        DATE(transaction_date) as date,
        COUNT(*) as total_transactions,
        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
        SUM(CASE WHEN status = 'declined' THEN 1 ELSE 0 END) as declined,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) as refunded,
        ROUND(SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END), 2) as total_volume,
        ROUND(AVG(amount), 2) as avg_amount,
        ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate
    FROM transactions
    WHERE transaction_date >= date('now', '-' || ? || ' days')
    GROUP BY DATE(transaction_date)
    ORDER BY date DESC
    '''
    
    df = pd.read_sql_query(query, conn, params=(days,))
    conn.close()
    
    return df

def get_payment_method_stats():
    """Retorna estatísticas por método de pagamento"""
    conn = get_connection()
    
    query = '''
    SELECT 
        payment_method,
        COUNT(*) as total_transactions,
        SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
        ROUND(SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END), 2) as total_volume,
        ROUND(AVG(amount), 2) as avg_amount,
        ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate
    FROM transactions
    GROUP BY payment_method
    ORDER BY total_transactions DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_top_merchants(limit=10):
    """Retorna os top merchants por volume"""
    conn = get_connection()
    
    query = '''
    SELECT 
        m.name,
        m.category,
        COUNT(t.id) as total_transactions,
        ROUND(SUM(t.amount), 2) as total_volume,
        ROUND(AVG(t.amount), 2) as avg_ticket,
        ROUND(100.0 * SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as approval_rate
    FROM merchants m
    JOIN transactions t ON m.id = t.merchant_id
    WHERE t.status = 'approved'
    GROUP BY m.id
    ORDER BY total_volume DESC
    LIMIT ?
    '''
    
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    
    return df

def get_hourly_distribution():
    """Retorna distribuição de transações por hora do dia"""
    conn = get_connection()
    
    query = '''
    SELECT 
        CAST(strftime('%H', transaction_date) AS INTEGER) as hour,
        COUNT(*) as total_transactions,
        ROUND(AVG(amount), 2) as avg_amount
    FROM transactions
    GROUP BY hour
    ORDER BY hour
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_status_distribution():
    """Retorna distribuição por status"""
    conn = get_connection()
    
    query = '''
    SELECT 
        status,
        COUNT(*) as count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 2) as percentage
    FROM transactions
    GROUP BY status
    ORDER BY count DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_category_performance():
    """Retorna performance por categoria de merchant"""
    conn = get_connection()
    
    query = '''
    SELECT 
        m.category,
        COUNT(t.id) as total_transactions,
        ROUND(SUM(CASE WHEN t.status = 'approved' THEN t.amount ELSE 0 END), 2) as total_volume,
        ROUND(AVG(t.amount), 2) as avg_ticket
    FROM merchants m
    JOIN transactions t ON m.id = t.merchant_id
    GROUP BY m.category
    ORDER BY total_volume DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_anomalies(threshold_amount=10000, threshold_frequency=5):
    """
    Detecta transações anômalas
    - Valores muito altos
    - Múltiplas transações em curto período
    """
    conn = get_connection()
    
    # Transações de valor muito alto
    query_high_value = '''
    SELECT 
        t.id,
        t.transaction_date,
        c.name as customer_name,
        m.name as merchant_name,
        t.amount,
        t.payment_method,
        t.status,
        'high_value' as anomaly_type
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    JOIN merchants m ON t.merchant_id = m.id
    WHERE t.amount > ?
    ORDER BY t.amount DESC
    LIMIT 50
    '''
    
    df_high = pd.read_sql_query(query_high_value, conn, params=(threshold_amount,))
    
#   Múltiplas transações do mesmo cliente em 1 hora
    query_frequency = '''
    WITH customer_hourly AS (
    SELECT 
        customer_id,
        strftime('%Y-%m-%d %H', transaction_date) as hour_window,
        COUNT(*) as transactions_count
    FROM transactions
    GROUP BY customer_id, hour_window
    HAVING COUNT(*) >= ?
    )
    SELECT 
    t.customer_id,
    c.name as customer_name,
    ch.hour_window,
    ch.transactions_count,
    'high_frequency' as anomaly_type
    FROM customer_hourly ch
    JOIN customers c ON ch.customer_id = c.id
    JOIN transactions t ON t.customer_id = ch.customer_id 
    AND strftime('%Y-%m-%d %H', t.transaction_date) = ch.hour_window
    GROUP BY t.customer_id, ch.hour_window
    ORDER BY ch.transactions_count DESC
    LIMIT 50
    '''
    
    df_freq = pd.read_sql_query(query_frequency, conn, params=(threshold_frequency,))
    
    conn.close()
    
    return df_high, df_freq

def get_kpis():
    """Retorna KPIs principais do sistema"""
    conn = get_connection()
    
    query = '''
    SELECT 
        COUNT(*) as total_transactions,
        ROUND(SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END), 2) as total_volume,
        ROUND(AVG(amount), 2) as avg_ticket,
        ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate,
        (SELECT COUNT(*) FROM customers) as total_customers,
        (SELECT COUNT(*) FROM merchants) as total_merchants
    FROM transactions
    '''
    
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    
    kpis = {
        'total_transactions': result[0],
        'total_volume': result[1],
        'avg_ticket': result[2],
        'approval_rate': result[3],
        'total_customers': result[4],
        'total_merchants': result[5]
    }
    
    conn.close()
    
    return kpis

def get_transactions_filtered(start_date=None, end_date=None, payment_method=None, status=None, limit=100):
    """Retorna transações com filtros aplicados"""
    conn = get_connection()
    
    query = '''
    SELECT 
        t.id,
        t.transaction_date,
        c.name as customer_name,
        m.name as merchant_name,
        m.category,
        t.amount,
        t.payment_method,
        t.status,
        t.description
    FROM transactions t
    JOIN customers c ON t.customer_id = c.id
    JOIN merchants m ON t.merchant_id = m.id
    WHERE 1=1
    '''
    
    params = []
    
    if start_date:
        query += ' AND DATE(t.transaction_date) >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND DATE(t.transaction_date) <= ?'
        params.append(end_date)
    
    if payment_method and payment_method != 'Todos':
        query += ' AND t.payment_method = ?'
        params.append(payment_method)
    
    if status and status != 'Todos':
        query += ' AND t.status = ?'
        params.append(status)
    
    query += ' ORDER BY t.transaction_date DESC LIMIT ?'
    params.append(limit)
    
    df = pd.read_sql_query(query, conn, params=tuple(params))
    conn.close()
    
    return df