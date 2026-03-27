const searchInput = document.getElementById('searchInput');

if (searchInput) {
  searchInput.addEventListener('keyup', function () {
    let value = this.value.toLowerCase();
    let cards = document.querySelectorAll('.project-card');

    cards.forEach(card => {
      card.style.display = card.innerText.toLowerCase().includes(value) ? '' : 'none';
    });
  });
}