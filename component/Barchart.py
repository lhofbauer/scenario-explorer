#from dash import Dash, html, dcc, callback, Output, Input
#import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
import json
#Check Color Scheme https://plotly.com/python/discrete-color/



def LongFormBarchart(id, path, title, x, y, category,
                     x_label = None, y_label = None, 
                     scenario = None, sex = None):
    raw_df = pd.read_csv(path)
    df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
    # legend_items = df[category].to_list()
    # if 'Others' in legend_items:
    #     legend_items.sort(key = 'Others'.__eq__)
    fig = px.bar(df, x = x, y = y, 
                 # category_orders = {category: legend_items}, 
                 color = category)
    fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', title = title)
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                      legend_title_text = sex, legend_tracegroupgap = 5)
    fig.update_xaxes(title_text = x_label)
    fig.update_yaxes(title_text = y_label)
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,)
                  # style = {'width': '155vh',
                  #          'height':'80vh'})
    )


def ScenCompInvBarchart(id, df_inv, naming, title=None,
                     x_label = None, y_label = None, z_label=None,
                     scenarios = None):
    
    gobj = list()
    titles = ["Networks","District heating",
              "Hydrogen production","Building technologies"]
    
    for df in df_inv:
        df = df.groupby("RUN",as_index=False).sum()
        df = df[df['RUN'].isin(scenarios)]
        df = df.replace(naming)
        
        fig = px.bar(df,x="RUN",y="VALUE")#color="TECHNOLOGY"
        gobj.append(fig)
            
    cols = 2
    rows = 2
    specs = [[{'type': 'bar'} for c in range(cols)] for r in range(rows)]
    fig = make_subplots(rows=rows, cols=cols,specs=specs,
                        subplot_titles=tuple(titles),
                        shared_xaxes=True,
                        #horizontal_spacing = 0,vertical_spacing = 0)
                        #column_titles=techs , row_titles=scens )
                        )
    i=0
    for r in range(rows):
        for c in range(cols):
            for t in gobj[i].select_traces():
                t["legendgroup"] = titles[i]
                t["legendgrouptitle_text"] = titles[i]
                #t['xaxis'] = {'showticklabels':False}
                fig.add_trace(t,row=r+1, col=c+1)
            i = i+1
    
    fig.update_yaxes(title_text="Investments (billion GBP)",col=1,row=2)
    fig.update_xaxes(tickangle=45, row=2)

    fig.update_layout(showlegend=False,
                     barmode='stack',
                     xaxis_title=None,
                     title=title)
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'displaylogo':False})
    )


def ScenCompCostBarchart(id, df_cost, year, scenarios, naming, title=None,
                     x_label = None, y_label = None, z_label=None):
    
    # due to the allocation of cost over years, it is important what
    # scenario is chosen here (e.g., with regard to gas grid cost increasing
    # cost in early years in scenarios with emission target)
    # using a scenario without emission target might be the best (?)
    by = df_cost.loc[(df_cost["YEAR"]==2015)&
                    (df_cost["RUN"]=="nz-2040_hp-00")]
    by.loc[:,"RUN"] = "Base year"
    df_cost = pd.concat([by,
                        df_cost.loc[(df_cost["YEAR"]==year)]])
    df_cost = df_cost[df_cost['RUN'].isin(scenarios+["Base year"])]
    df_cost = df_cost.drop("YEAR", axis=1)
    
    df_cost = df_cost.replace(naming)
    # cdm = {naming[k] if k in naming.index
    #        else k : v
    #        for k, v in 
    #        cdm.items()
    #        }
    
    fig = px.bar(df_cost,x="RUN",color="TECHNOLOGY",y="VALUE")
                 #color_discrete_map=cdm,)    
    fig.add_vline(
        x=0.5,
        line_dash="dot",
        line_color="black"
        )
    fig.update_layout(legend=dict(orientation="v",
                    title=z_label,
                    #x=1.2,
                    #xref = "container",
                    #yref= "container",
                    traceorder='reversed'),
                       yaxis=dict(
                           title=dict(text=y_label),
                           side="left",
                           #range=[0, 250],
                       ),
                       xaxis_title=x_label,
                       title=title,
                       )
    fig.update_xaxes(tickangle=45)

    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'displaylogo':False})
    )



def ScenCompGenBarchart(id, df_gen, df_cost, year, title, naming,
                        x_label = None, y_label = None, 
                        scenarios = None, colormap = None,
                        ):

    by = df_gen.loc[(df_gen["YEAR"]==2015)&
                    (df_gen["RUN"]=="nz-2040_hp-00")]
    by.loc[:,"RUN"] = "Base year"
    
    df_gen = pd.concat([by,
                        df_gen.loc[(df_gen["YEAR"]==year)]])
    
    df_gen = df_gen[df_gen['RUN'].isin(scenarios+["Base year"])]
    df_gen = df_gen.drop("YEAR", axis=1)
    
    df_gen = df_gen.replace(naming)
    
    # cdm = {naming[k] if k in naming.index
    #        else k : v
    #        for k, v in 
    #        cdm.items()
    #        }
    
    fig = px.bar(df_gen,x="RUN",y="VALUE",color="TECHNOLOGY",
                 color_discrete_map=colormap)
    # fig.update_traces(overwrite=False, legendgroup="tech",
    #                   legendgrouptitle_text="Technology")
    
    fig.add_vline(
        x=0.5,
        line_dash="dot",
        line_color="black"
        )

    
    df_cost = df_cost.drop("TECHNOLOGY",axis=1).groupby(["RUN","YEAR"]).sum()
    # due to the allocation of cost over years, it is important what
    # scenario is chosen here (e.g., with regard to gas grid cost increasing
    # cost in early years in scenarios with emission target)
    # using a scenario without emission target might be the best (?)
    # FIXME: pick appropriate scenario for base year
    df_cost.loc[("Base year",year),:] = df_cost.loc[("nz-2040_hp-00",2015),:]
    df_cost = df_cost[df_cost.index.get_level_values('RUN').isin(scenarios+["Base year"])]
    
    df_cost = df_cost.rename(index=naming)
    # df_cost = df_cost.rename(index=naming)
    # costf = cost.copy()
    # costf.loc[("Base year",year),:] = costf.loc[("No decarbonization",2015),:]
    # costf = costf.xs(year,level="YEAR")
    
    # costa = cost.copy()
    # costa = costa.groupby("RUN").mean() 
    
    fig.add_trace(
               go.Scatter(
                   x=df_cost.xs(year,level="YEAR").index.get_level_values("RUN"),
                   y=df_cost.xs(year,level="YEAR")["VALUE"],
                   yaxis="y2",
                   #legendgroup="cost",
                   #legendgrouptitle=dict(text="System cost"),
                   name="Annual cost (year shown)",
                   mode="markers",
                   marker=dict(size=12,
                               line=dict(width=2,
                               color='DarkSlateGrey'))
               ))
    
    fig.add_trace(
               go.Scatter(
                   x=df_cost.groupby("RUN").mean().index.get_level_values("RUN"),
                   y=df_cost.groupby("RUN").mean()["VALUE"],
                   yaxis="y2",
                   #legendgroup="cost",
                   #legendgrouptitle=dict(text="System cost"),
                   name="Annual cost (average)",
                   mode="markers",
                   marker=dict(size=12,
                               line=dict(width=2,
                               color='DarkRed'))
               ))
    
    
    fig.for_each_trace(
    lambda trace: trace.update(legendgroup="g1",
                       legendgrouptitle=dict(text="Technology")) if trace.yaxis != 'y2' else 
                trace.update(legendgroup="g2",
                             legendgrouptitle=dict(text="System cost")),
                    )

    fig.update_layout(title=title,
                        legend=dict(orientation="v",
                                    title=None,
                                    x=1.2,
                                    y=0.3,
                                    xref = "container",
                                    yref= "container",
                                    traceorder='grouped+reversed',
                                    groupclick="toggleitem"),
                       yaxis=dict(
                           title=dict(text="Heat generation (TJ)"),
                           side="left",
                           #range=[0, 250],
                       ),
                       yaxis2=dict(
                           title=dict(text="Energy system cost (billion GBP)"),
                           side="right",
                           range=[0, 50],
                           overlaying="y",
                           tickmode="sync",
                       ),
                       xaxis_title=None,
                       margin=dict(l=20, r=20, t=10, b=20),
                       )
    fig.update_xaxes(tickangle=45)     

    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'displaylogo':False})
    )

def ScenLocalCompGenBarchart(id, df_gen, lads, year, title, naming,
                        x_label = None, y_label = None, 
                        scenarios = None, colormap = None,
                        ):

    by = df_gen.loc[(df_gen["YEAR"]==2015)&
                    (df_gen["RUN"]=="nz-2040_hp-00")&
                    (df_gen["REGION"].isin(lads))]
    by.loc[:,"RUN"] = "Base year"
    
    df_gen = pd.concat([by,
                        df_gen.loc[(df_gen["YEAR"]==year)]])
    
    df_gen = df_gen[df_gen['RUN'].isin(scenarios+["Base year"])]
    df_gen = df_gen[df_gen['REGION'].isin(lads)]

    df_gen = df_gen.drop("YEAR", axis=1)
    
    df_gen = df_gen.replace(naming)
    
    df_gen["RUN"] = df_gen["RUN"] + "<br>" + df_gen["REGION"]
    
    fig = px.bar(df_gen,x="RUN",y="VALUE",color="TECHNOLOGY",
                 color_discrete_map=colormap)
    # fig.update_traces(overwrite=False, legendgroup="tech",
    #                   legendgrouptitle_text="Technology")

    fig.add_vline(
        x=1*(len(lads)-1)+0.5,
        line_dash="dot",
        line_color="black"
        )

    
    #fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', title = title)
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                      legend_title_text = "Technology", legend_tracegroupgap = 5,
                      margin=dict(l=20, r=20, t=10, b=20))
    fig.update_xaxes(title_text = x_label,
                     tickangle=45)
    fig.update_yaxes(title_text = y_label)

                     
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'displaylogo':False})
    )

    
# FIXME: deprecated, to be deleted
# def WideFormBarchart(id, path, title, xaxis, cat_position, 
#                      x_label = None, y_label = None, 
#                      scenario = None, sex = None):
#     raw_df = pd.read_csv(path)
#     df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
#     categories = df.columns.to_list()[cat_position:]
#     fig = px.bar(df, x = xaxis, y = categories, 
#                  color_discrete_sequence=px.colors.qualitative.Alphabet)
#     fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', title = title)
#     fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
#                       legend_title_text = sex, legend_tracegroupgap = 5)
#     fig.update_xaxes(title_text = x_label)
#     fig.update_yaxes(title_text = y_label)
    
#     return html.Div(
#         dcc.Graph(id = id, 
#                   figure = fig)
#     )