---
layout: page
title: Students
header: Students
group: navigation
---

<script>
// Image fallback handler for profile images
function handleImageError(img) {
  // Only fallback if we're not already showing the default image
  if (img.src.indexOf('default.jpg') === -1) {
    img.src = '{{ site.baseurl }}/assets/images/default.jpg';
  }
}

// Apply fallback to all profile images on page load
document.addEventListener('DOMContentLoaded', function() {
  const profileImages = document.querySelectorAll('img[src*="/assets/images/"]');
  profileImages.forEach(img => {
    img.addEventListener('error', function() {
      handleImageError(this);
    });
  });
});
</script>

{% for category in site.data.students %}
## {{ category.title }}

{% for student in category.students %}
  <div style="margin-bottom: 30px; display: flex; align-items: flex-start;">
    <img src="{{ site.baseurl }}/assets/images/{% if student.image %}{{ student.image }}{% else %}default.jpg{% endif %}" 
         alt="{{ student.name }}" 
         style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; margin-right: 20px; flex-shrink: 0;">
    
           <div style="flex: 1; display: flex; flex-direction: column;">
        <h3 style="margin: 0;">
          {% if student.website %}
            <a href="{{ student.website }}" target="_blank">{{ student.name }}</a>
          {% else %}
            {{ student.name }}
          {% endif %}
        </h3>
        
        <div style="margin: 10px 0; display: flex; gap: 20px;">
          {% if student.email %}
            <div style="display: flex; align-items: center;">
              <span class="icon icon--email" style="margin-right: 4px; display: flex; align-items: center; justify-content: center; width: 16px; height: 16px;">{% include icon-email.svg %}</span>
              <span style="color: #666;">{{ student.email | replace: '@', ' AT ' | replace: '.', ' DOT ' }}</span>
            </div>
          {% endif %}

          {% if student.twitter %}
            <div style="display: flex; align-items: center;">
              <span class="icon icon--twitter" style="margin-right: 4px; display: flex; align-items: center; justify-content: center; width: 16px; height: 16px;">{% include icon-twitter.svg %}</span>
              <a href="https://twitter.com/{{ student.twitter }}" target="_blank" style="color: #0366d6; text-decoration: none;">@{{ student.twitter }}</a>
            </div>
          {% endif %}
          {% if student.google_scholar %}
            <div style="display: flex; align-items: center;">
              <span class="icon icon--google_scholar" style="margin-right: 4px; display: flex; align-items: center; justify-content: center; width: 16px; height: 16px;">{% include icon-google_scholar.svg %}</span>
              <a href="{{ student.google_scholar }}" target="_blank" style="color: #0366d6; text-decoration: none;">Google Scholar</a>
            </div>
          {% endif %}
        </div>
        
        <p style="color: #666; font-size: 20px;">{{ student.keywords }}</p>
      </div>
</div>

{% endfor %}

{% endfor %}
