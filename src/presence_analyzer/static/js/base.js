var prepare_user_select = function()
{
	loading = $('#loading');
	$.getJSON("/api/v1/users", function(result) {
	    var dropdown = $("#user_id");
	    $.each(result, function(item) {
	        dropdown.append($("<option />").val(this.user_id).text(this.name));
	    });
	    dropdown.show();
	    loading.hide();
	});
}.bind(this);
