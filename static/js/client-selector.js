let $multiSelect = $("select#client-select").multipleSelect({
    width: '100%',
    placeholder: "Remove multiple clients"
});

$("button#checkAllBtn").on("click", $multiSelect.multipleSelect("checkAll"));
$("button#uncheckAllBtn").on("click", $multiSelect.multipleSelect("uncheckAll"));

function updateSelectOptions() {
    $multiSelect.multipleSelect('disable');
    $.ajax({
        url: "/api/client",
        success: function (data, status) {
            if (status === 'success') {
                let option_info = data.data;
                console.log(option_info);
                if (option_info.length > 0) {
                    $multiSelect.empty();
                    // Enable if we have options
                    $multiSelect.multipleSelect('enable');
                    $.each(option_info, function () {
                        $multiSelect.append(
                            $("<option></option>").val(this[2]).html(' ' + this[1] + ' (' + this[2] + ')')
                        );
                    });
                }
                $multiSelect.multipleSelect("refresh");
            }
        }
    });
}