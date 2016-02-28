import textwrap
from SymbolTable import SymbolTable
from uuid import uuid4


def XMLToVM(XMLTree):
    vmFile = []
    parseClass(vmFile, XMLTree)
    return "\n".join(vmFile)


def parseClass(vmFile, xmlElement):
    fileClass = xmlElement
    className = fileClass.find('identifier').text

    # TODO : find classVarDec

    for function in fileClass.findall('subroutineDec'):
        parseFunction(vmFile, function, className)


def parseFunction(vmFile, xmlElement, className):
    function = xmlElement
    functionName = function.find('identifier').text

    localVarsCount = countLocalVariablesInFunction(function)
    vmFile.append("function {className}.{functionName} {localVarsCount}".format(
        className=className, functionName=functionName, localVarsCount=localVarsCount))

    # Arguments
    methodSymbolTable = SymbolTable()
    arguments = function.find('parameterList')
    parseFunctionArguments(vmFile, arguments, methodSymbolTable)

    # Body
    functionBody = function.find('subroutineBody')

    # Local vars
    localVarsCount = 0
    varDeclarations = functionBody.findall('varDec')
    for varDeclaration in varDeclarations:
        parseVarDeclaration(vmFile, varDeclaration, methodSymbolTable)

    # Instructions
    statements = functionBody.find('statements')
    parseStatements(vmFile, statements, methodSymbolTable)


def parseFunctionArguments(vmFile, xmlElement, methodSymbolTable):
    arguments = xmlElement

    index = 0
    while index < len(arguments):
        argumentType = arguments[index].text
        argumentName = arguments[index+1].text

        methodSymbolTable.addSymbol(argumentName, argumentType, "argument")
        index += 3


def parseStatements(vmFile, statements, methodSymbolTable):
    for statement in statements:
        parseStatement(vmFile, statement, methodSymbolTable)


def parseStatement(vmFile, statement, methodSymbolTable):
    if statement.tag == 'doStatement':
        parseDoStatement(vmFile, statement, methodSymbolTable)

    elif statement.tag == 'returnStatement':
        parseReturnStatement(vmFile, statement)

    elif statement.tag == 'letStatement':
        parseLetStatement(vmFile, statement, methodSymbolTable)

    elif statement.tag == 'whileStatement':
        parseWhileStatement(vmFile, statement, methodSymbolTable)

    elif statement.tag == 'ifStatement':
        parseIfStatement(vmFile, statement, methodSymbolTable)


def parseReturnStatement(vmFile, xmlElement):
    vmFile.append('return\n')


def parseDoStatement(vmFile, xmlElement, methodSymbolTable):
    parseSubroutineCall(vmFile, xmlElement, methodSymbolTable)


def parseSubroutineCall(vmFile, xmlElement, methodSymbolTable):
    functionName = xmlElement.findall('identifier')[-1].text

    if xmlElement.find('symbol').text == '.':
        className = xmlElement.find('identifier').text
        functionName = "{}.{}".format(className, functionName)

    expressions = xmlElement.find('expressionList').findall('expression')
    argsCount = len(expressions)

    # Arguments
    for expression in expressions:
        parseExpression(vmFile, expression, methodSymbolTable)

    vmFile.append('call {functionName} {argsCount}'.format(
        functionName=functionName, argsCount=argsCount))


def parseExpression(vmFile, xmlElement, methodSymbolTable):
    if len(xmlElement) == 1:
        term = xmlElement[0]
        parseTerm(vmFile, term, methodSymbolTable)

    # Unary operator
    elif len(xmlElement) == 2:
        operator = xmlElement[0].text
        term = xmlElement[1]

        if operator == '~':
            parseTerm(vmFile, term, methodSymbolTable)
            vmFile.append('not')

        elif operator == '-':
            vmFile.append('push constant 0')
            parseTerm(vmFile, term, methodSymbolTable)
            vmFile.append('sub')

    elif len(xmlElement) > 2:
        term1 = xmlElement[0]
        parseTerm(vmFile, term1, methodSymbolTable)

        operator = xmlElement[1].text

        term2 = xmlElement[2]
        parseTerm(vmFile, term2, methodSymbolTable)

        if operator == '+':
            vmFile.append('add')
        elif operator == '-':
            vmFile.append('sub')
        elif operator == '*':
            instructions = textwrap.dedent('''\
                // We already have the 2 operands in the stack, we store them in temp0 and temp1
                pop temp 0
                pop temp 1

                // Result initialisation
                push constant 0

                // Loop
                label MULTIPLICATION_LOOP{uuid}

                    // Counter decrement
                    push temp 1
                    push constant 1
                    sub
                    pop temp 1

                    // Verify loop condition: until counter < 0
                    push temp 1
                    push constant 0
                    lt
                    if-goto MULTIPLICATION_END{uuid}

                    // Add first term value
                    push temp 0
                    add

                    goto MULTIPLICATION_LOOP{uuid}

                label MULTIPLICATION_END{uuid}''').format(uuid=uuid4())
            vmFile.extend(instructions.split("\n"))

        elif operator == '>':
            vmFile.append('gt')

        elif operator == '<':
            vmFile.append('lt')


def parseTerm(vmFile, xmlElement, methodSymbolTable):
    # Case: single value
    if len(xmlElement) == 1:
        value = xmlElement[0].text

        # Case: integer
        if xmlElement[0].tag == 'integerConstant':
            vmFile.append('push constant {}'.format(value))

        # Case: boolean value 'true'
        if xmlElement[0].tag == 'keyword' and xmlElement[0].text == 'true':
            vmFile.append('push constant 1')

        # Case: boolean value 'false'
        if xmlElement[0].tag == 'keyword' and xmlElement[0].text == 'false':
            vmFile.append('push constant 0')

        # Case: variable
        elif xmlElement[0].tag == 'identifier':
            symbol = methodSymbolTable.getSymbolByName(xmlElement[0].text)
            vmFile.append('push {symbol.segment} {symbol.offset}'.format(symbol=symbol))

        """ TODO
        elif xmlElement.tag == 'stringConstant':
        elif xmlElement.tag == 'keywordConstant':

        etc..."""

    # Case: Negative single value
    elif xmlElement[0].tag == 'symbol' and xmlElement[0].text == '-' and len(xmlElement) == 2:
        vmFile.append('push constant 0')

        term = xmlElement[1]
        parseTerm(vmFile, term, methodSymbolTable)

        vmFile.append('sub')

    # Case: parenthesis around a expression
    elif len(xmlElement) == 3:
        if xmlElement[0].text == '(' and xmlElement[2].text == ')':
            parseExpression(vmFile, xmlElement[1], methodSymbolTable)

    # Case: subroutine call
    elif (xmlElement[0].tag == "identifier" and xmlElement[1].text == "(" or
            xmlElement[0].tag == "identifier" and xmlElement[1].text == "."):
        parseSubroutineCall(vmFile, xmlElement, methodSymbolTable)


def parseVarDeclaration(vmFile, xmlElement, methodSymbolTable):
    varType = xmlElement[1].text

    for varNameNode in xmlElement.findall("identifier"):
        varName = varNameNode.text
        if varName == varType:
            continue

        newSymbol = methodSymbolTable.addSymbol(varName, varType, "local")
        initializeVariable(vmFile, newSymbol)


def parseLetStatement(vmFile, xmlElement, methodSymbolTable):
    symbolName = xmlElement[1].text
    # Brackets...

    expression = xmlElement.findall("expression")[-1]  # Last occurence
    parseExpression(vmFile, expression, methodSymbolTable)

    symbol = methodSymbolTable.getSymbolByName(symbolName)
    vmFile.append('pop {symbol.segment} {symbol.offset}'.format(symbol=symbol))


def parseIfStatement(vmFile, xmlElement, methodSymbolTable):
    # Generate uuid for the end label
    uuid = uuid4()

    # Parse the condition
    condition = xmlElement.find('expression')
    falseLabel = 'IF_FALSE{uuid}'.format(uuid=uuid)
    parseCondition(vmFile, condition, methodSymbolTable, falseLabel)

    # IF_TRUE body statements
    ifTrueStatements = xmlElement.findall('statements')[0]
    parseStatements(vmFile, ifTrueStatements, methodSymbolTable)

    # End of IF_TRUE
    vmFile.append('goto IF_END{uuid}'.format(uuid=uuid))

    # Beginning of IF_FALSE
    vmFile.append('label IF_FALSE{uuid}'.format(uuid=uuid))

    # IF_FALSE body statements
    if len(xmlElement.findall('statements')) > 1:
        ifFalseStatements = xmlElement.findall('statements')[1]
        parseStatements(vmFile, ifFalseStatements, methodSymbolTable)

    # End of if
    vmFile.append('label IF_END{uuid}'.format(uuid=uuid))


def parseWhileStatement(vmFile, xmlElement, methodSymbolTable):
    # Generate uuid for this loop
    uuid = uuid4()

    # Label for the beginning of loop
    instructions = textwrap.dedent('''\

    // While loop
    label WHILE_LOOP{uuid}''').format(uuid=uuid)
    vmFile.extend(instructions.split("\n"))

    # Parse the condition
    condition = xmlElement.find('expression')
    falseLabel = 'WHILE_END{uuid}'.format(uuid=uuid)
    parseCondition(vmFile, condition, methodSymbolTable, falseLabel)

    # Loop body statements
    statements = xmlElement.find('statements')
    parseStatements(vmFile, statements, methodSymbolTable)

    # End of loop body
    instructions = textwrap.dedent('''\

    goto WHILE_LOOP{uuid}
    label WHILE_END{uuid}''').format(uuid=uuid)
    vmFile.extend(instructions.split("\n"))


def parseCondition(vmFile, condition, methodSymbolTable, falseLabel):
    # Push condition result on stack
    parseExpression(vmFile, condition, methodSymbolTable)

    # Condition check
    instructions = textwrap.dedent('''\

    // Test if condition result is 'false'
    push constant 0
    eq
    if-goto {falseLabel}\n''').format(falseLabel=falseLabel)
    vmFile.extend(instructions.split("\n"))


def countLocalVariablesInFunction(functionElement):
    localVarsCount = 0

    for varDec in functionElement.find("subroutineBody").findall("varDec"):
        # Count the commas in the VarDec block, and add 1 to obtain vars count
        values = [element.text for element in varDec]
        localVarsCount += values.count(",") + 1

    return localVarsCount


def initializeVariable(vmFile, symbol):
    vmFile.append('push constant 0')
    vmFile.append('pop {symbol.segment} {symbol.offset}'.format(symbol=symbol))
