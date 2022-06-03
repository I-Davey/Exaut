from iniconfig import Parse
#example of using the iniconfig in another file

def example_1():
    #first example
    vars = Parse("Example").cfg
    int_example = vars["int"]
    string_example = vars["string"]
    print("example integer grabbed from Ini file, first config:", int_example)
    print("example String grabbed from Ini file, first config:", string_example)

def example_2():
    #second example
    vars = Parse("Second Example").cfg
    int_example = vars["bool"]
    string_example2 = vars["string"]
    print("\nexample bool grabbed from Ini file, second config:", int_example)
    print("example String grabbed from Ini file, second config:", string_example2)

example_1()
example_2()