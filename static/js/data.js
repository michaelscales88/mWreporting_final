function configDataPage(api, start_time, end_time, num_rows, ajaxFn, method="PUT") {

    // dateTimePicker for dtSelectStart & dtSelectEnd
    $.getScript("/static/js/dtSelector.js", function () {
        let pickerConfig = {
            start_time: start_time,
            end_time: end_time
        };
        dtSelector('#start-selector', '#end-selector', pickerConfig);
    });

    // configure the data grid
    $.getScript("/static/js/dataTable.js", function () {
        let tableConfig = {
            api: api,
            table_name: 'table#displayTable',
            num_rows: num_rows
        };

        let table = getDataTable(ajaxFn, tableConfig, method);
        $('button#refreshButton').on('click', function() {
            console.log("clicked refresh");
            table.ajax.reload()
        });
    });
}