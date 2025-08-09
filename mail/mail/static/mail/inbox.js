document.addEventListener('DOMContentLoaded', function() {
   
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  
  document.querySelector('#compose-form').onsubmit = send_email;

  
  load_mailbox('inbox');
});

function compose_email(reply_data = null) {
  
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  
  const recipients = document.querySelector('#compose-recipients');
  const subject = document.querySelector('#compose-subject');
  const body = document.querySelector('#compose-body');

  recipients.value = '';
  subject.value = '';
  body.value = '';

  
  if (reply_data) {
    recipients.value = reply_data.recipients;
    subject.value = reply_data.subject;
    body.value = reply_data.body;
  }
}

function send_email() {
 
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

   
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
     
    load_mailbox('sent');
  })
  .catch(error => {
    console.log('Error:', error);
  });

  
  return false;
}

function load_mailbox(mailbox) {
  
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';


  const emailsView = document.querySelector('#emails-view');
  emailsView.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

 
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
   
    emails.forEach(email => {
      const emailDiv = document.createElement('div');
      emailDiv.className = `email ${email.read ? 'read' : 'unread'}`;
      emailDiv.innerHTML = `
        <div class="email-sender">${mailbox === 'sent' ? `To: ${email.recipients.join(', ')}` : `From: ${email.sender}`}</div>
        <div class="email-subject">${email.subject}</div>
        <div class="email-timestamp">${email.timestamp}</div>
      `;
      
     
      emailDiv.addEventListener('click', () => view_email(email.id, mailbox));
      
      emailsView.appendChild(emailDiv);
    });
  });
}

function view_email(email_id, mailbox) {
  
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  const emailView = document.querySelector('#email-view');
  emailView.style.display = 'block';

  
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    
    emailView.innerHTML = `
      <div><strong>From:</strong> ${email.sender}</div>
      <div><strong>To:</strong> ${email.recipients.join(', ')}</div>
      <div><strong>Subject:</strong> ${email.subject}</div>
      <div><strong>Timestamp:</strong> ${email.timestamp}</div>
      ${mailbox !== 'sent' ? `<button class="btn btn-sm btn-outline-primary" id="archive">${email.archived ? 'Unarchive' : 'Archive'}</button>` : ''}
      <button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>
      <hr>
      <div>${email.body}</div>
    `;

   
    if (!email.read) {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
          read: true
        })
      });
    }

    
    if (mailbox !== 'sent') {
      document.querySelector('#archive').addEventListener('click', () => {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: !email.archived
          })
        })
        .then(() => load_mailbox('inbox'));
      });
    }

    
    document.querySelector('#reply').addEventListener('click', () => {
     
      const reply_data = {
        recipients: email.sender,
        subject: email.subject.startsWith('Re: ') ? email.subject : `Re: ${email.subject}`,
        body: `On ${email.timestamp} ${email.sender} wrote:\n${email.body}`
      };
      compose_email(reply_data);
    });
  });
}
