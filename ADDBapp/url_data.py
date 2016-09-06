#
# Utility file to generate artefacts used by Chart.js to display graphs
#


def generate_mulivariable_series_from_list(source_list):
    """
    """
    return "%s" % ("+".join([str(element) for element in source_list]))
