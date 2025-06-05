import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Simulo tu DataFrame spacex_df y launch_sites_df para ejemplo
spacex_df = pd.read_csv('spacex_launch_dash.csv')  # Usa tu DataFrame real aquí
launch_sites_df = pd.DataFrame({
    'Launch Site': ['CCAFS LC-40', 'CCAFS SLC-40', 'KSC LC-39A', 'VAFB SLC-4E'],
    'Lat': [28.562302, 28.563197, 28.573255, 34.632834],
    'Long': [-80.577356, -80.576820, -80.646895, -120.610745]
})

# Defino min y max payload basados en datos
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

app = dash.Dash(__name__)

site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites_df['Launch Site'].unique()
]

app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard'),

    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    dcc.Graph(id='success-pie-chart'),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={0: '0 Kg', 2500: '2500 Kg', 5000: '5000 Kg', 7500: '7500 Kg', 10000: '10000 Kg'}
    ),

    dcc.Graph(id='success-payload-scatter-chart')
])

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site].copy()
        # Mapear class 0/1 a etiquetas
        filtered_df['class'] = filtered_df['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Total Success vs Failure for {selected_site}'
        )
    return fig

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Payload vs. Launch Outcome for All Sites'
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Payload vs. Launch Outcome for {selected_site}'
        )

    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8051)

