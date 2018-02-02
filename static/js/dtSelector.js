function dtSelector(startName, endName, config) {
    let dtStart = $(startName).datetimepicker({
        sideBySide: true,
        useCurrent: false,
        toolbarPlacement: "top",
        showClear: true,
        maxDate: config['endTime'],
        defaultDate: config['startTime'],

    });
    let dtEnd = $(endName).datetimepicker({
        sideBySide: true,
        useCurrent: false, //Important! See issue #1075
        toolbarPlacement: "top",
        showClear: true,
        showTodayButton: true,
        minDate: config['startTime'],
        defaultDate: config['endTime'],
    });
    dtEnd.on("dp.change", function (e) {
        dtStart.data("DateTimePicker").maxDate(e.date);
    });
    dtStart.on("dp.change", function (e) {
        dtEnd.data("DateTimePicker").minDate(e.date);
    });
}