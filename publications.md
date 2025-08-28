---
layout: page
title: Publications
header: Publications
group: navigation
---
{% comment %}
{% include JB/setup %}
{% endcomment %}

For the most up-to-date list of my publications, please visit my [Google Scholar](https://scholar.google.com/citations?user=QKCHaHUAAAAJ&hl=en&oi=ao).

{% for y in site.data.papers %}
  <p>
  <b>{{ y.year }}</b>
  {% for p in y.papers %}
    {% unless p.show == false %}
    <p>
    <i>{{ p.title }}</i>
    {{ p.authors }}.
    {% if p.venue %}
    {{ p.venue }}.
    {% endif %}

    {% if p.year != null %}
    {{ p.year }}.
    {% endif %}

    {% if p.pdf != null %}
    <a href="{{ p.pdf }}">[pdf]</a>
    {% endif %}

    {% if p.bib != null %}
    <a href="{{ p.bib }}">[bib]</a>
    {% endif %}

    {% if p.code != null %}
    <a href="{{ p.code }}">[code]</a>
    {% endif %}

    {% if p.data != null %}
    <a href="{{ p.data }}">[data]</a>
    {% endif %}
   
    </p>
    {% endunless %}
  {% endfor %}
  </p>
{% endfor %}

<br />
<p><strong>Note:</strong> This publication list was automatically parsed from Semantic Scholar. There may be inaccuracies or missing publications.</p>

