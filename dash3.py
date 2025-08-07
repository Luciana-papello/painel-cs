import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
from io import BytesIO
import requests
from typing import Optional, Dict, List

# Configuração da página
st.set_page_config(
    page_title="CS Dashboard - Papello",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

senha_correta = st.secrets["app_password"]

# Controle de autenticação na sessão
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Se não estiver autenticado, mostra campo de senha
if not st.session_state.autenticado:
    with st.container():
        st.markdown("### 🔐 Acesso Restrito")
        senha = st.text_input("Digite a senha para acessar o dashboard:", type="password")
        if senha == senha_correta:
            st.session_state.autenticado = True
            st.success("✅ Acesso liberado com sucesso!")
            st.rerun()

        elif senha != "":
            st.error("❌ Senha incorreta. Tente novamente.")
    st.stop() 

# CSS aprimorado e moderno com fonte Montserrat
st.markdown("""
<style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Fonte global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header principal com cores Papello */
    .main-header {
        background: linear-gradient(135deg, #96CA00 0%, #84A802 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Cards de métricas modernos */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    
    .metric-card h3 {
        font-size: 0.9rem;
        font-weight: 500;
        color: #64748b;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    .metric-card .delta {
        font-size: 0.85rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Cores dos cards por prioridade */
    .metric-success {
        border-left: 4px solid #96CA00;
    }
    
    .metric-success .value {
        color: #84A802;
    }
    
    .metric-warning {
        border-left: 4px solid #f59e0b;
    }
    
    .metric-warning .value {
        color: #d97706;
    }
    
    .metric-danger {
        border-left: 4px solid #ef4444;
    }
    
    .metric-danger .value {
        color: #dc2626;
    }
    
    .metric-info {
        border-left: 4px solid #3b82f6;
    }
    
    .metric-info .value {
        color: #2563eb;
    }
    
    /* Cards de alerta */
    .alert-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #ef4444;
        transition: all 0.2s ease;
    }
    
    .alert-card:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    }
    
    .alert-high {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fff 100%);
    }
    
    .alert-medium {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fff 100%);
    }
    
    .alert-low {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #fff 100%);
    }
    
    .alert-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .alert-title {
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0;
    }
    
    .alert-priority {
        font-size: 1.5rem;
    }
    
    .alert-content {
        color: #374151;
        line-height: 1.5;
    }
    
    .alert-meta {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: #6b7280;
    }
    
    /* Seções */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    .section-header h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
        color: #1f2937;
    }
    
    .section-header .emoji {
        font-size: 1.8rem;
    }
    
    /* Filtros aprimorados */
    .filter-container {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Progresso personalizado */
    .progress-container {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 3px;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #96CA00, #84A802);
        height: 8px;
        border-radius: 6px;
        transition: width 0.3s ease;
    }
    
    .progress-label {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.25rem;
        color: #475569;
    }
    
    /* Ocultar elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Configurações - IDs das planilhas
CLASSIFICACAO_SHEET_ID = st.secrets["classificacao_sheet_id"]
PESQUISA_SHEET_ID = st.secrets["pesquisa_sheet_id"]
ACTIONS_FILE = "cs_actions_log.json"

# Cores padronizadas - Identidade Visual Papello
COLORS = {
    'primary': '#96CA00',      # Verde principal Papello
    'secondary': '#84A802',    # Verde escuro Papello  
    'success': '#96CA00',      # Verde Papello para sucesso
    'warning': '#f59e0b',      # Laranja para avisos
    'danger': '#ef4444',       # Vermelho para alertas
    'info': '#3b82f6',         # Azul para informações
    'light_green': '#C5DF56',  # Verde claro Papello
    'premium': '#8b5cf6',      # Roxo para Premium
    'gold': '#f59e0b',         # Dourado para Gold
    'silver': '#6b7280',       # Cinza para Silver
    'bronze': '#dc2626',       # Vermelho para Bronze
    'papello_black': '#000000' # Preto Papello
}

# Paleta para gráficos com cores Papello
CHART_COLORS = {
    'churn': {
        'Ativo': COLORS['success'],
        'Inativo': COLORS['danger'],
        'Dormant_Novo': COLORS['warning'],
        'Dormant_Premium': '#7c3aed',
        'Dormant_Gold': '#ea580c',
        'Dormant_Silver': '#64748b',
        'Dormant_Bronze': '#dc2626'
    },
    'nivel': {
        'Premium': COLORS['premium'],
        'Gold': COLORS['gold'],
        'Silver': COLORS['silver'],
        'Bronze': COLORS['bronze']
    },
    'risco': {
        'Alto': COLORS['danger'],
        'Novo_Alto': '#dc2626',
        'Médio': COLORS['warning'],
        'Novo_Médio': '#ea580c',
        'Baixo': COLORS['success'],
        'Novo_Baixo': COLORS['light_green']
    }
}

# === FUNÇÕES AUXILIARES ===

def get_latest_update_date(df_pedidos):
    """Pega a data mais recente da aba pedidos_com_id2"""
    if df_pedidos.empty:
        return "N/A"
    
    try:
        # Verificar se a coluna existe
        if 'data_pedido_realizado' not in df_pedidos.columns:
            return "N/A"
        
        # Converter coluna para datetime, tratando diferentes formatos
        df_temp = df_pedidos.copy()
        df_temp['data_pedido_realizado'] = pd.to_datetime(df_temp['data_pedido_realizado'], errors='coerce')
        
        # Remover valores nulos
        dates_valid = df_temp['data_pedido_realizado'].dropna()
        
        if len(dates_valid) == 0:
            return "N/A"
        
        # Pegar a data mais recente
        latest_date = dates_valid.max()
        
        if pd.isna(latest_date):
            return "N/A"
        
        # Formatar como dd/mm/aaaa
        return latest_date.strftime('%d/%m/%Y')
    
    except Exception as e:
        return "N/A"

def format_phone_number(phone):
    """Formata número de telefone removendo .0 e outros caracteres desnecessários"""
    if pd.isna(phone) or phone == "":
        return "N/A"
    
    phone_str = str(phone)
    # Remove .0 no final se existir
    if phone_str.endswith('.0'):
        phone_str = phone_str[:-2]
    
    return phone_str

def export_to_excel(df, filename="clientes_filtrados.xlsx"):
    """Gera arquivo Excel para download"""
    output = BytesIO()
    try:
        # Tentar usar openpyxl primeiro (mais comum)
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Clientes', index=False)
    except ImportError:
        try:
            # Fallback para xlsxwriter se disponível
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Clientes', index=False)
        except ImportError:
            # Se nenhum engine Excel estiver disponível, retorna None
            return None
    
    output.seek(0)
    return output.getvalue()

def export_to_csv(df, filename="clientes_filtrados.csv"):
    """Gera arquivo CSV para download"""
    return df.to_csv(index=False).encode('utf-8')

def convert_text_score_to_number(text_score):
    """Converte respostas em texto para valores numéricos"""
    if pd.isna(text_score) or text_score == "":
        return np.nan
    
    text_score = str(text_score).lower().strip()
    
    # Mapeamento otimizado
    mappings = {
        'entre 0 e 1': 0.5, 'entre 1 e 2': 1.5, 'entre 2 e 3': 2.5,
        'entre 3 e 4': 3.5, 'entre 4 e 5': 4.5, 'entre 5 e 6': 5.5,
        'entre 6 e 7': 6.5, 'entre 7 e 8': 7.5, 'entre 8 e 9': 8.5,
        'entre 9 e 10': 9.5, 'entre 1 e 6': 3.5
    }
    
    for key, value in mappings.items():
        if key in text_score:
            return value
    
    # Fallback para extração de números
    import re
    numbers = re.findall(r'\d+', text_score)
    if len(numbers) >= 2:
        return (float(numbers[0]) + float(numbers[1])) / 2
    elif len(numbers) == 1:
        return float(numbers[0])
    
    return np.nan

def categorize_nps_from_text(text_score):
    """Categoriza respostas em texto para NPS - Versão otimizada para Papello"""
    if pd.isna(text_score) or text_score == "" or str(text_score).lower().strip() == "":
        return "Sem resposta"
    
    text_score = str(text_score).lower().strip()
    
    # Detratores (0-6) - Padrões da sua planilha
    detrator_patterns = [
        'entre 0 e 1', 'entre 1 e 2', 'entre 2 e 3', 
        'entre 3 e 4', 'entre 4 e 5', 'entre 5 e 6', 
        'entre 1 e 6', '0', '1', '2', '3', '4', '5', '6'
    ]
    
    # Neutros (7-8)
    neutro_patterns = ['entre 7 e 8', '7', '8']
    
    # Promotores (9-10)
    promotor_patterns = ['entre 9 e 10', '9', '10']
    
    # Verificar padrões (ordem importante - mais específico primeiro)
    if any(pattern in text_score for pattern in promotor_patterns):
        return "Promotor"
    elif any(pattern in text_score for pattern in neutro_patterns):
        return "Neutro"
    elif any(pattern in text_score for pattern in detrator_patterns):
        return "Detrator"
    
    # Tentar extrair número se for formato numérico direto
    import re
    numbers = re.findall(r'\d+', text_score)
    if numbers:
        try:
            score = int(numbers[0])
            if score >= 9:
                return "Promotor"
            elif score >= 7:
                return "Neutro"
            elif score >= 0:
                return "Detrator"
        except ValueError:
            pass
    
    return "Indefinido"

@st.cache_data(ttl=300)
def load_google_sheet_public(sheet_id, tab_name):
    """Carrega planilha pública do Google Sheets"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar planilha {tab_name}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_satisfaction_data():
    """VERSÃO COM CORREÇÃO DE DATA BRASILEIRA"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{PESQUISA_SHEET_ID}/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # === FORÇAR FORMATO BRASILEIRO ===
        date_cols = [col for col in df.columns if any(x in col.lower() for x in ['carimbo', 'data', 'timestamp'])]
        
        for col in date_cols:
            # Forçar formato DD/MM/YYYY HH:MM:SS
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            
            # Se ainda tem nulos, tentar sem horário
            mask_null = df[col].isnull()
            if mask_null.any():
                df.loc[mask_null, col] = pd.to_datetime(df.loc[mask_null, col], format='%d/%m/%Y', errors='coerce')
        
        return df.copy()
    except Exception as e:
        st.error(f"Erro: {str(e)}")
        return pd.DataFrame()

def calculate_priority_score(row):
    """Calcula score de prioridade para ordenação"""
    priority_weights = {'Premium': 100, 'Gold': 80, 'Silver': 60, 'Bronze': 40}
    churn_weights = {
        'Dormant_Premium': 300, 'Dormant_Gold': 250, 'Dormant_Silver': 200,
        'Dormant_Bronze': 150, 'Dormant_Novo': 120, 'Inativo': 100, 'Ativo': 0
    }
    risk_weights = {
        'Novo_Alto': 80, 'Alto': 50, 'Novo_Médio': 40,
        'Médio': 30, 'Novo_Baixo': 20, 'Baixo': 10
    }
    
    nivel = row.get('nivel_cliente', 'Bronze')
    risco = row.get('risco_recencia', 'Baixo')
    churn = row.get('status_churn', 'Ativo')
    top20 = 1 if row.get('top_20_valor', 'Não') == 'Sim' else 0
    
    return (priority_weights.get(nivel, 0) + 
            risk_weights.get(risco, 0) + 
            churn_weights.get(churn, 0) + 
            top20 * 25)

def get_priority_color_class(priority_score):
    """Retorna classe CSS baseada no score de prioridade"""
    if priority_score >= 200:
        return "🔴", "alert-high"
    elif priority_score >= 100:
        return "🟡", "alert-medium"
    else:
        return "🟢", "alert-low"

def create_metric_card_with_explanation(title, value, delta=None, color_class="metric-info", explanation=""):
    """Cria um card de métrica moderno com explicação"""
    delta_html = f'<p class="delta">{delta}</p>' if delta else ''
    explanation_html = f'<p style="font-size: 0.8rem; color: #6b7280; margin-top: 0.5rem;">{explanation}</p>' if explanation else ''
    
    return f"""
    <div class="metric-card {color_class}">
        <h3>{title}</h3>
        <p class="value">{value}</p>
        {delta_html}
        {explanation_html}
    </div>
    """

def create_progress_bar(value, max_value, label="", color="#96CA00"):
    """Cria uma barra de progresso personalizada com cores Papello"""
    percentage = min((value / max_value) * 100, 100) if max_value > 0 else 0
    
    return f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%; background: {color};"></div>
        <div class="progress-label">{label}: {value:,} / {max_value:,} ({percentage:.1f}%)</div>
    </div>
    """

def create_alert_card(cliente, priority_score):
    """Cria um card de alerta moderno"""
    emoji, css_class = get_priority_color_class(priority_score)
    
    return f"""
    <div class="alert-card {css_class}">
        <div class="alert-header">
            <h4 class="alert-title">{cliente.get('nome', 'N/A')}</h4>
            <span class="alert-priority">{emoji}</span>
        </div>
        <div class="alert-content">
            <p><strong>📧 Email:</strong> {cliente.get('email', 'N/A')}</p>
            <p><strong>📱 Telefone:</strong> {format_phone_number(cliente.get('telefone1', 'N/A'))}</p>
            <p><strong>🏆 Nível:</strong> {cliente.get('nivel_cliente', 'N/A')}</p>
            <p><strong>💰 Receita:</strong> R$ {cliente.get('receita', '0')}</p>
            <p><strong>🎯 Ação Sugerida:</strong> {cliente.get('acao_sugerida', 'Nenhuma ação sugerida')}</p>
        </div>
        <div class="alert-meta">
            <span>Score: {priority_score:.0f}</span>
            <span>Risco: {cliente.get('risco_recencia', 'N/A')}</span>
            <span>Status: {cliente.get('status_churn', 'N/A')}</span>
        </div>
    </div>
    """

def calculate_satisfaction_with_comparison(df_satisfacao, column_name, is_nps=False):
    """Calcula satisfação dos últimos 30 dias - VERSÃO COM CORREÇÃO DE DATA"""
    if df_satisfacao.empty:
        return "N/A", "Sem dados", "metric-info", ""
    
    # Buscar coluna de data
    date_column = None
    for col in df_satisfacao.columns:
        if any(x in col.lower() for x in ['carimbo', 'data', 'timestamp', 'time']):
            date_column = col
            break
    
    if not date_column or column_name not in df_satisfacao.columns:
        return "N/A", "Coluna não encontrada", "metric-info", ""
    
    # === DEBUG ESSENCIAL PARA VERIFICAR DATA ===
    st.write(f"**📊 DEBUG - Verificação de Data:**")
    st.write(f"- Total de registros: {len(df_satisfacao)}")
    st.write(f"- Coluna de data: `{date_column}`")
    st.write(f"- Tipo da coluna: {df_satisfacao[date_column].dtype}")
    
    # Mostrar amostra das datas
    sample_dates = df_satisfacao[date_column].dropna().head(5)
    st.write(f"- Amostra de datas: {sample_dates.tolist()}")
    
    # Range completo
    if len(sample_dates) > 0:
        data_min = df_satisfacao[date_column].min()
        data_max = df_satisfacao[date_column].max()
        st.write(f"- Range completo: {data_min} até {data_max}")
    
    # === DEFINIR PERÍODOS ===
    hoje = datetime.now()
    inicio_atual = hoje - timedelta(days=30)
    st.write(f"- Hoje: {hoje.strftime('%d/%m/%Y %H:%M')}")
    st.write(f"- Início período (30 dias atrás): {inicio_atual.strftime('%d/%m/%Y %H:%M')}")
    
    # === FILTRAR DADOS ===
    df_valid = df_satisfacao.dropna(subset=[date_column])
    
    # Filtrar período atual
    dados_atual = df_valid[
        (df_valid[date_column] >= inicio_atual) & 
        (df_valid[date_column] <= hoje)
    ]
    
    # Filtrar período anterior  
    inicio_anterior = hoje - timedelta(days=60)
    fim_anterior = hoje - timedelta(days=30)
    dados_anterior = df_valid[
        (df_valid[date_column] >= inicio_anterior) & 
        (df_valid[date_column] < fim_anterior)
    ]
    
    st.write(f"**📅 Resultados do filtro:**")
    st.write(f"- Registros no período atual: {len(dados_atual)}")
    st.write(f"- Registros no período anterior: {len(dados_anterior)}")
    
    # === ANALISAR RESPOSTAS ===
    respostas_atual = dados_atual[column_name].dropna()
    respostas_anterior = dados_anterior[column_name].dropna()
    
    st.write(f"- Respostas válidas atual: {len(respostas_atual)}")
    st.write(f"- Respostas válidas anterior: {len(respostas_anterior)}")
    
    # === MOSTRAR DISTRIBUIÇÃO POR DIA (ÚLTIMOS 15 DIAS) ===
    if len(dados_atual) > 0:
        with st.expander("📊 Distribuição por dia (últimos 15 dias)"):
            dados_recentes = dados_atual.copy()
            dados_recentes['data_dia'] = dados_recentes[date_column].dt.date
            
            # Filtrar últimos 15 dias
            quinze_dias_atras = hoje - timedelta(days=15)
            dados_15_dias = dados_recentes[dados_recentes[date_column] >= quinze_dias_atras]
            
            if len(dados_15_dias) > 0:
                distribuicao = dados_15_dias.groupby('data_dia').size().reset_index()
                distribuicao.columns = ['Data', 'Quantidade']
                distribuicao = distribuicao.sort_values('Data', ascending=False)
                st.dataframe(distribuicao, use_container_width=True)
            else:
                st.write("Nenhum dado nos últimos 15 dias")
    
    if len(respostas_atual) == 0:
        st.error("❌ Nenhuma resposta encontrada no período atual!")
        return "N/A", "Sem dados nos últimos 30 dias", "metric-warning", ""
    
    # === CONTINUAR COM CÁLCULO NORMAL ===
    if is_nps:
        # Cálculo do NPS
        categorias_atual = respostas_atual.apply(categorize_nps_from_text)
        promotores_atual = (categorias_atual == 'Promotor').sum()
        neutros_atual = (categorias_atual == 'Neutro').sum()
        detratores_atual = (categorias_atual == 'Detrator').sum()
        total_validas_atual = promotores_atual + neutros_atual + detratores_atual
        
        if total_validas_atual == 0:
            return "N/A", "Sem respostas válidas para NPS", "metric-warning", ""
            
        valor_atual = ((promotores_atual - detratores_atual) / total_validas_atual * 100)
        
        # Debug do NPS
        with st.expander("🔍 Debug NPS - Clique para ver detalhes"):
            st.write(f"**📊 Período Atual ({len(respostas_atual)} respostas):**")
            st.write(f"- ✅ Promotores (9-10): {promotores_atual}")
            st.write(f"- ➡️ Neutros (7-8): {neutros_atual}")
            st.write(f"- ❌ Detratores (0-6): {detratores_atual}")
            st.write(f"- 📊 Total válidas: {total_validas_atual}")
            st.write(f"- 🎯 NPS: {valor_atual:.1f}% = ({promotores_atual} - {detratores_atual}) / {total_validas_atual} * 100")
            
            # Amostra das respostas
            st.write("**🔍 Amostra (primeiras 10 respostas):**")
            amostra = respostas_atual.head(10).tolist()
            for i, resp in enumerate(amostra, 1):
                categoria = categorize_nps_from_text(resp)
                emoji = "✅" if categoria == "Promotor" else "➡️" if categoria == "Neutro" else "❌"
                st.write(f"  {i}. `{resp}` → {emoji} {categoria}")
        
        # Calcular comparação com período anterior
        if len(respostas_anterior) > 0:
            categorias_anterior = respostas_anterior.apply(categorize_nps_from_text)
            promotores_anterior = (categorias_anterior == 'Promotor').sum()
            detratores_anterior = (categorias_anterior == 'Detrator').sum()
            neutros_anterior = (categorias_anterior == 'Neutro').sum()
            total_validas_anterior = promotores_anterior + neutros_anterior + detratores_anterior
            
            if total_validas_anterior > 0:
                valor_anterior = ((promotores_anterior - detratores_anterior) / total_validas_anterior * 100)
                diferenca = valor_atual - valor_anterior
                
                if diferenca > 5:
                    trend = f"↗️ +{diferenca:.0f} pts vs período anterior"
                    color_class = "metric-success"
                elif diferenca < -5:
                    trend = f"↘️ {diferenca:.0f} pts vs período anterior"
                    color_class = "metric-danger"
                else:
                    trend = f"➡️ {diferenca:+.0f} pts vs período anterior"
                    color_class = "metric-success" if valor_atual >= 50 else "metric-warning" if valor_atual >= 0 else "metric-danger"
            else:
                trend = f"{total_validas_atual} avaliações (sem dados anteriores)"
                color_class = "metric-success" if valor_atual >= 50 else "metric-warning" if valor_atual >= 0 else "metric-danger"
        else:
            trend = f"{total_validas_atual} avaliações (sem período anterior)"
            color_class = "metric-success" if valor_atual >= 50 else "metric-warning" if valor_atual >= 0 else "metric-danger"
            
        return f"{valor_atual:.0f}", trend, color_class, ""
    
    else:
        # Outras métricas (Atendimento, Produto, Prazo)
        scores_atual = respostas_atual.apply(convert_text_score_to_number).dropna()
        
        if len(scores_atual) == 0:
            return "N/A", "Erro na conversão", "metric-warning", ""
            
        valor_atual = scores_atual.mean()
        
        if len(respostas_anterior) > 0:
            scores_anterior = respostas_anterior.apply(convert_text_score_to_number).dropna()
            if len(scores_anterior) > 0:
                valor_anterior = scores_anterior.mean()
                diferenca = valor_atual - valor_anterior
                
                if diferenca > 0.3:
                    trend = f"↗️ +{diferenca:.1f} vs anterior"
                    color_class = "metric-success"
                elif diferenca < -0.3:
                    trend = f"↘️ {diferenca:.1f} vs anterior"
                    color_class = "metric-danger"
                else:
                    trend = f"➡️ {diferenca:+.1f} vs anterior"
                    color_class = "metric-success" if valor_atual >= 8 else "metric-warning" if valor_atual >= 6 else "metric-danger"
            else:
                trend = f"{len(respostas_atual)} avaliações"
                color_class = "metric-success" if valor_atual >= 8 else "metric-warning" if valor_atual >= 6 else "metric-danger"
        else:
            trend = f"{len(respostas_atual)} avaliações"
            color_class = "metric-success" if valor_atual >= 8 else "metric-warning" if valor_atual >= 6 else "metric-danger"
            
        return f"{valor_atual:.1f}/10", trend, color_class, ""
    
    
        

def analyze_client_recurrence(df_pedidos, data_inicio=None, data_fim=None):
    """Analisa recorrência de clientes baseado nos pedidos com filtro de data"""
    if df_pedidos.empty:
        return {}
    
    try:
        # Verificar se as colunas necessárias existem
        required_cols = ['data_pedido_realizado', 'status_pedido', 'cliente_unico_id', 'valor_do_pedido']
        missing_cols = [col for col in required_cols if col not in df_pedidos.columns]
        
        if missing_cols:
            return {}
        
        # Fazer cópia para não alterar o DataFrame original
        df_work = df_pedidos.copy()
        
        # Converter data do pedido com tratamento de erros
        df_work['data_pedido_realizado'] = pd.to_datetime(df_work['data_pedido_realizado'], errors='coerce')
        df_valid = df_work.dropna(subset=['data_pedido_realizado']).copy()
        
        if len(df_valid) == 0:
            return {}
        
        # Aplicar filtro de data se fornecido
        if data_inicio and data_fim:
            # Converter para datetime se necessário
            if isinstance(data_inicio, str):
                data_inicio = pd.to_datetime(data_inicio)
            if isinstance(data_fim, str):
                data_fim = pd.to_datetime(data_fim)
            
            # Filtrar dados
            df_valid = df_valid[
                (df_valid['data_pedido_realizado'] >= data_inicio) & 
                (df_valid['data_pedido_realizado'] <= data_fim)
            ]
        
        if len(df_valid) == 0:
            return {}
        
        # Calcular métricas de recorrência
        total_pedidos = len(df_valid)
        
        # Limpar e normalizar status para busca
        df_valid['status_pedido_clean'] = df_valid['status_pedido'].astype(str).str.strip().str.lower()
        
        # Buscar por diferentes variações dos valores (baseado no debug: "Primeiro" e "Recompra")
        primeira_variations = ['primeiro', 'primeira', 'first', 'nova', 'novo']
        recompra_variations = ['recompra', 'repeat', 'recorrente', 'retorno']
        
        pedidos_primeira_compra = 0
        pedidos_recompra = 0
        
        # Contar pedidos de primeira compra
        for variation in primeira_variations:
            count = len(df_valid[df_valid['status_pedido_clean'].str.contains(variation, na=False)])
            if count > 0:
                pedidos_primeira_compra = count
                break
        
        # Contar pedidos de recompra
        for variation in recompra_variations:
            count = len(df_valid[df_valid['status_pedido_clean'].str.contains(variation, na=False)])
            if count > 0:
                pedidos_recompra = count
                break
        
        # Clientes únicos
        clientes_unicos = df_valid['cliente_unico_id'].nunique()
        
        # Análise temporal (últimos 30 dias do período) - mantendo para compatibilidade
        if data_fim:
            inicio_mes = data_fim - timedelta(days=30)
            pedidos_mes = df_valid[df_valid['data_pedido_realizado'] >= inicio_mes]
        else:
            hoje = datetime.now()
            inicio_mes = hoje - timedelta(days=30)
            pedidos_mes = df_valid[df_valid['data_pedido_realizado'] >= inicio_mes]
        
        # Contar novos clientes e recompras no período (últimos 30 dias)
        novos_clientes_mes = 0
        recompras_mes = 0
        
        if len(pedidos_mes) > 0:
            pedidos_mes = pedidos_mes.copy()
            pedidos_mes['status_pedido_clean'] = pedidos_mes['status_pedido'].astype(str).str.strip().str.lower()
            
            for variation in primeira_variations:
                count = len(pedidos_mes[pedidos_mes['status_pedido_clean'].str.contains(variation, na=False)])
                if count > 0:
                    novos_clientes_mes = count
                    break
            
            for variation in recompra_variations:
                count = len(pedidos_mes[pedidos_mes['status_pedido_clean'].str.contains(variation, na=False)])
                if count > 0:
                    recompras_mes = count
                    break
        
        # Taxa de conversão para recompra
        if clientes_unicos > 0 and pedidos_primeira_compra > 0:
            try:
                # Clientes que fizeram primeira compra
                df_primeira = df_valid[df_valid['status_pedido_clean'].str.contains('|'.join(primeira_variations), na=False)]
                clientes_primeira = set(df_primeira['cliente_unico_id'])
                
                # Clientes que fizeram recompra  
                df_recompra = df_valid[df_valid['status_pedido_clean'].str.contains('|'.join(recompra_variations), na=False)]
                clientes_recompra = set(df_recompra['cliente_unico_id'])
                
                # Clientes que apareceram em ambos
                clientes_convertidos = len(clientes_primeira.intersection(clientes_recompra))
                taxa_conversao = (clientes_convertidos / len(clientes_primeira)) * 100 if len(clientes_primeira) > 0 else 0
            except:
                taxa_conversao = 0
        else:
            taxa_conversao = 0
        
        # Ticket médio por tipo - converter valor para numérico
        try:
            df_valid['valor_numerico'] = pd.to_numeric(
                df_valid['valor_do_pedido'].astype(str).str.replace(',', '.').str.replace('[^\d.]', '', regex=True), 
                errors='coerce'
            )
        except:
            df_valid['valor_numerico'] = 0
        
        # Calcular tickets médios
        ticket_primeira = 0
        ticket_recompra = 0
        
        try:
            if pedidos_primeira_compra > 0:
                df_primeira = df_valid[df_valid['status_pedido_clean'].str.contains('|'.join(primeira_variations), na=False)]
                if len(df_primeira) > 0:
                    ticket_primeira = df_primeira['valor_numerico'].mean()
                    ticket_primeira = ticket_primeira if not pd.isna(ticket_primeira) else 0
            
            if pedidos_recompra > 0:
                df_recompra = df_valid[df_valid['status_pedido_clean'].str.contains('|'.join(recompra_variations), na=False)]
                if len(df_recompra) > 0:
                    ticket_recompra = df_recompra['valor_numerico'].mean()
                    ticket_recompra = ticket_recompra if not pd.isna(ticket_recompra) else 0
        except:
            pass
        
        result = {
            'total_pedidos': total_pedidos,
            'pedidos_primeira': pedidos_primeira_compra,
            'pedidos_recompra': pedidos_recompra,
            'clientes_unicos': clientes_unicos,
            'novos_mes': novos_clientes_mes,
            'recompras_mes': recompras_mes,
            'taxa_conversao': taxa_conversao,
            'ticket_primeira': ticket_primeira,
            'ticket_recompra': ticket_recompra
        }
        
        return result
    
    except Exception as e:
        # Em caso de erro, retornar dados vazios
        return {}

# === SISTEMA DE LOGS E AÇÕES ===

def load_actions_log():
    """Carrega log de ações executadas"""
    if os.path.exists(ACTIONS_FILE):
        try:
            with open(ACTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_action_log(action_data):
    """Salva ação no log"""
    actions = load_actions_log()
    action_data['timestamp'] = datetime.now().isoformat()
    actions.append(action_data)
    
    with open(ACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(actions, f, ensure_ascii=False, indent=2)

# === INTERFACE PRINCIPAL ===

def main():
    # Header principal com logo Papello
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.image("https://acdn-us.mitiendanube.com/stores/002/907/105/themes/common/ogimage-1149314976-1685710658-ab8c89cb60705e9411f6e0d3a4338ae61685710659.png?0", width=120)
    
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Dashboard de Sucesso do Cliente</h1>
            <p>Papello Embalagens - Gestão Inteligente de Relacionamento</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Carregar dados com indicador de progresso
    with st.spinner("🔄 Carregando dados do sistema..."):
        df_clientes = load_google_sheet_public(CLASSIFICACAO_SHEET_ID, "classificacao_clientes3")
        df_pedidos = load_google_sheet_public(CLASSIFICACAO_SHEET_ID, "pedidos_com_id2")
        df_satisfacao = load_satisfaction_data()
        actions_log = load_actions_log()

    # Sidebar aprimorada (após carregar dados)
    with st.sidebar:
        st.markdown("### 🔧 Configurações")
        
        # Atualizar dados com feedback visual
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Atualizar", type="primary", use_container_width=True):
                with st.spinner("Atualizando dados..."):
                    st.cache_data.clear()
                    st.success("✅ Dados atualizados!")
                    st.rerun()
        
        with col2:
            if st.button("📤 Exportar", use_container_width=True):
                st.info("🚧 Em desenvolvimento")
        
        st.markdown("---")
        
        # Filtros aprimorados
        st.markdown("### 📊 Filtros de Análise")
        
        period_days = st.selectbox(
            "📅 Período de análise",
            [30, 60, 90, 180, 365],
            index=2,
            help="Período em dias para análise de tendências"
        )
        
        team_filter = st.selectbox(
            "👥 Membro da equipe",
            ["Todos", "Maria (Gerente)", "Ana (SAC)", "João (SAC)", "Pedro (SAC)"],
            help="Filtrar ações por responsável"
        )
        
        # Filtros rápidos
        st.markdown("### ⚡ Filtros Rápidos")
        show_only_critical = st.checkbox("🚨 Apenas críticos", help="Mostrar apenas clientes com alta prioridade")
        show_only_premium = st.checkbox("👑 Apenas Premium/Gold", help="Focar em clientes de alto valor")
        
        st.markdown("---")
        
        # Informações do sistema
        st.markdown("### ℹ️ Informações")
        
        # Data da última atualização dos dados (mais recente de pedidos)
        latest_data_date = get_latest_update_date(df_pedidos)
        st.caption(f"Última atualização de dados: {latest_data_date}")
        st.caption("Dados sincronizados com Google Sheets")
    
    if df_clientes.empty:
        st.error("❌ Não foi possível carregar os dados dos clientes. Verifique a conexão com as planilhas.")
        return
    
    # Processar dados
    df_clientes = df_clientes.copy()
    df_clientes['priority_score'] = df_clientes.apply(calculate_priority_score, axis=1)
    df_clientes = df_clientes.sort_values('priority_score', ascending=False)
    
    # Aplicar filtros se selecionados
    if show_only_critical:
        df_clientes = df_clientes[df_clientes['priority_score'] >= 200]
    
    if show_only_premium:
        df_clientes = df_clientes[df_clientes['nivel_cliente'].isin(['Premium', 'Gold'])]
    
    # Tabs principais com melhor organização
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Visão Executiva", 
        "👥 Gestão de Clientes", 
        "📈 Analytics & Performance",
        "🔔 Central de Ações"
    ])
    
    with tab1:
        show_executive_dashboard(df_clientes, df_pedidos, df_satisfacao, actions_log)
    
    with tab2:
        show_client_management_enhanced(df_clientes, actions_log)
    
    with tab3:
        show_analytics_dashboard(df_clientes, df_pedidos, df_satisfacao, actions_log, period_days)
    
    with tab4:
        show_actions_center_enhanced(df_clientes, actions_log, team_filter)

# === PÁGINAS DO DASHBOARD ===
def calculate_satisfaction_with_comparison_enhanced(df_satisfacao, column_name, is_nps=False, data_inicio=None, data_fim=None):
    """Calcula satisfação com períodos personalizados e explicações didáticas"""
    if df_satisfacao.empty:
        return "N/A", "Sem dados", "metric-info", ""
    
    # Usar período padrão se não especificado
    if not data_inicio or not data_fim:
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=30)
    else:
        # Converter para datetime se necessário
        if hasattr(data_inicio, 'date'):
            data_inicio = datetime.combine(data_inicio, datetime.min.time())
        if hasattr(data_fim, 'date'):
            data_fim = datetime.combine(data_fim, datetime.max.time())
    
    # Buscar coluna de data
    date_column = None
    for col in df_satisfacao.columns:
        if any(x in col.lower() for x in ['carimbo', 'data', 'timestamp', 'time']):
            date_column = col
            break
    
    if not date_column or column_name not in df_satisfacao.columns:
        return "N/A", "Coluna não encontrada", "metric-info", ""
    
    # === DEBUG ESSENCIAL (MENOS VERBOSO) ===
    st.write(f"**📊 {column_name}:** {len(df_satisfacao)} registros → Período: {data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')}")
    
    # Filtrar dados no período
    df_valid = df_satisfacao.dropna(subset=[date_column])
    dados_periodo = df_valid[
        (df_valid[date_column] >= data_inicio) & 
        (df_valid[date_column] <= data_fim)
    ]
    
    respostas_periodo = dados_periodo[column_name].dropna()
    st.write(f"→ **{len(respostas_periodo)} respostas válidas** no período")
    
    if len(respostas_periodo) == 0:
        return "N/A", "Sem dados no período", "metric-warning", ""
    
    # === CALCULAR PERÍODO DE COMPARAÇÃO ===
    periodo_dias = (data_fim - data_inicio).days
    inicio_comparacao = data_inicio - timedelta(days=periodo_dias)
    fim_comparacao = data_inicio
    
    dados_comparacao = df_valid[
        (df_valid[date_column] >= inicio_comparacao) & 
        (df_valid[date_column] < fim_comparacao)
    ]
    respostas_comparacao = dados_comparacao[column_name].dropna()
    
    if is_nps:
        # === CÁLCULO NPS ===
        categorias_periodo = respostas_periodo.apply(categorize_nps_from_text)
        promotores = (categorias_periodo == 'Promotor').sum()
        neutros = (categorias_periodo == 'Neutro').sum()
        detratores = (categorias_periodo == 'Detrator').sum()
        indefinidos = (categorias_periodo == 'Indefinido').sum()
        total_validas = promotores + neutros + detratores
        
        if total_validas == 0:
            return "N/A", "Sem respostas válidas para NPS", "metric-warning", ""
            
        nps_valor = ((promotores - detratores) / total_validas * 100)
        
        # === EXPLICAÇÃO DIDÁTICA COMPLETA DO NPS ===
        with st.expander(f"🎯 Análise Completa do NPS ({data_inicio.strftime('%d/%m')} - {data_fim.strftime('%d/%m')})"):
            st.markdown("### 📊 Categorização das Respostas")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Promotores", f"{promotores}", help="Notas 9-10: Clientes entusiasmados")
            with col2:
                st.metric("➡️ Neutros", f"{neutros}", help="Notas 7-8: Clientes satisfeitos mas passivos")
            with col3:
                st.metric("❌ Detratores", f"{detratores}", help="Notas 0-6: Clientes insatisfeitos")
            with col4:
                st.metric("📊 Total Válidas", f"{total_validas}")
            
            st.markdown("---")
            st.markdown("### 🧮 Cálculo do NPS")
            st.markdown(f"""
            **Fórmula:** `NPS = ((Promotores - Detratores) / Total Válidas) × 100`
            
            **Seu cálculo:**
            ```
            NPS = (({promotores} - {detratores}) / {total_validas}) × 100
            NPS = ({promotores - detratores} / {total_validas}) × 100  
            NPS = {(promotores - detratores) / total_validas:.3f} × 100
            NPS = {nps_valor:.1f}
            ```
            """)
            
            st.markdown("---")
            st.markdown("### 📈 Interpretação do Resultado")
            
            # Classificação do NPS
            if nps_valor >= 75:
                classificacao = "🏆 **EXCELENTE**"
                cor = "success"
                explicacao = "NPS excepcional! Seus clientes são verdadeiros defensores da marca."
            elif nps_valor >= 50:
                classificacao = "🌟 **MUITO BOM**"
                cor = "success"
                explicacao = "NPS muito bom! Maioria dos clientes recomendaria sua empresa."
            elif nps_valor >= 30:
                classificacao = "✅ **BOM**"
                cor = "info"
                explicacao = "NPS na zona de qualidade. Há espaço para melhorias."
            elif nps_valor >= 0:
                classificacao = "⚠️ **PRECISA MELHORAR**"
                cor = "warning"
                explicacao = "NPS na zona de melhoria. Foque em reduzir detratores."
            else:
                classificacao = "🚨 **CRÍTICO**"
                cor = "error"
                explicacao = "NPS negativo indica mais detratores que promotores. Ação urgente!"
            
            if cor == "success":
                st.success(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
            elif cor == "warning":
                st.warning(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
            elif cor == "error":
                st.error(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
            else:
                st.info(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
            
            # Benchmarking
            st.markdown("### 🎯 Benchmarking")
            benchmarks = {
                "Média Global": 32,
                "Média Brasil": 42,
                "Empresas Top": 70,
                "Classe Mundial": 80
            }
            
            for nome, valor in benchmarks.items():
                if nps_valor >= valor:
                    st.success(f"✅ {nome}: {valor} (Você: {nps_valor:.0f})")
                else:
                    diferenca = valor - nps_valor
                    st.info(f"🎯 {nome}: {valor} (Faltam {diferenca:.0f} pts)")
            
            # Amostra das respostas
            st.markdown("### 🔍 Amostra das Respostas")
            amostra = respostas_periodo.head(10).tolist()
            for i, resp in enumerate(amostra, 1):
                categoria = categorize_nps_from_text(resp)
                if categoria == "Promotor":
                    emoji, cor = "✅", "🟢"
                elif categoria == "Neutro":
                    emoji, cor = "➡️", "🟡"
                elif categoria == "Detrator":
                    emoji, cor = "❌", "🔴"
                else:
                    emoji, cor = "❓", "⚫"
                st.write(f"{i:2d}. `{resp}` {emoji} {categoria} {cor}")
            
            # Distribuição por dia
            if len(dados_periodo) > 0:
                st.markdown("### 📅 Distribuição Temporal")
                dados_tempo = dados_periodo.copy()
                dados_tempo['data_dia'] = dados_tempo[date_column].dt.date
                dist_diaria = dados_tempo.groupby('data_dia').size().reset_index()
                dist_diaria.columns = ['Data', 'Avaliações']
                dist_diaria = dist_diaria.sort_values('Data', ascending=False).head(10)
                st.dataframe(dist_diaria, use_container_width=True)
        
        # Calcular comparação
        if len(respostas_comparacao) > 0:
            categorias_comparacao = respostas_comparacao.apply(categorize_nps_from_text)
            promotores_comp = (categorias_comparacao == 'Promotor').sum()
            detratores_comp = (categorias_comparacao == 'Detrator').sum()
            neutros_comp = (categorias_comparacao == 'Neutro').sum()
            total_validas_comp = promotores_comp + neutros_comp + detratores_comp
            
            if total_validas_comp > 0:
                nps_comparacao = ((promotores_comp - detratores_comp) / total_validas_comp * 100)
                diferenca = nps_valor - nps_comparacao
                
                if diferenca > 5:
                    trend = f"↗️ +{diferenca:.0f} pts vs período anterior"
                    color_class = "metric-success"
                elif diferenca < -5:
                    trend = f"↘️ {diferenca:.0f} pts vs período anterior"
                    color_class = "metric-danger"
                else:
                    trend = f"➡️ {diferenca:+.0f} pts vs período anterior"
                    color_class = "metric-success" if nps_valor >= 50 else "metric-warning" if nps_valor >= 0 else "metric-danger"
            else:
                trend = f"{total_validas} avaliações ({periodo_dias} dias)"
                color_class = "metric-success" if nps_valor >= 50 else "metric-warning" if nps_valor >= 0 else "metric-danger"
        else:
            trend = f"{total_validas} avaliações ({periodo_dias} dias)"
            color_class = "metric-success" if nps_valor >= 50 else "metric-warning" if nps_valor >= 0 else "metric-danger"
            
        return f"{nps_valor:.0f}", trend, color_class, ""
    
    else:
        # === OUTRAS MÉTRICAS ===
        scores = respostas_periodo.apply(convert_text_score_to_number).dropna()
        
        if len(scores) == 0:
            return "N/A", "Erro na conversão", "metric-warning", ""
            
        valor = scores.mean()
        
        # Debug das outras métricas
        #with st.expander(f"🔍 Debug {column_name}"):
            #st.write(f"**📊 Conversões:** {len(scores)} de {len(respostas_periodo)}")
            #if len(scores) > 0:
                #st.write(f"**📊 Média:** {valor:.1f}/10")
                
                # Amostra das conversões
                #st.write("**🔍 Amostra:**")
                #amostra = respostas_periodo.head(8)
                #for i, resp in enumerate(amostra, 1):
                    #score = convert_text_score_to_number(resp)
                    #st.write(f"  {i}. `{resp}` → {score}")
        
        # Comparação
        if len(respostas_comparacao) > 0:
            scores_comp = respostas_comparacao.apply(convert_text_score_to_number).dropna()
            if len(scores_comp) > 0:
                valor_comp = scores_comp.mean()
                diferenca = valor - valor_comp
                
                if diferenca > 0.3:
                    trend = f"↗️ +{diferenca:.1f} vs anterior"
                    color_class = "metric-success"
                elif diferenca < -0.3:
                    trend = f"↘️ {diferenca:.1f} vs anterior"
                    color_class = "metric-danger"
                else:
                    trend = f"➡️ {diferenca:+.1f} vs anterior"
                    color_class = "metric-success" if valor >= 8 else "metric-warning" if valor >= 6 else "metric-danger"
            else:
                trend = f"{len(respostas_periodo)} avaliações"
                color_class = "metric-success" if valor >= 8 else "metric-warning" if valor >= 6 else "metric-danger"
        else:
            trend = f"{len(respostas_periodo)} avaliações"
            color_class = "metric-success" if valor >= 8 else "metric-warning" if valor >= 6 else "metric-danger"
            
        return f"{valor:.1f}/10", trend, color_class, ""
    
def show_executive_dashboard(df_clientes, df_pedidos, df_satisfacao, actions_log):
    """Dashboard executivo limpo com análises críticas estratégicas"""
    
    # KPIs principais em cards modernos
    st.markdown('<div class="section-header"><span class="emoji">📊</span><h2>Indicadores Principais</h2></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_clientes = len(df_clientes)
    clientes_ativos = len(df_clientes[df_clientes['status_churn'] == 'Ativo'])
    clientes_criticos = len(df_clientes[df_clientes['priority_score'] >= 200])
    receita_total = pd.to_numeric(df_clientes['receita'].str.replace(',', '.'), errors='coerce').sum()
    
    with col1:
        st.markdown(create_metric_card_with_explanation(
            "👥 Base de Clientes",
            f"{total_clientes:,}",
            "Últimos 24 meses",
            "metric-info",
            "Total de clientes únicos que fizeram pedidos nos últimos 2 anos"
        ), unsafe_allow_html=True)
    
    with col2:
        taxa_ativos = (clientes_ativos / total_clientes * 100) if total_clientes > 0 else 0
        color_class = "metric-success" if taxa_ativos >= 70 else "metric-warning"
        st.markdown(create_metric_card_with_explanation(
            "✅ Taxa de Retenção",
            f"{taxa_ativos:.1f}%",
            f"{clientes_ativos:,} clientes ativos",
            color_class,
            "Percentual de clientes que compraram recentemente (status Ativo)"
        ), unsafe_allow_html=True)
    
    with col3:
        taxa_criticos = (clientes_criticos / total_clientes * 100) if total_clientes > 0 else 0
        color_class = "metric-danger" if taxa_criticos >= 15 else "metric-warning" if taxa_criticos >= 10 else "metric-success"
        st.markdown(create_metric_card_with_explanation(
            "🚨 Clientes Críticos",
            f"{taxa_criticos:.1f}%",
            f"{clientes_criticos:,} precisam de atenção",
            color_class,
            "Clientes Premium/Gold em risco ou com alta prioridade de ação"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card_with_explanation(
            "💰 Receita Total",
            f"R$ {receita_total/1000:.0f}K",
            "Últimos 24 meses",
            "metric-success",
            "Soma de toda receita gerada pelos clientes da base ativa"
        ), unsafe_allow_html=True)
    
     # === ANÁLISE DE RECORRÊNCIA COM FILTRO DE DATA ===

    st.markdown('<div class="section-header"><span class="emoji">🔄</span><h2>Análise de Recorrência de Clientes</h2></div>', unsafe_allow_html=True)

    

    # Filtro de data específico para recorrência

    col1, col2, col3 = st.columns([2, 2, 1])

    

    with col1:

        # Data inicial - padrão últimos 6 meses

        data_inicio = st.date_input(

            "📅 Data inicial",

            value=datetime.now() - timedelta(days=180),
            format="DD/MM/YYYY",
            help="Data inicial para análise de recorrência"

        )

    

    with col2:

        # Data final - padrão hoje

        data_fim = st.date_input(

            "📅 Data final",

            value=datetime.now(),
            format="DD/MM/YYYY",
            help="Data final para análise de recorrência"

        )

    

    with col3:

        # Botão para aplicar filtro

        if st.button("🔍 Analisar Período", type="primary"):

            st.cache_data.clear()

    

    # Converter datas para datetime

    data_inicio_dt = pd.to_datetime(data_inicio)

    data_fim_dt = pd.to_datetime(data_fim)

    

    # Mostrar período selecionado

    st.info(f"📊 **Período de análise:** {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')} ({(data_fim_dt - data_inicio_dt).days} dias)")

    

    recurrence_data = analyze_client_recurrence(df_pedidos, data_inicio_dt, data_fim_dt)

    

    if recurrence_data:

        # Calcular período em dias para labels dinâmicos

        periodo_dias = (data_fim_dt - data_inicio_dt).days

        periodo_label = f"Período de {periodo_dias} dias"

        

        col1, col2, col3, col4 = st.columns(4)

        

        with col1:

            st.markdown(create_metric_card_with_explanation(

                "🆕 Novos Clientes",

                f"{recurrence_data.get('pedidos_primeira', 0):,}",

                periodo_label,

                "metric-info",

                f"Clientes que fizeram sua primeira compra no período selecionado ({data_inicio.strftime('%d/%m/%Y')} - {data_fim.strftime('%d/%m/%Y')})"

            ), unsafe_allow_html=True)

        

        with col2:

            st.markdown(create_metric_card_with_explanation(

                "🔄 Recompras",

                f"{recurrence_data.get('pedidos_recompra', 0):,}",

                periodo_label, 

                "metric-success",

                f"Pedidos de clientes que já haviam comprado antes no período selecionado"

            ), unsafe_allow_html=True)

        

        with col3:

            taxa_conversao = recurrence_data.get('taxa_conversao', 0)

            color_class = "metric-success" if taxa_conversao >= 30 else "metric-warning" if taxa_conversao >= 15 else "metric-danger"

            st.markdown(create_metric_card_with_explanation(

                "📈 Taxa de Conversão",

                f"{taxa_conversao:.1f}%",

                "Primeira → Recompra",

                color_class,

                "% de clientes únicos que fizeram primeira compra e depois recompraram no período"

            ), unsafe_allow_html=True)

        

        with col4:

            ticket_primeira = recurrence_data.get('ticket_primeira', 0)

            ticket_recompra = recurrence_data.get('ticket_recompra', 0)

            diferenca = ((ticket_recompra - ticket_primeira) / ticket_primeira * 100) if ticket_primeira > 0 else 0

            

            color_class = "metric-success" if diferenca > 0 else "metric-warning"

            delta_text = f"↗️ +{diferenca:.1f}% vs 1ª compra" if diferenca > 0 else f"↘️ {diferenca:.1f}% vs 1ª compra" if diferenca < 0 else "➡️ Igual à 1ª compra"

            

            st.markdown(create_metric_card_with_explanation(

                "💰 Ticket Recompra",

                f"R$ {ticket_recompra:,.0f}",

                delta_text,

                color_class,

                "Valor médio dos pedidos de recompra vs primeira compra no período"

            ), unsafe_allow_html=True)

        

        # Gráficos de recorrência

        col1, col2 = st.columns(2)

        

        with col1:

            # Gráfico de pizza: primeira vs recompra (período completo)

            labels = ['Primeira Compra', 'Recompra']

            values = [recurrence_data.get('pedidos_primeira', 0), recurrence_data.get('pedidos_recompra', 0)]

            

            if sum(values) > 0:  # Só criar gráfico se houver dados

                fig_recorrencia = px.pie(

                    values=values,

                    names=labels,

                    title=f"Distribuição no Período ({periodo_dias} dias)",

                    color=labels,

                    color_discrete_map={

                        'Primeira Compra': COLORS['warning'],

                        'Recompra': COLORS['success']

                    }

                )

                

                fig_recorrencia.update_traces(

                    textposition='inside',

                    textinfo='percent+label',

                    textfont_size=12

                )

                

                fig_recorrencia.update_layout(

                    font=dict(family="Inter", size=12),

                    height=300,

                    margin=dict(t=50, b=0, l=0, r=0)

                )

                

                st.plotly_chart(fig_recorrencia, use_container_width=True)

            else:

                st.info("📊 Aguardando dados para gerar gráfico...")

        

        with col2:

            # Comparação de tickets médios (período completo)

            if ticket_primeira > 0 or ticket_recompra > 0:  # Só criar gráfico se houver dados

                ticket_data = pd.DataFrame({

                    'Tipo': ['Primeira Compra', 'Recompra'],

                    'Ticket Médio': [ticket_primeira, ticket_recompra]

                })

                

                fig_ticket = px.bar(

                    ticket_data,

                    x='Tipo',

                    y='Ticket Médio',

                    title=f"Ticket Médio no Período ({periodo_dias} dias)",

                    color='Tipo',

                    color_discrete_map={

                        'Primeira Compra': COLORS['warning'],

                        'Recompra': COLORS['success']

                    }

                )

                

                fig_ticket.update_layout(

                    font=dict(family="Inter", size=12),

                    height=300,

                    margin=dict(t=50, b=0, l=0, r=0),

                    showlegend=False

                )

                

                fig_ticket.update_traces(

                    hovertemplate='<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>'

                )

                

                st.plotly_chart(fig_ticket, use_container_width=True)

            else:

                st.info("💰 Aguardando dados de ticket médio...")

    

    else:

        st.warning(f"📊 Nenhum dado de recorrência encontrado no período de {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}. Tente selecionar um período diferente ou verifique se a aba 'pedidos_com_id2' contém dados neste intervalo.")

    

    # Status da Base de Clientes

    st.markdown('<div class="section-header"><span class="emoji">🔄</span><h2>Status da Base de Clientes</h2></div>', unsafe_allow_html=True)

    

    col1, col2, col3, col4 = st.columns(4)

    

    with col1:

        st.markdown(create_metric_card_with_explanation(

            "👥 Base Total",

            f"{total_clientes:,}",

            "Clientes únicos",

            "metric-info",

            "Clientes com pelo menos 1 pedido nos últimos 24 meses"

        ), unsafe_allow_html=True)

    

    with col2:

        clientes_ativos = len(df_clientes[df_clientes['status_churn'] == 'Ativo'])

        taxa_ativos = (clientes_ativos / total_clientes * 100) if total_clientes > 0 else 0

        color_class = "metric-success" if taxa_ativos >= 50 else "metric-warning"

        st.markdown(create_metric_card_with_explanation(

            "✅ Ativos",

            f"{clientes_ativos:,}",

            f"{taxa_ativos:.1f}% da base",

            color_class,

            "Compraram dentro do prazo esperado para seu perfil"

        ), unsafe_allow_html=True)

    

    with col3:

        clientes_inativos = len(df_clientes[df_clientes['status_churn'] == 'Inativo'])

        taxa_inativos = (clientes_inativos / total_clientes * 100) if total_clientes > 0 else 0

        color_class = "metric-danger" if taxa_inativos >= 30 else "metric-warning"

        st.markdown(create_metric_card_with_explanation(

            "😴 Inativos",

            f"{clientes_inativos:,}",

            f"{taxa_inativos:.1f}% da base",

            color_class,

            "Não compram há muito tempo (>3x intervalo normal)"

        ), unsafe_allow_html=True)

    

    with col4:

        clientes_dormant = len(df_clientes[df_clientes['status_churn'].str.contains('Dormant', na=False)])

        taxa_dormant = (clientes_dormant / total_clientes * 100) if total_clientes > 0 else 0

        color_class = "metric-warning" if taxa_dormant >= 15 else "metric-success"

        st.markdown(create_metric_card_with_explanation(

            "💤 Dormant",

            f"{clientes_dormant:,}",

            f"{taxa_dormant:.1f}% da base",

            color_class,

            "Atrasados para próxima compra (>2x intervalo normal)"

        ), unsafe_allow_html=True)

    
    # === AVALIAÇÃO DO CLIENTE - VERSÃO LIMPA ===
    st.markdown('<div class="section-header"><span class="emoji">😊</span><h2>Avaliação do Cliente</h2></div>', unsafe_allow_html=True)
    
    # === FILTROS DE DATA PERSONALIZADOS ===
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        with col1:
            usar_periodo_custom = st.checkbox("🔧 Personalizar período", help="Marque para definir datas específicas")
        
        if usar_periodo_custom:
            with col2:
                data_inicio_custom = st.date_input(
                    "📅 Data inicial",
                    value=datetime.now() - timedelta(days=30),
                    format="DD/MM/YYYY",
                    help="Data inicial para análise"
                )
            
            with col3:
                data_fim_custom = st.date_input(
                    "📅 Data final", 
                    value=datetime.now(),
                    format="DD/MM/YYYY",
                    help="Data final para análise"
                )
                
            with col4:
                if st.button("🔍 Aplicar", type="primary", key="apply_custom_period"):
                    st.cache_data.clear()
        else:
            # Período padrão (últimos 30 dias)
            data_fim_custom = datetime.now().date()
            data_inicio_custom = data_fim_custom - timedelta(days=30)
        
        # Mostrar período e total de respostas
        periodo_dias = (data_fim_custom - data_inicio_custom).days if hasattr(data_fim_custom, 'days') else (pd.to_datetime(data_fim_custom) - pd.to_datetime(data_inicio_custom)).days
        
        # Calcular total de respostas no período para mostrar
        total_respostas_periodo = 0
        if not df_satisfacao.empty:
            date_column = None
            for col in df_satisfacao.columns:
                if any(x in col.lower() for x in ['carimbo', 'data', 'timestamp', 'time']):
                    date_column = col
                    break
            
            if date_column:
                # Converter datas para datetime adequadamente
                data_inicio_dt = pd.to_datetime(data_inicio_custom)
                data_fim_dt = pd.to_datetime(data_fim_custom) + pd.Timedelta(hours=23, minutes=59, seconds=59)
                
                df_periodo = df_satisfacao[
                    (df_satisfacao[date_column] >= data_inicio_dt) & 
                    (df_satisfacao[date_column] <= data_fim_dt)
                ]
                total_respostas_periodo = len(df_periodo.dropna(subset=[date_column]))
        
        st.info(f"📊 **Período:** {pd.to_datetime(data_inicio_custom).strftime('%d/%m/%Y')} até {pd.to_datetime(data_fim_custom).strftime('%d/%m/%Y')} ({periodo_dias} dias) • **{total_respostas_periodo} respostas**")
    
    # === MÉTRICAS LIMPAS ===
    if df_satisfacao.empty:
        col1, col2, col3, col4 = st.columns(4)
        for i, (col, title, icon) in enumerate([(col1, "Atendimento", "🎧"), (col2, "Produto", "📦"), (col3, "Prazo", "⏰"), (col4, "NPS", "📈")]):
            with col:
                st.markdown(create_metric_card_with_explanation(
                    f"{icon} {title}", "N/A", "Sem dados", "metric-info", "Dados de pesquisa não disponíveis"
                ), unsafe_allow_html=True)
    else:
        # Buscar colunas automaticamente
        atendimento_col = produto_col = prazo_col = nps_col = None
        
        for col in df_satisfacao.columns:
            col_lower = col.lower()
            if 'atendimento' in col_lower and not atendimento_col:
                atendimento_col = col
            elif 'produto' in col_lower and not produto_col:
                produto_col = col
            elif 'prazo' in col_lower and not prazo_col:
                prazo_col = col
            elif any(x in col_lower for x in ['possibilidade', 'recomenda']) and not nps_col:
                nps_col = col
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Guardar dados do NPS para análise expandível
        nps_data = None
        
        with col1:
            if atendimento_col:
                value, delta, color, _ = calculate_satisfaction_clean(
                    df_satisfacao, atendimento_col, False, data_inicio_custom, data_fim_custom
                )
                st.markdown(create_metric_card_with_explanation(
                    "🎧 Atendimento", value, delta, color, ""
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card_with_explanation(
                    "🎧 Atendimento", "N/A", "Coluna não encontrada", "metric-info", ""
                ), unsafe_allow_html=True)
        
        with col2:
            if produto_col:
                value, delta, color, _ = calculate_satisfaction_clean(
                    df_satisfacao, produto_col, False, data_inicio_custom, data_fim_custom
                )
                st.markdown(create_metric_card_with_explanation(
                    "📦 Produto", value, delta, color, ""
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card_with_explanation(
                    "📦 Produto", "N/A", "Coluna não encontrada", "metric-info", ""
                ), unsafe_allow_html=True)
        
        with col3:
            if prazo_col:
                value, delta, color, _ = calculate_satisfaction_clean(
                    df_satisfacao, prazo_col, False, data_inicio_custom, data_fim_custom
                )
                st.markdown(create_metric_card_with_explanation(
                    "⏰ Prazo", value, delta, color, ""
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card_with_explanation(
                    "⏰ Prazo", "N/A", "Coluna não encontrada", "metric-info", ""
                ), unsafe_allow_html=True)
        
        with col4:
            if nps_col:
                value, delta, color, nps_data = calculate_satisfaction_clean(
                    df_satisfacao, nps_col, True, data_inicio_custom, data_fim_custom
                )
                st.markdown(create_metric_card_with_explanation(
                    "📈 NPS", value, delta, color, ""
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card_with_explanation(
                    "📈 NPS", "N/A", "Coluna não encontrada", "metric-info", ""
                ), unsafe_allow_html=True)
        
        # === ANÁLISE EXPANDÍVEL DO NPS (ABAIXO DOS CARDS) ===
        if nps_data and nps_col:
            show_nps_detailed_analysis(nps_data, data_inicio_custom, data_fim_custom)
        
        # === ANÁLISE DE DETRATORES ===
        if nps_data and nps_data.get('detratores', 0) > 0:
            show_detractors_analysis(df_satisfacao, nps_col, data_inicio_custom, data_fim_custom, nps_data)
    
    # Distribuição visual moderna (mantido igual)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header"><span class="emoji">🏆</span><h2>Distribuição por Nível</h2></div>', unsafe_allow_html=True)
        
        nivel_counts = df_clientes['nivel_cliente'].value_counts()
        
        fig_nivel = px.pie(
            values=nivel_counts.values,
            names=nivel_counts.index,
            title="",
            color=nivel_counts.index,
            color_discrete_map=CHART_COLORS['nivel'],
            hole=0.4
        )
        
        fig_nivel.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>%{value} clientes<br>%{percent}<extra></extra>'
        )
        
        fig_nivel.update_layout(
            font=dict(family="Inter", size=12),
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=300
        )
        
        st.plotly_chart(fig_nivel, use_container_width=True)
        
        # Métricas de nível
        for nivel, count in nivel_counts.items():
            percentage = (count / total_clientes) * 100
            color = CHART_COLORS['nivel'].get(nivel, COLORS['info'])
            st.markdown(create_progress_bar(count, total_clientes, f"{nivel}", color), unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header"><span class="emoji">⚠️</span><h2>Status de Risco</h2></div>', unsafe_allow_html=True)
        
        # Agrupar riscos para melhor visualização
        risco_agrupado = df_clientes['risco_recencia'].map({
            'Alto': 'Alto Risco', 'Novo_Alto': 'Alto Risco',
            'Médio': 'Médio Risco', 'Novo_Médio': 'Médio Risco', 
            'Baixo': 'Baixo Risco', 'Novo_Baixo': 'Baixo Risco'
        }).value_counts()
        
        fig_risco = px.bar(
            x=risco_agrupado.values,
            y=risco_agrupado.index,
            orientation='h',
            title="",
            color=risco_agrupado.index,
            color_discrete_map={
                'Alto Risco': COLORS['danger'],
                'Médio Risco': COLORS['warning'],
                'Baixo Risco': COLORS['success']
            }
        )
        
        fig_risco.update_layout(
            font=dict(family="Inter", size=12),
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            height=300,
            yaxis=dict(title=None),
            xaxis=dict(title="Quantidade de Clientes")
        )
        
        fig_risco.update_traces(
            hovertemplate='<b>%{y}</b><br>%{x} clientes<extra></extra>'
        )
        
        st.plotly_chart(fig_risco, use_container_width=True)
    
    # === ANÁLISES CRÍTICAS ESTRATÉGICAS (SUBSTITUI ALERTAS ALEATÓRIOS) ===
    show_strategic_critical_analysis(df_clientes, df_satisfacao, nps_data if nps_data else {})


# === FUNÇÃO DE CÁLCULO LIMPA (SEM DEBUG EXCESSIVO) ===
def calculate_satisfaction_clean(df_satisfacao, column_name, is_nps=False, data_inicio=None, data_fim=None):
    """Versão limpa sem debug excessivo"""
    if df_satisfacao.empty:
        return "N/A", "Sem dados", "metric-info", {}
    
    # Converter datas adequadamente
    data_inicio_dt = pd.to_datetime(data_inicio) if data_inicio else datetime.now() - timedelta(days=30)
    data_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(hours=23, minutes=59, seconds=59) if data_fim else datetime.now()
    
    # Buscar coluna de data
    date_column = None
    for col in df_satisfacao.columns:
        if any(x in col.lower() for x in ['carimbo', 'data', 'timestamp', 'time']):
            date_column = col
            break
    
    if not date_column or column_name not in df_satisfacao.columns:
        return "N/A", "Coluna não encontrada", "metric-info", {}
    
    # Filtrar dados no período
    df_valid = df_satisfacao.dropna(subset=[date_column])
    dados_periodo = df_valid[
        (df_valid[date_column] >= data_inicio_dt) & 
        (df_valid[date_column] <= data_fim_dt)
    ]
    
    respostas_periodo = dados_periodo[column_name].dropna()
    
    if len(respostas_periodo) == 0:
        return "N/A", "Sem dados no período", "metric-warning", {}
    
    # Calcular período de comparação
    periodo_dias = (data_fim_dt - data_inicio_dt).days
    inicio_comparacao = data_inicio_dt - timedelta(days=periodo_dias)
    fim_comparacao = data_inicio_dt
    
    dados_comparacao = df_valid[
        (df_valid[date_column] >= inicio_comparacao) & 
        (df_valid[date_column] < fim_comparacao)
    ]
    respostas_comparacao = dados_comparacao[column_name].dropna()
    
    if is_nps:
        # Cálculo NPS
        categorias_periodo = respostas_periodo.apply(categorize_nps_from_text)
        promotores = (categorias_periodo == 'Promotor').sum()
        neutros = (categorias_periodo == 'Neutro').sum()
        detratores = (categorias_periodo == 'Detrator').sum()
        total_validas = promotores + neutros + detratores
        
        if total_validas == 0:
            return "N/A", "Sem respostas válidas", "metric-warning", {}
            
        nps_valor = ((promotores - detratores) / total_validas * 100)
        
        # Dados para análise detalhada
        nps_data = {
            'nps_valor': nps_valor,
            'promotores': promotores,
            'neutros': neutros,
            'detratores': detratores,
            'total_validas': total_validas,
            'respostas_raw': respostas_periodo,
            'dados_periodo': dados_periodo,
            'categorias': categorias_periodo
        }
        
        # Comparação com período anterior
        if len(respostas_comparacao) > 0:
            categorias_comp = respostas_comparacao.apply(categorize_nps_from_text)
            promotores_comp = (categorias_comp == 'Promotor').sum()
            detratores_comp = (categorias_comp == 'Detrator').sum()
            neutros_comp = (categorias_comp == 'Neutro').sum()
            total_comp = promotores_comp + neutros_comp + detratores_comp
            
            if total_comp > 0:
                nps_comp = ((promotores_comp - detratores_comp) / total_comp * 100)
                diferenca = nps_valor - nps_comp
                
                if diferenca > 5:
                    trend = f"↗️ +{diferenca:.0f} pts vs anterior"
                    color_class = "metric-success"
                elif diferenca < -5:
                    trend = f"↘️ {diferenca:.0f} pts vs anterior"
                    color_class = "metric-danger"
                else:
                    trend = f"➡️ {diferenca:+.0f} pts vs anterior"
                    color_class = "metric-success" if nps_valor >= 50 else "metric-warning" if nps_valor >= 0 else "metric-danger"
            else:
                trend = f"{total_validas} avaliações"
                color_class = "metric-success" if nps_valor >= 50 else "metric-warning" if nps_valor >= 0 else "metric-danger"
        else:
            trend = f"{total_validas} avaliações"
            color_class = "metric-success" if nps_valor >= 50 else "metric-warning" if nps_valor >= 0 else "metric-danger"
            
        return f"{nps_valor:.0f}", trend, color_class, nps_data
    
    else:
        # Outras métricas
        scores = respostas_periodo.apply(convert_text_score_to_number).dropna()
        
        if len(scores) == 0:
            return "N/A", "Erro na conversão", "metric-warning", {}
            
        valor = scores.mean()
        
        if len(respostas_comparacao) > 0:
            scores_comp = respostas_comparacao.apply(convert_text_score_to_number).dropna()
            if len(scores_comp) > 0:
                valor_comp = scores_comp.mean()
                diferenca = valor - valor_comp
                
                if diferenca > 0.3:
                    trend = f"↗️ +{diferenca:.1f} vs anterior"
                    color_class = "metric-success"
                elif diferenca < -0.3:
                    trend = f"↘️ {diferenca:.1f} vs anterior"
                    color_class = "metric-danger"
                else:
                    trend = f"➡️ {diferenca:+.1f} vs anterior"
                    color_class = "metric-success" if valor >= 8 else "metric-warning" if valor >= 6 else "metric-danger"
            else:
                trend = f"{len(respostas_periodo)} avaliações"
                color_class = "metric-success" if valor >= 8 else "metric-warning" if valor >= 6 else "metric-danger"
        else:
            trend = f"{len(respostas_periodo)} avaliações"
            color_class = "metric-success" if valor >= 8 else "metric-warning" if valor >= 6 else "metric-danger"
            
        return f"{valor:.1f}/10", trend, color_class, {}


# === ANÁLISE DETALHADA DO NPS (EXPANDÍVEL) ===
def show_nps_detailed_analysis(nps_data, data_inicio, data_fim):
    """Mostra análise detalhada do NPS em expander"""
    with st.expander(f"🎯 Análise Completa do NPS ({pd.to_datetime(data_inicio).strftime('%d/%m')} - {pd.to_datetime(data_fim).strftime('%d/%m')})"):
        st.markdown("### 📊 Categorização das Respostas")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("✅ Promotores", f"{nps_data['promotores']}", help="Notas 9-10: Clientes entusiasmados")
        with col2:
            st.metric("➡️ Neutros", f"{nps_data['neutros']}", help="Notas 7-8: Clientes satisfeitos mas passivos")
        with col3:
            st.metric("❌ Detratores", f"{nps_data['detratores']}", help="Notas 0-6: Clientes insatisfeitos")
        with col4:
            st.metric("📊 Total Válidas", f"{nps_data['total_validas']}")
        
        st.markdown("---")
        st.markdown("### 🧮 Cálculo do NPS")
        st.markdown(f"""
        **Fórmula:** `NPS = ((Promotores - Detratores) / Total Válidas) × 100`
        
        **Seu cálculo:**
        ```
        NPS = (({nps_data['promotores']} - {nps_data['detratores']}) / {nps_data['total_validas']}) × 100
        NPS = ({nps_data['promotores'] - nps_data['detratores']} / {nps_data['total_validas']}) × 100  
        NPS = {(nps_data['promotores'] - nps_data['detratores']) / nps_data['total_validas']:.3f} × 100
        NPS = {nps_data['nps_valor']:.1f}
        ```
        """)
        
        st.markdown("---")
        st.markdown("### 📈 Interpretação do Resultado")
        
        nps_valor = nps_data['nps_valor']
        # Classificação do NPS
        if nps_valor >= 75:
            classificacao = "🏆 **EXCELENTE**"
            explicacao = "NPS excepcional! Seus clientes são verdadeiros defensores da marca."
            st.success(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
        elif nps_valor >= 50:
            classificacao = "🌟 **MUITO BOM**"
            explicacao = "NPS muito bom! Maioria dos clientes recomendaria sua empresa."
            st.success(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
        elif nps_valor >= 30:
            classificacao = "✅ **BOM**"
            explicacao = "NPS na zona de qualidade. Há espaço para melhorias."
            st.info(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
        elif nps_valor >= 0:
            classificacao = "⚠️ **PRECISA MELHORAR**"
            explicacao = "NPS na zona de melhoria. Foque em reduzir detratores."
            st.warning(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
        else:
            classificacao = "🚨 **CRÍTICO**"
            explicacao = "NPS negativo indica mais detratores que promotores. Ação urgente!"
            st.error(f"{classificacao}: {nps_valor:.0f} - {explicacao}")
        
        # Benchmarking
        st.markdown("### 🎯 Benchmarking")
        benchmarks = {
            "Média Global": 32,
            "Média Brasil": 42,
            "Empresas Top": 70,
            "Classe Mundial": 80
        }
        
        for nome, valor in benchmarks.items():
            if nps_valor >= valor:
                st.success(f"✅ {nome}: {valor} (Você: {nps_valor:.0f})")
            else:
                diferenca = valor - nps_valor
                st.info(f"🎯 {nome}: {valor} (Faltam {diferenca:.0f} pts)")


# === ANÁLISE DE DETRATORES ===
def show_detractors_analysis(df_satisfacao, nps_col, data_inicio, data_fim, nps_data):
    """Análise específica dos detratores"""
    st.markdown('<div class="section-header"><span class="emoji">🔍</span><h2>Análise de Detratores</h2></div>', unsafe_allow_html=True)
    
    detratores_count = nps_data.get('detratores', 0)
    total_validas = nps_data.get('total_validas', 1)
    taxa_detratores = (detratores_count / total_validas * 100)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        color_class = "metric-danger" if taxa_detratores > 15 else "metric-warning" if taxa_detratores > 10 else "metric-success"
        st.markdown(create_metric_card_with_explanation(
            "❌ Detratores",
            f"{detratores_count}",
            f"{taxa_detratores:.1f}% do total",
            color_class,
            "Clientes que deram notas de 0 a 6"
        ), unsafe_allow_html=True)
    
    with col2:
        if detratores_count > 0:
            # Meta: reduzir detratores em 50%
            meta_reducao = max(1, detratores_count // 2)
            novo_nps = ((nps_data['promotores'] - meta_reducao) / total_validas * 100)
            ganho = novo_nps - nps_data['nps_valor']
            
            st.markdown(create_metric_card_with_explanation(
                "📈 Potencial de Melhoria",
                f"+{ganho:.0f}",
                f"pts se reduzir 50% detratores",
                "metric-info",
                f"NPS subiria para {novo_nps:.0f} convertendo {meta_reducao} detratores"
            ), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card_with_explanation(
                "🎉 Sem Detratores",
                "0",
                "Excelente resultado!",
                "metric-success",
                "Nenhum cliente insatisfeito no período"
            ), unsafe_allow_html=True)
    
    with col3:
        if detratores_count > 0:
            st.markdown(create_metric_card_with_explanation(
                "🎯 Ação Recomendada",
                "Contato",
                "Direto com detratores",
                "metric-warning",
                "Fazer contato individual para entender problemas"
            ), unsafe_allow_html=True)
        else:
            st.markdown(create_metric_card_with_explanation(
                "✅ Status",
                "Ótimo",
                "Manter qualidade",
                "metric-success",
                "Continuar com as práticas atuais"
            ), unsafe_allow_html=True)


# === ANÁLISES CRÍTICAS ESTRATÉGICAS ===
def show_strategic_critical_analysis(df_clientes, df_satisfacao, nps_data):
    """Análises críticas estratégicas ao invés de alertas aleatórios"""
    st.markdown('<div class="section-header"><span class="emoji">📊</span><h2>Análises Críticas</h2></div>', unsafe_allow_html=True)
    
    # Análises estratégicas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Clientes Premium em Risco")
        
        premium_em_risco = df_clientes[
            (df_clientes['nivel_cliente'].isin(['Premium', 'Gold'])) &
            (df_clientes['risco_recencia'].isin(['Alto', 'Novo_Alto', 'Médio', 'Novo_Médio']))
        ]
        
        total_premium = len(df_clientes[df_clientes['nivel_cliente'].isin(['Premium', 'Gold'])])
        premium_risco_count = len(premium_em_risco)
        taxa_premium_risco = (premium_risco_count / max(total_premium, 1)) * 100
        
        if premium_risco_count > 0:
            receita_em_risco = pd.to_numeric(premium_em_risco['receita'].str.replace(',', '.'), errors='coerce').sum()
            
            st.error(f"🚨 **{premium_risco_count} clientes Premium/Gold em risco** ({taxa_premium_risco:.1f}%)")
            st.write(f"💰 Receita em risco: R$ {receita_em_risco/1000:.0f}K")
            
            # Top 3 mais críticos
            top_criticos = premium_em_risco.nlargest(3, 'priority_score')
            st.write("**🎯 Top 3 mais críticos:**")
            for _, cliente in top_criticos.iterrows():
                st.write(f"• {cliente.get('nome', 'N/A')} ({cliente.get('nivel_cliente', 'N/A')}) - Score: {cliente.get('priority_score', 0):.0f}")
        else:
            st.success("✅ Nenhum cliente Premium/Gold em risco no momento!")
    
    with col2:
        st.markdown("### 📉 Métricas em Declínio")
        
        # Simular algumas métricas em declínio (em uma implementação real, você compararia períodos)
        metricas_declinio = []
        
        # Se temos dados de NPS
        if nps_data and nps_data.get('nps_valor', 0) < 50:
            metricas_declinio.append("📈 NPS abaixo da meta (50+)")
        
        # Clientes inativos crescendo
        taxa_inativos = len(df_clientes[df_clientes['status_churn'] == 'Inativo']) / len(df_clientes) * 100
        if taxa_inativos > 25:
            metricas_declinio.append(f"😴 Taxa de inativos alta ({taxa_inativos:.1f}%)")
        
        # Clientes dormant
        taxa_dormant = len(df_clientes[df_clientes['status_churn'].str.contains('Dormant', na=False)]) / len(df_clientes) * 100
        if taxa_dormant > 20:
            metricas_declinio.append(f"💤 Muitos clientes Dormant ({taxa_dormant:.1f}%)")
        
        # Mostrar métricas problemáticas
        if metricas_declinio:
            st.warning("⚠️ **Atenção necessária:**")
            for metrica in metricas_declinio:
                st.write(f"• {metrica}")
        else:
            st.success("✅ Todas as métricas principais estão saudáveis!")
        
        # Recomendações
        st.markdown("**💡 Recomendações:**")
        if taxa_inativos > 25:
            st.write("• Campanha de reativação de clientes inativos")
        if nps_data and nps_data.get('detratores', 0) > 0:
            st.write(f"• Contato direto com {nps_data['detratores']} detratores")
        if taxa_dormant > 20:
            st.write("• Programa de incentivos para clientes Dormant")
        
        if not metricas_declinio:
            st.write("• Manter práticas atuais de CS")
            st.write("• Focar em expansão da base")
    
    # Resumo executivo
    st.markdown("---")
    st.markdown("### 📋 Resumo Executivo")
    
    total_acoes_necessarias = premium_risco_count + len(metricas_declinio)
    
    if total_acoes_necessarias == 0:
        st.success("🎉 **Situação Excelente:** Todos os indicadores estão saudáveis. Continuar com as práticas atuais de Customer Success.")
    elif total_acoes_necessarias <= 2:
        st.warning(f"⚠️ **Atenção Moderada:** {total_acoes_necessarias} pontos requerem atenção. Priorizar ações corretivas.")
    else:
        st.error(f"🚨 **Ação Urgente:** {total_acoes_necessarias} pontos críticos identificados. Reunião de CS recomendada.")
    
    # Próximos passos
    if premium_risco_count > 0:
        st.info(f"🎯 **Próxima ação:** Contato com {min(3, premium_risco_count)} clientes Premium de maior risco nas próximas 48h.")

def show_client_management_enhanced(df_clientes, actions_log):
    """Gestão de clientes aprimorada"""
    
    # Inicializar session state para paginação
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    st.markdown('<div class="section-header"><span class="emoji">👥</span><h2>Gestão de Clientes</h2></div>', unsafe_allow_html=True)
    
    # Filtros avançados em container
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.markdown("**🔍 Filtros Avançados**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            nivel_filter = st.multiselect(
                "🏆 Nível",
                options=df_clientes['nivel_cliente'].unique(),
                default=df_clientes['nivel_cliente'].unique()
            )
        
        with col2:
            risco_filter = st.multiselect(
                "⚠️ Risco",
                options=df_clientes['risco_recencia'].unique(),
                default=df_clientes['risco_recencia'].unique()
            )
        
        with col3:
            churn_filter = st.multiselect(
                "🔄 Status",
                options=df_clientes['status_churn'].unique(),
                default=df_clientes['status_churn'].unique()
            )
        
        with col4:
            search_term = st.text_input("🔍 Buscar cliente", placeholder="Nome ou email...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Aplicar filtros
    df_filtered = df_clientes[
        (df_clientes['nivel_cliente'].isin(nivel_filter)) &
        (df_clientes['risco_recencia'].isin(risco_filter)) &
        (df_clientes['status_churn'].isin(churn_filter))
    ]
    
    if search_term:
        df_filtered = df_filtered[
            df_filtered['nome'].str.contains(search_term, case=False, na=False) |
            df_filtered['email'].str.contains(search_term, case=False, na=False)
        ]
    
    # Reset página se filtros mudaram
    if len(df_filtered) != st.session_state.get('last_filtered_count', -1):
        st.session_state.current_page = 1
        st.session_state.last_filtered_count = len(df_filtered)
    
    # Estatísticas dos filtros (sem botões de exportação)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Clientes Filtrados", f"{len(df_filtered):,}")
    with col2:
        avg_score = df_filtered['priority_score'].mean() if len(df_filtered) > 0 else 0
        st.metric("🎯 Score Médio", f"{avg_score:.1f}")
    with col3:
        receita_filtrada = pd.to_numeric(df_filtered['receita'].str.replace(',', '.'), errors='coerce').sum()
        st.metric("💰 Receita Filtrada", f"R$ {receita_filtrada/1000:.0f}K")
    
    # Lista de clientes com design melhorado
    if len(df_filtered) > 0:
        st.markdown("### 📋 Lista de Clientes")
        
        # Paginação
        items_per_page = 10
        total_pages = (len(df_filtered) - 1) // items_per_page + 1
        
        # Navegação de páginas melhorada
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        current_page = st.session_state.current_page
        
        with col1:
            if st.button("⬅️ Anterior", disabled=(current_page <= 1)):
                if current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
        
        with col2:
            if st.button("Primeira", disabled=(current_page <= 1)):
                st.session_state.current_page = 1
                st.rerun()
        
        with col3:
            page = st.selectbox(
                "Página",
                range(1, total_pages + 1),
                index=current_page - 1,
                format_func=lambda x: f"Página {x} de {total_pages}",
                key="page_selector"
            )
            
            if page != current_page:
                st.session_state.current_page = page
                st.rerun()
        
        with col4:
            if st.button("Última", disabled=(current_page >= total_pages)):
                st.session_state.current_page = total_pages
                st.rerun()
        
        with col5:
            if st.button("Próxima ➡️", disabled=(current_page >= total_pages)):
                if current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
        
        # Usar página do session_state
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        df_page = df_filtered.iloc[start_idx:end_idx]
        
        for _, cliente in df_page.iterrows():
            nivel = cliente.get('nivel_cliente', 'N/A')
            with st.expander(f"🏷️ {cliente.get('nome', 'N/A')} - {nivel}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    **📊 Informações Básicas:**
                    - 📧 **Email:** {cliente.get('email', 'N/A')}
                    - 📱 **Telefone:** {format_phone_number(cliente.get('telefone1', 'N/A'))}
                    - 🏢 **CNPJ:** {cliente.get('cpfcnpj', 'N/A')}
                    - 📍 **Localização:** {cliente.get('cidade', 'N/A')}, {cliente.get('estado', 'N/A')}
                    
                    **📈 Métricas de Performance:**
                    - 🔄 **Frequência:** {cliente.get('frequency', 0)} pedidos
                    - 💰 **Receita Total:** R$ {cliente.get('receita', '0')}
                    - 📅 **Última Compra:** {cliente.get('recency_days', 0)} dias atrás
                    - ⏰ **Intervalo Médio:** {float(str(cliente.get('ipt_cliente', 0)).replace(',', '.')) if cliente.get('ipt_cliente') else 0:.1f} dias
                    - 🎯 **Score Final:** {cliente.get('score_final', 0)}
                    
                    **⚠️ Status Atual:**
                    - 🏆 **Nível:** {cliente.get('nivel_cliente', 'N/A')}
                    - 📊 **Risco:** {cliente.get('risco_recencia', 'N/A')}
                    - 🔄 **Churn:** {cliente.get('status_churn', 'N/A')}
                    - 💎 **Top 20%:** {cliente.get('top_20_valor', 'N/A')}
                    """)
                
                with col2:
                    st.markdown("**🎯 Ação Recomendada:**")
                    acao = cliente.get('acao_sugerida', 'Nenhuma ação sugerida')
                    st.info(acao)
                    
                    if st.button(f"✅ Executar Ação", key=f"action_{cliente.get('cliente_unico_id', 'unknown')}"):
                        action_data = {
                            'cliente_id': cliente.get('cliente_unico_id'),
                            'cliente_nome': cliente.get('nome'),
                            'acao': acao,
                            'status': 'executada',
                            'executado_por': 'Usuário'
                        }
                        save_action_log(action_data)
                        st.success(f"✅ Ação registrada para {cliente.get('nome', 'cliente')}")
                        st.rerun()
        
        # Seção de exportação embaixo da lista
        st.markdown("---")
        st.markdown("### 📤 Exportar Dados")
        st.markdown("Exporte os dados filtrados nos formatos disponíveis:")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if len(df_filtered) > 0:
                excel_data = export_to_excel(df_filtered)
                if excel_data is not None:
                    st.download_button(
                        "📊 Excel (.xlsx)",
                        data=excel_data,
                        file_name=f"clientes_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                else:
                    st.button("📊 Excel (.xlsx)", disabled=True, help="Instale openpyxl: pip install openpyxl", use_container_width=True)
            else:
                st.button("📊 Excel (.xlsx)", disabled=True, use_container_width=True)
        
        with col2:
            if len(df_filtered) > 0:
                csv_data = export_to_csv(df_filtered)
                st.download_button(
                    "📄 CSV (.csv)",
                    data=csv_data,
                    file_name=f"clientes_filtrados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.button("📄 CSV (.csv)", disabled=True, use_container_width=True)
        
        with col3:
            st.info(f"📊 Total de {len(df_filtered):,} clientes serão exportados com os filtros aplicados.")
    
    else:
        st.warning("😔 Nenhum cliente encontrado com os filtros aplicados.")

def show_analytics_dashboard(df_clientes, df_pedidos, df_satisfacao, actions_log, period_days):
    """Dashboard de analytics avançado"""
    
    st.markdown('<div class="section-header"><span class="emoji">📈</span><h2>Analytics & Performance</h2></div>', unsafe_allow_html=True)
    
    # Métricas de performance da equipe
    col1, col2, col3, col4 = st.columns(4)
    
    acoes_executadas = len(actions_log)
    acoes_pendentes = len(df_clientes[df_clientes['acao_sugerida'].notna() & (df_clientes['acao_sugerida'] != '')])
    taxa_execucao = (acoes_executadas / (acoes_executadas + acoes_pendentes) * 100) if (acoes_executadas + acoes_pendentes) > 0 else 0
    
    with col1:
        st.markdown(create_metric_card_with_explanation(
            "📋 Ações Executadas",
            f"{acoes_executadas:,}",
            "Última semana",
            "metric-info",
            "Total de ações de CS executadas pela equipe"
        ), unsafe_allow_html=True)
    
    with col2:
        color_class = "metric-warning" if acoes_pendentes > 20 else "metric-success"
        st.markdown(create_metric_card_with_explanation(
            "⏳ Ações Pendentes", 
            f"{acoes_pendentes:,}",
            "Requer atenção",
            color_class,
            "Ações de CS identificadas mas ainda não executadas"
        ), unsafe_allow_html=True)
    
    with col3:
        color_class = "metric-success" if taxa_execucao >= 80 else "metric-warning" if taxa_execucao >= 60 else "metric-danger"
        st.markdown(create_metric_card_with_explanation(
            "✅ Taxa de Execução",
            f"{taxa_execucao:.1f}%",
            "Meta: 80%+",
            color_class,
            "Percentual de ações executadas vs. identificadas"
        ), unsafe_allow_html=True)
    
    with col4:
        tempo_resposta = 4.2  # Simulado
        color_class = "metric-success" if tempo_resposta <= 6 else "metric-warning"
        st.markdown(create_metric_card_with_explanation(
            "🕐 Tempo Médio",
            f"{tempo_resposta:.1f}h",
            "Tempo de resposta",
            color_class,
            "Tempo médio entre identificação e execução da ação"
        ), unsafe_allow_html=True)
    
    # Análise financeira
    st.markdown('<div class="section-header"><span class="emoji">💰</span><h2>Análise Financeira</h2></div>', unsafe_allow_html=True)
    
    # Converter receita para numérico
    df_clientes['receita_num'] = pd.to_numeric(df_clientes['receita'].str.replace(',', '.'), errors='coerce')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Receita por Nível de Cliente**")
        
        receita_nivel = df_clientes.groupby('nivel_cliente')['receita_num'].agg(['sum', 'mean', 'count']).reset_index()
        receita_nivel.columns = ['Nível', 'Receita Total', 'Ticket Médio', 'Quantidade']
        
        fig_receita = px.bar(
            receita_nivel,
            x='Nível',
            y='Receita Total',
            color='Nível',
            color_discrete_map=CHART_COLORS['nivel'],
            title=""
        )
        
        fig_receita.update_layout(
            font=dict(family="Inter", size=12),
            showlegend=False,
            margin=dict(t=20, b=0, l=0, r=0),
            height=350
        )
        
        fig_receita.update_traces(
            hovertemplate='<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>'
        )
        
        st.plotly_chart(fig_receita, use_container_width=True)
    
    with col2:
        st.markdown("**⚠️ Receita em Risco**")
        
        # Análise de risco financeiro
        clientes_risco = df_clientes[df_clientes['risco_recencia'].isin(['Alto', 'Novo_Alto'])]
        receita_em_risco = clientes_risco['receita_num'].sum()
        receita_total = df_clientes['receita_num'].sum()
        perc_risco = (receita_em_risco / receita_total * 100) if receita_total > 0 else 0
        
        # Gráfico de gauge para risco financeiro
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = perc_risco,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "% Receita em Risco"},
            delta = {'reference': 15, 'increasing': {'color': "red"}, 'decreasing': {'color': COLORS['success']}},
            gauge = {
                'axis': {'range': [None, 50]},
                'bar': {'color': COLORS['danger'] if perc_risco > 20 else COLORS['warning'] if perc_risco > 10 else COLORS['success']},
                'steps': [
                    {'range': [0, 10], 'color': "lightgray"},
                    {'range': [10, 20], 'color': "gray"},
                    {'range': [20, 50], 'color': "darkgray"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 20}}))
        
        fig_gauge.update_layout(
            font=dict(family="Inter", size=12),
            height=350,
            margin=dict(t=50, b=0, l=0, r=0)
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Status do risco
        if perc_risco > 20:
            st.error(f"🚨 CRÍTICO: {perc_risco:.1f}% da receita em risco!")
        elif perc_risco > 10:
            st.warning(f"⚠️ ATENÇÃO: {perc_risco:.1f}% da receita em risco")
        else:
            st.success(f"✅ Risco controlado: {perc_risco:.1f}%")

def show_actions_center_enhanced(df_clientes, actions_log, team_filter):
    """Central de ações aprimorada"""
    
    st.markdown('<div class="section-header"><span class="emoji">🔔</span><h2>Central de Ações</h2></div>', unsafe_allow_html=True)
    
    # Painel de controle de ações
    acoes_pendentes = df_clientes[
        df_clientes['acao_sugerida'].notna() & 
        (df_clientes['acao_sugerida'] != '')
    ].copy()
    
    executed_clients = {a.get('cliente_id') for a in actions_log}
    acoes_pendentes['ja_executada'] = acoes_pendentes['cliente_unico_id'].isin(executed_clients)
    acoes_pendentes = acoes_pendentes[~acoes_pendentes['ja_executada']]
    
    # Estatísticas de ações
    col1, col2, col3, col4 = st.columns(4)
    
    total_acoes = len(acoes_pendentes)
    acoes_alta_prioridade = len(acoes_pendentes[acoes_pendentes['priority_score'] >= 200])
    acoes_executadas_hoje = len([a for a in actions_log if datetime.fromisoformat(a['timestamp']).date() == datetime.now().date()])
    
    with col1:
        st.markdown(create_metric_card_with_explanation(
            "📋 Ações Pendentes",
            f"{total_acoes:,}",
            "Total na fila",
            "metric-warning" if total_acoes > 50 else "metric-info",
            "Ações identificadas pelo sistema que aguardam execução"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card_with_explanation(
            "🚨 Alta Prioridade",
            f"{acoes_alta_prioridade:,}",
            "Requer ação imediata",
            "metric-danger" if acoes_alta_prioridade > 0 else "metric-success",
            "Clientes Premium/Gold ou com score crítico (>200)"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card_with_explanation(
            "✅ Executadas Hoje",
            f"{acoes_executadas_hoje:,}",
            "Progresso diário",
            "metric-success",
            "Ações de CS concluídas no dia atual"
        ), unsafe_allow_html=True)
    
    with col4:
        eficiencia = (acoes_executadas_hoje / max(total_acoes, 1)) * 100
        st.markdown(create_metric_card_with_explanation(
            "📊 Eficiência",
            f"{eficiencia:.1f}%",
            "Meta diária",
            "metric-success" if eficiencia >= 20 else "metric-warning",
            "Percentual de ações executadas hoje vs. fila total"
        ), unsafe_allow_html=True)
    
    if len(acoes_pendentes) > 0:
        # Lista de ações prioritárias
        st.markdown("### 🎯 Ações Prioritárias")
        
        for _, cliente in acoes_pendentes.head(8).iterrows():
            emoji, css_class = get_priority_color_class(cliente['priority_score'])
            
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.markdown(f"""
                **{emoji} {cliente.get('nome', 'N/A')}**  
                📧 {cliente.get('email', 'N/A')} | 📱 {format_phone_number(cliente.get('telefone1', 'N/A'))}  
                🏆 {cliente.get('nivel_cliente', 'N/A')} | 💰 R$ {cliente.get('receita', '0')}
                """)
            
            with col2:
                st.markdown(f"""
                **🎯 Ação:** {cliente.get('acao_sugerida', '')}  
                **📊 Score:** {cliente.get('priority_score', 0):.0f}  
                **⚠️ Risco:** {cliente.get('risco_recencia', 'N/A')}
                """)
            
            with col3:
                if st.button("✅ Executar", key=f"exec_{cliente.get('cliente_unico_id')}", use_container_width=True):
                    action_data = {
                        'cliente_id': cliente.get('cliente_unico_id'),
                        'cliente_nome': cliente.get('nome'),
                        'acao': cliente.get('acao_sugerida'),
                        'status': 'executada',
                        'executado_por': team_filter if team_filter != 'Todos' else 'Usuário'
                    }
                    save_action_log(action_data)
                    st.success("✅ Ação registrada!")
                    st.rerun()
            
            st.markdown("---")
    
    else:
        st.success("🎉 Todas as ações foram executadas! Excelente trabalho da equipe.")
    
    # Histórico de ações com visualização melhorada
    st.markdown("### 📚 Histórico Recente")
    
    if actions_log:
        df_actions = pd.DataFrame(actions_log[-10:])  # Últimas 10 ações
        df_actions['data_formatada'] = pd.to_datetime(df_actions['timestamp']).dt.strftime('%d/%m %H:%M')
        
        for _, action in df_actions.iterrows():
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                st.markdown(f"**{action['data_formatada']}**")
            
            with col2:
                st.markdown(f"👤 **{action['cliente_nome']}** - {action['acao']}")
            
            with col3:
                st.markdown(f"👨‍💼 {action['executado_por']}")


if __name__ == "__main__":
    main()