import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import dash_table
from dash.dependencies import Input, Output

#---------------------------------------------------------------------------------------------

# Cargamos los datos
df = pd.read_csv("src/dataset_copd.csv")

#---------------------------------------------------------------------------------------------


# Definimos hoja de estilo externa
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Le asignamos la hoja de estilo a nuestra app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=[{"name":"viewport", 
"content":"width=device-width, initial-scale=0.5, maximun-scale=1, minimum-scale=0.5,"}])
server=app.server

#---------------------------------------------------------------------------------------------
#CONTENIDO DE LA PAGINA

row1=html.Div([
            html.Div([html.Label('Gender:'),
                dcc.Dropdown(id="genero", options=df['gender'].unique(), value='Male')]
                , className='two columns'),


            html.Div([html.Label('Seleccione el rango de edad:'),
            dcc.RangeSlider(id="rango", min=df['AGE'].min(), max=df['AGE'].max(),
                             step=1, value=[45,85])], className='ten columns'),
            
            ], className='row')


tab1=html.Div([dcc.Graph(id='g1')])

tab2=html.Div([dcc.Graph(id='g2')])

tab3=html.Div([
                html.Div([dcc.Graph(id='g3')], className='five columns'),


                html.Div([dash_table.DataTable(
                id = 'tabla',
                columns = [{'name': i, 'id':i} for i in df[['AGE','gender','MWT1',
                                                            'COPDSEVERITY','FEV1','FVC']].columns],
                data = df[['AGE','gender','MWT1','COPDSEVERITY','FEV1','FVC']].to_dict('records'),
                filter_action = 'native',
                sort_action = 'native',
                sort_mode='multi',
                page_size=10
                )], className='seven columns'),

                ], className='row')


# Definimos el layout
app.layout = html.Div([html.H1('Análisis de la gravedad de COPD'),
                html.H6('Chronic Obstructive Pulmonary Disease - Enfermedad Pulmonar Obstructiva Cronica'),
                html.Br(),
                       row1,
                              dcc.Tabs([
                            dcc.Tab(label='Calidad de Vida', children=tab1),
                            dcc.Tab(label='FEV1 vs FVC', children=tab2),
                            dcc.Tab(label='Gravedad COPD', children=tab3)
                            ])
       ])


#---------------------------------------------------------------------------------------------

# Definimos el callback
@app.callback([Output(component_id = 'g1', component_property = 'figure'),
               Output(component_id = 'g2', component_property = 'figure'),
               Output(component_id = 'g3', component_property = 'figure'),
               Output(component_id = 'tabla', component_property = 'data')],

              [Input(component_id = 'genero', component_property = 'value'),
               Input(component_id = 'rango', component_property = 'value')]
)

#---------------------------------------------------------------------------------------------

# Función de actualización
def funcion_actualizacion(genero,rango):

    df_filtro=df.copy()
    df_filtro=df_filtro[(df_filtro['AGE']<=rango[1]) &
                        (df_filtro['AGE']>=rango[0]) &
                        (df_filtro['gender']==genero)]
    
    f1=px.box(df_filtro, x="COPDSEVERITY", y="SGRQ", color="COPDSEVERITY", 
              color_discrete_sequence=['darkcyan', 'lightgreen', 'orange', 'red'],
              category_orders={"COPDSEVERITY": ["Mild", "Moderate", "Severe" ,"Very severe"]})
    f1.update_xaxes(showticklabels=False, title=None )
    f1.update_layout(title='Cuestionario SGRQ - A mayor puntuación, menor calidad de vida')
    f1.update_layout(yaxis_range=[0, 80])


    f2=px.scatter(df_filtro, x="FEV1", y="FVC", color="COPDSEVERITY",
                  color_discrete_sequence=['darkcyan', 'lightgreen', 'orange', 'red'],
                  category_orders={"COPDSEVERITY": ["Mild", "Moderate", "Severe" ,"Very severe"]})
    f2.update_layout(title='Relación entre el FEV1 y FVC')


 
    f3 = px.pie(df_filtro, values=df_filtro['COPDSEVERITY'].value_counts().sort_index(ascending=True),
                names=sorted(df_filtro["COPDSEVERITY"].unique()), hole=0.65,
                color_discrete_sequence=['darkcyan', 'lightgreen', 'orange', 'red'],
                category_orders={"COPDSEVERITY": ["Mild", "Moderate", "Severe" ,"Very severe"]}
                )
    f3.update_layout(title='Distribución de la gravedad de COPD')
    f3.update_layout(annotations=[dict(text="COPDSEVERITY", x=0.50, y=0.5, showarrow=False)])


    f4=df_filtro[['AGE','gender','MWT1','COPDSEVERITY','FEV1','FVC']].to_dict('records')

    
    return f1, f2, f3, f4


#---------------------------------------------------------------------------------------------

# Ejecucción de la app
if __name__ == '__main__':
    app.run_server(debug=False)