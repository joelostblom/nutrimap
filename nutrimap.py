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
grains = ['Quinoa,unckd', 'Oats', 'Barley,hulled', 'Barley,pearled,raw',
          'Buckwheat', 'Rice,brown,long-grain,raw', 'Wild rice,raw',
          'Millet,raw', 'Bulgur,dry', 'Spelt,unckd', 'Wheat,durum',
          'Wheat,soft white', 'Wheat,hard red winter', 'Sorghum grain',
          'Wheat,kamut khorasan,unckd', 'Rice,white,long-grain,reg,raw,unenr',
          'Semolina,unenriched', 'Triticale', 'Amaranth grain,unckd',
          'Teff,unckd', 'Rye grain'][:10]
vegetables = ['Brussel sprouts, raw', 'Beets,raw', 'Broccoli,raw',
              'Cauliflower,raw', 'Eggplant,raw', ]
greens = ['Kale,raw', 'Spinach,raw', 'Lettuce,cos or romaine,raw',
          'Chard,swiss,raw', 'Arugula,raw', 'Collards,raw',
          'Lettuce,iceberg (incl crisphead types),raw', 'Beet greens,raw',
          'Mustard greens,raw', 'Cabbage,chinese (pak-choi),raw',
          'Cabbage,raw', ]
legumes = ['Beans,black turtle,mature seeds,raw', 'Lentils,raw',
           'Lentils,pink or red,raw']
flowers = read_csv('../ABBREV.csv', usecols=coi)
flowers['Shrt_Desc'] = flowers['Shrt_Desc'].str.capitalize()
flowers = flowers.loc[flowers['Shrt_Desc'].isin(grains + vegetables + greens +
                      legumes)]
flowers['Category'] = ''
flowers.loc[flowers['Shrt_Desc'].isin(grains), 'Category'] = 'grains'
flowers.loc[flowers['Shrt_Desc'].isin(vegetables), 'Category'] = 'vegetables'
flowers.loc[flowers['Shrt_Desc'].isin(greens), 'Category'] = 'greens'
flowers.loc[flowers['Shrt_Desc'].isin(legumes), 'Category'] = 'legumes'
flowers.loc[flowers['Shrt_Desc'] == 'Oats', 'Sugar_Tot_(g)'] = 1.1
flowers.loc[flowers['Shrt_Desc'] == 'Quinoa,unckd', 'Sugar_Tot_(g)'] = 6.1
flowers.loc[flowers['Shrt_Desc'] == 'Buckwheat', 'Sugar_Tot_(g)'] = 1.9
flowers.loc[flowers['Shrt_Desc'] == 'Millet,raw', 'Sugar_Tot_(g)'] = 1.5
# used entry for semolina flour as th evalues were very similar
flowers.loc[flowers['Shrt_Desc'] == 'Semolina,unenriched',
            'Sugar_Tot_(g)'] = 0.7
# flowers.loc['Triticale', 'Sugar_Tot_(g)'] = 1
# flowers.loc['Triticale', 'Fiber_TD_(g)'] = 14.6
flowers = flowers.dropna()
flow_num = flowers.select_dtypes('number')
flowers = (((flow_num - flow_num.mean()) /
            flow_num.std()).join(flowers.select_dtypes('object')))

# Plot projection
flow_num = flowers.select_dtypes('number')
pca_coords = PCA(n_components=2).fit_transform(flow_num)
# tsne_coords = TSNE(n_components=2).fit_transform(flow_num)
flowers['tSNE_x'], flowers['tSNE_y'] = pca_coords.T
plot = figure(plot_height=400, plot_width=400, title="my sine wave",
              tools="box_select,pan,reset,save,wheel_zoom",
              active_drag='box_select')
# Set cmap to a repeating version of 2020 if there are many colors
n_grps = flowers['Category'].nunique()
if n_grps <= 10:
    cmap = Category10_10
else:
    cmap = Category20_20 * (n_grps // 20) + Category20_20[:n_grps % 20]

cat_cmap = {cat: cmap[num] for num, cat in
            enumerate(flowers['Category'].unique())}
flowers['colors'] = [cat_cmap[cat] for cat in flowers['Category']]
# Loop for the clicks to work on the legend
for grp_name, grp in flowers.groupby('Category'):
    sctr = plot.circle(grp['tSNE_x'], grp['tSNE_y'], line_color=None,
                       fill_color=cat_cmap[grp_name], size=7, fill_alpha=0.7,
                       legend=grp_name, muted_alpha=0.1,
                       muted_color=cat_cmap[grp_name])
plot.legend.click_policy = 'mute'
plot.toolbar.autohide = True

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
mapper = LinearColorMapper(palette='YlOrBr9', low=food_mlt['value'].min(),
                           high=food_mlt['value'].max())
tools = ['box_select', 'reset']
heatmap = figure(tools=tools, plot_height=150, plot_width=300,
                 x_axis_location="above", y_axis_location='right',
                 x_range=list(food_mlt['variable'].unique()),
                 y_range=list(food_mlt['Shrt_Desc'].unique()))
heatmap.height = 50 + 50 * food_mlt['Shrt_Desc'].nunique()
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
    food_mlt2 = flowers.iloc[new].melt(id_vars='Shrt_Desc').dropna()
    food_cds = ColumnDataSource(food_mlt2)
    # Update heatmap rows, figure size and y-axis labels
    heatmap.y_range.factors = food_mlt2.Shrt_Desc.unique().tolist()
    htmp.data_source.data = food_cds.data
    heatmap.height = 50 + 50 * food_mlt2.Shrt_Desc.nunique()


sctr.data_source.selected.on_change('indices', update)
