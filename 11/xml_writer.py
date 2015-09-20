import xml.etree.ElementTree as ET


def tokenListToXML(tokensWithTypes):
	root = ET.Element("tokens")

	for tokenType, tokenValue in tokensWithTypes:
		thisToken = createXMLNode(tokenType, tokenValue)
		root.append(thisToken)

	return root


def NodeToXML(node):
	# Type and Value
	xmlNode = createXMLNode(node.type, node.value)

	# Children
	for child in node.children:
		xmlNode.append(NodeToXML(child))

	return xmlNode


def XMLToText(XMLTree):
	return ET.tostring(XMLTree).decode("utf-8")


def createXMLNode(type, value):
	XMLNode = ET.Element(type)
	if value:
		XMLNode.text = value
	else:
		XMLNode.text = "\n"

	XMLNode.tail = "\n"
	return XMLNode
