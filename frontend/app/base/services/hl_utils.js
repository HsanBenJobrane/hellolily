angular.module('app.services').service('HLUtils', HLUtils);

function HLUtils() {
    this.formatPhoneNumber = function(phoneNumber) {
        if (!phoneNumber.raw_input || phoneNumber.raw_input.match(/[a-z]/i)) {
            // If letters are found, skip formatting: it may not be a phone field after all
            return false;
        }

        // Format phone number
        var newNumber = phoneNumber.raw_input
            .replace('(0)', '')
            .replace(/\s|\(|\-|\)|\.|\\|\/|\–|x|:|\*/g, '')
            .replace(/^00/, '+');

        if (newNumber.length === 0) {
            return false;
        }

        // Check if it's a mobile phone number
        if (newNumber.match(/^\+31([\(0\)]+)?6|^06/)) {
            // Set phone number type to mobile
            phoneNumber.type = 'mobile';
        }

        if (!newNumber.startsWith('+')) {
            if (newNumber.startsWith('0')) {
                newNumber = newNumber.substring(1);
            }

            newNumber = '+31' + newNumber;
        }

        if (newNumber.startsWith('+310')) {
            newNumber = '+31' + newNumber.substring(4);
        }

        phoneNumber.raw_input = newNumber;

        return phoneNumber;
    };
}