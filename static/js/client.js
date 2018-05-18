function configClientPage() {

    // configure DataTable
    function ajaxFn() {
        return {
            task: "GET"
        }
    }
    let tableConfig = {
        api: "/api/client",
        table_name: "table#displayTable",
        num_rows: 50
    };

    let table = getGridArea(ajaxFn, tableConfig);
    $('button#refreshTableButton').on('click', function () { table.ajax.reload() });
}