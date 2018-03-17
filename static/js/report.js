function configReportPage(api, start_time, end_time, num_rows, task, ajaxFn) {

    // dateTimePicker for start-selector & end-selector
    $.getScript("/static/js/dtSelector.js", function () {
        let pickerConfig = {
            start_time: start_time,
            end_time: end_time
        };
        dtSelector('#start-selector', '#end-selector', pickerConfig);
    });

    $.getScript("/static/js/dataTable.js", function () {
        // configure DataTable
        let tableConfig = {
            api: api,
            table_name: 'table#displayTable',
            num_rows: num_rows
        };

        let table = getDataTable(ajaxFn, tableConfig);
        $('button#refreshButton').on('click', table.ajax.reload());
    });
}