from cProfile import label
import markdown2
import secrets

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from . import util
from markdown import Markdown


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Entry title", widget=forms.TextInput(
        attrs={'class': 'form-control col-md-6 col-lg-6'}))
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control col-md-6 col-lg-6', 'rows': 10}))
    edit = forms.BooleanField(
        initial=False, widget=forms.HiddenInput(), required=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    md = Markdown()
    entry_page = util.get_entry(entry)
    if entry_page is None:
        return render(request, "encyclopedia/none.html", {
            'entry_title': entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            'entry': md.convert(entry_page),
            'entry_title': entry
        })


def new_entry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/new.html", {
                    'form': form,
                    'existing': True,
                    'entry': title
                })
        else:
            return render(request, "encyclopedia/new.html", {
                'form': form,
                'existing': False
            })
    else:
        return render(request, "encyclopedia/new.html", {
            'form': NewEntryForm(),
            'existing': False
        })


def edit(request, entry):
    entry_page = util.get_entry(entry)
    if entry_page is None:
        return render(request, "encyclopedia/none.html", {
            'entry_title': entry
        })
    else:
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput(
            attrs={'class': 'form-control col-md-6 col-lg-6'})
        form.fields["content"].initial = entry_page
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/new.html", {
            'form': form,
            'edit': form.fields["edit"].initial,
            'entry_title': form.fields["title"].initial
        })


def random(request):
    entries = util.list_entries()
    random_entry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': random_entry}))


def search(request):
    value = request.GET.get('q', '')
    if(util.get_entry(value) is not None):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': value}))
    else:
        sub_entries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                sub_entries.append(entry)

        return render(request, "encyclopedia/index.html", {
            'entries': sub_entries,
            'search': True,
            'value': value
        })
