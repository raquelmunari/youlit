"""
Processamento dos dados brutos da API do YouTube
"""

import pandas as pd
from pandasql import sqldf
from .api import get_category_mapping
from .utils import parse_duration_iso8601


def process_video_data(items):
    """Processa dados da API e os retorna em um DataFrame"""
    if not items:
        return pd.DataFrame()
    
    # Obter mapeamento de categorias
    category_map = get_category_mapping(language='pt')
    
    data = []
    data_atual = pd.Timestamp.now(tz='UTC')
    
    for item in items:
        # Extrair duração e converter para segundos
        duration_str = item.get('contentDetails', {}).get('duration', 'PT0S')
        duration_seconds = parse_duration_iso8601(duration_str)
        
        # Extrair dados básicos
        video_id = item['id']
        titulo = item['snippet']['title']
        canal = item['snippet']['channelTitle']
        channel_id = item['snippet'].get('channelId', '')
        category_id = item['snippet'].get('categoryId', '')
        categoria = category_map.get(category_id, f"Categoria {category_id}")
        
        visualizacoes = int(item['statistics'].get('viewCount', 0))
        likes = int(item['statistics'].get('likeCount', 0))
        comentarios = int(item['statistics'].get('commentCount', 0))
        
        # Data de publicação
        data_pub_str = item['snippet']['publishedAt']
        data_publicacao = pd.to_datetime(data_pub_str)
        
        # Calcular idade em dias
        idade_dias = (data_atual - data_publicacao).days
        if idade_dias == 0:
            idade_dias = 1  # Evitar divisão por zero
        
        # URL do vídeo
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        data.append({
            'video_id': video_id,
            'titulo': titulo,
            'canal': canal,
            'channel_id': channel_id,
            'categoria': categoria,
            'visualizacoes': visualizacoes,
            'likes': likes,
            'comentarios': comentarios,
            'duracao_segundos': duration_seconds,
            'data_publicacao': data_publicacao,
            'idade_dias': idade_dias,
            'url': url
        })
    
    # Criar DataFrame bruto
    df_raw = pd.DataFrame(data)
    
    query = """
        SELECT 
            video_id,
            titulo,
            canal,
            channel_id,
            categoria,
            visualizacoes,
            likes,
            comentarios,
            
            -- Duração em minutos dos vídeos
            ROUND(duracao_segundos / 60.0, 2) as duracao_minutos,
            
            -- Taxa de engajamento
            ROUND(
                CASE 
                    WHEN visualizacoes > 0 
                    THEN ((likes + comentarios) * 100.0 / visualizacoes)
                    ELSE 0 
                END, 
                2
            ) as taxa_engajamento,
            
            -- Visualizações por dia
            ROUND(
                CAST(visualizacoes AS REAL) / idade_dias, 
                2
            ) as visualizacoes_por_dia,
            
            -- Categoria de duração
            CASE 
                WHEN (duracao_segundos / 60.0) < 1 THEN 'Curto (<1min)'
                WHEN (duracao_segundos / 60.0) >= 1 
                     AND (duracao_segundos / 60.0) <= 5 THEN 'Médio (1-5min)'
                ELSE 'Longo (>5min)'
            END as categoria_duracao,
            
            -- Status de performance
            CASE 
                WHEN ((likes + comentarios) * 100.0 / NULLIF(visualizacoes, 0)) > 5 
                    THEN 'Alta'
                WHEN ((likes + comentarios) * 100.0 / NULLIF(visualizacoes, 0)) >= 2 
                     AND ((likes + comentarios) * 100.0 / NULLIF(visualizacoes, 0)) <= 5 
                    THEN 'Média'
                ELSE 'Baixa'
            END as status_performance,
            
            data_publicacao,
            idade_dias,
            url
            
        FROM df_raw
        ORDER BY visualizacoes DESC
    """
    
    # Executar SQL e obter DataFrame processado
    df = sqldf(query, locals())
    
    return df


def get_stats_by_channel(df):
    """
    Calcula estatísticas agregadas por canal
    Usa o DataFrame já processado como entrada
    """
    query = """
        SELECT 
            canal,
            SUM(visualizacoes) as total_views,
            SUM(likes) as total_likes,
            SUM(comentarios) as total_comentarios,
            ROUND(AVG(taxa_engajamento), 2) as eng_medio,
            COUNT(*) as num_videos
        FROM df
        GROUP BY canal
        ORDER BY total_views DESC
    """
    
    stats = sqldf(query, locals())
    stats.columns = ['Canal', 'Total Views', 'Total Likes', 'Total Comentários', 'Eng. Médio (%)', 'Nº Vídeos']
    stats.set_index('Canal', inplace=True)
    
    return stats


def get_stats_by_category(df):
    """
    Calcula estatísticas agregadas por categoria
    Usa o DataFrame já processado como entrada
    """
    query = """
        SELECT 
            categoria,
            ROUND(AVG(visualizacoes), 2) as media_views,
            ROUND(AVG(taxa_engajamento), 2) as eng_medio,
            COUNT(*) as num_videos
        FROM df
        GROUP BY categoria
        ORDER BY media_views DESC
    """
    
    stats = sqldf(query, locals())
    stats.columns = ['Categoria', 'Média Views', 'Eng. Médio (%)', 'Nº Vídeos']
    stats.set_index('Categoria', inplace=True)
    
    return stats


def get_top_video_by_metric(df, metric='visualizacoes', order='DESC'):
    """
    Obtém o vídeo com maior/menor valor de uma métrica específica
    
    Args:
        df: DataFrame processado
        metric: Nome da coluna métrica (ex: 'visualizacoes', 'taxa_engajamento', 'data_publicacao')
        order: Ordenação 'DESC' ou 'ASC' 
    """
    query = f"""
        SELECT *
        FROM df
        ORDER BY {metric} {order}
        LIMIT 1
    """
    
    result = sqldf(query, locals())
    return result.iloc[0] if not result.empty else None

