import argparse
import re  # regular expressions module

def readArguments():
	parser = argparse.ArgumentParser(description='Assemble a hack program.');
	parser.add_argument('asm_file', type=str, help='the file to assemble');
	parser.add_argument('-o', '--output', dest='hack_file', action='store',
	                   help='the output binary file');

	return parser.parse_args();

def readAsmProgram(asm_file):
	with open(asm_file, 'r') as f:
		lines = f.read().splitlines();

	asm_program = [];
	for line in lines:
		if not line.startswith("//") and len(line):
			# asm_program contains the exploitable data
			asm_program.append(line);

	return asm_program;

def assembleProgram(asm_program):
	hackProgram = [];

	for line in asm_program:

		regExResult1 = re.match('^@(\d+)$', line);

		# case: a-instruction
		if regExResult1:
			address = regExResult1.group(1);  # stock the address in address
			address = int(address);  # convert into int
			binaryInstruction = '0{:015b}'.format(address);  # format the 16-character instruction
			hackProgram.append(binaryInstruction);  # adds the instruction to the output list

		regExResult2 = re.match('^(\w)=(\w)$', line);

		# case: c-instruction
		if regExResult2:
			extractedDest = regExResult2.group(1);
			extractedComp = regExResult2.group(2);

			# dest identification
			if extractedDest == 'A':
				dest = "100";

			elif extractedDest == 'D':
				dest = "010";

			elif extractedDest == 'M':
				dest = "010";

			# comp identification
			if 'M' in extractedComp:
				a = "1";
			else:
				a = "0";

			if extractedComp == "A":
				c = "110000";
			elif extractedComp == "D":
				c = "001100";

			comp = "{:s}{:s}".format(a,c);

			# jump identification
			jump = "000";

			binaryInstruction = "111{:s}{:s}{:s}".format(comp, dest, jump);

			hackProgram.append(binaryInstruction);

		if regExResult1 is None and regExResult2 is None: 
			hackProgram.append(line);

	return hackProgram;


def writeHackProgram(hack_program):
	print('\n'.join(hack_program));


if __name__ == "__main__":
	args = readArguments();
	asm_program = readAsmProgram(args.asm_file);
	hack_program = assembleProgram(asm_program);
	writeHackProgram(hack_program);