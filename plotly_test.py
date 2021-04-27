import plotly
import seaborn as sns
import plotly.graph_objs as gobjs

import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=1)

fig.add_trace(go.Bar(x=[1, 2, 3], y=[1, 3, 2]), row=1, col=1)
fig.show()

inp = input("Do you want to add another graph?")

if inp == 1:
    fig.add_trace(go.Bar(x=[1, 2, 3], y=[4, 5, 6]), row=2, col=1)
    fig.show()

fig.show()