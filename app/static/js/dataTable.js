function getDataTable(ajaxFn, config) {
    return $(config['tableName']).DataTable({
        processing: true,
        pageLength: config['gridLength'],
        // sAjaxSource: config['api'],
        // // data: ajaxFn,
        // fnServerData: function (sSource, aoData, fnCallback, oSettings) {
        //     oSettings.jqXHR = $.ajax({
        //         "dataType": 'json',
        //         "type": "GET",
        //         "url": sSource,
        //         "data": aoData,
        //         "success": fnCallback,
        //         "timeout": 15000, // optional if you want to handle timeouts (which you should)
        //         "error": function (xhr, error, thrown) {
        //             alert('something broke');
        //             console.log(xhr);
        //             console.log(error);
        //             console.log(thrown);
        //         }, // this sets up jQuery to give me errors
        //     });
        // },
        ajax: {
            url: config['api'],
            data: ajaxFn,
            // error: function (xhr, error, thrown) {
            //     console.log('something broke');
            // },
        },
        dom: '<<B>lf<t>ip>',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        scrollX: true
    });
}