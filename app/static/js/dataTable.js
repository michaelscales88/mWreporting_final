function getDataTable(startName, endName, config) {
    function ajax_data() {
        return {
            start_time: $(startName).val(),
            end_time: $(endName).val(),
            task: 'get'
        };
    }

    return $(config['tableName']).DataTable({
        processing: true,
        pageLength: 50,
        ajax: {
            url: config['api'],
            data: ajax_data,
        },
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ]
    });
}
