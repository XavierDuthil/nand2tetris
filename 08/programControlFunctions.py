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

def translateFunctionDefinitionCommand(outputProgram, line):
	functionName = REGEX_SECOND_WORD.match(line).group(1);
	localVarsCount = int(REGEX_THIRD_WORD.match(line).group(1));
	outputProgram.append("({functionName})".format(functionName=functionName));

	# On avance SP de localVarsCount (en initialisant des 0)
	for _ in range(localVarsCount):
		outputProgram += pushConstant(0);

def translateReturnCommand(outputProgram, line):
	# On stocke ARG+1, qui sera la valeur finale de SP
	outputProgram.append("@ARG");
	outputProgram.append("D=M+1");
	outputProgram.append("@R13");
	outputProgram.append("M=D");

	# On retourne la valeur de la stack en l'empilant sur la stack précédente
	outputProgram += popD();
	outputProgram.append("@ARG");
	outputProgram.append("A=M");
	outputProgram.append("M=D");

	# SP passe à la valeur de LOCAL
	outputProgram.append("@LCL");
	outputProgram.append("D=M");
	outputProgram.append("@SP");
	outputProgram.append("M=D");

	# On remet les valeurs initiales des segments, qui étaient stockées dans ARG
	outputProgram += popInto("THAT");
	outputProgram += popInto("THIS");
	outputProgram += popInto("ARG");
	outputProgram += popInto("LCL");
	outputProgram += popInto("R14");

	# SP repasse à la valeur de ARG + 1
	outputProgram.append("@R13");
	outputProgram.append("D=M");
	outputProgram.append("@SP");
	outputProgram.append("M=D");

	# Go to returnAddress
	outputProgram.append("@R14");
	outputProgram.append("A=M");
	outputProgram.append("0;JMP");


def translateCallCommand(outputProgram, line):
	uniqueIndex = getUniqueIndex(outputProgram);
	functionName = REGEX_SECOND_WORD.match(line).group(1);	# Le nom de la fonction
	nArgs = REGEX_THIRD_WORD.match(line).group(1); 			# Le nombre d'arguments à la fonction (déja dans la stack)

	# On push la ligne du label 'returnAddress'
	outputProgram.append("@functionReturn{uniqueIndex}".format(uniqueIndex=uniqueIndex));
	outputProgram.append("D=A");
	outputProgram += pushD();

	# On ajoute les valeurs à sauvegarder à la stack
	outputProgram += pushConstant("LCL");
	outputProgram += pushConstant("ARG");
	outputProgram += pushConstant("THIS");
	outputProgram += pushConstant("THAT");

	# On définit le nouveau ARG
	outputProgram.append("@{offset}".format(offset=int(nArgs)+5));
	outputProgram.append("D=A");
	outputProgram.append("@SP");
	outputProgram.append("D=M-D");

	# On définit le nouveau LCL, qui prend la valeur de SP
	outputProgram.append("@SP");
	outputProgram.append("D=M");
	outputProgram.append("@LCL");
	outputProgram.append("M=D");

	# Execute la fonction 'functionName'
	outputProgram.append("@{functionName}".format(functionName=functionName));
	outputProgram.append("0;JMP");

	# Label de fin de fonction
	outputProgram.append("(functionReturn{uniqueIndex})".format(uniqueIndex=uniqueIndex));

def bootstrap():
	# Initialisation du stack pointer à 256
	outputProgram = ListWithAttribute([
		"@256", 
		"D=A", 
		"@SP",
		"M=D"
	]);
	outputProgram.uniqueIndex = 0;

	# Appelle la fonction Sys.init
	callCommand = "call Sys.init 0";
	translateCallCommand(outputProgram, callCommand);

	return outputProgram;