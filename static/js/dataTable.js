function getDataTable(ajaxFn, config) {
    return $(config['table_name']).DataTable({
        processing: true,
        pageLength: config['num_rows'],
        ajax: {
            url: config['api'],
            data: ajaxFn
        },
        dom: '<<B>lf<t>ip>',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        scrollX: true
    });
}