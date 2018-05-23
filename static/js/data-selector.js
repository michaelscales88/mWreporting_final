function loadDataSelect() {
    let $multiSelect = $("select#data-select").multipleSelect({
        width: '100%',
        single: true,
        placeholder: "Select a data table"
    });

    $multiSelect.multipleSelect('disable');

    $("button#checkAllBtn").on("click", $multiSelect.multipleSelect("checkAll"));

    $("button#uncheckAllBtn").on("click", $multiSelect.multipleSelect("uncheckAll"));

    $.ajax({
        url: "/api/data",
        success: function (data, status) {
            if (status === 'success') {
                let option_info = data.data;
                if (option_info.length > 0) {
                    $multiSelect.empty();
                    // Enable if we have options
                    $.each(option_info, function () {
                        $multiSelect.append($("<option></option>").val(this).html(' ' + this));
                    });
                    $multiSelect.select(0);
                    $multiSelect[0].selectedIndex = 0;
                }
                $multiSelect.multipleSelect("refresh");
                $multiSelect.multipleSelect('enable');
                console.log("set first option selected");
            }
        }
    });
}