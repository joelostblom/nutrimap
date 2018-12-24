from pandas import read_csv, Series
# from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.layouts import widgetbox, column, row
from bokeh.models.widgets import Slider, TextInput
from bokeh.palettes import Category10_10, Category20_20, YlOrBr9
from bokeh.models import ColumnDataSource, LinearColorMapper, LogColorMapper


coi = ['Shrt_Desc', 'Energ_Kcal', 'Protein_(g)',
       'Lipid_Tot_(g)', 'Carbohydrt_(g)', 'Fiber_TD_(g)',
       'Sugar_Tot_(g)', 'FA_Sat_(g)', 'FA_Mono_(g)', 'FA_Poly_(g)']
food_grps = {
    'grains': ['Quinoa,unckd', 'Oats', 'Barley,hulled', 'Barley,pearled,raw',
               'Buckwheat', 'Rice,brown,long-grain,raw', 'Wild rice,raw',
               'Millet,raw', 'Bulgur,dry', 'Spelt,unckd', 'Wheat,durum',
               'Wheat,soft white', 'Wheat,hard red winter', 'Sorghum grain',
               'Wheat,kamut khorasan,unckd', 'Amaranth grain,unckd',
               'Rice,white,long-grain,reg,raw,unenr', 'Semolina,unenriched',
               'Triticale', 'Teff,unckd', 'Rye grain'],
    'vegetables': ['Brussels sprouts,raw', 'Beets,raw', 'Broccoli,raw',
                   'Cauliflower,raw', 'Eggplant,raw', ],
    'greens': ['Kale,raw', 'Spinach,raw', 'Lettuce,cos or romaine,raw',
               'Chard,swiss,raw', 'Arugula,raw', 'Collards,raw',
               'Lettuce,iceberg (incl crisphead types),raw', 'Beet greens,raw',
               'Mustard greens,raw', 'Cabbage,chinese (pak-choi),raw',
               'Cabbage,raw', ],
    'legumes': ['Beans,black turtle,mature seeds,raw', 'Lentils,raw',
                'Lentils,pink or red,raw', 'Beans,snap,green,raw',
                'Soybeans,green,raw', 'Beans,pinto,mature seeds,sprouted,raw',
                'Beans,snap,yellow,raw', 'Beans,adzuki,mature seeds,raw',
                'Beans,black,mature seeds,raw',
                'Beans,black turtle,mature seeds,raw',
                'Beans,cranberry (roman),mature seeds,raw',
                'Beans,french,mature seeds,raw', 'Beans,navy,mature seeds,raw',
                'Beans,kidney,all types,mature seeds,raw',
                'Beans,pink,mature seeds,raw', 'Beans,pinto,mature seeds,raw',
                'Beans,sml white,mature seeds,raw',
                'Beans,white,mature seeds,raw', 'Soybeans,mature seeds,raw',
                'Broadbeans (fava beans),mature seeds,raw', 'Peas,green,raw',
                'Chickpeas (garbanzo bns,bengal gm),mature seeds,raw',
                'Peas,grn,split,mature seeds,raw'],
    'nuts': ['Beechnuts,dried', 'Brazilnuts,dried,unblanched',
             'Butternuts,dried',
             'Nuts,cashew nuts,raw',
             'Hazelnuts or filberts',
             'Hickorynuts,dried',
             'Macadamia nuts,raw',
             'Nuts,pilinuts,dried', 'Nuts,pine nuts,dried',
             'Pistachio nuts,raw',
             # 'Pistachio nuts,dry rstd,wo/salt', 'Walnuts,black,dried',
             'Walnuts,english',
             'Coconut meat,dried (desiccated),crmd',
             # 'Cashew nuts,dry rstd,w/salt', 'Cashew nuts,oil rstd,w/salt',
             # 'Macadamia nuts,dry rstd,w/salt',
             # 'Pistachio nuts,dry rstd,w/salt',
             'Peanuts,all types,raw',# 'Peanuts,all types,oil-roasted,w/salt',
             # 'Peanuts,all types,dry-roasted,w/salt',
             # 'Peanuts,all types,oil-roasted,wo/ salt',
             # 'Peanuts,all types,dry-roasted,wo/salt',
             ]
    }
foods_all = read_csv('./ABBREV.csv', usecols=coi, index_col=0)
foods_all.index = foods_all.index.str.capitalize()
foods = foods_all.loc[[x for sl in food_grps.values() for x in sl]].copy()
# flowers['Shrt_Desc'] = flowers['Shrt_Desc'].str.capitalize()
# flowers = flowers.loc[flowers['Shrt_Desc'].isin()]
# flowers.loc[flowers['Shrt_Desc'].isin(food_grps['grains']), 'Category'] = 'grains'
# flowers.loc[flowers['Shrt_Desc'].isin(food_grps['vegetables']), 'Category'] = 'vegetables'
# flowers.loc[flowers['Shrt_Desc'].isin(food_grps['greens']), 'Category'] = 'greens'
# flowers.loc[flowers['Shrt_Desc'].isin(food_grps['legumes']), 'Category'] = 'legumes'
flowers = foods.reset_index().copy()
flowers.loc[flowers['Shrt_Desc'] == 'Oats', 'Sugar_Tot_(g)'] = 1.1
flowers.loc[flowers['Shrt_Desc'] == 'Quinoa,unckd', 'Sugar_Tot_(g)'] = 6.1
flowers.loc[flowers['Shrt_Desc'] == 'Buckwheat', 'Sugar_Tot_(g)'] = 1.9
flowers.loc[flowers['Shrt_Desc'] == 'Millet,raw', 'Sugar_Tot_(g)'] = 1.5
# used entry for semolina flour as th evalues were very similar
flowers.loc[flowers['Shrt_Desc'] == 'Semolina,unenriched',
            'Sugar_Tot_(g)'] = 0.7
flowers.loc[flowers['Shrt_Desc'] == 'Triticale', 'Sugar_Tot_(g)'] = 1
flowers.loc[flowers['Shrt_Desc'] == 'Triticale', 'Fiber_TD_(g)'] = 14.6
na_indices = flowers.isnull().any(axis=1).nonzero()
na_foods = flowers.iloc[na_indices]['Shrt_Desc'].values
flowers = flowers.dropna()


# RDI
df_rdi = read_csv('nutrimap/data/matched_rdi.csv')
flowers = flowers.set_index('Shrt_Desc')
def get_rdi(row):
    new_row = Series()
    for col_name in row.index:
        new_row.loc[col_name] = round(100 * row[col_name] /
            df_rdi.loc[df_rdi['MatchedNutrient'] == col_name, 'Amount'].values[0], 1)
    return new_row
flowers = flowers.apply(get_rdi, axis=1)
flowers['Category'] = ''
for grp_name in food_grps:
    # short_names = [item[:10] for item in food_grps[grp_name]]
    # foods.loc[food_grps[grp_name], 'Category'] = grp_name
    new_food = [x for x in food_grps[grp_name] if x not in na_foods]
    flowers.loc[new_food, 'Category'] = grp_name
# for grp_name in food_grps:
#     food_grps[grp_name] = [item[:10] for item in food_grps[grp_name]]
#     foods.loc[food_grps[grp_name], 'Category'] = grp_name
flowers = flowers.reset_index().copy()

flowers['Shrt_Desc'] = flowers['Shrt_Desc'].str[:20]
# Plot projection
plot = figure(plot_height=400, plot_width=400, title='Food similarity',
              tools="box_select,pan,reset,save,wheel_zoom,tap",
              active_drag='box_select', tooltips=[('', '@Shrt_Desc')],)
              # x_axis_type='log')
              # x_range=(-2, 8))
              # ('Protein', '@Protein_(g)'), ('Energy', '@Energ_Kcal')])
plot.toolbar.autohide = True

# Standardize for PCA
flow_num = flowers.select_dtypes('number')
flow_num_stndr = (flow_num - flow_num.mean()) / flow_num.std()
            #).join(flowers.select_dtypes('object')))
pca_coords = PCA(n_components=2).fit_transform(flow_num_stndr)
# tsne_coords = TSNE(n_components=2).fit_transform(flow_num)
flowers['tSNE_x'], flowers['tSNE_y'] = pca_coords.T
# Set cmap to a repeating version of 2020 if there are many colors
n_grps = flowers['Category'].nunique()
if n_grps <= 10:
    cmap = Category10_10
else:
    cmap = Category20_20 * (n_grps // 20) + Category20_20[:n_grps % 20]

cat_cmap = {cat: cmap[num] for num, cat in
            enumerate(flowers['Category'].unique())}
flowers['colors'] = [cat_cmap[cat] for cat in flowers['Category']]
# TODO Figure out how to get clickable legend working properly with box select
# Loop for the clicks to work on the legend
# for grp_name, grp in flowers.groupby('Category'):
#     sctr = plot.circle(grp['tSNE_x'], grp['tSNE_y'], line_color=None,
#                        fill_color=cat_cmap[grp_name], size=7, fill_alpha=0.7,
#                        legend=grp_name, muted_alpha=0.1,
#                        muted_color=cat_cmap[grp_name])
# Temporary
food_cds1 = ColumnDataSource(flowers)
sctr = plot.circle('tSNE_x', 'tSNE_y', line_color=None, fill_color='colors',
                   size=7, fill_alpha=0.7, legend='Category', muted_alpha=0.1,
                   muted_color='colors', source=food_cds1)
# plot.legend.label_text_font_size(5)
# plot.legend.click_policy = 'mute'

# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)

# Plot heatmap


def create_heatmap(df):
    df = df.drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category'])
    df.columns = df.columns.str.rpartition('_').get_level_values(0)
    df = df.rename(columns={'Shrt': 'Shrt_Desc'})
    if df.shape[0] > 2:
        from scipy.cluster.hierarchy import dendrogram, linkage
        Z = linkage(df.select_dtypes('number').dropna(), 'single')
        dn = dendrogram(Z, no_plot=True)
        df_srtd = df.iloc[dn['leaves']]
    df_mlt = (df_srtd
              # .select_dtypes('number')
              .melt(id_vars='Shrt_Desc'))
    # food_mlt2 = flowers2.melt(id_vars='Shrt_Desc').dropna()
    # food_cds = ColumnDataSource(food_mlt2)
    plot_height = 100 + 20 * df['Shrt_Desc'].nunique()
    # mapper = LinearColorMapper(palette='YlOrBr9', low=df_mlt['value'].max(),
    #                            high=df_mlt['value'].min())
    mapper = LogColorMapper(palette=YlOrBr9[::-1], low=0, high=100)
    food_cds = ColumnDataSource(df_mlt)
    tools = ['box_select', 'reset']
    heatmap = figure(tools=tools, plot_height=plot_height, plot_width=400,
                     sizing_mode='fixed', x_axis_location="above",
                     y_axis_location='right',
                     x_range=list(df_mlt['variable'].unique()),
                     y_range=list(df_mlt['Shrt_Desc'].unique()), tooltips=[('',
                         '@variable @value')])
    heatmap.xaxis.major_label_orientation = 0.8
    heatmap.axis.major_label_standoff = 0
    heatmap.grid.grid_line_color = None
    heatmap.axis.axis_line_color = None
    heatmap.axis.major_tick_line_color = None
    heatmap.toolbar.autohide = True
    htmp = heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1,
                        source=food_cds, fill_color=transform('value', mapper),
                        line_color=None)
    return heatmap


# food_mlt = (flowers
#             .drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category'])
#             .melt(id_vars='Shrt_Desc'))
# tools = ['box_select', 'reset']
# heatmap = figure(tools=tools, plot_height=150, plot_width=400, sizing_mode='fixed',
#                  x_axis_location="above", y_axis_location='right',
#                  x_range=list(food_mlt['variable'].unique()),
#                  y_range=list(food_mlt['Shrt_Desc'].unique()),
#                  tooltips=[('', '@variable @value')])
# heatmap.height = 40 + 20 * food_mlt['Shrt_Desc'].nunique()
# heatmap.xaxis.major_label_orientation = 0.8
# heatmap.axis.major_label_standoff = 0
# heatmap.grid.grid_line_color = None
# heatmap.axis.axis_line_color = None
# heatmap.axis.major_tick_line_color = None
# heatmap.toolbar.autohide = True
# htmp = heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1,
#                     source=food_cds, fill_color=transform('value', mapper),
#                     line_color=None)

# from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Select

# menu = [("Item 1", "item_1"), ("Item 2", "item_2"), None, ("Item 3", "item_3")]
# dropdown.on_change(drop_select)

# Set up callback
# def update_data(attrname, old, new):
    # Get the current slider values
    # a = amplitude.value
    # b = offset.value
    # k = freq.value


# for w in [offset, amplitude, freq]:
    # w.on_change('value', update_data)


def update_webapp(df_sub):
    lay.children[0] = create_heatmap(df_sub)


def drop_select(attr, old, new):
    print(attr)
    print(old)
    print(new)
    df_sub = flowers.loc[flowers['Category'] == new]
    from bokeh.models import Selection
    print(df_sub.index)

    df_mlt = (flowers
              .drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category'])
              .melt(id_vars='Shrt_Desc'))
    print(df_mlt.loc[df_mlt['variable'] == 'Category'])
    # df_sub_mlt = df_mlt.loc[(df_mlt['variable'] == 'Category')].loc[(df_mlt['value'] == new)]
    # sctr.data_source.selected = Selection(indices=list(df_sub_mlt.index))
    print(sctr.data_source)
    update_webapp(df_sub)


def selection_change(attr, old, new):
    print(attr)
    print(old)
    print(new)
    if len(new) == 0:
        flowers2 = flowers.copy()
    else:
        flowers2 = flowers.iloc[new].copy()
    update_webapp(flowers2)


sctr.data_source.selected.on_change('indices', selection_change)

menu = [(grp, grp) for grp in food_grps.keys()]
dropdown = Select(options=menu)
dropdown.on_change('value', drop_select) #lambda attr, old, new: update(attr, old, new))

# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, freq)
lay = row(
        create_heatmap(flowers),
          column(widgetbox(dropdown), plot), height=300, width=2000, sizing_mode='fixed')
curdoc().add_root(lay)
curdoc().title = "Sliders"





    # htmp.data_source.data = food_cds.data
    # Update heatmap rows, figure size and y-axis labels
    # heatmap.y_range.factors = food_mlt2.Shrt_Desc.unique().tolist()
    # print(len(heatmap.y_range.factors), heatmap.height)
    # heatmap.height = 40 + 20 * food_mlt2.Shrt_Desc.nunique()
    # print(len(heatmap.y_range.factors), heatmap.height)


