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
function skillDelete(username, slug, pk) {
  fetch('/resume/' + username + '/' + slug + '/' + pk + '/skill_delete', {
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

  let skill = document.querySelector("#skill-" + pk);
  skill.classList.add("invisible")

}


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
