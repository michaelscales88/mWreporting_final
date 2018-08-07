function getGridArea(ajaxFn, config, method) {
    return $(config['table_name']).DataTable({
        processing: true,
        pageLength: config['num_rows'],
        ajax: {
            url: config['api'],
            data: ajaxFn,
            method: method
        },
        columns: [
            { title: "Client" },
            { title: "I/C Presented" },
            { title: "I/C Answered" },
            { title: "I/C Lost" },
            { title: "Voice Mails" },
            { title: "Incoming Live Answered (%)" },
            { title: "Incoming Received (%)" },
            { title: "Incoming Abandoned (%)" },
            // { title: "Answered Incoming Duration" },
            // { title: "Average Wait Answered" },
            // { title: "Average Wait Lost" },
            { title: "Calls Ans Within 15" },
            { title: "Calls Ans Within 30" },
            { title: "Calls Ans Within 45" },
            { title: "Calls Ans Within 60" },
            { title: "Calls Ans Within 999" },
            { title: "Call Ans + 999" },
            { title: "Longest Waiting Answered" },
            // { title: "PCA" }
        ],
        dom: '<<B>lf<t>ip>',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        scrollX: true
    });
}
