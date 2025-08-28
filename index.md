---
# You don''t need to edit this file, it''s empty on purpose.
# Edit theme''s home layout instead if you wanna make some changes
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
layout: default
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

<img src="{{ site.baseurl }}/assets/images/rr.jpg" alt="Drawing" style="width: 200px;"/> 


I am an Assistant Professor in [Computer Science](https://www.cs.umd.edu/) at the University of Maryland, College Park.
I also hold appointments in [UMIACS](https://www.umiacs.umd.edu/) and [Linguistics](https://linguistics.umd.edu/) at UMD.

My research focuses on problems in natural language understanding, including
knowledge acquisition, commonsense reasoning, an semantic representation.
I am also interested in problems of bias and fairness in NLP, and in particular
how commonsense reasoning can both lead to and help overcome social
overgeneralization in NLP systems.
