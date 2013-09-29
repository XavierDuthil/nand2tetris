import argparse
import re  # regular expressions module

parser = argparse.ArgumentParser(description='Assemble a hack program.')
parser.add_argument('asm_file', type=str, help='the file to assemble')
parser.add_argument('-o', '--output', dest='hack_file', action='store',
                   help='the output binary file')

args = parser.parse_args()

with open(args.asm_file, 'r') as f:
	lines = f.read().splitlines()

# print('\n'.join(lines) +'\n\n')

asm_program = []
for line in lines:
	if not line.startswith("//") and len(line):
		# asm_program contains the exploitable data
		asm_program.append(line)
		
# print('\n'.join(asm_program));

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
			c = "110000"
		elif extractedComp == "D":
			c = "001100"

		comp = "{:s}{:s}".format(a,c);

		# jump identification
		jump = "000";

		binaryInstruction = "111{:s}{:s}{:s}".format(comp, dest, jump);

		hackProgram.append(binaryInstruction);

	if regExResult1 is None and regExResult2 is None: 
		hackProgram.append(line);

print('\n'.join(hackProgram));
		

