from pandas import read_csv, Series
# from sklearn.manifold import TSNE
import pandas as pd
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.models.widgets import MultiSelect, CheckboxGroup, Dropdown
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

nutrients = dict(
macros = [
 'Energy',
 'Carbs',
 'Fat',
 'Protein',
 'Fiber',
],

macros_details =  [
 'Sugars',
 'Monounsaturated fat',
 'Polyunsaturated fat',
 'Saturated fat',
 'Cholesterol',
],

minerals = [
 'Calcium',
 'Copper',
 'Iron',
 'Magnesium',
 'Manganese',
 'Phosphorus',
 'Potassium',
 'Selenium',
 'Sodium',
 'Zinc'
],

vitamins = [
 'Vitamin B1 (Thiamin)',
 'Vitamin B2 (Riboflavin)',
 'Vitamin B3 (Niacin)',
 'Vitamin B4 (Pantothenic acid)',
 'Vitamin B6',
 'Vitamin B9 (Folate)',
 'Vitamin B12',
 # 'Vitamin A, IU',
 'Vitamin A',
 'Vitamin C',
 'Vitamin D (D2 + D3)',
 # 'Vitamin D (D2 + D3), International Units',
 'Vitamin E',
 'Vitamin K',
],

# eaas plus cysteine and tyrosine
aas = [
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

caretonoids = [
 'Lycopene',
 'Lutein + zeaxanthin',
 'alpha-Carotene',
 'beta-Carotene',
 # 'Retinol',
 'beta-Cryptoxanthin',
],
)

flowers = pd.read_csv('nutrimap/data/clean_rdi.csv')
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
flow_num = flowers.fillna(0.0000001).select_dtypes('number')
# flow_num_stndr = (flow_num - flow_num.mean()) / flow_num.std()
flow_num_stndr = (flow_num - flow_num.min()) / (flow_num.max() - flow_num.min())
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
                   size=7, fill_alpha=0.7, legend_group='Category', muted_alpha=0.1,
                   muted_color='colors', source=food_cds1)
legend_plot.outline_line_color = None
legend_plot.xgrid.grid_line_alpha = 0
legend_plot.ygrid.grid_line_alpha = 0
legend_plot.axis.visible = False
legend_plot.legend.border_line_alpha = 0


def create_heatmap(df, high_rdi, sort_by):
    '''Create a heatmap ordered by food similarity'''
    if 'tSNE_x' in df.columns:  # Only needed the first time
        df = df.drop(columns=['tSNE_x', 'tSNE_y', 'colors', 'Category'])
    # df.columns = df.columns.str.rpartition('_').get_level_values(0)
    # df = df.rename(columns={'Shrt': 'Shrt_Desc'})
    if sort_by is None:
        if df.shape[0] > 2:
            Z = linkage(df.select_dtypes('number').fillna(0), 'single',
                        optimal_ordering=True)
            dn = dendrogram(Z, no_plot=True)
            df_srtd = df.iloc[dn['leaves']]
            df_mlt = df_srtd.melt(id_vars='Shrt_Desc')
        else:
            df_mlt = df.melt(id_vars='Shrt_Desc')
    else:
        df_mlt = df.sort_values(sort_by).melt(id_vars='Shrt_Desc')
    plot_height = 100 + 20 * df['Shrt_Desc'].nunique()
    plot_width = len(df.columns) * 25 + 200
    # Cap colors at 100% RDI
    mapper = LogColorMapper(palette=YlOrBr, low=0, high=high_rdi)
    food_cds = ColumnDataSource(df_mlt)
    html_tooltips = """
        <div>
            <span style="font-size: 13px; color: #38b0e4;">@Shrt_Desc</span>
        </div>
        <div>
            <span style="font-size: 12px;">@variable</span>
            <span style="font-size: 14px; font-weight: bold;"> @value{0.0}%</span>
        </div>
    """
    heatmap = figure(plot_height=plot_height, plot_width=plot_width,
                     sizing_mode='fixed', x_axis_location="above",
                     y_axis_location='left',
                     x_range=list(df_mlt['variable'].unique()),
                     y_range=list(df_mlt['Shrt_Desc'].unique()),
                     tooltips=html_tooltips)
    heatmap.rect(x="variable", y="Shrt_Desc", width=1, height=1,
                 source=food_cds, fill_color=transform('value', mapper),
                 line_color=None)
    heatmap.min_border_right = 100  # To fit the angled labels
    heatmap.xaxis.major_label_text_font_size = '10pt'
    heatmap.yaxis.major_label_text_font_size = '10pt'
    heatmap.xaxis.major_label_orientation = 0.8
    heatmap.axis.major_label_standoff = 0
    heatmap.grid.grid_line_color = None
    heatmap.axis.axis_line_color = None
    heatmap.axis.major_tick_line_color = None
    heatmap.toolbar_location = None
    return heatmap


def replace_heatmap(df=None, high_rdi=100, sort_by=None):
    '''Replace the heatmap figure with one of the selected subset'''
    if df is None:
        try:
            df = df_sub
        except NameError:
            df = flowers
    # lay.children[2].children[0] = create_heatmap(df)
    lay.children[1].children[1].children[1] = create_heatmap(df, high_rdi, sort_by)


def select_category(attr, old, new):
    '''Subset foods on the selected categories'''
    # Use subgroups of columns from a previous selection
    global df_sub
    try:
        cols = df_sub.columns
    except NameError:
        cols = flowers.columns
    df_sub = flowers.loc[flowers['Category'].isin(new)][cols]
    # Pass a copy so that the column name modifications in replace_heatmap are
    # not saved in the global variable df_sub
    replace_heatmap(df_sub.copy())


def select_hm_cols(attr, old, new):
    '''Select heatmap columns'''
    new_nutrients = ['Shrt_Desc']  # Always include the name column
    for key in new:
        new_nutrients.extend(nutrients[key])
    # Use subgroups of rows from a previous selection
    global df_sub
    try:
        rows = df_sub.index
    except NameError:
        rows = flowers.index
    df_sub = flowers.loc[rows, new_nutrients]
    # Pass a copy so that the column name modifications in replace_heatmap are
    # not saved in the global variable df_sub
    replace_heatmap(df_sub.copy())


def select_scatter_points(attr, old, new):
    '''Subset foods on the data points selected in the scatter plot'''
    if len(new) == 0:
        df_sub = flowers.copy()
    else:
        df_sub = flowers.iloc[new].copy()
    replace_heatmap(df_sub)


def rdi_normalization(attr, old, new):
    if 0 in new:  # RDI norm
        print('norm')
    else:
        print('no-norm')
    if 1 in new:  # RDI cap
        high_rdi = 100
    else:
        high_rdi = None
    if 2 in new:  # Norm columns
        pass
    replace_heatmap(high_rdi=high_rdi)


def sort_by(attr, old, new):
    print(old)
    print(new)
    replace_heatmap(sort_by=new)


dd_sort = Dropdown(label='Sort by', menu=list(zip(flowers.columns, flowers.columns)), width=150)
dd_sort.on_change('value', sort_by)
# Scatter plot selection change
sctr.data_source.selected.on_change('indices', select_scatter_points)
# Multiselection list for food groups
# food_grp_options = [(grp, grp) for grp in flowers['Category'].unique()]
food_grp_options = list(zip(flowers['Category'].unique(), flowers['Category'].unique()))
food_grp_mselect = MultiSelect(options=food_grp_options, width=150,
                               value=['grains', 'greens', 'meats'])
food_grp_mselect.size = 7
food_grp_mselect.on_change('value', select_category)
# Multiselection list for heatmap columns
hm_cols_options = [(grp, grp) for grp in nutrients.keys()]
hm_cols_mselect = MultiSelect(options=hm_cols_options, width=150, value=['macros', 'macros_details', 'vitamins', 'minerals'])
hm_cols_mselect.size = 7
hm_cols_mselect.on_change('value', select_hm_cols)

checkboxes = CheckboxGroup(labels=['Normalize to RDI', 'Cap at 100% RDI'],
                           active=[0, 1])

checkboxes.on_change('active', rdi_normalization)
# Set up layouts and add to document
# Note that I have commented out the styling for now, seems not to be needed
# This could be made prettier and maybe multiline instead of soft wrap
desc_top = Div(text=
'''<head><title>Nutrimap</title></head>
<!--<style>p{margin-top: -15px;} .head {padding-right: -420px; margin-right: -420px;}</style>-->
<h1>Nutrimap</h1>
<p class="head">
This dashboard facilitates comparisons of nutrient composition between common
food items to give an overview of which foods are high and low in what
nutrients. I think colors are more efficient at presenting overviews than
tables with numbers, so I chose to present this information as heatmaps.
The data is from USDA, who don't yet collect phytonutrients, which are
generally abundant in plant-based foods. Evenutally I want to add more options
computing the RDI, but for now, the RDI is based on a 70 kg male in his 30s.
This is a minor issue since the dashboard mainly use RDI to provide a reference
value for coloring the heatmap rather than recommending how much of a certain
food item one should eat. For the latter, I highly reccomend <a
href=https://cronometer.com>Cronometer</a>.
</p>''')
desc_left = Div(text=
'''<!--<style>.left {padding-left: 0px; margin-left: 0px; padding-bottom: 2px;}</style>-->
<h2 class="left">Nutrient visualization</h2>
<p class="left">
The nutrients for 100g of each food are shown (dry weight for grains and
legumes, wet weight for everything else). The colors are normalized to RDI and
capped at 100% by default.
</p>''')
desc_right = Div(text=
'''<!--<style>.right {padding-left: 100px;, padding-right: -100px; margin-right: -100px;}</style>-->
<h2 class="right">Selection tools</h2>
<p class="right">
Pick nutrients and food groups to visualize using the lists or select
individual food items in the food similarity scatter plot by dragging with the
mouse or clicing to select. Ctrl and shift can be used to select multiple items.
</p>''')

lay = column(
    desc_top,
    row(
        column(desc_right,
               widgetbox(row(hm_cols_mselect, food_grp_mselect, column(checkboxes, dd_sort)),
                         width=550, background='#f0f0f0'),
               row(plot, legend_plot)),
        column(desc_left,
               create_heatmap(flowers, 100, None),
               width=950),
        ))
curdoc().add_root(lay)
curdoc().title = "Nutrimap"
# Temp workaroudn until I swtich to panel
select_category(0, 0, ['grains', 'greens', 'meats'])
select_hm_cols(0, 0, ['macros', 'macros_details', 'vitamins', 'minerals'])
