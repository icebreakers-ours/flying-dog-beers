# Import required libraries
import pandas as pd
import numpy as np
import e3colors
import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# Multi-dropdown options
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Create controls


# Load data
DataFolder="data"

master_id_map = pd.read_csv(DataFolder+"/master_id_map.csv")
const_data=pd.read_pickle(DataFolder+"/const_data.pkl")
table_data=pd.read_pickle(DataFolder+"/dashboard_table_data.pkl")
unit_plot_data=pd.read_pickle(DataFolder+"/dashboard_unit_plot_data.pkl")
df_all_runs=pd.read_pickle(DataFolder+"/dummy.pkl")

# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w'

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-74.200035,
            lat=40.591564

        ),
        zoom=7,
    )
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                
                                html.H2(
                                    'The Potential for Energy Storage to Augment Peaking Units in New York State',
        
                                ),
                                html.H5(
                                        "Click on a facility in map to begin",
                                )
                            ],
                            className="eight columns"
                        ),
                        html.Div(
                            [
                                html.Img(src="https://www.ethree.com/wp-content/themes/ethree/images/E3_logo.svg")
                            ],
                            className="four columns"
                        )
                    ],
                    className="row"
                ),
            ],
            id="header",
        ),
        html.Div(
            [
                html.Div( #left column
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className="five columns"
                ),
                html.Div( #right column
                    [
                        
                        
                        #container for two separate columns in the right columns
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(id='test_text'),
                                        html.Div(id="unit_stats_table"),
                                        html.Div(id="facility_stats_table",style={'display': 'none'})
                                    ],
                                    className="six columns"),
                                
                                html.Div(
                                    [
                                        html.H6("Choose a unit:"),
                                        dcc.Dropdown(id = 'my-dropdown',
                                                     options = [],
                                                     value = 'NYC'),
                                        dcc.Graph(id="unit_graph")
                                    ],
                                    className="six columns"),
                            ],
                            className="row"
                        ),
                    ],
                    className="seven columns"
                ),
            ],
            className="row"
        ),

        html.Div(
            [
                    html.H3("Peaker operations (allow a few seconds to query database)"),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Dropdown(id="congestion-dropdown",
                            options=[
                                    dict(label="10",value=10),
                                    dict(label="100",value=100),
                                    dict(label="1000",value=1000)],placeholder="Choose congestion threshold")
                            ],
                            className="two columns"),
                html.Div(
                    [dcc.Dropdown(id="capacity-dropdown",
                            options=[
                                    dict(label="25%",value=25),
                                    dict(label="50%",value=50),
                                    dict(label="75%",value=75),
                                    dict(label="100%",value=100),
                                    dict(label="125%",value=125),
                                    dict(label="150%",value=150)
                                    ],placeholder="Choose capacity (% of peak load)")
                            ],
                            className="two columns"),
                html.Div(
                    [dcc.Dropdown(id="duration-dropdown",
                            options=[
                                    dict(label="4 hours",value=4),
                                    dict(label="6 hours",value=6),
                                    dict(label="8 hours",value=8)
                                    ],placeholder="Choose duration")
                            ],
                            className="two columns"),
                html.Div(
                    [dcc.Dropdown(id="solar-dropdown",
                            options=[
                                    dict(label="With solar",value=1),
                                    dict(label="No solar",value=0)
                                    ],placeholder="Include solar?")
                            ],
                            className="two columns"),
                html.Div(
                    [dcc.Checklist(id="checklist",
                            options=[
                                    dict(label="Plot LBMP",value="LBMP"),
                                    dict(label="Plot NOx",value="NOx")
                                    ],value=["LBMP","NOx"])
                        ],
                            className="two columns"),
                html.Div(
                    [html.Button("Generate Plot",id="plot-button")]
                   ,
                   className="two columns"),
            ],
            className="row"
        ),
        html.Div(
            [
                html.Div(
                    [
                    dcc.Graph(id="dispatch-graph")
                    ]
                )
            ]
        ),
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    }
)


# Main graph generation
@app.callback(Output('main_graph', 'figure'),
              [Input('main_graph', 'relayoutData')])
def make_main_figure(main_graph_layout):

    traces = []
    for well_type, dfff in master_id_map.groupby("ORISPL_CODE").apply(lambda df: df.iloc[0]).groupby('Zone'):
        trace = dict(
            type='scattermapbox',
            lon=dfff['Longitude'],
            lat=dfff['Latitude'],
            text=dfff['Plant Name'],
            name=dfff['Zone'],
            marker=dict(
                size=10,
                opacity=0.9,
            )
        )
        traces.append(trace)

    if (main_graph_layout is not None):

        try:
            lon = main_graph_layout['mapbox.center']['lon']
            lat = main_graph_layout['mapbox.center']['lat']
            zoom = main_graph_layout['mapbox.zoom']
        except:
            lon = -74.05
            lat = 40.54
            zoom = 7
        layout['mapbox']['center']['lon'] = lon
        layout['mapbox']['center']['lat'] = lat
        layout['mapbox']['zoom'] = zoom
    else:
        lon = -74.05
        lat = 40.54
        zoom = 7
        layout['mapbox']['center']['lon'] = lon
        layout['mapbox']['center']['lat'] = lat
        layout['mapbox']['zoom'] = zoom


    figure = dict(data=traces, layout=layout)
    return figure

# Display facility selected

@app.callback(Output('test_text', 'children'), [Input('main_graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        chosen = "Please select a facility for analysis"
    else:
        chosen = "Facility selected: " + clickData['points'][0]["text"]
    return chosen

@app.callback(Output('my-dropdown', 'options'), [Input('main_graph', 'clickData')])
def display_click_data2(clickData):
    if clickData is None:
        unit_list ={'label':"Please select a unit for analysis:"}
    else:
        unit_list = []
        chosen = clickData['points'][0]["text"]
        df_test = master_id_map.loc[master_id_map['Plant Name'] == chosen]

        for unit in df_test['UNITID'].to_list():
            unit_list.append({'label': unit, 'value':unit})

    return unit_list

#Set default (first) option in dropdown
@app.callback(Output('my-dropdown','value'),[Input('my-dropdown','options')])
def update_dropdown_default(options):
        return options[0]['value']


#Create graph of percent of peaker load covered for current unit
@app.callback(Output('unit_graph','figure'),
              [Input('main_graph', 'clickData'), #facility name
               Input('my-dropdown','value')]) #unit ID
def make_unit_figure(clickData,unit_ID):
    facility_name=clickData['points'][0]["text"]
    df_cur=unit_plot_data.loc[(facility_name,unit_ID)]
    return {
        'data': [go.Scatter(
                x=df_cur.index,
                y=df_cur["With solar"]*100,
                mode="markers",
                marker=dict(size=15,opacity=0.5,color="orange",line=dict(width=0.5,color="white")),
                name="With solar"),
                go.Scatter(
                x=df_cur.index,
                y=df_cur["No solar"]*100,
                mode="markers",
                marker=dict(size=15,opacity=0.5,color="blue",line=dict(width=0.5,color="white")),
                name="No solar")
                ],
        'layout':go.Layout(
                xaxis=dict(title="Battery size (MWh)"),
                yaxis=dict(title="Percent of peaker load covered"),
                title="Peaker load covered as a function of battery size (MWh)",
                font=dict(size=12)
                )
            }

#Create table of peaker stats
@app.callback(Output('unit_stats_table','children'),
              [Input('main_graph', 'clickData'), #facility name
               Input('my-dropdown','value')]) #unit ID
def make_unit_table(clickData,unit_ID):
    facility_name=clickData['points'][0]["text"]
    df_table=table_data.set_index(["Facility name","Unit ID"],drop=False)
    srs_cur=df_table.loc[(facility_name,unit_ID)].iloc[1:-2].drop(labels="Unit ID")
    srs_cur_1=srs_cur[:9]
    srs_cur_2=srs_cur[9:]
    return[
            html.H5(children='Unit Stats'),
            html.Div(
                [
                    html.Div(
                        [
                            html.Table(
                            [html.Tr([
                                    html.Td(srs_cur_1.index[i]),html.Td(srs_cur_1.iloc[i])
                                    ]) for i in range(len(srs_cur_1))
                            ],style={"font-size":"1.1rem"})
                        ],
                        className="six columns"
                    ),
                    html.Div(
                        [
                            html.Table(
                            [html.Tr([
                                    html.Td(srs_cur_2.index[i]),html.Td(srs_cur_2.iloc[i])
                                    ]) for i in range(len(srs_cur_2))
                            ],style={"font-size":"1.1rem"})
                        ],
                        className="six columns"
                    ),
                ],
                className="row"
            )
            
            ]


# Create table of Facility stats
@app.callback(Output('facility_stats_table', 'children'),
              [Input('main_graph', 'clickData')])# facility name
def make_facility_table(clickData):

    facility_name = clickData['points'][0]["text"]
    facility_df_table = table_data.set_index(["Facility name"], drop=False)
    facility_srs_cur = facility_df_table.loc[(facility_name)].iloc[:-2]

    facility_df = facility_srs_cur[['Unit ID', 'Nameplate capacity (MW)', 'Age in 2019', 'Capacity factor',
                   'Smallest battery for full replacement', 'Smallest battery for hybridization']]
    if not(isinstance(facility_df, pd.DataFrame)):
        facility_df = facility_df.to_frame().transpose()

    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in facility_df.columns],
        data=facility_df.to_dict('rows'))
    

#Make dispatch chart
@app.callback(Output("dispatch-graph","figure"), #change to graph and make this the big honking function- make the buttons and such first
              [Input("plot-button","n_clicks")],
              [State('main_graph', 'clickData'), #facility name
               State('my-dropdown','value'), #unit ID
               State("congestion-dropdown","value"),
               State("capacity-dropdown","value"),
               State("duration-dropdown","value"),
               State("solar-dropdown","value"),
               State("checklist","value")])
def make_dispatch_chart(button_clicks,clickData,unit_ID,cong_thresh,capacity,duration,solar_binary,checklist_val):
    
    limit_2025=1.5 #will change later
    if "LBMP" in checklist_val:
        lbmp_bool=True
    else:
        lbmp_bool=False
    if "NOx" in checklist_val:
        nox_bool=True
    else:
        nox_bool=False
    
    facility_name=clickData['points'][0]["text"]
    orispl=pd.unique(master_id_map.ORISPL_CODE[master_id_map["Plant Name"]==facility_name])[0] #get orispl code
    if orispl==2628:
        unit_ID="001"
    elif orispl==56032:
        unit_ID="0001"
    
    #get run data and gen data
    rundata=df_all_runs.loc[(orispl,unit_ID,cong_thresh,capacity,duration,solar_binary)]
    gendata=const_data.loc[(orispl,unit_ID)]
    
    #merge run and gen data
    df=pd.concat([rundata,
                  gendata[["GLOAD_MWh",
                           "NOX_MASS_lbs",
                           "CO2_MASS_tons",
                           "HEAT_INPUT_mmBtu",
                           "lbmp_gen",
                           "lbmp_zonal",
                           "solar_output"]]],axis=1).copy() #so as not to modify the originals
    df["Congestion (binary)"]=((df.lbmp_gen-df.lbmp_zonal)>cong_thresh)*1
    df.solar_output=df.solar_output*solar_binary
    df=df.rename(columns={"charge":"Storage Charge (MW)",
                         "discharge":"Storage Discharge (MW)",
                         "GLOAD_MWh":"Peaker Load (MW)",
                         "NOX_MASS_lbs":"NOx Emissions (lb)",
                         "CO2_MASS_tons":"CO2 Emissions (tons)",
                         "HEAT_INPUT_mmBtu":"Heat Input (MMBtu)",
                         "lbmp_gen":"Generator LBMP ($/MWh)",
                         "lbmp_zonal":"Zonal LBMP ($/MWh)",
                         "solar_output":"Solar Output (MW)"})
    
    #remove arbitrage discharge (charge will still be in there, for now)
    peaker_no_load_bool=df["Peaker Load (MW)"]==0
    df["Storage Discharge (MW)"].loc[peaker_no_load_bool]=0
    
    #postprocess
    df["Remaining Peaker Load (MW)"]=df["Peaker Load (MW)"]-df["Storage Discharge (MW)"]-df["Solar Output (MW)"]
    df["Remaining Peaker Load (MW)"].loc[df["Remaining Peaker Load (MW)"]<0]=0
    df["Storage Charge (MW)"]=df["Storage Charge (MW)"]*-1

    df_plot=df[["Peaker Load (MW)",
                "Storage Charge (MW)",
                "Remaining Peaker Load (MW)",
                "Solar Output (MW)",
                "Storage Discharge (MW)",
                "Generator LBMP ($/MWh)",
                "Zonal LBMP ($/MWh)",
                "Congestion (binary)",
                "NOx Emissions (lb)"]]

    df_plot["nox_rate"]=df_plot["NOx Emissions (lb)"]/df_plot["Peaker Load (MW)"]
    df_plot.nox_rate.loc[df_plot.nox_rate.isnull()]=0
    df_plot.nox_rate.loc[df_plot.nox_rate==np.inf]=0
    
    nox_rate_daily=df_plot["NOx Emissions (lb)"].resample("D").sum()/df_plot["Peaker Load (MW)"].resample("D").sum()
    nox_rate_daily.loc[nox_rate_daily.isnull()]=0
    nox_rate_daily.loc[nox_rate_daily==np.inf]=0
    df_plot["nox_rate_daily"]=nox_rate_daily.resample("H").pad()
    
    #get daily average nox rate after storage
    remaining_load_frac=df_plot["Remaining Peaker Load (MW)"].resample("D").sum()/\
                                                df_plot["Peaker Load (MW)"].resample("D").sum()
    remaining_load_frac.loc[remaining_load_frac.isnull()]=0
    remaining_load_frac.loc[remaining_load_frac==np.inf]=0
    nox_daily_derated=df_plot["NOx Emissions (lb)"].resample("D").sum()*remaining_load_frac
    nox_rate_daily_derated=nox_daily_derated/(df_plot["Remaining Peaker Load (MW)"].resample("D").sum()+
                                             df_plot["Solar Output (MW)"].resample("D").sum()+
                                             df_plot["Storage Discharge (MW)"].resample("D").sum())
    df_plot["nox_rate_daily_derated"]=nox_rate_daily_derated.resample("H").pad()
    
    df_plot["limit_2025"]=limit_2025
                                                
    
    #find hardest day and start chart there
    daily_load=df_plot["Remaining Peaker Load (MW)"].resample("D").sum()
    hardest_day=daily_load.idxmax()
    start_day=hardest_day-pd.Timedelta(days=3)
    end_day=hardest_day+pd.Timedelta(days=3)
    
    xrange=[start_day.strftime("%Y-%m-%d"),end_day.strftime("%Y-%m-%d")]
    
    #get y1 range
    ymax=max(df["Storage Charge (MW)"].min()*-1.2,df["Peaker Load (MW)"].max()*1.2)
    y1range=[ymax*-1,ymax]
    
    #get y2 range
    max_y_lbmp=max(df_plot["Generator LBMP ($/MWh)"].max(),df_plot["Zonal LBMP ($/MWh)"].max())*1.2
    y2range=[max_y_lbmp*-1,max_y_lbmp]
    
    #get y3 range
    max_NOx=df_plot.nox_rate.quantile(q=0.98) #get 98th percentile nox rate, in case there are outliers
    y3range=[max_NOx*-1.25,max_NOx*1.25]
    
    #####get shapes for congestion ######
    
    cong=df_plot["Congestion (binary)"]
    binary=cong.values
    deltas=pd.Series(data=np.concatenate((np.array([0]),binary[1:]-binary[:-1])),index=cong.index) #start of start will be in the hour it actually starts, end of start will be in the hour after it ends
    all_starts=deltas[deltas.isin([1,-1])]
    if (len(all_starts)%2) !=0:
        all_starts=all_starts[:-1]
    all_starts=all_starts.reset_index()
    
    shape_list=[]
    
    if len(all_starts)!=0:
        for i in np.arange(0,len(all_starts),2): #for each congested period beginning
            cong_begin=all_starts.iloc[i].Time
            cong_end=all_starts.iloc[i+1].Time
    
            shape={'type':'rect',
                   'xref':'x',
                   'yref':'paper',
                   'x0':cong_begin,
                   'y0':0,
                   'x1':cong_end,
                   'y1':1,
                   'fillcolor':'#d3d3d3',
                   'opacity':0.3,
                   'line':{'width':0,}
                   }
            shape_list.append(shape)
    
    x=df_plot.index
    traces=[]
    #make traces
    trace0 = dict(
        x=x,
        y=df_plot["Storage Charge (MW)"],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5,
                 color="red"),
        stackgroup="two",
        name="Storage charge (MW)"
    )
    traces.append(trace0)
    
    trace1 = dict(
        x=x,
        y=df_plot["Remaining Peaker Load (MW)"],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5,
                 color="grey"),
        stackgroup="one",
        name="Remaining peaker load (MW)"
    )
    traces.append(trace1)
    
    trace2 = dict(
        x=x,
        y=df_plot["Solar Output (MW)"],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5,
                 color="orange"),
        stackgroup="one",
        name="Solar output (MW)"
    )
    traces.append(trace2)
    
    trace3 = dict(
        x=x,
        y=df_plot["Storage Discharge (MW)"],
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=0.5,
                 color="green"),
        stackgroup="one",
        name="Storage discharge (MW)"
    )
    traces.append(trace3)
    
    trace4 = go.Scatter(
        x=x,
        y=df_plot["Peaker Load (MW)"],
        name="Original Peaker Load (MW)",
        line=dict(color="black",width=0.8))
    traces.append(trace4)
    
    if lbmp_bool:
        trace5 = go.Scatter(
            x=x,
            y=df_plot["Zonal LBMP ($/MWh)"],
            name="Zonal LBMP ($/MWh)",
            yaxis="y2",
            line=dict(color=e3colors.e3_palettes["light"][0]))
        traces.append(trace5)
        
        trace6 = go.Scatter(
            x=x,
            y=df_plot["Generator LBMP ($/MWh)"],
            name="Generator LBMP ($/MWh)",
            yaxis="y2",
            line=dict(color=e3colors.e3_palettes["dark"][0]))
        traces.append(trace6)
    
    if nox_bool:
        trace7 = go.Scatter(
            x=x,
            y=df_plot.limit_2025,
            name="2025 NOx Limit (lb/MWh)",
            line=dict(color="black",dash="dot"),
            opacity=0.5,
            yaxis="y3")
        traces.append(trace7)
        
        #after storage
        trace8 = go.Scatter(
            x=x,
            y=df_plot["nox_rate_daily_derated"],
            name="Daily Avg NOx Rate After Storage/Solar (lb/MWh)",
            yaxis="y3",
            opacity=0.7,
            line=dict(color=e3colors.e3_palettes["deep"][3],dash="dot"))
        traces.append(trace8)
        
        #before storage
        trace9 = go.Scatter(
            x=x,
            y=df_plot["nox_rate_daily"],
            name="Daily Avg NOx Rate (lb/MWh)",
            yaxis="y3",
            opacity=0.7,
            line=dict(color=e3colors.e3_palettes["deep"][2],dash="dot"))
        traces.append(trace9)
        
    data=traces
    
    if lbmp_bool:
        yaxis2_cur=dict(title="LBMP ($/MWh)",
                                   titlefont=dict(color=e3colors.e3_palettes["dark"][0]),
                                   tickfont=dict(color=e3colors.e3_palettes["dark"][0]),
                                   overlaying="y",
                                   side="right",
                                   range=y2range,
                                   showgrid=False)
    else:
        yaxis2_cur=None
        
    if nox_bool:
        yaxis3_cur=dict(title="NOx rate (lb/MWh)",
                                   titlefont=dict(color=e3colors.e3_palettes["deep"][2]),
                                   tickfont=dict(color=e3colors.e3_palettes["deep"][2]),
                                   overlaying="y",
                                   side="right",
                                   showgrid=False,
                                   range=y3range,
                                   position=1)
    else:
        yaxis3_cur=None
    layout = go.Layout(xaxis=dict(range=xrange,domain=[0,0.95]),
                       yaxis=dict(title="Power output (MW)",range=y1range),
                       yaxis2=yaxis2_cur,
                       yaxis3=yaxis3_cur,
                       shapes=shape_list,
                       legend=dict(x=1.15,y=1))
    
    fig=dict(data=data,layout=layout)
    
    return fig

# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
