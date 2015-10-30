angular.module('app.dashboard').controller('WidgetSettingsModal', WidgetSettingsModalController);

WidgetSettingsModalController.$inject = ['$uibModalInstance', 'LocalStorage'];
function WidgetSettingsModalController($uibModalInstance, LocalStorage) {
    var vm = this;
    var storage = LocalStorage('');

    vm.widgetSettings = storage.get('widgetInfo', {});
    vm.notificationSettings = storage.get('notificationSettings', {
        enabled: false,
        openOnClick: false,
        sound: false,
    });

    vm.saveModal = saveModal;
    vm.closeModal = closeModal;

    ////////////

    function saveModal() {
        // Store the widget settings
        storage.put('widgetInfo', vm.widgetSettings);
        storage.put('notificationSettings', vm.notificationSettings);

        $uibModalInstance.close();
    }

    function closeModal() {
        $uibModalInstance.dismiss();
    }
}
