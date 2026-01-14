import plotly.graph_objects as go
import plotly.offline as pyo


# RAGFS
gpt4_ragfs = [81.66, 65.4, 51, 103.33]
gpt4o_ragfs = [85.4, 73.6, 58, 95.73]
gpt4omini_ragfs = [79.6, 67, 49.4, 96.59]
gpt3_ragfs = [82.6, 54.6, 37.4, 72.44]

# RAGNFS
gpt4_ragnfs = [80.6, 66.4, 52.4, 93.18]
gpt4omini_ragnfs = [77.4, 71.4, 57, 90.48]
gpt3_ragnfs = [83.4, 66.2, 47.2, 63.06]


# NRAG
gpt4_nrag = [69.6, 64, 57.6, 91.42]
gpt4o_nrag = [60.4, 65.4, 50.6, 90.90]
gpt4omini_nrag = [67, 68, 60, 88.13]


"""
fig_ragfs = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4_ragfs, theta=categories,  name='GPT4 RAGFS'),
        go.Scatterpolar(r=gpt4o_ragfs, theta=categories,  name='GPT4o RAGFS'),
        go.Scatterpolar(r=gpt4omini_ragfs, theta=categories,  name='GPT4o-mini RAGFS'),
        go.Scatterpolar(r=gpt3_ragfs, theta=categories,  name='GPT3.5-turbo RAGFS')
    ],
    layout=go.Layout(
        title=go.layout.Title(text='RAG w/ Few-Shot'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)

fig_ragnfs = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4_ragnfs, theta=categories,  name='GPT4 RAGNFS'),
        go.Scatterpolar(r=gpt4omini_ragnfs, theta=categories,  name='GPT4o-mini RAGNFS'),
        go.Scatterpolar(r=gpt3_ragnfs, theta=categories,  name='GPT3.5-turbo RAGNFS')
    ],
    layout=go.Layout(
        title=go.layout.Title(text='RAG w/o Few-Shot'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)

fig_nrag = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4_nrag, theta=categories,  name='GPT4'),
        go.Scatterpolar(r=gpt4o_nrag, theta=categories,  name='GPT4o'),
        go.Scatterpolar(r=gpt4omini_nrag, theta=categories,  name='GPT4o-mini'),
    ],
    layout=go.Layout(
        title=go.layout.Title(text='No RAG, No Few-Shot'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)
"""
"""
fig_gpt4 = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4_nrag, theta=categories,
                        name='NRAG', 
                        fill='toself',
                        marker=dict(color='rgb(106, 106, 252)'),
                        fillcolor='rgba(106, 106, 252, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4_ragfs, theta=categories,
                        name='RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(242, 82, 53)'),
                        fillcolor='rgba(242, 82, 53, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4_ragnfs, theta=categories,
                        name='RAGNFS',
                        fill='toself',
                        marker=dict(color='rgb(22, 199, 140)'),
                        fillcolor='rgba(22, 199, 140, 0.1)', 
                        line=dict(width=1.5)),
    ],
    layout=go.Layout(
        title=go.layout.Title(text='GPT-4'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)
fig_gpt4o = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4o_nrag, theta=categories,
                        name='NRAG', 
                        fill='toself',
                        marker=dict(color='rgb(106, 106, 252)'),
                        fillcolor='rgba(106, 106, 252, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4o_ragfs, theta=categories,
                         
                        name='RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(242, 82, 53)'),
                        fillcolor='rgba(242, 82, 53, 0.1)', 
                        line=dict(width=1.5)),
    ],
    layout=go.Layout(
        title=go.layout.Title(text='GPT-4o'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)
fig_gpt4omini = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4omini_nrag, theta=categories,
                        name='NRAG', 
                        fill='toself',
                        marker=dict(color='rgb(106, 106, 252)'),
                        fillcolor='rgba(106, 106, 252, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4omini_ragfs, theta=categories,
                        name='RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(242, 82, 53)'),
                        fillcolor='rgba(242, 82, 53, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4omini_ragnfs, theta=categories,
                        name='RAGNFS',
                        fill='toself',
                        marker=dict(color='rgb(22, 199, 140)'),
                        fillcolor='rgba(22, 199, 140, 0.1)', 
                        line=dict(width=1.5)),
    ],
    layout=go.Layout(
        title=go.layout.Title(text='GPT-4o-Mini'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)
fig_gpt3 = go.Figure(
    data=[
        go.Scatterpolar(r=gpt3_ragfs, theta=categories,
                        name='RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(242, 82, 53)'),
                        fillcolor='rgba(242, 82, 53, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt3_ragnfs, theta=categories,
                        name='RAGNFS',
                        fill='toself',
                        marker=dict(color='rgb(22, 199, 140)'),
                        fillcolor='rgba(22, 199, 140, 0.1)', 
                        line=dict(width=1.5)),
    ],
    layout=go.Layout(
        title=go.layout.Title(text='GPT-3.5-Turbo'),
        polar={'radialaxis': {'visible': True}},
        showlegend=True
    )
)
"""

range_redundancy = 86
range_accuracy = 74
range_completeness = 61
range_readability = 104

ranges = [range_redundancy, range_accuracy, range_completeness, range_readability]

for idx, value in enumerate(ranges):
    gpt3_ragfs[idx] = gpt3_ragfs[idx]/ranges[idx]
    gpt4_ragfs[idx] = gpt4_ragfs[idx]/ranges[idx]
    gpt4o_ragfs[idx] = gpt4o_ragfs[idx]/ranges[idx]
    gpt4omini_ragfs[idx] = gpt4omini_ragfs[idx]/ranges[idx]
    gpt3_ragnfs[idx] = gpt3_ragnfs[idx]/ranges[idx]
    gpt4omini_ragnfs[idx] = gpt4omini_ragnfs[idx]/ranges[idx]
    gpt4_ragnfs[idx] = gpt4_ragnfs[idx]/ranges[idx]
    gpt4_nrag[idx] = gpt4_nrag[idx]/ranges[idx]
    gpt4o_nrag[idx] = gpt4o_nrag[idx]/ranges[idx]
    gpt4omini_nrag[idx] = gpt4omini_nrag[idx]/ranges[idx]

gpt4_ragfs = [*gpt4_ragfs, gpt4_ragfs[0]]
gpt4o_ragfs = [*gpt4o_ragfs, gpt4o_ragfs[0]]
gpt4omini_ragfs = [*gpt4omini_ragfs, gpt4omini_ragfs[0]]
gpt3_ragfs = [*gpt3_ragfs, gpt3_ragfs[0]]

gpt4_ragnfs = [*gpt4_ragnfs, gpt4_ragnfs[0]]
gpt4omini_ragnfs = [*gpt4omini_ragnfs, gpt4omini_ragnfs[0]]
gpt3_ragnfs = [*gpt3_ragnfs, gpt3_ragnfs[0]]

gpt4_nrag = [*gpt4_nrag, gpt4_nrag[0]]
gpt4o_nrag = [*gpt4o_nrag, gpt4o_nrag[0]]
gpt4omini_nrag = [*gpt4omini_nrag, gpt4omini_nrag[0]]

categories = [f'Redundancy ({range_redundancy})', f'Accuracy ({range_accuracy})', f'Completeness ({range_completeness})', f'Readability ({range_readability})']
categories = [*categories, categories[0]]


fig_all = go.Figure(
    data=[
        go.Scatterpolar(r=gpt4_nrag, theta=categories,
                        name='GPT-4_NRAG', 
                        fill='toself',
                        marker=dict(color='rgb(100, 110, 250)', ),
                        fillcolor='rgba(100, 110, 250, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4_ragfs, theta=categories,
                        name='GPT-4_RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(240, 87, 60)', ),
                        fillcolor='rgba(240, 87, 60, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4_ragnfs, theta=categories,
                        name='GPT-4_RAGNFS',
                        fill='toself',
                        marker=dict(color='rgb(0, 204, 150)', ),
                        fillcolor='rgba(0, 204, 150, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4o_nrag, theta=categories,
                        name='GPT-4O_NRAG', 
                        fill='toself',
                        marker=dict(color='rgb(172, 100, 250)', ),
                        fillcolor='rgba(172, 100, 250, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4o_ragfs, theta=categories,
                        name='GPT-4O_RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(255, 161, 89)', ),
                        fillcolor='rgba(255, 161, 89, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4omini_nrag, theta=categories,
                        name='GPT-4O-MINI_NRAG', 
                        fill='toself',
                        marker=dict(color='rgb(24, 210, 242)', ),
                        fillcolor='rgba(24, 210, 242, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4omini_ragfs, theta=categories,
                        name='GPT-4O-MINI_RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(255, 102, 145)', ),
                        fillcolor='rgba(255, 102, 145, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt4omini_ragnfs, theta=categories,
                        name='GPT-4O-MINI_RAGNFS',
                        fill='toself',
                        marker=dict(color='rgb(182, 232, 128)', ),
                        fillcolor='rgba(182, 232, 128, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt3_ragfs, theta=categories,
                        name='GPT-3.5-TURBO_RAGFS',
                        fill='toself',
                        marker=dict(color='rgb(255, 150, 255)', ),
                        fillcolor='rgba(255, 150, 255, 0.1)', 
                        line=dict(width=1.5)),
        go.Scatterpolar(r=gpt3_ragnfs, theta=categories,
                        name='GPT-3.5-TURBO_RAGNFS',
                        fill='toself',
                        marker=dict(color='rgb(255, 203, 82)', ),
                        fillcolor='rgba(255, 203, 82, 0.1)', 
                        line=dict(width=1.5)),
    ],
    layout=go.Layout(
        polar={'radialaxis': {'visible': True}},
        showlegend=True, 
    )
)

fig_all.update_polars(radialaxis=dict(visible=False,range=[0, 1]))

fig_all.update_layout(
    font=dict(
        size=15,
        family='Times New Roman'
    )
)


"""fig_nrag.show()
fig_ragfs.show()
fig_ragnfs.show()"""

'''fig_gpt4.show()
fig_gpt4o.show()
fig_gpt4omini.show()
fig_gpt3.show()'''
fig_all.show()