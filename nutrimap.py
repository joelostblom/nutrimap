import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure
# from bokeh.sampledata.iris import flowers
from bokeh.transform import transform
# from bokeh.palettes import YlOrBr
from sklearn.manifold import TSNE
from bokeh.palettes import Category10_10, Category20_20
import pandas as pd


# Set up data
# N = 200
# x = np.linspace(0, 4*np.pi, N)
# y = np.sin(x)
# source = ColumnDataSource(data=dict(x=x, y=y))
coi = ['Shrt_Desc', 'Energ_Kcal', 'Protein_(g)',
       'Lipid_Tot_(g)', 'Carbohydrt_(g)', 'Fiber_TD_(g)',
       'Sugar_Tot_(g)', 'FA_Sat_(g)', 'FA_Mono_(g)', 'FA_Poly_(g)']
grains = ['Quinoa,unckd', 'Oats', 'Barley,hulled', 'Barley,pearled,raw',
    'Buckwheat', 'Rice,brown,long-grain,raw', 'Wild rice,raw', 'Teff,unckd',
    'Millet,raw', 'Bulgur,dry', 'Spelt,unckd', 'Wheat,durum', 'Rye grain',
    'Wheat,soft white', 'Wheat,hard red winter', 'Sorghum grain',
    'Wheat,kamut khorasan,unckd', 'Rice,white,long-grain,reg,raw,unenr',
    'Semolina,unenriched', 'Triticale', 'Amaranth grain,unckd',][:10]
vegetables = ['Brussel sprouts, raw', 'Beets,raw', 'Broccoli,raw',
        'Cauliflower,raw', 'Eggplant,raw', ]
greens = ['Kale,raw', 'Spinach,raw', 'Lettuce,cos or romaine,raw', 'Chard,swiss,raw',
    'Arugula,raw', 'Lettuce,iceberg (incl crisphead types),raw', 'Collards,raw',
    'Beet greens,raw', 'Mustard greens,raw', 'Cabbage,chinese (pak-choi),raw',
    'Cabbage,raw', ]
legumes = ['Beans,black turtle,mature seeds,raw', 'Lentils,raw', 'Lentils,pink or red,raw']
flowers = (
    pd.read_csv('../ABBREV.csv', usecols=coi)
        # .set_index('Shrt_Desc')
        # .loc['Shrt_Desc'grains, coi]#.sample(100, random_state=0)
    )
# print(flowers.shape)
flowers['Shrt_Desc'] = flowers['Shrt_Desc'].str.capitalize()
# flowers = flowers.set_index('Shrt_Desc')
flowers = flowers.loc[flowers['Shrt_Desc'].isin(grains + vegetables + greens +
                      legumes)]
flowers['Category'] = ''
flowers.loc[flowers['Shrt_Desc'].isin(grains), 'Category'] = 'grains'
flowers.loc[flowers['Shrt_Desc'].isin(vegetables), 'Category'] = 'vegetables'
flowers.loc[flowers['Shrt_Desc'].isin(greens), 'Category'] = 'greens'
flowers.loc[flowers['Shrt_Desc'].isin(legumes), 'Category'] = 'legumes'
# print(flowers['Oats'])
flowers.loc[flowers['Shrt_Desc'] == 'Oats', 'Sugar_Tot_(g)'] = 1.1
flowers.loc[flowers['Shrt_Desc'] == 'Quinoa,unckd', 'Sugar_Tot_(g)'] = 6.1
flowers.loc[flowers['Shrt_Desc'] == 'Buckwheat', 'Sugar_Tot_(g)'] = 1.9
flowers.loc[flowers['Shrt_Desc'] == 'Millet,raw', 'Sugar_Tot_(g)'] = 1.5
flowers.loc[flowers['Shrt_Desc'] == 'Semolina,unenriched', 'Sugar_Tot_(g)'] = 0.7 # used entry for semolina flour as th evalues were very similar
# flowers.loc['Triticale', 'Sugar_Tot_(g)'] = 1
# flowers.loc['Triticale', 'Fiber_TD_(g)'] = 14.6
flowers = flowers.dropna()
flow_num = flowers.select_dtypes('number')
flowers = ((flow_num - flow_num.mean()) / flow_num.std()).join(flowers.select_dtypes('object'))

from sklearn.decomposition import PCA
pca_coords = PCA(n_components=2).fit_transform(flowers.select_dtypes('number'))
# sns.scatterplot(pca_coords.T[0], pca_coords.T[1])


# X_embedded = TSNE(n_components=2).fit_transform(flowers.select_dtypes('number'))
flowers['tSNE_x'], flowers['tSNE_y'] = pca_coords.T
# print(1)

# print(flowers.head())
# Set up plot
plot = figure(plot_height=400, plot_width=400, title="my sine wave",
              tools="box_select,pan,reset,save,wheel_zoom",
              active_drag='box_select')
              # x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

# Set cmap to a repeating version of 2020 if there are many colors
# print(2)
n_cats = flowers['Category'].nunique()
if n_cats <= 10:
    cmap = Category10_10
else:
    cmap = Category20_20 * (n_cats // 20) + Category20_20[:n_cats % 20]

cat_cmap = {cat: cmap[num] for num, cat in enumerate(flowers['Category'].unique())}
print(cat_cmap)
flowers['colors'] = [cat_cmap[cat] for cat in flowers['Category']]
# print(3)
# print(flowers.head())
# print(flowers.shape)
# print(flowers)
# source = ColumnDataSource(grp)
for grp_name, grp in flowers.groupby('Category'):
    sctr = plot.circle(grp['tSNE_x'], grp['tSNE_y'], fill_color=cat_cmap[grp_name],
                       line_color=None, size=7, fill_alpha=0.7, legend=grp_name,
                       muted_alpha=0.1, muted_color=cat_cmap[grp_name])
plot.legend.click_policy="mute"
# print(4)
plot.toolbar.autohide = True


# Set up widgets
text = TextInput(title="title", value='my sine wave')
offset = Slider(title="offset", value=0.0, start=-5.0, end=5.0, step=0.1)
amplitude = Slider(title="amplitude", value=1.0, start=-5.0, end=5.0, step=0.1)
phase = Slider(title="phase", value=0.0, start=0.0, end=2*np.pi)
freq = Slider(title="frequency", value=1.0, start=0.1, end=5.1, step=0.1)

# plot2 = figure(plot_height=400, plot_width=400, title="my sine wave2",
#                tools="box_select,pan,reset,save,wheel_zoom",
#                active_drag='box_select')
               #x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])
# flw_plot = plot2.circle('sepal_width', 'sepal_length', source=flowers)
food_mlt = flowers.drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category']).melt(id_vars='Shrt_Desc')
food_cds = ColumnDataSource(food_mlt)
colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
mapper = LinearColorMapper(palette='YlOrBr9', low=food_mlt['value'].min(),
                           high=food_mlt['value'].max())
tools = ['box_select', 'reset']

print(list(food_mlt['variable'].unique()))
print(list(food_mlt['Shrt_Desc'].unique()))

heatmap = figure(tools=tools, plot_height=150, plot_width=300, x_axis_location="above",
        y_axis_location='right',
    x_range=list(food_mlt['variable'].unique()), y_range=list(food_mlt['Shrt_Desc'].unique()))
heatmap.xaxis.major_label_orientation = 0.8
heatmap.axis.major_label_standoff = 0
heatmap.grid.grid_line_color = None
heatmap.axis.axis_line_color = None
heatmap.axis.major_tick_line_color = None
heatmap.toolbar.autohide = True
#     toolbar_location=None, tools="", x_axis_location="above"))
htmp = heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1, source=food_cds,
       fill_color=transform('value', mapper), line_color=None)
print(5)
# htmp = heatmap.square(x="variable", y="Shrt_Desc", source=food_cds,
#        fill_color=transform('value', mapper), line_color=None)

# heatmap = 

# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value


text.on_change('value', update_title)


def update_data(attrname, old, new):

    # Get the current slider values
    a = amplitude.value
    b = offset.value
    w = phase.value
    k = freq.value

    # Generate the new curve
    # x = np.linspace(0, 4*np.pi, N)
    # y = a*np.sin(k*x + w) + b

    # source.data = dict(x=x, y=y)


for w in [offset, amplitude, phase, freq]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = widgetbox(text, offset, amplitude, phase, freq)

lay = column(inputs, plot, heatmap, height=300, width=800, sizing_mode='scale_width')
curdoc().add_root(lay)
curdoc().title = "Sliders"


def update(attr, old, new):
    # inds = new
    # print(old)
    # print(new)
    # f2 = ColumnDataSource(flowers.iloc[new])
    # flw_plot.data_source.data = f2.data

    food_mlt2 = flowers.iloc[new].melt(id_vars='Shrt_Desc').dropna()
    food_cds = ColumnDataSource(food_mlt2)

    # Alt 1
    # from bokeh.models import Range1d, FactorRange
    # print(lay.children[2].y_range.factors)
    heatmap.y_range.factors = food_mlt2.Shrt_Desc.unique().tolist()
    htmp.data_source.data = food_cds.data
    heatmap.height = 50 + 50 * food_mlt2.Shrt_Desc.nunique()
    # print(food_mlt2.Shrt_Desc.unique())
    # lay.children[2].y_range = FactorRange(factors=food_mlt2.Shrt_Desc.unique())
    # print(heatmap.y_range.factors, type(heatmap.y_range.factors))
    # print(heatmap.y_range.factors, type(heatmap.y_range.factors))
    # lay.children[2].y_range.factors = food_mlt2.Shrt_Desc.unique()
    # print(lay.children[2].y_range.factors)
    # plot.x_range.setv(Range1d(0, 10))
    # plot.x_range.start = 0
    # plot.x_range = 



    # Alt 2
    # colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    # mapper = LinearColorMapper(palette=colors, low=food_mlt2['value'].min(),
    #                            high=food_mlt2['value'].max())
    # # tools = ['box_select', 'reset']
    # heatmap = figure(tools=tools, plot_height=600, plot_width=200,
    #     x_range=list(food_mlt2.variable.unique()), y_range=list(food_mlt2['Shrt_Desc'].unique()))
    # # #     toolbar_location=None, tools="", x_axis_location="above"))
    # htmp = heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1, source=food_cds,
    #        fill_color=transform('value', mapper), line_color=None)
    
    # print(lay.children)
    # lay.children[2] = heatmap
    # print(lay.children)

    # inputs = widgetbox(text, offset, amplitude, phase, freq)

    # curdoc().add_root(column(inputs, plot, heatmap, width=800))







    # if len(inds) == 0 or len(inds) == len(x):
    #     hhist1, hhist2 = hzeros, hzeros
    #     vhist1, vhist2 = vzeros, vzeros
    # else:
    #     neg_inds = np.ones_like(x, dtype=np.bool)
    #     neg_inds[inds] = False
    #     hhist1, _ = np.histogram(x[inds], bins=hedges)
    #     vhist1, _ = np.histogram(y[inds], bins=vedges)
    #     hhist2, _ = np.histogram(x[neg_inds], bins=hedges)
    #     vhist2, _ = np.histogram(y[neg_inds], bins=vedges)

    # hh1.data_source.data["top"]   =  hhist1
    # hh2.data_source.data["top"]   = -hhist2
    # vh1.data_source.data["right"] =  vhist1
    # vh2.data_source.data["right"] = -vhist2


sctr.data_source.selected.on_change('indices', update)
