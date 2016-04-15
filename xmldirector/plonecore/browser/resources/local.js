$(document).ready(function() {

    var plone5 = $('[data-bundle="plone-legacy"]').length > 0;
    if (plone5) {
//        ace.config.set("basePath", $('body').attr('data-portal-url') + '/++resource++xmldirector.plonecore/ace-builds/src-min');
    }

    var editors = [];
    var num_editors = 0;

    init_ace_editors('.template-view .xmltext-field');
    init_ace_editors('textarea.xmltext-field');


    // Test connection button for XML Director controlpanel
    var button = $('.template-xmldirector-core-settings #form-buttons-save');
    if (button.length > 0) {

        $.ajax('xmldirector-settings-json', {
            success: function(settings) {

                var settings = $.parseJSON(settings); 

                var button2 = button.clone();
                var cancel_button = $('#form-buttons-cancel');
                button2.attr('value', 'Test connection');
                button2.attr('name', 'form-button-test-connection');
                button2.attr('id', 'form-button-test-connection');
                button2.attr('type', 'button');
                button2.attr('style', 'margin-left: 1em');
                button2.insertAfter(cancel_button);
                button2.on('click', function() {
                    window.location.href = '@@xmldirector-connection-test'; 
                });

                if (settings['connector_mode'] == 'existdb') {
                    var button3 = button.clone();
                    button3.attr('value', 'Install Exist-DB scripts');
                    button3.attr('name', 'form-button-install-scripts');
                    button3.attr('id', 'form-button-install-scripts');
                    button3.attr('type', 'button');
                    button3.attr('style', 'margin-left: 1em');
                    button3.insertAfter(button2);
                    button3.on('click', function() {
                        window.location.href = '@@xmldirector-install-scripts'; 
                    });
                }
            }
        })
    }            


});

