import json
import streamlit as st
import pandas as pd
import requests
import pymysql
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

mydb = pymysql.connect(host='127.0.0.1',
                   user='root',
                   password='8680974712@Sql',
                   database= 'phonepay'
                  )
mycursor = mydb.cursor()

#Aggregated_transaction

mycursor.execute("SELECT * FROM agg_trans")
table1 = mycursor.fetchall()
Aggre_transaction = pd.DataFrame(table1, columns=("States", "Years", "Quarter", "Transaction_type", "Transaction_count", "Transaction_amount"))

# Aggregated_user
mycursor.execute("SELECT * FROM agg_user")
table2 = mycursor.fetchall()
Aggre_user = pd.DataFrame(table2, columns=("States", "Years", "Quarter", "Brands", "Transaction_count", "Percentage"))

# Map_transaction
mycursor.execute("SELECT * FROM map_trans")
table3 = mycursor.fetchall()
Map_transaction = pd.DataFrame(table3, columns=("States", "Years", "Quarter", "Districts", "Transaction_count", "Transaction_amount"))

# Map_user
mycursor.execute("SELECT * FROM map_user")
table4 = mycursor.fetchall()
Map_user = pd.DataFrame(table4, columns=("States", "Years", "Quarter", "Districts", "RegisteredUser", "AppOpens"))

# Top_transaction
mycursor.execute("SELECT * FROM top_trans")
table5 = mycursor.fetchall()
Top_transaction = pd.DataFrame(table5, columns=("States", "Years", "Quarter", "Pincodes", "Transaction_count", "Transaction_amount"))

# Top_user
mycursor.execute("SELECT * FROM top_user")
table6 = mycursor.fetchall()
Top_user = pd.DataFrame(table6, columns=("States", "Years", "Quarter", "Pincodes", "RegisteredUser"))



def Agg_trans_yr(df, year):
    # Filter DataFrame for the specified year
    aty = df[df["Years"] == year].copy()
    aty.reset_index(drop=True, inplace=True)

    # Group by States and sum Transaction Count and Transaction Amount
    atyg = aty.groupby("States")[["Transaction_count", "Transaction_amount"]].sum().reset_index()

    # Melt the DataFrame to create a long-form DataFrame suitable for plotting
    atyg_melted = atyg.melt(id_vars=["States"], var_name="Transaction_Type", value_name="Value")

    # Create a grouped bar chart
    fig_combined = px.bar(
        atyg_melted,
        x="States",
        y="Value",
        color="Transaction_Type",  # Color each bar by Transaction Type
        barmode="group",  # Grouped bar chart
        title=f"{year} TRANSACTION COUNT vs AMOUNT",
        labels={"Value": "Value", "States": "States", "Transaction_Type": "Transaction Type"}
    )

    # Set the layout parameters
    fig_combined.update_layout(
        xaxis_title="States",
        yaxis_title="Value",
        legend_title="Transaction Type",
        width=1300,  # Adjust the width as needed
        height=700  # Adjust the height as needed
    )

    # Plot the bar chart
    st.plotly_chart(fig_combined)

    # Load India states GeoJSON data
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    data = json.loads(response.content)

    # Create choropleth maps for transaction amount and transaction count
    fig_amount = px.choropleth(
        atyg,
        geojson=data,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Transaction_amount",
        color_continuous_scale="Reds",
        range_color=(atyg["Transaction_amount"].min(), atyg["Transaction_amount"].max()),
        hover_name="States",
        title=f"{year} TRANSACTION AMOUNT",
        fitbounds="locations",
        width=600,
        height=600
    )
    fig_amount.update_geos(visible=False)  # Hide the base map
   

    fig_count = px.choropleth(
        atyg,
        geojson=data,
        locations="States",
        featureidkey="properties.ST_NM",
        color="Transaction_count",
        color_continuous_scale="Reds",
        range_color=(atyg["Transaction_count"].min(), atyg["Transaction_count"].max()),
        hover_name="States",
        title=f"{year} TRANSACTION COUNT",
        fitbounds="locations",
        width=600,
        height=600
    )
    fig_count.update_geos(visible=False)  # Hide the base map

    col1, col2 = st.columns(2)

    # Plot the choropleth maps in separate columns
    with col1:
        st.plotly_chart(fig_amount)

    with col2:
        st.plotly_chart(fig_count)
        
    return aty


def Agg_trans_yr_Q(df,quarter):
    atyq= df[df["Quarter"] == quarter]
    atyq.reset_index(drop= True, inplace= True)

    atyqg= atyq.groupby("States")[["Transaction_count", "Transaction_amount"]].sum()
    atyqg.reset_index(inplace= True)

    col1,col2= st.columns(2)

    with col1:
        fig_q_amount= px.bar(atyqg, x= "States", y= "Transaction_amount", 
                            title= f"{atyq['Years'].min()} AND {quarter} TRANSACTION AMOUNT",width= 600, height=650,
                            color_discrete_sequence=px.colors.diverging.Tropic_r)
        st.plotly_chart(fig_q_amount)

    with col2:
        fig_q_count= px.bar(atyqg, x= "States", y= "Transaction_count", 
                            title= f"{atyq['Years'].min()} AND {quarter} TRANSACTION COUNT",width= 600, height=650,
                            color_discrete_sequence=px.colors.sequential.Burg_r)
        st.plotly_chart(fig_q_count)

    col1,col2= st.columns(2)
    with col1:

        url= "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response= requests.get(url)
        data1= json.loads(response.content)
        states_name_tra= [feature["properties"]["ST_NM"] for feature in data1["features"]]
        states_name_tra.sort()

        fig_india_1= px.choropleth(atyqg, geojson= data1, locations= "States", featureidkey= "properties.ST_NM",
                                 color= "Transaction_amount", color_continuous_scale= "Reds",
                                 range_color= (atyqg["Transaction_amount"].min(),atyqg["Transaction_amount"].max()),
                                 hover_name= "States",title = f"{atyq['Years'].min()} AND {quarter} TRANSACTION AMOUNT",
                                 fitbounds= "locations",width =600, height= 600)
        fig_india_1.update_geos(visible =False)
        
        st.plotly_chart(fig_india_1)
    with col2:

        fig_india_2= px.choropleth(atyqg, geojson= data1, locations= "States", featureidkey= "properties.ST_NM",
                                 color= "Transaction_count", color_continuous_scale= "Reds",
                                 range_color= (atyqg["Transaction_count"].min(),atyqg["Transaction_count"].max()),
                                 hover_name= "States",title = f"{atyq['Years'].min()} AND {quarter} TRANSACTION COUNT",
                                 fitbounds= "locations",width =600, height= 600)
        fig_india_2.update_geos(visible =False)
        
        st.plotly_chart(fig_india_2)
    
    return atyq

def Aggre_Transaction_type(df, state):
    df_state= df[df["States"] == state]
    df_state.reset_index(drop= True, inplace= True)

    agttg= df_state.groupby("Transaction_type")[["Transaction_count", "Transaction_amount"]].sum()
    agttg.reset_index(inplace= True)

    col1,col2= st.columns(2)
    with col1:

        fig_hbar_1= px.bar(agttg, x= "Transaction_count", y= "Transaction_type", orientation="h",
                        color_discrete_sequence=px.colors.sequential.Aggrnyl, width= 600, 
                        title= f"{state.upper()} TRANSACTION TYPES AND TRANSACTION COUNT",height= 500)
        st.plotly_chart(fig_hbar_1)

    with col2:

        fig_hbar_2= px.bar(agttg, x= "Transaction_amount", y= "Transaction_type", orientation="h",
                        color_discrete_sequence=px.colors.sequential.Greens_r, width= 600,
                        title= f"{state.upper()} TRANSACTION TYPES AND TRANSACTION AMOUNT", height= 500)
        st.plotly_chart(fig_hbar_2)
        
def Aggre_user_plot_1(df,year):
    aguy= df[df["Years"] == year]
    aguy.reset_index(drop= True, inplace= True)
    
    aguyg= pd.DataFrame(aguy.groupby("Brands")["Transaction_count"].sum())
    aguyg.reset_index(inplace= True)

    fig_line_1= px.bar(aguyg, x="Brands",y= "Transaction_count", title=f"{year} BRANDS AND TRANSACTION COUNT",
                    width=1000,color_discrete_sequence=px.colors.sequential.haline_r)
    st.plotly_chart(fig_line_1)

    return aguy

def Aggre_user_plot_2(df,quarter):
    auqs= df[df["Quarter"] == quarter]
    auqs.reset_index(drop= True, inplace= True)

    fig_pie_1= px.pie(data_frame=auqs, names= "Brands", values="Transaction_count", hover_data= "Percentage",
                      width=1000,title=f"{quarter} QUARTER TRANSACTION COUNT PERCENTAGE",hole=0.5, color_discrete_sequence= px.colors.sequential.Magenta_r)
    st.plotly_chart(fig_pie_1)

    return auqs

def Aggre_user_plot_3(df,state):
    aguqy= df[df["States"] == state]
    aguqy.reset_index(drop= True, inplace= True)

    aguqyg= pd.DataFrame(aguqy.groupby("Brands")["Transaction_count"].sum())
    aguqyg.reset_index(inplace= True)

    fig_scatter_1= px.line(aguqyg, x= "Brands", y= "Transaction_count", markers= True,width=1000)
    st.plotly_chart(fig_scatter_1)

def map_trans_plot_1(df,state):
    miys= df[df["States"] == state]
    miysg= miys.groupby("Districts")[["Transaction_count","Transaction_amount"]].sum()
    miysg.reset_index(inplace= True)

    col1,col2= st.columns(2)
    with col1:
        fig_map_bar_1= px.bar(miysg, x= "Districts", y= "Transaction_amount",
                              width=600, height=500, title= f"{state.upper()} DISTRICTS TRANSACTION AMOUNT",
                              color_discrete_sequence= px.colors.sequential.Mint_r)
        st.plotly_chart(fig_map_bar_1)

    with col2:
        fig_map_bar_1= px.bar(miysg, x= "Districts", y= "Transaction_count",
                              width=600, height= 500, title= f"{state.upper()} DISTRICTS TRANSACTION COUNT",
                              color_discrete_sequence= px.colors.sequential.Mint)
        
        st.plotly_chart(fig_map_bar_1)

def map_trans_plot_2(df,state):
    miys= df[df["States"] == state]
    miysg= miys.groupby("Districts")[["Transaction_count","Transaction_amount"]].sum()
    miysg.reset_index(inplace= True)

    col1,col2= st.columns(2)
    with col1:
        fig_map_pie_1= px.pie(miysg, names= "Districts", values= "Transaction_amount",
                              width=600, height=500, title= f"{state.upper()} DISTRICTS TRANSACTION AMOUNT",
                              hole=0.5,color_discrete_sequence= px.colors.sequential.Mint_r)
        st.plotly_chart(fig_map_pie_1)

    with col2:
        fig_map_pie_1= px.pie(miysg, names= "Districts", values= "Transaction_count",
                              width=600, height= 500, title= f"{state.upper()} DISTRICTS TRANSACTION COUNT",
                              hole=0.5,  color_discrete_sequence= px.colors.sequential.Oranges_r)
        
        st.plotly_chart(fig_map_pie_1)

def map_user_plot_1(df, year):
    muy= df[df["Years"] == year]
    muy.reset_index(drop= True, inplace= True)
    muyg= muy.groupby("States")[["RegisteredUser", "AppOpens"]].sum()
    muyg.reset_index(inplace= True)

    fig_map_user_plot_1= px.line(muyg, x= "States", y= ["RegisteredUser","AppOpens"], markers= True,
                                width=1000,height=800,title= f"{year} REGISTERED USER AND APPOPENS", color_discrete_sequence= px.colors.sequential.Viridis_r)
    st.plotly_chart(fig_map_user_plot_1)

    return muy

def map_user_plot_2(df, quarter):
    muyq= df[df["Quarter"] == quarter]
    muyq.reset_index(drop= True, inplace= True)
    muyqg= muyq.groupby("States")[["RegisteredUser", "AppOpens"]].sum()
    muyqg.reset_index(inplace= True)

    fig_map_user_plot_1= px.line(muyqg, x= "States", y= ["RegisteredUser","AppOpens"], markers= True,
                                title= f"{df['Years'].min()}, {quarter} QUARTER REGISTERED USER AND APPOPENS",
                                width= 1000,height=800,color_discrete_sequence= px.colors.sequential.Rainbow_r)
    st.plotly_chart(fig_map_user_plot_1)

    return muyq

def map_user_plot_3(df, state):
    muyqs= df[df["States"] == state]
    muyqs.reset_index(drop= True, inplace= True)
    muyqsg= muyqs.groupby("Districts")[["RegisteredUser", "AppOpens"]].sum()
    muyqsg.reset_index(inplace= True)

    col1,col2= st.columns(2)
    with col1:
        fig_map_user_plot_1= px.bar(muyqsg, x= "RegisteredUser",y= "Districts",orientation="h",
                                    title= f"{state.upper()} REGISTERED USER",height=800,
                                    color_discrete_sequence= px.colors.sequential.Rainbow_r)
        st.plotly_chart(fig_map_user_plot_1)

    with col2:
        fig_map_user_plot_2= px.bar(muyqsg, x= "AppOpens", y= "Districts",orientation="h",
                                    title= f"{state.upper()} APPOPENS",height=800,
                                    color_discrete_sequence= px.colors.sequential.Rainbow)
        st.plotly_chart(fig_map_user_plot_2)

def top_user_plot_1(df,year):
    tuy= df[df["Years"] == year]
    tuy.reset_index(drop= True, inplace= True)

    tuyg= pd.DataFrame(tuy.groupby(["States","Quarter"])["RegisteredUser"].sum())
    tuyg.reset_index(inplace= True)

    fig_top_plot_1= px.bar(tuyg, x= "States", y= "RegisteredUser", barmode= "group", color= "Quarter",
                            width=1000, height= 800, color_continuous_scale= px.colors.sequential.Burgyl)
    st.plotly_chart(fig_top_plot_1)

    return tuy

def top_user_plot_2(df,state):
    tuys= df[df["States"] == state]
    tuys.reset_index(drop= True, inplace= True)

    tuysg= pd.DataFrame(tuys.groupby("Quarter")["RegisteredUser"].sum())
    tuysg.reset_index(inplace= True)

    fig_top_plot_1= px.bar(tuys, x= "Quarter", y= "RegisteredUser",barmode= "group",
                           width=1000, height= 800,color= "RegisteredUser",hover_data="Pincodes",
                            color_continuous_scale= px.colors.sequential.Magenta)
    st.plotly_chart(fig_top_plot_1)

def ques1():
    brand= Aggre_user[["Brands","Transaction_count"]]
    brand1= brand.groupby("Brands")["Transaction_count"].sum().sort_values(ascending=False)
    brand2= pd.DataFrame(brand1).reset_index()

    fig_brands= px.pie(brand2, values= "Transaction_count", names= "Brands", color_discrete_sequence=px.colors.sequential.dense_r,
                       title= "Top Mobile Brands of Transaction_count")
    return st.plotly_chart(fig_brands)

def ques2():
    lt= Aggre_transaction[["States", "Transaction_amount"]]
    lt1= lt.groupby("States")["Transaction_amount"].sum().sort_values(ascending= True)
    lt2= pd.DataFrame(lt1).reset_index().head(10)

    fig_lts= px.bar(lt2, x= "States", y= "Transaction_amount",title= "LOWEST TRANSACTION AMOUNT and STATES",
                    color_discrete_sequence= px.colors.sequential.Oranges_r)
    return st.plotly_chart(fig_lts)

def ques3():
    htd= Map_transaction[["Districts", "Transaction_amount"]]
    htd1= htd.groupby("Districts")["Transaction_amount"].sum().sort_values(ascending=False)
    htd2= pd.DataFrame(htd1).head(10).reset_index()

    fig_htd= px.pie(htd2, values= "Transaction_amount", names= "Districts", title="TOP 10 DISTRICTS OF HIGHEST TRANSACTION AMOUNT",
                    color_discrete_sequence=px.colors.sequential.Emrld_r)
    return st.plotly_chart(fig_htd)

def ques4():
    htd= Map_transaction[["Districts", "Transaction_amount"]]
    htd1= htd.groupby("Districts")["Transaction_amount"].sum().sort_values(ascending=True)
    htd2= pd.DataFrame(htd1).head(10).reset_index()

    fig_htd= px.pie(htd2, values= "Transaction_amount", names= "Districts", title="TOP 10 DISTRICTS OF LOWEST TRANSACTION AMOUNT",
                    color_discrete_sequence=px.colors.sequential.Greens_r)
    return st.plotly_chart(fig_htd)


def ques5():
    sa= Map_user[["States", "AppOpens"]]
    sa1= sa.groupby("States")["AppOpens"].sum().sort_values(ascending=False)
    sa2= pd.DataFrame(sa1).reset_index().head(10)

    fig_sa= px.bar(sa2, x= "States", y= "AppOpens", title="Top 10 States With AppOpens",
                color_discrete_sequence= px.colors.sequential.deep_r)
    return st.plotly_chart(fig_sa)

def ques6():
    sa= Map_user[["States", "AppOpens"]]
    sa1= sa.groupby("States")["AppOpens"].sum().sort_values(ascending=True)
    sa2= pd.DataFrame(sa1).reset_index().head(10)

    fig_sa= px.bar(sa2, x= "States", y= "AppOpens", title="lowest 10 States With AppOpens",
                color_discrete_sequence= px.colors.sequential.dense_r)
    return st.plotly_chart(fig_sa)

def ques7():
    stc= Aggre_transaction[["States", "Transaction_count"]]
    stc1= stc.groupby("States")["Transaction_count"].sum().sort_values(ascending=True)
    stc2= pd.DataFrame(stc1).reset_index()

    fig_stc= px.bar(stc2, x= "States", y= "Transaction_count", title= "STATES WITH LOWEST TRANSACTION COUNT",
                    color_discrete_sequence= px.colors.sequential.Jet_r)
    return st.plotly_chart(fig_stc)

def ques8():
    stc= Aggre_transaction[["States", "Transaction_count"]]
    stc1= stc.groupby("States")["Transaction_count"].sum().sort_values(ascending=False)
    stc2= pd.DataFrame(stc1).reset_index()

    fig_stc= px.bar(stc2, x= "States", y= "Transaction_count", title= "STATES WITH HIGHEST TRANSACTION COUNT",
                    color_discrete_sequence= px.colors.sequential.Magenta_r)
    return st.plotly_chart(fig_stc)

def ques9():
    ht= Aggre_transaction[["States", "Transaction_amount"]]
    ht1= ht.groupby("States")["Transaction_amount"].sum().sort_values(ascending= False)
    ht2= pd.DataFrame(ht1).reset_index().head(10)

    fig_lts= px.bar(ht2, x= "States", y= "Transaction_amount",title= "HIGHEST TRANSACTION AMOUNT and STATES",
                    color_discrete_sequence= px.colors.sequential.Oranges_r)
    return st.plotly_chart(fig_lts)

def ques10():
    dt= Map_transaction[["Districts", "Transaction_amount"]]
    dt1= dt.groupby("Districts")["Transaction_amount"].sum().sort_values(ascending=True)
    dt2= pd.DataFrame(dt1).reset_index().head(50)

    fig_dt= px.bar(dt2, x= "Districts", y= "Transaction_amount", title= "DISTRICTS WITH LOWEST TRANSACTION AMOUNT",
                color_discrete_sequence= px.colors.sequential.Mint_r)
    return st.plotly_chart(fig_dt)

# Streamlit part
def main():
    st.set_page_config(layout= "wide")

    st.title("PHONEPE DATA VISUALIZATION AND EXPLORATION")
    st.write("")

    with st.sidebar:
        select = option_menu("Main Menu", ["Home", "Data Exploration", "Statistical Charts"])

    if select == "Home":
        col1, col2 = st.columns(2)

        with col1:
            st.header("PHONEPE")
            st.subheader("INDIA'S BEST TRANSACTION APP")
            st.markdown("PhonePe is an Indian digital payments and financial technology company")
            st.write("****FEATURES****")
            st.write("****Credit & Debit card linking****")
            st.write("****Bank Balance check****")
            st.write("****Money Storage****")
            st.write("****PIN Authorization****")

        with col2:
            image_path = "C:\\Users\\mrnav\\OneDrive\\Desktop\\Python\\Phonepay\\phonepe_name.jpg"
            st.image(image_path)

        col3, col4 = st.columns(2)

        with col3:
            st.write("****Easy Transactions****")
            st.write("****One App For All Your Payments****")
            st.write("****Your Bank Account Is All You Need****")
            st.write("****Multiple Payment Modes****")
            st.write("****PhonePe Merchants****")
            st.write("****Multiple Ways To Pay****")
            st.write("****1.Direct Transfer & More****")
            st.write("****2.QR Code****")
            st.write("****Earn Great Rewards****")

        with col4:
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.markdown(" ")
            st.write("****No Wallet Top-Up Required****")
            st.write("****Pay Directly From Any Bank To Any Bank A/C****")
            st.write("****Instantly & Free****")

    if select == "Data Exploration":
            
            tab1, tab2, tab3= st.tabs(["Aggregated Analysis", "Map Analysis", "Top Analysis"])

            with tab1:
                method = st.selectbox("**Select the Analysis Method**",["Transaction Analysis", "User Analysis"])

                    
                if method == "Transaction Analysis":
                    col1,col2= st.columns(2)
                    with col1:
                        years_at = st.selectbox("**Select the Year**", range(2018, 2024), index=0)
                        
                    df_agg_tran_Y = Agg_trans_yr(Aggre_transaction, years_at)

                    
                    col1,col2= st.columns(2)
                    with col1:
                        quarters_at = st.selectbox("**Select the Quarter**", df_agg_tran_Y["Quarter"].unique())
                    df_agg_tran_Y_Q = Agg_trans_yr_Q(df_agg_tran_Y, quarters_at)
                    
                    #Select the State for Analyse the Transaction type
                    state_Y_Q= st.selectbox("**Select the State**",df_agg_tran_Y_Q["States"].unique())

                    Aggre_Transaction_type(df_agg_tran_Y_Q,state_Y_Q)

                elif method == "User Analysis":
                    year_au= st.selectbox("Select the Year_AU",Aggre_user["Years"].unique())
                    agg_user_Y= Aggre_user_plot_1(Aggre_user,year_au)

                    quarter_au= st.selectbox("Select the Quarter_AU",agg_user_Y["Quarter"].unique())
                    agg_user_Y_Q= Aggre_user_plot_2(agg_user_Y,quarter_au)

                    state_au= st.selectbox("**Select the State_AU**",agg_user_Y["States"].unique())
                    Aggre_user_plot_3(agg_user_Y_Q,state_au)

            with tab2:
                method_map = st.selectbox("**Select the Analysis Method(MAP)**",["Map Transaction Analysis", "Map User Analysis"])

                if method_map == "Map Transaction Analysis":
                    col1,col2= st.columns(2)
                    with col1:
                        years_m2= st.selectbox("**Select the Year_mt**", range(Map_transaction["Years"].min(), Map_transaction["Years"].max()+1), index=0)

                    df_map_tran_Y= Agg_trans_yr(Map_transaction, years_m2)

                    col1,col2= st.columns(2)
                    with col1:
                        state_m3= st.selectbox("Select the State_mt", df_map_tran_Y["States"].unique())

                    map_trans_plot_1(df_map_tran_Y,state_m3)
                    
                    col1,col2= st.columns(2)
                    with col1:
                         quarters_m2= st.selectbox("**Select the Quarter_mt**", df_map_tran_Y["Quarter"].unique())

                    df_map_tran_Y_Q= Agg_trans_yr_Q(df_map_tran_Y, quarters_m2)

                    col1,col2= st.columns(2)
                    with col1:
                        state_m4= st.selectbox("Select the State_mty", df_map_tran_Y_Q["States"].unique())            

                    map_trans_plot_2(df_map_tran_Y_Q, state_m4)

                elif method_map == "Map User Analysis":
                    col1,col2= st.columns(2)
                    with col1:
                        year_mu1= st.selectbox("**Select the Year_mu**", Map_user["Years"].unique())
                    map_user_Y= map_user_plot_1(Map_user, year_mu1)

                    col1,col2= st.columns(2)
                    with col1:
                        quarter_mu1= st.selectbox("**Select the Quarter_mu**", map_user_Y["Quarter"].unique())
                    map_user_Y_Q= map_user_plot_2(map_user_Y,quarter_mu1)

                    col1,col2= st.columns(2)
                    with col1:
                        state_mu1= st.selectbox("**Select the State_mu**", map_user_Y_Q["States"].unique())
                    map_user_plot_3(map_user_Y_Q, state_mu1)

            with tab3:
                method_top = st.selectbox("**Select the Analysis Method(TOP)**",["Top Transaction Analysis", "Top User Analysis"])

                if method_top == "Top Transaction Analysis":
                    col1,col2= st.columns(2)
                    with col1:
                        years_t2= st.selectbox("**Select the Year_tt**", range(Top_transaction["Years"].min(), Top_transaction["Years"].max()+1), index=0)

                    df_top_tran_Y= Agg_trans_yr(Top_transaction,years_t2)

                    
                    col1,col2= st.columns(2)
                    with col1:
                        quarters_t2= st.selectbox("**Select the Quarter_tt**", df_top_tran_Y["Quarter"].unique())

                    df_top_tran_Y_Q= Agg_trans_yr_Q(df_top_tran_Y, quarters_t2)

                elif method_top == "Top User Analysis":
                    col1,col2= st.columns(2)
                    with col1:
                        years_t3= st.selectbox("**Select the Year_tu**", Top_user["Years"].unique())

                    df_top_user_Y= top_user_plot_1(Top_user,years_t3)

                    col1,col2= st.columns(2)
                    with col1:
                        state_t3= st.selectbox("**Select the State_tu**", df_top_user_Y["States"].unique())

                    df_top_user_Y_S= top_user_plot_2(df_top_user_Y,state_t3)

    if select == "Statistical Charts":
        ques= st.selectbox("**Select the Question**",('Top Brands Of Mobiles Used','States With Lowest Trasaction Amount',
                                    'Districts With Highest Transaction Amount','Top 10 Districts With Lowest Transaction Amount',
                                    'Top 10 States With AppOpens','Least 10 States With AppOpens','States With Lowest Trasaction Count',
                                    'States With Highest Trasaction Count','States With Highest Trasaction Amount',
                                    'Top 50 Districts With Lowest Transaction Amount'))
        
        if ques=="Top Brands Of Mobiles Used":
            ques1()

        elif ques=="States With Lowest Trasaction Amount":
            ques2()

        elif ques=="Districts With Highest Transaction Amount":
            ques3()

        elif ques=="Top 10 Districts With Lowest Transaction Amount":
            ques4()

        elif ques=="Top 10 States With AppOpens":
            ques5()

        elif ques=="Least 10 States With AppOpens":
            ques6()

        elif ques=="States With Lowest Trasaction Count":
            ques7()

        elif ques=="States With Highest Trasaction Count":
            ques8()

        elif ques=="States With Highest Trasaction Amount":
            ques9()

        elif ques=="Top 50 Districts With Lowest Transaction Amount":
            ques10()

if __name__ == "__main__":
    main()
