function configReportPage(api, start_time, end_time, num_rows, task) {

    function ajaxFn() {
        return {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            task: task,
            clients: JSON.stringify($("#report-select").multipleSelect("getSelects"))
        };
    }

    $("button#loadButton").on("click", function () {
        $.ajax({
            method: "PUT",
            url: api,
            data: ajaxFn
        });
    });

    $.getScript("/static/js/dt-selector.js", function () {
        let pickerConfig = {
            start_time: start_time,
            end_time: end_time
        };
        dtSelector('#start-selector', '#end-selector', pickerConfig);
    });

    $.getScript("/static/js/data-table.js", function () {
        // configure DataTable
        let tableConfig = {
            api: api,
            table_name: 'table#displayTable',
            num_rows: num_rows
        };

        let table = getDataTable(ajaxFn, tableConfig, "PUT");
        $('button#refreshButton').on('click', table.ajax.reload());
    });
}