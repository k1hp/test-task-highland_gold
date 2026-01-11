import unittest
import sys

print("=" * 60)
print("Launching tests QGIS Processor")

# load tests
loader = unittest.TestLoader()
suite = loader.loadTestsFromName('tests.test_processor.TestProcessorSimple')

# run tests
runner = unittest.TextTestRunner(verbosity=2, failfast=True)
result = runner.run(suite)

print("=" * 60)
print(f"Result: {'SUCCESS' if result.wasSuccessful() else 'WE HAVE SOME ERRORS!'}")
print("=" * 60)

sys.exit(0 if result.wasSuccessful() else 1)