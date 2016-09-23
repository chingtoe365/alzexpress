#
# Utility file to generate artefacts used by Chart.js to display graphs
#
import requests

import pandas as pd

from views_constants import annotation_client

def generate_mulivariable_series_from_list(source_list):
    """
    """
    return "%s" % ("+".join([str(element) for element in source_list]))


def generate_string_id_get_query_from_list(source_list):
    """
    """
    return "%s" % ("%0D".join([str(element) for element in source_list]))

def from_symbol_to_entrez_gene_id(row):
	"""
	convert symbol to entrez gene id
	"""
	gene_entry = annotation_client.get_entrez_gene_id_from_symbol(row['symb'])
	# import pdb; pdb.set_trace()
	egid = str(gene_entry['entrez_gene_id'][0]) if gene_entry is not None else "0"
	return egid


def from_single_symbol_to_string_id(symb_series):
	"""
	convert symbol to STRING id
	"""
	queried_genes = symb_series.values.tolist()
	query_gene_str = "%0D".join(queried_genes)
	url = "http://string-db.org/api/tsv-no-header/resolveList?identifiers=%s&species=9606" % (query_gene_str, )
	response = requests.get(url)

	# print response.content
	# import pdb;pdb.set_trace();
	returned_symbols = [x.split("\t")[4] for x in response.content.split("\n") if not not x]
	returned_string_ids = [x.split("\t")[1] for x in response.content.split("\n") if not not x]

	return pd.Series(returned_string_ids)[pd.Series(returned_symbols).isin(queried_genes)].values.tolist()
	# gene_entry = annotation_client.get_entrez_gene_id_from_symbol(row['symb'])
	# import pdb; pdb.set_trace()
	# egid = str(gene_entry['entrez_gene_id'][0]) if gene_entry is not None else "0"
	# return egid
	# return response


