function sortOptions(selector) {
    let my_options = $(selector + " option");
    my_options.sort(function(a,b) {
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
    let allEntries = "optgroup#all-" + select_tag;
    let filteredEntries = "optgroup#filtered-" + select_tag;
    $selector.addClass("selectpicker");
    $selector.selectpicker({
        size: 4,
        width: "100%"
    });

    $selector.append(
        $('<optgroup></optgroup>')
            .attr("id", "filtered-" + select_tag)
            .attr("label", "Your clients")
    );
    $selector.append(
        $('<optgroup></optgroup>')
            .attr("id", "all-" + select_tag)
            .attr("label", "All clients")
    );
    $.ajax({
        url: url,
        data: {active: true},
        success: function (results, textStatus) {
            if (textStatus === 'success') {
                $.each(results.data, function () {
                    $(allEntries).append(
                        $("<option></option>")
                            .val(this['id'])
                            .html(this['name'])
                    );
                });
                sortOptions(allEntries);
            }
            $selector.selectpicker("refresh");
        }
    });

    $.get(url).done(function() {
        // Ajax success
        $.ajax({
            url: url,
            method: "POST",
            success: function (results, textStatus) {
                if (textStatus === 'success') {
                    $.each(results.data, function () {
                        $(filteredEntries).append(
                            $("<option></option>")
                                .val(this['id'])
                                .html(this['name'])
                                .prop('selected', true)
                        );
                    });
                    sortOptions(filteredEntries);
                }
                $selector.selectpicker("refresh");
            }
        });
    });
}