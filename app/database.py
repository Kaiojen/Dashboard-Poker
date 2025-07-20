import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from dotenv import load_dotenv
import psycopg2

class PokerDatabase:
    def __init__(self, db_path: str = "poker_dashboard.db"):
        load_dotenv()
        self.db_url = os.getenv("DATABASE_URL")
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Cria uma conexão com o banco de dados."""
        if self.db_url:
            return psycopg2.connect(self.db_url)
        return sqlite3.connect(self.db_path)

    def _execute(self, cursor, query: str, params: Tuple = ()):
        """Executa query adaptando placeholders para o banco configurado."""
        if self.db_url:
            query = query.replace("?", "%s")
        cursor.execute(query, params)
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Criar tabela de contas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contas (
                id_conta INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_conta TEXT NOT NULL UNIQUE,
                email TEXT
            )
        ''')
        
        # Criar tabela de tipos de torneio
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipos_torneio (
                id_tipo_torneio INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_tipo TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Criar tabela de torneios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS torneios (
                id_torneio INTEGER PRIMARY KEY AUTOINCREMENT,
                data_torneio DATE NOT NULL,
                id_conta INTEGER NOT NULL,
                id_tipo_torneio INTEGER NOT NULL,
                buy_in DECIMAL(10,2) NOT NULL,
                ganho_total DECIMAL(10,2) NOT NULL DEFAULT 0,
                FOREIGN KEY (id_conta) REFERENCES contas (id_conta),
                FOREIGN KEY (id_tipo_torneio) REFERENCES tipos_torneio (id_tipo_torneio)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Inserir dados iniciais
        self.insert_initial_data()
    
    def insert_initial_data(self):
        """Insere dados iniciais de contas e tipos de torneio."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Contas iniciais
        contas_iniciais = [
            ("PKagente", ""),  # Conta de agente
            ("I´Dr.t", "gabrielpecanha103@gmail.com"),
            ("JiNRiuk", "poker.cont002@gmail.com"),
            ("Blackk_killer", "testes404az@gmail.com"),
            ("I´mDrFIsh", "testes200y@gmail.com"),
            ("kaiojen", "testes300y@gmail.com")
        ]
        
        for nome_conta, email in contas_iniciais:
            self._execute(cursor, '''
                INSERT OR IGNORE INTO contas (nome_conta, email)
                VALUES (?, ?)
            ''', (nome_conta, email))
        
        # Tipos de torneio iniciais
        tipos_torneio_iniciais = ["Mystery", "Battle", "Plus", "Reentry", "Freeze", "Bounty"]
        
        for tipo in tipos_torneio_iniciais:
            self._execute(cursor, '''
                INSERT OR IGNORE INTO tipos_torneio (nome_tipo)
                VALUES (?)
            ''', (tipo,))
        
        conn.commit()
        conn.close()
    
    def get_contas(self) -> List[Dict]:
        """Retorna todas as contas."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_conta, nome_conta, email FROM contas ORDER BY nome_conta")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [{"id": row[0], "nome": row[1], "email": row[2]} for row in rows]
    
    def get_tipos_torneio(self) -> List[Dict]:
        """Retorna todos os tipos de torneio."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_tipo_torneio, nome_tipo FROM tipos_torneio ORDER BY nome_tipo")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [{"id": row[0], "nome": row[1]} for row in rows]
    
    def insert_torneio(self, data_torneio: str, id_conta: int, id_tipo_torneio: int, 
                      buy_in: float, ganho_total: float) -> bool:
        """Insere um novo torneio no banco de dados."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            self._execute(cursor, '''
                INSERT INTO torneios (data_torneio, id_conta, id_tipo_torneio, buy_in, ganho_total)
                VALUES (?, ?, ?, ?, ?)
            ''', (data_torneio, id_conta, id_tipo_torneio, buy_in, ganho_total))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao inserir torneio: {e}")
            return False
    
    def get_torneios(self, id_conta: Optional[int] = None, 
                    id_tipo_torneio: Optional[int] = None,
                    data_inicio: Optional[str] = None,
                    data_fim: Optional[str] = None) -> List[Dict]:
        """Retorna torneios com filtros opcionais."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT t.id_torneio, t.data_torneio, c.nome_conta, tt.nome_tipo,
                   t.buy_in, t.ganho_total, 
                   (t.ganho_total - t.buy_in) as lucro_liquido,
                   CASE 
                       WHEN t.buy_in > 0 THEN ((t.ganho_total - t.buy_in) / t.buy_in) * 100
                       ELSE 0
                   END as roi
            FROM torneios t
            JOIN contas c ON t.id_conta = c.id_conta
            JOIN tipos_torneio tt ON t.id_tipo_torneio = tt.id_tipo_torneio
            WHERE 1=1
        '''
        
        params = []
        
        if id_conta:
            query += " AND t.id_conta = ?"
            params.append(id_conta)
        
        if id_tipo_torneio:
            query += " AND t.id_tipo_torneio = ?"
            params.append(id_tipo_torneio)
        
        if data_inicio:
            query += " AND t.data_torneio >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND t.data_torneio <= ?"
            params.append(data_fim)
        
        query += " ORDER BY t.data_torneio DESC"
        
        self._execute(cursor, query, tuple(params))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [{
            "id_torneio": row[0],
            "data_torneio": row[1],
            "nome_conta": row[2],
            "nome_tipo": row[3],
            "buy_in": row[4],
            "ganho_total": row[5],
            "lucro_liquido": row[6],
            "roi": row[7]
        } for row in rows]
    
    def get_estatisticas_gerais(self, id_conta: Optional[int] = None,
                               data_inicio: Optional[str] = None,
                               data_fim: Optional[str] = None) -> Dict:
        """Retorna estatísticas gerais dos torneios."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                COUNT(*) as total_torneios,
                SUM(buy_in) as total_investido,
                SUM(ganho_total) as total_ganhos,
                SUM(ganho_total - buy_in) as lucro_liquido,
                CASE 
                    WHEN SUM(buy_in) > 0 THEN (SUM(ganho_total - buy_in) / SUM(buy_in)) * 100
                    ELSE 0
                END as roi_geral,
                AVG(buy_in) as abi,
                COUNT(CASE WHEN ganho_total > 0 THEN 1 END) as itm_count
            FROM torneios t
            WHERE 1=1
        '''
        
        params = []
        
        if id_conta:
            query += " AND t.id_conta = ?"
            params.append(id_conta)
        
        if data_inicio:
            query += " AND t.data_torneio >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND t.data_torneio <= ?"
            params.append(data_fim)
        
        self._execute(cursor, query, tuple(params))
        row = cursor.fetchone()
        
        conn.close()
        
        if row and row[0] > 0:  # Se há torneios
            itm_percentage = (row[6] / row[0]) * 100 if row[0] > 0 else 0
            return {
                "total_torneios": row[0],
                "total_investido": row[1] or 0,
                "total_ganhos": row[2] or 0,
                "lucro_liquido": row[3] or 0,
                "roi_geral": row[4] or 0,
                "abi": row[5] or 0,
                "itm_percentage": itm_percentage
            }
        else:
            return {
                "total_torneios": 0,
                "total_investido": 0,
                "total_ganhos": 0,
                "lucro_liquido": 0,
                "roi_geral": 0,
                "abi": 0,
                "itm_percentage": 0
            }
    
    def get_estatisticas_por_tipo(self, id_conta: Optional[int] = None,
                                 data_inicio: Optional[str] = None,
                                 data_fim: Optional[str] = None) -> List[Dict]:
        """Retorna estatísticas agrupadas por tipo de torneio."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                tt.nome_tipo,
                COUNT(*) as total_torneios,
                SUM(t.buy_in) as total_investido,
                SUM(t.ganho_total) as total_ganhos,
                SUM(t.ganho_total - t.buy_in) as lucro_liquido,
                CASE 
                    WHEN SUM(t.buy_in) > 0 THEN (SUM(t.ganho_total - t.buy_in) / SUM(t.buy_in)) * 100
                    ELSE 0
                END as roi
            FROM torneios t
            JOIN tipos_torneio tt ON t.id_tipo_torneio = tt.id_tipo_torneio
            WHERE 1=1
        '''
        
        params = []
        
        if id_conta:
            query += " AND t.id_conta = ?"
            params.append(id_conta)
        
        if data_inicio:
            query += " AND t.data_torneio >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND t.data_torneio <= ?"
            params.append(data_fim)
        
        query += " GROUP BY tt.nome_tipo ORDER BY lucro_liquido DESC"
        
        self._execute(cursor, query, tuple(params))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [{
            "nome_tipo": row[0],
            "total_torneios": row[1],
            "total_investido": row[2] or 0,
            "total_ganhos": row[3] or 0,
            "lucro_liquido": row[4] or 0,
            "roi": row[5] or 0
        } for row in rows]
    
    def backup_database(self, backup_path: str) -> bool:
        """Cria um backup do banco de dados."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Erro ao fazer backup: {e}")
            return False



    def delete_torneio(self, id_torneio: int) -> bool:
        """Deleta um torneio do banco de dados."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            self._execute(cursor, "DELETE FROM torneios WHERE id_torneio = ?", (id_torneio,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao deletar torneio: {e}")
            return False

    def update_torneio(self, id_torneio: int, data_torneio: str, id_conta: int, id_tipo_torneio: int, buy_in: float, ganho_total: float) -> bool:
        """Atualiza os dados de um torneio existente."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            self._execute(cursor, '''
                UPDATE torneios
                SET data_torneio = ?, id_conta = ?, id_tipo_torneio = ?, buy_in = ?, ganho_total = ?
                WHERE id_torneio = ?
            ''', (data_torneio, id_conta, id_tipo_torneio, buy_in, ganho_total, id_torneio))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar torneio: {e}")
            return False


