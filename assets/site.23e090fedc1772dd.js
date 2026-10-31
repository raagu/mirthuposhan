// Navigation enhancement only: orders and FAQs work without JavaScript.
document.querySelectorAll('.mobile-nav a').forEach((link) => {
  link.addEventListener('click', () => {
    link.closest('details').open = false;
  });
});

// Keep the existing process fragment usable when arriving from an old link.
function openLinkedDetails() {
  if (window.location.hash === '#process') {
    const process = document.getElementById('process');
    if (process) process.open = true;
  }
}
openLinkedDetails();
window.addEventListener('hashchange', openLinkedDetails);
