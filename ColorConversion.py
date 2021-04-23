import math

def IntegerToColor(i):
    if i != math.floor(i):
        print("Error!")
        return 0
    if i > 256*256*256 - 1:
        print("Error: Value too large!")
        return 0
    b = i % 256
    i = math.floor(i/256)
    g = i % 256
    i = math.floor(i/256)
    r = i % 256

    return (r/255, g/255, b/255)

def ColorToInteger(r,b,g):
    assert(0 <= r <= 255)
    assert(0 <= b <= 255)
    assert(0 <= g <= 255)
    hx = '%02x%02x%02x' % (r, b, g)
    return int(hx, 16)

def DecimalToColor(i):
    if i > 9.99999:
        print("Error: decimal too large")
        return 0
    if i < 0:
        print("Error: Decimal too small")
    i = math.floor(i*100000)
    return IntegerToColor(i)

def ColorToDecimal(r,b,g):
    intval = ColorToInteger(r,b,g)
    return intval / 100000


def StringToColor(input):
    input = input.upper()
    ascii_vals = ""
    for val in input[:3]:
        ascii_vals = ascii_vals + str(ord(val))
    intval = int(ascii_vals)
    return IntegerToColor(intval)

def ColorToString(r,b,g):
    intval = ColorToInteger(r,b,g)
    if intval > 999999:
        return None
    intstring = str(intval)
    string_output = ""
    for i in range(0, len(intstring), 2):
        string_output = string_output + chr(int(intstring[i:i+2]))
    return string_output

def ColorToBool(r,b,g):
    intval = ColorToInteger(r,b,g)
    return [bool(intval & (1<<n)) for n in range(18)]