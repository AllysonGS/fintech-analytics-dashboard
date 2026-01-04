-- ===================================
-- QUERIES SQL - FINTECH ANALYTICS
-- ===================================
-- Coleção de queries SQL úteis para análise de dados de pagamentos
-- Demonstra uso de JOINs, CTEs, Window Functions e agregações

-- -----------------------------------
-- 1. RESUMO DIÁRIO DE TRANSAÇÕES
-- -----------------------------------
-- Analisa volume, aprovação e valores médios por dia
SELECT 
    DATE(transaction_date) as date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN status = 'declined' THEN 1 ELSE 0 END) as declined_count,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
    SUM(CASE WHEN status = 'refunded' THEN 1 ELSE 0 END) as refunded_count,
    ROUND(SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END), 2) as approved_volume,
    ROUND(AVG(amount), 2) as avg_amount,
    ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate
FROM transactions
WHERE transaction_date >= date('now', '-30 days')
GROUP BY DATE(transaction_date)
ORDER BY date DESC;

-- -----------------------------------
-- 2. ANÁLISE POR MÉTODO DE PAGAMENTO
-- -----------------------------------
-- Performance de cada método (PIX, cartão, etc)
SELECT 
    payment_method,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    ROUND(SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END), 2) as total_volume,
    ROUND(AVG(amount), 2) as avg_ticket,
    ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate,
    MIN(amount) as min_amount,
    MAX(amount) as max_amount
FROM transactions
GROUP BY payment_method
ORDER BY total_volume DESC;

-- -----------------------------------
-- 3. TOP MERCHANTS POR VOLUME
-- -----------------------------------
-- Estabelecimentos que mais transacionam
SELECT 
    m.id,
    m.name,
    m.category,
    COUNT(t.id) as total_transactions,
    ROUND(SUM(t.amount), 2) as total_volume,
    ROUND(AVG(t.amount), 2) as avg_ticket,
    SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as approval_rate
FROM merchants m
JOIN transactions t ON m.id = t.merchant_id
WHERE t.status = 'approved'
GROUP BY m.id
ORDER BY total_volume DESC
LIMIT 20;

-- -----------------------------------
-- 4. PERFORMANCE POR CATEGORIA
-- -----------------------------------
-- Análise agregada por tipo de estabelecimento
SELECT 
    m.category,
    COUNT(DISTINCT m.id) as merchants_count,
    COUNT(t.id) as total_transactions,
    ROUND(SUM(CASE WHEN t.status = 'approved' THEN t.amount ELSE 0 END), 2) as total_volume,
    ROUND(AVG(t.amount), 2) as avg_ticket,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'approved' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as approval_rate
FROM merchants m
LEFT JOIN transactions t ON m.id = t.merchant_id
GROUP BY m.category
ORDER BY total_volume DESC;

-- -----------------------------------
-- 5. DISTRIBUIÇÃO POR HORA DO DIA
-- -----------------------------------
-- Padrões temporais de transações
SELECT 
    CAST(strftime('%H', transaction_date) AS INTEGER) as hour,
    COUNT(*) as total_transactions,
    ROUND(AVG(amount), 2) as avg_amount,
    SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    ROUND(100.0 * SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) / COUNT(*), 2) as approval_rate
FROM transactions
GROUP BY hour
ORDER BY hour;

-- -----------------------------------
-- 6. TOP CLIENTES POR VOLUME
-- -----------------------------------
-- Clientes mais valiosos
SELECT 
    c.id,
    c.name,
    c.email,
    COUNT(t.id) as total_transactions,
    ROUND(SUM(t.amount), 2) as lifetime_value,
    ROUND(AVG(t.amount), 2) as avg_transaction,
    DATE(MIN(t.transaction_date)) as first_transaction,
    DATE(MAX(t.transaction_date)) as last_transaction
FROM customers c
JOIN transactions t ON c.id = t.customer_id
WHERE t.status = 'approved'
GROUP BY c.id
ORDER BY lifetime_value DESC
LIMIT 50;

-- -----------------------------------
-- 7. ANÁLISE DE RECUSAS
-- -----------------------------------
-- Por que transações são recusadas?
SELECT 
    payment_method,
    COUNT(*) as declined_count,
    ROUND(AVG(amount), 2) as avg_declined_amount,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions WHERE status = 'declined'), 2) as pct_of_total_declined
FROM transactions
WHERE status = 'declined'
GROUP BY payment_method
ORDER BY declined_count DESC;

-- -----------------------------------
-- 8. DETECÇÃO DE TRANSAÇÕES ANÔMALAS
-- -----------------------------------
-- Transações com valores muito altos
SELECT 
    t.id,
    t.transaction_date,
    c.name as customer_name,
    m.name as merchant_name,
    m.category,
    t.amount,
    t.payment_method,
    t.status,
    ROUND((t.amount - avg_amount.value) / avg_amount.stddev, 2) as z_score
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN merchants m ON t.merchant_id = m.id
CROSS JOIN (
    SELECT 
        AVG(amount) as value,
        -- SQLite não tem STDDEV, simulação simples
        SQRT(AVG(amount * amount) - AVG(amount) * AVG(amount)) as stddev
    FROM transactions
) avg_amount
WHERE t.amount > (SELECT AVG(amount) * 3 FROM transactions)
ORDER BY t.amount DESC;

-- -----------------------------------
-- 9. CLIENTES COM MÚLTIPLAS TRANSAÇÕES RÁPIDAS
-- -----------------------------------
-- Possível comportamento suspeito
WITH customer_transactions AS (
    SELECT 
        customer_id,
        transaction_date,
        LAG(transaction_date) OVER (PARTITION BY customer_id ORDER BY transaction_date) as prev_transaction
    FROM transactions
)
SELECT 
    c.name,
    c.email,
    COUNT(*) as rapid_transactions,
    MIN(ct.transaction_date) as first_rapid_transaction
FROM customer_transactions ct
JOIN customers c ON ct.customer_id = c.id
WHERE (julianday(ct.transaction_date) - julianday(ct.prev_transaction)) * 24 < 1  -- menos de 1 hora
GROUP BY ct.customer_id
HAVING COUNT(*) >= 5
ORDER BY rapid_transactions DESC;

-- -----------------------------------
-- 10. CRESCIMENTO MÊS A MÊS
-- -----------------------------------
-- Análise de tendência usando Window Functions
WITH monthly_data AS (
    SELECT 
        strftime('%Y-%m', transaction_date) as month,
        COUNT(*) as transactions,
        SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END) as volume
    FROM transactions
    GROUP BY month
)
SELECT 
    month,
    transactions,
    volume,
    LAG(transactions) OVER (ORDER BY month) as prev_month_transactions,
    LAG(volume) OVER (ORDER BY month) as prev_month_volume,
    ROUND(100.0 * (transactions - LAG(transactions) OVER (ORDER BY month)) / 
          LAG(transactions) OVER (ORDER BY month), 2) as transaction_growth_pct,
    ROUND(100.0 * (volume - LAG(volume) OVER (ORDER BY month)) / 
          LAG(volume) OVER (ORDER BY month), 2) as volume_growth_pct
FROM monthly_data
ORDER BY month DESC;

-- -----------------------------------
-- 11. ANÁLISE DE COHORT (SIMPLIFICADA)
-- -----------------------------------
-- Comportamento de clientes por mês de entrada
WITH first_transactions AS (
    SELECT 
        customer_id,
        DATE(MIN(transaction_date)) as first_purchase_date,
        strftime('%Y-%m', MIN(transaction_date)) as cohort_month
    FROM transactions
    WHERE status = 'approved'
    GROUP BY customer_id
)
SELECT 
    ft.cohort_month,
    COUNT(DISTINCT ft.customer_id) as customers_acquired,
    COUNT(t.id) as total_transactions,
    ROUND(AVG(t.amount), 2) as avg_transaction_value
FROM first_transactions ft
LEFT JOIN transactions t ON ft.customer_id = t.customer_id AND t.status = 'approved'
GROUP BY ft.cohort_month
ORDER BY ft.cohort_month DESC;

-- -----------------------------------
-- 12. ESTORNOS - ANÁLISE DETALHADA
-- -----------------------------------
-- Quem e quando está estornando?
SELECT 
    DATE(t.transaction_date) as date,
    m.category,
    m.name as merchant_name,
    COUNT(*) as refund_count,
    ROUND(SUM(t.amount), 2) as refund_volume,
    ROUND(AVG(t.amount), 2) as avg_refund_amount
FROM transactions t
JOIN merchants m ON t.merchant_id = m.id
WHERE t.status = 'refunded'
GROUP BY DATE(t.transaction_date), m.category, m.name
ORDER BY refund_volume DESC;

-- -----------------------------------
-- 13. TICKET MÉDIO POR DIA DA SEMANA
-- -----------------------------------
-- Há diferença no comportamento por dia?
SELECT 
    CASE CAST(strftime('%w', transaction_date) AS INTEGER)
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Segunda'
        WHEN 2 THEN 'Terça'
        WHEN 3 THEN 'Quarta'
        WHEN 4 THEN 'Quinta'
        WHEN 5 THEN 'Sexta'
        WHEN 6 THEN 'Sábado'
    END as day_of_week,
    COUNT(*) as total_transactions,
    ROUND(AVG(amount), 2) as avg_ticket,
    ROUND(SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END), 2) as total_volume
FROM transactions
GROUP BY CAST(strftime('%w', transaction_date) AS INTEGER)
ORDER BY CAST(strftime('%w', transaction_date) AS INTEGER);

-- -----------------------------------
-- 14. MERCHANTS COM MAIOR TAXA DE RECUSA
-- -----------------------------------
-- Identificar problemas potenciais
SELECT 
    m.name,
    m.category,
    COUNT(t.id) as total_transactions,
    SUM(CASE WHEN t.status = 'declined' THEN 1 ELSE 0 END) as declined_count,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'declined' THEN 1 ELSE 0 END) / COUNT(t.id), 2) as decline_rate
FROM merchants m
JOIN transactions t ON m.id = t.merchant_id
GROUP BY m.id
HAVING COUNT(t.id) >= 10  -- Apenas merchants com volume significativo
ORDER BY decline_rate DESC
LIMIT 20;

-- -----------------------------------
-- 15. ANÁLISE COMPLETA DE PERFORMANCE
-- -----------------------------------
-- CTE com múltiplas análises combinadas
WITH 
transaction_stats AS (
    SELECT 
        COUNT(*) as total_transactions,
        SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END) as total_volume,
        AVG(amount) as avg_amount
    FROM transactions
),
customer_stats AS (
    SELECT COUNT(*) as total_customers FROM customers
),
merchant_stats AS (
    SELECT COUNT(*) as total_merchants FROM merchants
),
recent_trend AS (
    SELECT 
        COUNT(*) as last_7_days_transactions
    FROM transactions
    WHERE transaction_date >= date('now', '-7 days')
)
SELECT 
    ts.total_transactions,
    ROUND(ts.total_volume, 2) as total_volume,
    ROUND(ts.avg_amount, 2) as avg_ticket,
    cs.total_customers,
    ms.total_merchants,
    rt.last_7_days_transactions,
    ROUND(CAST(rt.last_7_days_transactions AS FLOAT) / 7, 0) as avg_daily_transactions
FROM transaction_stats ts, customer_stats cs, merchant_stats ms, recent_trend rt;