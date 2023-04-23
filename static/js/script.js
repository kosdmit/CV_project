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


// Bootstrap Popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl,{
  sanitize: false,
  // trigger: 'focus',
}))


// Bootstrap Tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
