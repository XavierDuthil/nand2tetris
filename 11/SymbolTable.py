from collections import namedtuple
Symbol = namedtuple('Symbol', ['name', 'type', 'segment', 'offset'])


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def addSymbol(self, name, type_, segment):
        # Retrieve max memory offset for this Segment
        maxSegmentOffset = -1
        for symbol in self.symbols.values():
            if symbol.segment == segment and symbol.offset > maxSegmentOffset:
                maxSegmentOffset = symbol.offset

        offset = maxSegmentOffset + 1
        newSymbol = self.symbols[name] = Symbol(name, type_, segment, offset)
        return newSymbol

    def countSymbols(self, segment):
        count = 0
        for symbol in self.symbols.values():
            if symbol.segment == segment:
                count += 1

        return count

    def getSymbolByName(self, name):
        return self.symbols.get(name)
