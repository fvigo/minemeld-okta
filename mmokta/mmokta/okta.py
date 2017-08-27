import logging
import requests
import json
import re
import sys

LOG = logging.getLogger(__name__)

# Object/Function Name for debugging purposes in log
# If this is invoked within an object, then it will be self.name, otherwise the function name
try:
  self
except NameError:
    MYNAME = sys._getframe().f_code.co_name
else:
    MYNAME = self.name
    

# OKTA URIs
url_userlookup = '/api/v1/users/{}'
url_usersuspend = '/api/v1/users/{}/lifecycle/suspend'
url_userunsuspend = '/api/v1/users/{}/lifecycle/unsuspend'
url_grouplookup = '/api/v1/groups?q={}&limit=2'
url_groupchange = '/api/v1/groups/{}/users/{}'
url_clearusersessions = '/api/v1/users/{}/sessions'
url_zonechange = '' # TBD

# Converts user/domain format
#
# Input can be:
#   - username@domain.ext
#   - domain\username
#   - username
#
#  Output should always be:
#   - username@domain.ext (Okta email format)
#
# The conversion table is checked at the end to map a group name (or absence of) to a specific value
# If no match is found in the table, tranlsated input (to username@domain) is sent unmodified
def convert_userdomain(input, conversion_table):
    domain = ""
    domainFound = False

    LOG.debug('{} - Invoked with input: {}'.format(MYNAME, input))

    # Match domain\user format
    m = re.search('^(?P<domain>[a-zA-Z0-9_\-\.]*)\\\\(?P<user>.*)$', input)
    if m != None:
        LOG.debug('{} - NetBIOS domain parser found\n\tUser: {}\n\tDomain: {}\n'.format(MYNAME,m.group('user'),m.group('domain')))
        if m.group('domain'):
                domain = m.group('domain')
                domainFound = True
    else:
        LOG.debug('{} - NetBIOS domain parser did not find anything'.format('convert_username'))
        

    # Match user@domain format
    if domainFound == False:
        m = re.search('^(?P<user>.*)@(?P<domain>.*)$', input)
        if m != None:
            LOG.debug('{} - Email domain parser found\n\tUser: {}\n\tDomain: {}\n'.format(MYNAME,m.group('user'),m.group('domain')))
            if m.group('domain'):
                    domain = m.group('domain')
        else:
            LOG.debug('{} - Email domain parser did not find anything'.format(MYNAME))

        if domain != "":
            LOG.debug('{} - Email domain parser did not find anything'.format(MYNAME))

    if domainFound == True:
        LOG.debug('{} - Ready to apply conversion table for domain: {}'.format(MYNAME,domain))
    else:
        LOG.debug('{} - No domain found - applying conversion table for empty domain if applicable'.format(MYNAME))
    
    # TODO: Add conversion table code here
    if domainFound:
        output = domain
    else:
        output = "nodomainfound.ext"

    return output

# Looks up an Okta user ID and Status from username
def lookup_user(oktatarget, user):

    url = 'https://{}{}'.format(oktatarget['addr'], url_userlookup.format(user))

    LOG.debug('{} - Invoking URL {} for user lookup'.format(MYNAME, url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.get(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise RuntimeError('{} - API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Performed user lookup for user {} !'.format(MYNAME, user))

    # Decode the JSON response into a dictionary and use the data
    data = response.json()

    u = { 'id' : data['id'], 'status' : data['status'] }

    LOG.debug('{} - User {} OKTA ID is: {} ; Status: {}'.format(MYNAME, user, u['id'], u['status']))

    return u


# Look up a Okta Group ID from the start of group name
# If there are multiple groups starting with the same name, an exception is returned
def lookup_group(oktatarget, group):

    # Lookup the group
    url = 'https://{}{}'.format(oktatarget['addr'],url_grouplookup.format(group))

    LOG.debug('{} - Invoking URL {} for group lookup'.format(MYNAME,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.get(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise RuntimeError('{} - API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Performed group lookup for group {} !'.format(MYNAME,group))

    # Decode the JSON response into a dictionary and use the data
    data = response.json()

    # TODO: define a logic to support multiple groups starting with the same name
    if(len(data) != 1):
        raise RuntimeError('{} - Group search for {} did not return exactly one entry ({}): please refine the query!'.format(MYNAME, group, len(data)))

    groupid = data[0]['id']

    LOG.debug('{} - Group {} OKTA ID is: {}'.format(MYNAME,group, groupid))

    return groupid


# Add an Okta user to an Okta group
# Inputs are userid and group ID in OKTA format
def add_user_to_group(oktatarget, u, groupid):

    userid = u['id']

    # Add the user to group
    url = 'https://{}{}'.format(oktatarget['addr'], url_groupchange.format(groupid,userid))

    LOG.debug('{} - Invoking HTTP PUT on URL {} for group assignment'.format(MYNAME,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.put(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Added user {} to group {}!'.format(MYNAME, userid, groupid))

# Remove an Okta user from an Okta group
# Inputs are userid and group ID in OKTA format
def remove_user_from_group(oktatarget, u, groupid):

    userid = u['id']

    # Remove the user from group
    url = 'https://{}{}'.format(oktatarget['addr'], url_groupchange.format(groupid,userid))

    LOG.debug('{} - Invoking HTTP DELETE on URL {} for group unassignment'.format(MYNAME, url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.delete(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Removed user {} from group {}!'.format(MYNAME, userid, groupid))

# Suspend an OKTA User
# Input userid in OKTA format
def suspend_user(oktatarget, u):
    
    userid = u['id']

    if(u['status'] == 'SUSPENDED'):
        LOG.debug('{} - User {} is already in SUSPENDED state, nothing to do!'.format(MYNAME, u['id']))
        return

    # Suspend user
    url = 'https://{}{}'.format(oktatarget['addr'],url_usersuspend.format(userid))

    LOG.debug('{} - Invoking HTTP POST on URL {} for user suspend'.format(MYNAME,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.post(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Suspended user {}!'.format(MYNAME, userid))

# Unsuspend an OKTA User
# Input userid in OKTA format
def unsuspend_user(oktatarget, u):

    userid = u['id']

    if(u['status'] == 'ACTIVE'):
        LOG.debug('{} - User {} is already in ACTIVE state, nothing to do!'.format(MYNAME, u['id']))
        return

    # Unsuspend user
    url = 'https://{}{}'.format(oktatarget['addr'],url_userunsuspend.format(userid))

    LOG.debug('{} - Invoking HTTP POST on URL {} for user unsuspend'.format(MYNAME,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.post(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Unsuspended user {}!'.format(MYNAME, userid))

# Clear user sessions
# Input userid in OKTA format
def clear_user_sessions(oktatarget, u):
    
    userid = u['id']

    # Clear user sessions
    url = 'https://{}{}'.format(oktatarget['addr'],url_clearusersessions.format(userid))

    LOG.debug('{} - Invoking HTTP DELETE on URL {} for user clear sessions'.format(MYNAME,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.delete(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(MYNAME, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Cleared sessions for user {}!'.format(MYNAME, userid))

# Look up user and group and add user to group
def lookup_and_add(oktatarget, user, group):
    add_user_to_group(oktatarget, lookup_user(oktatarget, user), lookup_group(oktatarget, group))

# Look up user and group and remove user from group
def lookup_and_remove(oktatarget, user, group):
    remove_user_from_group(oktatarget, lookup_user(oktatarget, user), lookup_group(oktatarget, group))

# Look up and suspend an user
def lookup_and_suspend_user(oktatarget, user):
    suspend_user(oktatarget, lookup_user(oktatarget, user))

# Look up and unsuspend an user
def lookup_and_unsuspend_user(oktatarget, user):
    unsuspend_user(oktatarget, lookup_user(oktatarget, user))

# Look up and clear sessions for an user
def lookup_and_clear_user_sessions(oktatarget, user):
    clear_user_sessions(oktatarget, lookup_user(oktatarget, user))
