<?php
/**
 * A class to turn a Page data structure into a blob of HTML
 */
class Layout {
	/**
	 * turns the Page into HTML
	 */
	public function display_page(Page $page) {
		global $config;

		$theme_name = $config->get_string('theme', 'default');
		$data_href = get_base_href();
		$contact_link = $config->get_string('contact_link');

		$header_html = "";
		foreach($page->html_headers as $line) {
			$header_html .= "\t\t$line\n";
		}

		$left_block_html = "";
		$right_block_html = "";
		$main_block_html = "";
		$head_block_html = "";
		$sub_block_html = "";

		foreach($page->blocks as $block) {
			switch($block->section) {
				case "left":
					$left_block_html .= $block->get_html(true);
					break;
				case "right":
					$right_block_html .= $block->get_html(true);
					break;
				case "head":
					$head_block_html .= "<td style='width: 250px; font-size: 0.85em;'>".$block->get_html(false)."</td>";
					break;
				case "main":
					$main_block_html .= $block->get_html(false);
					break;
				case "subheading":
					$sub_block_html .= $block->body; // $block->get_html(true);
					break;
				default:
					print "<p>error: {$block->header} using an unknown section ({$block->section})";
					break;
			}
		}

		$debug = get_debug_info();

		$contact = empty($contact_link) ? "" : "<br><a href='$contact_link'>Contact</a>";
		$subheading = empty($page->subheading) ? "" : "<div id='subtitle'>{$page->subheading}</div>";

		$wrapper = "";
		if(strlen($page->heading) > 100) {
			$wrapper = ' style="height: 3em; overflow: auto;"';
		}

		$flash = get_prefixed_cookie("flash_message");
		$flash_html = "";
		if($flash) {
			$flash_html = "<b id='flash'>".nl2br(html_escape($flash))." <a href='#' onclick=\"\$('#flash').hide(); return false;\">[X]</a></b>";
			set_prefixed_cookie("flash_message", "", -1, "/");
		}

		$header_html_thing = file_get_contents("themes/rule34v2/header.inc");
		print <<<EOD
<!DOCTYPE html>
<html>
	<head>
		<title>{$page->title}</title>
		<link rel="stylesheet" href="$data_href/themes/$theme_name/menuh.css" type="text/css">
		<meta name="ero_verify" content="16ecd096623b47cd03b3228d906dbd80" />
$header_html
<!-- Begin JuicyAds XAPI Code -->
<!--<script type="text/javascript">juicy_code='3494y203q256r2x2v284y2';</script>
<script type="text/javascript" src="http://xapi.juicyads.com/js/jac.js" charset="utf-8"></script>-->
<!-- End JuicyAds XAPI Code -->
	</head>

	<body>
<table id="header" class="bgtop">
	<tr>
		<td>
			$header_html_thing
		</td>
		$head_block_html
	</tr>
</table>
		$sub_block_html

		<nav>
			$left_block_html
			<p>
				<a href="http://contextshift.eu"><img src="/themes/rule34v2/ads/cshift_bottom.jpg" width="69" height="28" alt="contextshift" /></a>
				<a href="http://whos.amung.us/show/4vcsbthd"><img src="http://whos.amung.us/widget/4vcsbthd.png" alt="web counter" /></a>
			</p>
		</nav>

		<article>
			$flash_html
			$main_block_html
		</article>

		<footer>
			Images &copy; their respective owners,
			<a href="http://code.shishnet.org/shimmie2/">Shimmie</a> &copy;
			<a href="http://www.shishnet.org/">Shish</a> &amp;
			<a href="https://github.com/shish/shimmie2/contributors">The Team</a>
			2007-2013,
			based on the Danbooru concept.
			$debug
			$contact
		</footer>
		
		<!-- BEGIN EroAdvertising ADSPACE CODE -->
<!--<script type="text/javascript" language="javascript" charset="utf-8" src="http://adspaces.ero-advertising.com/adspace/158168.js"></script>-->
<!-- END EroAdvertising ADSPACE CODE -->
	</body>
</html>
EOD;
	}
}
?>
