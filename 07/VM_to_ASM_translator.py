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

		if firstWord == "add":
			translateAddCommand(outputProgram, line);

		if firstWord == "eq":
			translateEqCommand(outputProgram, line);

		if firstWord == "lt":
			translateLtCommand(outputProgram, line);

		if firstWord == "gt":
			translateGtCommand(outputProgram, line);

		if firstWord == "sub":
			translateSubCommand(outputProgram, line);
		
		if firstWord == "neg":
			translateNegCommand(outputProgram, line);

		if firstWord == "and":
			translateAndCommand(outputProgram, line);

		if firstWord == "or":
			translateOrCommand(outputProgram, line);


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

	outputProgram += incrementStackPointer();

def translateNegCommand(outputProgram, line):
	# Read value at the previous pointed address and store it in D
	outputProgram += decrementStackPointer();
	outputProgram.append("A=M");
	outputProgram.append("M=-M");
	outputProgram += incrementStackPointer();

def operation(func):
	def newFunc(outputProgram, line):
		# Read value at the previous pointed address and store it in D
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");
		outputProgram.append("D=M");
		
		# Load value into M
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");

		# Apply the operation
		func(outputProgram, line);

		outputProgram += incrementStackPointer();
	return newFunc;

# Decorate the function (execute code before and after)
@operation
def translateAddCommand(outputProgram, line):
	outputProgram.append("M=M+D");

@operation
def translateSubCommand(outputProgram, line):
	outputProgram.append("M=M-D");

@operation
def translateAndCommand(outputProgram, line):
	outputProgram.append("M=M&D");

@operation
def translateOrCommand(outputProgram, line):
	outputProgram.append("M=M|D");
	


def comparison(func):
	def newFunc(outputProgram, line):
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");
		outputProgram.append("D=M");

		# Substract previous value to this one and store result into D
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");
		outputProgram.append("D=M-D");

		outputProgram.append("@{value}".format(value=len(outputProgram) + 5));

		# Execute the decorated function
		func(outputProgram, line);

		# Else :
		outputProgram.append("D=0");
		outputProgram.append("@{value}".format(value=len(outputProgram) + 3));
		outputProgram.append("0;JMP");

		# If :
		outputProgram.append("D=-1");

		outputProgram+=pushD();
	return newFunc;

@comparison
def translateEqCommand(outputProgram, line):
	outputProgram.append("D;JEQ");

@comparison
def translateLtCommand(outputProgram, line):
	outputProgram.append("D;JLT");

@comparison
def translateGtCommand(outputProgram, line):
	outputProgram.append("D;JGT");


def incrementStackPointer():
	return ["@SP", "M=M+1"];

def decrementStackPointer():
	return ["@SP", "M=M-1"];

def pushD():
	return [
		"@SP",
		"A=M",
		"M=D",
	] + incrementStackPointer();

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
