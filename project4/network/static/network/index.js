document.addEventListener('DOMContentLoaded', function() {
    
    loadPosts('all');
    
    
    if (document.querySelector('#post-submit')) {
        document.querySelector('#post-submit').addEventListener('click', submitPost);
    }
});

function loadPosts(type, username=null, page=1) {
    let url;
    if (type === 'profile') {
        url = `/posts/user/${username}?page=${page}`;
    } else {
        url = `/posts/${type}?page=${page}`;
    }
    
    fetch(url)
    .then(response => response.json())
    .then(data => {
        renderPosts(data.posts);
        renderPagination(data.has_previous, data.has_next, type, username, page);
    });
}

function renderPosts(posts) {
    const postsView = document.querySelector('#posts-view');
    postsView.innerHTML = '';
    
    posts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'card mb-3';
        postElement.innerHTML = `
            <div class="card-body">
                <h5 class="card-title"><a href="/profile/${post.user}">${post.user}</a></h5>
                <p class="card-text" id="post-content-${post.id}">${post.content}</p>
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted">${post.timestamp}</small>
                    <div>
                        ${post.can_edit ? `<button class="btn btn-sm btn-outline-secondary edit-post" data-id="${post.id}">Edit</button>` : ''}
                        <button class="btn btn-sm ${post.is_liked ? 'btn-danger' : 'btn-outline-danger'} like-post" data-id="${post.id}">
                            ♥ ${post.likes}
                        </button>
                    </div>
                </div>
                ${post.can_edit ? `
                <div class="edit-form mt-2" id="edit-form-${post.id}" style="display: none;">
                    <textarea class="form-control mb-2" id="edit-textarea-${post.id}">${post.content}</textarea>
                    <button class="btn btn-sm btn-primary save-edit" data-id="${post.id}">Save</button>
                    <button class="btn btn-sm btn-outline-secondary cancel-edit" data-id="${post.id}">Cancel</button>
                </div>` : ''}
                
                <!-- Comments section -->
                <div class="mt-3 comments-section">
                    <h6>Comments (${post.comments.length})</h6>
                    <div id="comments-container-${post.id}" class="mb-2">
                        ${post.comments.map(comment => `
                            <div class="card mb-2 comment">
                                <div class="card-body p-2">
                                    <div class="d-flex justify-content-between">
                                        <h6 class="card-subtitle mb-1"><a href="/profile/${comment.user}">${comment.user}</a></h6>
                                        <small class="text-muted">${comment.timestamp}</small>
                                    </div>
                                    <p class="card-text mb-1">${comment.content}</p>
                                    ${comment.can_delete ? `<button class="btn btn-sm btn-outline-danger delete-comment" data-commentid="${comment.id}">Delete</button>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    ${post.can_comment ? `
                    <div class="input-group mb-3">
                        <input type="text" class="form-control comment-input" id="comment-input-${post.id}" placeholder="Add a comment...">
                        <div class="input-group-append">
                            <button class="btn btn-outline-primary add-comment" data-postid="${post.id}" type="button">Post</button>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        postsView.appendChild(postElement);
    });    
    
    
    document.querySelectorAll('.like-post').forEach(button => {
        button.addEventListener('click', likePost);
    });
    
    
    document.querySelectorAll('.edit-post').forEach(button => {
        button.addEventListener('click', showEditForm);
    });
    
    
    document.querySelectorAll('.save-edit').forEach(button => {
        button.addEventListener('click', saveEdit);
    });
    
    
    document.querySelectorAll('.cancel-edit').forEach(button => {
        button.addEventListener('click', cancelEdit);
    });

    document.querySelectorAll('.add-comment').forEach(button => {
        button.addEventListener('click', function() {
            addComment(this.dataset.postid);
        });
    });

     document.querySelectorAll('.comment-input').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const postId = this.id.split('-')[2];
                addComment(postId);
            }
        });
    });

    document.querySelectorAll('.delete-comment').forEach(button => {
        button.addEventListener('click', deleteComment);
    });
}




function renderPagination(hasPrevious, hasNext, type, username, currentPage) {
    const pagination = document.querySelector('#pagination');
    pagination.innerHTML = '';
    
    if (hasPrevious) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<a class="page-link" href="#" data-page="${parseInt(currentPage) - 1}">Previous</a>`;
        pagination.appendChild(li);
    }
    
    if (hasNext) {
        const li = document.createElement('li');
        li.className = 'page-item';
        li.innerHTML = `<a class="page-link" href="#" data-page="${parseInt(currentPage) + 1}">Next</a>`;
        pagination.appendChild(li);
    }
    
    
    document.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            loadPosts(type, username, this.dataset.page);
        });
    });
}

function submitPost() {
    const content = document.querySelector('#post-content').value;
    
    if (!content.trim()) {
        alert('Post content cannot be empty!');
        return;
    }
    
    fetch('/post', {
        method: 'POST',
        body: JSON.stringify({
            content: content
        }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.querySelector('#post-content').value = '';
            loadPosts('all');
        } else {
            alert('Error: ' + data.error);
        }
    });
}

function likePost() {
    const postId = this.dataset.id;
    
    fetch(`/like/${postId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            const button = document.querySelector(`.like-post[data-id="${postId}"]`);
            if (data.liked) {
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-danger');
            } else {
                button.classList.remove('btn-danger');
                button.classList.add('btn-outline-danger');
            }
            button.innerHTML = `♥ ${data.likes_count}`;
        }
    });
}

function showEditForm() {
    const postId = this.dataset.id;
    document.querySelector(`#edit-form-${postId}`).style.display = 'block';
    this.style.display = 'none';
}

function cancelEdit() {
    const postId = this.dataset.id;
    document.querySelector(`#edit-form-${postId}`).style.display = 'none';
    document.querySelector(`.edit-post[data-id="${postId}"]`).style.display = 'inline-block';
}

function saveEdit() {
    const postId = this.dataset.id;
    const content = document.querySelector(`#edit-textarea-${postId}`).value;
    
    fetch(`/post/${postId}`, {
        method: 'PUT',
        body: JSON.stringify({
            content: content
        }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.querySelector(`#post-content-${postId}`).textContent = content;
            document.querySelector(`#edit-form-${postId}`).style.display = 'none';
            document.querySelector(`.edit-post[data-id="${postId}"]`).style.display = 'inline-block';
        }
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
if (window.location.pathname === '/following') {
    loadFollowingPosts();
}

function loadFollowingPosts() {
    fetch('/posts/following')
        .then(response => response.json())
        .then(posts => {
        });
}


function renderComments(comments, postId) {
    const commentsContainer = document.querySelector(`#comments-container-${postId}`);
    if (!commentsContainer) return;
    
    commentsContainer.innerHTML = '';
    
    comments.forEach(comment => {
        const commentElement = document.createElement('div');
        commentElement.className = 'card mb-2';
        commentElement.innerHTML = `
            <div class="card-body p-2">
                <div class="d-flex justify-content-between">
                    <h6 class="card-subtitle mb-1"><a href="/profile/${comment.user}">${comment.user}</a></h6>
                    <small class="text-muted">${comment.timestamp}</small>
                </div>
                <p class="card-text mb-1">${comment.content}</p>
                ${comment.can_delete ? `<button class="btn btn-sm btn-outline-danger delete-comment" data-commentid="${comment.id}">Delete</button>` : ''}
            </div>
        `;
        commentsContainer.appendChild(commentElement);
    });
    
    
    document.querySelectorAll(`.delete-comment`).forEach(button => {
        button.addEventListener('click', deleteComment);
    });
}

function addComment(postId) {
    const content = document.querySelector(`#comment-input-${postId}`).value.trim();
    
    if (!content) {
        alert('Comment cannot be empty!');
        return;
    }
    
    fetch(`/post/${postId}/comment`, {
        method: 'POST',
        body: JSON.stringify({
            content: content
        }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.querySelector(`#comment-input-${postId}`).value = '';
            loadPosts('all'); 
        } else {
            alert('Error: ' + data.error);
        }
    });
}

function deleteComment() {
    const commentId = this.dataset.commentid;
    
    if (!confirm('Are you sure you want to delete this comment?')) {
        return;
    }
    
    fetch(`/comment/${commentId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            loadPosts('all'); 
        } else {
            alert('Error: ' + data.error);
        }
    });
}