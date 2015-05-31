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

#REGEX_FIRST_WORD = re.compile('^([^ ]*)')
REGEX_TOKEN_TYPE_IDENTIFIER = re.compile('[a-zA-Z_]\w*')
#COMMANDS = {}
Token = namedtuple("Token", ["type", "value"])


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

	# A décommenter après avoir géré les keywords intermédiaires
	#symbolClose = takeNode(tokensWithTypes, expectedType="symbol", possibleValues=["}"])
	#classNode.children.append(symbolClose)

	return classNode
	

def parseClassVarDec(tokensWithTypes):
	return 

def hasSubroutineDec(tokensWithTypes):
	firstValues = ["constructor", "function", "method"]
	return tokensWithTypes[0].value in firstValues:

def parseSubroutineDec(tokensWithTypes):
	possibleValues = ["constructor", "function", "method"]
	subroutineDecNode = new Node("subroutineDec")
	
	keyword = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=possibleValues)

	try:
		returnType = takeNode(tokensWithTypes, expectedType="keyword", possibleValues=["void", "int", "char", "boolean"])
	except JackSyntaxError:
		returnType = takeNode(tokensWithTypes, expectedType="identifier")

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

# TODO
def parseParameterList(tokensWithTypes):
	return 

def parseSubroutineBody(tokensWithTypes):
	return

def parseStatement():
	return

def parseWhileStatement():
	return

def parseIfStatement():
	return

def parseStatementSequence():
	return

def parseExpression():
	return

# Pop the first token from the list, verify condition and return as Node
def takeNode(tokensWithTypes, expectedType, possibleValues=None):
	currentToken = tokensWithTypes[0]

	if currentToken.type != expectedType:
		raise JackSyntaxError("Syntax error. Expected type {0}, found type {1}".format(expectedType, currentToken.type))

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