import networkx as nx
from pathlib import Path
files = list(Path("./objects/").glob("*.txt"))
fdict = {}
for f in files:
    try:
        i = int(f.stem)
        fdict[i] = f
    except:
        continue

def get_kv(o, kwrds=["parent"]):
    with f.open() as o:
        yield "id", int(o.readline().split("=")[1].replace("\n",""))
        yield "name", o.readline().replace("\n","")

# Make a dictionary of name, id, and parent
for i, f in fdict.items():
    out_dict = dict(get_kv(f))
    _id = out_dict["id"]
    del out_dict["id"]
    out_dict["file"] = fdict[_id]
    fdict[_id] = out_dict

# Transitions
tfiles = list(Path("./transitions/").glob("*.txt"))
tdict = {}
for f in tfiles:
    i = f.stem
    a, b, *args = i.split("_")
    tdict[i] = {"a":int(a), "b":int(b), "args":args, "file":f}
    with f.open() as o:
        l = o.readline()
        tout = []
        for t in l.split(" "):
            try:
                tout.append(int(t))
            except:
                tout.append(float(t))
        tdict[i]["numbers"] = tout

G = nx.DiGraph()

for k, v in fdict.items():
    if int(k) != -1:
        G.add_node(int(k), label=str(v["name"])+" \n")

for k, v in tdict.items():
    if v["a"] > 0 and v["numbers"][1] > 0:
        G.add_edge(v["a"], v["numbers"][1])
    if v["b"] > 0 and v["numbers"][1] > 0:
        G.add_edge(v["b"], v["numbers"][1])

# Go through the object dictionary
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly.graph_objs import *

def gen_fig(G):
    pos = nx.kamada_kawai_layout(G)

    edge_trace = Scatter(
                         x=[],
                         y=[],
                         line=Line(width=0.5,color='#888'),
                         hoverinfo='none',
                         mode='lines')

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]

    node_trace = Scatter(
                         x=[],
                         y=[],
                         text=[],
                         mode='markers',
                         hoverinfo='text',
                         marker=Marker(
                         showscale=True,
                         colorscale='YIGnBu',
                         reversescale=True,
                         color=[],
                         size=10,
                         colorbar=dict(
                             thickness=15,
                             title='Node Connections',
                             xanchor='left',
                             titleside='right'
                         ),
                         line=dict(width=2)
                         )
                     )

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['text'].append(G.nodes[node]["label"].replace("\n","") if "label" in G.nodes[node] else str(node))

    fig = Figure(data=Data([edge_trace, node_trace]),
                 layout=Layout(
                 title='<br>Network graph made with Python',
                 titlefont=dict(size=16),
                 showlegend=False,
                 hovermode='closest',
                 margin=dict(b=20,l=5,r=5,t=40),
                 annotations=[ dict(
                                    text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                                    showarrow=False,
                                    xref="paper", yref="paper",
                                    x=0.005, y=-0.002 ) ],
                 xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                 yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
    return fig

app = dash.Dash()
app.layout = html.Div([
    html.H1('Nodes'),
    dcc.Dropdown(
        id='node-selection',
        options=[
            {'label': 'all', 'value': 'All'}
            ] + [{'label': v.lower(), 'value': v} for v in
                [str(k)+": "+n["label"].replace("\n","") if "label" in n else str(k) for k, n in sorted(G.nodes.items())]],
        value='All'
        ),
    dcc.Graph(
        id='example-graph',
        figure = gen_fig(G)
    )
])

@app.callback(
              Output(component_id='example-graph', component_property='figure'),
              [Input(component_id='node-selection', component_property='value')]
              )
def update_plot(node_selection):
    if node_selection == "All":
        G0 = G
    else:
        n = int(node_selection.split(":")[0])
        s = nx.ancestors(G,n)
        s.add(n)
        G0 = G.subgraph(s)
    return gen_fig(G0)

if __name__ == '__main__':
    app.run_server(debug=True)
