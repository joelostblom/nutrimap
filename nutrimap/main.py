from pandas import read_csv, Series
# from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.models.widgets import MultiSelect
from bokeh.layouts import widgetbox, column, row
from bokeh.models import ColumnDataSource, LogColorMapper
from bokeh.palettes import Category10_10, Category20_20, YlOrBr9


coi = ['Shrt_Desc', 'Energ_Kcal', 'Protein_(g)',
       'Lipid_Tot_(g)', 'Carbohydrt_(g)', 'Fiber_TD_(g)',
       'Sugar_Tot_(g)', 'FA_Sat_(g)', 'FA_Mono_(g)', 'FA_Poly_(g)']
minerals = ['Calcium_(mg)', 'Iron_(mg)', 'Magnesium_(mg)', 'Phosphorus_(mg)',
            'Potassium_(mg)', 'Sodium_(mg)', 'Zinc_(mg)', 'Copper_mg)',
            'Manganese_(mg)', 'Selenium_(µg)']
vitamins = ['Thiamin_(mg)', 'Riboflavin_(mg)', 'Niacin_(mg)', 'Vit_B6_(mg)',
            'Vit_A_IU', 'Vit_C_(mg)', 'Vit_E_(mg)', 'Vit_K_(µg)']
# 'Panto_Acid_mg)', 'Folate_DFE_(µg)',
# vit a from chronometer, not canada
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
             'Butternuts,dried', 'Nuts,cashew nuts,raw',
             'Hazelnuts or filberts', 'Hickorynuts,dried',
             'Macadamia nuts,raw', 'Nuts,pilinuts,dried',
             'Nuts,pine nuts,dried', 'Pistachio nuts,raw', 'Walnuts,english',
             'Coconut meat,dried (desiccated),crmd', 'Peanuts,all types,raw']
    }
foods_all = read_csv('nutrimap/data/ABBREV.csv', usecols=coi, index_col=0)
foods_all.index = foods_all.index.str.capitalize()
foods = foods_all.loc[[x for sl in food_grps.values() for x in sl]].copy()
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
        new_row.loc[col_name] = round(
            100 * row[col_name] / df_rdi.loc[
                df_rdi['MatchedNutrient'] == col_name, 'Amount'].values[0], 1)
    return new_row


flowers = flowers.apply(get_rdi, axis=1)
flowers['Category'] = ''
for grp_name in food_grps:
    new_food = [x for x in food_grps[grp_name] if x not in na_foods]
    flowers.loc[new_food, 'Category'] = grp_name
flowers = flowers.reset_index().copy()

flowers['Shrt_Desc'] = flowers['Shrt_Desc'].str[:20]
# Projection figure
plot = figure(plot_height=400, plot_width=400, title='Food similarity',
              tools="box_select,pan,reset,save,wheel_zoom,tap",
              active_drag='box_select', tooltips=[('', '@Shrt_Desc')],)
plot.toolbar.autohide = True
# Standardize for PCA
flow_num = flowers.select_dtypes('number')
flow_num_stndr = (flow_num - flow_num.mean()) / flow_num.std()
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
# Temporary
food_cds1 = ColumnDataSource(flowers)
sctr = plot.circle('tSNE_x', 'tSNE_y', line_color=None, fill_color='colors',
                   size=7, fill_alpha=0.7, legend='Category', muted_alpha=0.1,
                   muted_color='colors', source=food_cds1)


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
              .melt(id_vars='Shrt_Desc'))
    plot_height = 100 + 20 * df['Shrt_Desc'].nunique()
    mapper = LogColorMapper(palette=YlOrBr9[::-1], low=0, high=100)
    food_cds = ColumnDataSource(df_mlt)
    tools = ['box_select', 'reset']
    heatmap = figure(tools=tools, plot_height=plot_height, plot_width=400,
                     sizing_mode='fixed', x_axis_location="above",
                     y_axis_location='right',
                     x_range=list(df_mlt['variable'].unique()),
                     y_range=list(df_mlt['Shrt_Desc'].unique()),
                     tooltips=[('', '@variable @value{0.0} %')])
    heatmap.xaxis.major_label_orientation = 0.8
    heatmap.axis.major_label_standoff = 0
    heatmap.grid.grid_line_color = None
    heatmap.axis.axis_line_color = None
    heatmap.axis.major_tick_line_color = None
    heatmap.toolbar.autohide = True
    heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1,
                 source=food_cds, fill_color=transform('value', mapper),
                 line_color=None)
    return heatmap


def update_webapp(df_sub):
    lay.children[0] = create_heatmap(df_sub)


def drop_select(attr, old, new):
    df_sub = flowers.loc[flowers['Category'].isin(new)]
    update_webapp(df_sub)


def selection_change(attr, old, new):
    if len(new) == 0:
        flowers2 = flowers.copy()
    else:
        flowers2 = flowers.iloc[new].copy()
    update_webapp(flowers2)


# Scatter plot selection
sctr.data_source.selected.on_change('indices', selection_change)
# Multiselection list
mselect_options = [(grp, grp) for grp in food_grps.keys()]
food_grp_mselect = MultiSelect(options=mselect_options)
food_grp_mselect.size = 5
food_grp_mselect.on_change('value', drop_select)
# Set up layouts and add to document
lay = row(
        create_heatmap(flowers),
        column(widgetbox(food_grp_mselect), plot),
        height=300, width=2000, sizing_mode='fixed')
curdoc().add_root(lay)
curdoc().title = "Sliders"
