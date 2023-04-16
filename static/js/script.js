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


