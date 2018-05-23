function configDataPage(start_time, end_time) {

    function ajaxFn() {
        return {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            table: $("#data-select").multipleSelect("getSelects")[0]
        };
    }

    // dateTimePicker for dtSelectStart & dtSelectEnd
    dtSelector(
        'input#start-selector', 'input#end-selector',
        { start_time: start_time, end_time: end_time})
    ;

    // configure the data grid
    let $table = getGridArea(
        ajaxFn, { api: "/api/data", table_name: 'table#displayTable', num_rows: 50 }, "PUT"
    );
    $('button#refreshTableButton').on('click', function () {$table.ajax.reload()});

    $('button#loadButton').on('click', function () {
        $.ajax({
            url: "/api/data",
            data: {
                start_time: $("input#start-selector").val(),
                end_time: $("input#end-selector").val(),
                task: "LOAD",
            },
            method: "PUT",
            success: function (data, textStatus) {
                if (textStatus === 'success') $table.ajax.reload();
            }
        }).done(function (data, textStatus) {
            if (textStatus === 'success' && $table.data().length > 0) {
                toastr.success("Selection loaded.");
            } else {
                toastr.info("Could not retrieve table data.");
            }
        });
    });
}