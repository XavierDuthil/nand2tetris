from stackHelpersFunctions import *


def translateLabelDefinitionCommand(outputProgram, line, vmProgram):
    labelName = REGEX_SECOND_WORD.match(line).group(1)
    outputProgram.append("({labelName})".format(labelName=labelName))


def translateIfGotoCommand(outputProgram, line, vmProgram):
    labelName = REGEX_SECOND_WORD.match(line).group(1)

    outputProgram += popD()
    outputProgram.append("@{labelName}".format(labelName=labelName))
    outputProgram.append("D;JLT")


def translateGotoCommand(outputProgram, line, vmProgram):
    labelName = REGEX_SECOND_WORD.match(line).group(1)
    outputProgram.append("@{labelName}".format(labelName=labelName))
    outputProgram.append("0;JMP")


def translateFunctionDefinitionCommand(outputProgram, line, vmProgram):
    functionName = REGEX_SECOND_WORD.match(line).group(1)
    localVarsCount = int(REGEX_THIRD_WORD.match(line).group(1))
    outputProgram.append("({functionName})".format(functionName=functionName))

    # On avance SP de localVarsCount (en initialisant des 0)
    for _ in range(localVarsCount):
        outputProgram += pushConstant(0)


def translateReturnCommand(outputProgram, line, vmProgram):
    # On stocke ARG+1, qui sera la valeur finale de SP
    outputProgram.append("@ARG")
    outputProgram.append("D=M")
    outputProgram.append("@R13")
    outputProgram.append("M=D")

    # On sauvegarde la valeur de retour de la fonction dans R15
    outputProgram += popInto("R15")

    # SP passe à la valeur de LOCAL
    outputProgram.append("@LCL")
    outputProgram.append("D=M")
    outputProgram.append("@SP")
    outputProgram.append("M=D")

    # On remet les valeurs initiales des segments, qui étaient stockées dans
    # ARG
    outputProgram += popInto("THAT")
    outputProgram += popInto("THIS")
    outputProgram += popInto("ARG")
    outputProgram += popInto("LCL")
    outputProgram += popInto("R14")

    # SP repasse à la valeur de ARG + 1
    outputProgram.append("@R13")
    outputProgram.append("D=M")
    outputProgram.append("@SP")
    outputProgram.append("M=D")

    # On push la valeur de retour
    outputProgram.append("@R15")
    outputProgram.append("D=M")
    outputProgram += pushD()

    # Go to returnAddress
    outputProgram.append("@R14")
    outputProgram.append("A=M")
    outputProgram.append("0;JMP")


def translateCallCommand(outputProgram, line, vmProgram):
    uniqueIndex = vmProgram.getUniqueIndex()
    functionName = REGEX_SECOND_WORD.match(line).group(1)
    # Le nom de la fonction
    nArgs = REGEX_THIRD_WORD.match(line).group(1)
    # Le nombre d'arguments à la fonction (déja dans la stack)

    # On push la ligne du label 'returnAddress'
    outputProgram.append(
        "@functionReturn{uniqueIndex}".format(uniqueIndex=uniqueIndex))
    outputProgram.append("D=A")
    outputProgram += pushD()

    # On ajoute les valeurs à sauvegarder à la stack
    outputProgram += pushPointer("LCL")
    outputProgram += pushPointer("ARG")
    outputProgram += pushPointer("THIS")
    outputProgram += pushPointer("THAT")

    # On définit le nouveau ARG
    outputProgram.append("@{offset}".format(offset=int(nArgs) + 5))
    outputProgram.append("D=A")
    outputProgram.append("@SP")
    outputProgram.append("D=M-D")
    outputProgram.append("@ARG")
    outputProgram.append("M=D")

    # On définit le nouveau LCL, qui prend la valeur de SP
    outputProgram.append("@SP")
    outputProgram.append("D=M")
    outputProgram.append("@LCL")
    outputProgram.append("M=D")

    # Execute la fonction 'functionName'
    outputProgram.append("@{functionName}".format(functionName=functionName))
    outputProgram.append("0;JMP")

    # Label de fin de fonction
    outputProgram.append(
        "(functionReturn{uniqueIndex})".format(uniqueIndex=uniqueIndex))


def bootstrap(vmProgram):
    # Initialisation du stack pointer à 256
    outputProgram = [
        "@256",
        "D=A",
        "@SP",
        "M=D"
    ]

    # Appelle la fonction Sys.init
    callCommand = "call Sys.init 0"
    translateCallCommand(outputProgram, callCommand, vmProgram)

    return outputProgram
