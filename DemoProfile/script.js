const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
const yearEl = document.getElementById('year');
const copyButton = document.querySelector('.copy-btn');

if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });

  navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => navLinks.classList.remove('active'));
  });
}

if (copyButton) {
  copyButton.addEventListener('click', async () => {
    const email = copyButton.getAttribute('data-email');

    try {
      await navigator.clipboard.writeText(email);
      copyButton.textContent = '복사 완료';
      setTimeout(() => {
        copyButton.textContent = '이메일 복사';
      }, 1500);
    } catch (error) {
      copyButton.textContent = '복사 실패';
    }
  });
}
