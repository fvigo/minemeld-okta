import logging
import requests
import json

LOG = logging.getLogger(__name__)

# OKTA URIs
url_userlookup = '/api/v1/users/'
url_grouplookup = '/api/v1/groups?q='
url_groupchange = '/api/v1/groups'
url_zonechange = '' # TBD

# Looks up an Okta user ID from username
def lookup_user(oktatarget, user):

    url = "https://" +  oktatarget['addr'] + url_userlookup + user

    LOG.debug('Invoking URL %s for user lookup' % url)

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.get(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise Exception('API Error! Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    LOG.debug('Performed user lookup for user ' + user + '!')

    # Decode the JSON response into a dictionary and use the data
    data = response.json()

    userid = data['id']

    LOG.debug('User ' + user + ' OKTA ID is ' + userid)

    return userid


# Look up a Okta Group ID from the start of group name
# If there are multiple groups starting with the same name, an exception is returned
def lookup_group(oktatarget, group):

    # Lookup the group
    url = "https://" +  oktatarget['addr'] + url_grouplookup + group + '&limit=2'

    LOG.debug('Invoking URL %s for group lookup' % url)

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.get(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise Exception('API Error! Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    LOG.debug('Performed group lookup for group ' + group + '!')

    # Decode the JSON response into a dictionary and use the data
    data = response.json()

    #print 'Returned %d entries!' % len(data)

    if(len(data) != 1):
    	raise Exception('Group search for %s did not return exactly one entry (%d):  please refine the query!' % (group, len(data)))

    groupid = data[0]['id']

    LOG.debug('Group ' + group + ' OKTA ID is ' + groupid)

    return groupid


# Add an Okta user to an Okta group
# Inputs are user and group ID in OKTA format
def add_user_to_group(oktatarget, userid, groupid):


    url = "https://" +  oktatarget['addr'] + url_groupchange + '/' + groupid + '/users/' + userid

    LOG.debug('Invoking HTTP PUT on URL %s for group assignment' % url)

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.put(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise Exception('API Error! Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    LOG.debug('Added user  %s to group %s!' % (userid, groupid))


# Remove an Okta user from an Okta group
# Inputs are user and group ID in OKTA format
def remove_user_from_group(oktatarget, userid, groupid):

    # Lookup the group
    url = "https://" +  oktatarget['addr'] + url_groupchange + '/' + groupid + '/users/' + userid

    LOG.debug('Invoking HTTP DELETE on URL %s for group unassignment' % url)

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.delete(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise Exception('API Error! Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        exit()

    LOG.debug('Removed user %s from group %s!' % (userid, groupid))

# Look up user and group and add user to group
def lookup_and_add(oktatarget, user, group):
    add_user_to_group(oktatarget, lookup_user(oktatarget, user), lookup_group(oktatarget, group))

# Look up user and group and remove user from group
def lookup_and_remove(oktatarget, user, group):
    remove_user_from_group(oktatarget, lookup_user(oktatarget, user), lookup_group(oktatarget, group))

