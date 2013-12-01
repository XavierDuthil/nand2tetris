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
			# asm_program contains the exploitable data, white spaces are stripped.
			asm_program.append(line.strip());

	return asm_program;

def replaceLabels(asm_program):
	labelFound = False;
	lineNumber = 0;

	for (index, line) in enumerate(asm_program):
		labelMatch = re.match('^\((\w+)\)', line);

		if labelMatch:
			labelName = labelMatch.group(1);
			lineNumber = index;
			replaceLabel(labelName, lineNumber, asm_program);

			labelFound = True;
			break;

	if labelFound:
		asm_program.pop(lineNumber);
		return replaceLabels(asm_program);

	return asm_program;


def replaceLabel(labelName, lineNumber, asm_program):
	for (index, line) in enumerate(asm_program):
		asm_program[index] = re.sub('^@' + labelName, '@%s' % lineNumber, line);

	print("replaced : @%s by @%s" % (labelName, lineNumber));


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
	asm_program = replaceLabels(asm_program);
	hack_program = assembleProgram(asm_program);
	writeHackProgram(hack_program, args.output_file);