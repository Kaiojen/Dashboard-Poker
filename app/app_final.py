import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os

from database import PokerDatabase
from calculations import PokerCalculations
from plotting import PokerPlotting
from export import PokerExport

# Configuração da página
st.set_page_config(
    page_title="Dashboard Suprema Poker",
    page_icon="♠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .positive {
        color: #10b981;
        font-weight: bold;
    }
    
    .negative {
        color: #ef4444;
        font-weight: bold;
    }
    
    .neutral {
        color: #6b7280;
        font-weight: bold;
    }
    
    .sidebar-section {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .export-section {
        background: #f0f9ff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #0ea5e9;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar banco de dados
@st.cache_resource
def init_database():
    return PokerDatabase()

db = init_database()
plotting = PokerPlotting()
export = PokerExport()

# Título principal
st.markdown('<h1 class="main-header">♠️ Dashboard Suprema Poker ♠️</h1>', unsafe_allow_html=True)

# Sidebar para inserção de dados e filtros
st.sidebar.markdown("## 📊 Controles")

# Seção de inserção de dados
with st.sidebar.expander("➕ Inserir Novo Torneio", expanded=False):
    st.markdown("### Dados do Torneio")
    
    # Obter contas e tipos de torneio
    contas = db.get_contas()
    tipos_torneio = db.get_tipos_torneio()
    
    # Formulário de inserção
    with st.form("inserir_torneio"):
        data_torneio = st.date_input(
            "Data do Torneio",
            value=date.today(),
            help="Data em que o torneio foi jogado"
        )
        
        conta_selecionada = st.selectbox(
            "Conta Utilizada",
            options=[c["nome"] for c in contas],
            help="Selecione a conta que jogou o torneio"
        )
        
        tipo_selecionado = st.selectbox(
            "Tipo de Torneio",
            options=[t["nome"] for t in tipos_torneio],
            help="Selecione o tipo de torneio"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            buy_in = st.number_input(
                "Buy-in (R$)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Valor pago para entrar no torneio"
            )
        
        with col2:
            ganho_total = st.number_input(
                "Ganho Total (R$)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Valor total ganho no torneio"
            )
        
        submitted = st.form_submit_button("💾 Salvar Torneio", use_container_width=True)
        
        if submitted:
            # Encontrar IDs das seleções
            id_conta = next(c["id"] for c in contas if c["nome"] == conta_selecionada)
            id_tipo_torneio = next(t["id"] for t in tipos_torneio if t["nome"] == tipo_selecionado)
            
            # Inserir no banco
            sucesso = db.insert_torneio(
                data_torneio.strftime("%Y-%m-%d"),
                id_conta,
                id_tipo_torneio,
                buy_in,
                ganho_total
            )
            
            if sucesso:
                st.success("✅ Torneio inserido com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao inserir torneio!")

# Seção de exclusão de torneios
with st.sidebar.expander("🗑️ Excluir Torneio", expanded=False):
    st.markdown("### Selecionar Torneio para Excluir")
    
    torneios_para_excluir = db.get_torneios()
    if torneios_para_excluir:
        df_torneios_excluir = pd.DataFrame(torneios_para_excluir)
        df_torneios_excluir["display"] = df_torneios_excluir.apply(lambda row: f"{row['data_torneio']} - {row['nome_conta']} - {row['nome_tipo']} - R$ {row['buy_in']:.2f}", axis=1)
        
        torneio_selecionado_display = st.selectbox(
            "Escolha o torneio a ser excluído",
            options=df_torneios_excluir["display"].tolist(),
            help="Selecione o torneio que deseja remover"
        )
        
        if st.button("🗑️ Confirmar Exclusão", use_container_width=True):
            id_torneio_excluir = df_torneios_excluir[df_torneios_excluir["display"] == torneio_selecionado_display]["id_torneio"].iloc[0]
            sucesso_exclusao = db.delete_torneio(id_torneio_excluir)
            
            if sucesso_exclusao:
                st.success("✅ Torneio excluído com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao excluir torneio!")
    else:
        st.info("Nenhum torneio para excluir.")

# Seção de exportação e backup
with st.sidebar.expander("📤 Exportar & Backup", expanded=False):
    st.markdown("### Exportação de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 CSV", use_container_width=True):
            try:
                torneios = db.get_torneios()
                if torneios:
                    filepath = export.export_to_csv(torneios)
                    st.success(f"✅ CSV exportado!")
                    
                    # Botão de download
                    with open(filepath, "rb") as file:
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=file,
                            file_name=os.path.basename(filepath),
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.warning("⚠️ Nenhum dado para exportar")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    with col2:
        if st.button("📈 Excel", use_container_width=True):
            try:
                torneios = db.get_torneios()
                if torneios:
                    estatisticas = db.get_estatisticas_gerais()
                    estatisticas_por_tipo = db.get_estatisticas_por_tipo()
                    
                    filepath = export.export_to_excel(torneios, estatisticas, estatisticas_por_tipo)
                    st.success(f"✅ Excel exportado!")
                    
                    # Botão de download
                    with open(filepath, "rb") as file:
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=file,
                            file_name=os.path.basename(filepath),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                else:
                    st.warning("⚠️ Nenhum dado para exportar")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    if st.button("📄 Relatório PDF", use_container_width=True):
        try:
            torneios = db.get_torneios()
            if torneios:
                estatisticas = db.get_estatisticas_gerais()
                estatisticas_por_tipo = db.get_estatisticas_por_tipo()
                
                filepath = export.export_to_pdf(torneios, estatisticas, estatisticas_por_tipo)
                st.success(f"✅ PDF gerado!")
                
                # Botão de download
                with open(filepath, "rb") as file:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=file,
                        file_name=os.path.basename(filepath),
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.warning("⚠️ Nenhum dado para exportar")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.markdown("### Backup")
    if st.button("💾 Criar Backup", use_container_width=True):
        try:
            backup_path = export.create_backup(db.db_path)
            st.success(f"✅ Backup criado!")
            
            # Botão de download do backup
            with open(backup_path, "rb") as file:
                st.download_button(
                    label="⬇️ Download Backup",
                    data=file,
                    file_name=os.path.basename(backup_path),
                    mime="application/octet-stream",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"❌ Erro no backup: {str(e)}")

# Seção de filtros
st.sidebar.markdown("### 🔍 Filtros")

# Filtro por conta
contas_opcoes = ["Todas as Contas"] + [c["nome"] for c in contas]
conta_filtro = st.sidebar.selectbox("Conta", contas_opcoes)

# Filtro por tipo de torneio
tipos_opcoes = ["Todos os Tipos"] + [t["nome"] for t in tipos_torneio]
tipo_filtro = st.sidebar.selectbox("Tipo de Torneio", tipos_opcoes)

# Filtro por período
periodo_opcoes = ["Todos os Períodos", "Última Semana", "Último Mês", "Últimos 3 Meses", "Último Ano", "Personalizado"]
periodo_filtro = st.sidebar.selectbox("Período", periodo_opcoes)

# Datas personalizadas se selecionado
data_inicio = None
data_fim = None

if periodo_filtro == "Personalizado":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início")
    with col2:
        data_fim = st.date_input("Data Fim")
elif periodo_filtro == "Última Semana":
    data_inicio = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    data_fim = date.today().strftime("%Y-%m-%d")
elif periodo_filtro == "Último Mês":
    data_inicio = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    data_fim = date.today().strftime("%Y-%m-%d")
elif periodo_filtro == "Últimos 3 Meses":
    data_inicio = (date.today() - timedelta(days=90)).strftime("%Y-%m-%d")
    data_fim = date.today().strftime("%Y-%m-%d")
elif periodo_filtro == "Último Ano":
    data_inicio = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    data_fim = date.today().strftime("%Y-%m-%d")

# Converter datas personalizadas para string se necessário
if data_inicio and isinstance(data_inicio, date):
    data_inicio = data_inicio.strftime("%Y-%m-%d")
if data_fim and isinstance(data_fim, date):
    data_fim = data_fim.strftime("%Y-%m-%d")

# Aplicar filtros
id_conta_filtro = None if conta_filtro == "Todas as Contas" else next(c["id"] for c in contas if c["nome"] == conta_filtro)
id_tipo_filtro = None if tipo_filtro == "Todos os Tipos" else next(t["id"] for t in tipos_torneio if t["nome"] == tipo_filtro)

# Obter dados filtrados
torneios = db.get_torneios(
    id_conta=id_conta_filtro,
    id_tipo_torneio=id_tipo_filtro,
    data_inicio=data_inicio,
    data_fim=data_fim
)

estatisticas = db.get_estatisticas_gerais(
    id_conta=id_conta_filtro,
    data_inicio=data_inicio,
    data_fim=data_fim
)

estatisticas_por_tipo = db.get_estatisticas_por_tipo(
    id_conta=id_conta_filtro,
    data_inicio=data_inicio,
    data_fim=data_fim
)

# Layout principal
if not torneios:
    st.info("📊 Nenhum torneio encontrado com os filtros selecionados. Insira alguns torneios para começar!")
    
    # Mostrar exemplo de como usar
    with st.expander("💡 Como usar o Dashboard", expanded=True):
        st.markdown("""
        ### 🚀 Primeiros Passos:
        
        1. **Inserir Torneios**: Use o formulário na barra lateral para adicionar seus resultados
        2. **Visualizar Dados**: Os gráficos e métricas aparecerão automaticamente
        3. **Filtrar Resultados**: Use os filtros para analisar períodos específicos ou contas
        4. **Exportar Dados**: Baixe relatórios em CSV, Excel ou PDF
        5. **Fazer Backup**: Mantenha seus dados seguros com backups regulares
        
        ### 📊 Métricas Disponíveis:
        - **ROI**: Retorno sobre investimento
        - **ITM**: Porcentagem de torneios "in the money"
        - **ABI**: Average buy-in (buy-in médio)
        - **Downswing**: Maior sequência de perdas
        
        ### 🎯 Contas Configuradas:
        - **PKagente** (Distribuição de fichas)
        - **I´Dr.t** (gabrielpecanha103@gmail.com)
        - **JiNRiuk** (poker.cont002@gmail.com)
        - **Blackk_killer** (testes404az@gmail.com)
        - **I´mDrFIsh** (testes200y@gmail.com)
        - **kaiojen** (testes300y@gmail.com)
        
        ### 🏆 Tipos de Torneios:
        - **Mystery** - Torneios Mystery Bounty
        - **Battle** - Torneios Battle
        - **Plus** - Torneios Plus
        - **Reentry** - Torneios com Reentry
        - **Freeze** - Torneios Freezeout (sem recompra)
        - **Bounty** - Torneios com sistema de recompensas
        """)
else:
    # Métricas principais
    st.markdown("## 📈 Indicadores Principais")
    
    # Comparação temporal (Este mês vs mês passado)
    from datetime import datetime, timedelta
    hoje = datetime.now()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    primeiro_dia_mes_passado = (primeiro_dia_mes_atual - timedelta(days=1)).replace(day=1)
    ultimo_dia_mes_passado = primeiro_dia_mes_atual - timedelta(days=1)
    
    # Estatísticas do mês atual
    stats_mes_atual = db.get_estatisticas_gerais(
        id_conta=id_conta_filtro,
        data_inicio=primeiro_dia_mes_atual.strftime("%Y-%m-%d"),
        data_fim=hoje.strftime("%Y-%m-%d")
    )
    
    # Estatísticas do mês passado
    stats_mes_passado = db.get_estatisticas_gerais(
        id_conta=id_conta_filtro,
        data_inicio=primeiro_dia_mes_passado.strftime("%Y-%m-%d"),
        data_fim=ultimo_dia_mes_passado.strftime("%Y-%m-%d")
    )
    
    # Seção de comparação temporal
    st.markdown("### 📊 Comparação Temporal (Este Mês vs Mês Passado)")
    col_temp1, col_temp2, col_temp3, col_temp4 = st.columns(4)
    
    with col_temp1:
        lucro_atual = stats_mes_atual['lucro_liquido']
        lucro_passado = stats_mes_passado['lucro_liquido']
        delta_lucro = lucro_atual - lucro_passado
        st.metric(
            "💰 Lucro do Mês",
            f"R$ {lucro_atual:.2f}",
            delta=f"R$ {delta_lucro:.2f}"
        )
    
    with col_temp2:
        roi_atual = stats_mes_atual['roi_geral']
        roi_passado = stats_mes_passado['roi_geral']
        delta_roi = roi_atual - roi_passado
        st.metric(
            "📊 ROI do Mês",
            f"{roi_atual:.1f}%",
            delta=f"{delta_roi:.1f}%"
        )
    
    with col_temp3:
        torneios_atual = stats_mes_atual['total_torneios']
        torneios_passado = stats_mes_passado['total_torneios']
        delta_torneios = torneios_atual - torneios_passado
        st.metric(
            "🎯 Torneios do Mês",
            f"{torneios_atual}",
            delta=f"{delta_torneios}"
        )
    
    with col_temp4:
        itm_atual = stats_mes_atual['itm_percentage']
        itm_passado = stats_mes_passado['itm_percentage']
        delta_itm = itm_atual - itm_passado
        st.metric(
            "💎 ITM do Mês",
            f"{itm_atual:.1f}%",
            delta=f"{delta_itm:.1f}%"
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        lucro_class = "positive" if estatisticas["lucro_liquido"] > 0 else "negative" if estatisticas["lucro_liquido"] < 0 else "neutral"
        st.metric(
            "💰 Lucro Líquido",
            f"R$ {estatisticas['lucro_liquido']:.2f}",
            delta=None
        )
    
    with col2:
        roi_class = "positive" if estatisticas["roi_geral"] > 0 else "negative" if estatisticas["roi_geral"] < 0 else "neutral"
        st.metric(
            "📊 ROI Geral",
            f"{estatisticas['roi_geral']:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            "🎯 Total de Torneios",
            f"{estatisticas['total_torneios']}",
            delta=None
        )
    
    with col4:
        st.metric(
            "💎 ITM",
            f"{estatisticas['itm_percentage']:.1f}%",
            delta=None
        )
    
    # Segunda linha de métricas
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "💸 Total Investido",
            f"R$ {estatisticas['total_investido']:.2f}",
            delta=None
        )
    
    with col6:
        st.metric(
            "💵 Total Ganhos",
            f"R$ {estatisticas['total_ganhos']:.2f}",
            delta=None
        )
    
    with col7:
        st.metric(
            "🎲 ABI",
            f"R$ {estatisticas['abi']:.2f}",
            delta=None
        )
    
    with col8:
        # Calcular variância
        calc = PokerCalculations()
        variance_data = calc.calculate_variance_and_downswing(torneios)
        st.metric(
            "📉 Maior Downswing",
            f"R$ {variance_data['maior_downswing']:.2f}",
            delta=None
        )

    # Seção de gráficos
    st.markdown("## 📊 Análises Visuais")
    
    # Primeira linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de evolução do ROI
        fig_roi = plotting.create_roi_evolution_chart(torneios)
        st.plotly_chart(fig_roi, use_container_width=True)
    
    with col2:
        # Gráfico de lucro por tipo de torneio
        fig_profit = plotting.create_profit_by_tournament_type_chart(estatisticas_por_tipo)
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # Segunda linha de gráficos
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfico de distribuição de tipos de torneio
        fig_pie = plotting.create_tournament_distribution_pie_chart(estatisticas_por_tipo)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col4:
        # Gráfico de evolução do bankroll (assumindo bankroll inicial de 0)
        fig_bankroll = plotting.create_bankroll_evolution_chart(torneios, 0)
        st.plotly_chart(fig_bankroll, use_container_width=True)
    
    # Gráfico de performance mensal (largura completa)
    fig_monthly = plotting.create_monthly_performance_chart(torneios)
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Gráfico de comparação entre contas (se não há filtro de conta específica)
    if conta_filtro == "Todas as Contas":
        fig_accounts = plotting.create_account_comparison_chart(db, contas)
        st.plotly_chart(fig_accounts, use_container_width=True)

# Tabela de torneios recentes
if torneios:
    st.markdown("## 📋 Torneios Recentes")
    
    # Preparar dados para exibição
    df_display = pd.DataFrame(torneios)
    df_display = df_display[['data_torneio', 'nome_conta', 'nome_tipo', 'buy_in', 'ganho_total', 'lucro_liquido', 'roi']]
    df_display.columns = ['Data', 'Conta', 'Tipo', 'Buy-in (R$)', 'Ganho (R$)', 'Lucro (R$)', 'ROI (%)']
    
    # Formatar valores
    df_display['Buy-in (R$)'] = df_display['Buy-in (R$)'].apply(lambda x: f"R$ {x:.2f}")
    df_display['Ganho (R$)'] = df_display['Ganho (R$)'].apply(lambda x: f"R$ {x:.2f}")
    df_display['Lucro (R$)'] = df_display['Lucro (R$)'].apply(lambda x: f"R$ {x:.2f}")
    df_display['ROI (%)'] = df_display['ROI (%)'].apply(lambda x: f"{x:.1f}%")
    
    # Determinar número de itens por página
    itens_por_pagina = 20
    total_torneios = len(df_display)
    
    # Paginação
    if total_torneios > itens_por_pagina:
        st.markdown("### 📄 Paginação")
        total_paginas = (total_torneios - 1) // itens_por_pagina + 1
        
        col_pag1, col_pag2, col_pag3 = st.columns([2, 2, 6])
        with col_pag1:
            pagina_atual = st.number_input(
                "Página", 
                min_value=1, 
                max_value=total_paginas, 
                value=1, 
                step=1,
                key="pagina_torneios"
            )
        with col_pag2:
            st.write(f"de {total_paginas} páginas")
        
        # Calcular slice
        inicio = (pagina_atual - 1) * itens_por_pagina
        fim = min(inicio + itens_por_pagina, total_torneios)
        df_display = df_display.iloc[inicio:fim]
    else:
        df_display = df_display.head(20)
    
    # Aplicar cores baseadas no lucro para melhor visualização
    def colorir_lucro(val):
        if 'R$' in str(val):
            valor = float(str(val).replace('R$', '').replace(',', '.').strip())
            if valor > 0:
                return 'background-color: #d4edda; color: #155724'  # Verde claro
            elif valor < 0:
                return 'background-color: #f8d7da; color: #721c24'  # Vermelho claro
        return ''
    
    def colorir_roi(val):
        if '%' in str(val):
            valor = float(str(val).replace('%', '').strip())
            if valor > 0:
                return 'background-color: #d4edda; color: #155724'  # Verde claro
            elif valor < 0:
                return 'background-color: #f8d7da; color: #721c24'  # Vermelho claro
        return ''
    
    # Aplicar estilos
    styled_df = df_display.style.applymap(
        colorir_lucro, subset=['Lucro (R$)']
    ).applymap(
        colorir_roi, subset=['ROI (%)']
    )
    
    # Mostrar dataframe com cores
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Seção de ações rápidas para torneios
    st.markdown("### ⚡ Ações Rápidas")
    
    # Tabs para ação individual vs ação em lote
    tab1, tab2 = st.tabs(["🎯 Ação Individual", "📦 Ação em Lote"])
    
    with tab1:
        # Dropdown para seleção de torneio
        torneios_opcoes = []
        inicio_pagina = 0
        if 'pagina_torneios' in st.session_state and total_torneios > itens_por_pagina:
            inicio_pagina = (st.session_state['pagina_torneios'] - 1) * itens_por_pagina
        
        torneios_pagina = torneios[inicio_pagina:inicio_pagina + itens_por_pagina]
        
        for i, torneio in enumerate(torneios_pagina):
            opcao = f"{torneio['data_torneio']} - {torneio['nome_conta']} - {torneio['nome_tipo']} - R$ {torneio['buy_in']:.2f}"
            torneios_opcoes.append(opcao)
        
        if torneios_opcoes:
            col1, col2, col3 = st.columns([6, 2, 2])
            
            with col1:
                torneio_selecionado = st.selectbox(
                    "Selecione um torneio para editar ou excluir:",
                    torneios_opcoes,
                    key="torneio_acao"
                )
        
        with col2:
            if st.button("✏️ Editar", use_container_width=True):
                idx_selecionado = torneios_opcoes.index(torneio_selecionado)
                torneio_dados = torneios[idx_selecionado]
                st.session_state['edit_id'] = torneio_dados['id_torneio']
                st.session_state['edit_data'] = torneio_dados['data_torneio']
                st.session_state['edit_conta'] = torneio_dados['nome_conta']
                st.session_state['edit_tipo'] = torneio_dados['nome_tipo']
                st.session_state['edit_buyin'] = torneio_dados['buy_in']
                st.session_state['edit_ganho'] = torneio_dados['ganho_total']
                st.rerun()
        
        with col3:
            if st.button("🗑️ Excluir", use_container_width=True):
                st.session_state['confirmar_exclusao'] = torneio_selecionado
                st.rerun()
        
        # Popup de confirmação de exclusão
        if 'confirmar_exclusao' in st.session_state:
            st.error("⚠️ **Confirmação de Exclusão**")
            st.write(f"Tem certeza que deseja excluir o torneio:")
            st.write(f"**{st.session_state['confirmar_exclusao']}**")
            
            col_sim, col_nao = st.columns(2)
            with col_sim:
                if st.button("✅ Sim, excluir", use_container_width=True):
                    idx_selecionado = torneios_opcoes.index(st.session_state['confirmar_exclusao'])
                    torneio_dados = torneios[idx_selecionado]
                    sucesso_exclusao = db.delete_torneio(torneio_dados['id_torneio'])
                    if sucesso_exclusao:
                        st.success("✅ Torneio excluído com sucesso!")
                        del st.session_state['confirmar_exclusao']
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir torneio!")
            
            with col_nao:
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state['confirmar_exclusao']
                    st.rerun()
    
    with tab2:
        st.markdown("**Selecione múltiplos torneios para ações em lote:**")
        
        # Criar checkboxes para seleção múltipla
        if 'torneios_selecionados' not in st.session_state:
            st.session_state['torneios_selecionados'] = []
        
        col_sel1, col_sel2, col_sel3 = st.columns([8, 2, 2])
        
        with col_sel1:
            todos_marcados = st.checkbox("🔲 Selecionar/Desmarcar todos da página", key="todos_checkbox")
            
        with col_sel2:
            if st.button("✏️ Editar Lote", use_container_width=True, disabled=len(st.session_state['torneios_selecionados']) == 0):
                st.session_state['modo_edicao_lote'] = True
                st.rerun()
                
        with col_sel3:
            if st.button("🗑️ Excluir Lote", use_container_width=True, disabled=len(st.session_state['torneios_selecionados']) == 0):
                st.session_state['confirmar_exclusao_lote'] = True
                st.rerun()
        
        # Lista de checkboxes para torneios
        for i, torneio in enumerate(torneios_pagina):
            torneio_id = torneio['id_torneio']
            opcao_checkbox = f"{torneio['data_torneio']} - {torneio['nome_conta']} - {torneio['nome_tipo']} - R$ {torneio['buy_in']:.2f}"
            
            # Controlar estado do checkbox
            if todos_marcados:
                if torneio_id not in st.session_state['torneios_selecionados']:
                    st.session_state['torneios_selecionados'].append(torneio_id)
                marcado = True
            else:
                marcado = torneio_id in st.session_state['torneios_selecionados']
            
            checkbox_alterado = st.checkbox(opcao_checkbox, value=marcado, key=f"checkbox_{torneio_id}")
            
            # Atualizar lista baseado no checkbox
            if checkbox_alterado and torneio_id not in st.session_state['torneios_selecionados']:
                st.session_state['torneios_selecionados'].append(torneio_id)
            elif not checkbox_alterado and torneio_id in st.session_state['torneios_selecionados']:
                st.session_state['torneios_selecionados'].remove(torneio_id)
        
        # Confirmação de exclusão em lote
        if 'confirmar_exclusao_lote' in st.session_state:
            st.error("⚠️ **Confirmação de Exclusão em Lote**")
            st.write(f"Tem certeza que deseja excluir **{len(st.session_state['torneios_selecionados'])}** torneios selecionados?")
            
            col_sim_lote, col_nao_lote = st.columns(2)
            with col_sim_lote:
                if st.button("✅ Sim, excluir todos", use_container_width=True):
                    sucessos = 0
                    for torneio_id in st.session_state['torneios_selecionados']:
                        if db.delete_torneio(torneio_id):
                            sucessos += 1
                    
                    st.success(f"✅ {sucessos} torneios excluídos com sucesso!")
                    st.session_state['torneios_selecionados'] = []
                    del st.session_state['confirmar_exclusao_lote']
                    st.rerun()
            
            with col_nao_lote:
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state['confirmar_exclusao_lote']
                    st.rerun()
        
        # Modo de edição em lote
        if 'modo_edicao_lote' in st.session_state:
            st.markdown("### ✏️ Edição em Lote")
            st.write(f"Editando **{len(st.session_state['torneios_selecionados'])}** torneios selecionados")
            
            with st.form("edicao_lote_form"):
                st.write("**Campos que deseja alterar (deixe em branco para não alterar):**")
                
                col_lote1, col_lote2 = st.columns(2)
                
                with col_lote1:
                    alterar_data = st.checkbox("Alterar Data")
                    if alterar_data:
                        nova_data = st.date_input("Nova Data")
                    
                    alterar_conta = st.checkbox("Alterar Conta")
                    if alterar_conta:
                        nova_conta = st.selectbox("Nova Conta", [c["nome"] for c in contas])
                    
                    alterar_tipo = st.checkbox("Alterar Tipo")
                    if alterar_tipo:
                        novo_tipo = st.selectbox("Novo Tipo", [t["nome"] for t in tipos_torneio])
                
                with col_lote2:
                    alterar_buyin = st.checkbox("Alterar Buy-in")
                    if alterar_buyin:
                        novo_buyin = st.number_input("Novo Buy-in (R$)", min_value=0.0, step=0.01)
                    
                    alterar_ganho = st.checkbox("Alterar Ganho")
                    if alterar_ganho:
                        novo_ganho = st.number_input("Novo Ganho (R$)", min_value=0.0, step=0.01)
                
                col_save_lote, col_cancel_lote = st.columns(2)
                
                with col_save_lote:
                    salvar_lote = st.form_submit_button("💾 Salvar Alterações em Lote", use_container_width=True)
                
                with col_cancel_lote:
                    cancelar_lote = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if salvar_lote:
                    sucessos = 0
                    for torneio_id in st.session_state['torneios_selecionados']:
                        # Buscar dados atuais do torneio
                        torneio_atual = next((t for t in torneios if t['id_torneio'] == torneio_id), None)
                        if torneio_atual:
                            # Usar novos valores ou manter os atuais
                            data_final = nova_data.strftime("%Y-%m-%d") if alterar_data else torneio_atual['data_torneio']
                            conta_final = next(c["id"] for c in contas if c["nome"] == nova_conta) if alterar_conta else next(c["id"] for c in contas if c["nome"] == torneio_atual['nome_conta'])
                            tipo_final = next(t["id"] for t in tipos_torneio if t["nome"] == novo_tipo) if alterar_tipo else next(t["id"] for t in tipos_torneio if t["nome"] == torneio_atual['nome_tipo'])
                            buyin_final = novo_buyin if alterar_buyin else torneio_atual['buy_in']
                            ganho_final = novo_ganho if alterar_ganho else torneio_atual['ganho_total']
                            
                            if db.update_torneio(torneio_id, data_final, conta_final, tipo_final, buyin_final, ganho_final):
                                sucessos += 1
                    
                    st.success(f"✅ {sucessos} torneios atualizados com sucesso!")
                    st.session_state['torneios_selecionados'] = []
                    del st.session_state['modo_edicao_lote']
                    st.rerun()
                
                if cancelar_lote:
                    del st.session_state['modo_edicao_lote']
                    st.rerun()
    
    # Formulário de edição (quando um torneio é selecionado para edição)
    if 'edit_id' in st.session_state:
        st.markdown("### ✏️ Editar Torneio")
        
        with st.form("editar_torneio_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                data_edit = st.date_input(
                    "Data do Torneio", 
                    value=pd.to_datetime(st.session_state['edit_data']).date()
                )
                
                conta_edit = st.selectbox(
                    "Conta",
                    options=[c["nome"] for c in contas],
                    index=[c["nome"] for c in contas].index(st.session_state['edit_conta'])
                )
                
                tipo_edit = st.selectbox(
                    "Tipo de Torneio",
                    options=[t["nome"] for t in tipos_torneio],
                    index=[t["nome"] for t in tipos_torneio].index(st.session_state['edit_tipo'])
                )
            
            with col2:
                buyin_edit = st.number_input(
                    "Buy-in (R$)", 
                    min_value=0.0, 
                    value=float(st.session_state['edit_buyin']), 
                    step=0.01
                )
                
                ganho_edit = st.number_input(
                    "Ganho Total (R$)", 
                    min_value=0.0, 
                    value=float(st.session_state['edit_ganho']), 
                    step=0.01
                )
            
            col_submit1, col_submit2 = st.columns(2)
            
            with col_submit1:
                submitted_edit = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
            
            with col_submit2:
                cancelar_edit = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted_edit:
                # Encontrar IDs das seleções
                id_conta = next(c["id"] for c in contas if c["nome"] == conta_edit)
                id_tipo = next(t["id"] for t in tipos_torneio if t["nome"] == tipo_edit)
                
                sucesso_update = db.update_torneio(
                    st.session_state['edit_id'],
                    data_edit.strftime("%Y-%m-%d"),
                    id_conta,
                    id_tipo,
                    buyin_edit,
                    ganho_edit
                )
                
                if sucesso_update:
                    st.success("✅ Torneio atualizado com sucesso!")
                    del st.session_state['edit_id']
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar torneio!")
            
            if cancelar_edit:
                del st.session_state['edit_id']
                st.rerun()

# Seção de estatísticas avançadas
if torneios:
    st.markdown("## 🔍 Estatísticas Avançadas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 Melhores Sessões")
        calc = PokerCalculations()
        best_worst = calc.get_best_and_worst_sessions(torneios, 3)
        
        for i, sessao in enumerate(best_worst["melhores"], 1):
            st.write(f"**{i}º** - {sessao['data_torneio']}: R$ {sessao['lucro_liquido']:.2f}")
    
    with col2:
        st.markdown("### 📉 Piores Sessões")
        for i, sessao in enumerate(best_worst["piores"], 1):
            st.write(f"**{i}º** - {sessao['data_torneio']}: R$ {sessao['lucro_liquido']:.2f}")
    
    with col3:
        st.markdown("### 📊 Métricas de Risco")
        variance_data = calc.calculate_variance_and_downswing(torneios)
        st.write(f"**Variância:** {variance_data['variancia']:.2f}")
        st.write(f"**Maior Downswing:** R$ {variance_data['maior_downswing']:.2f}")
        st.write(f"**Downswing Atual:** R$ {variance_data['downswing_atual']:.2f}")

# Rodapé
st.markdown("---")
st.markdown("**Dashboard Suprema Poker** - Desenvolvido para controle profissional de resultados")

if __name__ == "__main__":
    pass







