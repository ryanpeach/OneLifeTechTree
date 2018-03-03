import networkx as nx
from pathlib import Path

# Objects
# First, let's import object files
files = list(Path("./objects/").glob("*.txt"))
fdict = {}  # This is where they will go
for f in files:
    try:
        i = int(f.stem)  # Get the file name minus .txt
        fdict[i] = f     # Make that the key associated with the file PosixPath
    except:
        continue  # Skip if there's a problem

# Make a dictionary of name, id, and file
for i, f in fdict.items():  # Loop over files
    with f.open() as o:     # Open them
        out_dict = {"id": int(o.readline().split("=")[1].replace("\n","")),
                    "name": o.readline().replace("\n","")}  # Get the first two lines, the id and name
        _id = out_dict["id"]  # The id will be our key
        del out_dict["id"]    # So we delete it after extracting it
        out_dict["file"] = fdict[_id]  # Put the file itself in the "file" key
        fdict[_id] = out_dict  # And now use that whole dictionary as our data for the object id

# Transitions
# Now, we will do a similar thing for transitions
tfiles = list(Path("./transitions/").glob("*.txt"))
tdict = {}  # Our output
for f in tfiles:  # Loop over files
    i = f.stem    # Get the file name minus .txt
    a, b, *args = i.split("_")  # The file name has information called a and b in the title as to what interacts with what, it also occasionally has extra info
    tdict[i] = {"a":int(a), "b":int(b), "args":args, "file":f}  # Now we save that to the dictionary
    with f.open() as o:   # Open the file
        l = o.readline()  # These files are only one line
        tout = []         # Create a list of numbers as our main data
        for t in l.split(" "):  # Split by space
            # Type matters as well as position, so we try int and see if it throws an error, then we try float
            try:
                tout.append(int(t))
            except:
                tout.append(float(t))
        tdict[i]["numbers"] = tout  # Now we add that info to the dict

# Master Graph
# Initialize
G = nx.DiGraph()

# Add all nodes
# Ignore zero and -1
for k, v in fdict.items():
    if int(k) > 0:
        G.add_node(int(k), label=str(v["name"]))  # Give these a label as their name

# Add Edges based on A, B, and D
# A + B = D (simplistic, may not be correct)
for k, v in tdict.items():
    if v["a"] > 0 and v["numbers"][1] > 0:
        G.add_edge(v["a"], v["numbers"][1])
    if v["b"] > 0 and v["numbers"][1] > 0:
        G.add_edge(v["b"], v["numbers"][1])

# Web Interface
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly.graph_objs import *

# Generates a figure based on a graph
def gen_fig(G):
    # Calculate a position for all the nodes in G
    pos = nx.kamada_kawai_layout(G)

    # Create Edge Lines
    # By first creating a plotly scatter plot
    edge_trace = Scatter(
                         x=[],
                         y=[],
                         line=Line(width=0.5,color='#888'),
                         hoverinfo='none',
                         mode='lines')

    # And adding all the edge positions to it
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]

    # Create Nodes
    # By first creating a plotly scatter plot
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

    # And adding all the node positions to it
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        
        # Also adding text for these nodes
        node_trace['text'].append(G.nodes[node]["label"].replace("\n","") if "label" in G.nodes[node] else str(node))

    # Create the plotly figure combining on edge_trace and node_trace
    fig = Figure(data=Data([edge_trace, node_trace]),
                 layout=Layout(
                 title='<br>One Hour One Life Tech Tree',
                 titlefont=dict(size=16),
                 showlegend=False,
                 hovermode='closest',
                 margin=dict(b=20,l=5,r=5,t=40),
                 annotations=[ dict(
                                    text="Code Availible @ <a href='https://github.com/ryanpeach/OneLifeTechTree'>https://github.com/ryanpeach/OneLifeTechTree</a>",
                                    showarrow=False,
                                    xref="paper", yref="paper",
                                    x=0.005, y=-0.002 ) ],
                 xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                 yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))
    
    # Return the figure
    return fig

# Initialize a Dash app
app = dash.Dash()

# Give it a Title, a selection Dropdown, and a Graph
app.layout = html.Div([
    html.H1('One Hour One Life Tech Tree'),
    dcc.Dropdown(
        id='node-selection',
        options=[
            {'label': 'all', 'value': 'All'}
            ] + [{'label': v.lower(), 'value': v} for v in
                [str(k)+": "+n["label"].replace("\n","") if "label" in n else str(k) for k, n in sorted(G.nodes.items())]],
        value='All'
        ),
    dcc.Graph(
        id='tech-graph',
        figure = gen_fig(G)  # The default graph uses the entire tree
    )
])

# The selection dropdown will update the graph by showing only the ancestors of the given node
@app.callback(
              Output(component_id='tech-graph', component_property='figure'),
              [Input(component_id='node-selection', component_property='value')]
              )
def update_plot(node_selection):
    # The default selection is all the data
    if node_selection.lower() == "all":
        G0 = G
        
    # For all other selections
    else:
        n = int(node_selection.split(":")[0])  # The node id is passed via the first element of the string
        s = nx.ancestors(G,n)                  # We get the set of ancestor node id's
        s.add(n)                               # We add the current node id
        G0 = G.subgraph(s)                     # We get the subgraph of these nodes
        
    # Get the new figure with gen_fig and return it to Dash Graph
    return gen_fig(G0)

# Server Execution
if __name__ == '__main__':
    app.run_server(debug=True)
