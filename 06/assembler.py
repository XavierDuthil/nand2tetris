import argparse
import re  # regular expressions
import sys  # stdout

def readArguments():
	parser = argparse.ArgumentParser(description='Assemble a hack program.');
	parser.add_argument('asm_file', type=str, help='the file to assemble');
	parser.add_argument('-o', '--output', dest='output_file', action='store',
	                   help='the output binary file');

	return parser.parse_args();

def readAsmProgram(asm_file):
	with open(asm_file, 'r') as f:
		lines = f.read().splitlines();

	asm_program = [];
	for line in lines:
		if not line.startswith("//") and len(line):
			newLine = line;

			if "//" in line:
				newLine = re.sub('//.*', '', line);

			# asm_program contains the exploitable data, white spaces are stripped.
			asm_program.append(newLine.strip());

	return asm_program;

def replacePredefinedLabels(asm_program):
	replaceLabel("SP", 0, asm_program);
	replaceLabel("LCL", 1, asm_program); 
	replaceLabel("ARG", 2, asm_program); 
	replaceLabel("THIS", 3, asm_program);
	replaceLabel("THAT", 4, asm_program);
	replaceLabel("SCREEN", 16384, asm_program);
	replaceLabel("KBD", 24576, asm_program);

	for i in range(0, 16):
		replaceLabel("R%s" % i, i, asm_program);

def searchLabels():
	labelsList = {};

	for (index, line) in enumerate(asm_program):
		labelName = extractLabelDefinition(line);
		if labelName is not None:
			labelsList[labelName] = index - len(labelsList);

	print("Labels searched.")

	return labelsList;

def replaceLabels(asm_program):
	labelsList = searchLabels();
	asm_program2 = [];

	for line in asm_program:
		if not isLabelDefinition(line):
			asm_program2.append(replaceOnlyAInstruction(labelsList, line));

	return asm_program2;

# Renvoie une instruction A avec label remplacé (ou bien la ligne originale)
def replaceOnlyAInstruction(labelsList, line):
	labelName = extractLabelName(line);

	if labelName is not None and labelName in labelsList:
		line = "@" + str(labelsList[labelName]);

	return line;

# renvoie true si la ligne est une définition de label
def isLabelDefinition(line):
	regExResult = re.match('\([\w.$]+\)', line);
	return regExResult is not None;

def replaceLabel(labelName, memoryAddress, asm_program):
	if memoryAddress > 33000:
		raise Exception("%s %s" % (labelName, memoryAddress));

	for (index, line) in enumerate(asm_program):
		asm_program[index] = re.sub('^@' + re.escape(labelName) +'$', '@%s' % memoryAddress, line);

	print("replaced : @%s by @%s" % (labelName, memoryAddress));

def replaceVariables(asm_program):
	variables = {};
	memoryAddress = 16;

	for line in asm_program:
		variableName = extractLabelName(line);

		if variableName is not None and variableName not in variables:
			variables[variableName] = memoryAddress;
			memoryAddress += 1;

	for variableName, memoryAddress in variables.items():
		replaceLabel(variableName, memoryAddress, asm_program);

def extractLabelName(line):
	regExResult = re.match('^@([^\d].*)', line);
	if regExResult:
		return regExResult.group(1);

	return None;

def extractLabelDefinition(line):
	regExResult = re.match('\(([\w.$]+)\)', line);
	if regExResult:
		return regExResult.group(1);

	return None;

def assembleProgram(asm_program):
	hackProgram = [];

	for line in asm_program:

		regExResult1 = re.match('^@(\d+)', line);

		# case: a-instruction
		if regExResult1:
			address = regExResult1.group(1);  # stock the address in address
			address = int(address);  # convert into int
			binaryInstruction = '0{:015b}'.format(address);  # format the 16-character instruction
			hackProgram.append(binaryInstruction);  # adds the instruction to the output list

		regExResult2 = re.match('^(\w+)=([01ADM&!|+-]+)', line);
		regExResult3 = re.match('^(.);(\w+)', line);


		# case: c-instruction
		if regExResult2:
			extractedDest = regExResult2.group(1);
			extractedComp = regExResult2.group(2);

			# dest identification
			dest = list("000");
			if 'A' in extractedDest:
				dest[0] = '1';

			if 'D' in extractedDest:
				dest[1] = '1';

			if 'M' in extractedDest:
				dest[2] = '1';
			dest = "".join(dest);

			# comp
			comp = assembleComp(extractedComp);

			# jump identification
			jump = "000";

			binaryInstruction = assembleCInstruction(comp, dest, jump);

			hackProgram.append(binaryInstruction);

		#case: JUMP instruction
		if regExResult3:
			extractedComp = regExResult3.group(1);
			extractedJump = regExResult3.group(2);

			# comp
			comp = assembleComp(extractedComp);

			# dest
			dest = "000";

			#jump identification
			if extractedJump == "JGT":
				jump = "001";
			elif extractedJump == "JEQ":
				jump = "010";
			elif extractedJump == "JGE":
				jump = "011";
			elif extractedJump == "JLT":
				jump = "100";
			elif extractedJump == "JNE":
				jump = "101";
			elif extractedJump == "JLE":
				jump = "110";
			elif extractedJump == "JMP":
				jump = "111";
			else:
				raise Exception("Jump \"%s\" non reconnu" % extractedJump)

			binaryInstruction = assembleCInstruction(comp, dest, jump);

			hackProgram.append(binaryInstruction);

		if regExResult1 is None and regExResult2 is None and regExResult3 is None: 
			hackProgram.append(line);
			raise Exception("Could not assemble the instruction \"%s\"" % line);

		if len(hackProgram[-1]) > 16:
			raise Exception(line);

	return hackProgram;


def writeHackProgram(hack_program, output_file):
	hack_program = '\n'.join(hack_program);

	if not output_file:
		sys.stdout.write(hack_program);

	else:
		with open(output_file, 'w') as f:
			f.write(hack_program);

def assembleComp(extractedComp):
	# comp identification
	if 'M' in extractedComp:
		a = "1";
	else:
		a = "0";

	# Replaces A or M by an X in extractedComp (same output instruction)
	extractedComp = extractedComp.replace("A", "X");
	extractedComp = extractedComp.replace("M", "X");

	# All the cases
	if extractedComp == "0":
		c = "101010";
	elif extractedComp == "1":
		c = "111111";
	elif extractedComp == "-1":
		c = "111010";
	elif extractedComp == "D":
		c = "001100";
	elif extractedComp == "X":
		c = "110000";
	elif extractedComp == "!D":
		c = "001101";
	elif extractedComp == "!X":
		c = "110001";
	elif extractedComp == "-D":
		c = "001111";
	elif extractedComp == "-X":
		c = "110011";
	elif extractedComp == "D+1":
		c = "011111";
	elif extractedComp == "X+1":
		c = "110111";
	elif extractedComp == "D-1":
		c = "001110";
	elif extractedComp == "X-1":
		c = "110010";
	elif extractedComp == "D+X":
		c = "000010";
	elif extractedComp == "D-X":
		c = "010011";
	elif extractedComp == "X-D":
		c = "000111";
	elif extractedComp == "D&X":
		c = "000000";
	elif extractedComp == "D|X":
		c = "010101";
	elif extractedComp == "X":
		c = "110000";
	elif extractedComp == "D":
		c = "001100";
	else:
		raise Exception("Comp \"%s\" non reconnu" % extractedComp)

	assembledComp = "{:s}{:s}".format(a,c);

	return assembledComp;

def assembleCInstruction(comp, dest, jump):
	return "111{:s}{:s}{:s}".format(comp, dest, jump);

if __name__ == "__main__":
	args = readArguments();
	asm_program = readAsmProgram(args.asm_file);
	replacePredefinedLabels(asm_program);
	asm_program = replaceLabels(asm_program);
	replaceVariables(asm_program);
	try:
		hack_program = assembleProgram(asm_program);
	except Exception as e:
		print(e);
	writeHackProgram(hack_program, args.output_file);