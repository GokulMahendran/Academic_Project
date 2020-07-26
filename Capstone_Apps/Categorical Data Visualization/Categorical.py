#!/usr/bin/env python
# coding: utf-8

# In[57]:


import numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output,Input,State

df=pd.read_csv("train.csv")

df["Date.of.Birth"]=pd.to_datetime(df["Date.of.Birth"],format="%d-%m-%Y")
df["DisbursalDate"]=pd.to_datetime(df["DisbursalDate"],format="%d-%m-%Y")
df["Age_at_time_of_disbursement"]=((df["DisbursalDate"]-df["Date.of.Birth"])/365).dt.days
df["AVERAGE.ACCT.AGE"]=df["AVERAGE.ACCT.AGE"].apply(lambda x:int(x.split()[0].split("y")[0])*12+int(x.split()[1].split("m")[0]))
df["CREDIT.HISTORY.LENGTH"]=df["CREDIT.HISTORY.LENGTH"].apply(lambda x:int(x.split()[0].split("y")[0])*12+int(x.split()[1].split("m")[0]))

categorical_cols=['branch_id','supplier_id', 'manufacturer_id', 'Current_pincode_ID','Employment.Type','State_ID',
                  'Employee_code_ID','MobileNo_Avl_Flag', 'Aadhar_flag', 'PAN_flag', 'VoterID_flag',
       'Driving_flag', 'Passport_flag',"PERFORM_CNS.SCORE.DESCRIPTION"]

grp0=df[df["loan_default"]==0]
grp1=df[df["loan_default"]==1]

cat_df=df["State_ID"].value_counts()[:15]
data=go.Bar(x=["State_id"+str(i) for i in cat_df.index],y=cat_df.values)
cat_fig=go.Figure(data)

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

controls_cat = dbc.Card(
    [
        dbc.FormGroup(
            [
                html.P(),
                dbc.Label("X-variable"),
                html.P(),
                dcc.Dropdown(
                    id="x-variable",
                    options=[
                        {"label": col, "value": col} for col in categorical_cols
                    ],
                    value="State_ID",
                ),
                html.P(),
                dcc.Dropdown(
                    id="target_id",
                    options=[
                        {"label": i, "value": i} for i in ["No","Yes"]
                    ],
                    value="No",
                ),
                html.P(),
                dbc.Button(id="Submit-Button",children="Submit", color="info", className="mr-1",n_clicks=0)
            ] )
    ],
    body=True,
)

tab2=dbc.Container(
    [
        html.Div(navbar),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls_cat, md=4),
                dbc.Col(dcc.Graph(id="Figures",figure=cat_fig), md=8),
            ],
            align="center",
        ),
    ],
    fluid=True,
)

app.layout=tab2


@app.callback(Output("Figures","figure"),
              [Input("Submit-Button","n_clicks")],
             [State("x-variable","value"),
             State("target_id","value")])

def update_fig(clicks,x_variable,target):
    if target=="No":
        cat_df=df[x_variable].value_counts()[:15]
        if x_variable!="PERFORM_CNS.SCORE.DESCRIPTION":
            data=go.Bar(x=[x_variable+str(i) for i in cat_df.index],y=cat_df.values)
            fig=go.Figure(data)
            return fig
        else:
            data=go.Bar(x=[i for i in cat_df.index],y=cat_df.values)
            fig=go.Figure(data)
            return fig
    else:
        cat_df_1=grp1[x_variable].value_counts()[:15]
        ind=cat_df_1.index
        cat_df_0=grp0[x_variable].value_counts().loc[ind]
        if x_variable!="PERFORM_CNS.SCORE.DESCRIPTION":
            trace0=go.Bar(x=[x_variable+str(i) for i in cat_df_0.index],y=cat_df_0.values,name="grp0")
            trace1=go.Bar(x=[x_variable+str(i) for i in cat_df_1.index],y=cat_df_1.values,name="grp1")
            cat_fig=go.Figure([trace0,trace1])
            return cat_fig
        else:
            trace0=go.Bar(x=[i for i in cat_df_0.index],y=cat_df_0.values,name="grp0")
            trace1=go.Bar(x=[i for i in cat_df_1.index],y=cat_df_1.values,name="grp1")
            cat_fig=go.Figure([trace0,trace1])
            return cat_fig

if __name__ == "__main__":
    app.run_server()


# In[ ]:




