# Changelog - Dashboard Suprema Poker

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2025-07-17

### ✨ Adicionado
- **Funcionalidade de Exclusão de Torneios**
  - Interface para seleção de torneios específicos
  - Confirmação de exclusão para evitar remoções acidentais
  - Atualização automática da interface após exclusão
  - Função `delete_torneio()` no database.py

- **Novos Tipos de Torneio**
  - **Freeze**: Torneios Freezeout (sem recompra)
  - **Bounty**: Torneios com sistema de recompensas
  - Atualização automática do banco de dados

### 🔄 Modificado
- **Interface do Usuário**
  - Nova seção "🗑️ Excluir Torneio" na sidebar
  - Atualização da documentação inline
  - Melhor organização dos controles na sidebar

- **Banco de Dados**
  - Função `insert_initial_data()` atualizada
  - Novos tipos de torneio adicionados automaticamente
  - Melhoria na estrutura de dados

- **Documentação**
  - README.md completamente reescrito
  - Dashboard Suprema Poker - Entrega Final.md atualizado
  - Instruções de uso atualizadas
  - Changelog criado

### 🐛 Corrigido
- Correção na formatação de strings no selectbox de exclusão
- Melhoria na validação de dados
- Otimização das consultas ao banco

## [1.0.0] - 2025-07-16

### ✨ Funcionalidades Iniciais
- Dashboard completo para controle de resultados
- Inserção de torneios
- Métricas avançadas (ROI, ITM, ABI, Downswing)
- Gráficos interativos
- Sistema de filtros
- Exportação (CSV, Excel, PDF)
- Backup de dados
- 6 contas configuradas
- 4 tipos de torneio iniciais (Mystery, Battle, Plus, Reentry)

### 🔧 Tecnologias
- Streamlit para interface
- Flask para deploy
- SQLite para dados
- Plotly para gráficos
- Pandas para processamento

---

## Tipos de Mudanças
- `✨ Adicionado` para novas funcionalidades
- `🔄 Modificado` para mudanças em funcionalidades existentes
- `🐛 Corrigido` para correções de bugs
- `🗑️ Removido` para funcionalidades removidas
- `🔒 Segurança` para correções de vulnerabilidades

