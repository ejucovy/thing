from django import forms
from django.utils.translation import ugettext_lazy as _

class ProjectToolForm(forms.Form):
    name = forms.CharField(max_length=50)
    slug = forms.SlugField(max_length=50)

    description = forms.CharField(widget=forms.Textarea)

    PERMISSION_CHOICES = (
        ('0', _("Not even see this wiki")),
        ('1', _("View this wiki's contents")),
        ('2', _("And view the wiki's history")),
        ('3', _("And edit any page")),
        )
    PERMISSION_MAP = {
        '1': "view",
        '2': "view_history",
        '3': "edit",
        }

    member_level = forms.ChoiceField(
        choices=PERMISSION_CHOICES,
        )
    other_level = forms.ChoiceField(widget=forms.RadioSelect, choices=PERMISSION_CHOICES)

