function configDataPage(api, start_time, end_time, num_rows) {

    function ajaxFn() {
        return {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            task: "GET",
            tables: JSON.stringify($("#data-select").multipleSelect("getSelects"))
        }
    }

    // dateTimePicker for dtSelectStart & dtSelectEnd
    $.getScript("/static/js/dt-selector.js", function () {
        let pickerConfig = {
            start_time: start_time,
            end_time: end_time
        };
        dtSelector('#start-selector', '#end-selector', pickerConfig);
    });

    // configure the data grid
    $.getScript("/static/js/data-table.js", function () {
        let tableConfig = {
            api: api,
            table_name: 'table#displayTable',
            num_rows: num_rows
        };

        let table = getDataTable(ajaxFn, tableConfig, "PUT");
        $('button#refreshButton').on('click', function () {
            console.log("clicked refresh");
            table.ajax.reload()
        });

        $('button#loadButton').on('click', function () {
            console.log("clicked load");
            $.ajax({
                url: api,
                data: {
                    start_time: $("input#start-selector").val(),
                    end_time: $("input#end-selector").val(),
                    task: "LOAD",
                    tables: JSON.stringify($("#data-select").multipleSelect("getSelects"))
                },
                method: "PUT"
            });
            table.ajax.reload();
        });
    });
}