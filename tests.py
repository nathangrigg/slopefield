#! /usr/bin/python

import slopefield as sf
import unittest

class TestTick(unittest.TestCase):
    def setUp(self):
        self.translate_y = sf.translate_y
        self.translate_t = sf.translate_t
        sf.translate_y = sf.translation(-1,10,1,500)
        sf.translate_t = sf.translation(-1,10,1,500)
    def tearDown(self):
        sf.translate_y = self.translate_y
        sf.translate_t = self.translate_t
    def testArithmetic(self):
        r = sf.tick(1,1,lambda t,y:2*t-y,2**0.5)
        self.assertEqual(r,[499.5, 499.5, 500.5, 500.5])
    def testDivideZero(self):
        r = sf.tick(1,0,lambda t,y:t/y,1)
        self.assertEqual(r,[500.0, 254.5, 500.0, 255.5])
    def testSyntaxError(self):
        r = sf.tick(1,1,lambda t,y:ty,1)
        self.assertEqual(r,[500.0, 500.0, 500.0, 500.0])

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

class TestMisc(unittest.TestCase):
    def testSvgTick(self):
        r = sf.svg_tick([1.23,5.46,5.24,1.33])
        self.assertEqual(r,'<line x1 = "1.2" y1 = "5.5" x2 = "5.2" y2 = "1.3" />')

class TestTranslations(unittest.TestCase):
    def testGeneralTranslation(self):
        r = sf.translate(2,3,5)
        self.assertEqual(r,2*5+3)
        r = sf.translate(2,3,5,noshift=True)
        self.assertEqual(r,2*5)

    def testTranslationGenerator(self):
        f = sf.translation(1,2,3,5)
        self.assertEqual(f(1),2)
        self.assertEqual(f(3),5)

class TestSlopeFieldGenerator(unittest.TestCase):
    def testSingleTick(self):
        d = {'tmax':1,'tmin':0,'tticks':1,'ymin':0,'ymax':2,'yticks':1,'fn':lambda t,y:1}
        r = list(sf.slopefield(d))
        self.assertEqual(r[0],[0.2878679656440358, 0.7878679656440357, 0.7121320343559643, 1.2121320343559643])
    def testMultipleTick(self):
        d = {'tmax':1,'tmin':0,'tticks':20,'ymin':0,'ymax':2,'yticks':25,'fn':lambda t,y:1}
        r = len(list(sf.slopefield(d)))
        self.assertEqual(r,20*25)



if __name__ == "__main__":
    unittest.main()

