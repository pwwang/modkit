from os import path
import unittest
from cmdy import python

__DIR__ = path.dirname(path.abspath(__file__))

class Test(unittest.TestCase):

	def one(self, pyfile):
		
		lines = python(path.join(__DIR__, pyfile)).strip().splitlines()
		for i in range(0, len(lines), 2):
			expected = lines[i].split('##', 1)[0].rstrip(' ')[:-10]
			observed = lines[i+1]
			self.assertEqual(expected, observed)
	
	def testAlias(self):
		self.one('testAlias.py')

	def testBan(self):
		self.one('testBan.py')
	
	def testCall(self):
		self.one('testCall.py')
	
	def testExports(self):
		self.one('testExports.py')
	
	def testModuleAll(self):
		self.one('testModuleAll.py')
	
	def testAllDelegate(self):
		self.one('testAllDelegate.py')

	def testMultiple(self):
		self.one('testMultiple.py')

if __name__ == "__main__":
	unittest.main(verbosity = 2)
