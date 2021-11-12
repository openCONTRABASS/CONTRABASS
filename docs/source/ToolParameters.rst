
8. Tool parameters
==================

More information about the parameters of the tool can be obtained by executing ``findCPcli -h``.

::

	$ findCPcli [-h] [-v] [-l] -i <input file> [-o <output file>]
		         [-cp <output file>] [-swD <output file>] [-sF <output file>]
		         [-swDF <output file>]

		               
	optional arguments:
	  -h, --help           show this help message and exit
	  -v, --verbose        Print feedback while running.
	  -l, --license        View license info.
	  -i <input file>      Input metabolic model. Allowed file formats: .xml .json
		               .yml
	  -o <output file>     Output spreadsheet file with results. Allowed file
		               formats: .xls .xlsx .ods
	  -cp <output file>    Output spreadsheet file with growth dependent
		               chokepoints. Allowed file formats: .xls .xlsx .ods
	  -swD <output file>   Save output model without Dead End Metabolites. Allowed
		               file formats: .xml .json .yml
	  -sF <output file>    Save output model with reactions bounds updated with
		               Flux Variability Analysis. Allowed file formats: .xml
		               .json .yml
	  -swDF <output file>  Save output model with reactions bounds updated with
		               Flux Variability Analysis and without Dead End
		               Metabolites. Allowed file formats: .xml .json .yml
	  -objective <reaction id>
		                Reaction id to be used as objective function with Flux
		                Balance Analysis
