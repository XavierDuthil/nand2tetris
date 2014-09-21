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
		"A=M",
		"D=M",
	];
	return decrementStackPointer() + commands;
