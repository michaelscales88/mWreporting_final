function getTableDiv(api) {
    return $.ajax({
        url: api,
        data: {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            clients: JSON.stringify($("#report-select").val())
        },
        dataType: "JSON",
        method: "POST",
        success: function (json) {
            let $tableDiv = $("#tableDiv");
            let $table = '<table id="displayTable" class="table table-striped table-bordered" ' +
                '       cellspacing="0" width="100%" data-placement="top" ' +
                '       title="Scroll left or right to see more information."><thead><tr>' +
                '       </tr></thead></table>';

            $tableDiv.empty();
            $tableDiv.append($table);

            $.each(json.columns, function (i, val) {
                $('#displayTable thead tr').append("<th>" + val + "</th>")
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
                data: json.data
            });
        }
    });
}

function initTableDiv(api) {
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        $.fn.dataTable.tables({visible: true, api: true}).columns.adjust();
    });

    console.log("init table div");

    $('table.table').DataTable({
        ajax: {
            url: api,
            data: {
                start_time: $("input#start-selector").val(),
                end_time: $("input#end-selector").val(),
                clients: JSON.stringify($("#report-select").val())
            },
            dataType: "JSON",
            method: "POST",
            success: function (json) {
                let $tableDiv = $("#tableDiv");
                let $table = '<table id="displayTable" class="table table-striped table-bordered" ' +
                    '       cellspacing="0" width="100%" data-placement="top" ' +
                    '       title="Scroll left or right to see more information."><thead><tr>' +
                    '       </tr></thead></table>';

                $tableDiv.empty();
                $tableDiv.append($table);

                $.each(json.columns, function (i, val) {
                    $('#displayTable thead tr').append("<th>" + val + "</th>")
                });
            }
        },
        scrollY: 200,
        scrollCollapse: true,
        paging: false
    });

    // Apply a search to the second table for the demo
    // $('#myTable2').DataTable().search('New York').draw();
    // return $.ajax({
    //     url: api,
    //     data: {
    //         start_time: $("input#start-selector").val(),
    //         end_time: $("input#end-selector").val(),
    //         clients: JSON.stringify($("#report-select").val())
    //     },
    //     dataType: "JSON",
    //     method: "POST",
    //     success: function (json) {
    //         let $tableDiv = $("#tableDiv");
    //         let $table = '<table id="displayTable" class="table table-striped table-bordered" ' +
    //             '       cellspacing="0" width="100%" data-placement="top" ' +
    //             '       title="Scroll left or right to see more information."><thead><tr>' +
    //             '       </tr></thead></table>';
    //
    //         $tableDiv.empty();
    //         $tableDiv.append($table);
    //
    //         $.each(json.columns, function (i, val) {
    //             $('#displayTable thead tr').append("<th>" + val + "</th>")
    //         });
    //
    //         $('table.table').DataTable({
    //             processing: true,
    //             paging: false,
    //             pageLength: -1,
    //             dom: '<<B>lf<t>ip>',
    //             buttons: [
    //                 'copy', 'csv', 'excel', 'pdf', 'print'
    //             ],
    //             scrollX: true,
    //             scrollY: 400,
    //             scrollCollapse: true,
    //             data: json.data
    //         });
    //     }
    // });
}
