angular.module 'v.controllers.index', []

.controller 'IndexController', ['$scope', '$injector', ($scope, $injector) ->
    $v = $injector.get '$v'
    $state = $injector.get '$state'

    if $v.user.is_login
        $state.go 'v.applications'
    else
        $stae.go 'v.login'
]