import argparse
import re  # regular expressions
import sys  # stdout
import os
import time

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

def getOutputFile(inputFile):
	return re.sub("jack$", "vm", inputFile)

def writeVMProgram(outputProgram, outputFile):
	if not outputFile:
		sys.stdout.write(outputProgram)

	else:
		with open(outputFile, 'w') as f:
			f.write(outputProgram)

def main():
	args = readArguments()
	for jackFile in args.jackFiles:
		jackProgram = readJackPrograms(jackFile)
		outputProgram = translate(jackProgram)
		outputFile = getOutputFile(jackFile)
		writeVMProgram(outputProgram, outputFile)

if __name__ == "__main__":
	time1 = time.time()
	main()