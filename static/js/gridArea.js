function getTableDiv(ajaxFn, api) {
    return $.ajax({
        url: api,
        success: function (json) {
            let $tableDiv = $("#tableDiv");
            let $table = '<table id="displayTable" class="table table-striped table-bordered" ' +
                '       cellspacing="0" width="100%" data-toggle="tooltip" data-placement="top" ' +
                '       title="Scroll left or right to see more information."><thead><tr>' +
                '       </tr></thead></table>';

            $tableDiv.empty();
            $tableDiv.append($table);
            let $table2 = '<table id="displayTable2" class="table table-striped table-bordered" ' +
                '       cellspacing="0" width="100%" data-toggle="tooltip" data-placement="top" ' +
                '       title="Scroll left or right to see more information."><thead><tr>' +
                '       </tr></thead></table>';

            $tableDiv.append($table2);
            $.each(json.columns, function (i, val) {
                $('#displayTable thead tr').append("<th>" + val + "</th>")
                $('#displayTable2 thead tr').append("<th>" + val + "</th>")
            });

            $('table.table').DataTable({
                processing: true,
                paging: false,
                pageLength: -1,
                dom: '<<B>lf<t>ip>',
                buttons: [
                    'copy', 'csv', 'excel', 'pdf', 'print'
                ],
                scrollX: true,
                scrollY: 400,
                scrollCollapse: true,
                data: json
            });

            // Apply a search to the second table for the demo
            $('#displayTable2').DataTable().search( '22' ).draw();
        },
        dataType: "json",
        method: "POST"
    });
}
