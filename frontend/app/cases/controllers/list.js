angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases', {
        url: '/cases',
        views: {
            '@': {
                templateUrl: 'cases/controllers/list.html',
                controller: CaseListController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Cases',
        },
    });
}

angular.module('app.cases').controller('CaseListController', CaseListController);

CaseListController.$inject = ['$location', '$modal', '$scope', '$state', '$timeout', 'Case', 'Cookie', 'HLFilters',
    'UserTeams', '$q'];
function CaseListController($location, $modal, $scope, $state, $timeout, Case, Cookie, HLFilters, UserTeams, $q) {
    var cookie = Cookie('caseList');
    var vm = this;

    vm.openPostponeWidget = Case.openPostponeWidget;

    $scope.conf.pageTitleBig = 'Cases';
    $scope.conf.pageTitleSmall = 'do all your lookin\' here';

    /**
     * table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 60,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: '',  // search query
        order: cookie.get('order', {
            ascending: true,
            column: 'expires',  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            caseId: true,
            client: true,
            subject: true,
            priority: true,
            type: true,
            status: true,
            expires: true,
            created: true,
            assignedTo: true,
            createdBy: true,
            tags: true
        }),
        expiresFilter: cookie.get('expiresFilter', ''),
    };
    vm.displayFilterClear = false;
    vm.filterList = [];

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;
    vm.assignTo = assignTo;

    activate();

    //////

    function activate() {
        // This timeout is needed because by default getting a cookie with Angular has a delay
        $timeout(function() {
            _setSearchQuery();
            _getFilterList();
            _setupWatchers();
        }, 50);
    }

    function _setSearchQuery() {
        // Setup search query
        var searchQuery = '';

        // Check if filter is set as query parameter
        var search = $location.search().search;
        if (search != undefined) {
            searchQuery = search;
        } else {
            // Get searchQuery from cookie
            searchQuery = cookie.get('searchQuery', '');
        }
        vm.table.searchQuery = searchQuery;
    }

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    /**
     * Gets the filter list. Uses a cookie to merge selections.
     *
     * @returns filterList (object): object containing the filter list
     */
    function _getFilterList() {
        var filterListCookie = cookie.get('filterListSelected', null);
        var filterList;
        var teamsCall;
        var casesCall;


        // Use the value from cookie first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (filterListCookie) {
            vm.filterList = filterListCookie;
        }

        // But we still update the list afterwards (in case a filter was changed)
        filterList = [
            {
                name: 'Assigned to me',
                value: 'assigned_to_id:' + $scope.currentUser.id,
                selected: false,
            },
            {
                name: 'Assigned to nobody',
                value: 'NOT(assigned_to_id:*)',
                selected: false,
            },
            {
                name: 'Archived',
                value: '',
                selected: false,
                id: 'archived',
            },
        ];

        teamsCall = UserTeams.mine().$promise.then(function(teams) {
            var myTeamIds = [];
            var filters = [];
            teams.forEach(function(team) {
                myTeamIds.push(team.id);
            });

            filters.push({
                name: 'My teams cases',
                value: 'assigned_to_groups:(' + myTeamIds.join(' OR ') + ')',
                selected: false,
            });

            return filters;
        });

        casesCall = Case.getCaseTypes().then(function(cases) {
            var filters = [];
            angular.forEach(cases, function(caseName, caseId) {
                filters.push({
                    name: 'Case type ' + caseName,
                    value: 'casetype_id:' + caseId,
                    selected: false,
                });
            });
            return filters;
        });

        // Wait for all promises.
        $q.all([teamsCall, casesCall]).then(function(subFilterLists) {
            subFilterLists.forEach(function(subFilterList) {
                subFilterList.forEach(function(filter) {
                    filterList.push(filter);
                });
            });

            if (filterListCookie) {
                // Cookie is set, merge the selections from this cookie.
                angular.forEach(filterListCookie, function(caseInCookie) {
                    angular.forEach(filterList, function(caseInList) {
                        if (caseInCookie.name === caseInList.name) {
                            caseInList.selected = caseInCookie.selected;
                        }
                    });
                });
            }

            // Update filterList once AJAX calls are done.
            vm.filterList = filterList;
            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() sets scope variables to the cookie
     */
    function _updateTableSettings() {
        cookie.put('searchQuery', vm.table.searchQuery);
        cookie.put('archived', vm.table.archived);
        cookie.put('order', vm.table.order);
        cookie.put('visibility', vm.table.visibility);
        cookie.put('filterListSelected', vm.filterList);
    }

    /**
     * _updateCases() reloads the cases through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateCases() {
        Case.getCases(
            vm.table.searchQuery,
            vm.table.page,
            vm.table.pageSize,
            vm.table.order.column,
            vm.table.order.ascending,
            vm.table.archived,
            vm.table.filterQuery
        )
            .then(function(data) {
                vm.table.items = data.cases;
                vm.table.totalItems = data.total;
            }
        );
    }

    function _setupWatchers() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of cases
         */
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.ascending',
            'vm.table.searchQuery',
            'vm.table.archived',
            'vm.table.filterQuery',
        ], function() {
            _updateTableSettings();
            _updateCases();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', function() {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the cookie is loaded,
         * the filterQuery changes and a new set of deals is fetched
         */
        $scope.$watchCollection('vm.filterList', function() {
            updateFilterQuery();
        });

        $scope.$watch('vm.table.expiresFilter', function() {
            updateFilterQuery();
        });
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm);
    }

    function clearFilters() {
        HLFilters.clearFilters(vm);
    }

    function assignTo(myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/assignto.html',
            controller: 'CaseAssignModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase;
                },
            },
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}
