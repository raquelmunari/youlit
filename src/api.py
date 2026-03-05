"""
Comunicação com a API do YouTube
"""

import os
import streamlit as st
from dotenv import load_dotenv
from googleapiclient.discovery import build


# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    st.error("⚠️ YOUTUBE_API_KEY não encontrada! Crie um arquivo .env com sua chave.")
    st.stop()

youtube = build('youtube', 'v3', developerKey=API_KEY)


def get_category_mapping(language='pt'):
    """
    Busca categorias do YouTube
    Args:
        language: Código do idioma
    Returns:
        dict: {categoryId: categoryTitle}
    """
    try:
        categories_response = youtube.videoCategories().list(
            part='snippet',
            regionCode='US',
            hl=language
        ).execute()
        
        category_map = {}
        for item in categories_response.get('items', []):
            category_id = item['id']
            category_title = item['snippet']['title']
            category_map[category_id] = category_title
        
        return category_map
    except Exception as e:
        st.warning(f"Erro ao buscar categorias: {e}")
        return {}


def get_video_data(query=None, channel_id=None, max_results=50):
    """
    Busca vídeos do YouTube por diferentes critérios
    Garante que retorna exatamente max_results vídeos (excluindo canais/playlists), quando possível
    Args:
        query: Termo de busca
        channel_id: Código do canal
        max_results: Número máximo de resultados
    Returns:
        dict: {
            'items': Lista de itens de vídeo da API do YouTube,
            'stats': {
                'videos': Número de vídeos encontrados,
                'channels': Número de canais encontrados,
                'playlists': Número de playlists encontradas,
                'pages_processed': Número de páginas processadas
            }
        }
    """
    try:
        # Construir parâmetros da busca
        search_params = {
            'part': 'id,snippet',
            'maxResults': min(50, max_results),  # API permite no máximo 50 por requisição
            'type': 'video', # Está retornando outros tipos de resultados, mesmo com esse parâmetro, mas é tratado para retornar apenas vídeos
            'order': 'viewCount' # Retorna resultados do maior para o menor número de visualizações
        }
        
        # Adicionar query ou channelId nos parâmetros da busca
        if query:
            search_params['q'] = query
        elif channel_id:
            search_params['channelId'] = channel_id
        
        # Buscar vídeos até completar o max_results
        video_ids = []
        page_token = None
        max_pages = 5  # Limitar a 5 páginas para não exceder quota
        pages_processed = 0
        
        # Contadores para estatísticas
        total_videos = 0
        total_channels = 0
        total_playlists = 0
        
        while len(video_ids) < max_results and max_pages > 0:
            # Adicionar pageToken se houver
            if page_token:
                search_params['pageToken'] = page_token
            
            # Buscar resultados
            search_response = youtube.search().list(**search_params).execute()
            pages_processed += 1
            
            # Extrair video_ids e contar tipos de resultados
            for item in search_response.get('items', []):
                kind = item.get('id', {}).get('kind', '')
                
                # Contar tipos de resultados
                if kind == 'youtube#video':
                    total_videos += 1
                elif kind == 'youtube#channel':
                    total_channels += 1
                elif kind == 'youtube#playlist':
                    total_playlists += 1
                
                # Adicionar apenas vídeos à lista
                if len(video_ids) >= max_results:
                    continue
                
                if kind == 'youtube#video':
                    video_id_item = item['id'].get('videoId')
                    if video_id_item:
                        video_ids.append(video_id_item)
            
            # Verificar se há próxima página
            page_token = search_response.get('nextPageToken')
            if not page_token:
                break  # Não há mais resultados
            
            max_pages -= 1
        
        # Se não houver vídeos encontrados, retorna uma lista vazia e a estatística das buscas
        if not video_ids:
            return {
                'items': [],
                'stats': {
                    'videos': total_videos,
                    'channels': total_channels,
                    'playlists': total_playlists,
                    'pages_processed': pages_processed
                }
            }
        
        # Buscar estatísticas detalhadas dos vídeos encontrados
        stats_response = youtube.videos().list(
            id=','.join(video_ids),
            part='statistics,snippet,contentDetails,status'
        ).execute()

        # Se houver vídeos encontrados, retorna a lista de vídeos e as estatísticas das buscas
        return {
            'items': stats_response.get('items', []),
            'stats': {
                'videos': total_videos,
                'channels': total_channels,
                'playlists': total_playlists,
                'pages_processed': pages_processed
            }
        }
    
    except Exception as e:
        import traceback
        error_details = str(e)
        if "quota" in error_details.lower():
            st.error(f"⚠️ Erro: Quota da API do YouTube excedida. Tente novamente mais tarde.")
        elif "invalid argument" in error_details.lower():
            st.error(f"⚠️ Erro: Verifique se o código do canal ou termo de busca está correto.")
        else:
            st.error(f"Erro ao buscar dados da API: {error_details}")
        
        # Para debug (comentar em produção)
        # st.error(f"Detalhes técnicos: {traceback.format_exc()}")
        return {
            'items': [],
            'stats': {
                'videos': 0,
                'channels': 0,
                'playlists': 0,
                'pages_processed': 0
            }
        }

