# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[
                                                {'label': 'All Sites', 'value':'All'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            ],
                                            value='All',
                                            placeholder="Select a Launch Site Here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,         # Minimum value of the slider (minimum payload value in the DataFrame)
                                    max=10000,         # Maximum value of the slider (maximum payload value in the DataFrame)
                                    step=1000,               # Step size between each value on the slider
                                    value=[min_payload, max_payload],  # Initial value of the slider (full range)
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All':
        pie_chart_df = spacex_df.groupby(['Launch Site', 'class']).size().reset_index(name='counts')
        total_successful_launches = pie_chart_df[pie_chart_df['class'] == 1]['counts'].sum()

        # Create a pie chart for the total successful launches by site
        pie_chart_fig = px.pie(pie_chart_df, values='counts', names='Launch Site', title='Total Successful Launches by Site')
    else:
        pie_chart_df = spacex_df[spacex_df['Launch Site'] == selected_site].groupby('class').size().reset_index(name='counts')
        pie_chart_fig = px.pie(pie_chart_df, values='counts', names='class', title=f'Success vs. Failed Launches for {selected_site}')
    return pie_chart_fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'All':
        # Scatter plot for all sites
        scatter_chart_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                     (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        scatter_chart_fig = px.scatter(scatter_chart_df, x='Payload Mass (kg)', y='class',
                                       color='Booster Version Category', title='Payload vs. Success Rate for All Sites')
    else:
        # Scatter plot for a specific launch site
        scatter_chart_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                     (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                     (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        scatter_chart_fig = px.scatter(scatter_chart_df, x='Payload Mass (kg)', y='class',
                                       color='Booster Version Category', title=f'Payload vs. Success Rate for {selected_site}')

    return scatter_chart_fig

# Run the app
if __name__ == '__main__':
    app.run_server()
