var prepare_user_select = function()
{
    loading = $('#loading');
    $.getJSON("/api/v2/users", function(result) {
        var dropdown = $("#user_id");
        $.each(result, function(item) {
            var option = $("<option />").val(this.user_id).text(this.name);
            option.attr('avatar', this.avatar);
            dropdown.append(option);
        });
        dropdown.show();
        loading.hide();
    });
}
