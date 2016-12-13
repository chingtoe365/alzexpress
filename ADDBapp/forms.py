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
	('RNAseq', 'RNAseq'),
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
	dataType = forms.ChoiceField(choices=dataType_choices_list, label="Choose samples of a data type", widget=forms.Select(attrs={'class' : 'form-control'}))
	tissue = forms.ChoiceField(choices=tissue_choices_list, label="Choose a tissue", widget=forms.Select(attrs={'class' : 'form-control'}))
	category = forms.ChoiceField(choices=category_choices_list, label="Choose a category to analyze", widget=forms.Select(attrs={'class' : 'form-control'}))
	group = forms.ChoiceField(choices=group_choices_list, label="Choose a category value", widget=forms.Select(attrs={'class' : 'form-control'}))
	comparison = forms.ChoiceField(choices=comparison_choices_list, label="Choose a comparison", widget=forms.Select(attrs={'class' : 'form-control'}))
	probeSelectionMethod = forms.ChoiceField(choices=probe_select_choices_list, label="Choose a way to select probe when duplicate found", widget=forms.Select(attrs={'class' : 'form-control'}))
	featureInput = forms.CharField(widget=forms.Textarea(attrs={"placeholder" : "APOE\nBIN\nCLU", "class" : "form-control"}), label="Input the features in interest")



class tissueDataTypeSelectionForm(forms.Form):
	RNA_blood_region__ALL_AD__vs__Control = forms.BooleanField(label="RNA - Blood", required=False)
	protein_blood_region__ALL_AD__vs__Control = forms.BooleanField(label="Protein - Blood", required=False)
	protein_blood_region__ALL_AD__vs__Control = forms.BooleanField(label="RNAseq - PFC", required=False)
	RNA_brain_region__PFC_AD__vs__Control = forms.BooleanField(label="RNA - PFC", required=False)
	RNA_brain_region__HIP_AD__vs__Control = forms.BooleanField(label="RNA - HIP", required=False)
	RNA_brain_region__PC_AD__vs__Control = forms.BooleanField(label="RNA - PC", required=False)
	RNA_brain_region__POCG_AD__vs__Control = forms.BooleanField(label="RNA - POCG", required=False)
	RNA_brain_region__PVC_AD__vs__Control = forms.BooleanField(label="RNA - PVC", required=False)
	RNA_brain_region__SFG_AD__vs__Control = forms.BooleanField(label="RNA - SFG", required=False)
	RNA_brain_region__TC_AD__vs__Control = forms.BooleanField(label="RNA - TC", required=False)
	RNA_brain_region__VI_AD__vs__Control = forms.BooleanField(label="RNA - VI", required=False)
	RNA_brain_region__EC_AD__vs__Control = forms.BooleanField(label="RNA - EC", required=False)
	RNA_brain_region__CE_AD__vs__Control = forms.BooleanField(label="RNA - CE", required=False)
	# dataType = forms.ChoiceField(choices=dataType_choices_list, label="Choose samples of a data type")