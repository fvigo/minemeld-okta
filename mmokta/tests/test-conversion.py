import logging
import os
import sys
import json

TESTNAME='test_conversion'

logging.basicConfig(filename='/tmp/mmokta.log',level=logging.DEBUG)
LOG = logging.getLogger(__name__)


# Workaround to allow testing
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

try:
    from mmokta import okta as okta
except ImportError as e:
    LOG.error("Import error!")
    LOG.debug('%s', e)

class testclass(object):

        def __init__(self):
            self.name = TESTNAME

        def run_test(self):
            # Read the configuration
            with open('testconfig.json') as f:
                _testconfig = json.load(f)

            if 'conversion_table' in _testconfig.keys():
                conversion_table=_testconfig['conversion_table']
            else:
                conversion_table = ""
            
            default_input1=_testconfig['default_input1']
            default_input2=_testconfig['default_input2']
            default_input3=_testconfig['default_input3']

            # Check arguments to determine user nad group
            if len(sys.argv) != 3:
                LOG.info('{} - Arguments not provided! Using default!'.format(self.name))
                input1 = default_input1
                input2 = default_input2
                input3 = default_input3
            else:
                input1 = sys.argv[1]
                input2 = sys.argv[2]
                input3 = sys.argv[3]

            if(conversion_table):
                LOG.warning('{} - Conversion table not provided!'.format(self.name))

            # Test functions with different inputs

            LOG.info('{} - Testing conversion function with input: {}'.format(self.name,input1))
            output = okta.convert_userdomain(input1, conversion_table)
            LOG.info('{} - Output was: {}'.format(self.name,output))

            LOG.info('{} - Testing conversion function with input: {}'.format(self.name,input2))
            output = okta.convert_userdomain(input2, conversion_table)
            LOG.info('{} - Output was: {}'.format(self.name,output))

            LOG.info('{} - Testing conversion function with input: {}'.format(self.name,input3))
            output = okta.convert_userdomain(input3, conversion_table)
            LOG.info('{} - Output was: {}'.format(self.name,output))

            LOG.info('All tests were successful!')            


if __name__ == "__main__":
    t = testclass()
    t.run_test()

    print 'All tests were successful!'
    exit()

