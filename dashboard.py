"""
Dashboard interativo de análise de pagamentos FinTech
Visualizações e análises SQL avançadas
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import database as db

# Configuração da página
st.set_page_config(
    page_title="FinTech Analytics Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("💰 FinTech Analytics Dashboard")
st.markdown("---")

# Sidebar com filtros
st.sidebar.header("⚙️ Filtros")

# Filtro de período
period_options = {
    "Últimos 7 dias": 7,
    "Últimos 15 dias": 15,
    "Últimos 30 dias": 30,
    "Últimos 60 dias": 60,
    "Últimos 90 dias": 90
}
selected_period = st.sidebar.selectbox(
    "Período de análise:",
    options=list(period_options.keys()),
    index=2
)
days = period_options[selected_period]

# Informações sobre o projeto
st.sidebar.markdown("---")
st.sidebar.info("""
**🎯 Sobre este projeto:**

Dashboard de análise de pagamentos desenvolvido para demonstrar:
- SQL avançado
- Análise de dados
- Visualizações interativas
- Detecção de anomalias

**Tecnologias:**
- Python + Streamlit
- SQLite + Pandas
- Plotly
""")

# Carrega KPIs
kpis = db.get_kpis()

# Seção de KPIs
st.header("📊 Indicadores Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💳 Total de Transações",
        value=f"{kpis['total_transactions']:,}",
        delta="Todas as transações"
    )

with col2:
    st.metric(
        label="💰 Volume Total",
        value=f"R$ {kpis['total_volume']:,.2f}",
        delta="Transações aprovadas"
    )

with col3:
    st.metric(
        label="🎫 Ticket Médio",
        value=f"R$ {kpis['avg_ticket']:,.2f}",
        delta=f"{kpis['approval_rate']}% aprovação"
    )

with col4:
    st.metric(
        label="👥 Clientes Ativos",
        value=f"{kpis['total_customers']:,}",
        delta=f"{kpis['total_merchants']} merchants"
    )

st.markdown("---")

# Abas para diferentes análises
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tendências",
    "💳 Métodos de Pagamento",
    "🏪 Merchants",
    "⏰ Padrões Temporais",
    "🔍 Detecção de Anomalias"
])

# TAB 1: Tendências
with tab1:
    st.header("📈 Análise de Tendências")
    
    # Carrega dados diários
    df_daily = db.get_daily_summary(days)
    
    if not df_daily.empty:
        # Gráfico de linha - Volume diário
        fig_volume = go.Figure()
        
        fig_volume.add_trace(go.Scatter(
            x=df_daily['date'],
            y=df_daily['total_volume'],
            mode='lines+markers',
            name='Volume (R$)',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        
        fig_volume.update_layout(
            title="Volume Diário de Transações Aprovadas",
            xaxis_title="Data",
            yaxis_title="Volume (R$)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de transações por status
            fig_status = go.Figure()
            
            fig_status.add_trace(go.Bar(
                x=df_daily['date'],
                y=df_daily['approved'],
                name='Aprovadas',
                marker_color='#2ecc71'
            ))
            
            fig_status.add_trace(go.Bar(
                x=df_daily['date'],
                y=df_daily['declined'],
                name='Recusadas',
                marker_color='#e74c3c'
            ))
            
            fig_status.update_layout(
                title="Transações por Status",
                xaxis_title="Data",
                yaxis_title="Quantidade",
                barmode='stack',
                height=350
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Gráfico de taxa de aprovação
            fig_approval = go.Figure()
            
            fig_approval.add_trace(go.Scatter(
                x=df_daily['date'],
                y=df_daily['approval_rate'],
                mode='lines+markers',
                fill='tozeroy',
                name='Taxa de Aprovação (%)',
                line=dict(color='#9b59b6', width=2),
                marker=dict(size=6)
            ))
            
            fig_approval.update_layout(
                title="Taxa de Aprovação (%)",
                xaxis_title="Data",
                yaxis_title="Percentual (%)",
                yaxis=dict(range=[0, 100]),
                height=350
            )
            
            st.plotly_chart(fig_approval, use_container_width=True)
        
        # Tabela com resumo
        st.subheader("📋 Resumo Detalhado")
        st.dataframe(
            df_daily[['date', 'total_transactions', 'approved', 'declined', 'total_volume', 'approval_rate']],
            use_container_width=True,
            hide_index=True
        )

# TAB 2: Métodos de Pagamento
with tab2:
    st.header("💳 Análise por Método de Pagamento")
    
    df_methods = db.get_payment_method_stats()
    
    if not df_methods.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza - Distribuição
            fig_pie = px.pie(
                df_methods,
                values='total_transactions',
                names='payment_method',
                title='Distribuição de Transações por Método',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Gráfico de barras - Volume
            fig_bar = px.bar(
                df_methods,
                x='payment_method',
                y='total_volume',
                title='Volume Total por Método (R$)',
                color='payment_method',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Métricas por método
        st.subheader("📊 Métricas Detalhadas")
        
        cols = st.columns(len(df_methods))
        
        for idx, (col, row) in enumerate(zip(cols, df_methods.itertuples())):
            with col:
                st.metric(
                    label=f"🔹 {row.payment_method}",
                    value=f"R$ {row.total_volume:,.2f}",
                    delta=f"{row.approval_rate}% aprovação"
                )
                st.caption(f"{row.total_transactions:,} transações")
        
        # Tabela completa
        st.subheader("📋 Tabela Completa")
        st.dataframe(df_methods, use_container_width=True, hide_index=True)

# TAB 3: Merchants
with tab3:
    st.header("🏪 Performance dos Merchants")
    
    top_n = st.slider("Mostrar top N merchants:", 5, 20, 10)
    df_merchants = db.get_top_merchants(top_n)
    
    if not df_merchants.empty:
        # Gráfico de barras horizontais
        fig_merchants = px.bar(
            df_merchants,
            x='total_volume',
            y='name',
            orientation='h',
            title=f'Top {top_n} Merchants por Volume',
            color='total_volume',
            color_continuous_scale='Blues',
            text='total_volume'
        )
        fig_merchants.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
        fig_merchants.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_merchants, use_container_width=True)
        
        # Análise por categoria
        st.subheader("📊 Performance por Categoria")
        df_category = db.get_category_performance()
        
        fig_category = px.treemap(
            df_category,
            path=['category'],
            values='total_volume',
            title='Volume por Categoria de Merchant',
            color='total_volume',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_category, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Detalhes dos Merchants")
        st.dataframe(df_merchants, use_container_width=True, hide_index=True)

# TAB 4: Padrões Temporais
with tab4:
    st.header("⏰ Análise de Padrões Temporais")
    
    df_hourly = db.get_hourly_distribution()
    
    if not df_hourly.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de linha - Transações por hora
            fig_hourly = px.line(
                df_hourly,
                x='hour',
                y='total_transactions',
                title='Distribuição de Transações por Hora do Dia',
                markers=True
            )
            fig_hourly.update_layout(
            xaxis=dict(dtick=1, title='Hora do Dia'),
            yaxis=dict(title='Número de Transações')
            )
            fig_hourly.update_traces(line_color='#e67e22', line_width=3)
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            # Gráfico de barras - Ticket médio por hora
            fig_avg = px.bar(
                df_hourly,
                x='hour',
                y='avg_amount',
                title='Ticket Médio por Hora',
                color='avg_amount',
                color_continuous_scale='Reds'
            )
            fig_avg.update_layout(
            xaxis=dict(dtick=1, title='Hora do Dia'),
            yaxis=dict(title='Ticket Médio (R$)')
            )
            st.plotly_chart(fig_avg, use_container_width=True)
        
        # Insights
        peak_hour = df_hourly.loc[df_hourly['total_transactions'].idxmax()]
        st.info(f"""
        **💡 Insights:**
        - **Horário de pico:** {int(peak_hour['hour'])}h com {int(peak_hour['total_transactions'])} transações
        - **Período mais movimentado:** Entre 10h e 18h
        - **Ticket médio mais alto:** {df_hourly.loc[df_hourly['avg_amount'].idxmax(), 'hour']:.0f}h
        """)

# TAB 5: Detecção de Anomalias
with tab5:
    st.header("🔍 Detecção de Anomalias")
    
    st.info("""
    **O que são anomalias?**
    
    Transações que fogem do padrão normal e podem indicar:
    - Fraudes
    - Erros no sistema
    - Comportamentos suspeitos
    - Testes de sistema
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        threshold_amount = st.number_input(
            "Valor mínimo para considerar alto (R$):",
            min_value=1000,
            max_value=50000,
            value=10000,
            step=1000
        )
    
    with col2:
        threshold_freq = st.number_input(
            "Transações mínimas por hora para considerar suspeito:",
            min_value=3,
            max_value=20,
            value=5,
            step=1
        )
    
    df_high_value, df_high_freq = db.get_anomalies(threshold_amount, threshold_freq)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Transações de Alto Valor")
        if not df_high_value.empty:
            st.warning(f"⚠️ {len(df_high_value)} transações acima de R$ {threshold_amount:,.2f}")
            st.dataframe(
                df_high_value[['transaction_date', 'customer_name', 'merchant_name', 'amount', 'status']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ Nenhuma transação de alto valor detectada")
    
    with col2:
        st.subheader("🔄 Alta Frequência")
        if not df_high_freq.empty:
            st.warning(f"⚠️ {len(df_high_freq)} clientes com atividade suspeita")
            st.dataframe(
                df_high_freq[['customer_name', 'hour_window', 'transactions_count']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ Nenhum padrão de alta frequência detectado")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💰 <b>FinTech Analytics Dashboard</b> | Desenvolvido com Python, Streamlit e SQL</p>
    <p>📊 Projeto para demonstração de habilidades em análise de dados e SQL avançado</p>
</div>
""", unsafe_allow_html=True)