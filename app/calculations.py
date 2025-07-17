from typing import List, Dict
import pandas as pd
from datetime import datetime, timedelta

class PokerCalculations:
    
    @staticmethod
    def calculate_roi(ganho_total: float, buy_in: float) -> float:
        """Calcula o ROI de um torneio."""
        if buy_in <= 0:
            return 0
        return ((ganho_total - buy_in) / buy_in) * 100
    
    @staticmethod
    def calculate_lucro_liquido(ganho_total: float, buy_in: float) -> float:
        """Calcula o lucro líquido de um torneio."""
        return ganho_total - buy_in
    
    @staticmethod
    def calculate_itm_percentage(torneios: List[Dict]) -> float:
        """Calcula a porcentagem de ITM (In The Money)."""
        if not torneios:
            return 0
        
        itm_count = sum(1 for t in torneios if t['ganho_total'] > 0)
        return (itm_count / len(torneios)) * 100
    
    @staticmethod
    def calculate_abi(torneios: List[Dict]) -> float:
        """Calcula o ABI (Average Buy-In)."""
        if not torneios:
            return 0
        
        total_buy_in = sum(t['buy_in'] for t in torneios)
        return total_buy_in / len(torneios)
    
    @staticmethod
    def get_roi_evolution(torneios: List[Dict]) -> List[Dict]:
        """Calcula a evolução do ROI ao longo do tempo."""
        if not torneios:
            return []
        
        # Ordenar por data
        torneios_sorted = sorted(torneios, key=lambda x: x['data_torneio'])
        
        roi_evolution = []
        total_investido = 0
        total_ganhos = 0
        
        for torneio in torneios_sorted:
            total_investido += torneio['buy_in']
            total_ganhos += torneio['ganho_total']
            
            roi_acumulado = ((total_ganhos - total_investido) / total_investido) * 100 if total_investido > 0 else 0
            
            roi_evolution.append({
                'data': torneio['data_torneio'],
                'roi_acumulado': roi_acumulado,
                'lucro_acumulado': total_ganhos - total_investido,
                'total_investido': total_investido,
                'total_ganhos': total_ganhos
            })
        
        return roi_evolution
    
    @staticmethod
    def get_performance_by_period(torneios: List[Dict], period: str = 'monthly') -> List[Dict]:
        """Agrupa performance por período (weekly, monthly, yearly)."""
        if not torneios:
            return []
        
        df = pd.DataFrame(torneios)
        df['data_torneio'] = pd.to_datetime(df['data_torneio'])
        
        # Definir o agrupamento baseado no período
        if period == 'weekly':
            df['periodo'] = df['data_torneio'].dt.to_period('W')
        elif period == 'monthly':
            df['periodo'] = df['data_torneio'].dt.to_period('M')
        elif period == 'yearly':
            df['periodo'] = df['data_torneio'].dt.to_period('Y')
        else:
            df['periodo'] = df['data_torneio'].dt.to_period('M')  # Default para mensal
        
        # Agrupar e calcular estatísticas
        grouped = df.groupby('periodo').agg({
            'buy_in': ['sum', 'count', 'mean'],
            'ganho_total': 'sum',
            'lucro_liquido': 'sum'
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ['periodo', 'total_investido', 'total_torneios', 'abi', 'total_ganhos', 'lucro_liquido']
        
        # Calcular ROI e ITM
        grouped['roi'] = ((grouped['total_ganhos'] - grouped['total_investido']) / grouped['total_investido']) * 100
        grouped['roi'] = grouped['roi'].fillna(0)
        
        # Calcular ITM por período
        itm_by_period = df[df['ganho_total'] > 0].groupby('periodo').size().reset_index(name='itm_count')
        grouped = grouped.merge(itm_by_period, on='periodo', how='left')
        grouped['itm_count'] = grouped['itm_count'].fillna(0)
        grouped['itm_percentage'] = (grouped['itm_count'] / grouped['total_torneios']) * 100
        
        # Converter período para string
        grouped['periodo_str'] = grouped['periodo'].astype(str)
        
        return grouped.to_dict('records')
    
    @staticmethod
    def get_best_and_worst_sessions(torneios: List[Dict], limit: int = 5) -> Dict:
        """Retorna as melhores e piores sessões."""
        if not torneios:
            return {"melhores": [], "piores": []}
        
        # Agrupar por data para considerar sessões diárias
        df = pd.DataFrame(torneios)
        df['data_torneio'] = pd.to_datetime(df['data_torneio']).dt.date
        
        sessoes = df.groupby('data_torneio').agg({
            'buy_in': 'sum',
            'ganho_total': 'sum',
            'lucro_liquido': 'sum'
        }).reset_index()
        
        sessoes['roi'] = ((sessoes['ganho_total'] - sessoes['buy_in']) / sessoes['buy_in']) * 100
        sessoes['roi'] = sessoes['roi'].fillna(0)
        
        # Ordenar para pegar melhores e piores
        melhores = sessoes.nlargest(limit, 'lucro_liquido').to_dict('records')
        piores = sessoes.nsmallest(limit, 'lucro_liquido').to_dict('records')
        
        return {
            "melhores": melhores,
            "piores": piores
        }
    
    @staticmethod
    def calculate_variance_and_downswing(torneios: List[Dict]) -> Dict:
        """Calcula variância e maior downswing."""
        if not torneios:
            return {"variancia": 0, "maior_downswing": 0, "downswing_atual": 0}
        
        # Ordenar por data
        torneios_sorted = sorted(torneios, key=lambda x: x['data_torneio'])
        
        lucros = [t['lucro_liquido'] for t in torneios_sorted]
        
        # Calcular variância
        if len(lucros) > 1:
            variancia = pd.Series(lucros).var()
        else:
            variancia = 0
        
        # Calcular maior downswing
        saldo_acumulado = []
        saldo_atual = 0
        
        for lucro in lucros:
            saldo_atual += lucro
            saldo_acumulado.append(saldo_atual)
        
        # Encontrar maior downswing
        maior_downswing = 0
        pico_atual = saldo_acumulado[0] if saldo_acumulado else 0
        
        for saldo in saldo_acumulado:
            if saldo > pico_atual:
                pico_atual = saldo
            else:
                downswing = pico_atual - saldo
                if downswing > maior_downswing:
                    maior_downswing = downswing
        
        # Downswing atual (do último pico até agora)
        if saldo_acumulado:
            ultimo_pico = max(saldo_acumulado)
            saldo_final = saldo_acumulado[-1]
            downswing_atual = max(0, ultimo_pico - saldo_final)
        else:
            downswing_atual = 0
        
        return {
            "variancia": variancia,
            "maior_downswing": maior_downswing,
            "downswing_atual": downswing_atual
        }
    
    @staticmethod
    def get_hourly_performance(torneios: List[Dict]) -> Dict:
        """Analisa performance por horário (se houver dados de horário)."""
        # Esta função pode ser expandida se houver dados de horário nos torneios
        # Por enquanto, retorna uma estrutura básica
        return {
            "melhor_horario": "N/A",
            "pior_horario": "N/A",
            "performance_por_hora": []
        }
    
    @staticmethod
    def calculate_bankroll_management(torneios: List[Dict], bankroll_inicial: float = 0) -> Dict:
        """Calcula métricas de gestão de bankroll."""
        if not torneios:
            return {
                "bankroll_atual": bankroll_inicial,
                "maior_bankroll": bankroll_inicial,
                "menor_bankroll": bankroll_inicial,
                "buy_ins_restantes": 0
            }
        
        # Ordenar por data
        torneios_sorted = sorted(torneios, key=lambda x: x['data_torneio'])
        
        bankroll_atual = bankroll_inicial
        maior_bankroll = bankroll_inicial
        menor_bankroll = bankroll_inicial
        
        for torneio in torneios_sorted:
            bankroll_atual += torneio['lucro_liquido']
            maior_bankroll = max(maior_bankroll, bankroll_atual)
            menor_bankroll = min(menor_bankroll, bankroll_atual)
        
        # Calcular quantos buy-ins restam (baseado no ABI)
        abi = PokerCalculations.calculate_abi(torneios)
        buy_ins_restantes = bankroll_atual / abi if abi > 0 else 0
        
        return {
            "bankroll_atual": bankroll_atual,
            "maior_bankroll": maior_bankroll,
            "menor_bankroll": menor_bankroll,
            "buy_ins_restantes": buy_ins_restantes
        }

