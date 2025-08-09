# whiteboard/views.py
from django.shortcuts import render

def whiteboard_view(request, board_id=None):
    return render(request, 'whiteboard/whiteboard.html', {
        'board_id': board_id or 'main'
    })
