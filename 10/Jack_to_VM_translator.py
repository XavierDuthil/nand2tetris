import argparse
import re  # regular expressions
import sys  # stdout
import os
import time
from string import ascii_letters
from string import digits
from string import whitespace

#REGEX_FIRST_WORD = re.compile('^([^ ]*)')
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
				tokens.append(token)
				token = ""
				continue
			isInString = True
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

def convertToXML(tokens):

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
		tokens = tokenize(jackProgram)
		#tokenFile = convertToXML(tokens)
		writeFile("\n".join(tokens), None)

if __name__ == "__main__":
	time1 = time.time()
	main()