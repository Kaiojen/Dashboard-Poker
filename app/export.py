import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import base64

class PokerExport:
    
    @staticmethod
    def export_to_csv(torneios: List[Dict], filename: str = None) -> str:
        """Exporta dados dos torneios para CSV."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"torneios_poker_{timestamp}.csv"
        
        # Converter para DataFrame
        df = pd.DataFrame(torneios)
        
        # Reordenar e renomear colunas
        if not df.empty:
            df = df[['data_torneio', 'nome_conta', 'nome_tipo', 'buy_in', 'ganho_total', 'lucro_liquido', 'roi']]
            df.columns = ['Data', 'Conta', 'Tipo de Torneio', 'Buy-in (R$)', 'Ganho Total (R$)', 'Lucro Líquido (R$)', 'ROI (%)']
        
        # Salvar CSV
        filepath = os.path.join("/home/ubuntu/poker_dashboard", filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath
    
    @staticmethod
    def export_to_excel(torneios: List[Dict], estatisticas: Dict, estatisticas_por_tipo: List[Dict], filename: str = None) -> str:
        """Exporta dados completos para Excel com múltiplas abas."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dashboard_poker_{timestamp}.xlsx"
        
        filepath = os.path.join("/home/ubuntu/poker_dashboard", filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Aba 1: Torneios detalhados
            if torneios:
                df_torneios = pd.DataFrame(torneios)
                df_torneios = df_torneios[['data_torneio', 'nome_conta', 'nome_tipo', 'buy_in', 'ganho_total', 'lucro_liquido', 'roi']]
                df_torneios.columns = ['Data', 'Conta', 'Tipo de Torneio', 'Buy-in (R$)', 'Ganho Total (R$)', 'Lucro Líquido (R$)', 'ROI (%)']
                df_torneios.to_excel(writer, sheet_name='Torneios', index=False)
            
            # Aba 2: Estatísticas gerais
            df_stats = pd.DataFrame([estatisticas])
            df_stats.columns = ['Total de Torneios', 'Total Investido (R$)', 'Total Ganhos (R$)', 
                               'Lucro Líquido (R$)', 'ROI Geral (%)', 'ABI (R$)', 'ITM (%)']
            df_stats.to_excel(writer, sheet_name='Estatísticas Gerais', index=False)
            
            # Aba 3: Estatísticas por tipo
            if estatisticas_por_tipo:
                df_tipos = pd.DataFrame(estatisticas_por_tipo)
                df_tipos.columns = ['Tipo de Torneio', 'Total de Torneios', 'Total Investido (R$)', 
                                   'Total Ganhos (R$)', 'Lucro Líquido (R$)', 'ROI (%)']
                df_tipos.to_excel(writer, sheet_name='Por Tipo de Torneio', index=False)
        
        return filepath
    
    @staticmethod
    def export_to_pdf(torneios: List[Dict], estatisticas: Dict, estatisticas_por_tipo: List[Dict], filename: str = None) -> str:
        """Exporta relatório completo para PDF."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_poker_{timestamp}.pdf"
        
        filepath = os.path.join("/home/ubuntu/poker_dashboard", filename)
        
        # Criar documento PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Título
        story.append(Paragraph("♠️ Relatório Dashboard Suprema Poker ♠️", title_style))
        story.append(Spacer(1, 20))
        
        # Data do relatório
        data_relatorio = datetime.now().strftime("%d/%m/%Y às %H:%M")
        story.append(Paragraph(f"Relatório gerado em: {data_relatorio}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Estatísticas gerais
        story.append(Paragraph("📈 Estatísticas Gerais", heading_style))
        
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de Torneios', f"{estatisticas['total_torneios']}"],
            ['Total Investido', f"R$ {estatisticas['total_investido']:.2f}"],
            ['Total Ganhos', f"R$ {estatisticas['total_ganhos']:.2f}"],
            ['Lucro Líquido', f"R$ {estatisticas['lucro_liquido']:.2f}"],
            ['ROI Geral', f"{estatisticas['roi_geral']:.1f}%"],
            ['ABI (Average Buy-in)', f"R$ {estatisticas['abi']:.2f}"],
            ['ITM (In The Money)', f"{estatisticas['itm_percentage']:.1f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Estatísticas por tipo de torneio
        if estatisticas_por_tipo:
            story.append(Paragraph("🎯 Performance por Tipo de Torneio", heading_style))
            
            tipo_data = [['Tipo', 'Torneios', 'Investido (R$)', 'Ganhos (R$)', 'Lucro (R$)', 'ROI (%)']]
            
            for tipo in estatisticas_por_tipo:
                tipo_data.append([
                    tipo['nome_tipo'],
                    str(tipo['total_torneios']),
                    f"R$ {tipo['total_investido']:.2f}",
                    f"R$ {tipo['total_ganhos']:.2f}",
                    f"R$ {tipo['lucro_liquido']:.2f}",
                    f"{tipo['roi']:.1f}%"
                ])
            
            tipo_table = Table(tipo_data, colWidths=[1.2*inch, 0.8*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
            tipo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(tipo_table)
            story.append(PageBreak())
        
        # Torneios recentes (últimos 20)
        if torneios:
            story.append(Paragraph("📋 Torneios Recentes (Últimos 20)", heading_style))
            
            torneios_data = [['Data', 'Conta', 'Tipo', 'Buy-in', 'Ganho', 'Lucro', 'ROI']]
            
            for torneio in torneios[:20]:  # Últimos 20
                torneios_data.append([
                    torneio['data_torneio'],
                    torneio['nome_conta'][:10] + '...' if len(torneio['nome_conta']) > 10 else torneio['nome_conta'],
                    torneio['nome_tipo'][:8] + '...' if len(torneio['nome_tipo']) > 8 else torneio['nome_tipo'],
                    f"R$ {torneio['buy_in']:.0f}",
                    f"R$ {torneio['ganho_total']:.0f}",
                    f"R$ {torneio['lucro_liquido']:.0f}",
                    f"{torneio['roi']:.0f}%"
                ])
            
            torneios_table = Table(torneios_data, colWidths=[0.8*inch, 1*inch, 0.8*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.6*inch])
            torneios_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(torneios_table)
        
        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph("Dashboard Suprema Poker - Relatório gerado automaticamente", styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        
        return filepath
    
    @staticmethod
    def create_backup(db_path: str, backup_dir: str = "/home/ubuntu/poker_dashboard/backups") -> str:
        """Cria backup do banco de dados."""
        import shutil
        
        # Criar diretório de backup se não existir
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"poker_dashboard_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copiar arquivo
        shutil.copy2(db_path, backup_path)
        
        return backup_path
    
    @staticmethod
    def get_download_link(filepath: str, link_text: str = "Download") -> str:
        """Cria link de download para Streamlit."""
        with open(filepath, "rb") as f:
            bytes_data = f.read()
        
        b64 = base64.b64encode(bytes_data).decode()
        filename = os.path.basename(filepath)
        
        # Determinar tipo MIME baseado na extensão
        if filepath.endswith('.csv'):
            mime_type = 'text/csv'
        elif filepath.endswith('.xlsx'):
            mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif filepath.endswith('.pdf'):
            mime_type = 'application/pdf'
        else:
            mime_type = 'application/octet-stream'
        
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">{link_text}</a>'
        return href
    
    @staticmethod
    def cleanup_old_files(directory: str, max_age_days: int = 7):
        """Remove arquivos antigos do diretório."""
        import time
        
        if not os.path.exists(directory):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass  # Ignorar erros de remoção

