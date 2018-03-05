from lib import G, gen_fig, get_subgraph
import plotly
from tqdm import tqdm
import os, shutil
import bs4

OUTPATH = "./html_out/"

# Delete all files in directory and remake directory
if os.path.exists(OUTPATH):
    shutil.rmtree(OUTPATH)
os.makedirs(OUTPATH)

# Plot the all file and show it
plotly.offline.plot(gen_fig(G), filename=OUTPATH + "all.html")

# Open index template
with open("./index_template.html") as f:
    txt = f.read()
    soup = bs4.BeautifulSoup(txt, "html5lib")

# Plot the rest
options = soup.select("#dropdownSelect")[0]
for n in tqdm(list(sorted(list(G.nodes())))):
    # Get Title
    title = str(n)+": "+G.nodes[n]["label"].replace("\n","") if "label" in G.nodes[n] else str(n)

    # Create Options Tag
    t = soup.new_tag("option", value=n)
    t.append(title)
    options.append(t)

    # Save Figure
    fig = gen_fig(get_subgraph(str(n)), n, title=title)
    plotly.offline.plot(fig, filename=OUTPATH + "{}.html".format(n), auto_open=False)


# Save to index
with open("index.html", "w") as f:
    f.write(str(soup))
