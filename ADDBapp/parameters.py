# Some parameters set here

DB_HOST = "localhost"
DB_PORT = 27017

# about the database

ALL_PLATFORMS = ["rosetta", "affymetrix", "illumina", "agilent"]
ALL_REGIONS = ["CE", "EC", "HIP", "MTG", "PC", "PFC", "PVC", "SFG", "TC", "VI", ]

KEYS_WITH_FLEXIBLE_LENGTH = ALL_PLATFORMS

# From the perspective of a researcher

TISSUE_IN_INTEREST = ['brain', 'blood', ]
DATA_TYPE_IN_INTEREST = ['RNA', 'Protein', ]
# CATEGORY_IN_INTEREST = ['region', 'gender', ]
CATEGORY_IN_INTEREST = ['region', ]