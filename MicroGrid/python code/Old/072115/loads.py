from collections import namedtuple

#time units are minutes, duration, wavelength,
#start end are in hours
periodicLoad = namedtuple("Pload", "power duration wavelength")
# frequency is how many per hour
intermitentLoad = namedtuple("Iload", "power duration frequency start end")
#The newly created type can be used like this:

periodic = periodicLoad(0,0,0)
intermitent = intermitentLoad(0,0,0,0,0)

# duration is in minutes, wavelength is in minutes
fridge = periodicLoad(-9, 10, 60)
coffeeMaker = periodicLoad(-3, 2, 25)
lightsEarly = intermitentLoad(-5, 3, 3, 6, 9)
lightsLate = intermitentLoad(-5, 3, 5, 17, 22)
#Or you can use named arguments:
#m = MyStruct(field1 = "foo", field2 = "bar", field3 = "baz")
