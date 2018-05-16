function configDataPage(start_time, end_time) {

    function ajaxFn() {
        return {
            start_time: $("input#start-selector").val(),
            end_time: $("input#end-selector").val(),
            task: "GET",
            tables: JSON.stringify($("select#data-select").multipleSelect("getSelects"))
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
    $.getScript("/static/js/grid-area.js", function () {
        let tableConfig = {
            api: "/api/data",
            table_name: 'table#displayTable',
            num_rows: 50
        };

        let table = getGridArea(ajaxFn, tableConfig, "PUT");
        $('button#refreshTableButton').on('click', function () { table.ajax.reload()});

        $('button#loadButton').on('click', function () {
            $.ajax({
                url: "/api/data",
                data: {
                    start_time: $("input#start-selector").val(),
                    end_time: $("input#end-selector").val(),
                    task: "LOAD",
                    tables: JSON.stringify($("select#data-select").multipleSelect("getSelects"))
                },
                method: "PUT"
            });
            table.ajax.reload();
        });
    });
}