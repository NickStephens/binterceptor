import string 

# GLOBALS
LINEBREAK = 15

def convertToHex(data):
    """ convert data into a readable hexdecimal values like hexdump """
    data = map(ord, data)
    fmtstr = "{:02x} " * len(data) 
    return fmtstr.format(*data)

def convertToAscii(data):
    """ convert hexadecimal values to their ascii equivalents, non-printable
        data is converted to a period """
    result = ""
    for c in data:
        if c not in string.printable[:-5]:
            result += "."
        else:
            result += c

    return result

def convert(data):
    """ convert data to a hexdump -C like format, with a predominance on the 
        hex and an ascii conversion on the right """
    global LINEBREAK
    result = ""
  
    current = data[:LINEBREAK]
    next = data[LINEBREAK:]
    while (current):
        pad = LINEBREAK - len(current)
        result += convertToHex(current) + (pad * "   ") + "\t| " + convertToAscii(current) + (pad * " ") + " |\n" 
        current = next[:LINEBREAK]
        next = next[LINEBREAK:]

    return result
