function loadReportSelect() {
    let $multiSelect = $("select#report-select").multipleSelect({
        width: '100%',
        placeholder: "Select the clients for the report"
    });
    $multiSelect.multipleSelect('disable');
    $("button#checkAllBtn").on("click", $multiSelect.multipleSelect("checkAll"));
    $("button#uncheckAllBtn").on("click", $multiSelect.multipleSelect("uncheckAll"));

    // Populate the select box
    $.ajax({
        url: "/api/client",
        success: function (data, status) {
            if (status === 'success') {
                let allClients = data.data;
                if (allClients.length > 0) {
                    $multiSelect.empty();
                    $.each(allClients, function () {
                        $multiSelect.append(
                            $("<option></option>").val(this[2]).html(' ' + this[1] + ' (' + this[2] + ')')
                        );
                    });
                    $multiSelect.multipleSelect("refresh");
                }
            } // End /api/client Success
        }
    });

    // After the select box is populated -> select the current users options or all
    $.get("/api/user").done(function() {
        // Ajax success
        $multiSelect.multipleSelect("enable");
        $.ajax({
            url: "/api/user",
            success: function (data, status) {
                if (status === 'success') {
                    let myClients = data.data;
                    console.log("hit user success");
                    if (myClients && myClients.hasOwnProperty("length") && myClients.length > 0) {
                        console.log("setting clients");
                        let selectValues = [];
                        $.each(myClients, function () { selectValues.push(this['ext']); });
                        $multiSelect.val(selectValues);
                        console.log("set values");
                        $multiSelect.multipleSelect("refresh");
                    } else $("select#report-select").multipleSelect("checkAll");
                } else $("select#report-select").multipleSelect("checkAll");
            }
        });
    });
}