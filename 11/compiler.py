def XMLToVM(XMLTree):
	vmFile = []

	fileClass = XMLTree.find('class')
	className = fileClass.find('identifier').text

	# TODO : find classVarDec*

	for function in fileClass.findall('subroutineDec'):
		functionName = function.find('identifier')
		# Parameters...
		# Instructions...


		# TEMP
		localVarsCount = 0
		# /TEMP

		vmFile.append("function {className}.{functionName} {localVarsCount}".format(className=className, functionName=functionName, localVarsCount=localVarsCount))

	return vmFile