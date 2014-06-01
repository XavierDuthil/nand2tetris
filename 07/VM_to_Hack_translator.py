import argparse
import re  # regular expressions
import sys  # stdout
import time

REGEX_FIRST_WORD = re.compile('^([^ ]*)');
REGEX_SECOND_WORD = re.compile('^[^ ]* ([^ ]*)');
REGEX_PUSH_VALUE = re.compile('^[^ ]* [^ ]* (\d*)');
STACK_POINTER = 0;

def readArguments():
	parser = argparse.ArgumentParser(description='Translate VM code to Hack code.');
	parser.add_argument('vmFile', type=str, help='the file to translate');
	parser.add_argument('-o', '--output', dest='output_file', action='store',
	                   help='the output hack code file');

	return parser.parse_args();

def readVmProgram(vmFile):
	with open(vmFile, 'r') as f:
		lines = f.read().splitlines();

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

		if firstWord == "push":
			translatePushCommand(outputProgram, line);



	return outputProgram;


def translatePushCommand(outputProgram, line):
	secondWord = REGEX_SECOND_WORD.match(line).group(1);

	value = REGEX_PUSH_VALUE.match(line).group(1);

	if secondWord == "constant":
		# Read value and put it in D
		outputProgram.append("@{value}".format(value=value));
		outputProgram.append("D=A");

		# Put value at the adress indicated by the stackPointer
		outputProgram.append("@SP");
		outputProgram.append("A=M");
		outputProgram.append("M=D");

	# Increment the value of stackPointer
	outputProgram.append("@SP");
	outputProgram.append("M=M+1");


def writeHackProgram(outputProgram, output_file):
	outputString = '\n'.join(outputProgram);

	if not output_file:
		sys.stdout.write(outputString);

	else:
		with open(output_file, 'w') as f:
			f.write(outputString);

def main():
	args = readArguments();
	vmProgram = readVmProgram(args.vmFile);
	outputProgram = translate(vmProgram);
	writeHackProgram(outputProgram, args.output_file);

if __name__ == "__main__":
	time1 = time.time();
	main();
# 	print(time.time() - time1);
