from pandas import read_csv
# from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.layouts import widgetbox, column, row
from bokeh.models.widgets import Slider, TextInput
from bokeh.palettes import Category10_10, Category20_20
from bokeh.models import ColumnDataSource, LinearColorMapper


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
foods['Category'] = ''
for grp_name in food_grps:
    # short_names = [item[:10] for item in food_grps[grp_name]]
    # foods.loc[food_grps[grp_name], 'Category'] = grp_name
    foods.loc[food_grps[grp_name], 'Category'] = grp_name
# for grp_name in food_grps:
#     food_grps[grp_name] = [item[:10] for item in food_grps[grp_name]]
#     foods.loc[food_grps[grp_name], 'Category'] = grp_name
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
flowers.loc['Triticale', 'Sugar_Tot_(g)'] = 1
flowers.loc['Triticale', 'Fiber_TD_(g)'] = 14.6
flowers = flowers.dropna()
flow_num = flowers.select_dtypes('number')
flowers = (((flow_num - flow_num.mean()) /
            flow_num.std()).join(flowers.select_dtypes('object')))

flowers['Shrt_Desc'] = flowers['Shrt_Desc'].str[:20]
# Plot projection
plot = figure(plot_height=400, plot_width=400, title='Food similarity',
              tools="box_select,pan,reset,save,wheel_zoom,tap",
              active_drag='box_select', tooltips=[('', '@Shrt_Desc'),
              ('Protein', '@Protein_(g)'), ('Energy', '@Energ_Kcal')])
plot.toolbar.autohide = True
flow_num = flowers.select_dtypes('number')
pca_coords = PCA(n_components=2).fit_transform(flow_num)
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
food_mlt = (flowers
            .drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category'])
            .melt(id_vars='Shrt_Desc'))
food_cds = ColumnDataSource(food_mlt)
mapper = LinearColorMapper(palette='YlOrBr9', low=food_mlt['value'].max(),
                           high=food_mlt['value'].min())
tools = ['box_select', 'reset']
heatmap = figure(tools=tools, plot_height=150, plot_width=400, sizing_mode='fixed',
                 x_axis_location="above", y_axis_location='right',
                 x_range=list(food_mlt['variable'].unique()),
                 y_range=list(food_mlt['Shrt_Desc'].unique()),
                 tooltips=[('', '@variable @value')])
heatmap.height = 40 + 20 * food_mlt['Shrt_Desc'].nunique()
heatmap.xaxis.major_label_orientation = 0.8
heatmap.axis.major_label_standoff = 0
heatmap.grid.grid_line_color = None
heatmap.axis.axis_line_color = None
heatmap.axis.major_tick_line_color = None
heatmap.toolbar.autohide = True
htmp = heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1,
                    source=food_cds, fill_color=transform('value', mapper),
                    line_color=None)

# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, freq)
lay = row(plot, heatmap, height=300, width=2000,
             sizing_mode='fixed')
curdoc().add_root(lay)
curdoc().title = "Sliders"


# Set up callback
# def update_data(attrname, old, new):
    # Get the current slider values
    # a = amplitude.value
    # b = offset.value
    # k = freq.value


# for w in [offset, amplitude, freq]:
    # w.on_change('value', update_data)


def update(attr, old, new):
    flowers2 = flowers.iloc[new].copy()
    if len(new) > 2:
        from scipy.cluster.hierarchy import dendrogram, linkage
        Z = linkage(flowers2.select_dtypes('number').dropna(), 'single')
        dn = dendrogram(Z, no_plot=True)
        flowers2 = flowers2.iloc[dn['leaves']]
    food_mlt2 = flowers2.melt(id_vars='Shrt_Desc').dropna()
    food_cds = ColumnDataSource(food_mlt2)
    htmp.data_source.data = food_cds.data
    # Update heatmap rows, figure size and y-axis labels
    heatmap.y_range.factors = food_mlt2.Shrt_Desc.unique().tolist()
    htmp.data_source.data = food_cds.data
    heatmap.height = 50 + 50 * food_mlt2.Shrt_Desc.nunique()


sctr.data_source.selected.on_change('indices', update)
