<%
# vim:ft=html

left_block_html = ""
main_block_html = ""
sub_block_html = ""
head_block_html = ""

for block in page.blocks:
	if block.section == "left":
		left_block_html += block.__html__(True)
	elif block.section == "main":
		main_block_html += block.__html__(False)
	elif block.section == "sub":
		sub_block_html += block.__html__(False)
	elif block.section == "head":
		head_block_html += block.__html__(False)
	else:
		raise ThemeException("Block %r using an unknown section (%r)" % (block.header, block.section))

flash = ctx.request.cookies.get("shm_flash_message")
flash_html = ""
if flash:
	# TODO:
	#flash_html = "<b id='flash'>".nl2br(html_escape($flash))." <a href='#' onclick=\"\$('#flash').hide(); return false;\">[X]</a></b>";
	#set_prefixed_cookie("flash_message", "", -1, "/");
	pass

header_html_thing = file("shimpy/theme/rule34/header.inc").read()
%>
<!doctype html>
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang="en"> <![endif]-->
<!--[if IE 7]>    <html class="no-js lt-ie9 lt-ie8" lang="en"> <![endif]-->
<!--[if IE 8]>    <html class="no-js lt-ie9" lang="en"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
    <head>
        <title>${page.title}</title>
        % for header in page.html_headers:
        ${header}
        % endfor
    </head>

    <body>
        <table id="header" class="bgtop">
            <tr>
                <td>
                    ${header_html_thing}
                </td>
                <td width="250">
                    ${head_block_html}
                </td>
            </tr>
        </table>
        <nav>
            ${left_block_html}
        </nav>
        <article>
            ${flash_html}
            ${main_block_html}
        </article>
        <footer>
            Images &copy; their respective owners,
            <a href="http://github.com/shish/shimpy/">Shimpy</a> &copy;
            <a href="http://www.shishnet.org/">Shish</a> &amp;
            <a href="https://github.com/shish/shimpy/contributors">The Team</a>
            2013.

            ${ctx.get_debug_info()}

			% if ctx.config.get("contact_link"):
	            <br><a href='mailto:${ctx.config.get("contact_link")}'>Contact</a>
			% endif
        </footer>
    </body>
</html>
