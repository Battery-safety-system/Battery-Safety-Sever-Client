# program to demonstrate the use of flush()

# # creating a file
# fileObject = open("gfg.txt", "w+")
#
# # writing into the file
# fileObject.write("Geeks 4 geeks !")

# # closing the file
# fileObject.close()

# opening the file to read its content
fileObject = open("gfg.txt", "r")

# reading the contents before flush()
fileContent = fileObject.read()

# displaying the contents
print("\nBefore flush():\n", fileContent)

# clearing the input buffer
# fileObject.flush()

# reading the contents after flush()
# reads nothing as the internal buffer is cleared
fileContent = fileObject.read()

# displaying the contents
print("\nAfter flush():\n", fileContent)

# closing the file
fileObject.close()