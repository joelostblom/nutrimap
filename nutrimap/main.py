import math
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_labs as dl
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_html_components as html

# TODO add instructions from old dashboard
# TODO add option to normalize values to per 1000 kcal or similar, this would
# be more fair for food that is either dry weight or wet weight. Also it makes
# sense how we want to budget our ~2500 kcal per day in terms of what we eat.
# There is also of course a fillness factor that determines it, but this would
# kind of be fiber and protein per kcal and weight or something like that
# TODO Include the ANDI score for nutrient density https://www.drfuhrman.com/blog/128/andi-food-scores-rating-the-nutrient-density-of-foods
# TODO include someting realted to most ost efficient food? https://www.sciencedirect.com/science/article/abs/pii/S2212267213003067
# TODO Could add a step here in the beginning where one can search through all
# veggies etc in the entire data base by reading in all the neames as a list
# and then only reading one row from the full data frame

root_dir = Path(__file__).parents[1]
foods = pd.read_csv(root_dir / 'data' / 'processed' / 'foods.csv', index_col=0)
# RDI
rdis = pd.read_csv(root_dir / 'data' / 'processed' / 'matched_rdi_sr_nih.csv', comment='#')
def compute_rdi_proportion(row):
    '''Calculate the proportion of the RDI contained in each nutrient'''
    new_row = pd.Series(dtype=float)
    for col_name in row.index:
        nutrient_rdi = rdis.loc[rdis['MatchedNutrient'] == col_name, 'Amount'].values[0]
        rdi_proportion = round(100 * row[col_name] / nutrient_rdi, 3)
        # Round to 2 significant digits https://stackoverflow.com/a/48812729/2166823
        new_row.loc[col_name] = rdi_proportion # 
    return new_row

foods = foods.apply(compute_rdi_proportion, axis=1)

food_groups = {
    # TODO add corn on the cob as veggie
    'grains': ['Quinoa, uncooked',  'Amaranth grain, uncooked', 'Oats', 'Barley, pearled, raw', 'Corn grain, yellow', 
               'Buckwheat', 'Rice, brown, long-grain, raw', 'Wild rice, raw',
               'Millet, raw', 'Bulgur, dry', 'Spelt, uncooked', 'Wheat, durum',
               'Wheat, hard red winter', 'Sorghum grain',
               'Wheat, kamut khorasan, uncooked',
               'Rice, white, long-grain, regular, raw, unenriched', 
               'Teff, uncooked', 'Rye grain'],
    'vegetables': ['Brussels sprouts, raw', 'Beets, raw', 'Broccoli, raw', 
                   'Cauliflower, raw', 'Eggplant, raw', 'Tomatoes, red, ripe, raw, year round average',
                   'Peas, green, frozen, unprepared'],
    'greens': ['Kale, raw', 'Spinach, raw', 'Lettuce, cos or romaine, raw',
               'Chard, swiss, raw', 'Arugula, raw', 'Collards, raw',
               'Lettuce, iceberg (includes crisphead types), raw', 'Beet greens, raw',
               'Mustard greens, raw', 'Cabbage, chinese (pak-choi), raw',
               'Cabbage, raw', ],
    'legumes': ['Beans, black turtle, mature seeds, raw', 'Lentils, raw',
                'Lentils, pink or red, raw', 'Beans, snap, green, raw',
                'Soybeans, green, raw', 'Beans, pinto, mature seeds, sprouted, raw',
                'Beans, adzuki, mature seeds, raw',
                'Beans, black, mature seeds, raw',
                'Beans, kidney, all types, mature seeds, raw',
                'Beans, pinto, mature seeds, raw',
                'Beans, small white, mature seeds, raw',
                'Soybeans, mature seeds, raw',
                'Broadbeans (fava beans), mature seeds, raw', 'Peas, green, raw',
                'Chickpeas (garbanzo beans, bengal gram), mature seeds, raw',
                'Peas, green, split, mature seeds, raw'],
    'nuts': [f'Nuts, {x.lower()}' for x in ['Brazilnuts, dried, unblanched',
             'Cashew nuts, raw',
             'Hazelnuts or filberts', 
             'Macadamia nuts, raw', 
             'Pine nuts, dried', 'Pistachio nuts, raw', 'Walnuts, english',
             'Coconut meat, dried (desiccated), not sweetened']] + ['Peanuts, all types, raw'],
    'fruits': ["Apples, raw, with skin",
               'Pineapple, raw, all varieties', 'Plums, raw', 'Pears, raw',
               'Apricots, raw', 'Avocados, raw, all commercial varieties',
               'Blackberries, frozen, unsweetened', 'Blueberries, raw',
               'Cranberries, raw', 'Raspberries, raw', 'Clementines, raw',
               'Strawberries, raw', 'Dates, medjool', 'Plantains, green, raw',
               'Pomegranates, raw', 'Bananas, raw', 'Plantains, yellow, raw',
               'Kiwifruit, green, raw', 'Figs, dried, uncooked', 'Oranges, raw, all commercial varieties',
               'Apricots, dried, sulfured, uncooked', 'Olives, ripe, canned (small-extra large)',
               'Raisins, dark, seedless'],
    'meats': ['Fish, salmon, atlantic, farmed, raw', 'Fish, salmon, atlantic, wild, raw',
              'Fish, cod, atlantic, raw', 'Chicken, broiler or fryers, breast, skinless, boneless, meat only, raw',
              'Pork, fresh, ground, raw',  'Beef, grass-fed, ground, raw', 'Egg, whole, raw, fresh', ]
}

nutrient_groups = dict(
    macros = [
        'Energy',
        'Carbs',
        'Protein',
        'Fiber',
        'Fat',
    ],

    detailed_macros =  [
        'Sugar',
        'Fat (mono)',
        'Fat (poly)',
        'Fat (sat)',
        'Cholesterol',
    ],

    minerals = [
        'Calcium',
        'Copper',
        'Iron',
        'Magnesium',
        'Manganese',
        'Phosphorus',
        'Potassium',
        'Selenium',
        'Sodium',
        'Zinc'
    ],

# TODO shorten names by removing "vitamin" and adding suffixes https://en.wikipedia.org/wiki/B_vitamins
        # add b1 k2 etc annotation
    vitamins = [
        'Thiamin (B1)',
        'Riboflavin (B2)',
        'Niacin (B3)',
        'Pantothenic acid (B5)',
        'Pyridoxine (B6)',
        'Folate (B9)',
        'Cobalmins (B12)',
        'Vitamin A',
        'Vitamin C',
        'Vitamin D (D2 + D3)',
        'Vitamin E',
        'Vitamin K',
        # 'Vitamin K (Dihydrophylloquinone)',
        # 'Vitamin K (Menaquinone-4)',
        # 'Vitamin K (phylloquinone)'
    ],

# eaas plus cysteine and tyrosine
    aas = [
        'Cystine',
        'Histidine',
        'Isoleucine',
        'Leucine',
        'Lysine',
        'Methionine',
        'Phenylalanine',
        'Threonine',
        'Tryptophan',
        'Tyrosine',
        'Valine',
    ],

    caretonoids = [
        'Lycopene',
        'Lutein + zeaxanthin',
        'alpha-Carotene',
        'beta-Carotene',
        # 'Retinol',
        'beta-Cryptoxanthin',
    ],
)

# App layout and components
app = dash.Dash(__name__, plugins=[dl.plugins.FlexibleCallbacks()])
server = app.server
tpl = dl.templates.DbcSidebar(app, title="", sidebar_columns=3)

# Header bar
collapse_button = html.Div(
    [
        dbc.Button(
            "Learn more",
            id="collapse-button",
            className="mb-3",
            outline=False,
            style={
                'margin-top': '15px',
                'width': '120px',
                'background-color': 'white',
                'color': 'steelblue'
            }
        ),
    ]
)

header = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1(
                                    'Nutrimap',
                                    style={
                                       'color': 'white',
                                       'text-align': 'left',
                                       'font-size': '48px',  #, 'width': 300}),
                                    }
                                ),
                                html.P(
                                    'Select foods and nutrients to display in the heatmap',
                                    style={'color': 'white'}
                                ),
                            ]
                        ),
                    dbc.Col([collapse_button])
                    ]
                ),
                dbc.Collapse(
                    dcc.Markdown(
                       """
                       This dashboard facilitates comparisons of nutrient composition between common
                       food items to give an overview of which foods are high and low in what
                       nutrients. I think colors are more efficient at presenting overviews than
                       tables with numbers, so I chose to present this information as heatmaps.

                       The data is from USDA and the RDI from NIH. Evenutally I want to add more options
                       computing the RDI, but for now, the RDI is based on a 70 kg male in his 30s.
                       This is a minor issue since the dashboard mainly use RDI to provide a reference
                       value for coloring the heatmap rather than recommending exactly how much of a certain
                       food item one should eat. For the latter, I highly reccomend [Cronometer](https://cronometer.com).
                       """,
                       style={'color': 'white', 'width': '60%'}
                    ),
                    id="collapse",
                )
            ],
        )
    ],
    style={
        'backgroundColor': 'steelblue',
        'border-radius': 3,
        'padding': 15,
        'margin-top': 15,
        'margin-bottom': 10,
        'margin-right': 15,
        'margin-left': 15
    }
)

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Dropdowns 
food_dropdown = dl.Input(
    dcc.Dropdown(
        options=[{'label': group.capitalize(), 'value': group} for group in food_groups],
        multi=True,
        value=['vegetables', 'grains'],
    ),
    label='Food groups'
)

nutrient_dropdown = dcc.Dropdown(
    id='nutrient-dropdown',
    options=[{'label': group.capitalize().replace('_', ' '), 'value': group} for group in nutrient_groups],
    multi=True,
    value=['macros', 'detailed_macros'],
)

# TODO Add note (hover?) that this can also be used to rearrange columns
sort_by_dropdown = dcc.Dropdown(
    id='sort-by-dropdown',
    options=[],
    multi=True,
)

# TODO does the error when erasing all here crash the app?
color_max = dcc.Input(type='number', value=100, min=1)

@app.callback(
    Output('sort-by-dropdown', 'options'),
    Input('nutrient-dropdown', 'value'))
def set_sort_by_options(selected_nutrient_groups):
    nested_nutrient_names = [nutrient_groups[nutrient_group] for nutrient_group in selected_nutrient_groups]
    return [{'label': nutrient.capitalize().replace('_', ' '), 'value': nutrient}
            for group in nested_nutrient_names for nutrient in group]

# Heatmap callback
@app.callback(
    args=dict(
        selected_food_groups=food_dropdown,
        selected_nutrient_groups=dl.Input(nutrient_dropdown, label='Nutrient groups'),
        sort_by=dl.Input(sort_by_dropdown, label='Sort by'),
        heatmap_options=tpl.new_checklist(
            options=['Log color scale', 'Normalize to RDI'], label='Heatmap options',
            value=['Log color scale', 'Normalize to RDI']),
        color_max=dl.Input(color_max, label="Max color value"),
    ),
    output=tpl.new_graph(),
    template=tpl,
)
def create_nutrition_heatmap(selected_food_groups, selected_nutrient_groups, sort_by, heatmap_options, color_max):
    # nested_food_names = [fn for fn_list in selected_food_groups.values() for fn in fn_list]
    nested_food_names = [food_groups[food_group] for food_group in selected_food_groups]
    flattened_food_names = [val for sublist in nested_food_names for val in sublist]
    nested_nutrient_names = [nutrient_groups[nutrient_group] for nutrient_group in selected_nutrient_groups]
    flattened_nutrient_names = [val for sublist in nested_nutrient_names for val in sublist]
    if sort_by is None:
        foods_to_plot = foods.loc[flattened_food_names, flattened_nutrient_names]
    else:
        # Move sort_by columns to the left in the heatmap
        flattened_nutrient_names = [nutrient for nutrient in flattened_nutrient_names if nutrient not in sort_by] + sort_by[::-1]
        foods_to_plot = foods.loc[flattened_food_names, flattened_nutrient_names].sort_values(sort_by, ascending=False)
    if 'Log color scale' in heatmap_options:
        hover_data = foods_to_plot.applymap(lambda x: '{:g}'.format(float('{:.{p}g}'.format(x, p=2))))  #lambda x: f'{x:.2g}')
        foods_to_plot = foods_to_plot.apply('log1p')
        range_color = (math.log1p(0), math.log1p(color_max))
    else:
        range_color = (0, color_max)
        
    # temp
    # foods_to_plot = (foods_to_plot - foods_to_plot.min()) / (foods_to_plot.max() - foods_to_plot.min())

    # Consider clusterogram to have labelled columns for food_group and easier clustering and standardization (maybe not flex enough)
    fig = px.imshow(
        foods_to_plot,
        # aspect='equal', # the default, but figure size in plotly is so confusing that I am explicit
        # It works better when I don't set width and rely on the asepct ratio and height only
        height=92 + foods_to_plot.shape[0] * 20, # higher values than 20 push the map down
        width=200 + foods_to_plot.shape[1] * 20, # higher values than 20 push the map down
        range_color=range_color,
        color_continuous_scale='YlOrBr',
        # width=foods_to_plot.shape[1] * 50,
        # height=foods_to_plot.shape[0] * 50
    )
    fig.update_layout(
        # width=foods_to_plot.shape[1] * 50,
        # Only setting height 
        xaxis_nticks=foods_to_plot.shape[1] + 1,
        yaxis_nticks=foods_to_plot.shape[0] + 1,
        xaxis_title=None,
        yaxis_title=None,
        xaxis_side='top',
        yaxis_side='right',
        xaxis_tickangle=-45,
        coloraxis_showscale=False,
        margin=dict(r=200, t=92, b=0, l=0, pad=0),
        plot_bgcolor='lightgrey',  # NaN color
        # autosize=True,
    # These automargins sounds useful but they seem to have no effect so maybe already default?
    # Or not tried small enough matrix
    ).update_xaxes(
        automargin=False,  # Must set this to false and manually add label padding for chart not to jump around
        showgrid=False,  # For NaNs to show up without gridlines
    # constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
    ).update_yaxes(
        automargin=False,  # Must set this to false and manually add label padding for chart not to jump around
        showgrid=False,  # For NaNs to show up without gridlines
    # constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
    )

    if 'Log color scale' in heatmap_options:
        fig.update_traces(
            customdata=hover_data,
            hovertemplate =
                '<b>%{y}</b><br>' +
                # TODO Make the below format condition on wehter RDI or raw values are chosen
                # '%{x} %{z:.2r} ' + '{}'.format('%') # could also be other units and %
                '%{x} %{customdata} ' + '{}'.format('%') # could also be other units and %
                # '%{x} {:g}'.format(float('{:.{p}g}'.format('%{z}', p=2)))
        )
    else:
        fig.update_traces(
            hovertemplate =
                '<b>%{y}</b><br>' +
                '%{x} %{z:.2r} ' + '{}'.format('%') # could also be other units and %
        )

    return fig

# Must be last since `tpl` is modified in the callbacks
app.layout = dbc.Container([header] + tpl.children, fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)