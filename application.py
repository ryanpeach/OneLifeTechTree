from lib import G, gen_fig, get_subgraph, get_distances

# Dash
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

# Initialize a Dash app
app = dash.Dash()

# Give it a Title, a selection Dropdown, and a Graph
margin_size, margin_size_lr = 10, 10
app.layout = html.Div([
    html.H1('One Hour One Life Tech Tree'),
    html.Div([

        dcc.Dropdown(
            id='node-selection',
            options=[
                {'label': 'all', 'value': 'All'}
                ] + [{'label': v.lower(), 'value': v} for v in
                    [str(k)+": "+n["label"].replace("\n","") if "label" in n else str(k) for k, n in sorted(G.nodes.items())]],
            value='All'
        )],
        style={'marginBottom': margin_size, 'marginTop': margin_size}
    ),

    html.Table([
        html.Tr([
                html.Td("Depth: ",
                        style={"padding-right": margin_size_lr}),

                html.Td(
                    dcc.Slider(
                        id="depth-slider",
                        min=0,
                        max=0,
                        disabled=True,
                        marks={},
                        value=0,
                    ),
                    style={'width':'90%'}
                    ),

                html.Td(
                    dcc.Input(
                        id="depth-slider-indicator",
                        value='0',
                        type='text',
                        readonly=True,
                    ),
                    style={"padding-left": margin_size_lr,
                           "width": "10%"}
                    ),
                ])],
        style={'marginBottom': margin_size}
    ),

    dcc.Graph(
        id='tech-graph',
        figure = gen_fig(G)  # The default graph uses the entire tree
    )
])

@app.callback(Output(component_id='depth-slider-indicator', component_property='value'),
              [Input(component_id='depth-slider', component_property='value')])
def update_slider_indicator(new_value):
    return str(new_value)

@app.callback(Output(component_id='depth-slider', component_property='marks'),
              [Input(component_id='depth-slider', component_property='max')])
def update_ticks(new_max, n=5):
    return {int(float(i)/float(n-1)*new_max): str(int(float(i)/float(n-1)*new_max)) for i in range(n)}

@app.callback(Output(component_id='depth-slider', component_property='disabled'),
              [Input(component_id='depth-slider', component_property='max')])
def enable_slider(new_max):
    if new_max > 0:
        return False
    else:
        return True

# The selection dropdown will update the graph by showing only the ancestors of the given node
@app.callback(
              Output(component_id='tech-graph', component_property='figure'),
              [Input(component_id='node-selection', component_property='value'),
               Input(component_id='depth-slider', component_property='value')]
              )
def update_plot(node_selection, depth_slider):
    # The default selection is all the data
    if node_selection.lower() == "all":
        return gen_fig(G)

    # For all other selections
    else:
        G0 = get_subgraph(node_selection)
        n = int(node_selection.split(":")[0])  # The node id is passed via the first element of the string
        return gen_fig(G0, source=n, depth=depth_slider)


@app.callback(Output(component_id='depth-slider', component_property='max'),
              [Input(component_id='node-selection', component_property='value')])
def update_slider(node_selection):
    if node_selection.lower() == "all":
        return 0

    else:
        G0 = get_subgraph(node_selection)
        return max([G0.nodes[n]['d'] for n in G0.nodes() if "d" in G0.nodes[n]])


# Server Execution
if __name__ == '__main__':
    app.run_server(debug=False)
