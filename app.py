LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="PAVEL IA CV">
<defs>
  <linearGradient id="logoBg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#168B8B"/>
    <stop offset="50%" stop-color="#0E6B6B"/>
    <stop offset="100%" stop-color="#073F42"/>
  </linearGradient>

  <linearGradient id="paperShine" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFFFFF"/>
    <stop offset="55%" stop-color="#FFFFFF"/>
    <stop offset="100%" stop-color="#DCEEEF"/>
  </linearGradient>

  <linearGradient id="goldShine" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFE7A3"/>
    <stop offset="45%" stop-color="#F2A93B"/>
    <stop offset="75%" stop-color="#FFD66B"/>
    <stop offset="100%" stop-color="#C77B13"/>
  </linearGradient>

  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="1.4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="45%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="55%" stop-color="#FFFFFF" stop-opacity=".75"/>
    <stop offset="65%" stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
  </linearGradient>

  <clipPath id="logoClip">
    <rect width="64" height="64" rx="16"/>
  </clipPath>
</defs>

<rect width="64" height="64" rx="16" fill="url(#logoBg)"/>

<g clip-path="url(#logoClip)">
  <path d="M-20 10 L30 -20 L85 35 L35 85 Z"
        fill="url(#shine)"
        opacity=".45"/>
</g>

<path d="M18 12h18l10 10v26a3 3 0 0 1-3 3H18a3 3 0 0 1-3-3V15a3 3 0 0 1 3-3z"
      fill="url(#paperShine)"
      filter="url(#glow)"/>

<path d="M36 12v7a3 3 0 0 0 3 3h7z"
      fill="#B7D6D6"/>

<rect x="21" y="27" width="16" height="3" rx="1.5" fill="#0E6B6B"/>
<rect x="21" y="34" width="11" height="3" rx="1.5" fill="#9CC3C3"/>

<circle cx="44" cy="44" r="10"
        fill="url(#goldShine)"
        stroke="#0E6B6B"
        stroke-width="3"
        filter="url(#glow)"/>

<path d="M39.5 44.5l3.3 3.3 6-6.6"
      fill="none"
      stroke="#12272B"
      stroke-width="2.8"
      stroke-linecap="round"
      stroke-linejoin="round"/>

<circle cx="23" cy="17" r="1.2" fill="#FFFFFF" opacity=".9"/>
<circle cx="49" cy="15" r=".9" fill="#FFFFFF" opacity=".7"/>
<circle cx="53" cy="37" r=".8" fill="#FFE7A3" opacity=".8"/>
</svg>"""
