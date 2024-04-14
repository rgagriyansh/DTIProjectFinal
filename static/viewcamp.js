document.addEventListener('DOMContentLoaded', function() {
    const circles = document.querySelectorAll('.circle-container');
    
    circles.forEach(function(circle) {
      const percentage = circle.getAttribute('data-percentage');
      circle.style.setProperty('--percentage', `${percentage}deg`);
    });
  });
  