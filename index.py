# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 00:57:01 2018

@author: Pippo
"""
#import random
import sys
ver = sys.version[:1] == "2"

from flask import Flask, render_template, request
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import json_item #, components
import json
#from bokeh.models.widgets import Select

app = Flask(__name__)

import numpy as np
import re
import requests
import datetime


 #### Get dataset from scrapyhub
 
apikey = "c17aaf3afb114e59916306e0cd493350"
tag = datetime.datetime.now().date()

# update database (runscrapy spider)
data = {
  'project': '364889',
  'spider': 'house',
  'units': '1',
  'add_tag': tag
}

#runspider = requests.post('https://app.scrapinghub.com/api/run.json', 
#                         data=data, auth=(apikey, ''))

#get last job
params = (
    ('project', '364889'),
    ('spider', 'house'),
    ('state', 'finished')
    #('count', '1'),
)

lastJobs = requests.get('https://app.scrapinghub.com/api/jobs/list.json',
                        params=params, auth=(apikey, ''))
jobtodownload = lastJobs.json()['jobs'][0]['id']

# get database
response = requests.get("https://storage.scrapinghub.com/items/"+ jobtodownload +"?format=json", 
                        auth=(apikey,""))


data = response.json()
df = pd.DataFrame.from_records(data)

### Cleaning the dataset

df.dropna(subset=['price'], inplace=True)

df.price = df.price.apply(lambda x: x.replace("$",""))
df.price = df.price.apply(lambda x: max(re.findall("(\d+)",x)) if len(x) > 7 else x)
df.price = df.price.apply(lambda x: float(x.replace(",","")))
df = df[df.price<10000] #take out strange values

# Get rid of empty rows

df.dropna(subset=['address'], inplace=True)

# First start with numeric columns

def clean_numbers(col):
    col = col.str.extract(r"(\d+)")[0]
    col = col.apply(lambda x: float(x) if x is not np.nan else x)
    col = col.apply(lambda x: None if x > 10 else x)
    
    return col

df['views'] = df.views.str[0]
df['bathroom'] = clean_numbers(df.bathroom)
df['bedrooms'] = clean_numbers(df.bedrooms)


# Then date
def clean_date(col, today):
    col[col.str.contains("ago", na=False)] = today
    col[col.str.contains("yesterday", na=False)] = (pd.to_datetime(today,format="%d/%m/%Y")-pd.Timedelta('1 days')).strftime('%d/%m/%Y')
    col[col.notnull()] = col[col.notnull()].apply(lambda x: None if len(x)!=12 else x)
    col[col.str.contains(r"(\s)", na=False)] = None 
    col = pd.to_datetime(col,format="%d/%m/%Y")

df['availability'] = clean_date(df.availability, u"20/12/2018")
df['date_listed'] = clean_date(df.date_listed, u"20/12/2018")
df['date_update'] = clean_date(df.date_update, u"20/12/2018")

#### Finally with text

# Clean suburb names

suburb = ["Abbotsbury", "Abbotsford", "Acacia Gardens", "Agnes Banks", "Airds", "Alexandria", "Alfords Point", "Allambie Heights", "Allawah", "Ambarvale", "Annandale", "Annangrove", "Arcadia", "Arncliffe", "Arndell Park", "Artarmon", "Ashbury", "Ashcroft", "Ashfield", "Asquith", "Auburn", "Austral", "Avalon Beach", "Badgerys Creek", "Balgowlah", "Balgowlah Heights", "Balmain", "Balmain East", "Bangor", "Banksia", "Banksmeadow", "Bankstown", "Bankstown Aerodrome", "Barangaroo", "Barden Ridge", "Bardia", "Bardwell Park", "Bardwell Valley", "Barra Brui", "Bass Hill", "Baulkham Hills", "Bayview", "Beacon Hill", "Beaconsfield", "Beaumont Hills", "Beecroft", "Belfield", "Bella Vista", "Bellevue Hill", "Belmore", "Belrose", "Berala", "Berkshire Park", "Berowra", "Berowra Creek", "Berowra Heights", "Berowra Waters", "Berrilee", "Beverley Park", "Beverly Hills", "Bexley", "Bexley North", "Bickley Vale", "Bidwill", "Bilgola Beach", "Bilgola Plateau", "Birchgrove", "Birrong", "Blackett", "Blacktown", "Blair Athol", "Blairmount", "Blakehurst", "Bligh Park", "Bondi", "Bondi Beach", "Bondi Junction", "Bonnet Bay", "Bonnyrigg", "Bonnyrigg Heights", "Bossley Park", "Botany", "Bow Bowing", "Box Hill", "Bradbury", "Breakfast Point", "Brighton-Le-Sands", "Bringelly", "Bronte", "Brooklyn", "Brookvale", "Bundeena", "Bungarribee", "Burwood", "Burwood Heights", "Busby", "", "Cabarita", "Cabramatta", "Cabramatta West", "Caddens", "Cambridge Gardens", "Cambridge Park", "Camden", "Camden South", "Camellia", "Cammeray", "Campbelltown", "Camperdown", "Campsie", "Canada Bay", "Canley Heights", "Canley Vale", "Canoelands", "Canterbury", "Caringbah", "Caringbah South", "Carlingford", "Carlton", "Carnes Hill", "Carramar", "Carss Park", "Cartwright", "Castle Cove", "Castle Hill", "Castlecrag", "Castlereagh", "Casula", "Catherine Field", "Cattai", "Cawdor", "Cecil Hills", "Cecil Park", "Centennial Park", "Central Business District", "Chatswood", "Chatswood West", "Cheltenham", "Cherrybrook", "Chester Hill", "Chifley", "Chippendale", "Chipping Norton", "Chiswick", "Chullora", "Church Point", "Claremont Meadows", "Clarendon", "Clareville", "Claymore", "Clemton Park", "Clontarf", "Clovelly", "Clyde", "Coasters Retreat", "Cobbitty", "Colebee", "Collaroy", "Collaroy Plateau", "Colyton", "Como", "Concord", "Concord West", "Condell Park", "Connells Point", "Constitution Hill", "Coogee", "Cottage Point", "Cowan", "Cranebrook", "Cremorne", "Cremorne Point", "Cromer", "Cronulla", "Crows Nest", "Croydon", "Croydon Park", "Curl Curl", "Currans Hill", "Currawong Beach", "Daceyville", "Dangar Island", "Darling Point", "Darlinghurst", "Darlington", "Davidson", "Dawes Point", "Dean Park", "Dee Why", "Denham Court", "Denistone", "Denistone East", "Denistone West", "Dharruk", "Dolans Bay", "Dolls Point", "Doonside", "Double Bay", "Dover Heights", "Drummoyne", "Duffys Forest", "Dulwich Hill", "Dundas", "Dundas Valley", "Dural", "Eagle Vale", "Earlwood", "East Gordon", "East Hills", "East Killara", "East Lindfield", "East Ryde", "East Sydney", "Eastern Creek", "Eastgardens", "Eastlakes", "Eastwood", "Edensor Park", "Edgecliff", "Edmondson Park", "Elanora Heights", "Elderslie", "Elizabeth Bay", "Elizabeth Hills", "Ellis Lane", "Elvina Bay", "Emerton", "Emu Heights", "Emu Plains", "Enfield", "Engadine", "Englorie Park", "Enmore", "Epping", "Ermington", "Erskine Park", "Erskineville", "Eschol Park", "Eveleigh", "Fairfield", "Fairfield East", "Fairfield Heights", "Fairfield West", "Fairlight", "Fiddletown", "Five Dock", "Flemington", "Forest Glen", "Forest Lodge", "Forestville", "Freemans Reach", "Frenchs Forest", "Freshwater", "Galston", "Georges Hall", "Gilead", "Girraween", "Gladesville", "Glebe", "Gledswood Hills", "Glen Alpine", "Glendenning", "Glenfield", "Glenhaven", "Glenmore Park", "Glenorie", "Glenwood", "Glossodia", "Gordon", "Granville", "Grasmere", "Grays Point", "Great Mackerel Beach", "Green Valley", "Greenacre", "Greendale", "Greenfield Park", "Greenhills Beach", "Greenwich", "Gregory Hills", "Greystanes", "Guildford", "Guildford West", "Gymea", "Gymea Bay", "Haberfield", "Hammondville", "Harrington Park", "Harris Park", "Hassall Grove", "Hawkesbury River", "Haymarket", "Heathcote", "Hebersham", "Heckenberg", "Henley", "Hillsdale", "Hinchinbrook", "Hobartville", "Holroyd", "Holsworthy", "Homebush", "Homebush West", "Horningsea Park", "Hornsby", "Hornsby Heights", "Horsley Park", "Hoxton Park", "Hunters Hill", "Huntingwood", "Huntleys Cove", "Huntleys Point", "Hurlstone Park", "Hurstville", "Hurstville Grove", "Illawong", "Ingleburn", "Ingleside", "Jamisontown", "Jannali", "Jordan Springs", "Kangaroo Point", "Kareela", "Kearns", "Kellyville", "Kellyville Ridge", "Kemps Creek", "Kensington", "Kenthurst", "Kentlyn", "Killara", "Killarney Heights", "Kings Cross", "Kings Langley", "Kings Park", "Kingsford", "Kingsgrove", "Kingswood", "Kingswood Park", "Kirkham", "Kirrawee", "Kirribilli", "Kogarah", "Kogarah Bay", "Ku-ring-gai Chase", "Kurnell", "Kurraba Point", "Kyeemagh", "Kyle Bay", "La Perouse", "Lakemba", "Lalor Park", "Lane Cove", "Lane Cove North", "Lane Cove West", "Lansdowne", "Lansvale", "Laughtondale", "Lavender Bay", "Leets Vale", "Leichhardt", "Len Waters Estate", "Leonay", "Leppington", "Lethbridge Park", "Leumeah", "Lewisham", "Liberty Grove", "Lidcombe", "Lilli Pilli", "Lilyfield", "Lindfield", "Linley Point", "Little Bay", "Liverpool", "Llandilo", "Loftus", "Londonderry", "Long Point", "Longueville", "Lower Portland", "Luddenham", "Lugarno", "Lurnea", "Macquarie Fields", "Macquarie Links", "Macquarie Park", "Maianbar", "Malabar", "Manly", "Manly Vale", "Maraylya", "Marayong", "Maroota", "Maroubra", "Marrickville", "Marsden Park", "Marsfield", "Mascot", "Matraville", "Mays Hill", "McCarrs Creek", "McGraths Hill", "McMahons Point", "Meadowbank", "Melrose Park", "Menai", "Menangle Park", "Merrylands", "Merrylands West", "Middle Cove", "Middle Dural", "Middleton Grange", "Miller", "Millers Point", "Milperra", "Milsons Passage", "Milsons Point", "Minchinbury", "Minto", "Minto Heights", "Miranda", "Mona Vale", "Monterey", "Moore Park", "Moorebank", "Mortdale", "Mortlake", "Mosman", "Mount Annan", "Mount Colah", "Mount Druitt", "Mount Kuring-Gai", "Mount Lewis", "Mount Pritchard", "Mount Vernon", "Mulgoa", "Mulgrave", "Narellan Vale", "Naremburn", "Narrabeen", "Narraweena", "Narwee", "Nelson", "Neutral Bay", "Newington", "Newport", "Newtown", "Normanhurst", "North Balgowlah", "North Bondi", "North Curl Curl", "North Epping", "North Manly", "North Narrabeen", "North Parramatta", "North Richmond", "North Rocks", "North Ryde", "North Seaforth", "North St Ives", "North St Marys", "North Strathfield", "North Sydney", "North Turramurra", "North Willoughby", "North Wahroonga", "Northbridge", "Northmead", "Northwood", "Oakhurst", "Oakville", "Oatlands", "Oatley", "Old Guildford", "Old Toongabbie", "Oran Park", "Orchard Hills", "Osborne Park", "Oxford Falls", "Oxley Park", "Oyster Bay", "Paddington", "Padstow", "Padstow Heights", "Pagewood", "Palm Beach", "Panania", "Parklea", "Parramatta", "Peakhurst", "Peakhurst Heights", "Pemulwuy", "Pendle Hill", "Pennant Hills", "Penrith", "Penshurst", "Petersham", "Phillip Bay", "Picnic Point", "Pitt Town", "Pleasure Point", "Plumpton", "Point Piper", "Port Botany", "Potts Hill", "Potts Point", "Prairiewood", "Prestons", "Prospect", "Punchbowl", "Putney", "Pymble", "Pyrmont", "Quakers Hill", "Queens Park", "Queenscliff", "Raby", "Ramsgate", "Ramsgate Beach", "Randwick", "Redfern", "Regents Park", "Regentville", "Revesby", "Revesby Heights", "Rhodes", "Richmond", "Riverstone", "Riverview", "Riverwood", "Rockdale", "Rodd Point", "Rookwood", "Rooty Hill", "Ropes Crossing", "Rose Bay", "Rosebery", "Rosehill", "Roselands", "Rosemeadow", "Roseville", "Roseville Chase", "Rossmore", "Rouse Hill", "Royal National Park", "Rozelle", "Ruse", "Rushcutters Bay", "Russell Lea", "Rydalmere", "Ryde", "Sackville", "Sackville North", "Sadleir", "Sandringham", "Sans Souci", "Scheyville", "Schofields", "Scotland Island", "Seaforth", "Sefton", "Seven Hills", "Shalvey", "Shanes Park", "Silverwater", "Singletons Mill", "Smeaton Grange", "Smithfield", "South Coogee", "South Granville", "South Hurstville", "South Maroota", "South Penrith", "South Turramurra", "South Wentworthville", "South Windsor", "Spring Farm", "St Andrews", "St Clair", "St Helens Park", "St Ives", "St Ives Chase", "St Johns Park", "St Leonards", "St Marys", "St Peters", "Stanhope Gardens", "Stanmore", "Strathfield", "Strathfield South", "Summer Hill", "Surry Hills", "Sutherland", "Sydenham", "Sydney Olympic Park", "Sylvania", "Sylvania Waters", "Tamarama", "Taren Point", "Telopea", "Tempe", "Tennyson Point", "Terrey Hills", "The Ponds", "The Rocks", "Thornleigh", "Toongabbie", "Tregear", "Turramurra", "Turrella", "Ultimo", "Varroville", "Vaucluse", "Villawood", "Vineyard", "Voyager Point", "Wahroonga", "Waitara", "Wakeley", "Wallacia", "Wareemba", "Warrawee", "Warriewood", "Warwick Farm", "Waterfall", "Waterloo", "Watsons Bay", "Wattle Grove", "Waverley", "Waverton", "Weavers", "Wedderburn", "Wentworth Point", "Wentworthville", "Werrington", "Werrington County", "Werrington Downs", "West Hoxton", "West Killara", "West Lindfield", "West Pennant Hills", "West Pymble", "West Ryde", "Westleigh", "Westmead", "Wetherill Park", "Whalan", "Wheeler Heights", "Wiley Park", "Willmot", "Willoughby", "Willoughby East", "Windsor", "Windsor Downs", "Winston Hills", "Wisemans Ferry", "Wolli Creek", "Wollstonecraft", "Woodbine", "Woodcroft", "Woodpark", "Woollahra", "Woolloomooloo", "Woolooware", "Woolwich", "Woronora", "Woronora Heights", "Yagoona", "Yarramundi", "Yarrawarrah", "Yennora", "Yowie Bay", "Zetland"]
suburb = map(lambda x:x.lower(),suburb)
neigh=[]
for i in df.address.str.lower():
    if ver:
        neigh.append(max([w for w in suburb if w in i], key=len))
    else:
        neigh.append(max([w for w in suburb if w in i], key=len, default=None))

df['neigh']= neigh
df.neigh[df.neigh == ""] = df.link[df.neigh == ""].str.split("/").str[4]
df['neigh'] = df.neigh.str.replace("-"," ")
df.neigh = df.neigh.str.replace("sydney city", "sydney")
df.neigh = df.neigh.str.replace("kings cross","potts point")
#df.neigh = df.neigh.str.replace("sydney region","auburn")

# Clean adv text and title

df.text = df.text.apply(' '.join) # turn list  of sentence into one text
df.title = df.title.apply(' '.join)

# identify if adv is available for couples

def detect_couple(x):
    
    text = x[0] 
    title = x[1]
    
    no_couple = bool(re.findall(r"((no |not )(\w+\W+){0,3}couple)", text, flags=re.IGNORECASE))
    
    we_couple = bool(bool(
            re.search(r"((we (\w+\W+){0,3}couple)|(share (\w+\W+){0,3}\b(?!for\b)\w* couple)|([^\.\,]+(\w\W)*(by )(\w+\W){0,4}couple)|(couple( owner)))", 
                                text, flags=re.IGNORECASE)) & (not bool(
                                        re.search(r"(we (prefer|want)((\w+\W+){0,2}) couple)", 
                                                  text, flags=re.IGNORECASE))))

    title_couple = bool(re.search("couple",title, flags=re.IGNORECASE))
        
    couple_times=len(re.findall("couple",text, flags=re.IGNORECASE))
    
    if no_couple:
        return "no_couple"
    elif title_couple:
        return "couple"
    elif (couple_times == 1) & (we_couple):
        return "no_couple"
    elif couple_times > 0:
        return "couple"
    else:
        return "no_couple"

df['couple'] = map(detect_couple,zip(df.text,df.title))

### Load geodata set

import geopandas as gpd

# Clean geoshapes
geo_df = gpd.read_file('./shp/NSW_LOCALITY_POLYGON_shp.shp')
geo_df['neigh'] = geo_df.NSW_LOCA_2.str.lower()
geo_df['neigh'] = geo_df.neigh.str.replace("-"," ")
geo_df.DT_CREATE = pd.to_datetime(geo_df.DT_CREATE)
geo_df = geo_df.loc[geo_df.groupby('neigh').DT_CREATE.idxmax(),:]

#### Create tables, maps and plots

# tables

def filt_table(df,tipos):
    if tipos == None:
        tipos = "All"
    if tipos == "All":
        tt = df[['neigh','price']].groupby('neigh').agg('median').sort_values(by='price')
    else:
        tt = df[['neigh','price']][df.couple==tipos].groupby('neigh').agg('median').sort_values(by='price')
    return tt


# Create the histogram plot

def make_plot(title,measured):
    dfClean = df[measured][df[measured].notnull()]
    hist, edges = np.histogram(dfClean, density=True)
                               #, bins=50)
    #x = np.linspace(0, 400, 1000)
    #pdf = 1/(0.5 * np.sqrt(2*np.pi)) * np.exp(-(x-0)**2 / (2*0.5**2))
#    cdf = (1+scipy.special.erf((x-mu)/np.sqrt(2*sigma**2)))/2
    
    p = figure(title=title, background_fill_color="#fafafa", background_fill_alpha=0 ,
               plot_width=400, plot_height=200,name=title, border_fill_alpha=0)
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color="navy", line_color="white", alpha=0.5)
    p.left[0].formatter.use_scientific = False
    #p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")
#    p.line(x, cdf, line_color="orange", line_width=2, alpha=0.7, legend="CDF")

    p.y_range.start = 0
    #p.legend.location = "center_right"
    #p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = measured
    p.yaxis.axis_label = 'Value'
    p.grid.grid_line_color="white"
    return p

# Create the boxplot
    
# Aux function to find the outliers for each category
def outliers(group, upper,lower):
    cat = group.name
    return group[(group.price > upper.loc[cat]['price']) | (group.price < lower.loc[cat]['price'])]['price']

def make_boxplot(df):
    # find the quartiles and IQR for each category
    groups = df[['neigh','price']].groupby('neigh')
    neigh = df.neigh.unique()
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr
    
    out = groups.apply(lambda x: outliers(x,upper,lower)).dropna()
    
    # prepare outlier data for plotting, we need coordinates for every outlier.
    if not out.empty:
        outx = []
        outy = []
        for keys in out.index:
            outx.append(keys[0])
            outy.append(out.loc[keys[0]].loc[keys[1]])
    
    p = figure(tools="", background_fill_color="#fafafa", background_fill_alpha=0 ,
               plot_width=400, plot_height=200, border_fill_alpha=0,
               x_range=neigh)
    p.left[0].formatter.use_scientific = False
    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1)
    upper.price = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'price']),upper.price)]
    lower.price = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'price']),lower.price)]
    
    # stems
    p.segment(neigh, upper.price, neigh, q3.price, line_color="black")
    p.segment(neigh, lower.price, neigh, q1.price, line_color="black")
    
    # boxes
    p.vbar(neigh, 0.7, q2.price, q3.price, fill_color="#E08E79", line_color="black")
    p.vbar(neigh, 0.7, q1.price, q2.price, fill_color="#3B8686", line_color="black")
    
    # whiskers (almost-0 height rects simpler than segments)
    p.rect(neigh, lower.price, 0.2, 0.01, line_color="black")
    p.rect(neigh, upper.price, 0.2, 0.01, line_color="black")
    
    # outliers
    if not out.empty:
        p.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)
    
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="12pt"
    
    #output_file("boxplot.html", title="boxplot.py example")
    
    return p

# Create the MAP

# merge geoshapes with price data


import folium
import os
import platform

if platform.system() == "Windows":
    os.environ["PROJ_LIB"] = "C:/Users/Cami/Anaconda2/Library/share" #windows

# Aux function to get lon and lat

def getXY(pt):
    return [pt.y, pt.x]


def mapear(tt, ver, geo_df):
    dfg = geo_df.merge(tt, on = 'neigh', how ='left')
    dfg = dfg.dropna(subset=['price'])
    
    centroidseries = dfg['geometry'].centroid
    dfg['centroidlist'] = list(map(getXY, centroidseries))
    
    dfg = dfg.drop('DT_CREATE',axis=1)
    
    mapa = folium.Map(location=[-33.8473567,150.651782],
                      tiles='Stamen Toner')
    if ver:
        mapa.choropleth(geo_data=dfg,
                        data=dfg,
                        columns=['neigh','price'], key_on = 'feature.properties.neigh', fill_color = 'Spectral',
                        threshold_scale=[0,100,150, 200, 300, 400], fill_opacity = 0.8)
    else:
        folium.Choropleth(geo_data=dfg,
                          data=dfg,
                          columns=['neigh','price'], key_on = 'feature.properties.neigh', fill_color = 'Spectral',
                          threshold_scale=[0,100,150, 200, 300, 400], fill_opacity = 0.8).add_to(mapa)

    for i in range(0,len(dfg.geometry)):
        folium.Circle(dfg.centroidlist.iloc[i],radius=10,
                      popup=dfg.NSW_LOCA_2.iloc[i]
                      ).add_to(mapa)

    mapa.save('static\map.html')

# Get variables to show as filters

feature_names = df.columns[[3,4,12]].values.tolist()
tipos = df.couple.unique().tolist()
tipos.append("All")

#select1 = Select(title="Option:", value="price", options=feature_names)
#select2 = Select(title="Option:", value="All", options=tipos)

#current_feature_name = None
#current_tipos = "All"

# Index page
@app.route('/')
def index():
    # Determine the selected feature
    current_tipos = request.args.get("tipos")
    if current_tipos == None:
        current_tipos = "All"

    # Create the plots
    # Create price tables
    tt = filt_table(df,current_tipos)
    
    cheapest = tt.head(10)
    expensive = tt.sort_values(by='price', ascending = False).head(10)
    
    tabla1 = cheapest.to_html(header="true", table_id="table1")
    tabla2 = expensive.to_html(header="true", table_id="table2")
    
    mapear(tt, ver, geo_df)

    # Embed plot into HTML via Flask Render
    #script, div = components(plot)
    #script2, div2 = components(plot2)
    
    
    #return render_template("chart.html", script=script, div=div,  script2=script2, div2=div2,
    #                       feature_names=feature_names,  current_feature_name=current_feature_name)
    return render_template("chart.html",
                           feature_names = feature_names, 
                           #current_feature_name=current_feature_name,
                           tabla1 = tabla1, tipos = tipos, current_tipos = current_tipos,
                           tabla2 = tabla2)

@app.route('/plot')
def plot():
    #global current_feature_name
    #if current_feature_name == None:
    current_feature_name = "price"
    plot = make_plot("histogram", current_feature_name)
    return json.dumps(json_item(plot, "histogram"))

@app.route('/plot2')
def plot2():
    plot2 = make_boxplot(df)
    return json.dumps(json_item(plot2,"graph"))
                      


if __name__ == "__main__":
    app.run(debug=True)