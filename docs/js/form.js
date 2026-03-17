/**
 * Form submission handler — sends form data to the Azure Function endpoint.
 *
 * UPDATE the FUNCTION_URL below after deploying your Azure Function.
 */
const FUNCTION_URL = 'https://func-xijkj7tcxghyk.azurewebsites.net/api/contact';

document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form[data-form-type]');

  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const statusEl = form.querySelector('.form-status');
      const submitBtn = form.querySelector('button[type="submit"]');
      const formType = form.dataset.formType; // "contact", "school-events", "teacher-pd"

      // Gather form data
      const formData = new FormData(form);
      const data = { formType };
      formData.forEach((value, key) => {
        data[key] = value;
      });

      // Show sending state
      statusEl.className = 'form-status sending';
      statusEl.textContent = 'Sending your message…';
      submitBtn.disabled = true;

      try {
        const response = await fetch(FUNCTION_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          statusEl.className = 'form-status success';
          statusEl.textContent = 'Thank you! Your message has been sent. We\'ll be in touch soon.';
          form.reset();
        } else {
          // Try to parse a structured error from the API
          let errBody;
          try { errBody = await response.json(); } catch (_) { /* ignore */ }

          if (errBody?.error === 'solicitation') {
            statusEl.className = 'form-status error';
            statusEl.textContent = errBody.message;
          } else if (errBody?.error === 'rate_limit') {
            statusEl.className = 'form-status error';
            statusEl.textContent = errBody.message;
          } else {
            throw new Error(errBody?.message || 'Something went wrong');
          }
        }
      } catch (err) {
        statusEl.className = 'form-status error';
        statusEl.textContent = 'Sorry, something went wrong. Please email us directly at info@connectedcode.org';
        console.error('Form submission error:', err);
      } finally {
        submitBtn.disabled = false;
      }
    });
  });
});
