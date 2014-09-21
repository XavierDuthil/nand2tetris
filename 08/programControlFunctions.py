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

	# SP repasse à la valeur de ARG + 1
	outputProgram.append("@R13");
	outputProgram.append("D=M");
	outputProgram.append("@SP");
	outputProgram.append("M=D");


def translateCallCommand(outputProgram, line):
	# C'est un début de réflexion, on l'avait mis sur definition de fonction, en fait c'est sur l'appel
	# La valeur de Argument prend la valeur de l'état initial de SP avant la définition de la fonction
	outputProgram.append("@SP");
	outputProgram.append("D=M");
	outputProgram.append("@ARG");
	outputProgram.append("M=D");

	# La valeur de Local ne bouge pas, mais comme on connait la longueur de ce segment, SP obtiendra la valeur suivant ce segment
	outputProgram.append("@LCL");
	outputProgram.append("D=M");
	outputProgram.append("@{localArgsCount}".format(localArgsCount=localArgsCount));
	outputProgram.append("D=D+A");
	outputProgram.append("@SP");
	outputProgram.append("M=D");
