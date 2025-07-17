# Dashboard Suprema Poker

Este projeto é um dashboard para análise de dados do Suprema Poker.

## Estrutura do Projeto

```
├── app/                  # Código principal da aplicação
│   ├── __init__.py
│   ├── app_final.py
│   ├── calculations.py
│   ├── database.py
│   ├── export.py
│   ├── main.py
│   └── plotting.py
│
├── tests/                # Testes automatizados
│   └── (adicione seus testes aqui)
│
├── requirements.txt      # Dependências do projeto
├── README.md             # Este arquivo
├── .gitignore            # Ignora arquivos desnecessários
└── start_dashboard.sh    # Script para iniciar o dashboard
```

## Como rodar o projeto

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Execute o dashboard:

```bash
cd app
python main.py
```

Ou utilize o script:

```bash
./start_dashboard.sh
```

## Testes

Coloque seus testes automatizados na pasta `tests/`.

---

> Estrutura organizada seguindo boas práticas para facilitar manutenção e escalabilidade.
