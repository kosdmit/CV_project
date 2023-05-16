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
    let likeSign = document.querySelector("#like-" + pk + " i");
    let likesCount = document.querySelector("#like-" + pk + " small");
    likesCount.innerHTML = data['likes_count']
    if (data['is_liked']) {
        likeSign.classList.remove("fa-regular")
        likeSign.classList.add("fa-solid")
    }
    else {
        likeSign.classList.remove("fa-solid")
        likeSign.classList.add("fa-regular")
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



// Get the button element
const buttons = document.querySelectorAll('.skill-item');
for (let i = 0; i < buttons.length; i++) {
// Attach click event listener to the button
  buttons[i].addEventListener('click', function (event) {
    // Handle button click event
    openModal('comments-' + buttons[i].id);
  });
  let deleteSpan = buttons[i].querySelector('.close-skill-badge');
  deleteSpan.addEventListener('click', function(event) {
  // Handle delete span click event
    event.stopPropagation();
    skillDelete(buttons[i].id);
  });

  let likeSpan = buttons[i].querySelector('.like-skill-badge');
  likeSpan.addEventListener('click', function(event) {
  // Handle like span click event
    event.stopPropagation();
  clickLike(buttons[i].id);
  });
}
