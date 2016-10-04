from django import forms

# connection with MongoDb
from pymongo import MongoClient
# import gridfs
client = MongoClient()

class fileUploadForm(forms.Form):
	uploadType = forms.ChoiceField(choices=(('samples', 'samples'), ('annotation', 'annotation')), label="Upload file type")
	fileUpload = forms.FileField(label="Upload Your File")

# def get_filterby_choice():
# 	db = client.addb
# 	choices_list = db.mapreduce(
# 		mapFunction() { for (var key in this) { emit(key, null); }},
# 		function(key, stuff) { return null; }, 
# 		{
# 			out: "key_totals"
# 		}
# 	)
filterby_choices_list = (
	('GEOseries','GEOseries'),
	('age','age'),
	('gender','gender'),
	('region','region'),
	('disease_state','disease_state'),
	('pmi','pmi'),
	('rin','rin'),
	('batch','batch'),
	('pres','pres'),
	('ph','ph'),
)
relation_choices_list = (
	('$gt', 'greater than'),
	('$gte', 'greater than or equal'),
	('$lt', 'less than'),
	('$lte', 'less than or equal'),
	('$eq', 'equal to (number)'),
	('$ne', 'not equal to'),
	('$regex', 'contain'),
	('!$regex', 'does not contain'),
	('$exists', 'has field'),
	('!$exists', 'has no field'),
	('$in', 'within'),
	('$nin', 'not within'),
)
# 	return choices_list


class sampleFilterForm(forms.Form):
	# def __init__(self, *args, **kwargs):
	# 	super(sampleFilterForm, self).__init__()
		
	# 	filterBy_list = db[keyCol.result].distinct("_id")
	# 	import pdb; pdb.set_trace()
	# 	# filterBy_list = []
	filterBy_0 = forms.ChoiceField(choices=filterby_choices_list, label="Filtered By")
	relation_0 = forms.ChoiceField(choices=relation_choices_list, label="Relation")
	keyword_0 = forms.CharField(max_length=100, label="Keyword")
	
	extra_field_count = forms.CharField(widget=forms.HiddenInput())
	def __init__(self, *args, **kwargs):
		extra_fields = kwargs.pop('extra', 0)

		super(sampleFilterForm, self).__init__(*args, **kwargs)
		self.fields['extra_field_count'].initial = extra_fields
		# import pdb; pdb.set_trace()
		
		for index in range(int(extra_fields) + 1):
			# generate extra fields in the number specified via extra_fields
			self.fields['filterBy_{index}'.format(index=index)] = forms.ChoiceField(choices=filterby_choices_list, label="Filtered By")
			self.fields['relation_{index}'.format(index=index)] = forms.ChoiceField(choices=relation_choices_list, label="Relation")
			self.fields['keyword_{index}'.format(index=index)] = forms.CharField(max_length=100, label="Keyword")


category_choices_list = (
	# ('gender','Gender'),
	('region','Region'),
	('MMSE','MMSE'),
	# ('age','Age'),
)
group_choices_list = (
	('ALL', 'ALL'),
	('PFC', 'PFC'),
	('HIP', 'HIP'),
	('EC', 'EC'),
	('VI', 'VI'),
	('CE', 'CE'),
	('MTG', 'MTG'),
	('PC', 'PC'),
	('PVC', 'PVC'),
	('SFG', 'SFG'),
	('TC', 'TC'),
)

comparison_choices_list = (
	('AD-vs-Control', 'AD-vs-Control'),
)

dataType_choices_list = (
	('RNA', 'RNA'),
	('protein', 'Protein'),
)

tissue_choices_list = (
	('brain', 'brain'),
	('blood', 'blood'),
)

probe_select_choices_list = (
	('fold change', 'fold change'),
	# ('limma p value', 'limma p value'),
	# ('t test p value', 't test p value'),
)



class featureSelectionForm(forms.Form):
	dataType = forms.ChoiceField(choices=dataType_choices_list, label="Choose samples of a data type")
	tissue = forms.ChoiceField(choices=tissue_choices_list, label="Choose a tissue")
	category = forms.ChoiceField(choices=category_choices_list, label="Choose a category to analyze")
	group = forms.ChoiceField(choices=group_choices_list, label="Choose a category value")
	comparison = forms.ChoiceField(choices=comparison_choices_list, label="Choose a comparison")
	probeSelectionMethod = forms.ChoiceField(choices=probe_select_choices_list, label="Choose a way to select probe when duplicate found")
	featureInput = forms.CharField(widget=forms.Textarea(attrs={"placeholder" : "APOE\nBIN\nCLU"}), label="Input the features in interest")