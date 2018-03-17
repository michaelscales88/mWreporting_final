function configClientPage(api, num_rows, ajaxFn) {

    // configure DataTable
    $.getScript("/static/js/data-table.js", function () {
        let tableConfig = {
            api: api,
            table_name: 'table#displayTable',
            num_rows: num_rows
        };

        let table = getDataTable(ajaxFn, tableConfig);
        $('button#refreshButton').on('click', table.ajax.reload());
    });
}