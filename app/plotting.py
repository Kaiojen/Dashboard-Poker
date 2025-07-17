import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict
from calculations import PokerCalculations

class PokerPlotting:
    
    @staticmethod
    def create_roi_evolution_chart(torneios: List[Dict]) -> go.Figure:
        """Cria gráfico de evolução do ROI ao longo do tempo."""
        if not torneios:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        calc = PokerCalculations()
        roi_evolution = calc.get_roi_evolution(torneios)
        
        df = pd.DataFrame(roi_evolution)
        df['data'] = pd.to_datetime(df['data'])
        
        fig = go.Figure()
        
        # Linha do ROI acumulado
        fig.add_trace(go.Scatter(
            x=df['data'],
            y=df['roi_acumulado'],
            mode='lines+markers',
            name='ROI Acumulado (%)',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=6),
            hovertemplate='<b>Data:</b> %{x}<br>' +
                         '<b>ROI:</b> %{y:.1f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Linha de referência no zero
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title={
                'text': '📈 Evolução do ROI ao Longo do Tempo',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Data',
            yaxis_title='ROI Acumulado (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_profit_by_tournament_type_chart(estatisticas_por_tipo: List[Dict]) -> go.Figure:
        """Cria gráfico de barras para lucro líquido por tipo de torneio."""
        if not estatisticas_por_tipo:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(estatisticas_por_tipo)
        
        # Cores baseadas no lucro (verde para positivo, vermelho para negativo)
        colors = ['#10b981' if x >= 0 else '#ef4444' for x in df['lucro_liquido']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=df['nome_tipo'],
                y=df['lucro_liquido'],
                marker_color=colors,
                text=[f'R$ {x:.2f}' for x in df['lucro_liquido']],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>' +
                             'Lucro: R$ %{y:.2f}<br>' +
                             '<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': '💰 Lucro Líquido por Tipo de Torneio',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Tipo de Torneio',
            yaxis_title='Lucro Líquido (R$)',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        # Linha de referência no zero
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    @staticmethod
    def create_tournament_distribution_pie_chart(estatisticas_por_tipo: List[Dict]) -> go.Figure:
        """Cria gráfico de pizza para proporção de tipos de torneios jogados."""
        if not estatisticas_por_tipo:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(estatisticas_por_tipo)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=df['nome_tipo'],
                values=df['total_torneios'],
                hole=0.4,
                textinfo='label+percent',
                textposition='auto',
                marker=dict(
                    colors=['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
                    line=dict(color='#FFFFFF', width=2)
                ),
                hovertemplate='<b>%{label}</b><br>' +
                             'Torneios: %{value}<br>' +
                             'Percentual: %{percent}<br>' +
                             '<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': '🎯 Distribuição de Tipos de Torneios',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            template='plotly_white',
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    @staticmethod
    def create_monthly_performance_chart(torneios: List[Dict]) -> go.Figure:
        """Cria gráfico de performance mensal."""
        if not torneios:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        calc = PokerCalculations()
        monthly_data = calc.get_performance_by_period(torneios, 'monthly')
        
        if not monthly_data:
            fig = go.Figure()
            fig.add_annotation(
                text="Dados insuficientes para análise mensal",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(monthly_data)
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Lucro Líquido Mensal', 'ROI Mensal (%)'),
            vertical_spacing=0.1
        )
        
        # Gráfico de barras para lucro líquido
        colors_lucro = ['#10b981' if x >= 0 else '#ef4444' for x in df['lucro_liquido']]
        fig.add_trace(
            go.Bar(
                x=df['periodo_str'],
                y=df['lucro_liquido'],
                name='Lucro Líquido',
                marker_color=colors_lucro,
                text=[f'R$ {x:.2f}' for x in df['lucro_liquido']],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Gráfico de linha para ROI
        fig.add_trace(
            go.Scatter(
                x=df['periodo_str'],
                y=df['roi'],
                mode='lines+markers',
                name='ROI (%)',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8)
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title={
                'text': '📊 Performance Mensal',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            template='plotly_white',
            height=600,
            showlegend=False
        )
        
        # Linhas de referência no zero
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_account_comparison_chart(db, contas: List[Dict]) -> go.Figure:
        """Cria gráfico de comparação entre contas."""
        if not contas:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma conta disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Obter estatísticas para cada conta
        dados_contas = []
        for conta in contas:
            stats = db.get_estatisticas_gerais(id_conta=conta['id'])
            if stats['total_torneios'] > 0:  # Só incluir contas com torneios
                dados_contas.append({
                    'nome_conta': conta['nome'],
                    'lucro_liquido': stats['lucro_liquido'],
                    'roi_geral': stats['roi_geral'],
                    'total_torneios': stats['total_torneios'],
                    'itm_percentage': stats['itm_percentage']
                })
        
        if not dados_contas:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma conta com torneios registrados",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        df = pd.DataFrame(dados_contas)
        
        # Criar subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Lucro Líquido por Conta', 'ROI por Conta', 
                           'Total de Torneios', 'ITM (%)'),
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        # Lucro líquido
        colors_lucro = ['#10b981' if x >= 0 else '#ef4444' for x in df['lucro_liquido']]
        fig.add_trace(
            go.Bar(x=df['nome_conta'], y=df['lucro_liquido'], 
                  marker_color=colors_lucro, name='Lucro'),
            row=1, col=1
        )
        
        # ROI
        colors_roi = ['#10b981' if x >= 0 else '#ef4444' for x in df['roi_geral']]
        fig.add_trace(
            go.Bar(x=df['nome_conta'], y=df['roi_geral'], 
                  marker_color=colors_roi, name='ROI'),
            row=1, col=2
        )
        
        # Total de torneios
        fig.add_trace(
            go.Bar(x=df['nome_conta'], y=df['total_torneios'], 
                  marker_color='#3b82f6', name='Torneios'),
            row=2, col=1
        )
        
        # ITM
        fig.add_trace(
            go.Bar(x=df['nome_conta'], y=df['itm_percentage'], 
                  marker_color='#8b5cf6', name='ITM'),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': '⚖️ Comparação entre Contas',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            template='plotly_white',
            height=600,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_bankroll_evolution_chart(torneios: List[Dict], bankroll_inicial: float = 0) -> go.Figure:
        """Cria gráfico de evolução do bankroll."""
        if not torneios:
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhum dado disponível",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16)
            )
            return fig
        
        # Ordenar por data
        torneios_sorted = sorted(torneios, key=lambda x: x['data_torneio'])
        
        # Calcular evolução do bankroll
        datas = []
        bankroll_values = []
        bankroll_atual = bankroll_inicial
        
        for torneio in torneios_sorted:
            bankroll_atual += torneio['lucro_liquido']
            datas.append(pd.to_datetime(torneio['data_torneio']))
            bankroll_values.append(bankroll_atual)
        
        fig = go.Figure()
        
        # Linha do bankroll
        fig.add_trace(go.Scatter(
            x=datas,
            y=bankroll_values,
            mode='lines+markers',
            name='Bankroll',
            line=dict(color='#10b981', width=3),
            marker=dict(size=6),
            fill='tonexty' if bankroll_inicial > 0 else None,
            hovertemplate='<b>Data:</b> %{x}<br>' +
                         '<b>Bankroll:</b> R$ %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # Linha de referência do bankroll inicial
        if bankroll_inicial > 0:
            fig.add_hline(y=bankroll_inicial, line_dash="dash", 
                         line_color="blue", opacity=0.5,
                         annotation_text=f"Bankroll Inicial: R$ {bankroll_inicial:.2f}")
        
        fig.update_layout(
            title={
                'text': '💳 Evolução do Bankroll',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Data',
            yaxis_title='Bankroll (R$)',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig

