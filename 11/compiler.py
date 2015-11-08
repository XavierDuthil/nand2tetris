import textwrap
from SymbolTable import SymbolTable

def XMLToVM(XMLTree):
	vmFile = []
	parseClass(vmFile, XMLTree)
	return "\n".join(vmFile)

def parseClass(vmFile, xmlElement):
	fileClass = xmlElement
	className = fileClass.find('identifier').text

	# TODO : find classVarDec


	for function in fileClass.findall('subroutineDec'):
		parseFunction(vmFile, function, className)

def parseFunction(vmFile, xmlElement, className):
	function = xmlElement
	functionName = function.find('identifier').text
	# Parameters...

	functionBody = function.find('subroutineBody')

	# Local vars
	methodSymbolTable = SymbolTable()
	localVarsCount = 0
	varDeclarations = functionBody.findall('varDec')
	for varDeclaration in varDeclarations:
		parseVarDeclaration(vmFile, varDeclaration, methodSymbolTable)
		
	localVarsCount = methodSymbolTable.countSymbols("local")
	vmFile.append("function {className}.{functionName} {localVarsCount}".format(className=className, functionName=functionName, localVarsCount=localVarsCount))

	# Instructions
	instructions = functionBody.find('statements')
	for instruction in instructions:
		if instruction.tag == 'doStatement':
			parseDoStatement(vmFile, instruction)

		elif instruction.tag == 'returnStatement':
			parseReturnStatement(vmFile, instruction)


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
	term1 = xmlElement[0]
	parseTerm(vmFile, term1)

	if len(xmlElement) > 1:
		operator = xmlElement[1].text
		term2 = xmlElement[2]
		parseTerm(vmFile, term2)

		if operator == '+':
			vmFile.append('add')
		elif operator == '-':
			vmFile.append('sub')
		elif operator == '*':
			instructions = textwrap.dedent('''\
				// We already have the 2 operands in the stack, we store them in temp0 and temp1
				pop temp 0
				pop temp 1

				// Result initialisation
				push constant 0

				// Loop
				label MULTIPLICATION_LOOP
			
					// Counter decrement
					push temp 1
					push constant 1
					sub
					pop temp 1

					// Verify loop condition: until counter < 0
					push temp 1
					push constant 0
					lt
					if-goto MULTIPLICATION_END

					// Add first term value
					push temp 0
					add

					goto MULTIPLICATION_LOOP

				label MULTIPLICATION_END''').format(term1=term1.text, term2=term2.text)
			vmFile.extend(instructions.split("\n"))

def parseTerm(vmFile, xmlElement):
	if len(xmlElement) == 1:
		value = xmlElement[0].text
		if xmlElement[0].tag == 'integerConstant':
			vmFile.append('push constant {}'.format(value))

		""" TODO
		elif xmlElement.tag == 'stringConstant':
		elif xmlElement.tag == 'keywordConstant':
		elif xmlElement.tag == 'varName':

		etc..."""

	elif len(xmlElement) == 3:
		if xmlElement[0].text == '(' and xmlElement[2].text == ')':
			parseExpression(vmFile, xmlElement[1])


def parseVarDeclaration(vmFile, xmlElement, methodSymbolTable):
	varType = xmlElement[1].text
	varNames = []

	for varNameNode in xmlElement.findall("identifier"):
		varName = varNameNode.text
		if varName == varType:
			continue

		methodSymbolTable.addSymbol(varName, varType, "local")
