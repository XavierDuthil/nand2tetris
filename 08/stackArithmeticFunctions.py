from stackHelpersFunctions import *

SEGMENTS_POINTER = {
	"local": 	"LCL",
	"argument":	"ARG",
	"this":		"THIS",
	"that":		"THAT",
};
SEGMENTS_OFFSET = {
	"temp":		5,
	"static":	16,
	"pointer": 	3,
};

def translatePushCommand(outputProgram, line, vmProgram):
	segmentName = REGEX_SECOND_WORD.match(line).group(1);
	thirdWord = REGEX_THIRD_WORD.match(line).group(1);

	if segmentName == "constant":	# constant = stack segment
		# Read value and put it in D
		outputProgram.append("@{value}".format(value=thirdWord));
		outputProgram.append("D=A");

	elif segmentName == "static":
		addressInSegment = int(thirdWord);
		outputProgram.append("@{fileName}.{offset}".format(fileName=vmProgram.getFileName(),offset=addressInSegment));
		outputProgram.append("D=A");

		# Store the value from the source in D
		outputProgram.append("A=D");
		outputProgram.append("D=M");

	else:
		addressInSegment = int(thirdWord);
		loadAbsoluteAddressIntoD(outputProgram, segmentName, addressInSegment);

		# Store the value from the source in D
		outputProgram.append("A=D");
		outputProgram.append("D=M");

	# Push value on the stack
	outputProgram.append("@SP");
	outputProgram.append("A=M");
	outputProgram.append("M=D");

	outputProgram += incrementStackPointer();


def translatePopCommand(outputProgram, line, vmProgram):
	segmentName = REGEX_SECOND_WORD.match(line).group(1);
	addressInSegment = int(REGEX_THIRD_WORD.match(line).group(1));
	if segmentName == "static":
		outputProgram.append("@{fileName}.{offset}".format(fileName=vmProgram.getFileName(),offset=addressInSegment));
		outputProgram.append("D=A");

	else:
		loadAbsoluteAddressIntoD(outputProgram, segmentName, addressInSegment);

	# Push value of the destination address (place to pop to) on stack
	outputProgram.append("@SP");
	outputProgram.append("A=M");
	outputProgram.append("M=D");

	# Store value to pop in D
	outputProgram += decrementStackPointer();
	outputProgram.append("@SP");
	outputProgram.append("A=M");
	outputProgram.append("D=M");

	# Put the value at the address
	outputProgram += incrementStackPointer();
	outputProgram.append("@SP");
	outputProgram.append("A=M");
	outputProgram.append("A=M");
	outputProgram.append("M=D");	# Place the value at the address of the specified segment
	
	outputProgram += decrementStackPointer();
	outputProgram.append("@2002");


def loadAbsoluteAddressIntoD(outputProgram, segmentName, addressInSegment):
	if segmentName in SEGMENTS_OFFSET :
		address = int(addressInSegment) + SEGMENTS_OFFSET[segmentName];
		outputProgram.append("@{address}".format(address=address));
		outputProgram.append("D=A");

	else:
		segmentPointer = SEGMENTS_POINTER[segmentName];
		# Compute the destination address
		outputProgram.append("@{segmentPointer}".format(segmentPointer=segmentPointer));
		outputProgram.append("D=M");
		outputProgram.append("@{address}".format(address=addressInSegment));
		outputProgram.append("D=D+A");

def translateNegCommand(outputProgram, line, vmProgram):
	# Read value at the previous pointed address and store it in D
	outputProgram += decrementStackPointer();
	outputProgram.append("A=M");
	outputProgram.append("M=-M");
	outputProgram += incrementStackPointer();

def translateNotCommand(outputProgram, line, vmProgram):
	# Read value at the previous pointed address and store it in D
	outputProgram += decrementStackPointer();
	outputProgram.append("A=M");
	outputProgram.append("M=!M");
	outputProgram += incrementStackPointer();

def operation(func):
	def newFunc(outputProgram, line, vmProgram):
		# Read value at the previous pointed address and store it in D
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");
		outputProgram.append("D=M");
		
		# Load value into M
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");

		# Apply the operation
		func(outputProgram, line, vmProgram);

		outputProgram += incrementStackPointer();
	return newFunc;

# Decorate the function (execute code before and after)
@operation
def translateAddCommand(outputProgram, line, vmProgram):
	outputProgram.append("M=M+D");

@operation
def translateSubCommand(outputProgram, line, vmProgram):
	outputProgram.append("M=M-D");

@operation
def translateAndCommand(outputProgram, line, vmProgram):
	outputProgram.append("M=M&D");

@operation
def translateOrCommand(outputProgram, line, vmProgram):
	outputProgram.append("M=M|D");

def comparison(func):
	def newFunc(outputProgram, line, vmProgram):
		uniqueIndex = getUniqueIndex(outputProgram);
		outputProgram += popD();

		# Substract previous value to this one and store result into D
		outputProgram += decrementStackPointer();
		outputProgram.append("A=M");
		outputProgram.append("D=M-D");

		outputProgram.append("@ifTrue{uniqueIndex}".format(uniqueIndex=uniqueIndex));

		# Execute the decorated function
		func(outputProgram, line, vmProgram);

		# Else :
		outputProgram.append("D=0");
		outputProgram.append("@endIf{uniqueIndex}".format(uniqueIndex=uniqueIndex));
		outputProgram.append("0;JMP");

		# If Label :
		outputProgram.append("(ifTrue{uniqueIndex})".format(uniqueIndex=uniqueIndex));
		outputProgram.append("D=-1");

		# EndIf Label
		outputProgram.append("(endIf{uniqueIndex})".format(uniqueIndex=uniqueIndex));
		outputProgram += pushD();

	return newFunc;

@comparison
def translateEqCommand(outputProgram, line, vmProgram):
	outputProgram.append("D;JEQ");

@comparison
def translateLtCommand(outputProgram, line, vmProgram):
	outputProgram.append("D;JLT");

@comparison
def translateGtCommand(outputProgram, line, vmProgram):
	outputProgram.append("D;JGT");