class ModalForm {
    constructor(config) {
        this.form = config['form'];
        this.api = config['api'];
        this.cb = config['callback'];
    }

    process(){
        let button = this.cb;
        $.ajax({
            url: this.api,
            type: 'PUT',
            contentType: 'application/x-www-form-urlencoded',
            data: $(this.form).serialize(),
            success: function( data, textStatus, jqxhr ) {
                if (textStatus === 'success') {
                    $(button).click();
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