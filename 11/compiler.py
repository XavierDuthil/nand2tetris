def XMLToVM(XMLTree):
	vmFile = []

	fileClass = XMLTree
	className = fileClass.find('identifier').text

	# TODO : find classVarDec

	for function in fileClass.findall('subroutineDec'):
		functionName = function.find('identifier').text
		# Parameters...

		# TEMP
		localVarsCount = 0
		# /TEMP

		vmFile.append("function {className}.{functionName} {localVarsCount}".format(className=className, functionName=functionName, localVarsCount=localVarsCount))

		# Instructions
		functionBody = function.find('subroutineBody')
		instructions = functionBody.find('statements')
		for instruction in instructions:
			if instruction.tag == 'doStatement':
				parseDoStatement(vmFile, instruction)

			elif instruction.tag == 'returnStatement':
				parseReturnStatement(vmFile, instruction)

	return "\n".join(vmFile)


def parseReturnStatement(vmFile, xmlElement):
	vmFile.append('return')


def parseDoStatement(vmFile, xmlElement):
	functionName = xmlElement.findall('identifier')[-1].text

	if xmlElement.find('symbol').text == '.':
		className = xmlElement.find('identifier').text
		functionName = "{}.{}".format(className, functionName)

	expressions = xmlElement.find('expressionList').findall('expression')
	argsCount = len(expressions)

	# Arguments
	for expression in expressions:
		parseExpression(vmFile, expression)

	vmFile.append('call {functionName} {argsCount}'.format(functionName=functionName, argsCount=argsCount))


def parseExpression(vmFile, xmlElement):
	#TODO
	pass
