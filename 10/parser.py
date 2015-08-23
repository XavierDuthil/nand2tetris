from Node import Node
from contextlib import suppress
from Exceptions import JackSyntaxError

BUILT_IN_TYPES = ["int", "char", "boolean"]
OPERATORS = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
UNARY_OPERATORS = ["-", "~"]


def parseFile(tokensWithTypes):
	classNode = parseClass(tokensWithTypes)

	if tokensWithTypes:
		raise Exception("Syntax error. Class ended, found {}".format(tokensWithTypes[0]))

	return classNode


def parseClass(tokensWithTypes):
	classNode = Node("class")

	keyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["class"])
	identifier = takeNode(tokensWithTypes, expectedType="identifier")
	symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["{"])
	classNode.children = [keyword, identifier, symbolOpen]

	while hasClassVarDec(tokensWithTypes):
		classVarDecNode = parseClassVarDec(tokensWithTypes)
		classNode.children.append(classVarDecNode)

	while hasSubroutineDec(tokensWithTypes):
		subroutineDecNode = parseSubroutineDec(tokensWithTypes)
		classNode.children.append(subroutineDecNode)

	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])
	classNode.children.append(symbolClose)

	return classNode


def hasSubroutineDec(tokensWithTypes):
	firstValues = ["constructor", "function", "method"]
	return tokensWithTypes[0].value in firstValues


def hasParameter(tokensWithTypes):
	tokenType = tokensWithTypes[0].type
	tokenValue = tokensWithTypes[0].value

	if tokenType == "keyword" and tokenValue in BUILT_IN_TYPES:
		return True
	elif tokenType == "identifier":
		return True

	return False


def parseSubroutineDec(tokensWithTypes):
	possibleValues = ["constructor", "function", "method"]
	subroutineDecNode = Node("subroutineDec")

	keyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=possibleValues)

	returnType = parseType(tokensWithTypes, extraTypes=["void"])

	subroutineName = takeNode(tokensWithTypes, expectedType="identifier")
	symbolParenthesisOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])

	parameterList = parseParameterList(tokensWithTypes)

	symbolParenthesisClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])
	subroutineBody = parseSubroutineBody(tokensWithTypes)

	subroutineDecNode.children.append(keyword)
	subroutineDecNode.children.append(returnType)
	subroutineDecNode.children.append(subroutineName)
	subroutineDecNode.children.append(symbolParenthesisOpen)
	subroutineDecNode.children.append(parameterList)
	subroutineDecNode.children.append(symbolParenthesisClose)
	subroutineDecNode.children.append(subroutineBody)

	return subroutineDecNode


def parseParameterList(tokensWithTypes):
	parameterListNode = Node("parameterList")

	# For each parameter :
	while hasParameter(tokensWithTypes):
		# Type handling
		varType = parseType(tokensWithTypes)

		# Variable name handling
		varName = takeNode(tokensWithTypes, expectedType="identifier")

		parameterListNode.children.append(varType)
		parameterListNode.children.append(varName)

		# Comma handling
		with suppress(JackSyntaxError):
			commaNode = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[","])
			parameterListNode.children.append(commaNode)

	return parameterListNode


def parseType(tokensWithTypes, extraTypes=None):
	extraTypes = extraTypes or []

	try:
		varType = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=extraTypes+BUILT_IN_TYPES)
	except JackSyntaxError:
		varType = takeNode(tokensWithTypes, expectedType="identifier")

	return varType


def parseSubroutineBody(tokensWithTypes):
	subroutineBodyNode = Node("subroutineBody")

	symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["{"])
	subroutineBodyNode.children.append(symbolOpen)

	while hasVarDec(tokensWithTypes):
		varDecNode = parseVarDec(tokensWithTypes)
		subroutineBodyNode.children.append(varDecNode)

	statements = parseStatements(tokensWithTypes)
	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])
	subroutineBodyNode.children.append(statements)
	subroutineBodyNode.children.append(symbolClose)

	return subroutineBodyNode


def hasVarDec(tokensWithTypes):
	return tokensWithTypes[0].value == "var"


def hasClassVarDec(tokensWithTypes):
	return tokensWithTypes[0].value in ("field", "static")


def parseVarDec(tokensWithTypes):
	varDecNode = Node("varDec")

	varKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["var"])
	varDecNode.children.append(varKeyword)

	varDecNode = _parseVarDecTypeNames(tokensWithTypes, varDecNode)
	return varDecNode


def parseClassVarDec(tokensWithTypes):
	classVarDecNode = Node("classVarDec")

	scope = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["field", "static"])
	classVarDecNode.children.append(scope)

	classVarDecNode = _parseVarDecTypeNames(tokensWithTypes, classVarDecNode)
	return classVarDecNode


def _parseVarDecTypeNames(tokensWithTypes, varDecNode):
	varType = parseType(tokensWithTypes)
	varName = takeNode(tokensWithTypes, expectedType="identifier")

	varDecNode.children.append(varType)
	varDecNode.children.append(varName)

	while tokensWithTypes[0].value == ',':
		comma = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[","])
		varName = takeNode(tokensWithTypes, expectedType="identifier")
		varDecNode.children.append(comma)
		varDecNode.children.append(varName)

	semicolon = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[";"])
	varDecNode.children.append(semicolon)
	return varDecNode


def parseStatements(tokensWithTypes):
	statementsNode = Node("statements")
	statementMapping = {
		"let": parseLetStatement,
		"if": parseIfStatement,
		"while": parseWhileStatement,
		"do": parseDoStatement,
		"return": parseReturnStatement
	}

	while hasStatement(tokensWithTypes):
		keyword = tokensWithTypes[0].value
		statement = statementMapping[keyword](tokensWithTypes)
		statementsNode.children.append(statement)

	return statementsNode


def hasStatement(tokensWithTypes):
	return tokensWithTypes[0].value in ["let", "if", "while", "do", "return"]


def parseLetStatement(tokensWithTypes):
	statementNode = Node("letStatement")

	letKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["let"])
	varName = takeNode(tokensWithTypes, expectedType="identifier")
	statementNode.children.append(letKeyword)
	statementNode.children.append(varName)

	if tokensWithTypes[0].value == "[":
		bracketOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["["])
		expression = parseExpression(tokensWithTypes)
		bracketClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["]"])
		statementNode.children.append(bracketOpen)
		statementNode.children.append(expression)
		statementNode.children.append(bracketClose)

	letKeyword = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["="])
	expression = parseExpression(tokensWithTypes)
	semicolon = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[";"])
	statementNode.children.append(letKeyword)
	statementNode.children.append(expression)
	statementNode.children.append(semicolon)

	return statementNode


def parseIfStatement(tokensWithTypes):
	statementNode = Node("ifStatement")

	ifKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["if"])
	openParenthesis = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])
	conditionNode = parseExpression(tokensWithTypes)
	closeParenthesis = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])

	openBracket = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["{"])
	body = parseStatements(tokensWithTypes)
	closeBracket = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])

	statementNode.children.append(ifKeyword)
	statementNode.children.append(openParenthesis)
	statementNode.children.append(conditionNode)
	statementNode.children.append(closeParenthesis)
	statementNode.children.append(openBracket)
	statementNode.children.append(body)
	statementNode.children.append(closeBracket)

	if tokensWithTypes[0].value == "else":
		elseKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["else"])
		openBracket = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["{"])
		elseBody = parseStatements(tokensWithTypes)
		closeBracket = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])

		statementNode.children.append(elseKeyword)
		statementNode.children.append(openBracket)
		statementNode.children.append(elseBody)
		statementNode.children.append(closeBracket)

	return statementNode


def parseWhileStatement(tokensWithTypes):
	statementNode = Node("whileStatement")

	whileKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["while"])
	openParenthesis = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])
	conditionNode = parseExpression(tokensWithTypes)
	closeParenthesis = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])

	openBracket = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["{"])
	body = parseStatements(tokensWithTypes)
	closeBracket = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])

	statementNode.children.append(whileKeyword)
	statementNode.children.append(openParenthesis)
	statementNode.children.append(conditionNode)
	statementNode.children.append(closeParenthesis)
	statementNode.children.append(openBracket)
	statementNode.children.append(body)
	statementNode.children.append(closeBracket)

	return statementNode


def parseDoStatement(tokensWithTypes):
	statementNode = Node("doStatement")

	doKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["do"])
	statementNode.children.append(doKeyword)
	statementNode.children += parseSubroutineCall(tokensWithTypes)
	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[";"])
	statementNode.children.append(symbolClose)

	return statementNode


def parseReturnStatement(tokensWithTypes):
	statementNode = Node("returnStatement")

	returnStatement = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["return"])
	statementNode.children.append(returnStatement)

	if tokensWithTypes[0].value != ";":
		expressionNode = parseExpression(tokensWithTypes)
		statementNode.children.append(expressionNode)

	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[";"])
	statementNode.children.append(symbolClose)

	return statementNode


def parseExpression(tokensWithTypes):
	expressionNode = Node("expression")

	term = parseTerm(tokensWithTypes)
	expressionNode.children.append(term)

	while tokensWithTypes[0].value in OPERATORS:
		operator = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=OPERATORS)
		term = parseTerm(tokensWithTypes)
		expressionNode.children.append(operator)
		expressionNode.children.append(term)

	return expressionNode


def parseSubroutineCall(tokensWithTypes):
	nodeList = []

	if tokensWithTypes[1].value == ".":
		objectName = takeNode(tokensWithTypes, expectedType="identifier")
		dot = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["."])
		nodeList += [objectName, dot]

	if tokensWithTypes[1].value != "(":
		raise JackSyntaxError("Expected '(', found '{}'".format(tokensWithTypes[1].value))

	subroutineName = takeNode(tokensWithTypes, expectedType="identifier")
	symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])
	expressionList = parseExpressionList(tokensWithTypes)
	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])
	nodeList += [subroutineName, symbolOpen, expressionList, symbolClose]
	return nodeList


def parseExpressionList(tokensWithTypes):
	expressionListNode = Node("expressionList")

	if hasExpression(tokensWithTypes):
		expressionNode = parseExpression(tokensWithTypes)
		expressionListNode.children.append(expressionNode)

		while hasComma(tokensWithTypes):
			commaNode = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[","])
			expressionNode = parseExpression(tokensWithTypes)
			expressionListNode.children.append(commaNode)
			expressionListNode.children.append(expressionNode)

	return expressionListNode


def hasExpression(tokensWithTypes):
	return tokensWithTypes[0].value != ")"


def hasComma(tokensWithTypes):
	return tokensWithTypes[0].value == ","


def parseTerm(tokensWithTypes):
	termNode = Node("term")

	firstNode = tokensWithTypes[0]

	if firstNode.type in ("integerConstant", "stringConstant"):
		constant = Node(firstNode.type, firstNode.value)
		tokensWithTypes.pop(0)
		termNode.children.append(constant)

	elif firstNode.type == "keyword" and firstNode.value in ("true", "false", "null", "this"):
		constant = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["true", "false", "null", "this"])
		termNode.children.append(constant)

	elif firstNode.value == "(":
		symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])
		expression = parseExpression(tokensWithTypes)
		symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])
		termNode.children.append(symbolOpen)
		termNode.children.append(expression)
		termNode.children.append(symbolClose)

	elif firstNode.value in UNARY_OPERATORS:
		unaryOp = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=UNARY_OPERATORS)
		term = parseTerm(tokensWithTypes)
		termNode.children.append(unaryOp)
		termNode.children.append(term)

	elif firstNode.type == "identifier":
		try:
			subroutineCallNodes = parseSubroutineCall(tokensWithTypes)
			termNode.children += subroutineCallNodes

		# If exception : not a subroutineCall, but a varName
		except JackSyntaxError:
			varName = takeNode(tokensWithTypes, expectedType="identifier")
			termNode.children.append(varName)

			if tokensWithTypes[0].value == "[":
				symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["["])
				expression = parseExpression(tokensWithTypes)
				symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["]"])
				termNode.children.append(symbolOpen)
				termNode.children.append(expression)
				termNode.children.append(symbolClose)

	return termNode


# Pop the first token from the list, verify condition and return as Node
def takeNode(tokensWithTypes, expectedType, possibleValues=None):
	currentToken = tokensWithTypes[0]

	if currentToken.type != expectedType:
		raise JackSyntaxError("Syntax error. Expected type {0}, found type {1} (value : '{2}')".format(expectedType, currentToken.type, currentToken.value))

	if possibleValues is not None and currentToken.value not in possibleValues:
		raise JackSyntaxError("Syntax error. Expected values '{0}', found value '{1}'".format(possibleValues, currentToken.value))

	print(tokensWithTypes[0].value)

	return Node.fromToken(tokensWithTypes.pop(0))
