import argparse
import re  # regular expressions
import sys  # stdout
import os
import time
from string import ascii_letters
from string import digits
from string import whitespace

#REGEX_FIRST_WORD = re.compile('^([^ ]*)')
REGEX_TOKEN_TYPE_IDENTIFIER = re.compile('[a-zA-Z_]\w*')
#COMMANDS = {}

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
			token = token[1:-2]
			tokenType = "stringConstant"

		elif REGEX_TOKEN_TYPE_IDENTIFIER.match(token):
			tokenType = "identifier"

		else:
			raise Exception("Error : invalid token {}".format(token))

		tokensWithTypes.append((token, tokenType))
	return tokensWithTypes

def convertToXML(tokensWithTypes):
	

	return tokenFile

def getOutputFile(inputFile):
	return re.sub("jack$", "vm", inputFile)

def writeFile(outputText, outputFile):
	if not outputFile:
		sys.stdout.write(outputText)

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
		#tokenFile = convertToXML(tokenList)
		writeFile("\n".join(tokenList), None)

if __name__ == "__main__":
	time1 = time.time()
	main()