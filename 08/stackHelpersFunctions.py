import re;

REGEX_SECOND_WORD = re.compile('^[^ ]* ([^ ]*)');
REGEX_THIRD_WORD = re.compile('^[^ ]* [^ ]* ([^ ]*)');

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

def popD():
	commands = [
		"@SP",
		"A=M",
		"D=M",
	];
	return decrementStackPointer() + commands;

def popInto(destinationAddress):
	commands = [
		"@{destinationAddress}".format(destinationAddress=destinationAddress),
		"M=D",
	];
	return popD() + commands;

def pushConstant(value):
	commands = [
		"@{value}".format(value=value),
		"D=A",
	];
	return commands + pushD();

def getUniqueIndex(outputProgram):
	outputProgram.uniqueIndex += 1;
	return outputProgram.uniqueIndex;

class ListWithAttribute(list):
	uniqueIndex = 0;