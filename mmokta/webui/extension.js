
console.log('Loading Okta WebUI');

(function() {

function OKTASideConfigController($scope, MinemeldConfigService, MineMeldRunningConfigStatusService,
                                  toastr, $modal, ConfirmService, $timeout) {
    var vm = this;

    // side config settings
    vm.okta_token = undefined;
    vm.okta_base_url = undefined;

    vm.quarantine_group = undefined;

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

            if (resul.okta_base_url) {
                vm.okta_base_url = result.okta_base_url;
            } else {
                vm.okta_base_url = undefined;
            }

            if (resul.quarantine_group) {
                vm.quarantine_group = result.quarantine_group;
            } else {
                vm.quarantine_group = undefined;
            }
        }, (error) => {
            toastr.error('ERROR RETRIEVING NODE SIDE CONFIG: ' + error.status);
            vm.okta_token = undefined;
            vm.okta_base_url = undefined;
            vm.quarantine_group = undefined;
        })
        .finally();
    };

    vm.saveSideConfig = function() {
        var side_config = {};
        var hup_node = undefined;
        var nodename = $scope.$parent.vm.nodename;

        if (vm.okta_token) {
            side_config.okta_token = vm.okta_token;
        }

        if (vm.okta_base_url) {
            side_config.okta_base_url = vm.okta_base_url;
        }

        if (vm.okta_base_url) {
            side_config.quarantine_group = vm.quarantine_group;
        }

        return MinemeldConfigService.saveDataFile(
            nodename + '_side_config',
            side_config
        );
    };

    vm.setOktaToken = function() {
        var mi = $modal.open({
            templateUrl: '/extensions/webui/mmoktaWebui/okta.output.key.html',
            controller: ['$modalInstance', OKTAAutomationKeyController],
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