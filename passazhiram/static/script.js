// главный слайдер
document.addEventListener('DOMContentLoaded', function() {
  const slider = document.querySelector('.slider');
  if (slider) {
      let slides = document.querySelectorAll('.slide');
      let currentSlide = 0;
      let slideInterval;
      
      function showSlide(index) {
          slides.forEach((slide, i) => {
              slide.classList.toggle('active', i === index);
          });
          updateDots(index);
      }
      
      function nextSlide() {
          currentSlide = (currentSlide + 1) % slides.length;
          showSlide(currentSlide);
      }
      
      function prevSlide() {
          currentSlide = (currentSlide - 1 + slides.length) % slides.length;
          showSlide(currentSlide);
      }
      
      function createDots() {
          const dotsContainer = document.querySelector('.slider-dots');
          if (dotsContainer) {
              dotsContainer.innerHTML = '';
              slides.forEach((_, i) => {
                  const dot = document.createElement('div');
                  dot.classList.add('dot');
                  if (i === 0) dot.classList.add('active');
                  dot.addEventListener('click', () => {
                      currentSlide = i;
                      showSlide(currentSlide);
                      resetInterval();
                  });
                  dotsContainer.appendChild(dot);
              });
          }
      }
      
      function updateDots(index) {
          const dots = document.querySelectorAll('.dot');
          dots.forEach((dot, i) => {
              dot.classList.toggle('active', i === index);
          });
      }
      
      function startInterval() {
          slideInterval = setInterval(nextSlide, 3000);
      }
      
      function resetInterval() {
          clearInterval(slideInterval);
          startInterval();
      }
      
      const prevBtn = document.querySelector('.prev');
      const nextBtn = document.querySelector('.next');
      
      if (prevBtn) prevBtn.addEventListener('click', () => { prevSlide(); resetInterval(); });
      if (nextBtn) nextBtn.addEventListener('click', () => { nextSlide(); resetInterval(); });
      
      createDots();
      startInterval();
  }
  
  // слайдер в кабинете
  const miniSlider = document.querySelector('.mini-slider');
  if (miniSlider) {
      let miniSlides = document.querySelectorAll('.mini-slide');
      let miniCurrent = 0;
      
      setInterval(() => {
          miniSlides.forEach(slide => slide.classList.remove('active'));
          miniCurrent = (miniCurrent + 1) % miniSlides.length;
          miniSlides[miniCurrent].classList.add('active');
      }, 3000);
  }
  

  document.querySelectorAll('.alert-close').forEach(btn => {
      btn.addEventListener('click', function() {
          this.closest('.alert').remove();
      });
  });
  
  // исчезновение уведомлений 
  setTimeout(() => {
      document.querySelectorAll('.alert').forEach(alert => {
          alert.style.opacity = '0';
          setTimeout(() => alert.remove(), 300);
      });
  }, 5000);
});

// валидация регистрации 
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', function(e) {
      const login = this.querySelector('[name="login"]').value;
      const password = this.querySelector('[name="password"]').value;
      
      if (!/^[a-zA-Z0-9]{6,}$/.test(login)) {
          e.preventDefault();
          alert('Логин должен содержать минимум 6 символов латиницы и цифр');
      } else if (password.length < 8) {
          e.preventDefault();
          alert('Пароль должен содержать минимум 8 символов');
      }
  });
}