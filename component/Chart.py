import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
import json
# Check Color Scheme https://plotly.com/python/discrete-color/

class Chart:
    @staticmethod
    def LongFormBarchart(id, path, title, x, y, category,
                        x_label = None, y_label = None, 
                        scenario = None, sex = None):
        raw_df = pd.read_csv(path)
        df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
        fig = px.bar(df, x = x, y = y,  
                    color = category)
        fig.layout = dict(xaxis = dict(type = "category"), 
                          barmode = 'stack', title = title)
        fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                        legend_title_text = sex, legend_tracegroupgap = 5,
                        margin=dict(l=20, r=20, t=10, b=20))
        fig.update_xaxes(title_text = x_label)
        fig.update_yaxes(title_text = y_label)
        
        return html.Div(
            dcc.Graph(id = id, 
                    figure = fig,)
        )

    @staticmethod
    def ScenCompInvBarchart(id, df_inv, naming, title = None,
                        x_label = None, y_label = None, z_label = None,
                        scenarios = None, lads = None):
        
        gobj = list()
        titles = ["Power and gas networks","District heating systems",
                "Hydrogen production","Building heat and retrofit"]
        ymax = 0
        for df in df_inv:
            
            df = df[df['RUN'].isin(scenarios)]
            df = df.replace(naming)
            if lads:
                df = df[df['REGION'].isin(lads)]
                df["RUN"] = df["RUN"] + "<br>" + df["REGION"]
                
            df = df.groupby("RUN",as_index=False).sum() 
            
            fig = px.bar(df,x="RUN",y="VALUE")
            gobj.append(fig)
            ymax = max(ymax,df["VALUE"].max())
        
        if lads:
            order = [2,1,0,3]
            gobj = [gobj[i] for i in order]
            titles = [titles[i] for i in order]
            titles[0] = ""
                    
        cols = 2
        rows = 2
        specs = [[{'type': 'bar'} for c in range(cols)] for r in range(rows)]
        fig = make_subplots(rows=rows, cols=cols,specs=specs,
                            subplot_titles=tuple(titles),
                            shared_xaxes=True,
                            horizontal_spacing = 0.1,vertical_spacing = 0.1
                            )
        i=0
        for r in range(rows):
            for c in range(cols):
                for t in gobj[i].select_traces():
                    t["legendgroup"] = titles[i]
                    t["legendgrouptitle_text"] = titles[i]
                    fig.add_trace(t,row=r+1, col=c+1)
                i = i+1
        
        fig.update_yaxes(title_text=y_label,col=1,row=2)
        fig.update_yaxes(range=[0, ymax+1])
        fig.update_xaxes(tickangle=45, row=2)

        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                        showlegend=False,
                        barmode='stack',
                        xaxis_title=None,
                        title=title)
        
        return html.Div(
            dcc.Graph(id = id, 
                    figure = fig,
                    config={'displaylogo':False})
        )

    @staticmethod
    def ScenCompCostBarchart(id, df_cost, year, scenarios, naming, title = None,
                            x_label = None, y_label = None, z_label = None):
        
        # due to the allocation of cost over years, it is important what
        # scenario is chosen here (e.g., with regard to gas grid cost increasing
        # cost in early years in scenarios with emission target)
        # using a scenario without emission target might be the best (?)

        by = df_cost.loc[(df_cost["YEAR"]==2015)&
                         (df_cost["RUN"]=="nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO")]
        by.loc[:,"RUN"] = "Base year"
        df_cost = pd.concat([by,
                            df_cost.loc[(df_cost["YEAR"]==year)]])
        df_cost = df_cost[df_cost['RUN'].isin(scenarios+["Base year"])]
        df_cost = df_cost.drop("YEAR", axis=1)
        
        df_cost = df_cost.replace(naming)       
        fig = px.bar(df_cost,x="RUN",color="TECHNOLOGY",y="VALUE")   
        fig.add_vline(
            x=0.5,
            line_dash="dot",
            line_color="black"
            )
        fig.update_layout(margin=dict(l=20, r=20, t=10, b=20),
                        legend=dict(orientation="v",
                        title=z_label,
                        traceorder='reversed'),
                        yaxis=dict(
                            title=dict(text=y_label),
                            side="left",
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


    @staticmethod
    def ScenCompGenBarchart(id, df_gen, df_cost, year, title, naming,
                            x_label = None, y_label = None, 
                            scenarios = None, colormap = None,
                            ):

        by = df_gen.loc[(df_gen["YEAR"]==2015)&
                        (df_gen["RUN"]=="nz-2050_hp-00_dh-00_lp-00_h2-01_UK|LA|SO")]
        by.loc[:,"RUN"] = "Base year"
        
        df_gen = pd.concat([by,
                            df_gen.loc[(df_gen["YEAR"]==year)]])

        df_gen = df_gen[df_gen['RUN'].isin(scenarios+["Base year"])]
        df_gen = df_gen.drop("YEAR", axis=1)
        
        df_gen = df_gen.replace(naming)

        fig = px.bar(df_gen,x="RUN",y="VALUE",color="TECHNOLOGY",
                    color_discrete_map=colormap)
        
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

        df_cost.loc[("Base year",2015),:] = df_cost.loc[("nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO",2015),:]
        df_cost = df_cost[df_cost.index.get_level_values('RUN').isin(scenarios+["Base year"])]
        
        df_cost = df_cost.rename(index=naming)

        
        fig.add_trace(
                    go.Scatter(
                        x=df_cost.xs("Base year",level="RUN",
                                    drop_level=False).index.get_level_values("RUN"),
                        y=df_cost.xs("Base year",level="RUN")["VALUE"],
                        yaxis="y2",
                        name="2015",
                        mode="markers",
                        marker=dict(size=12,
                                    line=dict(width=2,
                                    color='DarkSlateGrey'))
                    ))
        fig.add_trace(
                    go.Scatter(
                        x=df_cost.xs(year,level="YEAR").index.get_level_values("RUN"),
                        y=df_cost.xs(year,level="YEAR")["VALUE"],
                        yaxis="y2",
                        name=str(year),
                        mode="markers",
                        marker=dict(size=12,
                                    line=dict(width=2,
                                    color='DarkSlateGrey'))
                    ))    
        df_cost = df_cost.loc[df_cost.index.get_level_values("RUN")!="Base year"].groupby("RUN").mean()
        fig.add_trace(
                    go.Scatter(
                        x=df_cost.index.get_level_values("RUN"),
                        y=df_cost["VALUE"],
                        yaxis="y2",
                        #legendgroup="cost",
                        #legendgrouptitle=dict(text="System cost"),
                        name="Average",
                        mode="markers",
                        marker=dict(size=12,
                                    line=dict(width=2,
                                    color='DarkRed'))
                    ))
        
        
        fig.for_each_trace(
        lambda trace: trace.update(legendgroup="g1",
                            legendgrouptitle=dict(text="Technology")) if trace.yaxis != 'y2' else 
                    trace.update(legendgroup="g2",
                                legendgrouptitle=dict(text="Annual energy system cost")),
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
                            range=[0, 75],
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

    @staticmethod
    def ScenLocalCompGenBarchart(id, df_gen, lads, year, title, naming,
                            x_label = None, y_label = None, 
                            scenarios = None, colormap = None,
                            ):

        by = df_gen.loc[(df_gen["YEAR"]==2015)&
                        (df_gen["RUN"]=="nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO")&
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
        fig.add_vline(
            x=1*(len(lads)-1)+0.5,
            line_dash="dot",
            line_color="black"
            )
        
        fig.update_layout(margin=dict(l=20, r=20, t=10, b=20),
                        legend_title_text = "Technology")
        fig.update_xaxes(title_text = x_label,
                        tickangle=45)
        fig.update_yaxes(title_text = y_label)

                        
        return html.Div(
            dcc.Graph(id = id, 
                    figure = fig,
                    config={'displaylogo':False})
        )
    
    @staticmethod
    def GenericLinechart(id, df, x, y, category, naming=None, title=None,
                        x_label = None, y_label = None,l_label=None, y_range=None,
                        scenarios = None, lads=None):

        df = df[df['RUN'].isin(scenarios)] if scenarios else df
        df = df[df['REGION'].isin(lads)] if lads else df
        

        df = df.replace(naming)
        
        if lads:
            df["RUN"] = df["RUN"] + "<br>" + df["REGION"]
            
        fig = px.line(df, x = x, y = y,
                    color = category)
        if y_range:
            fig.update_layout(yaxis_range=y_range)
        
        fig.update_layout(
                        #paper_bgcolor = 'white',
                        #plot_bgcolor = 'white',
                        
                        yaxis_title=y_label,
                        xaxis_title=x_label,
                        legend_title_text=l_label,
                        title=title,
                        margin=dict(l=20, r=20, t=10, b=20),
                        )
                    
        return html.Div(
            dcc.Graph(id = id, 
                    figure = fig,
                    config={'displaylogo':False})
        )