import logging
import json
from mmokta import okta as okta

from minemeld.ft.actorbase import ActorBaseFT
import minemeld.ft.base as base

LOG = logging.getLogger(__name__)

# Okta Output Node for MineMeld
class OktaOutput(ActorBaseFT):
    def configure(self):
        super(IPSOutput, self).configure()

        # Okta Endpoint Configuration
        self.oktatarget = {
            'addr' : self.config.get('okta_base_url', None),
            'token' : self.config.get('okta_token', None),
        }

        # Okta Group name (not ID) to assign users to
        self.quarantine_group = self.config.get('quarantine_group', None)

    @base._counting('update.processed')
    def filtered_update(self, source=None, indicator=None, value=None):
        # TODO: change this to 'User-ID' when available
        if(value['type'] == 'domain'):
            okta.lookup_and_add(self.oktatarget, [indicator], self.quarantine_group)

    @base._counting('withdraw.processed')
    def filtered_withdraw(self, source=None, indicator=None, value=None):
        # TODO: change this to 'User-ID' when available
        if(value['type'] == 'domain'):
            okta.lookup_and_remove(self.oktatarget, [indicator], self.quarantine_group)
