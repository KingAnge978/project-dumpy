document.addEventListener('DOMContentLoaded', function() {
    const username = document.querySelector('#profile-username').textContent.trim();
    loadProfile(username);
    loadPosts('profile', username);
    
    if (document.querySelector('#follow-btn')) {
        document.querySelector('#follow-btn').addEventListener('click', toggleFollow);
    }
});

function loadProfile(username) {
    fetch(`/profile/${username}`)
    .then(response => response.json())
    .then(data => {
        document.querySelector('#followers-count').textContent = data.followers_count;
        document.querySelector('#following-count').textContent = data.following_count;
        
        const followBtn = document.querySelector('#follow-btn');
        if (followBtn) {
            if (data.is_following) {
                followBtn.textContent = 'Unfollow';
                followBtn.classList.remove('btn-primary');
                followBtn.classList.add('btn-danger');
            } else {
                followBtn.textContent = 'Follow';
                followBtn.classList.remove('btn-danger');
                followBtn.classList.add('btn-primary');
            }
        }
    });
}

function toggleFollow() {
    const username = document.querySelector('#profile-username').textContent.trim();
    const action = this.textContent === 'Follow' ? 'follow' : 'unfollow';
    
    fetch(`/profile/${username}`, {
        method: 'PUT',
        body: JSON.stringify({
            action: action
        }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            loadProfile(username);
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
