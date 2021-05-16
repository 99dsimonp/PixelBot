# PixelBot
Basic pixel bot framework for World of Warcraft WOTLK. 

Functions using two parts:
1) Addon: Encodes key game information in colors overlaid on the UI.
2) Python script: Screenshots the game and decodes the colors.

Information can be encoded using colors as each pixel has an RGB tuple consisting of three values. Each of these values can encode [0,255] and we can thus encode a total of 256^3 unique values. 

Different data types are encoded as follows:
One color can encode 24 boolean variables using the bits of the three bytes.
One color can encode (at least) three characters, using one byte for each. Limiting the available characters means more characters can be encoded in a single color.
One color can encode a decimal value with up to 10 digits. No decimal values larger than 9.9 are used in the game, and are thus not supported.
One color can encode an integer up to 256^3-1.

The Python script uses the pywin32 library to send messages to the game process. This is done in the background. However, switching between foreground and background while a key is pressed down will release the key and the script does not currently register this.
Similarly, pywin32 is used to take screenshots of the window and can be done in the background. A separate thread continuously updates the Python script by reading the bar of colors and decoding them. 
