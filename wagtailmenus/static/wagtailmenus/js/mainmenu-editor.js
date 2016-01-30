$(document).ready(function(){
	var $addButton = $("#id_menu_items-ADD");

	function toggle_menuitem_fields(fieldset_element, animate){
		$this = $(fieldset_element);
		$show_children_menu_checkbox = $this.find("input[name$='show_children_menu']");
		$repeat_in_children_menu_checkbox = $this.find("input[name$='repeat_in_children_menu']");
		$repeat_in_children_menu_field = $repeat_in_children_menu_checkbox.closest('li');
		$children_menu_link_text_field = $this.find("input[name$='children_menu_link_text']").closest('li');
		if($show_children_menu_checkbox.prop('checked')) {
			if(animate) $repeat_in_children_menu_field.slideDown(300);
			else $repeat_in_children_menu_field.show();
		} else {
			if(animate) {
				$repeat_in_children_menu_field.slideUp(300);
				$children_menu_link_text_field.slideUp(300);
			} else {
				$repeat_in_children_menu_field.hide();
				$children_menu_link_text_field.hide();
			}
		}
		if($repeat_in_children_menu_checkbox.prop('checked')) {
			if(animate) $children_menu_link_text_field.slideDown(300)
			else $children_menu_link_text_field.show();
		} else {
			if(animate) $children_menu_link_text_field.slideUp(300)
			else $children_menu_link_text_field.hide();
		}
	}

	function apply_menuitem_stuff(){
		$menuitem_fieldsets = $('ul#id_menu_items-FORMS fieldset');
		$menuitem_fieldsets.each(function(){
			var fieldset = this;
			toggle_menuitem_fields(this, false);
			$(this).find("input[type='checkbox']").change(function(){
				toggle_menuitem_fields(fieldset, true);
			})
		})
	}

	apply_menuitem_stuff();

	$addButton.click(apply_menuitem_stuff);
});
