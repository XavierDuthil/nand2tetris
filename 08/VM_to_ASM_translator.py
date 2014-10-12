import argparse
import re  # regular expressions
import sys  # stdout
import time
from stackArithmeticFunctions import *
from programControlFunctions import *

REGEX_FIRST_WORD = re.compile('^([^ ]*)');
COMMANDS = {
	"push": 	translatePushCommand,
	"pop": 		translatePopCommand,
	"add": 		translateAddCommand,
	"eq": 		translateEqCommand,
	"lt": 		translateLtCommand,
	"gt": 		translateGtCommand,
	"sub": 		translateSubCommand,
	"neg": 		translateNegCommand,
	"and": 		translateAndCommand,
	"or": 		translateOrCommand,
	"not":		translateNotCommand,
	"label":	translateLabelDefinitionCommand,
	"if-goto":	translateIfGotoCommand,
	"goto":		translateGotoCommand,
	"function":	translateFunctionDefinitionCommand,
	"return":	translateReturnCommand,
	"call":		translateCallCommand,
}

def readArguments():
	parser = argparse.ArgumentParser(description='Translate VM code to Hack code.');
	parser.add_argument('vmFiles', type=str, nargs='+', help='the files to translate');
	parser.add_argument('-o', '--output', dest='output_file', action='store',
	                   help='the output hack code file');

	return parser.parse_args();

def readVmPrograms(vmFiles):
	lines = [];
	for vmFile in vmFiles:
		with open(vmFile, 'r') as f:
			lines += f.read().splitlines();

	vmProgram = [];
	for line in lines:
		if not line.startswith("//") and len(line):
			newLine = line;

			if "//" in line:
				newLine = re.sub('//.*', '', line);

			# vmProgram contains the exploitable data, white spaces are stripped.
			vmProgram.append(newLine.strip());

	return vmProgram;


def translate(vmProgram):
	outputProgram = [];

	outputProgram = [];

	for line in vmProgram:
		firstWord = REGEX_FIRST_WORD.match(line).group(1);

		if firstWord in COMMANDS:
			COMMANDS[firstWord](outputProgram, line);

		else:
			print("Line ignored : {line}".format(line=line));


	return outputProgram;

def writeHackProgram(outputProgram, output_file):
	outputString = '\n'.join(outputProgram);

	if not output_file:
		sys.stdout.write(outputString);

	else:
		with open(output_file, 'w') as f:
			f.write(outputString);

def main():
	args = readArguments();
	vmProgram = readVmPrograms(args.vmFiles);
	outputProgram = translate(vmProgram);
	writeHackProgram(outputProgram, args.output_file);

if __name__ == "__main__":
	time1 = time.time();
	main();
# 	print(time.time() - time1);
