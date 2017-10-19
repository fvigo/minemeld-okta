
console.log('Loading Okta WebUI');

(function() {

function OKTASideConfigController($scope, MinemeldConfigService, MineMeldRunningConfigStatusService,
                                  toastr, $modal, ConfirmService, $timeout) {
    var vm = this;

    // side config settings
    vm.okta_token = undefined;
    vm.okta_base_url = undefined;

    vm.quarantine_group = undefined;
    vm.suspend_user = undefined;
    vm.unsuspend_user = undefined;
    vm.clear_user_sessions = undefined;

    vm.loadSideConfig = function() {
        var nodename = $scope.$parent.vm.nodename;

        MinemeldConfigService.getDataFile(nodename + '_side_config')
        .then((result) => {
            if (!result) {
                return;
            }

            if (result.okta_token) {
                vm.okta_token = result.okta_token;
            } else {
                vm.okta_token = undefined;
            }

            if (result.okta_base_url) {
                vm.okta_base_url = result.okta_base_url;
            } else {
                vm.okta_base_url = undefined;
            }

            if (result.quarantine_group) {
                vm.quarantine_group = result.quarantine_group;
            } else {
                vm.quarantine_group = undefined;
            }

            if (typeof result.suspend_user !== 'undefined') {
                vm.suspend_user = result.suspend_user;
            } else {
                vm.suspend_user = undefined;
            }

            if (typeof result.unsuspend_user !== 'undefined') {
                vm.unsuspend_user = result.unsuspend_user;
            } else {
                vm.unsuspend_user = undefined;
            }

            if (typeof result.clear_user_sessions !== 'undefined') {
                vm.clear_user_sessions = result.clear_user_sessions;
            } else {
                vm.clear_user_sessions = undefined;
            }

        }, (error) => {
            toastr.error('ERROR RETRIEVING NODE SIDE CONFIG: ' + error.status);
            vm.okta_token = undefined;
            vm.okta_base_url = undefined;
            vm.quarantine_group = undefined;
            vm.suspend_user = undefined;
            vm.unsuspend_user = undefined;
            vm.clear_user_sessions = undefined;
        })
        .finally();
    };

    vm.saveSideConfig = function() {
        var side_config = {};
        var nodename = $scope.$parent.vm.nodename;

        if (vm.okta_token) {
            side_config.okta_token = vm.okta_token;
        }

        if (vm.okta_base_url) {
            side_config.okta_base_url = vm.okta_base_url;
        }

        if (vm.quarantine_group) {
            side_config.quarantine_group = vm.quarantine_group;
        }

        if (typeof vm.suspend_user !== 'undefined') {
            side_config.suspend_user = vm.suspend_user;
        }

        if (typeof vm.unsuspend_user !== 'undefined') {
            side_config.unsuspend_user = vm.unsuspend_user;
        }

        if (typeof vm.clear_user_sessions !== 'undefined') {
            side_config.clear_user_sessions = vm.clear_user_sessions;
        }

        return MinemeldConfigService.saveDataFile(
            nodename + '_side_config',
            side_config,
            nodename
        );
    };

    vm.setOktaToken = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/mmoktaWebui/okta.output.key.html',
            controller: ['$modalInstance', OKTAAuthTokenController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.okta_token = result.okta_token;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('AUTOMATION KEY SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING AUTOMATION KEY: ' + error.statusText);
        });
    };

   vm.setBaseUrl = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/mmoktaWebui/okta.output.baseurl.html',
            controller: ['$modalInstance', OKTABaseUrlController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.okta_base_url = result.okta_base_url;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('BASE URL SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING BASE URL: ' + error.statusText);
        });
    };

   vm.setQuarantineGroup = function() {

        var mi = $modal.open({
            templateUrl: '/extensions/webui/mmoktaWebui/okta.output.quarantinegroup.html',
            controller: ['$modalInstance', OKTAQuarantineGroupController],
            controllerAs: 'vm',
            bindToController: true,
            backdrop: 'static',
            animation: false
        });

        mi.result.then((result) => {
            vm.quarantine_group = result.quarantine_group;

            return vm.saveSideConfig();
        })
        .then((result) => {
            toastr.success('QUARANTINE GROUP SET');
            vm.loadSideConfig();
        }, (error) => {
            toastr.error('ERROR SETTING QUARANTINE GROUP: ' + error.statusText);
        });
    };

    vm.toggleSuspendUser = function() {
        var p, new_value;

        if (typeof this.suspend_user === 'undefined' || !this.suspend_user) {
            new_value = true;
            p = ConfirmService.show(
                'SUSPEND OKTA USER',
                'Suspend OKTA User when an indicator is added ?'
            );
        } else {
            new_value = false;
            p = ConfirmService.show(
                'SUSPEND OKTA USER',
                'Do not suspend OKTA User when an indicator is added ?'
            );
        }

        p.then((result) => {
            vm.suspend_user = new_value;

            return vm.saveSideConfig().then((result) => {
                toastr.success('SUSPEND OKTA USER TOGGLED');
                vm.loadSideConfig();
            }, (error) => {
                toastr.error('ERROR TOGGLING SUSPEND OKTA USER: ' + error.statusText);
            });
        });
    };

    vm.toggleUnsuspendUser = function() {
        var p, new_value;

        if (typeof this.unsuspend_user === 'undefined' || !this.unsuspend_user) {
            new_value = true;
            p = ConfirmService.show(
                'UNSUSPEND OKTA USER',
                'Unsuspend OKTA User when an indicator is withdrawn ?'
            );
        } else {
            new_value = false;
            p = ConfirmService.show(
                'UNSUSPEND OKTA USER',
                'Do not unsuspend OKTA User when an indicator is withdrawn ?'
            );
        }

        p.then((result) => {
            vm.unsuspend_user = new_value;

            return vm.saveSideConfig().then((result) => {
                toastr.success('UNSUSPEND OKTA USER TOGGLED');
                vm.loadSideConfig();
            }, (error) => {
                toastr.error('ERROR TOGGLING UNSUSPEND OKTA USER: ' + error.statusText);
            });
        });
    };

    vm.toggleClearUserSessions = function() {
        var p, new_value;

        if (typeof this.clear_user_sessions === 'undefined' || !this.clear_user_sessions) {
            new_value = true;
            p = ConfirmService.show(
                'CLEAR OKTA USER SESSIONS',
                'Clear OKTA User Sessions when an indicator is found ?'
            );
        } else {
            new_value = false;
            p = ConfirmService.show(
                'CLEAR OKTA USER SESSIONS',
                'Do not clear OKTA User Sessions when an indicator is found ?'
            );
        }

        p.then((result) => {
            vm.clear_user_sessions = new_value;

            return vm.saveSideConfig().then((result) => {
                toastr.success('CLEAR OKTA USER SESSIONS TOGGLED');
                vm.loadSideConfig();
            }, (error) => {
                toastr.error('ERROR TOGGLING CLEAR OKTA USER SESSIONS: ' + error.statusText);
            });
        });
    };

    vm.loadSideConfig();
}

function OKTAAuthTokenController($modalInstance) {
    var vm = this;

    vm.okta_token = undefined;
    vm.okta_token2 = undefined;

    vm.valid = function() {
        if (vm.okta_token !== vm.okta_token2) {
            angular.element('#fgOktaToken1').addClass('has-error');
            angular.element('#fgOktaToken2').addClass('has-error');

            return false;
        }
        angular.element('#fgOktaToken1').removeClass('has-error');
        angular.element('#fgOktaToken2').removeClass('has-error');

        if (!vm.okta_token) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.okta_token = vm.okta_token2;

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

function OKTABaseUrlController($modalInstance) {
    var vm = this;

    vm.okta_base_url = undefined;
    
    vm.valid = function() {
        if (!vm.okta_base_url) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.okta_base_url = vm.okta_base_url

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

function OKTAQuarantineGroupController($modalInstance) {
    var vm = this;

    vm.quarantine_group = undefined;
    
    vm.valid = function() {
        if (!vm.quarantine_group) {
            return false;
        }

        return true;
    };

    vm.save = function() {
        var result = {};

        result.quarantine_group = vm.quarantine_group

        $modalInstance.close(result);
    }

    vm.cancel = function() {
        $modalInstance.dismiss();
    }
}

angular.module('mmoktaWebui', [])
    .controller('OKTASideConfigController', [
        '$scope', 'MinemeldConfigService', 'MineMeldRunningConfigStatusService',
        'toastr', '$modal', 'ConfirmService', '$timeout',
        OKTASideConfigController
    ])
    .config(['$stateProvider', function($stateProvider) {
        $stateProvider.state('nodedetail.oktainfo', {
            templateUrl: '/extensions/webui/mmoktaWebui/okta.output.info.html',
            controller: 'NodeDetailInfoController',
            controllerAs: 'vm'
        });
    }])
    .run(['NodeDetailResolver', '$state', function(NodeDetailResolver, $state) {
        NodeDetailResolver.registerClass('mmokta.node.OktaOutput', {
            tabs: [{
                icon: 'fa fa-circle-o',
                tooltip: 'INFO',
                state: 'nodedetail.oktainfo',
                active: false
            },
            {
                icon: 'fa fa-area-chart',
                tooltip: 'STATS',
                state: 'nodedetail.stats',
                active: false
            },
            {
                icon: 'fa fa-asterisk',
                tooltip: 'GRAPH',
                state: 'nodedetail.graph',
                active: false
            }]
        });

        // if a nodedetail is already shown, reload the current state to apply changes
        // we should definitely find a better way to handle this...
        if ($state.$current.toString().startsWith('nodedetail.')) {
            $state.reload();
        }
    }]);
})();
