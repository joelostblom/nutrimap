import altair as alt
import pandas as pd
import panel as pn


# import data
foods = pd.read_csv('data/processed/foods.csv', index_col=0)

# get RDI values
rdis = pd.read_csv('data/processed/matched_rdi_sr_nih.csv', comment='#')


def compute_rdi_proportion(row):
    '''Calculate the proportion of the RDI contained in each nutrient'''
    new_row = pd.Series(dtype=float)
    for col_name in row.index:
        nutrient_rdi = rdis.loc[rdis['MatchedNutrient'] == col_name, 'Amount'].values[0]
        rdi_proportion = round(100 * row[col_name] / nutrient_rdi, 3)
        # Round to 2 significant digits https://stackoverflow.com/a/48812729/2166823
        new_row.loc[col_name] = rdi_proportion  #
    return new_row


# compute RDI values
foods = foods.apply(compute_rdi_proportion, axis=1).reset_index()

# pivot the data to long form
foods_long = pd.melt(
    foods, id_vars='food', value_vars=foods.columns.tolist()[1:], ignore_index=False
).rename(columns={'variable': 'nutrient'})

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


# flatten list of food/nutrient groups selected in widget
def get_selected(values):
    names = []
    for group in values:
        for i in group:
            names.append(i)
    return names

# add checkbuttongroup for food groups
food_group = pn.widgets.MultiChoice(name='Food Groups',
                                                value=['vegetables', 'grains'], # currently selected
                                                options=list(food_groups.keys()) # options
                                               )

# add checkbuttongroup for nutrient groups
nutrient_group = pn.widgets.MultiChoice(name='Nutrient Groups',
                                                value=['macros', 'detailed_macros'],
                                                options=list(nutrient_groups.keys())
                                               )

# add slider to set maximum DV value, affecting max value of heatmap color range
max_dv = pn.widgets.IntSlider(name = 'Maximum Daily Value',
                                   start = 0,
                                   end = int(max(foods_long['value'])),
                                   value = 300
                                  )

# tell panel to reload chart when parameters change
@pn.depends(food_group.param.value, nutrient_group.param.value, max_dv.param.value)
def make_plot(food_group, nutrient_group, max_dv):
    # Load the data
    df = foods_long # define df
    df.loc[df['value'] > max_dv, 'value'] = max_dv
    # filter data according to selectors
    selected_foods = []
    [selected_foods.extend(food_groups[food]) for food in food_group]
    selected_nutrients = []
    [selected_nutrients.extend(nutrient_groups[nutrient]) for nutrient in nutrient_group]
    mask = (df['food'].isin(selected_foods) & (df['nutrient'].isin(selected_nutrients)))
    df = df.loc[mask] # filter the dataframe
    # create the Altair chart object
    chart = alt.Chart(df).mark_rect().encode(
        x = alt.X('nutrient', axis=alt.Axis(title = 'Nutrient')),
        y = alt.Y('food', axis=alt.Axis(title = 'Food')),
        color = alt.Color('value', legend=alt.Legend(title="Percent of Daily Value")),
        tooltip=alt.Tooltip(['food:O', 'nutrient:O', 'value:Q'])
    ).configure_axisY(
        orient = 'right'
    ).configure_axisX(
        orient = 'top',
        labelAngle = -45
    )
    return chart


# build the dashboard
pn.template.FastListTemplate(site='Nutrimap', title='A cure for food label indigestion',
                                       sidebar=[pn.pane.Markdown("## Settings"),
                                               food_group,
                                               nutrient_group,
                                               max_dv],
                                       main=[make_plot]).servable()
