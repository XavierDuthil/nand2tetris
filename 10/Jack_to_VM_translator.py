import argparse
import re  # regular expressions
import sys  # stdout
import os
import time
from string import ascii_letters
from string import digits
from string import whitespace
import xml.etree.ElementTree as ET
from collections import namedtuple
from Node import Node
from contextlib import suppress
from Exceptions import JackSyntaxError
import pdb

#REGEX_FIRST_WORD = re.compile('^([^ ]*)')
REGEX_TOKEN_TYPE_IDENTIFIER = re.compile('[a-zA-Z_]\w*')
#COMMANDS = {}
Token = namedtuple("Token", ["type", "value"])
BUILT_IN_TYPES = ["int", "char", "boolean"]
OPERATORS = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
UNARY_OPERATORS = ["-", "~"]

def readArguments():
	parser = argparse.ArgumentParser(description='Translate Jack code to VM code.')
	parser.add_argument('jackFiles', type=str, nargs='+', help='the files to translate')

	return parser.parse_args()

def readJackPrograms(jackFile):
	with open(jackFile, 'r') as f:
		fileContent = f.read()

	return stripComments(fileContent)

def stripComments(program):
	program = re.sub("/\*.*?\*/", "", program, flags=re.DOTALL)
	program = re.sub(r"//.*", "", program)
	return program

def translate(jackProgram):
	return jackProgram
	for line in jackProgram:
		firstWord = REGEX_FIRST_WORD.match(line).group(1)

		if firstWord in COMMANDS:
			COMMANDS[firstWord](outputProgram, line, jackProgram)

		else:
			print("Line ignored : {line}".format(line=line))

	return outputProgram

def tokenize(jackProgram):
	token = ""
	tokens = []
	isInString = False
	tokenDictionary = {}

	for char in jackProgram:
		# Case of a String :
		if char == '"':
			if isInString:
				isInString = False
				token += char
				tokens.append(token)
				token = ""
				continue
			isInString = True
			token += char
			continue

		if isInString:
			token += char
			continue

		# Case of the rest
		if char in ascii_letters or char in digits or char == '_':
			token += char
			continue

		# if already building a tokenString and it breaks
		if token:
			tokens.append(token)
			token = ""
		
		if char in whitespace:
			continue

		# Case of a symbol
		else:
			tokens.append(char)
			token = ""
			continue

	return tokens

def analyseTokenType(tokenList):
	knownKeywords = ("class","constructor","function","method","field","static","var","int","char","boolean",
		"void","true","false","null","this","let","do","if","else","while","return",)
	knownSymbols = ("{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~",)
	tokensWithTypes = []

	for token in tokenList:
		if token in knownKeywords:
			tokenType = "keyword"

		elif token in knownSymbols:
			tokenType = "symbol"

		elif token.isdigit() and 0 <= int(token) <= 32767:
			tokenType = "integerConstant"
			
		elif token.startswith('"') and token.endswith('"'):
			token = token[1:-1]
			tokenType = "stringConstant"

		elif REGEX_TOKEN_TYPE_IDENTIFIER.match(token):
			tokenType = "identifier"

		else:
			raise Exception("Error : invalid token {}".format(token))

		tokensWithTypes.append(Token(value=token, type=tokenType))
	return tokensWithTypes

def tokenListToXML(tokensWithTypes):
	root = ET.Element("tokens")

	for tokenType, tokenValue in tokensWithTypes:
		thisToken = createXMLNode(tokenType, tokenValue)
		root.append(thisToken)

	return root

def NodeToXML(node):
	# Type and Value
	xmlNode = createXMLNode(node.type, node.value)	

	# Children
	for child in node.children:
		xmlNode.append(NodeToXML(child))
		
	return xmlNode

def XMLToText(XMLTree):
	return ET.tostring(XMLTree).decode("utf-8")

def createXMLNode(type, value):
	XMLNode = ET.Element(type)
	if value:
		XMLNode.text = " {} ".format(value)
	else:
		XMLNode.text = "\n"

	XMLNode.tail = "\n"
	return XMLNode

def parseFile(tokensWithTypes):
	classNode = parseClass(tokensWithTypes)

	if tokensWithTypes:
		raise Exception("Syntax error. Class ended, found {}".format(tokensWithTypes[0]))

	return classNode

def parseClass(tokensWithTypes):
	classNode =	Node("class")

	keyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["class"])
	identifier = takeNode(tokensWithTypes, expectedType="identifier")
	symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["{"])
	classNode.children = [keyword, identifier, symbolOpen]

	for classVarDec in parseClassVarDec(tokensWithTypes):
		classNode.children.append(classVarDec)

	while hasSubroutineDec(tokensWithTypes):
		subroutineDecNode = parseSubroutineDec(tokensWithTypes)
		classNode.children.append(subroutineDecNode)

	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])
	classNode.children.append(symbolClose)

	return classNode
	

def parseClassVarDec(tokensWithTypes):

	#TEMP
	return []

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
	# TEMP : prend tout, pour tester
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

def parseVarDec(tokensWithTypes):
	varDecNode = Node("varDec")

	varKeyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["var"])
	varType = parseType(tokensWithTypes)
	varName = takeNode(tokensWithTypes, expectedType="identifier")
	varDecNode.children.append(varKeyword)
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
	statementNode.children.append(letKeyword)
	statementNode.children.append(expression)

	return statementNode

def parseIfStatement(tokensWithTypes):
	statementNode = Node("ifStatement")
	#TODO
	return statementNode

def parseWhileStatement(tokensWithTypes):
	statementNode = Node("whileStatement")
	
	#TEMP
	while tokensWithTypes[0].value != "}":
		tokensWithTypes.pop(0)

	tokensWithTypes.pop(0)
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
	
	#TEMP
	while tokensWithTypes[0].value != ";":
		tokensWithTypes.pop(0)

	tokensWithTypes.pop(0)
	return statementNode

def parseExpression(tokensWithTypes):
	expressionNode = Node("expression")

	term = parseTerm(tokensWithTypes)
	expression.children.append(term)
	
	while tokensWithTypes.value[0] in OPERATORS:
		operator = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=OPERATORS)
		term = parseTerm(tokensWithTypes)
		expression.children.append(operator)
		expression.children.append(term)

	return expressionNode

def parseSubroutineCall(tokensWithTypes):
	nodeList = []

	#TODO : Cas 2 pdf page 16 (className/varName . subroutineName)

	subroutineName = takeNode(tokensWithTypes, expectedType="identifier")

	symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])
	expressionList = parseExpressionList(tokensWithTypes)
	symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])

	return nodeList

def parseExpressionList(tokensWithTypes):
	#TODO
	return

def parseTerm(tokensWithTypes):
	termNode = Node("term")

	firstNode = tokensWithTypes[0]

	if firstNode.type in ("integerConstant", "stringConstant"):
		constant = Node(firstNode.type, firstNode.value)
		tokensWithTypes.pop(0)
		termNode.children.append(constant)

	elif firstNode.type == "keyword" && firstNode.value in ("true", "false", "null", "this"):
		constant = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["true", "false", "null", "this"])
		termNode.children.append(constant)

	elif firstNode.value == "(":
		symbolOpen = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["("])
		expression = parseExpression(tokensWithTypes)
		symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=[")"])
		termNode.children.append(symbolOpen)
		termNode.children.append(expression)
		termNode.children.append(symbolClose)

	elif firstNode.value == UNARY_OPERATORS:
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

	return Node.fromToken(tokensWithTypes.pop(0))


def getOutputFile(inputFile):
	return re.sub("jack$", "vm", inputFile)

def writeFile(outputText, outputFile):
	if not outputFile:
		print(outputText)

	else:
		with open(outputFile, 'w') as f:
			f.write(outputText)

def main():
	args = readArguments()
	for jackFile in args.jackFiles:
		jackProgram = readJackPrograms(jackFile)

		# Token file generation
		tokenList = tokenize(jackProgram)
		tokensWithTypes = analyseTokenType(tokenList)
		XMLTree = tokenListToXML(tokensWithTypes)
		tokenFile = XMLToText(XMLTree)
		writeFile(tokenFile, jackFile.replace(".jack", "T.xml"))

		syntaxNode = parseFile(tokensWithTypes)
		XMLTree = NodeToXML(syntaxNode)
		syntaxFile = XMLToText(XMLTree)
		writeFile(syntaxFile, jackFile.replace(".jack", ".xml"))

if __name__ == "__main__":
	time1 = time.time()
	main()