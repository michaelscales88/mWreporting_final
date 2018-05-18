function configReportPage(start_time, end_time) {

    function ajaxFn() {
        return {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            task: "sla_report",
            clients: JSON.stringify($("#report-select").multipleSelect("getSelects"))
        };
    }

    $.getScript("/static/js/dt-selector.js", function () {
        let pickerConfig = {
            start_time: start_time,
            end_time: end_time
        };
        dtSelector('#start-selector', '#end-selector', pickerConfig);
    });

    $.getScript("/static/js/grid-area.js", function () {
        // configure DataTable
        let tableConfig = {
            api: "/api/sla-report",
            table_name: 'table#displayTable',
            num_rows: -1
        };

        let table = getGridArea(ajaxFn, tableConfig, "GET");
        $('button#refreshButton').on('click', function() { table.ajax.reload(); });

        $.get("/api/sla-report").done(function (data, textStatus) {
            let respData = data.data;
            if (textStatus === 'success' && respData && respData.length > 0) {
                toastr.success("Selection loaded.");
            } else {
                toastr.info("Could not retrieve table data.");
            }
        });
    });
}