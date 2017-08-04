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

    LOG.debug('{} - Invoking URL {} for user lookup'.format(self.name, url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.get(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise RuntimeError('{} - API Error! Status: {} Headers: {} Error Response: {}'.format(self.name, response.status_code, response.headers,response.json())

    LOG.debug('{} - Performed user lookup for user {} !'.format(self.name, user))

    # Decode the JSON response into a dictionary and use the data
    data = response.json()

    userid = data['id']

    LOG.debug('{} - User {} OKTA ID is: {}'.format(self.name, user, userid)))

    return userid


# Look up a Okta Group ID from the start of group name
# If there are multiple groups starting with the same name, an exception is returned
def lookup_group(oktatarget, group):

    # Lookup the group
    url = "https://" +  oktatarget['addr'] + url_grouplookup + group + '&limit=2'

    LOG.debug('{} - Invoking URL {} for group lookup'.format(self.name,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.get(url, headers=headers )

    # Check for HTTP codes other than 200
    if response.status_code != 200:
        raise RuntimeError('{} - API Error! Status: {} Headers: {} Error Response: {}'.format(self.name, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Performed group lookup for group {} !'.format(self.name,group))

    # Decode the JSON response into a dictionary and use the data
    data = response.json()

    # TODO: define a logic to support multiple groups starting with the same name
    if(len(data) != 1):
    	raise RuntimeError('{} - Group search for {} did not return exactly one entry ({}): please refine the query!'.format(self.name, group, len(data)))

    groupid = data[0]['id']

    LOG.debug('{} - Group {} OKTA ID is: {}'.format(self.name,groupid))

    return groupid


# Add an Okta user to an Okta group
# Inputs are user and group ID in OKTA format
def add_user_to_group(oktatarget, userid, groupid):


    url = "https://" +  oktatarget['addr'] + url_groupchange + '/' + groupid + '/users/' + userid

    LOG.debug('{} - Invoking HTTP PUT on URL {} for group assignment'.format(self.name,url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.put(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(self.name, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Added user {} to group {}!'.format(self.name, userid, groupid))


# Remove an Okta user from an Okta group
# Inputs are user and group ID in OKTA format
def remove_user_from_group(oktatarget, userid, groupid):

    # Lookup the group
    url = "https://" +  oktatarget['addr'] + url_groupchange + '/' + groupid + '/users/' + userid

    LOG.debug('{} - Invoking HTTP DELETE on URL {} for group unassignment'.format(self.name, url))

    # Set proper headers
    headers = {"Content-Type":"application/json","Accept":"application/json", "Authorization":"SSWS " + oktatarget['token']}

    response = requests.delete(url, headers=headers )

    # Check for HTTP codes other than 204
    if response.status_code != 204:
        raise RuntimeError('{} API Error! Status: {} Headers: {} Error Response: {}'.format(self.name, response.status_code, response.headers,response.json()))

    LOG.debug('{} - Removed user {} from group {}!'.format(self.name, userid, groupid))

# Look up user and group and add user to group
def lookup_and_add(oktatarget, user, group):
    add_user_to_group(oktatarget, lookup_user(oktatarget, user), lookup_group(oktatarget, group))

# Look up user and group and remove user from group
def lookup_and_remove(oktatarget, user, group):
    remove_user_from_group(oktatarget, lookup_user(oktatarget, user), lookup_group(oktatarget, group))

