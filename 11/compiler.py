import textwrap
from SymbolTable import SymbolTable


class Compiler:
    def __init__(self):
        self.vmFile = []
        self.currentMethodSymbolTable = None
        self.currentClassSymbolTable = None
        self.labelUniqueID = 0

    def XMLToVM(self, XMLTree):
        self.parseClass(XMLTree)
        return "\n".join(self.vmFile)

    def parseClass(self, xmlElement):
        fileClass = xmlElement
        className = fileClass.find('identifier').text

        self.currentClassSymbolTable = SymbolTable()
        for classVarDec in fileClass.findall('classVarDec'):
            self.parseVarDeclaration(classVarDec)

        for function in fileClass.findall('subroutineDec'):
            self.parseFunction(function, className)

    def parseFunction(self, xmlElement, className):
        function = xmlElement
        functionName = function.find('identifier').text

        localVarsCount = self.countLocalVariablesInFunction(function)
        self.vmFile.append("function {className}.{functionName} {localVarsCount}".format(
            className=className, functionName=functionName, localVarsCount=localVarsCount))

        # Arguments
        self.currentMethodSymbolTable = SymbolTable()
        arguments = function.find('parameterList')
        self.parseFunctionArguments(arguments)

        # Body
        functionBody = function.find('subroutineBody')

        # Local vars
        localVarsCount = 0
        varDeclarations = functionBody.findall('varDec')
        for varDeclaration in varDeclarations:
            self.parseVarDeclaration(varDeclaration)

        # Instructions
        statements = functionBody.find('statements')
        self.parseStatements(statements)

    def parseFunctionArguments(self, xmlElement):
        arguments = xmlElement

        index = 0
        while index < len(arguments):
            argumentType = arguments[index].text
            argumentName = arguments[index+1].text

            self.currentMethodSymbolTable.addSymbol(argumentName, argumentType, "argument")
            index += 3

    def parseStatements(self, statements):
        for statement in statements:
            self.parseStatement(statement)

    def parseStatement(self, statement):
        if statement.tag == 'doStatement':
            self.parseDoStatement(statement)

        elif statement.tag == 'returnStatement':
            self.parseReturnStatement(statement)

        elif statement.tag == 'letStatement':
            self.parseLetStatement(statement)

        elif statement.tag == 'whileStatement':
            self.parseWhileStatement(statement)

        elif statement.tag == 'ifStatement':
            self.parseIfStatement(statement)

    def parseReturnStatement(self, xmlElement):
        if xmlElement[1].tag == 'expression':
            self.parseExpression(xmlElement[1])

        self.vmFile.append('return\n')

    def parseDoStatement(self, xmlElement):
        self.parseSubroutineCall(xmlElement)

    def parseSubroutineCall(self, xmlElement):
        functionName = xmlElement.findall('identifier')[-1].text

        if xmlElement.find('symbol').text == '.':
            className = xmlElement.find('identifier').text
            functionName = "{}.{}".format(className, functionName)

        expressions = xmlElement.find('expressionList').findall('expression')
        argsCount = len(expressions)

        # Arguments
        for expression in expressions:
            self.parseExpression(expression)

        self.vmFile.append('call {functionName} {argsCount}'.format(
            functionName=functionName, argsCount=argsCount))

    def parseExpression(self, xmlElement):
        if len(xmlElement) == 1:
            term = xmlElement[0]
            self.parseTerm(term)

        # Unary operator
        elif len(xmlElement) == 2:
            operator = xmlElement[0].text
            term = xmlElement[1]

            if operator == '~':
                self.parseTerm(term)
                self.vmFile.append('not')

            elif operator == '-':
                self.vmFile.append('push constant 0')
                self.parseTerm(term)
                self.vmFile.append('sub')

        elif len(xmlElement) > 2:
            term1 = xmlElement[0]
            self.parseTerm(term1)

            operator = xmlElement[1].text

            term2 = xmlElement[2]
            self.parseTerm(term2)

            if operator == '+':
                self.vmFile.append('add')
            elif operator == '-':
                self.vmFile.append('sub')
            elif operator == '*':
                instructions = textwrap.dedent('''\
                    // We already have the 2 operands in the stack, we store them in temp0 and temp1
                    pop temp 0
                    pop temp 1

                    // Result initialisation
                    push constant 0

                    // Loop
                    label MULTIPLICATION_LOOP{labelID}

                        // Counter decrement
                        push temp 1
                        push constant 1
                        sub
                        pop temp 1

                        // Verify loop condition: until counter < 0
                        push temp 1
                        push constant 0
                        lt
                        if-goto MULTIPLICATION_END{labelID}

                        // Add first term value
                        push temp 0
                        add

                        goto MULTIPLICATION_LOOP{labelID}

                    label MULTIPLICATION_END{labelID}''').format(labelID=self.nextLabelUniqueID())
                self.vmFile.extend(instructions.split("\n"))

            elif operator == '>':
                self.vmFile.append('gt')
            elif operator == '<':
                self.vmFile.append('lt')
            elif operator == '=':
                self.vmFile.append('eq')
            elif operator == '&':
                self.vmFile.append('and')
            elif operator == '|':
                self.vmFile.append('or')

    def parseTerm(self, xmlElement):
        # Case: single value
        if len(xmlElement) == 1:
            value = xmlElement[0].text

            # Case: integer
            if xmlElement[0].tag == 'integerConstant':
                self.vmFile.append('push constant {}'.format(value))

            # Case: boolean value 'true'
            if xmlElement[0].tag == 'keyword' and value == 'true':
                self.vmFile.append('push constant 1')

            # Case: boolean value 'false'
            if xmlElement[0].tag == 'keyword' and value == 'false':
                self.vmFile.append('push constant 0')

            # Case: variable
            elif xmlElement[0].tag == 'identifier':
                symbol = self.lookupSymbol(value)

                self.vmFile.append('push {symbol.segment} {symbol.offset}'.format(symbol=symbol))

            """ TODO
            elif xmlElement.tag == 'stringConstant':
            elif xmlElement.tag == 'keywordConstant':

            etc..."""

        # Case: Negative single value
        elif xmlElement[0].tag == 'symbol' and xmlElement[0].text == '-' and len(xmlElement) == 2:
            self.vmFile.append('push constant 0')

            term = xmlElement[1]
            self.parseTerm(term)

            self.vmFile.append('sub')

        # Case: parenthesis around a expression
        elif len(xmlElement) == 3:
            if xmlElement[0].text == '(' and xmlElement[2].text == ')':
                self.parseExpression(xmlElement[1])

        # Case: subroutine call
        elif (xmlElement[0].tag == "identifier" and xmlElement[1].text == "(" or
                xmlElement[0].tag == "identifier" and xmlElement[1].text == "."):
            self.parseSubroutineCall(xmlElement)

    def parseVarDeclaration(self, xmlElement):
        variableScope = xmlElement[0].text
        varType = xmlElement[1].text

        for varNameNode in xmlElement.findall("identifier"):
            varName = varNameNode.text

            # If the type is an object name (identifier), skip the first identifier occurence
            if varName == varType:
                continue

            if variableScope == "var":
                newSymbol = self.currentMethodSymbolTable.addSymbol(varName, varType, "local")

            elif variableScope == "field":
                newSymbol = self.currentClassSymbolTable.addSymbol(varName, varType, "this")

            elif variableScope == "static":
                newSymbol = self.currentClassSymbolTable.addSymbol(varName, varType, "static")

            self.initializeVariable(newSymbol)

    def parseLetStatement(self, xmlElement):
        symbolName = xmlElement[1].text
        # Brackets...

        expression = xmlElement.findall("expression")[-1]  # Last occurence
        self.parseExpression(expression)

        symbol = self.lookupSymbol(symbolName)
        self.vmFile.append('pop {symbol.segment} {symbol.offset}'.format(symbol=symbol))

    def parseIfStatement(self, xmlElement):
        # Generate labelID for the end label
        labelID = self.nextLabelUniqueID()

        # Parse the condition
        condition = xmlElement.find('expression')
        falseLabel = 'IF_FALSE{labelID}'.format(labelID=labelID)
        self.parseCondition(condition, falseLabel)

        # IF_TRUE body statements
        ifTrueStatements = xmlElement.findall('statements')[0]
        self.parseStatements(ifTrueStatements)

        # End of IF_TRUE
        self.vmFile.append('goto IF_END{labelID}'.format(labelID=labelID))

        # Beginning of IF_FALSE
        self.vmFile.append('label IF_FALSE{labelID}'.format(labelID=labelID))

        # IF_FALSE body statements
        if len(xmlElement.findall('statements')) > 1:
            ifFalseStatements = xmlElement.findall('statements')[1]
            self.parseStatements(ifFalseStatements)

        # End of if
        self.vmFile.append('label IF_END{labelID}'.format(labelID=labelID))

    def parseWhileStatement(self, xmlElement):
        # Generate labelID for this loop
        labelID = self.nextLabelUniqueID()

        # Label for the beginning of loop
        instructions = textwrap.dedent('''\

        // While loop
        label WHILE_LOOP{labelID}''').format(labelID=labelID)
        self.vmFile.extend(instructions.split("\n"))

        # Parse the condition
        condition = xmlElement.find('expression')
        falseLabel = 'WHILE_END{labelID}'.format(labelID=labelID)
        self.parseCondition(condition, falseLabel)

        # Loop body statements
        statements = xmlElement.find('statements')
        self.parseStatements(statements)

        # End of loop body
        instructions = textwrap.dedent('''\

        goto WHILE_LOOP{labelID}
        label WHILE_END{labelID}''').format(labelID=labelID)
        self.vmFile.extend(instructions.split("\n"))

    def parseCondition(self, condition, falseLabel):
        # Push condition result on stack
        self.parseExpression(condition)

        # Condition check
        instructions = textwrap.dedent('''\

        // Test if condition result is 'false'
        push constant 0
        eq
        if-goto {falseLabel}\n''').format(falseLabel=falseLabel)
        self.vmFile.extend(instructions.split("\n"))

    def countLocalVariablesInFunction(self, functionElement):
        localVarsCount = 0

        for varDec in functionElement.find("subroutineBody").findall("varDec"):
            # Count the commas in the VarDec block, and add 1 to obtain vars count
            values = [element.text for element in varDec]
            localVarsCount += values.count(",") + 1

        return localVarsCount

    def initializeVariable(self, symbol):
        self.vmFile.append('push constant 0')
        self.vmFile.append('pop {symbol.segment} {symbol.offset}'.format(symbol=symbol))

    def nextLabelUniqueID(self):
        self.labelUniqueID += 1
        return self.labelUniqueID

    def lookupSymbol(self, symbolName):
        symbol = self.currentMethodSymbolTable.getSymbolByName(symbolName)
        if not symbol:
            symbol = self.currentClassSymbolTable.getSymbolByName(symbolName)

        if not symbol:
            raise Exception("Unknown variable (not declared ?): {}".format(symbolName))

        return symbol
