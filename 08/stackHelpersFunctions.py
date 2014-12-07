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

def pushPointer(value):
	commands = [
		"@{value}".format(value=value),
		"D=M",
	];
	return commands + pushD();

class VmProgram(object):
	positionIndex = -1;
	programInstructions = [];
	uniqueIndex = 0;
	filePosition = {};

	def getNextLine(self):
		self.positionIndex += 1;
		return self.programInstructions[self.positionIndex];

	def getFileName(self):
		previousMarkers = [key for key in self.filePosition.keys() if key <= self.positionIndex];
		currentMarker = max(previousMarkers);
		fileName = self.filePosition[currentMarker];
		return fileName;

	def addFile(self, fileName, fileContent):
		self.filePosition[len(self.programInstructions)] = fileName;
		self.programInstructions += fileContent;

	def hasNext(self):
		return self.positionIndex < len(self.programInstructions)-1;

	def getUniqueIndex(self):
		self.uniqueIndex += 1;
		return self.uniqueIndex;
