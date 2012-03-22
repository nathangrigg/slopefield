#! /usr/bin/python

import slopefield as sf
import unittest

class TestTick(unittest.TestCase):
    def testArithmetic(self):
        r = sf.tick(1,1,lambda t,y:2*t-y,2**0.5)
        self.assertEqual(r,[0.5,0.5,1.5,1.5])
    def testDivideZero(self):
        r = sf.tick(1,0,lambda t,y:t/y,1)
        self.assertEqual(r,[1,-0.5,1,0.5])
    def testSyntaxError(self):
        r = sf.tick(1,1,lambda t,y:ty,1)
        self.assertEqual(r,[1,1,1,1])

class TestSanitization(unittest.TestCase):
    def testValidFunction(self):
        r = sf.sanitize('sin(2+pi)*e^(1.2) + 1/2 - sqrt(2)')
        self.assertEqual(r(1,1),-3.933187336977838)
        r = sf.sanitize('t+y/2')
        self.assertEqual(r(1,1),1.5,'t=1,y=1')
        self.assertEqual(r(-1,4),1,'t=-1,y=1')
    def testInvalidWord(self):
        self.assertRaises(sf.SanitizeError,sf.sanitize,'3 + int(1.2)')
    def testSyntaxError(self):
        self.assertRaises(sf.SanitizeError,sf.sanitize,'3+*2')
    def testNameError(self):
        self.assertRaises(sf.SanitizeError,sf.sanitize,'sin.t')
    def testSanityError(self):
        self.assertRaises(sf.SanitizeError,sf.sanitize,'sin + t')

class TestClip(unittest.TestCase):
    def testClipMiddle(self):
        self.assertEqual(sf.clip(1,5,10),5)
    def testClipRight(self):
        self.assertEqual(sf.clip(1,11,10),10)
    def testClipLeft(self):
        self.assertEqual(sf.clip(1,0,10),1)




if __name__ == "__main__":
    unittest.main()

