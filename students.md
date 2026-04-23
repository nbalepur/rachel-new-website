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

<style>
  .student-contact-actions {
    margin: 10px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  .student-contact-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border: 1px solid #d0d7de;
    border-radius: 999px;
    color: #24292f;
    background: #f6f8fa;
    text-decoration: none;
    font-size: 14px;
    line-height: 1.2;
    cursor: pointer;
    font-family: inherit;
  }

  .student-contact-btn:hover {
    background: #eef2f6;
    text-decoration: none;
  }

  .student-contact-btn:visited,
  .student-contact-btn:active,
  .student-contact-btn:focus {
    color: #24292f;
  }

  .student-contact-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
  }

  .student-contact-icon-img {
    width: 16px;
    height: 16px;
    object-fit: contain;
    display: block;
  }

  @media (max-width: 640px) {
    .student-contact-actions {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }
  }
</style>

{% for category in site.data.students %}
## {{ category.title }}

{% for student in category.students %}
  <div style="margin-bottom: 30px; display: flex; align-items: flex-start;">
    <img src="{{ site.baseurl }}/assets/images/{% if student.image %}{{ student.image }}{% else %}default.jpg{% endif %}" 
         alt="{{ student.name }}" 
         style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; margin-right: 20px; flex-shrink: 0;">
    
           <div style="flex: 1; display: flex; flex-direction: column;">
        <h3 style="margin: 0;">{{ student.name }}</h3>
        
        <div class="student-contact-actions">
          {% if student.twitter %}
            <a href="https://twitter.com/{{ student.twitter }}" target="_blank" rel="noopener noreferrer" class="student-contact-btn">
              <span class="student-contact-icon">
                <img src="{{ site.baseurl }}/assets/icons/twitter.svg" alt="" class="student-contact-icon-img">
              </span>
              <span>Twitter</span>
            </a>
          {% endif %}

          {% if student.website %}
            <a href="{{ student.website }}" target="_blank" rel="noopener noreferrer" class="student-contact-btn">
              <span class="student-contact-icon">
                <img src="{{ site.baseurl }}/assets/icons/globe.svg" alt="" class="student-contact-icon-img">
              </span>
              <span>Website</span>
            </a>
          {% endif %}
        </div>
        
        <p style="color: #666; font-size: 20px;">{{ student.keywords }}</p>
      </div>
</div>

{% endfor %}

{% endfor %}
