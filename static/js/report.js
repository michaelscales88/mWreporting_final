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
            num_rows: 50
        };

        let table = getGridArea(ajaxFn, tableConfig, "PUT");
        $('button#refreshButton').on('click', function() { table.ajax.reload(); });

        $("button#loadButton").on("click", function () {
            $.ajax({
                url: "/api/sla-report",
                data: ajaxFn,
                method: "PUT"
            });
            table.ajax.reload();
        });
    });
}