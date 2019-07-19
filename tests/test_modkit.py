
import sys
from os import path
import pytest
from cmdy import python
python = python.bake(_exe = sys.executable)

__DIR__ = path.dirname(path.abspath(__file__))

def one(pyfile):

	cmd = python(path.join(__DIR__, pyfile))
	lines = cmd.strip().splitlines()
	for i in range(0, len(lines), 2):
		expected = lines[i].split('##', 1)[0].rstrip(' ')[:-10]
		try:
			observed = lines[i+1]
		except IndexError:
			observed = 'IndexError'
		assert observed == expected

def testAlias():
	one('_testAlias.py')

def testBan():
	one('_testBan.py')

def testCall():
	one('_testCall.py')

def testExports():
	one('_testExports.py')

def testModuleAll():
	one('_testModuleAll.py')

def testAllDelegate():
	one('_testAllDelegate.py')

def testMultiple():
	one('_testMultiple.py')
