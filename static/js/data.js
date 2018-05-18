function configDataPage(start_time, end_time) {

    function ajaxFn() {
        return {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            task: "GET",
            table: JSON.stringify($("select#data-select").multipleSelect("getSelects")[0])
        }
    }

    // dateTimePicker for dtSelectStart & dtSelectEnd
    let pickerConfig = {
        start_time: start_time,
        end_time: end_time
    };
    dtSelector('#start-selector', '#end-selector', pickerConfig);

    // configure the data grid
    let tableConfig = {
        api: "/api/data",
        table_name: 'table#displayTable',
        num_rows: 50
    };

    let $table = getGridArea(ajaxFn, tableConfig, "PUT");
    $('button#refreshTableButton').on('click', function () { $table.ajax.reload()});

    $('button#loadButton').on('click', function () {
        $.ajax({
            url: "/api/data",
            data: {
                start_time: $("input#start-selector").val(),
                end_time: $("input#end-selector").val(),
                task: "LOAD"
            },
            method: "PUT",
            success: function (resp, status) {
                if (status === 'success') {
                    $table.ajax.reload();
                }
            }
        });
    });

    $.get("/api/data").done(function () {
        if ($("table#displayTable").data().length > 0 ) {
            toastr.success("Selection loaded.");
        } else toastr.info("Could not retrieve table data.");
    });
}