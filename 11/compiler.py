import textwrap
from SymbolTable import SymbolTable


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
    # Parameters...

    functionBody = function.find('subroutineBody')

    # Local vars
    methodSymbolTable = SymbolTable()
    localVarsCount = 0
    varDeclarations = functionBody.findall('varDec')
    for varDeclaration in varDeclarations:
        parseVarDeclaration(vmFile, varDeclaration, methodSymbolTable)

    localVarsCount = methodSymbolTable.countSymbols("local")
    vmFile.append("function {className}.{functionName} {localVarsCount}".format(
        className=className, functionName=functionName, localVarsCount=localVarsCount))

    # Instructions
    statements = functionBody.find('statements')
    for statement in statements:
        parseStatement(vmFile, statement, methodSymbolTable)


def parseStatement(vmFile, statement, methodSymbolTable):
    if statement.tag == 'doStatement':
        parseDoStatement(vmFile, statement, methodSymbolTable)

    elif statement.tag == 'returnStatement':
        parseReturnStatement(vmFile, statement)

    elif statement.tag == 'letStatement':
        parseLetStatement(vmFile, statement, methodSymbolTable)


def parseReturnStatement(vmFile, xmlElement):
    vmFile.append('return')


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
    term1 = xmlElement[0]
    parseTerm(vmFile, term1, methodSymbolTable)

    if len(xmlElement) > 1:
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
                label MULTIPLICATION_LOOP

                    // Counter decrement
                    push temp 1
                    push constant 1
                    sub
                    pop temp 1

                    // Verify loop condition: until counter < 0
                    push temp 1
                    push constant 0
                    lt
                    if-goto MULTIPLICATION_END

                    // Add first term value
                    push temp 0
                    add

                    goto MULTIPLICATION_LOOP

                label MULTIPLICATION_END''').format(term1=term1.text, term2=term2.text)
            vmFile.extend(instructions.split("\n"))


def parseTerm(vmFile, xmlElement, methodSymbolTable):
    # Case: single value
    if len(xmlElement) == 1:
        value = xmlElement[0].text
        if xmlElement[0].tag == 'integerConstant':
            vmFile.append('push constant {}'.format(value))

        # Case: variable
        elif xmlElement[0].tag == 'identifier':
            symbol = methodSymbolTable.getSymbolByName(xmlElement[0].text)
            vmFile.append('push {symbol.segment} {symbol.offset}'.format(symbol=symbol))

        """ TODO
        elif xmlElement.tag == 'stringConstant':
        elif xmlElement.tag == 'keywordConstant':

        etc..."""

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

        methodSymbolTable.addSymbol(varName, varType, "local")


def parseLetStatement(vmFile, xmlElement, methodSymbolTable):
    symbolName = xmlElement[1].text
    # Brackets...

    expression = xmlElement.findall("expression")[-1]  # Last occurence
    parseExpression(vmFile, expression, methodSymbolTable)

    symbol = methodSymbolTable.getSymbolByName(symbolName)
    vmFile.append('pop {symbol.segment} {symbol.offset}'.format(symbol=symbol))
