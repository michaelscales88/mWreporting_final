function getDataTable(ajaxFn, config) {
    return $(config['tableName']).DataTable({
        processing: true,
        pageLength: config['gridLength'],
        ajax: {
            url: config['api'],
            data: ajaxFn,
        },
        dom: '<<B>lf<t>ip>',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        scrollX: true
    });
}