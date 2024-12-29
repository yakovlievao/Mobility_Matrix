import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import base64
from sklearn.linear_model import LinearRegression
import numpy as np
import dash
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go


# plot 1 (car sales)



car_sales = pd.read_csv('./data/car_sales.csv')

# use melt() for plotting

car_sales_melted = car_sales.melt(
                                id_vars = 'million_units' ,
                                var_name = 'year' ,
                                value_name = 'units'
)

# filter the data for each category
global_sales = car_sales_melted[car_sales_melted['million_units'] == 'global_car_sales']
us_sales = car_sales_melted[car_sales_melted['million_units'] == 'us_car_sales']
europe_sales = car_sales_melted[car_sales_melted['million_units'] == 'europe_car_sales']

# Create the figure

car_sales_fig = go.Figure()

# add global sales as line chart

car_sales_fig.add_trace(go.Scatter(
                    x = global_sales['year'] ,
                    y = global_sales['units'] ,
                    mode = 'lines+markers' ,  
                    name = 'Global' ,
                    line = dict(color = '#26518e') ,
                    hovertemplate = 'Year: %{x}<br>Global Sales: %{y} million<extra></extra>'
                    )
)

# add US sales as a bar chart

car_sales_fig.add_trace(go.Bar(
                x = us_sales['year'] ,
                y = us_sales['units'] ,
                name = 'United States' ,
                marker_color = '#cc1f1f' ,
                hovertemplate = 'Year: %{x}<br>US Sales: %{y} million<extra></extra>'
                )
)

# add Europe sales as a bar chart

car_sales_fig.add_trace(go.Bar(
                x = europe_sales['year'] ,
                y = europe_sales['units'] ,
                name = 'Europe' ,
                marker_color = '#27a920' ,
                hovertemplate = 'Year: %{x}<br>Europe Sales: %{y} million<extra></extra>'
                )
)

# Customize layout

car_sales_fig.update_layout(
                title = 'Car Sales' ,
                xaxis = dict(
                            title = 'year' , 
                            tickmode = 'linear' ,
                            showgrid = True , 
                            gridcolor = 'white'
                        ) ,
                yaxis = dict(
                            title = 'units sold' ,
                            ticksuffix = 'M' ,
                            showgrid = True , 
                            gridcolor = 'white'
                        ) ,
                barmode = 'group' ,  # Bars are grouped side by side
                plot_bgcolor = '#BDC3C7' ,
                paper_bgcolor = '#2C3E50' ,
                width = 700 ,
                height = 500 ,
                legend = dict(title = "Sales Category") ,
                font = dict(
                        family = 'PT Sans Narrow' ,
                        size = 16 ,
                        color = '#ECF0F1'
                        )
)



#market shares plots (scatter)



# function to encode images in base64

def encode_image(image_path):
    # open(image_path, "rb"): opens the image file in binary mode (rb = read binary)

    with open(image_path, "rb") as image_file:

        # image_file.read(): reads the entire file content
        # base64.b64encode(): encodes the binary content into a base64 string
        # "data:image/png;base64,": adds a prefix to tell the browser this is an embedded PNG image.
        # .decode(): converts the base64 binary string into a regular string for Plotly

        return "data:image/png;base64," + base64.b64encode(image_file.read()).decode()


# plot 2 (market share global)



global_market_share = pd.read_csv('./data/global_market_share.csv')



global_market_share = global_market_share.melt(
                                            id_vars = ['company' , 'image'] ,
                                            var_name = 'year' , 
                                            value_name = 'value'
                                        )

# encode the images in the df

global_market_share['image'] = global_market_share['image'].apply(encode_image)

# initialize the figure

global_market_share_fig = go.Figure()

# get unique years

years_gms = sorted(global_market_share['year'].unique())

# add scatter trace for hover functionality (starting frame)

initial_year_gms = years_gms[0] # picks the first year in the sorted list (e.g., 2015)
initial_data_gms = global_market_share[global_market_share['year'] == initial_year_gms] # filters the df to include only rows where year == initial_year

# add a scatter plot for the first year’s data (e.g., 2015)

global_market_share_fig.add_trace(go.Scatter(
                                    x = initial_data_gms['company'] , # company names are on the x-axis
                                    y = initial_data_gms['value'] ,  # market share values are on the y-axis
                                    mode = 'markers' ,  # displays invisible markers
                                    marker = dict(size = 10 , color = 'rgba(0,0,0,0)') ,  # invisible markers are added for hover functionality.
                                    text = [
                                            f"{row['company']}<br>{row['value']}% Market Share" # list comprehension generates hover text for each company.
                                            for _ , row in initial_data_gms.iterrows()
                                        ] ,
                                    hoverinfo = 'text'
                                    )
)

# Add animation frames

frames = []

# loops through each year in the sorted list of years

for year in years_gms:

    # filters the df (year_data) for rows corresponding to the current year

    year_data = global_market_share[global_market_share['year'] == year]
    
    # scatter trace for the current frame

    scatter = go.Scatter(
                    x = year_data['company'] ,
                    y = year_data['value'] , 
                    mode = 'markers' ,
                    marker = dict(size = 10 , color = 'rgba(0,0,0,0)') ,
                    text = [
                        f"{row['company']}<br>{row['value']}% Market Share<br>{row['year']}"
                        for _ , row in year_data.iterrows()
                    ] ,
                    hoverinfo = 'text'
    )
    
    # add images dynamically to the frame
    images = [
        go.layout.Image(
                    source = row['image'] ,    # uses the base64-encoded image
                    x = row['company'] ,       # places the image at the company’s x-coordinate 
                    y = row['value'] ,         # places the image at market share y-coordinate.
                    xref = 'x' ,
                    yref = 'y' ,
                    sizex = 2 ,              # size of images on x-axis
                    sizey = 2 ,              # size of images on y-axis
                    xanchor = 'center' ,       # centers the image at the specified coordinates
                    yanchor = 'middle'         # centers the image at the specified coordinates
                    )   
        for _ , row in year_data.iterrows()
    ]
    
    # add the year annotation dynamically to each frame

    annotation = dict(
                    x = 0.5 , 
                    y = 1.1 ,
                    text = f'<b>{year}</b>' ,
                    showarrow = False ,
                    xref = 'paper' ,
                    yref = 'paper' ,
                    font = dict(
                            family = 'PT Sans Narrow' , 
                            size = 20 , 
                            color = '#ECF0F1'
                            ) ,
                    align = 'center'
    )
    
    # combine the scatter plot, images, and annotation into a single frame

    frames.append(go.Frame(
                        data = [scatter] ,
                        layout = dict(
                                    images = images , 
                                    annotations = [annotation]
                                ) ,
                        name = str(year)
                        )
    )

# add all frames to the figure

global_market_share_fig.frames = frames

# add play and pause buttons for the animation

global_market_share_fig.update_layout(
                                updatemenus = [
                                    {
                                        'buttons' : [
                                            {                                                       #'Play' : starts cycling through the frames
                                                'args' : [None , {'frame' : {'duration' : 1000 ,    # at a speed of 1 frame per second 
                                                                            'redraw' : True} ,       
                                                                            'fromcurrent' : True}] ,
                                                'label' : 'Play' ,
                                                'method' : 'animate'
                                            } ,
                                            {                                                                       #'Pause' : stops the animation
                                                'args' : [[None] , {'frame' : {'duration' : 0 , 'redraw' : True} , 
                                                                    'mode' : 'immediate' , 
                                                                    'transition' : {'duration' : 0}}
                                                        ] ,
                                                'label' : 'Pause' ,
                                                'method' : 'animate'
                                            }
                                        ] ,
                                        'direction' : 'left' ,
                                        'pad' : {'r' : 10 , 't' : 87} ,
                                        'showactive' : False ,
                                        'type' : 'buttons' ,
                                        'x' : 0.1 ,
                                        'xanchor' : 'right' ,
                                        'y' : 0 ,
                                        'yanchor' : 'top'
                                    }
                                ]
)

# set layout properties

global_market_share_fig.update_layout(
                                title = 'Global Market Shares' ,
                                xaxis = dict(title = 'company') ,
                                yaxis = dict(
                                            title = 'market share' ,
                                            range = [0 , 21] ,
                                            tickmode = 'linear' ,
                                            tick0 = 0 ,
                                            dtick = 3 ,
                                            ticksuffix = '%'
                                        ) ,
                                plot_bgcolor = '#BDC3C7' ,
                                paper_bgcolor = '#2C3E50' ,
                                font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                        ) ,
                                width = 700 ,
                                height = 700
)




# plot 3 (us market shares)



us_market_share = pd.read_csv('./data/us_market_share.csv')

us_market_share = us_market_share.melt(
                                    id_vars = ['company' , 'image'] , 
                                    var_name = 'year' , 
                                    value_name = 'value'
                    )

# encode the images in the df

us_market_share['image'] = us_market_share['image'].apply(encode_image)

# initialize the figure

us_market_share_fig = go.Figure()

# get unique years

years_usms = sorted(us_market_share['year'].unique())

# add scatter trace for hover functionality (starting frame)

initial_year_usms = years_usms[0] # picks the first year in the sorted list (e.g., 2015)
initial_data_usms = us_market_share[us_market_share['year'] == initial_year_usms] # filters the df to include only rows where year == initial_year

# add a scatter plot for the first year’s data (e.g., 2015)

us_market_share_fig.add_trace(go.Scatter(
                                    x = initial_data_usms['company'] , # company names are on the x-axis
                                    y = initial_data_usms['value'] ,  # market share values are on the y-axis
                                    mode = 'markers' ,  # displays invisible markers
                                    marker = dict(size = 10 , color = 'rgba(0,0,0,0)') ,  # invisible markers are added for hover functionality.
                                    text = [
                                            f"{row['company']}<br>{row['value']}% Market Share" # list comprehension generates hover text for each company.
                                            for _ , row in initial_data_usms.iterrows()
                                        ] ,
                                    hoverinfo = 'text'
                                    )
)

# Add animation frames

frames = []

# loops through each year in the sorted list of years

for year in years_usms:

    # filters the df (year_data) for rows corresponding to the current year

    year_data = us_market_share[us_market_share['year'] == year]
    
    # scatter trace for the current frame

    scatter = go.Scatter(
                    x = year_data['company'] ,
                    y = year_data['value'] , 
                    mode = 'markers' ,
                    marker = dict(size = 10 , color = 'rgba(0,0,0,0)') ,
                    text = [
                        f"{row['company']}<br>{row['value']}% Market Share<br>{row['year']}"
                        for _ , row in year_data.iterrows()
                    ] ,
                    hoverinfo = 'text'
    )
    
    # add images dynamically to the frame
    images = [
        go.layout.Image(
                    source = row['image'] ,    # uses the base64-encoded image
                    x = row['company'] ,       # places the image at the company’s x-coordinate 
                    y = row['value'] ,         # places the image at market share y-coordinate.
                    xref = 'x' ,
                    yref = 'y' ,
                    sizex = 1.5 ,              # size of images on x-axis
                    sizey = 1.5 ,              # size of images on y-axis
                    xanchor = 'center' ,       # centers the image at the specified coordinates
                    yanchor = 'middle'         # centers the image at the specified coordinates
                    )   
        for _ , row in year_data.iterrows()
    ]
    
    # add the year annotation dynamically to each frame

    annotation = dict(
                    x = 0.5 , 
                    y = 1.1 ,
                    text = f'<b>{year}</b>' ,
                    showarrow = False ,
                    xref = 'paper' ,
                    yref = 'paper' ,
                    font = dict(
                            family = 'PT Sans Narrow' , 
                            size = 20 , 
                            color = '#ECF0F1'
                            ) ,
                    align = 'center'
    )
    
    # combine the scatter plot, images, and annotation into a single frame

    frames.append(go.Frame(
                        data = [scatter] ,
                        layout = dict(
                                    images = images , 
                                    annotations = [annotation]
                                ) ,
                        name = str(year)
                        )
    )

# add all frames to the figure

us_market_share_fig.frames = frames

# add play and pause buttons for the animation

us_market_share_fig.update_layout(
                                updatemenus = [
                                    {
                                        'buttons' : [
                                            {                                                       #'Play' : starts cycling through the frames
                                                'args' : [None , {'frame' : {'duration' : 1000 ,    # at a speed of 1 frame per second 
                                                                            'redraw' : True} ,       
                                                                            'fromcurrent' : True}
                                                        ] ,
                                                'label' : 'Play' ,
                                                'method' : 'animate'
                                            } ,
                                            {                                                                       #'Pause' : stops the animation
                                                'args' : [[None] , {'frame' : {'duration' : 0 , 'redraw' : True} , 
                                                                    'mode' : 'immediate' , 
                                                                    'transition' : {'duration' : 0}}
                                                        ] ,
                                                'label' : 'Pause' ,
                                                'method' : 'animate'
                                            }
                                        ] ,
                                        'direction' : 'left' ,
                                        'pad' : {'r' : 10 , 't' : 87} ,
                                        'showactive' : False ,
                                        'type' : 'buttons' ,
                                        'x' : 0.1 ,
                                        'xanchor' : 'right' ,
                                        'y' : 0 ,
                                        'yanchor' : 'top'
                                    }
                                ]
)

# set layout properties

us_market_share_fig.update_layout(
                                title = 'United States Market Shares' ,
                                xaxis = dict(title = 'company') ,
                                yaxis = dict(
                                            title = 'market share' ,
                                            range = [0 , 17] ,
                                            tickmode = 'linear' ,
                                            tick0 = 0 ,
                                            dtick = 3 ,
                                            ticksuffix = '%'
                                        ) ,
                                plot_bgcolor = '#BDC3C7' ,
                                paper_bgcolor = '#2C3E50' ,
                                font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                        ) ,
                                width = 700 ,
                                height = 700
)



# plot 4 (europe market share)



europe_market_share = pd.read_csv('./data/europe_market_share.csv')

europe_market_share = europe_market_share.melt(
                                    id_vars = ['company' , 'image'] , 
                                    var_name = 'year' , 
                                    value_name = 'value'
                    )

# encode the images in the df

europe_market_share['image'] = europe_market_share['image'].apply(encode_image)

# initialize the figure

europe_market_share_fig = go.Figure()

# get unique years

years_ems = sorted(europe_market_share['year'].unique())

# add scatter trace for hover functionality (starting frame)

initial_year_ems = years_ems[0] # picks the first year in the sorted list (e.g., 2015)
initial_data_ems = europe_market_share[europe_market_share['year'] == initial_year_ems] # filters the df to include only rows where year == initial_year

# add a scatter plot for the first year’s data (e.g., 2015)

europe_market_share_fig.add_trace(go.Scatter(
                                        x = initial_data_ems['company'] , # company names are on the x-axis
                                        y = initial_data_ems['value'] ,  # market share values are on the y-axis
                                        mode = 'markers' ,  # displays invisible markers
                                        marker = dict(size = 10 , color = 'rgba(0,0,0,0)') ,  # invisible markers are added for hover functionality.
                                        text = [
                                                f"{row['company']}<br>{row['value']}% Market Share" # list comprehension generates hover text for each company.
                                                for _ , row in initial_data_ems.iterrows()
                                            ] ,
                                        hoverinfo = 'text'
                                        )
)

# Add animation frames

frames = []

# loops through each year in the sorted list of years

for year in years_ems:

    # filters the df (year_data) for rows corresponding to the current year

    year_data = europe_market_share[europe_market_share['year'] == year]
    
    # scatter trace for the current frame

    scatter = go.Scatter(
                    x = year_data['company'] ,
                    y = year_data['value'] , 
                    mode = 'markers' ,
                    marker = dict(size = 10 , color = 'rgba(0,0,0,0)') ,
                    text = [
                        f"{row['company']}<br>{row['value']}% Market Share<br>{row['year']}"
                        for _ , row in year_data.iterrows()
                    ] ,
                    hoverinfo = 'text'
    )
    
    # add images dynamically to the frame
    images = [
        go.layout.Image(
                    source = row['image'] ,    # uses the base64-encoded image
                    x = row['company'] ,       # places the image at the company’s x-coordinate 
                    y = row['value'] ,         # places the image at market share y-coordinate.
                    xref = 'x' ,
                    yref = 'y' ,
                    sizex = 3 ,              # size of images on x-axis
                    sizey = 3 ,              # size of images on y-axis
                    xanchor = 'center' ,       # centers the image at the specified coordinates
                    yanchor = 'middle'         # centers the image at the specified coordinates
                    )   
        for _ , row in year_data.iterrows()
    ]
    
    # add the year annotation dynamically to each frame

    annotation = dict(
                    x = 0.5 , 
                    y = 1.1 ,
                    text = f'<b>{year}</b>' ,
                    showarrow = False ,
                    xref = 'paper' ,
                    yref = 'paper' ,
                    font = dict(
                            family = 'PT Sans Narrow' , 
                            size = 20 , 
                            color = '#ECF0F1'
                            ) ,
                    align = 'center'
    )
    
    # combine the scatter plot, images, and annotation into a single frame

    frames.append(go.Frame(
                        data = [scatter] ,
                        layout = dict(
                                    images = images , 
                                    annotations = [annotation]
                                ) ,
                        name = str(year)
                        )
    )

# add all frames to the figure

europe_market_share_fig.frames = frames

# add play and pause buttons for the animation

europe_market_share_fig.update_layout(
                                    updatemenus = [
                                        {
                                            'buttons' : [
                                                {                                                       #'Play' : starts cycling through the frames
                                                    'args' : [None , {'frame' : {'duration' : 1000 ,    # at a speed of 1 frame per second 
                                                                                'redraw' : True} ,       
                                                                                'fromcurrent' : True}] ,
                                                    'label' : 'Play' ,
                                                    'method' : 'animate'
                                                } ,
                                                {                                                                       #'Pause' : stops the animation
                                                    'args' : [[None] , {'frame' : {'duration' : 0 , 'redraw' : True} , 
                                                                        'mode' : 'immediate' , 
                                                                        'transition' : {'duration' : 0}}
                                                            ] ,
                                                    'label' : 'Pause' ,
                                                    'method' : 'animate'
                                                }
                                            ] ,
                                            'direction' : 'left' ,
                                            'pad' : {'r' : 10 , 't' : 87} ,
                                            'showactive' : False ,
                                            'type' : 'buttons' ,
                                            'x' : 0.1 ,
                                            'xanchor' : 'right' ,
                                            'y' : 0 ,
                                            'yanchor' : 'top'
                                        }
                                    ]
)

# set layout properties

europe_market_share_fig.update_layout(
                                    title = 'Europe Market Shares' ,
                                    xaxis = dict(title = 'company') ,
                                    yaxis = dict(
                                                title = 'market share' ,
                                                range = [0 , 31] ,
                                                tickmode = 'linear' ,
                                                tick0 = 0 ,
                                                dtick = 3 ,
                                                ticksuffix = '%'
                                            ) ,
                                    plot_bgcolor = '#BDC3C7' ,
                                    paper_bgcolor = '#2C3E50' ,
                                    font = dict(
                                            family = 'PT Sans Narrow' ,
                                            size = 16 ,
                                            color = '#ECF0F1'
                                            ) ,
                                    width = 700 ,
                                    height = 700
)



# comparising plots

# plot 5 (sales by category GB3)



audi_sales = pd.read_csv('./data/audi_sales.csv')
bmw_sales = pd.read_csv('./data/bmw_sales.csv')
mercedes_sales = pd.read_csv('./data/mercedes_sales.csv')

# melting the dfs to long format and adding column 'brand'

audi_sales_melted = audi_sales.melt(
                                id_vars = ['category'] , 
                                var_name = 'year' , 
                                value_name = 'volume'
                    )

audi_sales_melted['brand'] = 'Audi'

bmw_sales_melted = bmw_sales.melt(
                                id_vars = ['category'] , 
                                var_name = 'year' , 
                                value_name  ='volume'
                    )

bmw_sales_melted['brand'] = 'BMW'

mercedes_sales_melted = mercedes_sales.melt(
                                        id_vars = ['category'] , 
                                        var_name = 'year' , 
                                        value_name = 'volume'
                        )

mercedes_sales_melted['brand'] = 'Mercedes-Benz'

# combining all sales data into a single df

big_three_sales = pd.concat([audi_sales_melted , bmw_sales_melted , mercedes_sales_melted])

# creating the stacked bar chart (using Plotly Express)

big_three_sales_fig = px.bar(
                            big_three_sales,  
                            x = 'year' , 
                            y = 'volume' , 
                            color = 'brand' , 
                            color_discrete_map = {
                                                'Audi' : '#F50537' ,
                                                'BMW' : '#007eed' ,
                                                'Mercedes-Benz' : '#7a8084'
                                            } ,
                            #  facet_col='brand'

                            title = 'Total Sales by Year and Company' ,
                            hover_data = ['category' , 'brand' , 'volume'] ,
                            labels = {'volume' : 'sales volume' , 'year' : 'year' , 'category' : 'category'} ,
                            barmode = 'group'
                        )

# update layout 

big_three_sales_fig.update_layout(
                                xaxis_title = 'year' ,
                                yaxis_title = 'total sales volume' ,
                                legend_title = 'Company' ,
                                template = 'plotly' ,
                                xaxis = dict(type = 'category') ,
                                yaxis = dict(
                                            tickmode = 'linear',  # set tick mode to linear
                                            tick0 = 0,            # start ticks at 0
                                            dtick = 300000,            # step size of 100000
                                            range = [0, 2500000]
                                        ) ,
                                plot_bgcolor = '#BDC3C7' ,
                                paper_bgcolor = '#2C3E50' ,
                                font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                        ) ,
                                width = 700 , 
                                height = 500        
)

# formatting hovertemplate

big_three_sales_fig.update_traces(
                                hovertemplate = (
                                                '<b>Brand:</b> %{customdata[1]}<br>'
                                                '<b>Year:</b> %{x}<br>'
                                                '<b>Category:</b> %{customdata[0]}<br>'
                                                '<b>Sales Volume:</b> %{y:,} units'
                                            )
)



# plot 6 (sales by category T&V)



toyota_sales = pd.read_csv('./data/toyota_sales.csv')
vw_sales = pd.read_csv('./data/volkswagen_sales.csv')

# melting the dfs to long format and adding column 'brand'

toyota_sales_melted = toyota_sales.melt(
                                    id_vars = ['category'] , 
                                    var_name = 'year' , 
                                    value_name = 'volume'
                    )

toyota_sales_melted['brand'] = 'Toyota'

vw_sales_melted = vw_sales.melt(
                            id_vars = ['category'] , 
                            var_name = 'year' , 
                            value_name = 'volume'
                )

vw_sales_melted['brand'] = 'Volkswagen'

# combining all sales data into a single df

sales_tv = pd.concat([toyota_sales_melted , vw_sales_melted])

# creating the stacked bar chart (using Plotly Express)

sales_tv_fig = px.bar(sales_tv,  
                            x = 'year' , 
                            y = 'volume' , 
                            color = 'brand' , 
                            color_discrete_map = {
                                                'Toyota' : '#EB0A1E' ,
                                                'Volkswagen' : '#6091C3'
                                            } ,
                            title = 'Total Sales by Year and Company' ,
                            hover_data = ['category' , 'brand' , 'volume'] ,
                            labels = {'volume' : 'Total Sales Volume' , 'year' : 'Year' , 'category' : 'Category'} ,
                            barmode = 'group'
)

sales_tv_fig.update_layout(
                        xaxis_title = 'year' ,
                        yaxis_title = 'total sales volume' ,
                        legend_title = 'Company' ,
                        template = 'plotly' ,
                        xaxis = dict(type = 'category') ,
                        yaxis = dict(
                                    tickmode = 'linear',       # set tick mode to linear
                                    tick0 = 0,                 # start ticks at 0
                                    dtick = 800000,            # step size of 800000
                                    range = [0, 11000000]
                                ) ,
                        plot_bgcolor = '#BDC3C7' ,
                        paper_bgcolor = '#2C3E50' ,
                        font = dict(
                                    family = 'PT Sans Narrow' ,
                                    size = 16 ,
                                    color = '#ECF0F1'
                                ) ,
                        width = 700 , 
                        height = 500
)

# formatting hovertemplate

sales_tv_fig.update_traces(
                        hovertemplate = (
                                        '<b>Brand:</b> %{customdata[1]}<br>'
                                        '<b>Year:</b> %{x}<br>'
                                        '<b>Category:</b> %{customdata[0]}<br>'
                                        '<b>Sales Volume:</b> %{y:,} units'
                                    )
)



# plot 7 (revenue BG3)



audi_revenue = pd.read_csv('./data/audi_revenue.csv')
bmw_revenue = pd.read_csv('./data/bmw_revenue.csv')
mercedes_revenue = pd.read_csv('./data/mercedes_revenue.csv')

# filter rows for 'Revenue'

a_revenue = audi_revenue[audi_revenue['category'] == 'revenue_(euro_billion)']
b_revenue = bmw_revenue[bmw_revenue['category'] == 'revenue_(euro_billion)']
m_revenue = mercedes_revenue[mercedes_revenue['category'] == 'revenue_(euro_billion)']

# prepare data for plotting
years_bg3r = a_revenue.columns[1:]                   # skip the 'category' column
audi_values_r = a_revenue.iloc[0 , 1:].values         # get values for Audi
bmw_values_r = b_revenue.iloc[0 , 1:].values          # get values for BMW
mercedes_values_r = m_revenue.iloc[0 , 1:].values     # get values for Mercedes

revenue_bg3_fig = go.Figure()

# Audi's revenue line

revenue_bg3_fig.add_trace(go.Scatter(
                                    x = years_bg3r ,
                                    y = audi_values_r ,
                                    mode = 'lines+markers' ,
                                    name = 'Audi' ,
                                    line_color = '#F50537' ,
                                    line_width = 3 ,
                                    marker = dict(size = 10, symbol = 'circle')
                                )
)

# BMW's revenue line

revenue_bg3_fig.add_trace(go.Scatter(
                                    x = years_bg3r ,
                                    y = bmw_values_r ,
                                    mode = 'lines+markers' ,
                                    name = 'BMW' ,
                                    line_color = '#007eed' ,
                                    line_width = 3 ,
                                    marker = dict(size = 10, symbol = 'circle')
                                )
)


# Mercedes's revenue line


revenue_bg3_fig.add_trace(go.Scatter(
                                    x = years_bg3r ,
                                    y = mercedes_values_r ,
                                    mode = 'lines+markers' ,
                                    name = 'Mercedes-Benz' ,
                                    line_color = '#7a8084' ,
                                    line_width = 3 ,
                                    marker = dict(size = 10, symbol = 'circle')
                                )
)

# customize layout

revenue_bg3_fig.update_layout(
                            title = 'Revenue: German Big Three' ,
                            xaxis_title = 'year' ,
                            yaxis_title = 'revenue' ,
                            legend_title = 'company' ,
                            template = 'plotly' ,
                            xaxis = dict(
                                        tickformat = '%Y' ,                       # format x-axis for years
                                        showgrid = True , 
                                        gridcolor = 'white'
                                    ) ,                   
                            yaxis = dict(
                                        tickprefix = '€' ,                         # add € prefix
                                        ticksuffix = 'B' ,                         # add B suffix
                                        showgrid = True , 
                                        gridcolor = 'white'
                                    ) ,
                            width = 700 ,
                            height = 500 ,
                            plot_bgcolor = '#BDC3C7' ,
                            paper_bgcolor = '#2C3E50' ,
                            font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                    )         

)



# plot 8 (revenue growth BG3)



# filter rows for 'Revenue growth'

a_growth = audi_revenue[audi_revenue['category'] == 'revenue_growth_(%)']
b_growth = bmw_revenue[bmw_revenue['category'] == 'revenue_growth_(%)']
m_growth = mercedes_revenue[mercedes_revenue['category'] == 'revenue_growth_(%)']

# prepare data for plotting

years_bg3rg = a_growth.columns[1:]                  # skip the 'category' column
audi_values_rg = a_growth.iloc[0 , 1:].values       # get values for Audi
bmw_values_rg = b_growth.iloc[0 , 1:].values        # get values for BMW
mercedes_values_rg = m_growth.iloc[0 , 1:].values   # get values for Mercedes

# plot

revenue_growth_bg3_fig = go.Figure()

# Audi's revenue line

revenue_growth_bg3_fig.add_trace(go.Scatter(
                                            x = years_bg3rg ,
                                            y = audi_values_rg ,
                                            mode = 'lines+markers' ,
                                            name = 'Audi' ,
                                            line_color = '#F50537' ,
                                            line_width = 3 ,
                                            marker = dict(size = 10, symbol = 'circle')
                                        )
)

# BMW's revenue line

revenue_growth_bg3_fig.add_trace(go.Scatter(
                                            x = years_bg3rg ,
                                            y = bmw_values_rg ,
                                            mode = 'lines+markers' ,
                                            name = 'BMW' ,
                                            line_color = '#007eed' ,
                                            line_width = 3 ,
                                            marker = dict(size = 10, symbol = 'circle')
                                        )
)

# Mercedes's revenue line

revenue_growth_bg3_fig.add_trace(go.Scatter(
                                            x = years_bg3rg ,
                                            y = mercedes_values_rg ,
                                            mode = 'lines+markers' ,
                                            name = 'Mercedes-Benz' ,
                                            line_color = '#7a8084' ,
                                            line_width = 3 ,
                                            marker = dict(size = 10, symbol = 'circle')
                                        )
)

# customize layout

revenue_growth_bg3_fig.update_layout(
                                    title = 'Revenue growth: German Big Three' ,
                                    xaxis_title = 'year' ,
                                    yaxis_title = 'revenue growth %' ,
                                    legend_title = 'company' ,
                                    template = 'plotly' ,
                                    xaxis = dict(
                                                tickformat = '%Y' ,          # format x-axis for years
                                                showgrid = True , 
                                                gridcolor = 'white'
                                            ) , 
                                    yaxis = dict(
                                                ticksuffix = '%' ,           # add % suffix
                                                showgrid = True , 
                                                gridcolor = 'white'
                                            ) ,
                                    width = 700 ,
                                    height = 500 ,
                                    plot_bgcolor = '#BDC3C7' ,
                                    paper_bgcolor = '#2C3E50' ,
                                    font = dict(
                                                family = 'PT Sans Narrow' ,
                                                size = 16 ,
                                                color = '#ECF0F1'
                                            )       
)



# plot 9 (revenue T&V)



toyota_revenue = pd.read_csv('./data/toyota_revenue.csv')
vw_revenue = pd.read_csv('./data/volkswagen_revenue.csv')

# filter rows for 'revenue'

t_revenue = toyota_revenue[toyota_revenue['category'] == 'revenue_(euro_billion)']
v_revenue = vw_revenue[vw_revenue['category'] == 'revenue_(euro_billion)']

# prepare data for plotting

years_tvr = t_revenue.columns[1:]                   # skip the 'category' column
toyota_values_r = t_revenue.iloc[0 , 1:].values     # get values for Toyota
vw_values_r = v_revenue.iloc[0 , 1:].values         # get values for Volkswagen

# plot

revenue_tv_fig = go.Figure()

# Toyota's revenue line

revenue_tv_fig.add_trace(go.Scatter(
                                    x = years_tvr ,
                                    y = toyota_values_r ,
                                    mode = 'lines+markers' ,
                                    name = 'Toyota' ,
                                    line_color = '#EB0A1E' ,
                                    line_width = 3 ,
                                    marker = dict(size = 10, symbol = 'circle')
                                )
)

# Volkswagen's revenue line

revenue_tv_fig.add_trace(go.Scatter(
                                    x = years_tvr ,
                                    y = vw_values_r ,
                                    mode = 'lines+markers' ,
                                    name = 'Volkswagen' ,
                                    line_color = '#6091C3' ,
                                    line_width = 3 ,
                                    marker = dict(size = 10, symbol = 'circle')
                                )
)

# customize layout

revenue_tv_fig.update_layout(
                            title = 'Revenue: Toyota vs Volkswagen' ,
                            xaxis_title = 'year' ,
                            yaxis_title = 'revenue' ,
                            legend_title = 'company' ,
                            template = 'plotly' ,
                            xaxis = dict(
                                        tickformat = '%Y' , 
                                        showgrid = True , 
                                        gridcolor = 'white'
                                    ) , 
                            yaxis = dict(
                                        tickprefix = '€' , 
                                        ticksuffix = 'B' , 
                                        showgrid = True , 
                                        gridcolor = 'white'
                                    ) ,
                            width = 700 ,
                            height = 500 , 
                            plot_bgcolor = '#BDC3C7' ,
                            paper_bgcolor = '#2C3E50' ,
                            font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                    )             
)



# plot 10 (revenue growth T&V)



# filter rows for 'Revenue Growh'

t_growth = toyota_revenue[toyota_revenue['category'] == 'revenue_growth_(%)']
v_growth = vw_revenue[vw_revenue['category'] == 'revenue_growth_(%)']

# prepare data for plotting

years_tvrg = t_growth.columns[1:]                   # skip the 'category' column
toyota_values_rg = t_growth.iloc[0 , 1:].values     # get values for Toyota
vw_values_rg = v_growth.iloc[0 , 1:].values         # get values for Volkswagen

# plot

revenue_growth_tv_fig = go.Figure()

# Toyota's revenue growth line

revenue_growth_tv_fig.add_trace(go.Scatter(
                                        x = years_tvrg ,
                                        y = toyota_values_rg ,
                                        mode = 'lines+markers' ,
                                        name = 'Toyota' ,
                                        line_color = '#EB0A1E' ,
                                        line_width = 3 ,
                                        marker = dict(size = 10, symbol = 'circle')
                                    )
)

# Volkswagen's revenue growth line

revenue_growth_tv_fig.add_trace(go.Scatter(
                                        x = years_tvrg ,
                                        y = vw_values_rg ,
                                        mode = 'lines+markers' ,
                                        name = 'Volkswagen' ,
                                        line_color = '#6091C3' ,
                                        line_width = 3 ,
                                        marker = dict(size = 10, symbol = 'circle')
                                    )
)

# customize layout

revenue_growth_tv_fig.update_layout(
                                    title = 'Revenue Growth: Toyota vs Volkswagen' ,
                                    xaxis_title = 'year' ,
                                    yaxis_title = 'revenue growth %' ,
                                    legend_title = 'company' ,
                                    template = 'plotly' ,
                                    xaxis = dict(
                                                tickformat = '%Y' ,
                                                showgrid = True , 
                                                gridcolor = 'white'
                                            ) , 
                                    yaxis = dict(
                                                ticksuffix = '%' ,
                                                showgrid = True , 
                                                gridcolor = 'white'
                                            ) ,
                                    width = 700 ,
                                    height = 500 , 
                                    plot_bgcolor = '#BDC3C7' ,
                                    paper_bgcolor = '#2C3E50' ,
                                    font = dict(
                                                family = 'PT Sans Narrow' ,
                                                size = 16 ,
                                                color = '#ECF0F1'
                                            )            
)



# plot 11 (total registration by company)



total_reg_germany = pd.read_csv('./data/total_reg_germany.csv')

# using melt() to transform the year columns into rows for plotting

total_reg_melted = total_reg_germany.melt(
                                        id_vars = 'brand' ,
                                        var_name = 'year' ,
                                        value_name = 'value'
                    )

# plot

total_reg_fig = px.line(
                        total_reg_melted ,
                        x = 'year' ,
                        y = 'value' ,
                        color = 'brand' ,
                        title = 'Total registrated cars in Germany (2015-2023)' ,
                        labels = {
                            'brand' : 'brand' , 
                            'value' : 'amount of units'
                            } ,
                        color_discrete_map = {
                                        'audi': '#F50537',
                                        'bmw': '#007eed',
                                        'mercedes': '#697c85' ,
                                        'toyota' : '#000000' ,
                                        'volkswagen' : '#1F2F57'
                                        }    
)

# adjusting line appearance

total_reg_fig.update_traces(
                            line_width = 3 ,
                            mode = 'lines+markers' , 
                            marker = dict(size = 10 , symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Amount of units: %{y}'
)

total_reg_fig.update_layout(
                xaxis = dict(showgrid = True, gridcolor = 'white') ,
                yaxis = dict(showgrid = True, gridcolor = 'white') ,
                width = 1000 ,
                height = 500 ,
                plot_bgcolor = '#BDC3C7' ,
                paper_bgcolor = '#2C3E50' ,
                font = dict(
                            family = 'PT Sans Narrow' ,
                            size = 16 ,
                            color = '#ECF0F1'
                        )      
)



# plot 12 (diesel registration by company)



diesel_reg_germany = pd.read_csv('./data/diesel_reg_germany.csv')

# using melt() to transform the year columns into rows for plotting

diesel_reg_melted = diesel_reg_germany.melt(
                                        id_vars = 'brand' ,
                                        var_name = 'year' ,
                                        value_name = 'value'
)

# plot

diesel_reg_fig = px.line(
                        diesel_reg_melted ,
                        x = 'year' ,
                        y = 'value' ,
                        color = 'brand' ,
                        title = 'of which Diesel' ,
                        labels = {
                            'brand' : 'brand' , 
                            'value' : 'amount of units'
                            } ,
                        color_discrete_map = {
                                        'audi': '#F50537',
                                        'bmw': '#007eed',
                                        'mercedes': '#697c85' ,
                                        'toyota' : '#000000' ,
                                        'volkswagen' : '#1F2F57'
                                        }    
            
)

# adjusting line appearance

diesel_reg_fig.update_traces(
                            line_width = 3 ,
                            mode = 'lines+markers' , 
                            marker = dict(size = 10 , symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Amount of units: %{y}'
)

# add grid 

diesel_reg_fig.update_layout(
                            xaxis = dict(showgrid = True , gridcolor = 'white') ,
                            yaxis = dict(showgrid = True , gridcolor = 'white') ,
                            width = 1000 ,
                            height = 600 ,
                            plot_bgcolor = '#BDC3C7' ,
                            paper_bgcolor = '#2C3E50' ,
                            font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                    )      
)



# plot 13 (hybrid registration by company)



hybrid_reg_germany = pd.read_csv('./data/hybrid_reg_germany.csv')

# using melt() to transform the year columns into rows for plotting

hybrid_reg_melted = hybrid_reg_germany.melt(
                                        id_vars = 'brand' ,
                                        var_name = 'year' ,
                                        value_name = 'value'
)

# plot

hybrid_reg_fig = px.line(
                        hybrid_reg_melted ,
                        x = 'year' ,
                        y = 'value' ,
                        color = 'brand' ,
                        title = 'of which Hybrid' ,
                        labels = {
                            'brand' : 'brand' , 
                            'value' : 'amount of units'
                            } ,
                        color_discrete_map = {
                                        'audi': '#F50537',
                                        'bmw': '#007eed',
                                        'mercedes': '#697c85' ,
                                        'toyota' : '#000000' ,
                                        'volkswagen' : '#1F2F57'
                                        }   
)

# adjusting line appearance

hybrid_reg_fig.update_traces(
                            line_width = 3 ,
                            mode = 'lines+markers' , 
                            marker = dict(size = 10 , symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Amount of units: %{y}'
)

hybrid_reg_fig.update_layout(
                        xaxis = dict(showgrid = True, gridcolor = 'white') ,
                        yaxis = dict(showgrid = True, gridcolor = 'white') ,
                        width = 750 ,
                        height = 500 ,
                        plot_bgcolor = '#BDC3C7' ,
                        paper_bgcolor = '#2C3E50' ,
                        font = dict(
                                    family = 'PT Sans Narrow' ,
                                    size = 16 ,
                                    color = '#ECF0F1'
                                )      
)



# plot 14 (electric registration by company)



ev_reg_germany = pd.read_csv('./data/ev_reg_germany.csv')

# using melt() to transform the year columns into rows for plotting

ev_reg_melted = ev_reg_germany.melt(
                                id_vars = 'brand' ,
                                var_name = 'year' ,
                                value_name = 'value'
)

# plot

ev_reg_fig = px.line(
                    ev_reg_melted ,
                    x = 'year' ,
                    y = 'value' ,
                    color = 'brand' ,
                    title = 'of which Electric' ,
                    labels = {
                        'brand' : 'brand' , 
                        'value' : 'amount of units'
                        } ,
                    color_discrete_map = {
                                    'audi': '#F50537',
                                    'bmw': '#007eed',
                                    'mercedes': '#697c85' ,
                                    'toyota' : '#000000' ,
                                    'volkswagen' : '#1F2F57'
                                    }   
)

# adjusting line appearance

ev_reg_fig.update_traces(
                        line_width = 3 ,
                        mode = 'lines+markers' , 
                        marker = dict(size = 10 , symbol = 'circle') ,
                        hovertemplate = 'Year: %{x}<br>Amount of units: %{y}'
)

ev_reg_fig.update_layout(
                        xaxis = dict(showgrid = True, gridcolor = 'white') ,
                        yaxis = dict(showgrid = True, gridcolor = 'white') ,
                        width = 750 ,
                        height = 500 ,
                        plot_bgcolor = '#BDC3C7' ,
                        paper_bgcolor = '#2C3E50' ,
                        font = dict(
                                    family = 'PT Sans Narrow' ,
                                    size = 16 ,
                                    color = '#ECF0F1'
                                )      
)



# plot 15 (energy prices)



gas_el_price = pd.read_csv('./data/price_gas_electricity.csv')

# using melt() to transform the year columns into rows for plotting

prices_melted = gas_el_price.melt(
                                id_vars = 'type' ,
                                var_name = 'year' ,
                                value_name = 'value'
)

energy_prices_fig = px.line(
                            prices_melted ,
                            x = 'year' ,
                            y = 'value' ,
                            color = 'type' ,
                            title = 'Prices trend' ,
                            labels = {'type' : 'fuel type' , 'value' : 'price'} ,
                            color_discrete_map = {
                                            'diesel': '#EBC427',  
                                            'e5': '#B22929',  
                                            'e10': '#E5292B' ,
                                            'electricity' : '#0072CE'
                                            }
)

energy_prices_fig.update_traces(
                                mode = 'lines+markers' , 
                                marker = dict(size = 10 , symbol = 'circle') ,
                                hovertemplate = 'Year: %{x}<br>Price: %{y}'
)

energy_prices_fig.update_layout(
                                xaxis = dict(tickformat = '%Y') ,              # format x-axis for years
                                yaxis = dict(
                                            tickprefix = "€" ,                 # add € prefix
                                            tickmode = 'linear' ,              # set tick mode to linear
                                            tick0 = 0 ,                        # start ticks at 0
                                            dtick = 0.25 ,                     # step size of 0.25
                                            range = [0 , 2.25]
                                        ) , 
                                plot_bgcolor = '#BDC3C7' ,
                                paper_bgcolor = '#2C3E50' ,
                                font = dict(
                                            family = 'PT Sans Narrow' ,
                                            size = 16 ,
                                            color = '#ECF0F1'
                                        )                                     
)



# plot 16 (energy prices % changes)



percentage_changes = pd.read_csv('./data/percentage_changes.csv')

# using melt() to transform the year columns into rows for plotting

percent_melted = percentage_changes.melt(
                                id_vars = 'type' ,
                                var_name = 'year' ,
                                value_name = 'value'
)

# plot

energy_change_p_fig = px.line(
                            percent_melted ,
                            x = 'year' ,
                            y = 'value' ,
                            color = 'type' ,
                            title = 'Prices trend in %' ,
                            labels = {'type' : 'fuel type' , 'value' : '%'} ,
                            color_discrete_map = {
                                                'diesel': '#EBC427',  
                                                'e5': '#B22929',  
                                                'e10': '#E5292B' ,
                                                'electricity' : '#0072CE'
                                            }
)

# adjusting line appearance

energy_change_p_fig.update_traces(
                                mode = 'lines+markers' , 
                                marker = dict(size = 10 , symbol = 'circle') ,
                                hovertemplate = 'Year: %{x}<br>Change in %: %{y}'
)

# formatting axis

energy_change_p_fig.update_layout(
                                xaxis = dict(tickformat = '%Y') ,   # format x-axis for years
                                yaxis = dict(ticksuffix = "%") ,    # add % suffix
                                plot_bgcolor = '#BDC3C7' ,
                                paper_bgcolor = '#2C3E50' ,
                                font = dict(
                                            family = 'PT Sans Narrow' ,
                                            size = 16 ,
                                            color = '#ECF0F1'
                                        )                   
)



# plot 17 (amount of charging points map)



charging_points_2015 = pd.read_csv('./data/charging_points_2015.csv')
charging_points_2016 = pd.read_csv('./data/charging_points_2016.csv')
charging_points_2017 = pd.read_csv('./data/charging_points_2017.csv')
charging_points_2018 = pd.read_csv('./data/charging_points_2018.csv')
charging_points_2019 = pd.read_csv('./data/charging_points_2019.csv')
charging_points_2020 = pd.read_csv('./data/charging_points_2020.csv')
charging_points_2021 = pd.read_csv('./data/charging_points_2021.csv')
charging_points_2022 = pd.read_csv('./data/charging_points_2022.csv')
charging_points_2023 = pd.read_csv('./data/charging_points_2023.csv')

layer1 = go.Scattermapbox(
                        lat = charging_points_2015['latitude'] ,
                        lon = charging_points_2015['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5, color = '#964F4C') ,  
                        name = '2015'    
)

layer2 = go.Scattermapbox(
                        lat = charging_points_2016['latitude'] ,
                        lon = charging_points_2016['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#f7caca') ,  
                        name = '2016'
)

layer3 = go.Scattermapbox(
                        lat = charging_points_2017['latitude'] ,
                        lon = charging_points_2017['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#88B04B') ,  
                        name = '2017'  
)

layer4 = go.Scattermapbox(
                        lat = charging_points_2018['latitude'] ,
                        lon = charging_points_2018['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#5F4B8B') ,
                        name = '2018' 
)

layer5 = go.Scattermapbox(
                        lat = charging_points_2019['latitude'] ,
                        lon = charging_points_2019['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#ff6f61') ,  
                        name = '2019'  
)

layer6 = go.Scattermapbox(
                        lat = charging_points_2020['latitude'] ,
                        lon = charging_points_2020['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#0F4C81') ,
                        name = '2020'
)

layer7 = go.Scattermapbox(
                        lat = charging_points_2021['latitude'] ,
                        lon = charging_points_2021['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#f5df4d') , 
                        name = '2021'  
)

layer8 = go.Scattermapbox(
                        lat = charging_points_2022['latitude'] ,
                        lon = charging_points_2022['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#6667AB') ,
                        name = '2022'
)

layer9 = go.Scattermapbox(
                        lat = charging_points_2023['latitude'] ,
                        lon = charging_points_2023['longitude'] ,
                        mode = 'markers' ,
                        marker = dict(size = 5 , color = '#BE3455') , 
                        name = '2023'
)

# create the map layout

layout = go.Layout(
                mapbox = dict(
                            style = 'carto-positron' , 
                            zoom = 4.5 ,
                            center = dict(lat = 51.1657 , lon = 10.4515)        # center of Germany
                        ),
                margin = dict(r = 0 , t = 0 , l = 0 , b = 0) ,                  # remove margins
                paper_bgcolor = '#2C3E50' ,
                font = dict(
                            family = 'PT Sans Narrow' ,
                            size = 16 ,
                            color = '#ECF0F1'
                        ) ,
                legend = dict(
                            title = dict(text = 'Year')  
                        )                       
)

# combine layers into a figure

charging_points_map_fig = go.Figure(
                                    data = [layer1, layer2, layer3, layer4, layer5, layer6, layer7, layer8, layer9] , 
                                    layout = layout
                                )



# plot 18 (amount of gas stations (top 5 brands) map)



top_5_gas_stations = pd.read_csv('./data/top5_gasstations.csv')

brand_colors = {
                'ARAL' : '#1670B9' ,
                'ESSO' : '#d6dbdb' ,
                'TotalEnergies' : '#FF7800' ,
                'Shell' : '#FFD500' ,
                'AVIA' : '#E30613'
}


top5_gas_st_fig = px.scatter_mapbox(
                                    top_5_gas_stations ,
                                    lat = 'latitude' ,
                                    lon = 'longitude', 
                                    text = 'brand' ,
                                    color = 'brand' ,
                                    color_discrete_map = brand_colors ,
                                    zoom = 4.5 ,       
                                    height = 500    
)

top5_gas_st_fig.update_layout(
                            mapbox_style = 'carto-positron' ,  
                            paper_bgcolor = '#2C3E50' ,
                            font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                    ) ,
                            margin = {'r' : 0 ,'t' : 0 , 'l' : 0 , 'b' : 0}             # remove margins 
)



# plot 20 (total amount of charging points per federal state)



total_cp = pd.read_csv('./data/total_cp.csv')

# convert data to a long format

total_melted = total_cp.melt(
                            id_vars = 'federal_state' , 
                            var_name = 'year' , 
                            value_name = 'value'
                        )

total_melted['year'] = total_melted['year'].astype(int)

custom_colors = {
    'Baden-Württemberg' : '#FFD700' ,  
    'Bayern' : '#4682B4' ,
    'Berlin' : '#8B0000' ,
    'Brandenburg' : '#8B0000' ,
    'Bremen' : '#8B0000' ,
    'Hamburg' : '#8B0000' ,
    'Hessen' : '#8B0000' ,
    'Mecklenburg-Vorpommern' : '#FFBF00' ,
    'Niedersachsen' : 'black' ,
    'Nordrhein-Westfalen' : '#228B22' ,
    'Rheinland-Pfalz' : 'black' ,
    'Saarland' : '#4682B4' ,
    'Sachsen' : '#228B22' ,
    'Sachsen-Anhalt' : '#FFBF00' ,
    'Schleswig-Holstein' : '#4682B4' ,
    'Thüringen' : '#4682B4'  
}

# create the small multiples plot

total_cp_fs_fig = px.line(
                        total_melted ,
                        x = 'year' ,
                        y = 'value' ,
                        color = 'federal_state' ,
                        facet_col = 'federal_state' ,
                        facet_col_wrap = 4 , 
                        title = 'Amount of Charging Points per Federal State' ,
                        labels = {'value' : 'amount of charging points' , 'year' : 'year'} ,
                        height = 900 ,
                        color_discrete_map = custom_colors
)

total_cp_fs_fig.update_layout(
                            plot_bgcolor = '#BDC3C7' ,
                            paper_bgcolor = '#2C3E50' ,
                            font = dict(
                                        family = 'PT Sans Narrow' ,
                                        size = 16 ,
                                        color = '#ECF0F1'
                                    ) ,  
                            xaxis = dict(showgrid = True , gridcolor = 'white') ,  
                            yaxis = dict(showgrid = True , gridcolor = 'white') ,
                            showlegend = False  
)

total_cp_fs_fig.update_traces(
                            line = dict(width = 2) ,
                            marker = dict(size = 3)  
)

total_cp_fs_fig.for_each_annotation(lambda a: a.update(text = a.text.split("=")[-1]))



# plot 21 (amount of slow charging points per federal state)



nlp = pd.read_csv('./data/nlp.csv')

# convert data to a long format

nlp_melted = nlp.melt(
                    id_vars = 'federal_state' , 
                    var_name = 'year' , 
                    value_name = 'value'
                )

nlp_melted['year'] = nlp_melted['year'].astype(int)

custom_colors = {
    'Baden-Württemberg' : '#FFD700' ,  
    'Bayern' : '#4682B4' ,
    'Berlin' : '#8B0000' ,
    'Brandenburg' : '#8B0000' ,
    'Bremen' : '#8B0000' ,
    'Hamburg' : '#8B0000' ,
    'Hessen' : '#8B0000' ,
    'Mecklenburg-Vorpommern' : '#FFBF00' ,
    'Niedersachsen' : 'black' ,
    'Nordrhein-Westfalen' : '#228B22' ,
    'Rheinland-Pfalz' : 'black' ,
    'Saarland' : '#4682B4' ,
    'Sachsen' : '#228B22' ,
    'Sachsen-Anhalt' : '#FFBF00' ,
    'Schleswig-Holstein' : '#4682B4' ,
    'Thüringen' : '#4682B4'  
}

# create the small multiples plot

nlp_fig = px.line(
            nlp_melted ,
            x = 'year' ,
            y = 'value' ,
            color = 'federal_state' ,
            facet_col = 'federal_state' ,
            facet_col_wrap = 4 ,   
            title = 'Amount of Standard Charging Points in Federal States' ,
            labels = {'value' : 'amount of charging points' , 'year' : 'year'} ,
            height = 900 ,
            color_discrete_map = custom_colors
)

nlp_fig.update_layout(
                    plot_bgcolor = '#BDC3C7' ,
                    paper_bgcolor = '#2C3E50' ,
                    font = dict(
                                family = 'PT Sans Narrow' ,
                                size = 16 ,
                                color = '#ECF0F1'
                            ) ,  
                    xaxis = dict(showgrid = True , gridcolor = 'white') ,  
                    yaxis = dict(showgrid = True , gridcolor = 'white') ,
                    showlegend = False
)

nlp_fig.update_traces(
                    line = dict(width = 2) ,  
                    marker = dict(size = 3)  
)

nlp_fig.for_each_annotation(lambda a : a.update(text=a.text.split("=")[-1]))



# plot 22 (amount of fast charging points per federal state)



slp = pd.read_csv('./data/slp.csv')

# convert data to a long format

slp_melted = slp.melt(
                    id_vars = 'federal_state' , 
                    var_name = 'year' , 
                    value_name = 'value'
            )

slp_melted['year'] = slp_melted['year'].astype(int)

custom_colors = {
    'Baden-Württemberg' : '#FFD700' ,  
    'Bayern' : '#4682B4' ,
    'Berlin' : '#8B0000' ,
    'Brandenburg' : '#8B0000' ,
    'Bremen' : '#8B0000' ,
    'Hamburg' : '#8B0000' ,
    'Hessen' : '#8B0000' ,
    'Mecklenburg-Vorpommern' : '#FFBF00' ,
    'Niedersachsen' : 'black' ,
    'Nordrhein-Westfalen' : '#228B22' ,
    'Rheinland-Pfalz' : 'black' ,
    'Saarland' : '#4682B4' ,
    'Sachsen' : '#228B22' ,
    'Sachsen-Anhalt' : '#FFBF00' ,
    'Schleswig-Holstein' : '#4682B4' ,
    'Thüringen' : '#4682B4'  
}

# create the small multiples plot

slp_fig = px.line(
                slp_melted,
                x = 'year' ,
                y = 'value' ,
                color = 'federal_state' ,
                facet_col = 'federal_state' ,
                facet_col_wrap = 4 ,   
                title = 'Amount of Fast Charging Points in Federal States' ,
                labels = {'value' : 'amount of charging points' , 'year' : 'year'} ,
                height = 900 ,
                color_discrete_map = custom_colors
)

slp_fig.update_layout(
                    plot_bgcolor = '#BDC3C7' ,
                    paper_bgcolor = '#2C3E50' ,
                    font = dict(
                                family = 'PT Sans Narrow' ,
                                size = 16 ,
                                color = '#ECF0F1'
                            ) ,  
                    xaxis = dict(showgrid = True , gridcolor = 'white') ,  
                    yaxis = dict(showgrid = True , gridcolor = 'white') ,
                    showlegend = False
)

slp_fig.update_traces(
                    line = dict(width = 2) ,  
                    marker = dict(size = 3)  
)

slp_fig.for_each_annotation(lambda a : a.update(text=a.text.split("=")[-1]))



# plot 23 (prediction on amount of charging points)



total_total_cp = pd.read_csv('./data/total_total_cp.csv')

years_ttcp = np.array([2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]).reshape(-1, 1)

# initialize figure

ttcp_fig = go.Figure()

# colors for each index

colors_ttcp = {'NLP' : '#20b843' , 'SLP' : '#2049b8' , 'total' : '#20b8b4'}

# regression for each index

for index in ['NLP' , 'SLP' , 'total'] :

    # extract data for the current index

    points = total_total_cp.loc[total_total_cp['index'] == index].iloc[0, 1:].values

    # fit the model

    model = LinearRegression()
    model.fit(years_ttcp , points)

    # predict values up to 2035

    future_years = np.array(range(2017, 2036)).reshape(-1, 1)
    predicted_points = model.predict(future_years)

    # add actual data points to the plot

    ttcp_fig.add_trace(go.Scatter(
                                x = years_ttcp.flatten() ,
                                y = points ,
                                mode = 'markers' ,
                                name = f'{index} Actual' ,
                                marker = dict(
                                            size = 8 , 
                                            symbol = 'circle' , 
                                            color = colors_ttcp[index])
                            )
    )

    # add predicted trendline to the plot

    ttcp_fig.add_trace(go.Scatter(
                                x = future_years.flatten() ,
                                y = predicted_points ,
                                mode = 'lines' ,
                                name = f'{index} Prediction' ,
                                line = dict(
                                            color = colors_ttcp[index] , 
                                            dash = 'dash'
                                        )
                            )
    )

ttcp_fig.update_layout(
                    title = 'Prediction on amount of charging points in Germany (2017-2035)' ,
                    xaxis_title = 'year' ,
                    yaxis_title = 'amount of charging points' ,
                    legend = dict(x = 0.1 , y = 0.9) ,
                    template = 'plotly_white' ,
                    plot_bgcolor = '#BDC3C7' ,
                    paper_bgcolor = '#2C3E50' ,
                    font = dict(
                                family = 'PT Sans Narrow' ,
                                size = 16 ,
                                color = '#ECF0F1'
                            ) ,       
                    xaxis = dict(showgrid = True , gridcolor = 'white') ,
                    yaxis = dict(showgrid = True , gridcolor = 'white') ,
                    updatemenus = [
                                    dict(
                                        buttons = list([

                                                    # Show All Button : make all traces visible

                                                    dict(
                                                        label = 'Show All' ,
                                                        method = 'update' ,
                                                        args = [{'visible' : [True , True , True , True , True , True]}]
                                                    ) ,

                                                    # NLP Only Button : show only NLP Actual and NLP Prediction

                                                    dict(
                                                        label = 'NLP Only' ,
                                                        method = 'update' ,
                                                        args = [{'visible' : [True , True , False , False , False , False]}]
                                                    ) ,

                                                    # SLP Only Button : show only SLP Actual and SLP Prediction

                                                    dict(
                                                        label = 'SLP Only' ,
                                                        method = 'update' ,
                                                        args = [{'visible' : [False , False , True , True , False , False]}]
                                                    ) ,

                                                    # Total Only Button : show only Total Actual and Total Prediction

                                                    dict(
                                                        label = 'Total Only' ,
                                                        method = 'update' ,
                                                        args = [{'visible' : [False , False , False , False , True , True]}]
                                                    ) ,
                                                ]) ,
                                        direction = 'down' ,
                                    )
                                ]
)



# plot 24 (audi revenue)



# filtering using boolean mask just needed category (revenue)

revenue_a_data = audi_revenue[audi_revenue['category'] == 'revenue_(euro_billion)']

#  using melt() to transform the year columns into rows for plotting

revenue_a_melted = revenue_a_data.melt(
                                    id_vars = 'category',       # keep the 'category' column as is
                                    var_name = 'year',          # create a column for years
                                    value_name = 'revenue'      # create a column for revenue values
)

# plot

a_revenue_fig = px.line(
                    revenue_a_melted ,
                    x = 'year' ,                 # years on the x-axis
                    y = 'revenue' ,              # revenue on the y-axis
                    title = 'Audi Revenue (2015-2023)'
)

# adjusting line appearance

a_revenue_fig.update_traces(
                            line_color = '#F50537' ,
                            line_width = 4 ,
                            mode = 'lines+markers' ,
                            marker = dict(size = 10 , symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Revenue: %{y}'
)

a_revenue_fig.update_layout(
                        xaxis = dict(
                                    tickformat = '%Y' ,
                                     showgrid = True , 
                                     gridcolor = 'black' ,
                                     rangeslider = dict(visible = True)
                                ) ,                       
                        yaxis = dict(
                                    tickprefix = '€' , 
                                    ticksuffix = 'B' ,
                                    showgrid = True , 
                                    gridcolor = 'black'
                                ) ,
                        plot_bgcolor = 'white' ,
                        paper_bgcolor = 'black' ,
                        font = dict(
                                    family = 'Futura' ,  # use 'Futura' as closest to AudiType
                                    size = 12 ,
                                    color = 'white'
                                ) ,
                        width = 600 , 
                        height = 400        
)



# plot 25 (audi revenue growth)



# filtering using boolean mask just needed category (revenue growth)

growth_a_data = audi_revenue[audi_revenue['category'] == 'revenue_growth_(%)']

#  using melt() to transform the year columns into rows for plotting

growth_a_melted = growth_a_data.melt(
                                    id_vars = 'category' ,              # keep the 'category' column as is
                                    var_name = 'year' ,                 # create a column for years
                                    value_name = '%'                    # create a column for revenue values
)

# plot

a_revenue_growth_fig = px.line (
                                growth_a_melted ,
                                x = 'year' ,
                                y = '%' ,
                                title = 'Audi Revenue Growth (2015-2023)'
)

a_revenue_growth_fig.update_traces(
                                    line_color = '#F50537' ,
                                    line_width = 4 ,
                                    mode = 'lines+markers' , 
                                    marker = dict(size = 10 , symbol = 'circle') ,
                                    hovertemplate = 'Year: %{x}<br>Growth: %{y}'
)

a_revenue_growth_fig.update_layout(
                                    xaxis = dict(
                                                 tickformat = '%Y' ,
                                                 showgrid = True , 
                                                 gridcolor = 'black' ,
                                                 rangeslider = dict(visible = True)
                                            ) ,  
                                    yaxis = dict(
                                                 ticksuffix = "%" ,
                                                 showgrid = True , 
                                                 gridcolor = 'black' ,
                                                 tickmode = 'linear' ,  # set tick mode to linear
                                                 tick0 = 0 ,            # start ticks at 0
                                                 dtick = 3 ,            # step size of 1
                                                 range = [-4 , 16]
                                            ) ,
                                    plot_bgcolor = 'white' ,
                                    paper_bgcolor = 'black' ,
                                    font = dict(
                                                family = 'Futura' ,     # use 'Futura' as closest to AudiType
                                                size = 12 ,
                                                color = 'white'
                                            ) ,
                                    width = 600 , 
                                    height = 400              
)



# plot 26 (bmw revenue)



# filtering using boolean mask just needed category (revenue)

revenue_b_data = bmw_revenue[bmw_revenue['category'] == 'revenue_(euro_billion)']

#  using melt() to transform the year columns into rows for plotting

revenue_b_melted = revenue_b_data.melt(
                                    id_vars = 'category',       # Keep the 'category' column as is
                                    var_name = 'year',          # Create a column for years
                                    value_name = 'revenue'      # Create a column for revenue values
)

# plot

b_revenue_fig = px.line(
                        revenue_b_melted,
                        x = 'year' ,                            # years on the x-axis
                        y = 'revenue' ,                         # revenue on the y-axis
                        title = 'BMW Revenue (2015-2023)' ,
)

b_revenue_fig.update_traces(
                            line_color = '#007eed' ,
                            line_width = 4 ,
                            mode = 'lines+markers' ,
                            marker = dict(size = 10 , symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Revenue: %{y}'               
)

b_revenue_fig.update_layout(
                            xaxis = dict(
                                        tickformat = '%Y' , 
                                        showgrid = True, 
                                        gridcolor = '#6F6F6F' ,
                                        rangeslider = dict(visible = True)
                                    ),  
                            yaxis = dict(
                                        tickprefix = "€" , 
                                        ticksuffix = "B" , 
                                        showgrid = True , 
                                        gridcolor = '#6F6F6F'
                                    ) ,
                            plot_bgcolor = 'white' ,
                            paper_bgcolor = '#6F6F6F' ,
                            font = dict(
                                        family = 'Helvetica' ,  # 'Helvetica' as most close to font used by bmw
                                        size = 12 ,
                                        color = 'black'
                                    ) ,
                            width = 600 , 
                            height = 400                
)



# plot 27 (bmw revenue growth)



# filtering using boolean mask just needed category (revenue growth)

growth_b_data = bmw_revenue[bmw_revenue['category'] == 'revenue_growth_(%)']

#  using melt() to transform the year columns into rows for plotting

growth_b_melted = growth_b_data.melt(
                                    id_vars = 'category' ,       # keep the 'category' column as is
                                    var_name = 'year' ,          # create a column for years
                                    value_name = '%'             # create a column for revenue growth values
)

# plot

b_revenue_growth_fig = px.line(
                                growth_b_melted ,
                                x = 'year' ,
                                y = '%' ,
                                title = 'BMW Revenue Growth (2015-2023)'
)

b_revenue_growth_fig.update_traces(
                                    line_color = '#007eed' ,
                                    line_width = 4 ,
                                    mode = 'lines+markers' ,
                                    marker = dict(size = 10 , symbol = 'circle') ,
                                    hovertemplate = 'Year: %{x}<br>Growth: %{y}'
)

b_revenue_growth_fig.update_layout(
                                    xaxis = dict(
                                                tickformat = '%Y' ,
                                                showgrid = True , 
                                                gridcolor = '#6F6F6F' ,
                                                rangeslider = dict(visible = True)
                                            ) ,  
                                    yaxis = dict(
                                                ticksuffix = '%' ,
                                                showgrid = True , 
                                                gridcolor = '#6F6F6F' ,
                                                tickmode = 'linear' ,                   # set tick mode to linear
                                                tick0 = 0 ,                             # start ticks at 0
                                                dtick = 3 ,                             # step size of 3
                                                range = [-12 , 19]
                                            ) ,
                                    plot_bgcolor = 'white' ,
                                    paper_bgcolor = '#6F6F6F' ,
                                    font = dict(
                                                family = 'Helvetica' , 
                                                size = 12 ,
                                                color = 'black'
                                            ) ,
                                    width = 600 ,
                                    height = 450                 
)



# plot 28 (mercedes revenue)



# boolean mask for filtering only needed row (revenue)

revenue_m_data = mercedes_revenue[mercedes_revenue['category'] == 'revenue_(euro_billion)']

# using melt() to transform the year columns into rows for plotting

revenue_m_melted = revenue_m_data.melt(
                                        id_vars = 'category' ,          # keeps the 'category' column as is
                                        var_name = 'year' ,             # create a column for years
                                        value_name = 'revenue'          # create a column for revenue values
)

# plot

m_revenue_fig = px.line(
                        revenue_m_melted ,
                        x = 'year' ,
                        y = 'revenue' ,
                        title = 'Mercedes-Benz Revenue (2015-2023)'
) 

m_revenue_fig.update_traces(
                            line_color = '#231f20' ,
                            line_width = 4 ,
                            mode = 'lines+markers' , 
                            marker = dict(size = 10, symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Revenue: %{y}'
)

m_revenue_fig.update_layout(
                            xaxis = dict(
                                        tickformat = '%Y' ,
                                        showgrid = True , 
                                        gridcolor = '#dcddd7' ,
                                        rangeslider = dict(visible = True)
                                    ) , 
                            yaxis = dict(
                                        tickprefix = '€' , 
                                        ticksuffix = 'B' ,
                                        showgrid = True , 
                                        gridcolor = '#dcddd7'
                                    ) ,
                            width = 600 ,
                            height = 400 ,
                            plot_bgcolor = 'white' ,
                            paper_bgcolor = '#dcddd7' ,
                            font = dict(
                                        family = 'Noto Serif' ,
                                        size = 12 ,
                                        color = '#231f20'
                                    )       
)



# plot 29 (mercedes revenue growth)



# boolean mask for filtering only needed row

growth_m_data = mercedes_revenue[mercedes_revenue['category'] == 'revenue_growth_(%)']

# using melt() to transform the year columns into rows for plotting

growth_m_melted = growth_m_data.melt(
                                    id_vars = 'category' ,              # keeps the 'category' column as is
                                    var_name = 'year' ,                 # create a column for years
                                    value_name = '%'                    # create a column for grow % values
)

# plotting line plot

m_revenue_growth_fig = px.line(
                                growth_m_melted ,
                                x = 'year' ,
                                y = '%' ,
                                title = 'Mercedes-Benz Revenue Growth (2015-2023)' 
) 

# adjusting line

m_revenue_growth_fig.update_traces(
                                    line_color = '#231f20' ,
                                    line_width = 4 ,
                                    mode = 'lines+markers' , 
                                    marker = dict(size = 10, symbol = 'circle') ,
                                    hovertemplate = 'Year: %{x}<br>Growth: %{y}'
)

m_revenue_growth_fig.update_layout(
                                    xaxis = dict(
                                                tickformat = '%Y' ,
                                                showgrid = True , 
                                                gridcolor = '#dcddd7' ,
                                                rangeslider = dict(visible = True)
                                            ) , 
                                    yaxis = dict(
                                                ticksuffix = '%' ,
                                                showgrid = True ,
                                                gridcolor = '#dcddd7' ,
                                                tickmode = 'linear',                    # set tick mode to linear
                                                tick0 = 0,                              # start ticks at 0
                                                dtick = 3,                              # step size of 3
                                                range = [-3 , 16]
                                            ) ,
                                    width = 600 ,
                                    height = 400 ,
                                    plot_bgcolor = 'white' ,
                                    paper_bgcolor = '#dcddd7' ,
                                    font = dict(
                                                family = 'Noto Serif' ,
                                                size = 12 ,
                                                color = '#231f20'
                                            )       
)



# plot 30 (toyota revenue)



# boolean mask for filtering only needed row

revenue_t_data = toyota_revenue[toyota_revenue['category'] == 'revenue_(euro_billion)']

# using melt() to transform the year columns into rows for plotting

revenue_t_melted = revenue_t_data.melt(
                                        id_vars = 'category' ,              # keeps the 'category' column as is
                                        var_name = 'year' ,                 # create a column for years
                                        value_name = 'revenue'              # create a column for revenue values
        )

t_revenue_fig = px.line(
                        revenue_t_melted ,
                        x = 'year' ,
                        y = 'revenue' ,
                        title = 'Toyota Revenue (2015-2023)' 
) 

# adjusting line

t_revenue_fig.update_traces(
                            line_color = '#EB0A1E' ,
                            line_width = 4 ,
                            mode = 'lines+markers' , 
                            marker = dict(size = 10, symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Revenue: %{y}'
)

t_revenue_fig.update_layout(
                            xaxis = dict(
                                        tickformat = '%Y' ,
                                        showgrid = True , 
                                        gridcolor = 'black' ,
                                        rangeslider = dict(visible = True)
                                    ) , 
                            yaxis = dict(
                                        tickprefix = '€' , 
                                        ticksuffix = 'B' ,
                                        showgrid = True , 
                                        gridcolor = 'black'
                                    ) ,
                            width = 600 ,
                            height = 400 ,
                            plot_bgcolor = 'white' ,
                            font = dict(
                                        family = 'Arial' ,
                                        size = 12 ,
                                        color = 'black'
                                    )
)



# plot 31 (toyota revenue growth)



# boolean mask for filtering only needed row

growth_t_data = toyota_revenue[toyota_revenue['category'] == 'revenue_growth_(%)']

# using melt() to transform the year columns into rows for plotting

growth_t_melted = growth_t_data.melt(
                                    id_vars = 'category' ,              # keeps the 'category' column as is
                                    var_name = 'year' ,                 # create a column for years
                                    value_name = '%'                    # create a column for grow % values
)

t_revenue_growth_fig = px.line(
                                growth_t_melted ,
                                x = 'year' ,
                                y = '%' ,
                                title = 'Toyota Revenue Growth (2015-2023)' 
) 

t_revenue_growth_fig.update_traces(
                                    line_color = '#EB0A1E' ,
                                    line_width = 4 ,
                                    mode = 'lines+markers' , 
                                    marker = dict(size = 10, symbol = 'circle') ,
                                    hovertemplate = 'Year: %{x}<br>Growth: %{y}'
)

t_revenue_growth_fig.update_layout(
                                    xaxis = dict(
                                                tickformat = '%Y' ,
                                                showgrid = True , 
                                                gridcolor = 'black' ,
                                                rangeslider = dict(visible = True)
                                            ) ,
                                    yaxis = dict(
                                                ticksuffix = '%' ,
                                                showgrid = True , 
                                                gridcolor = 'black' ,
                                                tickmode = 'linear',                    # set tick mode to linear
                                                tick0 = 0,                              # start ticks at 0
                                                dtick = 3,                              # step size of 3
                                                range = [-16 , 18]
                                            ) ,
                                    width = 600 ,
                                    height = 500 ,
                                    plot_bgcolor = 'white' ,
                                    font = dict(
                                                family = 'Arial' ,
                                                size = 12 ,
                                                color = 'black'
                                            )
)



# plot 32 (volkswagen revenue)



# boolean mask for filtering only needed row

revenue_v_data = vw_revenue[vw_revenue['category'] == 'revenue_(euro_billion)']

# using melt() to transform the year columns into rows for plotting

revenue_v_melted = revenue_v_data.melt(
                                        id_vars = 'category' ,                      # keeps the 'category' column as is
                                        var_name = 'year' ,                         # create a column for years
                                        value_name = 'revenue'                      # create a column for revenue values
)

# plotting line plot

v_revenue_fig = px.line(
                        revenue_v_melted ,
                        x = 'year' ,
                        y = 'revenue' ,
                        title = 'Volkswagen Revenue (2015-2023)' 
) 

# adjusting line

v_revenue_fig.update_traces(
                            line_color = '#1F2F57' ,
                            line_width = 4 ,
                            mode = 'lines+markers' , 
                            marker = dict(size = 10, symbol = 'circle') ,
                            hovertemplate = 'Year: %{x}<br>Revenue: %{y}'
)

v_revenue_fig.update_layout(
                            xaxis = dict(
                                        tickformat = '%Y' ,
                                        showgrid = True , 
                                        gridcolor = '#A8A8A8' ,
                                        rangeslider = dict(visible = True)
                                    ) , 
                            yaxis = dict(
                                        tickprefix = '€' ,
                                        ticksuffix = 'B' ,
                                        showgrid = True , 
                                        gridcolor = '#A8A8A8'
                                    ) ,
                            width = 600 ,
                            height = 400 ,
                            plot_bgcolor = 'white' ,
                            paper_bgcolor = '#A8A8A8' ,
                            font = dict(
                                        family = 'Arial Rounded MT Bold' ,
                                        size = 12 ,
                                        color = 'black'
                                    )
)



# plot 33 (volkswagen revenue growth)



# boolean mask for filtering only needed row

growth_v_data = vw_revenue[vw_revenue['category'] == 'revenue_growth_(%)']

# using melt() to transform the year columns into rows for plotting

growth_v_melted = growth_v_data.melt(
                                    id_vars = 'category' ,                      # keeps the 'category' column as is
                                    var_name = 'year' ,                         # create a column for years
                                    value_name = '%'                            # create a column for grow % values
)

# plotting line plot

v_revenue_growth_fig = px.line(
                                growth_v_melted ,
                                x = 'year' ,
                                y = '%' ,
                                title = 'Volkswagen Revenue Growth (2015-2023)' 
) 

v_revenue_growth_fig.update_traces(
                                    line_color = '#1F2F57' ,
                                    line_width = 4 ,
                                    mode = 'lines+markers' , 
                                    marker = dict(size = 10, symbol = 'circle') ,
                                    hovertemplate = 'Year: %{x}<br>Growth: %{y}'
)

# formating ticks

v_revenue_growth_fig.update_layout(
                                    xaxis = dict(
                                                tickformat = '%Y' ,
                                                showgrid = True , 
                                                gridcolor = '#A8A8A8' ,
                                                rangeslider = dict(visible = True)
                                            ) , 
                                    yaxis = dict(
                                                ticksuffix = '%' ,
                                                showgrid = True , 
                                                gridcolor = '#A8A8A8' ,
                                                tickmode = 'linear',                        # set tick mode to linear
                                                tick0 = 0,                                  # start ticks at 0
                                                dtick = 3,                                  # step size of 3
                                                range = [-25 , 18]
                                            ) ,
                                    width = 600 ,
                                    height = 500 ,
                                    plot_bgcolor = 'white' ,
                                    paper_bgcolor = '#A8A8A8' ,
                                    font = dict(
                                                family = 'Arial Rounded MT Bold' ,
                                                size = 12 ,
                                                color = 'black'
                                            )
)



# plot 34 (audi sales by category)



# transform data into a long format for plotting

audi_sales_long = audi_sales.melt(
                                id_vars = 'category' , 
                                var_name = 'year' ,
                                value_name = 'amount of units sold'
)

# create a grouped bar chart

a_sales_fig = px.bar(
                    audi_sales_long,
                    x = 'year' ,
                    y = 'amount of units sold' ,
                    color = 'category' ,
                    title = 'Audi Sales Volume by Category (2015-2023)' ,
                    color_discrete_map = {
                                    'Internal Combustion Engine' : '#F50537' ,  
                                    'Hybrid' : '#A5ACAF' ,  
                                    'Electric Vehicles' : '#4B4B4B'
                                        } ,
                    barmode = 'group'
)

a_sales_fig.update_layout(
                            xaxis = dict(
                                        showgrid = True , 
                                        gridcolor = 'black'
                                    ) ,
                            yaxis = dict(
                                        showgrid = True , 
                                        gridcolor = 'black' ,
                                        tickmode = 'linear' ,  # set tick mode to linear
                                        tick0 = 0 ,            # start ticks at 0
                                        dtick = 100000
                                    ) ,
                            width = 700 , 
                            height = 500 ,
                            plot_bgcolor = 'white' ,
                            paper_bgcolor = 'black' ,  
                            font = dict(
                                        family = 'Futura' ,  
                                        size = 12 ,
                                        color = 'white'
                                    )
)

a_sales_fig.update_traces(
                            hovertemplate = 'Year: %{x}<br>Amount: %{y}'
)



# plot 35 (bmw sales by category)



# transform data into a long format for plotting

bmw_sales_long = bmw_sales.melt(
                                id_vars = 'category' , 
                                var_name = 'year' , 
                                value_name = 'amount of units sold'
)

# grouped bar chart

b_sales_fig = px.bar(
                    bmw_sales_long ,
                    x = 'year' ,
                    y = 'amount of units sold' ,
                    color = 'category' ,
                    title = 'BMW Sales Volume by Category (2015-2023)',
                    color_discrete_map = {
                                    'Internal Combustion Engine' : '#f40000' ,  
                                    'Hybrid' : '#522dae' ,  
                                    'Electric Vehicles' : '#007eed'
                                    } ,
                    barmode = 'group'
)

# add grid

b_sales_fig.update_layout(
                        xaxis = dict(
                                    showgrid = True , 
                                    gridcolor = '#6F6F6F'
                                ) ,
                        yaxis = dict(
                                    showgrid = True , 
                                    gridcolor = '#6F6F6F' ,
                                    tickmode ='linear' ,        # set tick mode to linear
                                    tick0 = 0 ,                 # start ticks at 0
                                    dtick = 100000
                                ) ,
                        width = 700 , 
                        height = 500 ,
                        plot_bgcolor = 'white' ,
                        paper_bgcolor = '#6F6F6F' ,
                        font = dict(
                                    family = 'Helvetica' ,  
                                    size = 12 ,
                                    color = 'black'
                                )
)

b_sales_fig.update_traces(
                hovertemplate = 'Year: %{x}<br>Amount: %{y}'
)



# plot 36 (mercedes sales by category)



# transform data into a long format for plotting

mercedes_sales_long = mercedes_sales.melt(
                                        id_vars = 'category' , 
                                        var_name = 'year' , 
                                        value_name = 'amount of units sold'
)

# grouped bar chart

m_sales_fig = px.bar(
                    mercedes_sales_long ,
                    x = 'year' ,
                    y = 'amount of units sold' ,
                    color = 'category' ,
                    title = 'Mercedes-Benz Sales Volume by Category (2015-2023)' ,
                    color_discrete_map = {
                                        'Internal Combustion Engine': '#231f20' ,  
                                        'Hybrid': '#697c85' ,  
                                        'Electric Vehicles': '#7a8084'
                                        } ,
                    barmode = 'group'
)

# add grid

m_sales_fig.update_layout(
                        xaxis = dict(
                                    showgrid = True , 
                                    gridcolor = '#dcddd7'
                                ) , 
                        yaxis = dict(
                                    showgrid = True , 
                                    gridcolor = '#dcddd7' ,
                                    tickmode = 'linear' ,  # set tick mode to linear
                                    tick0 = 0 ,            # start ticks at 0
                                    dtick = 100000
                                ) ,
                        width = 700 , 
                        height = 500 ,
                        plot_bgcolor = 'white' ,
                        paper_bgcolor = '#dcddd7' ,
                        font = dict(
                                    family = 'Noto Serif' ,
                                    size = 12 ,
                                    color = '#231f20'
                                )
)

m_sales_fig.update_traces(
                        hovertemplate = 'Year: %{x}<br>Amount: %{y}'
)



# plot 37 (toyota sales by category)



# transform data into a long format for plotting

toyota_sales_long = toyota_sales.melt(
                                    id_vars = 'category' , 
                                    var_name = 'year' , 
                                    value_name = 'amount of units sold'
)

# grouped bar chart

t_sales_fig = px.bar(
                    toyota_sales_long ,
                    x = 'year' ,
                    y = 'amount of units sold' ,
                    color = 'category' ,
                    title = 'Toyota Sales Volume by Category (2015-2023)' ,
                    color_discrete_map = {
                                    'Internal Combustion Engine': '#EB0A1E' ,  
                                    'Hybrid': '#58595B' ,  
                                    'Electric Vehicles': '#000000'
                                    } ,
                    barmode = 'group'
)

t_sales_fig.update_layout(
                        xaxis = dict(
                                    showgrid = True , 
                                    gridcolor = 'black'
                                ) ,
                        yaxis = dict(
                                    showgrid = True , 
                                    gridcolor = 'black' ,
                                    tickmode = 'linear' ,       # set tick mode to linear
                                    tick0 = 0 ,                 # start ticks at 0
                                    dtick = 300000
                                ) ,
                        width = 700 , 
                        height = 600 ,
                        plot_bgcolor = 'white' ,
                        paper_bgcolor = 'white' ,
                        font = dict(
                                    family = 'Arial' ,
                                    size = 12 ,
                                    color = 'black'
                                )   
)

t_sales_fig.update_traces(
                        hovertemplate = 'Year: %{x}<br>Amount: %{y}'
)



# plot 38 (volkswagen sales by category)



# transform data into a long format for plotting

vw_sales_long = vw_sales.melt(
                            id_vars = 'category' , 
                            var_name = 'year' , 
                            value_name = 'amount of units sold'
)

# create a grouped bar chart

v_sales_fig = px.bar(
                    vw_sales_long ,
                    x = 'year' ,
                    y = 'amount of units sold' ,
                    color = 'category' ,
                    title = 'Volkswagen Sales Volume by Category (2015-2023)' ,
                    color_discrete_map = {
                                        'Internal Combustion Engine': '#1F2F57',  
                                        'Hybrid': '#A8A8A8',  
                                        'Electric Vehicles': '#6091C3'
                                    } ,
                    barmode = 'group'
)

v_sales_fig.update_layout(
                        xaxis = dict(
                                    showgrid = True , 
                                    gridcolor='#A8A8A8'
                                ) ,
                        yaxis = dict(
                                    showgrid = True , 
                                    gridcolor = '#A8A8A8' ,
                                    tickmode = 'linear' ,  
                                    tick0 = 0 ,            
                                    dtick = 300000 
                                ) ,
                        width = 700 , 
                        height = 600 ,
                        plot_bgcolor = 'white' ,
                        paper_bgcolor = '#A8A8A8' ,
                        font = dict(
                                    family = 'Arial Rounded MT Bold' ,
                                    size = 12 ,
                                    color = 'black'
                                )
)

v_sales_fig.update_traces(
                        hovertemplate='Year: %{x}<br>Amount: %{y}'
)



# initialize the Dash app

app = Dash(__name__ , external_stylesheets=["/assets/styles.css?v=1"])

# define the app layout

app.layout = html.Div(
                    [

    # dropdown menu for navigation (with custom class)

    dcc.Dropdown(
                id = "dropdown" ,
                options = [
                            {"label" : "HOME" , "value" : "overview"} ,
                            {"label" : "AUDI" , "value" : "audi"} ,
                            {"label" : "BMW" , "value" : "bmw"} ,
                            {"label" : "MERCEDES-BENZ" , "value" : "mercedes"} ,
                            {"label" : "TOYOTA" , "value" : "toyota"} ,
                            {"label" : "VOLKSWAGEN" , "value" : "volkswagen"} ,
                            {"label" : "Laws & Regulations" , "value" : "laws_regulations"} ,
                            {"label" : "Charging Points Infrastructure" , "value" : "charging_points"} ,
                            {"label" : "Gas Stations Infrastructure" , "value" : "gas_stations"} ,
                            {"label" : "Environmental Impact" , "value" : "environment"}
                        ] ,
                value = "overview" ,                                        # default selection
                className = "dropdown-small-right" ,                        # apply custom class
                placeholder = "Select a section..." ,                       # placeholder text
            ) ,

    # content container

    html.Div(
            id = "tab-content" , 
            className = "tab-content"
        )
    ]
    )

# callback to dynamically update content

@app.callback(
            Output("tab-content" , "children") ,
            Input("dropdown" , "value")
)

def display_content(selected_tab) :

    content = html.Div(
                    [
                        html.H1("Not Found") , 
                        html.P("The selected tab does not exist.") ,
                        html.Img(
                                src = "/assets/image-1.png" ,  
                                alt = "Image1"
                        )
                    ] ,

                        className = "not-found" 

                    )
    
    if selected_tab == "overview" :

        content = html.Div(
                    [
                        html.H1(
                            "Cars, Currents, and Change" , 
                            className = "header"
                        ) ,

                        html.P(
                            "Explore the automotive industry's transformation." ,
                            className = "s-header"
                        ) ,

                        html.Ul(
                            [
                                html.Li("Insights into major brands.") ,
                                html.Li("Germany's EV charging infrastructure.") ,
                                html.Li("Sales trends, market shares, and sustainability.") ,
                                html.Li("Impact of policies like the 2035 ICE ban.")
                            ] ,

                            className = "intro-text" 

                        ) ,

                            html.Div(
                                [
                                    dcc.Graph(
                                            figure = car_sales_fig , 
                                            id = 'car_sales_fig' , 
                                            className = "car-sales-graph"
                                        ) ,
                                    html.Div(
                                        [
                                        
                                            html.P(
                                                    "World Car Sales." ,
                                                    className = "car-sales-text"
                                            ) ,
                                            html.Ul(
                                                [
                                                    html.Li("Global Chip Shortage 2021-2022;") ,
                                                    html.Li("Logistical backlogs and raw material shortages;") ,
                                                    html.Li("Rising EV demand;") ,
                                                    html.Li("Economic Recovery Post-COVID-19;") ,
                                                    html.Li("Inflation and Rising Prices.")
                                                ] ,

                                                className = "car-sales-insights-list" 
                                            ) ,
                                        ] ,

                                        className = "car-sales-text-container"

                                    ) ,     
                                ] ,

                                className = "car-sales-container" 
                                
                            ) ,

                            html.Div(
                                [
                                    html.P(
                                         "Car Market" ,
                                        className = "car-market-h"
                                        ) ,

                                    html.Ul(
                                        [
                                            html.Li("The global automotive industry is valued at over $4 trillion;") ,
                                            html.Li("Approximately 10,000 to 20,000 companies globally;") ,
                                            html.Li("The Asia-Pacific region dominates car manufacturing and sales.")
                                        ] ,

                                        className = "car-market-insights-list" 

                                    ) ,

        

                                    dcc.Graph(
                                            figure = global_market_share_fig , 
                                            id = 'global_market_share_fig' ,
                                            className = "global-market-graph"
                                        ) ,

                                    html.Div(
                                        [

                                            dcc.Graph(
                                                    figure = us_market_share_fig , 
                                                    id = 'us_market_share_fig' ,
                                                    className = "us-market-graph"
                                                ) ,
                                                
                                            dcc.Graph(
                                                    figure = europe_market_share_fig , 
                                                    id = 'europe_market_share_fig' ,
                                                    className = "europe-market-graph"
                                                )
                                        ] ,

                                        className = "graphs-wrapper"
                                    ) ,
                                ] , 

                                    className = "car-market-container"

                            ) ,

                            html.Div(
                                [
                                    html.P(
                                        "Global Giants" ,
                                        className = "global-giant-h"
                                    ) ,

                                    html.Ul(
                                        [
                                            html.Li("Top three premium automotive manufacturers and absolute market leaders;") ,
                                            html.Li("Toyota and Volkswagen lead the mainstream automotive market;") ,
                                            html.Li("Audi, BMW and Mercedes-Benz dominate the luxury car market.") 
                                        ] ,

                                        className = "text-global-g"
                                    ) ,

                                    html.Div(
                                        [

                                            dcc.Graph(
                                                    figure = big_three_sales_fig ,
                                                    id = "big_three_sales_fig" ,
                                                    className = "gbt-sales-graph"
                                            ) ,

                                            dcc.Graph(
                                                    figure = sales_tv_fig ,
                                                    id = "sales_tv_fig" ,
                                                    className = "tv-sales-graph"
                                            ) ,

                                            dcc.Graph(
                                                    figure = revenue_bg3_fig ,
                                                    id = "revenue_bg3_fig" ,
                                                    className = "r-bgt-graph"
                                            ) ,

                                            dcc.Graph(
                                                    figure = revenue_tv_fig ,
                                                    id = "revenue_tv_fig" ,
                                                    className = "r-tv-graph"
                                            ) ,
                                            
                                            dcc.Graph(
                                                    figure = revenue_growth_bg3_fig ,
                                                    id = "revenue_growth_bg3_fig" ,
                                                    className = "rg-bgt-graph"
                                            ) ,

                                            dcc.Graph(
                                                    figure = revenue_growth_tv_fig ,
                                                    id = "revenue_growth_tv_fig" ,
                                                    className = "rg-tv-graph"
                                            ) 
                                        ] ,

                                        className="graphs-g-wrapper"
                                    ),

                                ] ,

                                    className = "global-giants-container"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.Div(
                                                [
                                    
                                                    html.P(
                                                        "Germany's Automotive Market: New Car Registrations Overview" ,
                                                        className = "gam-new-reg-h"
                                                    ) ,

                                                    html.Ul(
                                                        [
                                                            html.Li("Germany has the largest car market in Europe;") ,
                                                            html.Li("Over 45 million registered vehicles;") ,
                                                            html.Li("Germany leads in new car registrations;") ,
                                                            html.Li("German government offers significant subsidies for purchasing EVs.")
                                                        ] ,

                                                        className = "text-g-cg"

                                                    ) ,

                                                ] ,

                                                    className = "text-section-wrapper" ,
                                            ) ,    

                                            dcc.Graph(
                                                    figure = total_reg_fig ,
                                                    id = "total_reg_fig" ,
                                                    className = "total-reg-graph"
                                            ) 
                                        ] ,

                                        className = "text-graph-wrapper" ,
                                    ) ,

                                    dcc.Graph(
                                            figure = diesel_reg_fig ,
                                            id = "diesel_reg_fig" ,
                                            className = "diesel-reg-graph"
                                    ) ,

                                    html.Div(
                                        [
                                            dcc.Graph(
                                                    figure = hybrid_reg_fig ,
                                                    id = "hybrid_reg_fig" ,
                                                    className = "hybrid-reg-graph"
                                            ) ,

                                            dcc.Graph(
                                                    figure = ev_reg_fig ,
                                                    id = "ev_reg_fig" ,
                                                    className = "ev-reg-graph"
                                            )

                                        ] ,

                                        className = "h-ev-graphs-wrapper" ,

                                    ) 

                                ] ,

                                    className = "ger-reg-container"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.Div(
                                                [

                                                    dcc.Graph(
                                                            figure = energy_prices_fig ,
                                                            id = "energy_prices_fig" ,
                                                            className = "en-pr-graph"
                                                    ) ,

                                                    dcc.Graph(
                                                            figure = energy_change_p_fig ,
                                                            id = "energy_change_p_fig" ,
                                                            className = "en-change-p-graph"
                                                    )
                                                ] ,

                                                className = "graphs-e-wrapper"

                                            ) ,

                                            html.Div(
                                                [        
                                                    html.P(
                                                        "Energy Prices" ,
                                                        className = "energy-price-text"
                                                    ) ,

                                                    html.Ul(
                                                        [
                                                            html.Li("Petrol prices influenced by global oil prices, taxes, and supply chain logistics;") ,
                                                            html.Li("The cost of electricity depending on the country and the energy mix;") ,
                                                            html.Li("Governments heavily influence electricity prices for charging to encourage the switch to EVs.")
                                                        ] ,

                                                        className = "text-en-prices"

                                                    ) ,

                                                ] ,

                                                className = "text-en-wrapper" 

                                            ) ,

                                        ] ,

                                        className="text-graphs-en-container"
                                    ) ,

                                ] ,

                                className = "energy-prices-container"       
                                    
                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [
                                            html.P(
                                                "Distribution of Fuel Sources" ,
                                                className = "fuel-sources-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Germany has 16,846 gas stations;") ,
                                                    html.Li("The first gas station in Germany was established in 1888 in Berlin;") ,
                                                    html.Li("For full tank it takes 2 to 5 minutes;") ,
                                                    html.Li("Germany has 73,889 publicly accessible charging points;") ,
                                                    html.Li("The first public charging station in Germany was installed in 1992 in Berglen;") ,
                                                    html.Li("For 0-100 it takes 4-8 hours on standard public charger and 40-60 minutes on fast one.")
                                                ] ,

                                                className = "fuel-insights-text"
                                            ) ,
                                        ] ,

                                        className = "top-middle-container"

                                    ) ,

                                    html.Div(
                                        [
                                            dcc.Graph(
                                                    figure = charging_points_map_fig ,
                                                    id = "charging_points_map_fig" ,
                                                    className = "charging-map"
                                            ) ,

                                            dcc.Graph(
                                                    figure = top5_gas_st_fig ,
                                                    id = "top5_gas_st_fig" ,
                                                    className = "gas-station-map"
                                            ) ,

                                        ] ,

                                        className = "maps-container"

                                    ) ,

                                    html.Div(
                                        [

                                            html.P(
                                                "Distribution of charging points in Federal States" ,
                                                className = "dist-cp-fs-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Baden-Württemberg was among the early adopters of charging stations;") ,
                                                    html.Li("In June 2010, partnered with Daimler AG and EnBW to launch the 'e-mobility Baden-Württemberg' project;") ,
                                                    html.Li("The state allocated €28.5 million to support electric vehicle research through 2014;") ,
                                                    html.Li("North Rhine-Westphalia was one of the first regions to integrate EV infrastructure;") ,
                                                    html.Li("In 2008, the 'E-Mobility Berlin' project, led by RWE AG and Daimler, launched one of Germany's first large-scale efforts, installing charging stations.")
                                                ] ,

                                                className = "states-efforts"
                                            ) ,

                                            dcc.Graph(
                                                    figure = total_cp_fs_fig ,
                                                    id = "total_cp_fs_fig" ,
                                                    className = "total-cp-fs-graph"
                                            ) ,

                                        ] ,

                                        className = "distribution-container"
                                    
                                    ) ,

                                    html.Div(
                                        [

                                            dcc.Graph(
                                                    figure = nlp_fig ,
                                                    id = "nlp_fig" ,
                                                    className = "nlp-graph"
                                            ) ,

                                            dcc.Graph(
                                                    figure = slp_fig ,
                                                    id = "slp_fig" ,
                                                    className = "slp-graph"
                                            ) 

                                        ] ,

                                        className = "nlp-slp-container"
                                    ) ,

                                ] ,

                                    className = "distr-cp-fs-container"

                            ) ,

                            html.Div(
                                [
                                    html.P(
                                        "Prediction of amount of charging points by 2035" ,
                                        className = "prediction-h"
                                    ) ,

                                    html.Ul(
                                        [
                                            html.Li("The European Union has legislated a ban on the sale of new petrol and diesel cars by 2035;") ,
                                            html.Li("The ICE ban was officially approved in June 2022;") ,
                                            html.Li("It mandates the end of sales of new ICE cars by 2035;") ,
                                            html.Li("It's designed to help the EU meet its ambitious climate goals;") ,
                                            html.Li("Includes hybrid cars as well, as the focus is specifically on emission-free vehicles;") ,
                                            html.Li("The success of the ban depends heavily on the development of a robust charging infrastructure across the EU.")
                                        ] ,

                                        className = "ice-ban-text"

                                    ) ,

                                    dcc.Graph(
                                            figure = ttcp_fig ,
                                            id = "ttcp_fig" ,
                                            className = 'predict-graph'
                                    )

                                ] ,

                                    className = "predict-container"

                            )
        
                    ] ,

                        className = "home-page"

                    )
        
    elif selected_tab == "audi" :

        content = html.Div(
                        [
                            
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H1(
                                                    "AUDI" , 
                                                    className = "h-audi"
                                            ) ,

                                            html.Img(
                                                    src = "/assets/audi-logo.png" ,  
                                                    alt = "audi-logo" ,
                                                    className = "audi-logo"
                                            ) ,
                                        ] ,

                                        className = "h-audi-logo-container" 
                                    ) ,

                                    html.P(
                                        "This section provides an in-depth look at Audi's financial and sales performance between 2015 and 2023." ,
                                        className = "intro-audi-h"
                                    ) ,

                                ] ,

                                className = "audi-intro-text"

                            ) ,

                            html.Div(
                                [
                                    
                                    html.Div(
                                        [
                                            html.P(
                                                "Strategy Overview:" ,
                                                className = "h2-audi"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Focused on optimizing ICE technology and launched 'Strategy 2025';") ,
                                                    html.Li("2017-2019: Strengthened commitment to EVs with the 'Consistently Audi' strategy;") ,
                                                    html.Li("2020-2021: Accelerated EV focus, announcing the phase-out of new ICE models by 2033;"),
                                                    html.Li("2022-2023: Transitioned to an all-electric future, positioning Audi as a leader in green mobility and EV innovation.")
                                                ] ,

                                                className = "audi-strategy-list"
                                            ) 

                                        ] ,

                                        className = "audi-strategy-container"
                                    ) ,

                                    html.Div(
                                        [
                                            html.P(
                                                "Laws and regulations which impacted brand:" ,
                                                className = "h3-audi"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Dieselgate Fallout and WLTP Testing Regulations (2017-2018)") ,
                                                    html.Li("EV Subsidies and Incentives (2019 onward)") ,
                                                    html.Li("CO₂ Emission Performance Standards (2020-2021)") ,
                                                    html.Li("CO₂ Emission Performance Fines (2020-2021)") ,
                                                    html.Li("EU Taxonomy Regulation (2021)") ,
                                                    html.Li("Euro 7 Emission Standards (2022)")
                                                ] ,

                                                className = "audi-laws-impact"

                                            )

                                        ] ,

                                        className = "audi-laws-container"
                                    )        
                                ] ,

                                className = "audi-1-container"
                            ) ,

                            html.Div(
                                [
                                    html.Div(
                                        [

                                            dcc.Graph(
                                                figure = a_revenue_fig ,
                                                id = "a_revenue_fig" ,
                                                className = "a_revenue_graph"
                                            ) ,

                                            dcc.Graph(
                                                figure = a_revenue_growth_fig ,
                                                id = "a_revenue_growth_fig" ,
                                                className = "a_revenue_growth_graph"
                                            )

                                        ] ,

                                        className = "audi-revenue-graphs"
                                    ) ,

                                    html.Div(
                                        [

                                            html.P(
                                                "Impact" ,
                                                className = "audi-revenue-impact-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Audi optimized internal combustion engine (ICE) models and focused on operational efficiency;") ,
                                                    html.Li("2016-2017:  Early progress in the 'Strategy 2025' plan, with increased investments in electric vehicle (EV) research and expanding global markets;") ,
                                                    html.Li("2017-2018: Introduction of WLTP emissions testing caused production and delivery delays;") ,
                                                    html.Li("2017-2018: Ongoing fallout from the Dieselgate scandal hurt diesel sales and trust;") ,
                                                    html.Li("2018-2019: Improved delivery timelines post-WLTP disruptions and increased demand for premium vehicles, especially in emerging markets;") ,
                                                    html.Li("2019-2020: COVID-19 pandemic disrupted global supply chains and vehicle production;") ,
                                                    html.Li("2020-2021: Strong post-pandemic recovery in vehicle demand;") ,
                                                    html.Li("2020-2021: Growing success of Audi's electric vehicles (e-tron models) and premium market positioning;") ,
                                                    html.Li("2021-2022: Continued momentum in EV sales and high-end vehicle demand, supported by EV incentives and green policies in the EU;") ,
                                                    html.Li("2022-2023: Accelerated adoption of electric vehicles, with models like the Q4 e-tron and premium offerings driving sales;") ,
                                                    html.Li("2022-2023: Price increases to manage inflation and strong recovery in global markets, particularly in Europe and China.")
                                                ] ,

                                                className = "audi-revenue-reasons"

                                            )

                                        ] ,

                                        className = "audi-revenue-text"

                                    )

                                ] ,
                                
                                className = "audi-revenue-container"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.P(
                                                "Sales:" ,
                                                className = "audi-sales-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("ICE Dominance (2015-2018): Strong demand but declining due to regulations and Dieselgate;") ,
                                                    html.Li("Transition Phase (2019-2021): Drop in ICE sales while hybrids and EVs emerged slowly;") ,
                                                    html.Li("EV Growth (2022-2023): Driven by green policies, consumer demand, and Audi's expanding electrification strategy.")
                                                ] ,

                                                className = "audi-sales-text"

                                            )

                                        ] , 
                                        
                                        className = "audi-sales-text-container"
                                        
                                    ) ,

                                    dcc.Graph(
                                        figure = a_sales_fig ,
                                        id = "a_sales_fig" ,
                                        className = "a_sales_graph"
                                    )

                                ] ,

                                className = "audi-sales-container"
                            )

                        ] ,

                        className = "audi-page"

                    )
        
    elif selected_tab == "bmw" :

        content = html.Div(
                        [

                            html.Div(
                                [
                                    html.Div(
                                        [

                                            html.H1(
                                                    "BMW" ,
                                                    className = "h-bmw"
                                            ) ,

                                            html.Img(
                                                    src = "/assets/bmw-logo.png" ,  
                                                    alt = "bmw-logo" ,
                                                    className = "bmw-logo"
                                            ) ,

                                        ] ,

                                        className = "h-bmw-logo-container"

                                    ) ,

                                    html.P(
                                        "This section provides an in-depth look at BMW's financial and sales performance between 2015 and 2023." ,
                                        className = "intro-bmw-h"
                                    ) 

                                ] ,

                                className = "bmw-intro-text"

                            ) ,

                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                "Strategy Overview:" ,
                                                className = "h2-bmw"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Broadened innovation and launched 'Strategy NUMBER ONE > NEXT' , focusing on digitalization and electrification;") ,
                                                    html.Li("2017-2019: Balanced ICE and alternative powertrains with the 'Power of Choice' strategy, increased EV and hybrid investments;") ,
                                                    html.Li("2020-2021: Accelerated electrification and sustainability efforts while recovering from pandemic challenges;") ,
                                                    html.Li("2022-2023: Emphasized full electrification, achieving record revenues and reduced ICE reliance.") 
                                                ] ,

                                                className = "bmw-strategy-list"
                                            ) 

                                        ] ,

                                        className = "bmw-strategy-container" 

                                    ) ,

                                    html.Div(
                                        [
                                            html.P(
                                                "Laws and regulations which impacted brand:" ,
                                                className = "h3-bmw"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("CO₂ Emission Performance Standards (2019);") ,
                                                    html.Li("Incentives for Zero- and Low-Emission Vehicles (ZLEV);") ,
                                                    html.Li("Stricter CO₂ Emission Targets (2023 Amendment);") ,
                                                    html.Li("End-of-Life Vehicles (ELV) Regulation.")
                                                ] ,

                                                className = "bmw-laws-impact"

                                            ) 

                                        ] ,

                                        className = "bmw-laws-container"

                                    )

                                ] ,

                                className = "bmw-1-container"

                            ) ,

                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                figure = b_revenue_fig ,
                                                id = "b_revenue_fig" ,
                                                className = "b_revenue_graph"
                                            ) ,

                                            dcc.Graph(
                                                figure = b_revenue_growth_fig ,
                                                id = "b_revenue_growth_fig" ,
                                                className = "b_revenue_growth_graph"
                                            )

                                        ] ,

                                        className = "bmw-revenue-graphs"

                                    ) ,

                                    html.Div(
                                        [
                                            html.P(
                                                "Impact:" ,
                                                className = "bmw-revenue-impact-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Continued global demand for BMW's premium vehicles, particularly in the SUV segment;") ,
                                                    html.Li("2016-2017: Growth in key markets, including China and the United States;") ,
                                                    html.Li("2017-2018: Transition to the Worldwide Harmonized Light Vehicles Test Procedure caused production adjustments and delivery delays;") ,
                                                    html.Li("2018-2019: Stabilization post-WLTP disruptions improved production and deliveries, high demand for BMW's SUV models;") ,
                                                    html.Li("2019-2020: COVID-19 Pandemic, challenges in sourcing components affected manufacturing;") ,
                                                    html.Li("2020-2021:  Rebound in consumer demand and easing of lockdowns;") ,
                                                    html.Li("2021-2022: Expansion of the electric vehicle lineup attracting environmentally conscious consumers;") ,
                                                    html.Li("2022-2023: Models like the iX and i4 driving sales, economic improvements in regions like Europe and China boosting sales.")
                                                ] ,

                                                className = "bmw-revenue-reasons"

                                            ) 

                                        ] ,

                                        className = "bmw-revenue-text"

                                    )

                                ] ,

                                className = "bmw-revenue-container"
                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.P(
                                                "Sales:" ,
                                                className = "bmw-sales-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2019: ICE vehicles remained the dominant category due to consumer preference, especially for BMW's SUVs (X3, X5);") ,
                                                    html.Li("2019-2020: Transition period - Hybrids served as a bridge between ICE and fully electric vehicles;") ,
                                                    html.Li("2021-2023: Accelerated Growth of EV, EU regulations promoting zero-emission vehicles (CO₂ targets, incentives) increased EV demand.")
                                                ] ,

                                                className = "bmw-sales-text"
                                            )

                                        ] ,

                                        className = "bmw-sales-text-container"

                                    ) ,

                                    dcc.Graph(
                                        figure = b_sales_fig ,
                                        id = "b_sales_fig" ,
                                        className = "b_sales_graph"
                                    )

                                ] ,

                                className = "bmw-sales-container"

                            )

                        ] ,

                        className = "bmw-page"
                    )
        
    elif selected_tab == "mercedes" :

        content = html.Div(
                        [

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.H1(
                                                    "MERCEDES-BENZ" ,
                                                    className = "h-mercedes"
                                            ) ,

                                            html.Img(
                                                    src = "/assets/mercedes-logo.png" ,  
                                                    alt = "mercedes-logo" ,
                                                    className = "mercedes-logo"
                                            ) ,

                                        ] ,

                                        className = "h-mercedes-logo-container"

                                    ) ,

                                     html.P(
                                        "This section provides an in-depth look at Mercedes-Benz's financial and sales performance between 2015 and 2023." ,
                                        className = "intro-mercedes-h"
                                    ) 

                                ] ,

                                className = "mercedes-intro-text"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.P(
                                                "Strategy Overview:" ,
                                                className = "h2-mercedes"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Initial focus on electrification with the launch of 'Concept EQ';") ,
                                                    html.Li("2017-2019: Intensified efforts in electric vehicles (EV) development, maintaining consistent investment in research and innovation;") ,
                                                    html.Li("2020-2021: Strategic shift to 'Electric first' , marking a significant acceleration in EV focus;") ,
                                                    html.Li("2022-2023: Full commitment to an 'Electric Only' strategy, aligning with sustainability goals.")
                                                ] ,

                                                className = "mercedes-strategy-list"

                                            )

                                        ] ,

                                        className = "mercedes-strategy-container" 

                                    ) ,

                                    html.Div(
                                        [
                                            html.P(
                                                "Laws and regulations which impacted brand:" ,
                                                className = "h3-mercedes"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Incentives for Zero- and Low-Emission Vehicles (ZLEVs);") ,
                                                    html.Li("Support for Electric Mobility;") ,
                                                    html.Li("Stricter CO₂ Emission Standards;") ,
                                                    html.Li("Euro 7 Emission Standards;") ,
                                                    html.Li("Ban on Combustion Engine Vehicles by 2035.")
                                                ] ,

                                                className = "mercedes-laws-impact"

                                            ) 

                                        ] ,

                                        className = "mercedes-laws-container"

                                    )

                                ] ,

                                className = "mercedes-1-container"

                            ) ,

                            html.Div(
                                [
                                    html.Div(
                                        [

                                            dcc.Graph(
                                                figure = m_revenue_fig ,
                                                id = "m_revenue_fig" ,
                                                className = "m_revenue_graph"
                                            ) ,

                                            dcc.Graph(
                                                figure = m_revenue_growth_fig ,
                                                id = "m_revenue_growth_fig" ,
                                                className = "m_revenue_growth_graph"
                                            ) 

                                        ] ,

                                        className = "mercedes-revenue-graphs"

                                    ) ,

                                    html.Div(
                                        [
                                            html.P(
                                                "Impact:" ,
                                                className = "mercedes-revenue-impact-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Success in premium ICE models. Strong market demand in Europe and China supported growth;") ,
                                                    html.Li("2016-2017: Focused on expanding its premium vehicle lineup and rolled out successful luxury models, such as the S-Class;") ,
                                                    html.Li("2017-2018: Implementation of WLTP disrupted production and delivery schedules, leading to short-term delays, continued fallout from Dieselgate indirectly impacted diesel car sales;") ,
                                                    html.Li("2018-2019: Streamlined operations post-WLTP disruptions and strong sales in China and the U.S., particularly for SUVs and high-end luxury models;") ,
                                                    html.Li("2019-2020: COVID-19 pandemic;") ,
                                                    html.Li("2020-2021: Ongoing pandemic recovery challenges, semiconductor shortages, and continued production bottlenecks limited output;") ,
                                                    html.Li("2021-2022: Strong post-pandemic recovery and rebound in premium vehicle demand, Launch of the 'Electric First' strategy, with models like the EQS and EQE gaining traction in the electric luxury market;") ,
                                                    html.Li("2022-2023: High demand for luxury and premium vehicles globally, with China and Europe leading sales.")
                                                ] ,

                                                className = "mercedes-revenue-reasons"

                                            )

                                        ] ,

                                        className = "mercedes-revenue-text"

                                    )

                                ] ,

                                className = "mercedes-revenue-container"

                            ) ,

                            html.Div(
                                [
                                    html.Div(
                                        [

                                            html.P(
                                                "Sales:" ,
                                                className = "mercedes-sales-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2019: High market demand for premium ICE vehicles in regions like Europe, China, and the U.S.;") ,
                                                    html.Li("2019-2021: Popularity of hybrid versions of flagship models like the C-Class and E-Class contributed to steady growth;") ,
                                                    html.Li("2021-2023: Enhanced EV charging networks in Europe and China removed key barriers to EV adoption, supporting higher sales.")
                                                ] ,

                                                className = "mercedes-sales-text" 

                                            )

                                        ] ,

                                        className = "mercedes-sales-text-container"

                                    ) ,

                                    dcc.Graph(
                                        figure = m_sales_fig ,
                                        id = "m_sales_fig" ,
                                        className = "m_sales_graph"
                                    )

                                ] ,

                                className = "mercedes-sales-container"

                            )

                        ] ,

                        className = "mercedes-page"

                ) 
        
    elif selected_tab == "toyota" :

        content = html.Div(
                        [
                            
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H1(
                                                "TOYOTA" ,
                                                className = "h-toyota"
                                            ) ,

                                            html.Img(
                                                    src = "/assets/toyota-logo.png" ,  
                                                    alt = "toyota-logo" ,
                                                    className = "toyota-logo"
                                            ) 

                                        ] ,

                                        className = "h-toyota-logo-container"

                                    ) ,

                                    html.P(
                                        "This section provides an in-depth look at Toyota's financial and sales performance between 2015 and 2023." ,
                                        className = "intro-toyota-h"
                                    ) 

                                ] ,

                                className = "toyota-intro-text"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.P(
                                                "Strategy Overview:" ,
                                                className = "h2-toyota"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Focused on hybrid technology as a competitive advantage, laying the foundation for gradual electrification;") ,
                                                    html.Li("2017-2020: Announced a broader electrification strategy while maintaining hybrids as a core focus and exploring hydrogen fuel cell technology;") ,
                                                    html.Li("2021: Adopted a multi-pathway approach to carbon neutrality, balancing investments in hybrids, battery EVs, and hydrogen technologies;") ,
                                                    html.Li("2022-2023: Accelerated the development of battery EV platforms while emphasizing technology diversity to adapt to global market needs.")
                                                ] ,

                                                className = "toyota-strategy-list"

                                            )

                                        ] ,

                                        className = "toyota-strategy-container"

                                    ) ,

                                    html.Div(
                                        [
                                            html.P(
                                                "Laws and regulations which impacted brand:" ,
                                                className = "h3-toyota"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Super-Credits for Low Emission Vehicles (2015);") ,
                                                    html.Li("Stricter CO₂ Emission Standards (2019/2020);") ,
                                                    html.Li("Phase-Out of Internal Combustion Engine Vehicles (2023).")
                                                ] ,

                                                className = "toyota-laws-impact"

                                            )

                                        ] ,

                                        className = "toyota-laws-container"

                                    )

                                ] ,

                                className = "toyota-1-container"

                            ) ,

                            html.Div(
                                [
                                    
                                    html.Div(
                                        [

                                            dcc.Graph(
                                                figure = t_revenue_fig ,
                                                id = "t_revenue_fig" ,
                                                className = "t_revenue_graph"
                                            ) ,

                                            dcc.Graph(
                                                figure = t_revenue_growth_fig ,
                                                id = "t_revenue_growth_fig" ,
                                                className = "t_revenue_growth_graph"
                                            )

                                        ] ,

                                        className = "toyota-revenue-graphs"

                                    ) ,

                                    html.Div(
                                        [

                                            html.P(
                                                "Impact:" ,
                                                className = "toyota-revenue-impact-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: driven by operational efficiency and hybrid technology leadership;") ,
                                                    html.Li("2016-2017: Market fluctuations and increased competition in major markets like China;") ,
                                                    html.Li("2017-2018: Launch of an electrification strategy and new hybrid models increased sales in Europe. Improved operational efficiency and recovery in emerging markets also contributed;") ,
                                                    html.Li("2018-2019: continued leadership in hybrid vehicles and strong demand in North America and Asia;") ,
                                                    html.Li("2019-2020: Impact of the COVID-19 pandemic, including production shutdowns, disrupted supply chains, and reduced global demand for vehicles;") ,
                                                    html.Li("2020-2021: Lingering effects of the pandemic combined with semiconductor shortages significantly disrupted vehicle production. Economic uncertainty reduced consumer spending;") ,
                                                    html.Li("2021-2022: Strong post-pandemic recovery in demand, particularly for hybrids;") ,
                                                    html.Li("2022-2023: Accelerated electrification efforts, improved supply chain stability, and recovery in global markets, particularly Europe and Asia.")
                                                ] ,

                                                className = "toyota-revenue-reasons"

                                            )

                                        ] ,

                                        className = "toyota-revenue-text"

                                    )

                                ] ,

                                className = "toyota-revenue-container"

                            ) ,

                            html.Div(
                                [
                                    
                                    html.Div(
                                        [
                                            html.P(
                                                "Sales:" ,
                                                className = "toyota-sales-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Maintaine a strong foothold in ICE sales, especially in markets like North America, Africa, and Asia;") ,
                                                    html.Li("Steady growth in hybrid vehicle sales, particularly in Europe and Japan, where sustainability initiatives were prioritized;") ,
                                                    html.Li("While ICE sales suffered during the COVID-19 pandemic, hybrid sales remained stable due to growing interest in environmentally friendly vehicles;") ,
                                                    html.Li("Toyota faced criticism for being slower in transitioning to EVs compared to competitors like Tesla and Volkswagen;") ,
                                                    html.Li("Toyota's strategy of prioritizing hybrids ensured consistent growth amid regulatory changes. The steady rise in hybrid sales correlates with global sustainability initiatives, while ICE sales reflect strong demand in emerging markets.")
                                                ] ,

                                                className = "toyota-sales-text"

                                            )

                                        ] ,

                                        className = "toyota-sales-text-container"

                                    ) ,

                                    dcc.Graph(
                                        figure = t_sales_fig ,
                                        id = "t_sales_fig" ,
                                        className = "t_sales_graph"
                                    )

                                ] ,

                                className = "toyota-sales-container"

                            )

                        ] ,

                        className = "toyota-page"

                    )
        
    elif selected_tab == 'volkswagen' :

        content = html.Div(
                        [
                            html.Div(
                                [
                                    
                                    html.Div(
                                        [
                                            html.H1(
                                                "VOLKSWAGEN" ,
                                                className = "h-volkswagen"
                                            ) ,

                                            html.Img(
                                                    src = "/assets/volkswagen-logo.png" ,  
                                                    alt = "volkswagen-logo" ,
                                                    className = "volkswagen-logo"
                                            ) 

                                        ] ,

                                        className = "h-volkswagen-logo-container"

                                    ) ,

                                     html.P(
                                        "This section provides an in-depth look at Volkswagen's financial and sales performance between 2015 and 2023." ,
                                        className = "intro-volkswahen-h"
                                    ) 

                                ] ,
                                
                                className = "volkswagen-intro-text"

                            ) ,

                            html.Div(
                                [
                                    
                                    html.Div(
                                        [
                                            html.P(
                                                "Strategy Overview:" ,
                                                className = "h2-volkswagen"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Began early steps toward electrification and efficiency improvements;") ,
                                                    html.Li("2017-2019: Accelerated focus on electric vehicles (EVs) and future mobility;") ,
                                                    html.Li("2020-2021: Strategy centered on increasing EV production to align with climate goals;") ,
                                                    html.Li("2022-2023: Solidified political alignment toward an all-electric future, increasing global competitiveness.")
                                                ] ,

                                                className = "volkswagen-strategy-list"

                                            )

                                        ] ,

                                        className = "volkswagen-strategy-container"

                                    ) ,

                                    html.Div(
                                        [

                                            html.P(
                                                "Laws and regulations which impacted brand:" ,
                                                className = "h3-volkswagen"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("CO₂ Emission Performance Standards Compliance (2021);") ,
                                                    html.Li("Alignment with EU's Climate Neutrality Goals (2021-2023);") ,
                                                    html.Li("Diesel Emissions Scandal Repercussions (2015 onwards);") ,
                                                    html.Li("Stricter CO₂ Emission Targets (2025 and Beyond);") ,
                                                    html.Li("Potential Financial Penalties for Non-Compliance (2025).")
                                                ] ,

                                                className = "volkswagen-laws-impact"

                                            )

                                        ] ,

                                        className = "volkswagen-laws-container"

                                    )

                                ] ,

                                className = "volkswagen-1-container"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            dcc.Graph(
                                                figure = v_revenue_fig ,
                                                id = "v_revenue_fig" ,
                                                className = "v_revenue_graph"
                                            ) ,

                                            dcc.Graph(
                                                figure = v_revenue_growth_fig ,
                                                id = "v_revenue_growth_fig" ,
                                                className = "v_revenue_growth_graph"
                                            )

                                        ] ,

                                        className = "volkswagen-revenue-graphs"

                                    ) ,

                                    html.Div(
                                        [

                                            html.P(
                                                "Impact:" ,
                                                className = "volkswagen-revenue-impact-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("2015-2016: Despite fallout from the Dieselgate scandal, Volkswagen maintained stable revenue due to a strong portfolio of combustion engine vehicles;") ,
                                                    html.Li("2016-2017: Dieselgate consequences intensified, leading to legal penalties, reputational damage, and reduced diesel vehicle sales, corporate restructuring;") ,
                                                    html.Li("2017-2018: Increased demand in global markets, particularly China and emerging economies;") ,
                                                    html.Li("2018-2019: Growth in emerging markets and strong performance of popular models like the Golf and Tiguan;") ,
                                                    html.Li("2019-2020: COVID-19 pandemic;") ,
                                                    html.Li("2020-2021: Early success of Volkswagen's electric models (ID.3 and ID.4) aligned with global EV incentives;") ,
                                                    html.Li("2021-2022: Global semiconductor shortage impacted production capacity and delivery schedules;") ,
                                                    html.Li("2022-2023: Strong government support for EVs in the EU contributed to revenue resurgence.")
                                                ] ,

                                                className = "volkswagen-revenue-reasons"

                                            )

                                        ] ,

                                        className = "volkswagen-revenue-text"

                                    )

                                ] ,

                                className = "volkswagen-revenue-container"

                            ) ,

                            html.Div(
                                [

                                    html.Div(
                                        [

                                            html.P(
                                                "Sales:" ,
                                                className = "volkswagen-sales-h"
                                            ) ,

                                            html.Ul(
                                                [
                                                    html.Li("Stricter emission standards and phase-out timelines for ICE vehicles incentivized Volkswagen to invest in EVs and reduce reliance on traditional engines;") ,
                                                    html.Li("Hybrids gained traction as a transitional option, particularly in regions where EV infrastructure remained underdeveloped;") ,
                                                    html.Li("EU regulations, including the CO₂ fleet emission targets and upcoming ICE bans (2035), drove EV production and consumer demand.")
                                                ] ,

                                                className = "volkswagen-sales-text"

                                            )

                                        ] ,

                                        className = "volkswagen-sales-text-container"

                                    ) ,

                                    dcc.Graph(
                                        figure = v_sales_fig ,
                                        id = "v_sales_fig" ,
                                        className = "v_sales_graph"
                                    )

                                ] ,

                                className = "volkswagen-sales-container"

                            )

                        ] ,

                        className = "volkswagen-page"
                )
        
    elif selected_tab == "laws_regulations" :

        content = html.Div(
                        [
                            
                            html.P(
                                "Coming Soon..." ,
                                className = "coming-soon"
                            )

                        ]

                    )
        
    elif selected_tab == "charging_points" :

        content = html.Div(
                        [

                            html.P(
                                "Coming Soon..." ,
                                className = "coming-soon"
                            )

                        ]

                    )
        
    elif selected_tab == "gas_stations" :

        content = html.Div(
                        [

                            html.P(
                                "Coming Soon..." ,
                                className = "coming-soon"
                            )

                        ]
                    )
        
    elif selected_tab == "environment" :

        content = html.Div(
                        [

                            html.P(
                                "Coming Soon..." ,
                                className = "coming-soon"
                            )
                            
                        ]
                    )
        
    return content

if __name__ == "__main__" :
    app.run_server(port=8091)
