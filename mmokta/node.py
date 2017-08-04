import logging
import json
from mmokta import okta as okta

from minemeld.ft.actorbase import ActorBaseFT
import minemeld.ft.base as base

LOG = logging.getLogger(__name__)

# Okta Output Node for MineMeld
class OktaOutput(ActorBaseFT):
    def configure(self):
        super(OktaOutput, self).configure()
        
        # Load Side Config
        self.side_config_path = self.config.get('side_config', None)
        if self.side_config_path is None:
            self.side_config_path = os.path.join(
                os.environ['MM_CONFIG_DIR'],
                '%s_side_config.yml' % self.name
            )

        self._load_side_config()

        # Okta Endpoint Configuration
        self.oktatarget = {
            'addr' : sconfig.get('okta_base_url', None),
            'token' : sconfig.get('okta_token', None),
        }

        # Okta Group name (not ID) to assign users to
        self.quarantine_group = sconfig.get('quarantine_group', None)

    def _load_side_config(self):
        try:
            with open(self.side_config_path, 'r') as f:
                sconfig = yaml.safe_load(f)

        except Exception as e:
            LOG.error('%s - Error loading side config: %s', self.name, str(e))
            return

    def hup(self, source=None):
        LOG.info('%s - hup received, reload side config', self.name)
        self._load_side_config()
        super(Miner, self).hup(source)

    @base._counting('update.processed')
    def filtered_update(self, source=None, indicator=None, value=None):
        if self.okta_token is None:
            raise RuntimeError('{} - OKTA Auth Token not set'.format(self.name))

       if self.okta_base_url is None:
            raise RuntimeError('{} - OKTA Base URL not set'.format(self.name))

       if self.quarantine_group is None:
            raise RuntimeError('{} - Quarantine Group not set'.format(self.name))

        if(value['type'] == 'user-id'):
            okta.lookup_and_add(self.oktatarget, indicator, self.quarantine_group)

    @base._counting('withdraw.processed')
    def filtered_withdraw(self, source=None, indicator=None, value=None):
       if self.okta_token is None:
            raise RuntimeError('{} - OKTA Auth Token not set'.format(self.name))

       if self.okta_base_url is None:
            raise RuntimeError('{} - OKTA Base URL not set'.format(self.name))

       if self.quarantine_group is None:
            raise RuntimeError('{} - Quarantine Group not set'.format(self.name))

        if(value['type'] == 'user-id'):
            okta.lookup_and_remove(self.oktatarget, indicator, self.quarantine_group)
