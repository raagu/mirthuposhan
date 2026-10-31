// Keep content and navigation usable if JavaScript or the contact API fails.
const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = document.getElementById('sendButton');
    const status = document.getElementById('form-status');
    if (button.disabled) return;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    const originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = 'Sending…';
    status.textContent = '';
    form.setAttribute('aria-busy', 'true');
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok || result.success !== true) throw new Error('Submission failed');
      status.textContent = 'Message sent. Thank you for contacting Mirthu Poshan.';
      form.reset();
    } catch {
      // Preserve the message and offer a direct way to contact the business.
      status.textContent = 'Your message could not be confirmed. Please try again or contact us by phone or WhatsApp.';
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
      button.textContent = originalLabel;
      form.removeAttribute('aria-busy');
    }
  });
}
