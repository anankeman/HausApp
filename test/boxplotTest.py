# -*- coding: utf-8 -*-
"""
Created on Mon Feb 04 18:14:25 2019

@author: Cami
"""
from bokeh.plotting import figure, show, output_file


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
    
    p = figure(tools="", background_fill_color="#efefef", x_range=neigh, toolbar_location=None)
    
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