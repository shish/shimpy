<%
def display_page():
	page.title = "Admin Tools"
	page.heading = "Admin Tools"
	page.add_block(NavBlock())
%>

<%def name="button(name, action, protected)">
	${make_form(make_link("admin/"+action), "POST", False, False, False, "admin " + c_protected)}
	% if protected:
		<input type='submit' id='$action' value='$name' disabled='true'>
		<input type='checkbox' onclick='$("#$action").attr("disabled", !$(this).is(":checked"))'>
	% else:
		<input type='submit' id='$action' value='$name'>
	% endif
	</form>
</%def>

<%def name="display_form()">
	${button("All tags to lowercase", "lowercase_all_tags", True)}
	${button("Recount tag use", "recount_tag_use", False)}
	${button("Download all images", "image_dump", False)}
	${button("Download database contents", "database_dump", False)}
	${button("Reset image IDs", "reset_image_ids", True)}

	${make_form(make_link("admin/set_tag_case"), "POST")}
		<input type='text' name='tag' placeholder='Enter tag with correct case'>
		<input type='submit' value='Set Tag Case'>
	</form>
</%def>

<%def name="dbq_html(terms)">
	${make_form(make_link("admin/delete_by_query"), "POST")}
		<input type='button' class='shm-unlocker' data-unlock-sel='#dbqsubmit' value='Unlock'>
		<input type='hidden' name='query' value='${terms}'>
		% if class_exists("ImageBan"):
			<input type='text' name='reason' placeholder='Ban reason (leave blank to not ban)'>
		% endif
		<input type='submit' id='dbqsubmit' disabled='true' value='Delete All These Images'>
	</form>
</%def>
