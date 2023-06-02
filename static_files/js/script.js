// Display window for range input
const values = document.querySelectorAll(".completion-percentage-value")
const inputs = document.querySelectorAll(".completion-percentage-input")

for (let i = 0; i < values.length; i++) {
  const value = values[i]
  const input = inputs[i]

  value.textContent = input.value

    input.addEventListener("input", (event) => {
      value.textContent = event.target.value
    })
}


// Get the CSRF token from the cookie
const csrftoken = getCookie('csrftoken');

// Close function for badges of Skill items
function skillDelete(pk) {
  fetch('/resume/skill_delete/' + pk, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({

    })
  })
  .then(response => {
    console.log('Success:', response);
  })
  .catch((error) => {
    console.error('Error:', error);
  });

  let skill = document.getElementById(pk);
  skill.classList.add("invisible")

}

// Add and delete Likes
function clickLike(pk) {
    fetch('/social/click_like', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({
      pk: pk,
    })
  })
  .then(response => response.json())
  .then(data => {
    // Process the received JSON data
    console.log(data);
    // Perform any desired operations with the data
    let likeSign = document.querySelectorAll("#like-" + pk + " i");
    let likesCount = document.querySelectorAll("#like-" + pk + " small");
    for (let i = 0; i < likeSign.length; i++) {
      likesCount[i].innerHTML = data['likes_count']
      if (data['is_liked']) {
        likeSign[i].classList.remove("fa-regular")
        likeSign[i].classList.add("fa-solid")
      }
      else {
        likeSign[i].classList.remove("fa-solid")
        likeSign[i].classList.add("fa-regular")
      }
    }
  })
  .catch((error) => {
    console.error('Error:', error);
  });

}


// Function to get the CSRF token from the cookie
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


// Bootstrap Popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl,{
  sanitize: false,
  // trigger: 'focus',
}))


// Bootstrap Tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))


// Open modal then item added
window.addEventListener('load', function() {
  var urlParams = new URLSearchParams(window.location.search);
  var modalId = urlParams.get('modal_id');

  if (modalId) {
    var modal = new bootstrap.Modal(document.getElementById(modalId));
    var modalDom = document.getElementById(modalId)
    modalDom.classList.remove('fade')
    modal.show();
    setTimeout(function() {
      modalDom.classList.add('fade')
    }, 1000);

  }
});


// Display comment edit form
function toggleCommentEditForm(button) {
  var commentItem = button.closest('.comment-item');
  var commentText = commentItem.querySelector('.comment-text');
  var editForm = commentItem.querySelector('.edit-form');

  if (commentText.style.display === 'none') {
    commentText.style.display = 'block';
    editForm.style.display = 'none';
  } else {
    commentText.style.display = 'none';
    editForm.style.display = 'block';
  }
}


//Clear url parameters then modals are hidden
const modals = document.querySelectorAll('.modal')
for (let i = 0 ; i < modals.length; i++) {
  modals[i].addEventListener('hide.bs.modal', event => {
    removeUrlParameters()
  })
};

function removeUrlParameters() {
  let urlWithoutParameters = window.location.origin + window.location.pathname;
  window.history.replaceState({}, document.title, urlWithoutParameters);
}


// Opens the modal if button clicked
function openModal(modalId) {
  var modal = new bootstrap.Modal(document.getElementById(modalId));
  modal.show();
};


// Skill button functionality
const buttons = document.querySelectorAll('.skill-item');
for (let i = 0; i < buttons.length; i++) {
  // Attach click event listener to the button
  buttons[i].addEventListener('click', function (event) {
    // Handle button click event
    openModal('comments-' + buttons[i].id);
  });
  let deleteSpan = buttons[i].querySelector('.close-skill-badge');
  if (deleteSpan) {
    deleteSpan.addEventListener('click', function (event) {
      // Handle delete span click event
      event.stopPropagation();
      skillDelete(buttons[i].id);
    });
  }

  let likeSpan = buttons[i].querySelector('.like-skill-badge');
  if (likeSpan) {
    likeSpan.addEventListener('click', function (event) {
      // Handle like span click event
      event.stopPropagation();
      clickLike(buttons[i].id);
    });
  }
}


// Resume items clickable
const resumes = document.querySelectorAll('.resume-item');
for (let i = 0; i < resumes.length; i++) {
  resumes[i].addEventListener('click', function (event) {
    let linkElement = resumes[i].querySelector('.resume-hidden-link');
    let linkUrl = linkElement.href;
    window.location.href = linkUrl
  });

  let commentButton = resumes[i].querySelector('.comment-button');
  commentButton.addEventListener('click', function(event) {
    event.stopPropagation();
    openModal(commentButton.dataset.target)
  });

  let likeButton = resumes[i].querySelectorAll('.like-button');
  for (let i = 0; i < likeButton.length; i++) {
    likeButton[i].addEventListener('click', function (event) {
      event.stopPropagation();
      console.log('like button is clicked')
      clickLike(likeButton.dataset.target);
    });
  }

  let ratingButton = resumes[i].querySelector('.rating-button');
  ratingButton.addEventListener('click', function(event) {
    event.stopPropagation();

  });
}


// Items on mobile screens is clickable
if(window.innerWidth <= 767) {
    itemList = document.querySelectorAll('.item:not(.item-in-modal)')
    for (let i = 0; i < itemList.length; i++){
      itemList[i].addEventListener('click', function (event) {
        openModal('comments-' + itemList[i].getAttribute('data-id'));
      })
    }
}


// password repeat front-end verification
document.getElementById('signup_form').addEventListener('submit', function (event) {
  var password1 = document.getElementById('password1_field');
  var password2 = document.getElementById('password2_field');
  var alertMessage = document.getElementById('password_repeat_alert')

  if (password1.value !== password2.value) {
    console.log('Passwords do not match!')
    event.preventDefault();
    alertMessage.removeAttribute('hidden')
  }
});