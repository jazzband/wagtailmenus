from django.template import loader
from rest_framework.renderers import BrowsableAPIRenderer


class BrowsableAPIWithArgumentFormRenderer(BrowsableAPIRenderer):

    template = 'wagtailmenus/api/api_with_argument_form.html'
    argument_form_template = 'wagtailmenus/api/argument_form_modal.html'

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        context['argument_form'] = self.get_argument_form(
            data, context['view'], context['request']
        )
        return context

    def get_argument_form(self, data, view, request):
        form = view.get_argument_form(request)
        template = loader.get_template(self.argument_form_template)
        context = {'elements': [form.to_html(request, view)]}
        return template.render(context)
