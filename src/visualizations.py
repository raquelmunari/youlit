"""
Criação de gráficos e visualizações
"""

import pandas as pd
import plotly.express as px
from .utils import truncate_text


def create_top_views_chart(df, top_n=10):
    """Cria gráfico de top n vídeos por visualizações"""
    top_data = df.nlargest(top_n, 'visualizacoes')[['titulo', 'visualizacoes', 'url', 'canal']].copy()
    top_data['titulo_curto'] = top_data['titulo'].apply(lambda x: truncate_text(x, 40))
    
    fig = px.bar(
        top_data,
        x='visualizacoes',
        y='titulo_curto',
        orientation='h', # Barras da esquerda para a direita
        title=f'Top {top_n} Vídeos por Visualizações',
        labels={'visualizacoes': 'Visualizações', 'titulo_curto': ''},
        color='visualizacoes', # Usa o valor da visualização para a intensidade da cor
        color_continuous_scale='Reds'
    )
    
    # Personalizar hover
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>Canal: %{customdata[1]}<br>Visualizações: %{x:,.0f}<extra></extra>',
        customdata=top_data[['titulo', 'canal']].values
    )
    
    #Personalizar o layout do gráfico
    fig.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig, top_data


def create_top_engagement_chart(df, top_n=10):
    """Cria gráfico de top n vídeos por taxa de engajamento (com filtro de visualizações mínimas)"""
    # Filtrar vídeos com visualizações mínimas (mediana) para evitar distorções no gráfico
    threshold = df['visualizacoes'].median()
    df_filtered = df[df['visualizacoes'] >= threshold].copy()
    
    if len(df_filtered) < top_n:
        df_filtered = df.copy()
        threshold = 0
    
    top_data = df_filtered.nlargest(top_n, 'taxa_engajamento')[['titulo', 'taxa_engajamento', 'url', 'canal', 'visualizacoes']].copy()
    top_data['titulo_curto'] = top_data['titulo'].apply(lambda x: truncate_text(x, 40))
    
    fig = px.bar(
        top_data,
        x='taxa_engajamento',
        y='titulo_curto',
        orientation='h', # Barras da esquerda para a direita
        title=f'Top {top_n} Vídeos por Taxa de Engajamento',
        labels={'taxa_engajamento': 'Taxa de Engajamento (%)', 'titulo_curto': ''},
        color='taxa_engajamento',  # Usa o valor da taxa de engajamento para a intensidade da cor
        color_continuous_scale='Reds'
    )
    
    # Personalizar hover
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>Canal: %{customdata[1]}<br>Taxa de Engajamento: %{x:.2f}%<br>Visualizações: %{customdata[2]:,.0f}<extra></extra>',
        customdata=top_data[['titulo', 'canal', 'visualizacoes']].values
    )
    
    # Personalizar o layout do gráfico
    fig.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig, top_data, threshold


def create_duration_distribution_chart(df):
    """Cria gráfico de distribuição por duração dos vídeos"""
    dist_data = df['categoria_duracao'].value_counts().reset_index()
    dist_data.columns = ['Categoria', 'Quantidade']
    
    # Ordenar por vídeo com classificaçãoCurto, Médio e Longo
    order = ['Curto (<1min)', 'Médio (1-5min)', 'Longo (>5min)']
    dist_data['Categoria'] = pd.Categorical(dist_data['Categoria'], categories=order, ordered=True)
    dist_data = dist_data.sort_values('Categoria')

    colors = {'Curto (<1min)': '#FF8A8A', 'Médio (1-5min)': '#FF0000', 'Longo (>5min)': '#9C2007'}
    
    fig = px.bar(
        dist_data,
        x='Categoria',
        y='Quantidade',
        title='Distribuição por Duração',
        color='Categoria',
        color_discrete_map=colors
    )
    
    # Personalizar hover
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Quantidade de Vídeos: %{y}<extra></extra>'
    )
    
    # Personalizar o layout do gráfico
    fig.update_layout(height=400, showlegend=False)
    
    return fig


def create_performance_distribution_chart(df):
    """Cria gráfico de distribuição por performance dos vídeos"""
    dist_data = df['status_performance'].value_counts().reset_index()
    dist_data.columns = ['Performance', 'Quantidade']
    
    # Ordenar por performance Baixa, Média e Alta
    order = ['Baixa', 'Média', 'Alta']
    dist_data['Performance'] = pd.Categorical(dist_data['Performance'], categories=order, ordered=True)
    dist_data = dist_data.sort_values('Performance')
    
    colors = {'Baixa': '#FF8A8A', 'Média': '#FF0000', 'Alta': '#9C2007'}
    
    fig = px.bar(
        dist_data,
        x='Performance',
        y='Quantidade',
        title='Distribuição por Status de Performance',
        color='Performance',
        color_discrete_map=colors
    )
    
    # Personalizar hover
    fig.update_traces(
        hovertemplate='<b>Performance %{x}</b><br>Quantidade de Vídeos: %{y}<extra></extra>'
    )
    
    # Personalizar o layout do gráfico
    fig.update_layout(height=400, showlegend=False)
    
    return fig


def create_scatter_plot(df):
    """Cria gráfico de dispersão: duração vs engajamento (tamanho das bolhas = quantidade de visualizações)"""
    df_scatter = df.copy()
    
    fig = px.scatter(
        df_scatter,
        x='duracao_minutos',
        y='taxa_engajamento',
        size='visualizacoes',
        color='status_performance',
        title='Relação entre Duração e Taxa de Engajamento',
        labels={
            'duracao_minutos': 'Duração (minutos)',
            'taxa_engajamento': 'Taxa de Engajamento (%)',
            'status_performance': 'Performance'
        },
        color_discrete_map={'Baixa': '#FF8A8A', 'Média': '#FF0000', 'Alta': '#9C2007'},
        category_orders={'status_performance': ['Baixa', 'Média', 'Alta']}
    )
    
    # Personalizar hover (conforme a categoria de performance)
    for trace in fig.data:
        # Filtrar dados correspondentes a este trace (tipo de performance) específico
        performance_category = trace.name
        df_trace = df_scatter[df_scatter['status_performance'] == performance_category]
        
        trace.customdata = df_trace[['titulo', 'canal', 'visualizacoes', 'status_performance']].values
        trace.hovertemplate = '<b>%{customdata[0]}</b><br>Canal: %{customdata[1]}<br>Duração: %{x:.2f} min<br>Taxa de Engajamento: %{y:.2f}%<br>Visualizações: %{customdata[2]:,.0f}<br>Performance: %{customdata[3]}<extra></extra>'
    
    # Personalizar o layout do gráfico
    fig.update_layout(height=500)
    
    # Calcular percentuais de distribuição
    perf_counts = df['status_performance'].value_counts(normalize=True) * 100
    perf_pcts = {k: round(v, 1) for k, v in perf_counts.items()}
    
    return fig, perf_pcts


def create_timeline_chart(df, selected_videos=None):
    """
    Cria gráfico de timeline mostrando todos os vídeos postados (referente ao termo ou canal) ao longo do tempo,
    com destaque para o vídeo selecionado
    Args:
        df: DataFrame com dados dos vídeos
        selected_videos: Lista com o título do vídeo a ser destacado
    """
    df_sorted = df.sort_values('data_publicacao').copy()
    
    # Adicionar coluna de destaque
    selected_title = selected_videos[0] if selected_videos else None
    df_sorted['destaque'] = df_sorted['titulo'].apply(
        lambda x: '⭐ ' + truncate_text(x, 40) if x == selected_title else truncate_text(x, 40)
    )
    df_sorted['is_selected'] = df_sorted['titulo'] == selected_title
    
    # Formatar data para exibição no hover
    df_sorted['data_formatada'] = pd.to_datetime(df_sorted['data_publicacao']).dt.strftime('%d/%m/%Y')
    
    # Criar gráfico com todos os vídeos
    fig = px.line(
        df_sorted,
        x='data_publicacao',
        y='visualizacoes',
        title='Timeline de Publicações ao Longo do Tempo',
        labels={'data_publicacao': 'Data de Publicação', 'visualizacoes': 'Visualizações'},
        markers=True
    )
    
    # Personalizar hover e linhas e bolhas não destacadas
    fig.update_traces(
        line=dict(width=2, color='#FFB3B3'),
        marker=dict(size=8, color='#FFB3B3'),
        opacity=0.5,
        hovertemplate='<b>%{customdata[0]}</b><br>Canal: %{customdata[1]}<br>Visualizações: %{customdata[2]:,.0f}<br>Data de Publicação: %{customdata[3]}<extra></extra>',
        customdata=df_sorted[['titulo', 'canal', 'visualizacoes', 'data_formatada']].values
    )
    
    # Adicionar linha destacada para o vídeo selecionado
    if selected_title:
        df_selected = df_sorted[df_sorted['is_selected']]
        if not df_selected.empty:
            fig.add_scatter(
                x=df_selected['data_publicacao'],
                y=df_selected['visualizacoes'],
                mode='lines+markers',
                name=truncate_text(selected_title, 50),
                line=dict(width=4, color='#FF0000'),
                marker=dict(size=14, color='#FF0000'),
                hovertemplate='<b>%{customdata[0]}</b><br>Canal: %{customdata[1]}<br>Visualizações: %{customdata[2]:,.0f}<br>Data de Publicação: %{customdata[3]}<extra></extra>',
                customdata=df_selected[['titulo', 'canal', 'visualizacoes', 'data_formatada']].values
            )

    # Personalizar o layout do gráfico
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

