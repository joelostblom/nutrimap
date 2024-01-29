importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.4/pyc/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/1.2.3/dist/wheels/bokeh-3.2.2-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.2.3/dist/wheels/panel-1.2.3-py3-none-any.whl', 'pyodide-http==0.2.1', 'altair', 'numpy', 'pandas', 'scipy', 'scikit-learn']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import altair as alt
import pandas as pd
import panel as pn
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as pca
from scipy.cluster import hierarchy 

pn.extension('vega')

# Read RDI and food data
rdi_url = 'https://raw.githubusercontent.com/joelostblom/nutrimap/main/data/processed/matched_rdi_sr_nih.csv'
rdis = pd.read_csv(rdi_url, comment='#')

food_url = 'https://raw.githubusercontent.com/joelostblom/nutrimap/main/data/processed/foods.csv'
foods = pd.read_csv(food_url, index_col=0)

# Fill in some missing values via manual lookups
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

# Add RDI to the foods df
foods = foods.reset_index().melt(
    id_vars='food',
    value_name='amount',
    ignore_index=False
).rename(
    columns={'variable': 'nutrient'}
).assign(
    unit=lambda df: df['nutrient'].map(rdis.set_index('MatchedNutrient')['Unit']),
    rdi_max=lambda df: df['nutrient'].map(rdis.set_index('MatchedNutrient')['Amount']),
    # Reassign rdi as a proportion instead
    rdi=lambda df: df['amount'] / df['rdi_max']
).drop(
    columns='rdi_max'
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
        data[col] = data[col].fillna(data[col].mean())
    
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

    scatter = alt.Chart(
        pca_data,
        width=200,
        height=200,
        title=alt.Title(
            ' ',
            subtitle="Food similarity (drag to select)",
            anchor='start',
        )
    ).mark_circle(size=50).encode(
        alt.X("component_1", title="").axis(domain=False, ticks=False, labels=False),
        alt.Y("component_2", title="").axis(domain=False, ticks=False, labels=False),
        color = alt.condition(brush, alt.Color("food_group:N", title=""), alt.value("lightgray")),
        tooltip="food"
    ).add_params(brush)

    return pn.pane.Vega(scatter)

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

    # Inlclude only food items selected in the scatter plot
    if selection:
        pca_df = pca_df[
            pca_df["component_1"].between(selection["component_1"][0], selection["component_1"][1])
            & pca_df["component_2"].between(selection["component_2"][0], selection["component_2"][1])
        ]
        filtered_df = filtered_df[filtered_df["food"].isin(pca_df["food"].unique())]

    # No need to create a chart if there are no points selected
    if filtered_df.shape[0] == 0:
        return None
    else:
        heatmap = alt.Chart(filtered_df).mark_rect().transform_calculate(
            tooltip_amount_and_unit = "round(100 * datum.amount) / 100 + ' ' + datum.unit"
        ).encode(
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
                alt.Tooltip('tooltip_amount_and_unit:N', title='Amount'),
            ]
        )
        return pn.pane.Vega(heatmap)
    
template = pn.template.BootstrapTemplate(site='Nutrimap',
    title='A cure for food label indigestion',
    sidebar=[pn.pane.Markdown("## Settings"), food_group, nutrient_group, max_dv]
    )

# Re-filter the dataframe and re-create the charts when the eidget values change
@pn.depends(food_group.param.value, nutrient_group.param.value, max_dv.param.value)
def update_charts(food_group, nutrient_group, max_dv):
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

    # Create the Altair charts
    pca_data = pca_2_components(filtered_df)
    scatter = make_scatter(pca_data)
    # Set the heatmap up to listen to the selection in the scatter plot
    heatmap = pn.bind(create_heatmap, filtered_df, scatter.selection.param.brush)

    template.sidebar.extend(scatter)

    return pn.Column(heatmap, pn.Column(scatter, visible=False))

template.main.append(update_charts)

template.servable()


await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.globals.set('patch', msg.patch)
    self.pyodide.runPythonAsync(`
    state.curdoc.apply_json_patch(patch.to_py(), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.globals.set('location', msg.location)
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads(location)
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()