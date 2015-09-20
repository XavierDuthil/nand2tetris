import re  # regular expressions
import time
import argparse
from tokenizer import tokenize, analyseTokenType
from xml_writer import tokenListToXML, XMLToText, NodeToXML
from compiler import XMLToVM
from parser import parseFile

#REGEX_FIRST_WORD = re.compile('^([^ ]*)')


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
		#tokenFile = XMLToText(XMLTree)
		#writeFile(tokenFile, jackFile.replace(".jack", "T.xml"))

		syntaxNode = parseFile(tokensWithTypes)
		XMLTree = NodeToXML(syntaxNode)
		syntaxFile = XMLToText(XMLTree)
		writeFile(syntaxFile, jackFile.replace(".jack", ".xml"))

		vmFile = XMLToVM(XMLTree)
		writeFile(vmFile, jackFile.replace(".jack", ".vm"))

if __name__ == "__main__":
	time1 = time.time()
	main()
