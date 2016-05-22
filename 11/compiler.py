import textwrap
from contextlib import suppress
from SymbolTable import SymbolTable


class NoSuchSymbol(Exception):
    pass


class NoSuchOperator(Exception):
    pass


class CompilationError(Exception):
    pass


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

        self.currentClassName = className
        self.currentClassSymbolTable = SymbolTable()
        for classVarDec in fileClass.findall('classVarDec'):
            self.parseVarDeclaration(classVarDec)

        for function in fileClass.findall('subroutineDec'):
            self.parseMethod(function)

    def parseMethod(self, xmlElement):
        function = xmlElement
        methodName = function[2].text

        localVarsCount = self.countLocalVariablesInFunction(function)
        self.vmFile.append("function {className}.{methodName} {localVarsCount}".format(
            className=self.currentClassName, methodName=methodName, localVarsCount=localVarsCount))

        if function[0].text == 'constructor':
            sizeToAlloc = self.currentClassSymbolTable.countSymbols('this')
            self.vmFile.append("push constant {}".format(sizeToAlloc))  # Argument for the next call
            self.vmFile.append("call Memory.alloc 1")  # System call to allocate a given size in ram
            self.vmFile.append("pop pointer 0")  # Base address for THIS

        # Set THIS to the value of the first argument
        elif function[0].text == 'method':
            self.vmFile.append("push argument 0")
            self.vmFile.append("pop pointer 0")

        # Arguments
        self.currentMethodSymbolTable = SymbolTable()
        arguments = function.find('parameterList')
        self.parseMethodArguments(arguments)

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

    def parseMethodArguments(self, xmlElement):
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

        else:
            self.vmFile.append('push constant 0')

        self.vmFile.append('')
        self.vmFile.append('return\n')

    def parseDoStatement(self, xmlElement):
        self.parseSubroutineCall(xmlElement)
        self.vmFile.append('pop temp 0')

    def parseSubroutineCall(self, xmlElement):
        methodName = xmlElement.findall('identifier')[-1].text
        className = self.currentClassName
        argsCount = 0

        if xmlElement.find('symbol').text == '.':
            objectName = xmlElement.find('identifier').text
            className = objectName

            # Push identified object address instead of the currently executed object address as first argument
            # If no object of this name is found, it is a static call and no THIS argument is required
            with suppress(NoSuchSymbol):
                objectInstance = self.lookupSymbol(objectName)
                className = objectInstance.type
                push_this = 'push {obj.segment} {obj.offset}'.format(obj=objectInstance)  # Retrieve the THIS base adress for this object
                argsCount = 1
                self.vmFile.append(push_this)

        else:
            # If call is within current object, the first argument is the current object address, to be used as THIS
            argsCount = 1
            push_this = 'push pointer 0'
            self.vmFile.append(push_this)

        methodName = "{}.{}".format(className, methodName)

        expressions = xmlElement.find('expressionList').findall('expression')
        argsCount += len(expressions)

        # Arguments
        for expression in expressions:
            self.parseExpression(expression)

        command = 'call {methodName} {argsCount}'.format(methodName=methodName, argsCount=argsCount)
        self.vmFile.append(command)

    def parseExpression(self, xmlElement):
        if len(xmlElement) == 1:
            term = xmlElement[0]
            self.parseTerm(term)

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

        else:
            raise CompilationError("Expression unkown: {} {}".format(xmlElement[0].text, xmlElement[1].text))

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

            # Case: 'this'
            if xmlElement[0].tag == 'keyword' and value == 'this':
                self.vmFile.append('push pointer 0')  # Push the base THIS address

            # Case: variable
            elif xmlElement[0].tag == 'identifier':
                symbol = self.lookupSymbol(value)

                self.vmFile.append('push {symbol.segment} {symbol.offset}'.format(symbol=symbol))

            """ TODO
            elif xmlElement.tag == 'stringConstant':
            elif xmlElement.tag == 'keywordConstant':

            etc..."""

        # Unary operator
        elif xmlElement[0].tag == 'symbol' and len(xmlElement) == 2:
            operator = xmlElement[0].text
            term = xmlElement[1]

            if operator == '~':
                self.parseTerm(term)

                # Boolean not <=> (a+1)%2
                self.vmFile.append('push constant 1')
                self.vmFile.append('add')
                self.vmFile.append('push constant 1')
                self.vmFile.append('and')

            elif operator == '-':
                self.vmFile.append('push constant 0')
                self.parseTerm(term)
                self.vmFile.append('sub')

            else:
                raise NoSuchOperator("Operator '{}' unknown".format(operator))

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
                self.initializeVariable(newSymbol)

            elif variableScope == "field":
                newSymbol = self.currentClassSymbolTable.addSymbol(varName, varType, "this")

            elif variableScope == "static":
                newSymbol = self.currentClassSymbolTable.addSymbol(varName, varType, "static")

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
            raise NoSuchSymbol("Unknown variable (not declared ?): {}".format(symbolName))

        return symbol
