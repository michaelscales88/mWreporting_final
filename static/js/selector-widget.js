function loadMultiSelect(api, selector) {
    // Run code
    let multiSelect = $(selector).multipleSelect({
        width: '100%'
    });

    $("button#checkAllBtn").on("click", multiSelect.multipleSelect("checkAll"));

    $("button#uncheckAllBtn").on("click", multiSelect.multipleSelect("uncheckAll"));

    $.ajax({
        url: api,
        type: 'GET',
        contentType: 'application/x-www-form-urlencoded',
        success: function (data, textStatus, jqxhr) {
            if (textStatus === 'success') {
                let options = '';
                let option_info = data.data;
                console.log(option_info);
                for (let i = 0; i < option_info.length; i++) {
                    options += '<option selected value="' + option_info[i] + '">' +
                        option_info[i]
                        + '</option>';
                }
                multiSelect.html(options);
                multiSelect.multipleSelect("refresh");
            }
        }
    });
}