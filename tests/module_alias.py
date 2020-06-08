import modkit
modkit = modkit.modkit

NAME1 = {}
NAME3 = {}

modkit.alias('NAME2', 'NAME1')
modkit.alias({'NAME4': 'NAME3'})
modkit.alias(NAME5='NAME6')
