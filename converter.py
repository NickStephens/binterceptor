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

def convertFromRawPretty(data):
    """ convert data to a hexdump -C like format, with a predominance on the 
        hex and an ascii conversion on the right, FOR PRINTING"""
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

def convertFromRaw(data):
    """ convert data to a hexdump like format, FOR EDITING """
    global LINEBREAK
    result = ""

    current = data[:LINEBREAK]
    next = data[LINEBREAK:]
    while (current):
        result += convertToHex(current) + "\n"
        current = next[:LINEBREAK]
        next = next[LINEBREAK:]
   
    return result 

def convertToRaw(str):
    """ converts of string of ascii digits to raw binary values """
    raw = ""
    
    str = str.split()
    for b in str:
        raw += (chr(int(b,16)))

    return raw
