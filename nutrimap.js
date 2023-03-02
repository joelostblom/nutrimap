importScripts("https://cdn.jsdelivr.net/pyodide/v0.22.1/full/pyodide.js");

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
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.3/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.3/dist/wheels/panel-0.14.3-py3-none-any.whl', 'pyodide-http==0.1.0', 'altair', 'pandas']
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

# import pyodide_http
# pyodide_http.patch_all()  # Patch all libraries

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
).apply(
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


# tell panel to reload chart when parameters change
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
    chart = alt.Chart(filtered_df).mark_rect().encode(
        alt.X(
            'nutrient',
            title='',
            axis=alt.Axis(
                orient='top',
                labelAngle=-45
            )
        ),
        alt.Y('food', title='', axis=alt.Axis(orient='right')),
        alt.Color('rdi', title="Percent of RDI", legend=alt.Legend(format='.0%')),
        tooltip=[
            alt.Tooltip('food', title='Food'),
            alt.Tooltip('nutrient', title='Nutrient'),
            alt.Tooltip('rdi', title='RDI', format='.1%'),
        ]
    )
    return chart


# Build the dashboard
pn.template.FastListTemplate(
    site='Nutrimap',
    title='A cure for food label indigestion',
    sidebar=[pn.pane.Markdown("## Settings"), food_group, nutrient_group, max_dv],
    main=[make_plot],
).servable()


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
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()