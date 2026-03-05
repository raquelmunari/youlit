# 🎥 YouLit

> **You**Tube analytics dashboard using Stream**Lit**

Dashboard interativo para análise de métricas de vídeos do YouTube usando Streamlit e YouTube Data API v3.

---

## 📁 Estrutura do Projeto youlit

```
youlit/
├── app.py                     # Aplicação principal Streamlit
├── src/
│   ├── __init__.py           # Inicializador do pacote
│   ├── api.py                # Comunicação com YouTube Data API v3
│   ├── data_processing.py    # Processamento de dados e cálculo de métricas
│   ├── utils.py              # Funções utilitárias
│   └── visualizations.py     # Gráficos interativos com Plotly
├── assets/
│   └── yt_short_icon_red.png # Ícone do YouTube
├── .streamlit/
│   └── config.toml           # Tema e configurações do Streamlit
├── .env                      # Variáveis de ambiente (não versionado)
├── env.example               # Template de configuração
├── requirements.txt          # Dependências Python
└── README.md                 # Documentação (este arquivo)
```

---

## 🚀 Como Executar (após já ter clonado o repositório)

### 1. Configure o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure o arquivo .env

```bash
cp env.example .env
```

Edite o arquivo `.env` e adicione sua chave (necessário) e o java path (se necessário):
```
YOUTUBE_API_KEY=sua_chave_aqui
JAVA_HOME=sua_path_java_aqui
```

### 3. Execute o dashboard
```bash
streamlit run app.py
```

Localmente, o dashboard abrirá em `http://localhost:8501`

---

## 🎯 Funcionalidades

### Tipos de Busca
- **Termo geral**: Pesquisa como no YouTube (ex: "Olivia Rodrigo")
- **Código do canal**: Análise de canal específico (ex: "UCy3zgWom-5AGypGX_FVTKpg")

### KPIs Principais
- Total de Visualizações
- Total de Likes
- Taxa de Engajamento Média
- Média de Visualizações por Dia
- Total de Vídeos Analisados

### Visualizações

**📊 Aba Visualizações:**
- **Top 10 Vídeos por Visualizações**: Barras horizontais ordenadas com links
- **Top 10 Vídeos por Taxa de Engajamento**: Filtrado por mediana de views para evitar distorções
- **Distribuição por Duração**: Curtos (<1min), Médios (1-5min), Longos (>5min)
- **Distribuição por Performance**: Alta (>5%), Média (2-5%), Baixa (<2%)
- **Gráfico de Correlação (Bolhas)**: Duração vs Engajamento (tamanho do plot = quantidade de visualizações)
- **Timeline de Publicações dos Vídeos**: Filtro de vídeo selecionado com destaque visual em vermelho

**🎯 Aba Análises:**
- Insights automáticos (vídeo mais visto, maior engajamento, mais recente)
- Estatísticas por Categoria
- Estatísticas por Canal (quando busca por termo)

**📋 Aba Dados Detalhados:**
- Tabela completa com todas as métricas
- Download em CSV disponível

---

## 📦 Módulos

### `app.py`
Interface principal com Streamlit. Gerencia session_state para persistência de dados entre interações.

### `src/api.py`
**Funções:**
- `get_video_data(query, channel_id, max_results)`: Busca vídeos com paginação até 5 páginas
- `get_category_mapping(language)`: Mapeia IDs de categorias para nomes legíveis

**Características:**
- Filtra apenas vídeos (ignora canais e playlists)
- Ordena por visualizações (viewCount)
- Tratamento de erros (quota, API inválida, etc.)

### `src/data_processing.py`
Processa dados brutos da API usando SQL (pandasql):
- `process_video_data(items)`: Converte para DataFrame com métricas calculadas
- `get_stats_by_channel(df)`: Estatísticas agregadas por canal
- `get_stats_by_category(df)`: Estatísticas agregadas por categoria
- `get_top_video_by_metric(df, metric, order)`: Retorna top vídeo por métrica

### `src/visualizations.py`
Cria gráficos interativos com Plotly:
- `create_top_views_chart()`: Top n vídeos por visualizações
- `create_top_engagement_chart()`: Top n vídeos por engajamento (filtrado pela mediana)
- `create_duration_distribution_chart()`: Distribuição por duração
- `create_performance_distribution_chart()`: Distribuição por performance
- `create_scatter_plot()`: Correlação duração vs engajamento
- `create_timeline_chart()`: Timeline de publicação dos vídeos encontrados

### `src/utils.py`
- `parse_duration_iso8601(duration)`: Converte formato PT#H#M#S para segundos
- `truncate_text(text, max_length)`: Trunca texto para exibição

---

## ⚠️ Limitações da API

| Item | Valor |
|------|-------|
| **Custo por busca** | 100 unidades |
| **Quota diária padrão** | 10.000 unidades (~100 buscas/dia) |
| **Máximo por requisição** | 50 vídeos |
| **Páginas por busca** | Até 5 páginas |

**Por que 5 páginas?**  
A API pode retornar canais e playlists misturados. O sistema busca múltiplas páginas até completar o número de vídeos desejado.

---

### 🔀 Ordenação dos Resultados
Os vídeos são retornados ordenados por **maior número de visualizações** (`order=viewCount`).

---

**Desenvolvido com ❤️**
