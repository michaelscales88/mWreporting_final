function dtSelector(first_selector, second_selector, config) {
    let dtStart = $(first_selector).datetimepicker({
        sideBySide: true,
        useCurrent: false,
        toolbarPlacement: "top",
        showClear: true,
        defaultDate: config['start_time'],
        maxDate: moment()
    });
    let dtEnd = $(second_selector).datetimepicker({
        sideBySide: true,
        useCurrent: false, //Important! See issue #1075
        toolbarPlacement: "top",
        showClear: true,
        showTodayButton: true,
        minDate: config['start_time'],
        defaultDate: config['end_time'],
        maxDate: moment()
    });
    dtEnd.on("dp.change", function (e) {
        dtStart.data("DateTimePicker").maxDate(e.date);
    });
    dtStart.on("dp.change", function (e) {
        dtEnd.data("DateTimePicker").minDate(e.date);
    });
}