angular.module('app.base').config(appConfig);

appConfig.$inject = ['$stateProvider'];
function appConfig($stateProvider) {
    $stateProvider.state('base', {
        controller: BaseController,
        ncyBreadcrumb: {
            label: 'Lily',
        },
    });
}

angular.module('app.base').controller('BaseController', BaseController);

BaseController.$inject = ['$scope', '$state', 'Settings', 'Notifications', 'HLShortcuts'];
function BaseController($scope, $state, Settings, Notifications, HLShortcuts) {
    // Make sure the settings are available everywhere.
    $scope.settings = Settings;

    $scope.loadNotifications = loadNotifications;

    activate();

    //////////

    function activate() {
        $scope.$on('$stateChangeStart', function() {
            new window.Intercom('update', {email: currentUser.email});
        });

        $scope.$on('$stateChangeSuccess', _setPreviousState);
        $scope.$on('$viewContentLoaded', _contentLoadedActions);

        $scope.$on('$stateChangeError', _handleResolveErrors);
    }

    function loadNotifications() {
        Notifications.query(function(notifications) {  // On success
            angular.forEach(notifications, function(message) {
                toastr[message.level](message.message);
            });
        }, function(error) {  // On error
            toastr.error(error, 'Couldn\'t load notifications');
        });
    }

    function _setPreviousState(event, toState, toParams, fromState, fromParams) {
        var previousInbox;

        $scope.previousState = $state.href(fromState, fromParams);
        Settings.page.previousState = {state: fromState, params: fromParams};

        if (fromState.name === 'base.email.list' || fromState.name === 'base.email.accountList') {
            previousInbox = {
                state: fromState.name,
                params: fromParams,
            };

            Settings.email.setPreviousInbox(previousInbox);
        }

        if (Settings.email.sidebar && fromState && fromState.name === 'base.email.detail') {
            Settings.email.resetEmailSettings();

            $scope.$$phase || $scope.apply();
        }

        Settings.page.toolbar.data = null;

        // For some reason we need to do two update calls to display messages
        // when they should.
        new window.Intercom('update', {email: currentUser.email});
    }

    function _contentLoadedActions() {
        Metronic.unblockUI();
        Metronic.initComponents(); // init core components
        HLSelect2.init();
        HLFormsets.init();
        HLShowAndHide.init();
        autosize($('textarea'));

        $scope.loadNotifications();
        $scope.toolbar = Settings.page.toolbar.data;
    }

    function _handleResolveErrors(event, toState, toParams, fromState, fromParams, error) {
        switch (error.status) {
            case 404:
                $state.go('base.404');
                break;
            default:
                // With JS errors, error isn't an object, but still the default case gets called.
                $state.go('base.500');
        }
    }
}
