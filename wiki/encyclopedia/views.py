import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django import forms
from django.template.loader import get_template
import random


from . import util

def convert_markdown_to_html(markdown_content):
    for i in range(1, 7):
        markdown_content = re.sub(
            f'^{"#" * i}\\s+(.+?)(\\n|$)',
            f'<h{i}>\\1</h{i}>',
            markdown_content,
            flags=re.MULTILINE
        )
    
    markdown_content = re.sub(
        r'(\*\*|__)(?=\S)(.+?)(?<=\S)\1',
        r'<strong>\2</strong>',
        markdown_content
    )
    
    markdown_content = re.sub(
        r'(\*|_)(?=\S)(.+?)(?<=\S)\1',
        r'<em>\2</em>',
        markdown_content
    )
    
    markdown_content = re.sub(
        r'\[([^\]]+)\]\(([^\)]+)\)',
        r'<a href="\2">\1</a>',
        markdown_content
    )
    
    lines = markdown_content.split('\n')
    in_list = False
    html_lines = []
    
    for line in lines:
        if re.match(r'^\*\s+', line):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = re.sub(r'^\*\s+(.+)', r'\1', line)
            html_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(line)
    
    if in_list:
        html_lines.append('</ul>')
    
    markdown_content = '\n'.join(html_lines)
    
    markdown_content = re.sub(
        r'^(?!<[a-z])(?!\s*$)(.+?)(?:\n\n|\Z)',
        r'<p>\1</p>',
        markdown_content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    markdown_content = re.sub(
        r'(?<!<br>)\n(?![\n<ul])',
        '<br>',
        markdown_content
    )
    
    return markdown_content
    
class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), label="Content")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' does not exist."
        })
    
    html_content = convert_markdown_to_html(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('index')
        
    entries = util.list_entries()
    query_lower = query.lower()

    for entry in entries:
        if entry.lower() == query_lower:
            return redirect('entry', title=entry)
    
    matches = [entry for entry in entries if query_lower in entry.lower()]
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches,
        "has_results": bool(matches)
    })

def new_page(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        
        if util.get_entry(title):
            return render(request, "encyclopedia/new_page.html", {
                "error": f"An entry with the title '{title}' already exists.",
                "title": title,
                "content": content
            })
        
        if title and content:
            util.save_entry(title, content)
            return redirect("entry", title=title)
    
    return render(request, "encyclopedia/new_page.html")

def edit_page(request, title):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            util.save_entry(title, content)
            return redirect("entry", title=title)
    
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": f"The page '{title}' does not exist."
        })
    
    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "content": content
    })
        
def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries exist yet."
        })
    
    random_entry = random.choice(entries)
    return redirect("entry", title=random_entry)
