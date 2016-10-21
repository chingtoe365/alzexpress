#
# Utility file to generate artefacts used by Chart.js to display graphs
#
import pandas as pd
import numpy as np

def generate_series_from_list(source_list):
    """
    """
    return "[%s]" % (", ".join([str(element) for element in source_list]))


def generate_labels_from_list(source_list):
    """
    Create a string list of items suitable for Chart.js graph
    """
    return generate_series_from_list(source_list)


def generate_graphset_data_from_list(titles, data_series):
    """
    Generate a string that can be used as dataset in Chart.js
    """
    graphsets = []
    for i in range(0, len(titles)):
        graphsets.append(
            {
                'title': titles[i],
                'data': generate_series_from_list(data_series[i]),
            }
        )
    return graphsets


def generate_scatterplot_series(sample_range, start_x, expression_table):
    """
        Generate a list of cordinates for one-dimensional scatterplot
        It's a list like this
        [[1, y0], [1, y2], [1, y3], ...[2, y4], [2, y5], ....]
        1, 2, 3, .... represent different x-value for different features in the plot
    """
    df = pd.DataFrame(columns=['x', 'y'])
    
    for i in range(0, expression_table.shape[1]):
        y_coord = expression_table.iloc[sample_range, i]
        x_coord = [start_x + 2 * i] * len(sample_range)
        new_df = pd.DataFrame({'x' : x_coord, 'y' : y_coord})
        new_df = new_df[np.invert(np.isnan(y_coord))]
        df = df.append(new_df, ignore_index=True)

    return df.values.tolist()

def generate_volcanoplot_series(fold_change_p_value_df):
    # fold_change_p_value_df = fold_change_p_value_df.drop(['pid', 'symb'], axis=1)
    fold_change_p_value_df['lp'] = -np.log10(fold_change_p_value_df['lp'])
    fold_change_p_value_df['temp'] = fold_change_p_value_df['lp'] + fold_change_p_value_df['fc']
    not_null_boolean_array = np.invert(np.isnan(fold_change_p_value_df['temp']))
    # not_null_boolean_array_fc = np.invert(np.isnan(fold_change_p_value_df['fc']))
    fold_change_p_value_df = fold_change_p_value_df[not_null_boolean_array]

    differentially_expressed_probes_or_not = (abs(fold_change_p_value_df['fc']) > np.log2(1.5)) & (fold_change_p_value_df['lp'] > -np.log10(0.05))
    normal_probes_or_not = list(np.invert(differentially_expressed_probes_or_not))
    differentially_expressed_probes_df = fold_change_p_value_df[differentially_expressed_probes_or_not]
    normal_expressed_probes_df = fold_change_p_value_df[normal_probes_or_not]

    deg_symbols = list(differentially_expressed_probes_df['symb'])
    deg_symbols = [x.encode('utf-8') for x in deg_symbols]
    normal_symbols = list(normal_expressed_probes_df['symb'])
    normal_symbols = [x.encode('utf-8') for x in normal_symbols]

    # print symbols
    differentially_expressed_probes_df = differentially_expressed_probes_df[['fc', 'lp']]
    normal_expressed_probes_df = normal_expressed_probes_df[['fc', 'lp']]
    
    deg_series = differentially_expressed_probes_df.values.tolist()
    normal_series = normal_expressed_probes_df.values.tolist()

    return deg_series, normal_series, deg_symbols, normal_symbols
