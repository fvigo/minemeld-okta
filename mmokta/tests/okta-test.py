import logging
import os
import sys
import json

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
    exit()


if __name__ == "__main__":
    # Read the configuration
    with open('testconfig.json') as f:
        _testconfig = json.load(f)

    okta_org_url=_testconfig['okta_org_url']
    okta_token=_testconfig['okta_token']

    default_user=_testconfig['default_user']
    default_group1=_testconfig['default_group1']
    default_group2=_testconfig['default_group2']

    # Check arguments to determine user nad group
    if len(sys.argv) != 3:
        LOG.info('Arguments not provided! Using default!')
        user = default_user
        group1 = default_group1
        group2 = default_group2
    else:
        user = sys.argv[1]
        group1 = sys.argv[2]
        group2 = sys.argv[3]

    if(okta_org_url == '') or (okta_token == ''):
        raise Exception('Cannot read OKTA URL and Token from configuration')

    # Okta Endpoint information
    oktatarget = {
        'addr' :  okta_org_url,
        'token' : okta_token
    }

    # Test atomic functions
    userid = okta.lookup_user(oktatarget, user)
    LOG.info('Looked up user OKTA ID %s from user name %s' % (userid, user))

    groupid1 = okta.lookup_group(oktatarget, group1)
    LOG.info('Looked up group OKTA ID %s from group name %s' % (groupid1, group1))

    groupid2 = okta.lookup_group(oktatarget, group2)
    LOG.info('Looked up group OKTA ID %s from group name %s' % (groupid1, group1))

    okta.add_user_to_group(oktatarget, userid, groupid1)
    LOG.info('Added user %s (OKTA ID %s) to group %s (OKTA ID %s)' % (user, userid, group1, groupid1))

    okta.remove_user_from_group(oktatarget, userid, groupid2)
    LOG.info('Removed user %s (OKTA ID %s) from group %s (OKTA ID %s)' % (user, userid, group2, groupid2))

    # Test added functions
    okta.lookup_and_add(oktatarget, user, group1)
    LOG.info('Looked up and added user %s to group %s' % (user, group1))

    okta.lookup_and_remove(oktatarget, user, group2)
    LOG.info('Looked up and removed user %s from group %s' % (user, group2))

    LOG.info('All tests were successful!')
    print 'All tests were successful!'
    exit()
