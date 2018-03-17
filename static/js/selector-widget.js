function loadMultiSelect(api, selector, task) {
    // Run code
    let multiSelect = $(selector).multipleSelect({
        width: '100%'
    });

    $("button#checkAllBtn").click(function () {
        multiSelect.multipleSelect("checkAll");
    });

    $("button#uncheckAllBtn").click(function () {
        multiSelect.multipleSelect("uncheckAll");
    });

    $.ajax({
        url: api,
        type: 'GET',
        contentType: 'application/x-www-form-urlencoded',
        data: {
            task: task
        },
        success: function (data, textStatus, jqxhr) {
            if (textStatus === 'success') {
                let options = '';
                let clientInfo = data.data;
                // console.log(clientInfo);
                // for (let i = 0; i < clientInfo.length; i++) {
                //     options += '<option selected value="' + clientInfo[i][2] + '">' +
                //         clientInfo[i][1]
                //         + '</option>';
                // }
                multiSelect.html(options);
                multiSelect.multipleSelect("refresh");
            }

        }
    });
}