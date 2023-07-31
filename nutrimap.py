import altair as alt
import pandas as pd
import panel as pn
pn.extension('vega')
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as pca
from scipy.cluster import hierarchy 


# get RDI values
url = 'https://raw.githubusercontent.com/joelostblom/nutrimap/main/data/processed/matched_rdi_sr_nih.csv'
rdis = pd.read_csv(url, comment='#')

def compute_rdi_proportion(row):
    '''Calculate the proportion of the RDI contained in each nutrient'''
    new_row = pd.Series(dtype=float)
    for col_name in row.index:
        nutrient_rdi = rdis.loc[rdis['MatchedNutrient'] == col_name, 'Amount'].to_numpy()[0]
        rdi_proportion = round(row[col_name] / nutrient_rdi, 3)
        # Round to 2 significant digits https://stackoverflow.com/a/48812729/2166823
        new_row.loc[col_name] = rdi_proportion  #
    return new_row

url = 'https://raw.githubusercontent.com/joelostblom/nutrimap/main/data/processed/foods.csv'

foods = pd.read_csv(
    url,
    index_col=0
)

# fill in some missing values
foods.loc['Oats', 'Sugar'] = 1.1
foods.loc['Oats', 'Selenium'] = 28.9
foods.loc['Oats', 'Vitamin E'] = 0.42
foods.loc['Oats', 'Vitamin K'] = 2
foods.loc['Oats', 'beta-Carotene'] = 0
foods.loc['Oats', 'alpha-Carotene'] = 0
foods.loc['Oats', 'beta-Cryptoxanthin'] = 0
foods.loc['Oats', 'Lycopene'] = 0
foods.loc['Oats', 'Lutein + zeaxanthin'] = 180

foods.loc['Quinoa, uncooked', 'Sugar'] = 6.1
foods.loc['Quinoa, uncooked', 'Vitamin C'] = 0
foods.loc['Buckwheat', 'Sugar'] = 1.9
foods.loc['Millet, raw', 'Sugar'] = 1.5

foods = foods.apply(
    compute_rdi_proportion,
    axis=1
).reset_index().melt(
    id_vars='food',
    value_name='rdi',
    ignore_index=False
).rename(
    columns={'variable': 'nutrient'}
)

food_groups = {
    # TODO add corn on the cob as veggie
    'grains': [
        'Quinoa, uncooked',
        'Amaranth grain, uncooked',
        'Oats',
        'Barley, pearled, raw',
        'Corn grain, yellow',
        'Buckwheat',
        'Rice, brown, long-grain, raw',
        'Wild rice, raw',
        'Millet, raw',
        'Bulgur, dry',
        'Spelt, uncooked',
        'Wheat, durum',
        'Wheat, hard red winter',
        'Sorghum grain',
        'Wheat, kamut khorasan, uncooked',
        'Rice, white, long-grain, regular, raw, unenriched',
        'Teff, uncooked',
        'Rye grain',
    ],
    'vegetables': [
        'Brussels sprouts, raw',
        'Beets, raw',
        'Broccoli, raw',
        'Cauliflower, raw',
        'Eggplant, raw',
        'Tomatoes, red, ripe, raw, year round average',
        'Peas, green, frozen, unprepared',
    ],
    'greens': [
        'Kale, raw',
        'Spinach, raw',
        'Lettuce, cos or romaine, raw',
        'Chard, swiss, raw',
        'Arugula, raw',
        'Collards, raw',
        'Lettuce, iceberg (includes crisphead types), raw',
        'Beet greens, raw',
        'Mustard greens, raw',
        'Cabbage, chinese (pak-choi), raw',
        'Cabbage, raw',
    ],
    'legumes': [
        'Beans, black turtle, mature seeds, raw',
        'Lentils, raw',
        'Lentils, pink or red, raw',
        'Beans, snap, green, raw',
        'Soybeans, green, raw',
        'Beans, pinto, mature seeds, sprouted, raw',
        'Beans, adzuki, mature seeds, raw',
        'Beans, black, mature seeds, raw',
        'Beans, kidney, all types, mature seeds, raw',
        'Beans, pinto, mature seeds, raw',
        'Beans, small white, mature seeds, raw',
        'Soybeans, mature seeds, raw',
        'Broadbeans (fava beans), mature seeds, raw',
        'Peas, green, raw',
        'Chickpeas (garbanzo beans, bengal gram), mature seeds, raw',
        'Peas, green, split, mature seeds, raw',
    ],
    'nuts': [
        f'Nuts, {x.lower()}'
        for x in [
            'Brazilnuts, dried, unblanched',
            'Cashew nuts, raw',
            'Hazelnuts or filberts',
            'Macadamia nuts, raw',
            'Pine nuts, dried',
            'Pistachio nuts, raw',
            'Walnuts, english',
            'Coconut meat, dried (desiccated), not sweetened',
        ]
    ]
    + ['Peanuts, all types, raw'],
    'fruits': [
        "Apples, raw, with skin",
        'Pineapple, raw, all varieties',
        'Plums, raw',
        'Pears, raw',
        'Apricots, raw',
        'Avocados, raw, all commercial varieties',
        'Blackberries, frozen, unsweetened',
        'Blueberries, raw',
        'Cranberries, raw',
        'Raspberries, raw',
        'Clementines, raw',
        'Strawberries, raw',
        'Dates, medjool',
        'Plantains, green, raw',
        'Pomegranates, raw',
        'Bananas, raw',
        'Plantains, yellow, raw',
        'Kiwifruit, green, raw',
        'Figs, dried, uncooked',
        'Oranges, raw, all commercial varieties',
        'Apricots, dried, sulfured, uncooked',
        'Olives, ripe, canned (small-extra large)',
        'Raisins, dark, seedless',
    ],
    'meats': [
        'Fish, salmon, atlantic, farmed, raw',
        'Fish, salmon, atlantic, wild, raw',
        'Fish, cod, atlantic, raw',
        'Chicken, broiler or fryers, breast, skinless, boneless, meat only, raw',
        'Pork, fresh, ground, raw',
        'Beef, grass-fed, ground, raw',
        'Egg, whole, raw, fresh',
    ],
}

nutrient_groups = dict(
    macros=[
        'Energy',
        'Carbs',
        'Protein',
        'Fiber',
        'Fat',
    ],
    detailed_macros=[
        'Sugar',
        'Fat (mono)',
        'Fat (poly)',
        'Fat (sat)',
        'Cholesterol',
    ],
    minerals=[
        'Calcium',
        'Copper',
        'Iron',
        'Magnesium',
        'Manganese',
        'Phosphorus',
        'Potassium',
        'Selenium',
        'Sodium',
        'Zinc',
    ],
    # TODO shorten names by removing "vitamin" and adding suffixes https://en.wikipedia.org/wiki/B_vitamins
    # add b1 k2 etc annotation
    vitamins=[
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
    aas=[
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
    caretonoids=[
        'Lycopene',
        'Lutein + zeaxanthin',
        'alpha-Carotene',
        'beta-Carotene',
        # 'Retinol',
        'beta-Cryptoxanthin',
    ],
)


# add checkbuttongroup for food groups
food_group = pn.widgets.MultiChoice(
    name='Food Groups',
    value=['vegetables', 'grains'],
    options=list(food_groups.keys()),
)

# add checkbuttongroup for nutrient groups
nutrient_group = pn.widgets.MultiChoice(
    name='Nutrient Groups',
    value=['macros', 'detailed_macros'],
    options=list(nutrient_groups.keys()),
)

# add slider to set maximum DV value, affecting max value of heatmap color range
max_dv = pn.widgets.IntSlider(
    name='Cap color scale at this RDI',
    start=0,
    end=600,
    value=300,
)

# function to get food group for each food in foods dataframe
def get_food_group(food) -> str:
    for k in food_groups:
        if food in food_groups.get(k):
            return k
        
# fill NA values of wide-form foods data with column mean value
def fill_na_mean(data):
    for col in data.columns[data.isnull().any(axis=0)]:
        data[col].fillna(data[col].mean(),inplace=True)
    
    return data

# selects interval over scatterplot for filtering heatmap
#brush = alt.selection_interval(fields = ["food"])

# perform PCA to reduce dataframe to 2 dimensions
def pca_2_components(data):
    data = pd.pivot(data, index="food", columns="nutrient", values="rdi").reset_index()
    data.columns = data.columns.get_level_values(0)
    data['food_group'] = data.apply(lambda row: get_food_group(row["food"]), axis=1)

    # fill NA values with column mean
    data = fill_na_mean(data)

    X = data.iloc[:, 1:-1].values
    
    # create scaler object
    scaler = StandardScaler()

    # get mean and standard deviation
    scaler.fit(X)

    # transform values
    X_scaled = scaler.transform(X)
    
    # reduce filtered data to n dimensions using PCA
    pca_2 = pca(n_components = 2, random_state = 2023)
    pca_2.fit(X_scaled)
    X_pca_2 = pca_2.transform(X_scaled)
    
    # convert numpy array to dataframe
    pca_2_df = pd.DataFrame(X_pca_2, columns=("component_1", "component_2"))
    pca_2_df['food'] = data["food"]
    pca_2_df['food_group'] = data["food_group"]

    return pca_2_df

def make_scatter(pca_data):
    
    brush = alt.selection_interval(name = "brush")

    chart = alt.Chart(pca_data).mark_circle(size=50).encode(
        alt.X("component_1",
              title="Component 1"
        ),
        alt.Y("component_2",
              title="Component 2"
        ),
        alt.Color("food_group",
                  title="Food Group"
        ),
        # color = alt.condition(brush, "food_group", alt.value("lightgray")), # color selected points only
        tooltip="food"
    ).add_params(brush)

    scatter = pn.pane.Vega(chart, debounce = 10)

    return scatter

# sort data using hierarchical clustering and optimal leaf-ordering
def sort_similar_foods(filtered_df):
    """
    requires that the data matches the input of create_heatmap function
    """
    # No sorting needed if there are less than 2 data points
    if filtered_df['food'].nunique() < 2:
        return []

    wide_data = pd.pivot(filtered_df, index="food", columns="nutrient", values="rdi").reset_index()
    wide_data.columns = wide_data.columns.get_level_values(0)
    
     # fill NA values with column mean
    wide_data = fill_na_mean(wide_data)

    X = wide_data.iloc[:, 1:]

    # using average method
    Z = hierarchy.linkage(X, method="average", optimal_ordering=True)

    # find the optimal order of row indexes according to the clustering algorithm
    optimal_order = hierarchy.leaves_list(Z)

    return wide_data.loc[optimal_order, 'food'].tolist()

# create a heatmap chart using filtered data
def create_heatmap(filtered_df, selection):
    pca_df = pca_2_components(filtered_df)

    if selection:
        pca_df = pca_df[(pca_df["component_1"].between(min(selection["component_1"]), max(selection["component_1"]))) & 
                        (pca_df["component_2"].between(min(selection["component_2"]), max(selection["component_2"])))]
        filtered_df = filtered_df[filtered_df["food"].isin(pca_df["food"].unique())]

    # No need to create a chart if there are no points selected
    if filtered_df.shape[0] == 0:
        return None
    else:
        heatmap = alt.Chart(filtered_df).mark_rect().encode(
            alt.X(
                'nutrient',
                title='',
                axis=alt.Axis(
                    orient='top',
                    labelAngle=-45
                )
            ),
            alt.Y('food', title='', axis=alt.Axis(orient='right'), sort=sort_similar_foods(filtered_df)),
            alt.Color('rdi', title="Percent of RDI", legend=alt.Legend(format='.0%')),
            tooltip=[
                alt.Tooltip('food', title='Food'),
                alt.Tooltip('nutrient', title='Nutrient'),
                alt.Tooltip('rdi', title='RDI', format='.1%'),
            ]
        )
        return pn.pane.Vega(heatmap)

# Re-filter the dataframe and re-create the charts when the eidget values change
@pn.depends(food_group.param.value, nutrient_group.param.value, max_dv.param.value)
def make_plot(food_group, nutrient_group, max_dv):
    # Find all the values of each selected groups (e.g. all the food names for type "vegetable")
    selected_foods = []
    [selected_foods.extend(food_groups[food]) for food in food_group]
    selected_nutrients = []
    [
        selected_nutrients.extend(nutrient_groups[nutrient])
        for nutrient in nutrient_group
    ]

    filtered_df = foods.assign(
        rdi=lambda df: df['rdi'].clip(upper=max_dv / 100)  # From percentage to proportion
    ).query(
        'food.isin(@selected_foods)'
        '& nutrient.isin(@selected_nutrients)'
    )

    # Create the Altair chart object
    scatter = make_scatter(pca_2_components(filtered_df))

    heatmap = pn.bind(create_heatmap, filtered_df, scatter.selection.param.brush)

    # TODO: change this so that heatmap is in main panel, scatter is in sidebar
    return pn.Column(scatter, heatmap)

# Build the dashboard
pn.template.BootstrapTemplate(
    site='Nutrimap',
    title='A cure for food label indigestion',
    sidebar=[pn.pane.Markdown("## Settings"), food_group, nutrient_group, max_dv], #TODO: add scatter
    main=[make_plot],
).servable()
