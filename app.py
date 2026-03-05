"""
Aplicação Streamlit
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Importar módulos do projeto
from src.api import get_video_data
from src.data_processing import (
    process_video_data,
    get_stats_by_channel,
    get_stats_by_category,
    get_top_video_by_metric
)
from src.utils import truncate_text
from src.visualizations import (
    create_top_views_chart,
    create_top_engagement_chart,
    create_duration_distribution_chart,
    create_performance_distribution_chart,
    create_scatter_plot,
    create_timeline_chart
)

# Configurações da página
st.set_page_config(
    page_title="youlit",
    page_icon=":material/youtube_activity:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    /* Estilo dos KPIs */
    .stMetric {
        background-color: #FF5C5C;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric label {
        color: white;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white;
    }
    /* Esconder mensagem "Press enter to apply" */
    [data-testid="InputInstructions"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Título da página
st.markdown("<h1><span style='color: #FF0000;'>You</span>Tube analytics dashboard using Stream<span style='color: #FF0000;'>Lit</span></h1>", unsafe_allow_html=True)

# Inicializar session_state (usada para manter os dados entre interações), caso seja a primeira vez que o usuário acessa a página, inicializa com None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'channel_id' not in st.session_state:
    st.session_state.channel_id = None

# Sidebar
with st.sidebar:
    left, middle, right = st.columns(3)
    with middle:
        st.image("./assets/yt_short_icon_red.png", width=80)
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # Tipo de busca
    tipo_busca = st.selectbox(
        "Tipo de busca:",
        ["Termo geral", "Código do canal"],
        help="Escolha buscar por termo geral ou por código específico de um canal.",
        index=0 # Inicializa com o primeiro item (Termo geral)
    )
    
    if tipo_busca == "Termo geral":
        query = st.text_input("Digite o termo de busca", placeholder="Ex: Olivia Rodrigo", icon=":material/search:")
        channel_id = None
    else:
        query = None
        channel_id = st.text_input("Digite o código do canal", placeholder="Ex: UCy3zgWom-5AGypGX_FVTKpg", icon=":material/barcode:")
   
    max_results = st.slider("Número máximo de resultados", 5, 50, 20)
    
    st.markdown("---")
    buscar = st.button("🔎 Buscar Dados", type="primary", width='stretch')

# Área principal
if buscar:
    if not query and not channel_id:
        st.warning("⚠️ Por favor, preencha pelo menos um parâmetro de busca!")
    else:
        with st.spinner(f"🔄 Buscando {max_results} vídeos do YouTube (pode levar alguns segundos)..."):
            # Buscar dados da API
            result = get_video_data(
                query=query,
                channel_id=channel_id,
                max_results=max_results
            )
            
            items = result['items']
            stats = result['stats']
            
            # Processar dados
            df = process_video_data(items)
            
            # Salvar no session_state
            if df.empty:
                st.session_state.df = None
                st.session_state.channel_id = None
                st.error("❌ Nenhum vídeo encontrado com os parâmetros informados.")
                
                # Mostrar estatísticas da busca
                # Se não houver vídeos, items retorna vazio [], df fica vazio, mas stats['channels'] e stats['playlists'] ainda pode retornar valores, caso encontre somente canais ou playlists
                if stats['videos'] > 0 or stats['channels'] > 0 or stats['playlists'] > 0:
                    st.warning(f"""
                    **📊 Resultados encontrados na busca:**
                    - 🎬 Vídeos: {stats['videos']}
                    - 📺 Canais: {stats['channels']}
                    - 📋 Playlists: {stats['playlists']}
                    - 📄 Páginas processadas: {stats['pages_processed']}
                    """)
                
                st.info("""
                **💡 Dicas:**
                - Verifique se os parâmetros de busca estão corretos
                - Tente termos de busca mais genéricos
                - Alguns canais podem não ter vídeos públicos
                - Se estiver usando código do canal, verifique se está correto (formato: UCxxxxxxxxx)
                """)
            else:
                st.session_state.df = df
                st.session_state.channel_id = channel_id
                
                # Mensagem de sucesso com estatísticas detalhadas
                videos_encontrados = len(df)
                msg_parts = [f"{videos_encontrados} vídeo{'s' if videos_encontrados != 1 else ''} encontrado{'s' if videos_encontrados != 1 else ''}"]
                
                # Adiciona à mensagem de quantos vídeos foram encontrados, quantos canais e playlists foram encontrados e ignorados, caso seja o caso
                if stats['channels'] > 0 or stats['playlists'] > 0:
                    outros = []
                    if stats['channels'] > 0:
                        outros.append(f"{stats['channels']} canal{'is' if stats['channels'] != 1 else ''}")
                    if stats['playlists'] > 0:
                        outros.append(f"{stats['playlists']} playlist{'s' if stats['playlists'] != 1 else ''}")
                    msg_parts.append(f" ({' e '.join(outros)} ignorado{'s' if (stats['channels'] + stats['playlists']) > 1 else ''})")
                
                st.toast("".join(msg_parts), icon="✅")
                
                # Informação sobre páginas processadas se relevante
                if videos_encontrados < max_results:
                    st.info(f"""
                    ℹ️ **Informação sobre a busca:**
                    - Solicitado: {max_results} vídeos
                    - Encontrado: {videos_encontrados} vídeos
                    - Páginas processadas: {stats['pages_processed']}
                    
                    A API do YouTube retornou apenas {videos_encontrados} vídeos disponíveis para esta busca.

                    Às vezes, a API do Youtube retorna menos vídeos do que o solicitado por alguma questão de indisponibilidade.
                    
                    Se for o caso, vale a pena **tentar novamente em alguns segundos**. 
                    """)

# Exibir dados se houver no session_state
if st.session_state.df is not None:
    df = st.session_state.df
    
    # KPIs principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total de Visualizações",
            f"{df['visualizacoes'].sum():,.0f}",
            help="Soma de todas as visualizações dos vídeos encontrados."
        )
    
    with col2:
        st.metric(
            "Total de Likes",
            f"{df['likes'].sum():,.0f}",
            help="Soma de todos os likes dos vídeos encontrados."
        )
    
    with col3:
        st.metric(
            "Taxa de Engajamento Média",
            f"{df['taxa_engajamento'].mean():.2f}%",
            help="Média da taxa de engajamento de todos os vídeos encontrados. Taxa de Engajamento = (Likes + Comentários) / Visualizações × 100"
        )
    
    with col4:
        st.metric(
            "Média de Visualizações/Dia",
            f"{df['visualizacoes_por_dia'].mean():,.0f}",
            help="Média de visualizações diárias de todos os vídeos encontrados."
        )
    
    with col5:
        st.metric(
            "Vídeos Analisados",
            len(df),
            help="Número de vídeos analisados."
        )
    
    # Tabs para organizar o conteúdo
    tab1, tab2, tab3 = st.tabs(["📊 Visualizações", "🎯 Análises", "📋 Dados Detalhados"])
    
    with tab1:
        st.markdown("""
            <div style='background-color: #F5F5F5; padding: 15px; margin: 0 -1rem; border-radius: 5px;'>
            <h3 style='color: black; margin: 0; font-weight: 600;'>📉 Performance Geral</h3>
            </div>
        """, unsafe_allow_html=True)
        # Gráficos em 2 colunas
        col1, col2 = st.columns(2)
        
        # Gráfico de top n vídeos por visualizações (default: 10)
        with col1:
            fig_views, top_views_data = create_top_views_chart(df)
            st.plotly_chart(fig_views, width='stretch')
            
            with st.expander("🔗 Links dos vídeos"):
                for idx, row in top_views_data.iterrows():
                    st.markdown(f"• [{truncate_text(row['titulo'], 60)}]({row['url']})")
        
        # Gráfico de top n vídeos por taxa de engajamento (default: 10)
        with col2:
            fig_engagement, top_engagement_data, threshold = create_top_engagement_chart(df)
            st.plotly_chart(fig_engagement, width='stretch')
            
            with st.expander("🔗 Links dos vídeos"):
                for idx, row in top_engagement_data.iterrows():
                    st.markdown(f"• [{truncate_text(row['titulo'], 60)}]({row['url']})")
            
            if int(threshold) > 0:
                st.caption(f"⚠️ Apenas vídeos com ≥ {int(threshold):,} visualizações, sendo este valor a mediana de visualizações dos vídeos analisados. Serve para evitar distorções no gráfico de top vídeos por taxa de engajamento.")
        
        # Segunda linha de gráficos
        col3, col4 = st.columns(2)
        
        # Gráfico de distribuição por duração dos vídeos (curtos, médios, longos)
        with col3:
            fig_duration = create_duration_distribution_chart(df)
            st.plotly_chart(fig_duration, width='stretch')
        
        # Gráfico de distribuição por performance dos vídeos (baixa, média, alta)
        with col4:
            fig_performance = create_performance_distribution_chart(df)
            st.plotly_chart(fig_performance, width='stretch')
        
        st.markdown("""
            <div style='background-color: #F5F5F5; padding: 15px; margin: 0 -1rem; border-radius: 5px;'>
            <h3 style='color: black; margin: 0; font-weight: 600;'>📊 Análise de Correlação</h3>
            </div>
        """, unsafe_allow_html=True)

        # Gráfico de dispersão
        fig_scatter, perf_pcts = create_scatter_plot(df)
        st.plotly_chart(fig_scatter, width='stretch')
        st.caption(f"📊 Distribuição: Alta: {perf_pcts.get('Alta', 0)}% | Média: {perf_pcts.get('Média', 0)}% | Baixa: {perf_pcts.get('Baixa', 0)}%")
        
        # Timeline de publicações dos vídeos encontrados
        if len(df) > 1:
            st.markdown("""
                <div style='background-color: #F5F5F5; padding: 15px; margin: 0 -1rem; border-radius: 5px;'>
                <h3 style='color: black; margin: 0; font-weight: 600;'>📅 Timeline de Publicações</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Filtro de vídeo para a timeline (seleção única)
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_filter, col_space = st.columns([3, 1])
            with col_filter:
                # Criar lista de opções com título truncado
                video_options = [truncate_text(titulo, 80) for titulo in df['titulo'].tolist()]
                video_mapping = dict(zip(video_options, df['titulo'].tolist()))
                
                selected_video_display = st.selectbox(
                    "🎬 Selecione um vídeo para visualizar na timeline:",
                    options=video_options,
                    index=0,
                    help="Escolha um vídeo para visualizar na timeline de publicações.",
                    key="timeline_video_selector"
                )
                
                # Converter título truncado de volta para título completo
                selected_video = video_mapping[selected_video_display]
            
            fig_timeline = create_timeline_chart(df, [selected_video])
            if fig_timeline:
                st.plotly_chart(fig_timeline, width='stretch')
                st.caption(f"⚠️ A timeline mostra a publicação dos vídeos encontrados ao longo do tempo, sendo os vídeos encontrados os de maior número de visualizações, e não todos os vídeos publicados referentes ao termo ou o canal.")
            else:
                st.warning("⚠️ Não foi possível gerar o gráfico.")
        
        st.markdown("---")
            
        # Informações sobre as métricas
        with st.expander("ℹ️ Entenda as Métricas"):
            st.markdown("""
            ### 📊 Taxa de Engajamento
            
            **Fórmula:** `(Likes + Comentários) / Visualizações × 100`
            
            Indica o percentual de pessoas que **interagiram** com o vídeo em relação ao total de visualizações.
            
            **Exemplo:** Um vídeo com 1.000 visualizações, 50 likes e 10 comentários tem:
            - Taxa de Engajamento = (50 + 10) / 1.000 × 100 = **6%**
            
            **⚠️ Importante sobre o visual Top 10 Vídeos por Taxa de Engajamento:**
            
            Para evitar distorções, o gráfico considera apenas vídeos com um número **mínimo de visualizações**.
            
            ---
            
            ### 🎯 Classificação de Performance
            
            - 🔵 **Alta Performance**: Taxa de Engajamento > 5%
            - 🟢 **Média Performance**: Taxa de Engajamento entre 2% e 5%
            - 🟠 **Baixa Performance**: Taxa de Engajamento < 2%
            
            ---
            
            ### 📊 Gráfico de Correlação (Bolhas)
            
            - **Tamanho da Bolha** = Número de Visualizações
            - Permite identificar padrões entre duração e engajamento
            """)

    with tab2:
        st.markdown("""
            <div style='background-color: #F5F5F5; padding: 15px; margin: 0 -1rem; border-radius: 5px;'>
            <h3 style='color: black; margin: 0; font-weight: 600;'>🎯 Análises Estatísticas</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Insights automáticos
        st.markdown("### 💡 Insights Automáticos")
        
        col1, col2, col3 = st.columns(3)
        
        # Card de vídeo mais visto
        with col1:
            video_mais_visto = get_top_video_by_metric(df, 'visualizacoes')
            st.info(f"""
            **🏆 Vídeo Mais Visto**
            
            [{truncate_text(video_mais_visto['titulo'], 50)}]({video_mais_visto['url']})
            
            📊 {video_mais_visto['visualizacoes']:,.0f} visualizações
            """)
        
        # Card de vídeo com maior engajamento
        with col2:
            # Aplicar o mesmo filtro de mediana usado no gráfico de top engajamento
            threshold_engajamento = df['visualizacoes'].median()
            df_filtered_engajamento = df[df['visualizacoes'] >= threshold_engajamento].copy()
            
            # Se não houver vídeos suficientes após o filtro, usar todos
            if len(df_filtered_engajamento) == 0:
                df_filtered_engajamento = df.copy()
            
            video_mais_engajamento = get_top_video_by_metric(df_filtered_engajamento, 'taxa_engajamento')
            st.success(f"""
            **⭐Vídeo com Maior Engajamento**
            
            [{truncate_text(video_mais_engajamento['titulo'], 50)}]({video_mais_engajamento['url']})
            
            💚 {video_mais_engajamento['taxa_engajamento']:.2f}% de engajamento
            """)
        
        # Card de vídeo mais recente trazido
        with col3:
            video_mais_recente = get_top_video_by_metric(df, 'data_publicacao', 'DESC')
            st.warning(f"""
            **🆕 Vídeo Mais Recente Trazido**
            
            [{truncate_text(video_mais_recente['titulo'], 50)}]({video_mais_recente['url']})
            
            📅 {pd.to_datetime(video_mais_recente['data_publicacao']).strftime('%d/%m/%Y')}
            """)

        # Se for busca por canal, não mostrar estatísticas por canal (pois será apenas um canal)
        if st.session_state.channel_id:
            # Apenas estatísticas por categoria
            st.markdown("### 📈 Estatísticas por Categoria")
            # Tabela de estatísticas por categoria
            stats_categoria = get_stats_by_category(df)
            st.dataframe(stats_categoria, width='stretch')
        else:
            # Mostrar ambas as estatísticas (categoria primeiro)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Estatísticas por Categoria")
                # Tabela de estatísticas por categoria
                stats_categoria = get_stats_by_category(df)
                st.dataframe(stats_categoria, width='stretch')
            
            with col2:
                st.markdown("### 📊 Estatísticas por Canal")
                # Tabela de estatísticas por canal
                stats_canal = get_stats_by_channel(df)
                st.dataframe(stats_canal, width='stretch')

    with tab3:
        st.markdown("""
            <div style='background-color: #F5F5F5; padding: 15px; margin: 0 -1rem; border-radius: 5px;'>
            <h3 style='color: black; margin: 0; font-weight: 600;'>📋 Tabela de Dados Completa</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Preparar dados para exibição
        df_display = df[[
            'titulo', 'canal', 'visualizacoes', 'likes', 'comentarios',
            'taxa_engajamento', 'visualizacoes_por_dia', 'duracao_minutos',
            'categoria_duracao', 'status_performance', 'categoria', 'data_publicacao'
        ]].copy()
        
        df_display.columns = [
            'Título', 'Canal', 'Visualizações', 'Likes', 'Comentários',
            'Taxa Engajamento (%)', 'Views/Dia', 'Duração (min)',
            'Cat. Duração', 'Performance', 'Categoria', 'Data Publicação'
        ]
        
        # Tabela de dados completos
        st.dataframe(df_display, width='stretch', height=600)
        
        # Opção de download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f'youtube_analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
        )

elif st.session_state.df is None:
    # Tela inicial
    st.markdown("""
    👋 **Bem-vindo ao YouLit: YouTube analytics dashboard using StreamLit!** 
    </br>Ou ainda, traduzindo: Painel de análises do YouTube utilizando o StreamLit!
    
    Este dashboard, criado a partir do framework Python, StreamLit, permite analisar métricas de vídeos do YouTube de forma visual e interativa.
    
    **Como usar:**
    1. Escolha o tipo de busca: **Termo geral** ou **Código do canal**
    2. Digite o parâmetro de busca:
       - **Termo geral**: Como se estivesse pesquisando no YouTube (Ex: "Olivia Rodrigo")
       <br>**📎 Por que usar Termo geral?**
    <br>Se você desejar analisar tudo sobre um termo específico, procurando entender, por exemplo, quais são os vídeos mais populares dadas determinadas palavras-chave de busca.
       - **Código do canal**: ID único do canal (Ex: "UCy3zgWom-5AGypGX_FVTKpg")
       <br>**📎 Por que usar Código do canal?**
    <br>Se você desejar analisar um canal específico, procurando entender, por exemplo, quais são os vídeos mais populares do canal.
    3. Escolha o número máximo de resultados desejado, de 5 a 50
    4. Clique em "Buscar Dados"
    5. Explore as visualizações e análises!
    
    **📺 Como encontrar o código do canal?**
    1. Acesse a página do canal no YouTube
    2. Clique em **...mais** para expandir a Descrição do canal
    3. Role para baixo até encontrar o link de **Compartilhar canal**
    4. Ao clicar no link, você terá duas opções:
        - **Compartilhar canal**
        - **Copiar ID do canal**
    5. Selecione **Copiar ID do canal**
    
    **Recursos disponíveis:**
    - 📊 Visualizações interativas
    - 📋 Tabelas detalhadas com todas as métricas
    - 🎯 Análises estatísticas e insights automáticos
    - 📥 Download dos dados em CSV
    """, unsafe_allow_html=True)
    
    # Quadro destacado com informações sobre limitações e ordenação
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FFE5E5 0%, #FFF0F0 100%); 
                padding: 25px; 
                border-radius: 10px; 
                border-left: 5px solid #FF0000;
                box-shadow: 0 2px 8px rgba(255, 0, 0, 0.1);
                margin-top: 20px;'>
        <h3 style='color: #CC0000; margin-top: 0; margin-bottom: 15px;'>⚠️ Sobre as limitações da API do YouTube</h3>
        <ul style='color: #333; line-height: 1.8; margin-bottom: 20px;'>
            <li>Cada busca consome <strong>100 unidades de quota</strong> da API</li>
            <li>A quota padrão diária é de <strong>10.000 unidades</strong> (aproximadamente 100 buscas por dia)</li>
            <li>O máximo de resultados por consulta é de <strong>50 vídeos</strong></li>
            <li>Este dashboard está configurado para buscar até <strong>5 páginas de resultados</strong> (pois os resultados trazem também canais e playlists, como estamos interessados apenas em vídeos, precisamos estender a busca até que a quantidade de vídeos encontrados seja igual ao número máximo de resultados desejado, caso seja possível)</li>
            <li>É possível solicitar aumento de quota diretamente ao Google, caso necessário</li>
        </ul>
        <h3 style='color: #CC0000; margin-bottom: 10px;'>📊 Ordenação dos resultados</h3>
        <p style='color: #333; line-height: 1.8; margin: 0;'>
            Os vídeos são retornados ordenados por <strong>maior número de visualizações</strong> relacionadas ao termo pesquisado.
        </p>
    </div>
    """, unsafe_allow_html=True)
