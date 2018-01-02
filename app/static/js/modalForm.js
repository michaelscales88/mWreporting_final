class ModalForm {
    constructor(config) {
        this.form = config['form'];
        this.api = config['api'];
        this.scb = config['successTrigger'];
        this.ecb = config['successCB'];
    }

    process(){
        let button = this.scb;
        $.ajax({
            url: this.api,
            type: 'PUT',
            contentType: 'application/x-www-form-urlencoded',
            data: $(this.form).serialize(),
            success: function( data, textStatus, jqxhr ) {
                if (parseInt(textStatus) === 200) {
                    $(button).trigger( "click" );
                }
            }
        });
    }

    submit(event) {
        // bind the action to the form task
        $(this.form).find("input[name=task]").val(event.action);
        this.process();
    }
}


function getModalForm(modalConfig) {
    return new ModalForm(modalConfig);
}