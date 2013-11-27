<%def name="action()">
	% if user.can("manage_alias_list"):
		<th width="10%">Action</th>
	% endif
</%def>

<%def name="add()">
	% if user.can("manage_alias_list"):
		<tr>
			<form> <!-- TODO -->
				<td><input type='text' name='oldtag'></td>
				<td><input type='text' name='newtag'></td>
				<td><input type='submit' value='Add'></td>
			</form>
		</tr>
	% endif
</%def>

<%def name="display_aliases(page, aliases, page_number, total_pages)">
<%
	page.title = "Alias List"
	page.heading = "Alias List"
	page.add_block(NavBlock())
	page.add_block(Block("Aliases", alias_table(aliases)))
	if user.can("manage_alias_list"):
		page.add_block("Bulk Upload", bulk_uploader())
	display_paginator(page, "alias/list", None, page_number, total_pages)
%>
</%def>

<%def name="alias_table(aliases)">
	<table id="aliases" class="sortable zebra">
		<thead>
			<tr>
				<th>From</th>
				<th>To</th>
				${action()}
			</tr>
		</thead>
		<tbody>
		</tbody>
		<tfoot>
			${add()}
		</tfoot>
	</table>

	<p><a href="${make_link("alias/export/aliases.csv")}">Download as CSV</a></p>
</%def>
