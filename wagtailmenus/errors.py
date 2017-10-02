from django.template import TemplateSyntaxError


class SubMenuUsageError(TemplateSyntaxError):
    def __init__(self):
        return TemplateSyntaxError.__init__(self, (
            "The 'sub_menu' tag can only be used in menu templates to render "
            "parts of other menus, initiated by calling one of the other "
            "included tags: 'main_menu', 'flat_menu', 'section_menu' or "
            "'children_menu' (custom tags are not supported). You might "
            "want to update your template to use the 'children_menu' tag "
            "instead."))
