#!/usr/bin/env python
# coding: utf-8

# # COVID 19 Case

# Week 4: Test case 2
# 
# Groep 16: 
# Studenten: Floor van de Meent, Maxim van Duin, Benjamin Niemann en Roy Pontman

# # Importing packages

# In[1]:


import pandas as pd
import numpy as np
import requests
import plotly.express as px
import missingno as msno
#!pip install kaggle
import kaggle
import os
#!pip install streamlit
import streamlit as st
from PIL import Image


# In[2]:


print(os.getcwd())
dir(kaggle.api)


# # Datasets ophalen d.m.v API request

# Dataset voor aantal coronagevallen en sterfgevallen:

# In[3]:


#kaggle.api.dataset_download_file('totoro29/covid19-cases-deaths', 'covid 19 CountryWise.csv')


# In[4]:


covid_death = pd.read_csv('covid%2019%20CountryWise.csv')
covid_death.head()


# Dataset voor aantal vaccinaties:

# In[5]:


kaggle.api.dataset_download_file('gpreda/covid-world-vaccination-progress', 'country_vaccinations.csv')


# In[6]:


covid_vac = pd.read_csv('country_vaccinations.csv')
covid_vac.head()


# Dataset voor manufacturers (Welk vaccins is waar gegeven en hoe vaak):

# In[7]:


kaggle.api.dataset_download_file('gpreda/covid-world-vaccination-progress', 'country_vaccinations_by_manufacturer.csv')


# In[8]:


covid_manufac = pd.read_csv('country_vaccinations_by_manufacturer.csv')
covid_manufac.head()


# **API Beschrijving**
# 
# Om tot de datasets te komen is eerst geprobeerd om via de normale package _requests_ en de methode _get.requests()_ tot de csv-file te komen. Echter werkte dit niet, met deze package kregen we alleen de html code als text file. Hierdoor moesten we gebruik maken van een andere API. Kaggle heeft zijn eigen API gemaakt om zo tot de datasets te komen van Kaggle.
# 
# Door _'kaggle.api.dataset_download_file()'_ te gebruiken wordt er alshetware een request gestuurd naar kaggle waarbij er gekeken wordt naar de owner van de dataset, de dataset zelf en de file die je eruit wil extracten. In ons geval gaat het om:
# - De owners: _gpreda_ en _totoro29_
# - De datasets: _covid-world-vaccination-progress_ en _covid19-cases-deaths_.

# # EDA Sterfgevallen

# In[9]:


#covid_death.shape


# In[10]:


#covid_death.columns


# In[11]:


covid_death.describe()


# In[12]:


covid_death.info()


# **MISSING VALUES**

# In[13]:


covid_death.isna().sum()


# In[14]:


msno.matrix(covid_death, figsize = (30,10))


# In[15]:


df = covid_death['Total Cases per 100k pop'].isna()
df = df[df == True]


# In[16]:


#covid_death.iloc[226,:]


# In[17]:


covid_death = covid_death.drop(226)


# In[18]:


msno.matrix(covid_death, figsize = (30,10))


# **TOTAL CASES**

# In[19]:


table_total_cases = covid_death[covid_death['Total Cases'] == 0]


# In[20]:


covid_death = covid_death.drop(233)
covid_death = covid_death.drop(236)
#covid_death[covid_death['Total Cases'] == 0]


# In[21]:


#covid_death.shape


# In[22]:


covid_death.groupby('Region')['Total Cases'].agg(sum)


# In[23]:


covid_death['Total Recovered'] = covid_death['Total Cases'] - covid_death['Total Deaths']
covid_death.head()
#covid_death['Total Deaths'].max()


# # EDA Dataset Vaccinaties

# In[24]:


#covid_vac.shape


# In[25]:


#covid_vac.columns


# In[26]:


covid_vac.describe()


# In[27]:


covid_vac.info()


# In[28]:


covid_vac.isna().sum()


# In[29]:


msno.matrix(covid_vac, figsize = (30,10))


# In[30]:


covid_vac['country'].value_counts()


# In[31]:


covid_vac.head()


# In[32]:


covid_vac.rename(columns ={'country':'Country'},inplace = True)
covid_vac.head()


# In[33]:


covid_death_vac = covid_death.merge(covid_vac, on = 'Country')
covid_death_vac.head()


# In[34]:


df = covid_death_vac[['Country','date','total_vaccinations','Region']]


# In[35]:


df.dropna()
fig = px.line(df, x='date', y='total_vaccinations', color = 'Region')


# In[36]:


df = covid_death_vac.groupby('Country').agg({'Total Cases':'sum','total_vaccinations':'sum',
                                        'Total Deaths':'sum','Total Recovered':'sum'})


# In[ ]:





# **CODE VOOR VACCINATIES PER MAAND (SLIDER) + VISUALISATIE**

# In[37]:


covid_vac['month_year'] = pd.to_datetime(covid_vac['date']).dt.to_period('M')
covid_vac = covid_vac.sort_values("month_year")


# In[38]:


covid_vac_mean = covid_vac.groupby(["month_year", 'Country', 'iso_code'])['total_vaccinations_per_hundred'].mean().reset_index(name='Monthly_average')

covid_vac_mean["month_year"] = covid_vac_mean["month_year"].astype(str)


# In[39]:


fig1 = px.choropleth(covid_vac_mean, locations="iso_code",
                    animation_frame="month_year",
                    color="Monthly_average",
                    hover_name="Country",
                    color_continuous_scale=px.colors.sequential.Plasma)

fig1.update_layout(
    title= 'Monthly average vaccinations per hundred people per country',
    width=950, height=700,
    titlefont={'size': 28}, paper_bgcolor= '#E6E6E6',
    plot_bgcolor= '#E6E6E6',
    legend_title = 'Monthly average vaccinations')


# In[40]:


covid_vac_mean1 = covid_vac.groupby(["month_year", 'Country', 'iso_code'])['people_vaccinated_per_hundred'].mean().reset_index(name='Monthly_average_people')
covid_vac_mean1["month_year"] = covid_vac_mean1["month_year"].astype(str)


# In[41]:


fig2 = px.choropleth(covid_vac_mean1, locations="iso_code",
                    animation_frame="month_year",
                    color="Monthly_average_people",
                    hover_name="Country",
                    color_continuous_scale=px.colors.sequential.Plasma)

fig2.update_layout(
    title= 'Monthly average of vaccinated people per hundred inhabitants per country',
    width=900, height=700,
    titlefont={'size': 20}, paper_bgcolor= '#E6E6E6',
    plot_bgcolor= '#E6E6E6',
    legend_title = 'Monthly average vaccinations')


# **CODE VOOR CASES PER COUNTRY/REGIO (DROPDOWN) + VISUALISATIE**

# In[42]:


#Aantal gevallen per 100.000 inwoners
fig3 = px.bar(covid_death, x = "Country" , y="Total Cases per 100k pop", color = "Region", title = 'All Regions', text = "Country")

dropdown_buttons = [  {'label': "All Regions", 'method': "update",'args': [{"visible": [True, True, True, True, True, True, True]}, {'title': 'alles'}]}, 
                   {'label': 'Americas', 'method': 'update','args': [{'visible': [True, False, False, False, False, False, False]}, {'title': 'America'}]},  
                    {'label': 'South-East Asia', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False]}, {'title': 'South-East Asia'}]},  
                    {'label': "Europe", 'method': "update",'args': [{"visible": [False, False, True, False, False, False, False]}, {'title': 'Europe'}]},
                   {'label': 'Western Pacific', 'method': 'update','args': [{'visible': [False, False, False, True, False, False, False]}, {'title': 'Western Pacific'}]},
                   {'label': "Eastern Mediterranean", 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False]}, {'title': 'Eastern Mediterranean'}]},
                   {'label': "Africa", 'method': "update",'args': [{"visible": [False, False, False, False, False, True, False]}, {'title': 'Africa'}]}
                  ]

fig3.update_layout({'updatemenus':[{'type': "dropdown",'x': 1.3,'y': 0.6,'showactive': True,'active': 0,'buttons': dropdown_buttons}]},
                   height = 700, width = 1000)


# In[43]:


#aantal gevallen in log en linear schaal
fig4 = px.bar(covid_death, x = "Country" , y="Total Cases", color = "Region", text = "Country", title = 'All regions')

dropdown_buttons_region = [  {'label': "All Regions", 'method': "update",'args': [{"visible": [True, True, True, True, True, True, True]}, {'title': 'All Regions'}]}, 
                   {'label': 'Americas', 'method': 'update','args': [{'visible': [True, False, False, False, False, False, False]}, {'title': 'America'}]},  
                    {'label': 'South-East Asia', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False]}, {'title': 'South-East Asia'}]},  
                    {'label': "Europe", 'method': "update",'args': [{"visible": [False, False, True, False, False, False, False]}, {'title': 'Europe'}]},
                   {'label': 'Western Pacific', 'method': 'update','args': [{'visible': [False, False, False, True, False, False, False]}, {'title': 'Western Pacific'}]},
                   {'label': "Eastern Mediterranean", 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False]}, {'title': 'Eastern Mediterranean'}]},
                   {'label': "Africa", 'method': "update",'args': [{"visible": [False, False, False, False, False, True, False]}, {'title': 'Africa'}]}
                  ]

fig4.update_layout({'updatemenus':[{'type': "dropdown",'x': 1.3,'y': 0.6,'showactive': True,'active': 0,'buttons': dropdown_buttons_region},
                dict(buttons =[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}]),
                                  ])]},height = 700, width = 1000)



# In[44]:


# Aantal doden per 100.000
fig5 = px.bar(covid_death, x = "Country" , y="Total Deaths per 100k pop", color = "Region",title = 'All Regions', text = "Country")

dropdown_buttons = [  {'label': "All regions", 'method': "update",'args': [{"visible": [True, True, True, True, True, True, True]}, {'title': 'All Regions'}]}, 
                   {'label': 'Americas', 'method': 'update','args': [{'visible': [True, False, False, False, False, False, False]}, {'title': 'America'}]},  
                    {'label': 'South-East Asia', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False]}, {'title': 'South-East Asia'}]},  
                    {'label': "Europe", 'method': "update",'args': [{"visible": [False, False, True, False, False, False, False]}, {'title': 'Europe'}]},
                   {'label': 'Western Pacific', 'method': 'update','args': [{'visible': [False, False, False, True, False, False, False]}, {'title': 'Western Pacific'}]},
                   {'label': "Eastern Mediterranean", 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False]}, {'title': 'Eastern Mediterranean'}]},
                   {'label': "Africa", 'method': "update",'args': [{"visible": [False, False, False, False, False, True, False]}, {'title': 'Africa'}]}
                  ]

fig5.update_layout({'updatemenus':[{'type': "dropdown",'x': 1.3,'y': 0.6,'showactive': True,'active': 0,'buttons': dropdown_buttons}]},
                   height = 700, width = 1000)



# In[45]:


#Totaal aantal doden in log en linear schaal 
fig6 = px.bar(covid_death, x = "Country" , y="Total Deaths", color = "Region",title = 'All Regions', text = "Country")

dropdown_buttons = [  {'label': "All regions", 'method': "update",'args': [{"visible": [True, True, True, True, True, True, True]}, {'title': 'All Regions'}]}, 
                   {'label': 'Americas', 'method': 'update','args': [{'visible': [True, False, False, False, False, False, False]}, {'title': 'America'}]},  
                    {'label': 'South-East Asia', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False]}, {'title': 'South-East Asia'}]},  
                    {'label': "Europe", 'method': "update",'args': [{"visible": [False, False, True, False, False, False, False]}, {'title': 'Europe'}]},
                   {'label': 'Western Pacific', 'method': 'update','args': [{'visible': [False, False, False, True, False, False, False]}, {'title': 'Western Pacific'}]},
                   {'label': "Eastern Mediterranean", 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False]}, {'title': 'Eastern Mediterranean'}]},
                   {'label': "Africa", 'method': "update",'args': [{"visible": [False, False, False, False, False, True, False]}, {'title': 'Africa'}]}
                  ]


fig6.update_layout({'updatemenus':[{'type': "dropdown",'x': 1.3,'y': 0.6,'showactive': True,'active': 0,'buttons': dropdown_buttons}, dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
)]},height = 700, width = 1000)





# In[46]:


fig7 = px.bar(covid_death, x = "Country" , y="Total Recovered" , color = "Region",title = 'All Regions', text = "Country")

dropdown_buttons = [  {'label': "All regions", 'method': "update",'args': [{"visible": [True, True, True, True, True, True, True]}, {'title': 'All Regions'}]}, 
                   {'label': 'Americas', 'method': 'update','args': [{'visible': [True, False, False, False, False, False, False]}, {'title': 'America'}]},  
                    {'label': 'South-East Asia', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False]}, {'title': 'South-East Asia'}]},  
                    {'label': "Europe", 'method': "update",'args': [{"visible": [False, False, True, False, False, False, False]}, {'title': 'Europe'}]},
                   {'label': 'Western Pacific', 'method': 'update','args': [{'visible': [False, False, False, True, False, False, False]}, {'title': 'Western Pacific'}]},
                   {'label': "Eastern Mediterranean", 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False]}, {'title': 'Eastern Mediterranean'}]},
                   {'label': "Africa", 'method': "update",'args': [{"visible": [False, False, False, False, False, True, False]}, {'title': 'Africa'}]}
                  ]


fig7.update_layout({'updatemenus':[{'type': "dropdown",'x': 1.3,'y': 0.6,'showactive': True,'active': 0,'buttons': dropdown_buttons}, dict(
                 buttons=[
                     dict(label="Linear",  
                          method="relayout", 
                          args=[{"yaxis.type": "linear"}]),
                     dict(label="Log", 
                          method="relayout", 
                          args=[{"yaxis.type": "log"}])]
)]},height = 700, width = 1000)


# # EDA Manufactures

# In[47]:


covid_manufac1 = covid_manufac.groupby(["location", 'vaccine'])['total_vaccinations'].max().reset_index(name='Aantal vacinaties')


# In[48]:


fig8 = px.bar(covid_manufac1, x = "location" , y="Aantal vacinaties", color = "vaccine")

 

fig8.update_layout({'updatemenus':[{'type': "dropdown", 'x': 1.25,'y': 0.65,
            'buttons':list([
                dict(label="All",
                     method="update",
                     args=[{"visible": [True, True , True, True, True, True, True, True, True, True]},
                           {"title": "All vaccins"}]),
                dict(label="CanSino",
                     method="update",
                     args=[{"visible": [True, False , False, False, False, False, False, False, False, False]},
                           {"title": "CanSino",
                            }]),
                dict(label="Moderna",
                     method="update",
                     args=[{"visible": [False, True , False, False, False, False, False, False, False, False]},
                           {"title": "Moderna",
                            }]),
                dict(label="Oxford/AstraZeneca",
                     method="update",
                     args=[{"visible": [False, False , True, False, False, False, False, False, False, False]},
                           {"title": "Oxford/AstraZeneca",
                            }]),
                dict(label="Pfizer/BioNTech",
                     method="update",
                     args=[{"visible": [False, False , False, True, False, False, False, False, False, False]},
                           {"title": "Pfizer/BioNTech",
                            }]),  
                dict(label="Sinopharm/Beijing",
                     method="update",
                     args=[{"visible": [False, False , False, False, True, False, False, False, False, False]},
                           {"title": "Sinopharm/Beijing",
                            }]),
                dict(label="Sputnik V",
                     method="update",
                     args=[{"visible": [False, False , False, False, False, True, False, False, False, False]},
                           {"title": "Sputnik V",
                            }]),
                dict(label="Johnson&Jhonson",
                     method="update",
                     args=[{"visible": [False, False , False, False, False, False, True, False, False, False]},
                           {"title": "Johnson&Johnson",
                            }]),
                dict(label="Novavax",
                     method="update",
                     args=[{"visible": [False, False , False, False, False, False, False, True, False, False]},
                           {"title": "Novavax",
                            }]),
                dict(label="Sinovac",
                     method="update",
                     args=[{"visible": [False, False , False, False, False, False, False, False, True, False]},
                           {"title": "Sinovac",
                            }]),
                dict(label="Covaxin",
                     method="update",
                     args=[{"visible": [False, False , False, False, False, False, False, False, False, True]},
                           {"title": "Covaxin",
                            }])                 
            ])}]},height = 900, width = 1000)


# # Blog in Streamlit

# In[52]:


st.title('World Wide Covid')


# In[51]:


# Buttons voor cases, recovered, deaths, vaccinaties, manufactures
if st.sidebar.button('Home',key = "1"):
    st.header('Home')
    st.markdown('**Welcome to the Covid19 dashboard**') 
    st.markdown('This dashboard is made to visualize every subject around the covid pandemic. On the left side of the screen are buttons to select a specific subject. Every subject has his own graphs and description.')
    st.sidebar.button('Cases',key = "2")
    st.sidebar.button('Deaths',key = "3")
    st.sidebar.button('Vaccinations',key = "4")
    st.sidebar.button('Manufactures',key = "5")
elif st.sidebar.button('Cases', key = "6"):
    st.header('Total Cases')
    st.markdown('**Welcome to the Covid19 dashboard of total cases**') 
    st.markdown('Here you can find some visualizations of total cases around the world, per region, per country and per 100.000 inhabitants')
    st.plotly_chart(fig3)
    st.plotly_chart(fig4)
    st.sidebar.button('Home',key = "7")
elif st.sidebar.button('Deaths', key = "8"):
    st.header('Total Deaths')
    st.markdown('**Welcome to the Covid19 dashboard of total deaths**') 
    st.markdown('Here you can find some visualizations of total deaths around the world, per region, per country and per 100.000 inhabitants')
    st.plotly_chart(fig5)
    st.plotly_chart(fig6)
    st.sidebar.button('Home',key = "9")
elif st.sidebar.button('Vaccinations', key = "10"):
    st.header('Total Vaccinations')
    st.markdown('**Welcome to the Covid19 dashboard of total vaccinations**') 
    st.markdown('Here you can find some visualizations of total vaccinations around the world, per region, per country and per 100.000 inhabitants')
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)
    st.sidebar.button('Home',key = "11")
elif st.sidebar.button('Recovered',key = "12"):
    st.header('Total Recovered')
    st.markdown('**Welcome to the Covid19 dashboard of total recovered people from covid19**') 
    st.markdown('Here you can find some visualizations of recovering form covid19 around the world, per region, per country and per 100.000 inhabitants')
    st.plotly_chart(fig7)
    st.sidebar.button('Home', key = "13")
elif st.sidebar.button('Manufactures',key = "14"):
    st.header('Total Manufacturers')
    st.markdown('**Welcome to the Covid19 dashboard of manufacturers**') 
    st.markdown('Here you can find some visualizations of manufacturers around the world, per region, per country and per 100.000 inhabitants')
    st.plotly_chart(fig8)
    st.sidebar.button('Home', key = "15")
else :
    st.header('Home')
    st.markdown('**Welcome to the Covid19 dashboard**') 
    st.markdown('This dashboard is made to visualize every subject around the covid pandemic. On the left side of the screen are buttons to select a specific subject. Every subject has his own graphs and description.')
    st.image('https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.hva.nl%2F&psig=AOvVaw0KvpAwsfpcA3e0HekFiYFU&ust=1664534835998000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCJDS-c7pufoCFQAAAAAdAAAAABAE', caption = None)
# Checkboxen


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# # Bronnen

# API Kaggle aanmaken:
# - https://www.kaggle.com/docs/api
# 
