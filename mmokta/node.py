import logging
import json
import yaml
import os
from mmokta import okta as okta

from minemeld.ft.actorbase import ActorBaseFT
import minemeld.ft.base as base

LOG = logging.getLogger(__name__)

# Okta Output Node for MineMeld
class OktaOutput(ActorBaseFT):
    def configure(self):
        super(OktaOutput, self).configure()
    
        self.oktatarget = {
            'addr' : None,
            'token' : None
        }
    
        # Load Side Config
        self.side_config_path = self.config.get('side_config', None)
        if self.side_config_path is None:
            self.side_config_path = os.path.join(
                os.environ['MM_CONFIG_DIR'],
                '%s_side_config.yml' % self.name
            )

        self._load_side_config()

    def _load_side_config(self):
        try:
            with open(self.side_config_path, 'r') as f:
                sconfig = yaml.safe_load(f)

        except Exception as e:
            LOG.error('{} - Error loading side config: {}'.format(self.name, str(e)))
            return

        # Okta Endpoint Configuration
        self.oktatarget = {
            'addr' : sconfig.get('okta_base_url', None),
            'token' : sconfig.get('okta_token', None),
        }

        # Okta Group name (not ID) to assign users to
        self.quarantine_group = sconfig.get('quarantine_group', None)

        # Okta Suspend User
        self.suspend_user = sconfig.get('suspend_user', None)

        # Okta Unsuspend User when indicator is withdrawn
        self.unsuspend_user = sconfig.get('unsuspend_user', None)

        # Okta Clear User Sessions
        self.clear_user_sessions = sconfig.get('clear_user_sessions', None)

    def hup(self, source=None):
        LOG.info('{} - hup received, reload side config'.format(self.name))
        self._load_side_config()
        super(OktaOutput, self).hup(source)

    @base._counting('update.processed')
    def filtered_update(self, source=None, indicator=None, value=None):
        if self.oktatarget['token'] is None:
            raise RuntimeError('{} - OKTA Auth Token not set'.format(self.name))

        if self.oktatarget['addr'] is None:
            raise RuntimeError('{} - OKTA Base URL not set'.format(self.name))

        # Work exclusively with user-id indicators
        if(value['type'] != 'user-id'):
            LOG.debug('{} - Received Indicator of type {}, expecting user-id, skipping'.format(self.name, value['type']))
            return

        # Lookup user
        user = okta.lookup_user(self.oktatarget, indicator)

        # Add user to Group
        if self.quarantine_group is not None:
            groupid = okta.lookup_group(self.oktatarget, self.quarantine_group)
            okta.add_user_to_group(self.oktatarget, user, groupid)

        # Suspend user
        if self.suspend_user is not None:
            okta.suspend_user(self.oktatarget, user)

        # Clear user sessions
        if self.clear_user_sessions is not None:
            okta.clear_user_sessions(self.oktatarget, user)

    @base._counting('withdraw.processed')
    def filtered_withdraw(self, source=None, indicator=None, value=None):
        if self.oktatarget['token'] is None:
            raise RuntimeError('{} - OKTA Auth Token not set'.format(self.name))

        if self.oktatarget['addr'] is None:
            raise RuntimeError('{} - OKTA Base URL not set'.format(self.name))

        # Work exclusively with user-id indicators
        if(value['type'] != 'user-id'):
            LOG.debug('{} - Received Indicator of type {}, expecting user-id, skipping'.format(self.name, value['type']))
            return

        # Lookup user
        user = okta.lookup_user(self.oktatarget, indicator)

        # Remove user from  Group
        if self.quarantine_group is not None:
            groupid = okta.lookup_group(self.oktatarget, self.quarantine_group)
            okta.remove_user_from_group(self.oktatarget, user, groupid)

       # UnSuspend user
        if self.unsuspend_user is not None:
            okta.unsuspend_user(self.oktatarget, user)

    