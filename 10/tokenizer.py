import re
from string import ascii_letters
from string import digits
from string import whitespace
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])
REGEX_TOKEN_TYPE_IDENTIFIER = re.compile('[a-zA-Z_]\w*')


def tokenize(jackProgram):
	token = ""
	tokens = []
	isInString = False

	for char in jackProgram:
		# Case of a String :
		if char == '"':
			if isInString:
				isInString = False
				token += char
				tokens.append(token)
				token = ""
				continue
			isInString = True
			token += char
			continue

		if isInString:
			token += char
			continue

		# Case of the rest
		if char in ascii_letters or char in digits or char == '_':
			token += char
			continue

		# if already building a tokenString and it breaks
		if token:
			tokens.append(token)
			token = ""

		if char in whitespace:
			continue

		# Case of a symbol
		else:
			tokens.append(char)
			token = ""
			continue

	return tokens


def analyseTokenType(tokenList):
	knownKeywords = ("class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
		"void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return", )
	knownSymbols = ("{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~", )
	tokensWithTypes = []

	for token in tokenList:
		if token in knownKeywords:
			tokenType = "keyword"

		elif token in knownSymbols:
			tokenType = "symbol"

		elif token.isdigit() and 0 <= int(token) <= 32767:
			tokenType = "integerConstant"

		elif token.startswith('"') and token.endswith('"'):
			token = token[1:-1]
			tokenType = "stringConstant"

		elif REGEX_TOKEN_TYPE_IDENTIFIER.match(token):
			tokenType = "identifier"

		else:
			raise Exception("Error : invalid token {}".format(token))

		tokensWithTypes.append(Token(value=token,  type=tokenType))
	return tokensWithTypes
