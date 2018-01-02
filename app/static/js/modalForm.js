class ModalForm {
    constructor(config) {
        this.form = config['formName'];
        this.api = config['api'];
    }

    process(){
        $.ajax({
            url: this.api,
            type: 'PUT',
            contentType: 'application/x-www-form-urlencoded',
            data: $(this.form).serialize()
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