function sortOptions(selector) {
    let my_options = $(selector + " option");
    my_options.sort(function (a, b) {
        if (a.text > b.text) return 1;
        else if (a.text < b.text) return -1;
        else return 0;
    });
    $(selector)
        .empty()
        .append(my_options);
}

function initSelectBox(url, select_tag) {
    let $selector = $("select#" + select_tag);
    let otherOpts = "optgroup#all-" + select_tag;
    let selectedOpts = "optgroup#filtered-" + select_tag;
    $selector.addClass("selectpicker");
    $selector.selectpicker({
        size: 4,
        width: "100%",
        actionsBox: true
    });

    $selector.append(
        $('<optgroup></optgroup>')
            .attr("id", "filtered-" + select_tag)
            .attr("label", "Your clients")
    );
    $selector.append('<option data-divider="true"></option>');
    $selector.append(
        $('<optgroup></optgroup>')
            .attr("id", "all-" + select_tag)
            .attr("label", "All clients")
    );
    $.ajax({
        url: url,
        method: "POST",
        success: function (results, textStatus) {
            if (textStatus === 'success') {
                $.each(results.data, function () {
                    $(selectedOpts).append(
                        $("<option></option>")
                            .val(this['ext'])
                            .html(this['name'])
                            .prop('selected', true)
                    );
                });
                sortOptions(selectedOpts);
            }
            $selector.selectpicker("refresh");
        }
    });

    $.get(url).done(function () {
        // Ajax success
        $.ajax({
            url: url,
            data: {active: true},
            success: function (results, textStatus) {
                if (textStatus === 'success') {
                    $.each(results.data, function () {
                        let selectedOpt = $("#report-select option[value='" + this['ext'] + "']");
                        if (selectedOpt.length === 0) {
                            $(otherOpts).append(
                                $("<option></option>")
                                    .val(this['ext'])
                                    .html(this['name'])
                            );
                        }
                    });
                    sortOptions(otherOpts);
                }
                $selector.selectpicker("refresh");
            }
        });
    });
}