from stackHelpersFunctions import *

def translateLabelDefinitionCommand(outputProgram, line):
	labelName = REGEX_SECOND_WORD.match(line).group(1);
	outputProgram.append("({labelName})".format(labelName=labelName));


def translateIfGotoCommand(outputProgram, line):
	labelName = REGEX_SECOND_WORD.match(line).group(1);

	outputProgram += popD();
	outputProgram.append("@{labelName}".format(labelName=labelName));
	outputProgram.append("D;JGT");

def translateGotoCommand(outputProgram, line):
	labelName = REGEX_SECOND_WORD.match(line).group(1);
	outputProgram.append("@{labelName}".format(labelName=labelName));
	outputProgram.append("0;JMP");
