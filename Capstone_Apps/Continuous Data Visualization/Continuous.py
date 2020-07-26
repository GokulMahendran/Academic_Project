#!/usr/bin/env python
# coding: utf-8

# In[73]:


import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State
from scipy import stats

df=pd.read_csv("train.csv")

df["Date.of.Birth"]=pd.to_datetime(df["Date.of.Birth"],format="%d-%m-%Y")
df["DisbursalDate"]=pd.to_datetime(df["DisbursalDate"],format="%d-%m-%Y")
df["Age_at_time_of_disbursement"]=((df["DisbursalDate"]-df["Date.of.Birth"])/365).dt.days

df["AVERAGE.ACCT.AGE"]=df["AVERAGE.ACCT.AGE"].apply(lambda x:int(x.split()[0].split("y")[0])*12+int(x.split()[1].split("m")[0]))

df["CREDIT.HISTORY.LENGTH"]=df["CREDIT.HISTORY.LENGTH"].apply(lambda x:int(x.split()[0].split("y")[0])*12+int(x.split()[1].split("m")[0]))




def freedman_diaconis(data, returnas="width"):
    data = np.asarray(data, dtype=np.float_)
    IQR  = stats.iqr(data, rng=(25, 75), scale="raw", nan_policy="omit")
    N    = data.size
    bw   = (2 * IQR) / np.power(N, 1/3)

    if returnas=="width":
        result = bw
    else:
        datmin, datmax = data.min(), data.max()
        datrng = datmax - datmin
        result = int((datrng / bw) + 1)
    return(result)

continuous_cols=['disbursed_amount', 'asset_cost', 'ltv','PERFORM_CNS.SCORE','PRI.NO.OF.ACCTS', 'PRI.ACTIVE.ACCTS',
       'PRI.OVERDUE.ACCTS', 'PRI.CURRENT.BALANCE', 'PRI.SANCTIONED.AMOUNT',
       'PRI.DISBURSED.AMOUNT', 'SEC.NO.OF.ACCTS', 'SEC.ACTIVE.ACCTS',
       'SEC.OVERDUE.ACCTS', 'SEC.CURRENT.BALANCE', 'SEC.SANCTIONED.AMOUNT',
       'SEC.DISBURSED.AMOUNT', 'PRIMARY.INSTAL.AMT', 'SEC.INSTAL.AMT',
       'NEW.ACCTS.IN.LAST.SIX.MONTHS', 'DELINQUENT.ACCTS.IN.LAST.SIX.MONTHS',
       'AVERAGE.ACCT.AGE', 'CREDIT.HISTORY.LENGTH', 'NO.OF_INQUIRIES','Age_at_time_of_disbursement']

range_=[]
for i in continuous_cols:
    range_.append(round(freedman_diaconis(df[i])))
bin_df=pd.DataFrame(index=continuous_cols,data=range_,columns=["Bin"])
bin_df["Bin"]=bin_df["Bin"].replace({0:10})

data=go.Histogram(x=df["disbursed_amount"],xbins=dict(size=bin_df.loc["disbursed_amount"][0]))
layout=go.Layout(xaxis=dict(title="Rupees in M"),
                 yaxis=dict(title=""))
fig=go.Figure(data=data,layout=layout)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Continuous", href="https://capstone-continuous-app.herokuapp.com")),
        dbc.NavItem(dbc.NavLink("Categorical", href="https://capstone-categorical-app.herokuapp.com"))
    ],
    brand="Univariate_Analysis",
    color="primary",
    dark=True
)

controls_num = dbc.Card(
    [
        dbc.FormGroup(
            [   
                dbc.Label("Plot-Type"),
                dcc.Dropdown(
                    id="Plot-Type",
                    options=[
                        {"label":i,"value":i} for i in ["Box_Plot","Histogram"]
                    ],
                    value="Histogram"
                ),
                html.P(),
                dbc.Label("X-variable"),
                html.P(),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in continuous_cols
                    ],
                    value="disbursed_amount",
                ),
                html.P(),
                dbc.Label("Target"),
                html.P(),
                dcc.Dropdown(
                    id="target_id",
                    options=[
                        {"label": i, "value": i} for i in ["Yes","No"]
                    ],
                    value="No",
                ),
                html.P(),
                dbc.Button(id="Submit-Button",children="Submit", color="info", className="mr-1",n_clicks=0),
            ]
        )
    ],
    body=True,
)
tab1=dbc.Container(
    [
        html.Div(navbar),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls_num, md=4),
                dbc.Col(dcc.Graph(id="Figures",figure=fig), md=8),
            ],
            align="center",
        ),
    ],
    fluid=True,
)


app.layout=tab1
@app.callback(Output("Figures","figure"),
              [Input("Submit-Button","n_clicks")],
             [State("x-variable","value"),
             State("Plot-Type","value"),
             State("target_id","value")])

def update_fig(clicks,x_variable,plot_type,target):
    if target=="No":
        if plot_type=="Histogram":
            data=go.Histogram(x=df[x_variable],xbins=dict(size=bin_df.loc[x_variable][0]))
            layout=go.Layout(xaxis=dict(title="Rupees in M"),
                     yaxis=dict(title=""))
            fig=go.Figure(data=data,layout=layout)
            return fig
        elif plot_type=="Box_Plot":
            data=go.Box(x=x_variable,y=df[x_variable])
            layout=go.Layout(xaxis=dict(title="Rupees in M"),
                     yaxis=dict(title=""))
            fig=go.Figure(data=data,layout=layout)
            return fig
        else:
            return go.Figure()
    else:
        grp0=df[df["loan_default"]==0]
        grp1=df[df["loan_default"]==1]
        grp0["loan_default"]=grp0["loan_default"].astype(object)
        grp1["loan_default"]=grp1["loan_default"].astype(object)
        if plot_type=="Histogram":
            data0=go.Histogram(x=grp0[x_variable],xbins=dict(size=bin_df.loc[x_variable][0]))
            data1=go.Histogram(x=grp1[x_variable],xbins=dict(size=bin_df.loc[x_variable][0]))
            fig=go.Figure([data0,data1])
            return fig
        elif plot_type=="Box_Plot":
            data0=go.Box(name="grp0",y=grp0[x_variable].values)
            data1=go.Box(name="grp1",y=grp1[x_variable].values)
            fig=go.Figure([data0,data1])
            return fig
        else:
            return go.Figure()
if __name__ == "__main__":
    app.run_server()

