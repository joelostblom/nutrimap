from pandas import read_csv, Series
# from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.models.widgets import MultiSelect
from bokeh.layouts import widgetbox, column, row
from bokeh.models import ColumnDataSource, LogColorMapper, Div
from bokeh.palettes import Category10_10, Category20_20


# Exported from mpl via "', '".join([colors.rgb2hex(x) for x in cm.YlOrBr(range(256))])
YlOrBr = [
    '#ffffe5', '#ffffe4', '#fffee2', '#fffee1', '#fffee0', '#fffedf', '#fffddd',
    '#fffddc', '#fffddb', '#fffdd9', '#fffcd8', '#fffcd7', '#fffcd6', '#fffcd4',
    '#fffbd3', '#fffbd2', '#fffbd0', '#fffbcf', '#ffface', '#fffacd', '#fffacb',
    '#fffaca', '#fff9c9', '#fff9c7', '#fff9c6', '#fff9c5', '#fff8c4', '#fff8c2',
    '#fff8c1', '#fff8c0', '#fff7be', '#fff7bd', '#fff7bc', '#fff6ba', '#fff6b9',
    '#fff5b8', '#fff4b6', '#fff4b5', '#fff3b4', '#fff3b2', '#fff2b1', '#fff1b0',
    '#fff1ae', '#fff0ad', '#ffefac', '#ffefaa', '#ffeea9', '#ffeea8', '#feeda6',
    '#feeca5', '#feeca4', '#feeba2', '#feeaa1', '#feeaa0', '#fee99e', '#fee89d',
    '#fee89b', '#fee79a', '#fee799', '#fee697', '#fee596', '#fee595', '#fee493',
    '#fee392', '#fee390', '#fee28e', '#fee18c', '#fee08a', '#fedf88', '#fede86',
    '#fedd84', '#fedc82', '#fedb80', '#feda7e', '#fed97c', '#fed87a', '#fed778',
    '#fed676', '#fed573', '#fed471', '#fed36f', '#fed26d', '#fed16b', '#fed069',
    '#fecf67', '#fece65', '#fecd63', '#fecc61', '#fecb5f', '#feca5d', '#fec95b',
    '#fec859', '#fec857', '#fec754', '#fec652', '#fec550', '#fec34f', '#fec24d',
    '#fec14c', '#febf4b', '#febe4a', '#febd49', '#febb47', '#feba46', '#feb945',
    '#feb744', '#feb643', '#feb541', '#feb340', '#feb23f', '#feb13e', '#feaf3d',
    '#feae3b', '#fead3a', '#feab39', '#feaa38', '#fea937', '#fea736', '#fea634',
    '#fea433', '#fea332', '#fea231', '#fea030', '#fe9f2e', '#fe9e2d', '#fe9c2c',
    '#fe9b2b', '#fe9a2a', '#fe9829', '#fd9728', '#fd9627', '#fc9427', '#fb9326',
    '#fb9225', '#fa9125', '#fa8f24', '#f98e23', '#f98d23', '#f88b22', '#f88a21',
    '#f78921', '#f68820', '#f6861f', '#f5851f', '#f5841e', '#f4821d', '#f4811d',
    '#f3801c', '#f27f1b', '#f27d1b', '#f17c1a', '#f17b1a', '#f07919', '#f07818',
    '#ef7718', '#ee7617', '#ee7416', '#ed7316', '#ed7215', '#ec7014', '#eb6f14',
    '#ea6e13', '#e96d13', '#e86c12', '#e76b11', '#e66a11', '#e56910', '#e46710',
    '#e3660f', '#e2650f', '#e1640e', '#e0630d', '#df620d', '#de610c', '#dd5f0c',
    '#dc5e0b', '#db5d0b', '#da5c0a', '#d95b09', '#d85a09', '#d75908', '#d65808',
    '#d55607', '#d45507', '#d35406', '#d25306', '#d15205', '#d05104', '#cf5004',
    '#ce4f03', '#cd4d03', '#cc4c02', '#cb4b02', '#c94b02', '#c84a02', '#c64902',
    '#c44802', '#c34802', '#c14702', '#c04602', '#be4503', '#bc4503', '#bb4403',
    '#b94303', '#b84203', '#b64203', '#b44103', '#b34003', '#b13f03', '#b03f03',
    '#ae3e03', '#ac3d03', '#ab3c03', '#a93c03', '#a83b03', '#a63a03', '#a43904',
    '#a33904', '#a13804', '#a03704', '#9e3604', '#9c3604', '#9b3504', '#993404',
    '#983404', '#963304', '#943304', '#933204', '#913204', '#903104', '#8e3104',
    '#8c3004', '#8b3005', '#892f05', '#882f05', '#862e05', '#842e05', '#832d05',
    '#812d05', '#802d05', '#7e2c05', '#7c2c05', '#7b2b05', '#792b05', '#782a05',
    '#762a05', '#742905', '#732905', '#712806', '#702806', '#6e2706', '#6c2706',
    '#6b2606', '#692606', '#682506', '#662506']

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
             'Coconut meat,dried (desiccated),crmd', 'Peanuts,all types,raw'],
    'fruits': ["Apples,raw,with skin",
               'Pineapple,raw', 'Plums,raw', 'Pears,raw',
               'Apricots,raw', 'Avocados,raw,all comm var',
               'Blackberries, frozen, unsweetened', 'Blueberries,raw',
               'Cranberries,raw', 'Raspberries,raw', 'Clementines,raw',
               'Strawberries,raw', 'Dates,medjool', 'Plantains,raw',
               'Pomegranates,raw', 'Bananas,raw',
               'Kiwifruit,green,raw', 'Figs,dried,uncooked', 'Oranges,raw,all comm var',
               'Apricots,dried,sulfured,unckd', 'Olives,ripe,cnd (small-extra lrg)']
    }

nutrients = dict(
    macros=['Energ_Kcal', 'Protein_(g)',
            'Lipid_Tot_(g)', 'Carbohydrt_(g)', 'Fiber_TD_(g)'],
    macros_details=['Sugar_Tot_(g)', 'FA_Sat_(g)', 'FA_Mono_(g)', 'FA_Poly_(g)'],
    minerals=['Zinc_(mg)', 'Magnesium_(mg)', 'Calcium_(mg)', 'Iron_(mg)',
              'Potassium_(mg)', 'Sodium_(mg)', 'Selenium_(µg)',
              'Phosphorus_(mg)', 'Copper_mg)', 'Manganese_(mg)'],
    vitamins=['Thiamin_(mg)', 'Riboflavin_(mg)', 'Niacin_(mg)', 'Vit_B6_(mg)',
              'Vit_A_IU', 'Vit_C_(mg)', 'Vit_E_(mg)', 'Vit_K_(µg)']
)
# 'Panto_Acid_mg)', 'Folate_DFE_(µg)',
# vit a from chronometer, not canada
coi = ['Shrt_Desc'] + [x for sub in nutrients.values() for x in sub]

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
    '''Calculate the RDI'''
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
plot.xgrid.grid_line_alpha = 0
plot.ygrid.grid_line_alpha = 0
plot.outline_line_color = None
plot.toolbar.logo = None
plot.toolbar_location = 'above'

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
food_cds1 = ColumnDataSource(flowers)
sctr = plot.circle('tSNE_x', 'tSNE_y', line_color=None, fill_color='colors',
                   size=7, fill_alpha=0.7, muted_alpha=0.1,
                   muted_color='colors', source=food_cds1)

legend_plot = figure(plot_height=200, plot_width=140, y_range=(1111, 2222))
legend_plot.toolbar.autohide = True
legend_plot.circle('tSNE_x', 'tSNE_y', line_color=None, fill_color='colors',
                   size=7, fill_alpha=0.7, legend='Category', muted_alpha=0.1,
                   muted_color='colors', source=food_cds1)
legend_plot.outline_line_color = None
legend_plot.xgrid.grid_line_alpha = 0
legend_plot.ygrid.grid_line_alpha = 0
legend_plot.axis.visible = False
legend_plot.legend.border_line_alpha = 0


def create_heatmap(df):
    '''Create a heatmap ordered by food similarity'''
    df = df.drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category'])
    df.columns = df.columns.str.rpartition('_').get_level_values(0)
    df = df.rename(columns={'Shrt': 'Shrt_Desc'})
    if df.shape[0] > 2:
        Z = linkage(df.select_dtypes('number').dropna(), 'single')
        dn = dendrogram(Z, no_plot=True)
        df_srtd = df.iloc[dn['leaves']]
        df_mlt = df_srtd.melt(id_vars='Shrt_Desc')
    else:
        df_mlt = df.melt(id_vars='Shrt_Desc')
    plot_height = 100 + 20 * df['Shrt_Desc'].nunique()
    plot_width = len(coi) * 30
    # Cap colors at 100% RDI
    mapper = LogColorMapper(palette=YlOrBr, low=0, high=100)
    food_cds = ColumnDataSource(df_mlt)
    tools = ['box_select', 'reset']
    heatmap = figure(tools=tools, plot_height=plot_height, plot_width=plot_width,
                     sizing_mode='fixed', x_axis_location="above",
                     y_axis_location='right',
                     x_range=list(df_mlt['variable'].unique()),
                     y_range=list(df_mlt['Shrt_Desc'].unique()),
                     tooltips=[('', '@variable @value{0.0} %')])
    heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1,
                 source=food_cds, fill_color=transform('value', mapper),
                 line_color=None)
    heatmap.xaxis.major_label_orientation = 0.8
    heatmap.axis.major_label_standoff = 0
    heatmap.grid.grid_line_color = None
    heatmap.axis.axis_line_color = None
    heatmap.axis.major_tick_line_color = None
    heatmap.toolbar.autohide = True
    return heatmap


def replace_heatmap(df):
    '''Replace the heatmap figure with one of the selected subset'''
    lay.children[2].children[0] = create_heatmap(df)


def select_category(attr, old, new):
    '''Subset foods on the selected category'''
    df_sub = flowers.loc[flowers['Category'].isin(new)]
    replace_heatmap(df_sub)


def selection_change(attr, old, new):
    '''Subset foods on the selected data points'''
    if len(new) == 0:
        df_sub = flowers.copy()
    else:
        df_sub = flowers.iloc[new].copy()
    replace_heatmap(df_sub)


# Scatter plot selection change
sctr.data_source.selected.on_change('indices', selection_change)
# Multiselection list change
mselect_options = [(grp, grp) for grp in food_grps.keys()]
food_grp_mselect = MultiSelect(options=mselect_options)
food_grp_mselect.size = 5
food_grp_mselect.on_change('value', select_category)
# Set up layouts and add to document
desc_top = Div(text='<style>p{margin-top: -15px;} .head {padding-right: -420px; margin-right: -420px;}</style><h1>Nutrimap</h1><p class="head">The goal of this web app is to facilitate comparisons of nutrient content in food and to find nutrionally similar food items. This app is still under active development and more food items are to be added.</p>')
desc_left = Div(text='<style>.left {padding-left: 0px; margin-left: 0px; padding-bottom: 2px;}</style><h2 class="left">Nutrient visualization</h2><p class="left">The colors are normalized to RDI and capped at 100%.<br></p>')
desc_right = Div(text='<style>.right {padding-left: 100px;, padding-right: -100px; margin-right: -100px;}</style><h2 class="right">Selection tools</h2><p class="right">Pick a group to visualize or select data points in the food similarity scatter plot.<br></p>')
lay = column(
    desc_top,
    row(desc_left, desc_right),
    row(create_heatmap(flowers), column(widgetbox(food_grp_mselect), row(plot, legend_plot)),
        sizing_mode='fixed'))
curdoc().add_root(lay)
curdoc().title = "Sliders"
