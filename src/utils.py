"""
Funções auxiliares
"""

import re


def parse_duration_iso8601(duration_str):
    """Converte duração ISO 8601 (PT#H#M#S) para segundos"""
    if not duration_str or duration_str == 'PT0S':
        return 0
    
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)
    
    if not match:
        return 0
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds


def truncate_text(text, max_length=50):
    """
    Trunca texto para exibição
    Será utilizado para exibir o título dos vídeos nos links de visualização e engajamento e nos cards de Insights Automáticos
    """
    return text if len(text) <= max_length else text[:max_length-3] + "..."

