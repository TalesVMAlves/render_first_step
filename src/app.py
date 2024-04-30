import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go

# Inicializar o aplicativo Dash
app = Dash(__name__)
server = app.server

df = pd.read_csv('datasets_finais\acordo_nbr.csv')

apresentacao_utilizada = df['APRESENTACAO_NOME'].unique()
especie_madeira = df['MADEIRA_NOME'].unique()

# Layout do aplicativo
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-especie',
        options=[{'label': especie, 'value': idx} for idx, especie in enumerate(especie_madeira)],
        value=None,  # Definir o valor inicial como None
        style={'width': '50%'},
        placeholder="Selecione a espécie",
    ),
    html.Div(
        dcc.Graph(id='bar-chart'),
        id='bar-container',
        style={'display': 'none'}),
    html.Div(
        dcc.Graph(id='pie-chart'),
        id='pie-container',
        style={'display': 'none'})  # Container vazio para o gráfico de pizza
])

# Callback para atualizar a visibilidade do gráfico com base nas seleções do usuário
@app.callback(
    Output('bar-container', 'style'),
    [Input('dropdown-especie', 'value')]
)
def update_bar_visibility(especie_index):
    if especie_index is None:
        # Se o dropdown for None, oculta o contêiner do gráfico
        return {'display': 'none'}
    else:
        # Caso contrário, exibe o contêiner do gráfico
        return {'display': 'block'}

# Callback para atualizar o gráfico de barras com base na espécie de madeira selecionada
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('dropdown-especie', 'value')]
)
def update_bar_chart(especie_index):
    if especie_index is None:
        # Retorna um gráfico vazio se nenhuma espécie for selecionada
        return go.Figure()

    especie_nome = especie_madeira[especie_index]

    quantidade_calculada = df[df['MADEIRA_NOME'] == especie_nome].groupby('APRESENTACAO_NOME')['VOLUME'].sum()

    # Ordenar quantidade_calculada de acordo com as apresentações de madeira
    quantidade_calculada = quantidade_calculada.reindex(df['APRESENTACAO_NOME'].unique())

    # Criar o gráfico de barras
    fig = go.Figure(data=[go.Bar(x=quantidade_calculada.index, 
                                  y=quantidade_calculada.values,
                                  marker=dict(color='#66B2FF'))])

    # Personalizar o layout do gráfico de barras
    fig.update_layout(title=f'Soma do Volume por Apresentação de Madeira ({especie_nome})',
                      xaxis_title='Apresentação de Madeira',
                      yaxis_title='Soma do Volume')

    return fig

# Callback para atualizar a visibilidade do gráfico de pizza com base no clique nas barras
@app.callback(
    Output('pie-container', 'style'),
    [Input('bar-chart', 'clickData')]
)
def update_pie_visibility(click_data):
    if click_data is None:
        # Se não houver clique nas barras, oculta o contêiner do gráfico de pizza
        return {'display': 'none'}
    else:
        # Caso contrário, exibe o contêiner do gráfico de pizza
        return {'display': 'block'}

# Callback para limpar o clique nas barras quando o dropdown é alterado
@app.callback(
    Output('bar-chart', 'clickData'),
    [Input('dropdown-especie', 'value')]
)
def clear_bar_click_data(especie_index):
    # Retorna None para limpar o clique nas barras ao alterar o dropdown
    return None


# Callback para criar o gráfico de pizza com base no clique nas barras do gráfico de barras
@app.callback(
    Output('pie-chart', 'figure'),  # Alterado para 'figure'
    [Input('bar-chart', 'clickData'),
     Input('dropdown-especie', 'value')]
)
def update_pie_chart(clickData, especie_index):
    if clickData is None or especie_index is None:
        # Retorna um gráfico vazio se nenhum ponto for clicado ou nenhuma espécie for selecionada
        return {}

    apresentacao_selecionada = clickData['points'][0]['x']
    especie_nome = especie_madeira[especie_index]

    # Filtrar o DataFrame para obter os dados relevantes
    dados_selecionados = df[(df['APRESENTACAO_NOME'] == apresentacao_selecionada) & (df['MADEIRA_NOME'] == especie_nome)]

    # Contar as categorias de df_final['COD_MODELO']
    contagem_categorias = dados_selecionados['COD_MODELO'].value_counts()

    # Criar o gráfico de pizza
        # Criar o gráfico de pizza com cores constantes
    fig_pie = go.Figure(data=[go.Pie(labels=['Prestação de Serviços', 'Varejo'], 
                                     values=contagem_categorias.values,
                                     marker=dict(colors=['#FF9999', '#99FF99']))])
    fig_pie.update_layout(title=f'Tipo de venda para - {apresentacao_selecionada} ({especie_nome})')

    return fig_pie


# Executar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
