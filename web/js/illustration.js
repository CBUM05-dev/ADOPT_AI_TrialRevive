// Bibliothèque d'illustrations : personnages et icônes de laboratoire en dessin vectoriel plat (trait noir, aplats verts).
// L'illustration d'accueil et les petites illustrations de chaque page sont composées avec les mêmes pièces.
const INK = "#1a1a1a", GREEN = "#6fcf9f", MINT = "#b8ecd2", SW = 2.5;

/* ---------- pièces (coordonnées locales) ---------- */
const TUBES = `
  <g><path d="M0 6h22v66a11 11 0 0 1-22 0z" fill="#fff"/><path d="M0 40h22v32a11 11 0 0 1-22 0z" fill="${GREEN}"/><rect x="-3" y="1" width="28" height="7" rx="3.5" fill="#fff"/></g>
  <g transform="translate(36 14)"><path d="M0 6h22v52a11 11 0 0 1-22 0z" fill="#fff"/><path d="M0 34h22v24a11 11 0 0 1-22 0z" fill="${MINT}"/><rect x="-3" y="1" width="28" height="7" rx="3.5" fill="#fff"/></g>`;
const SYRINGE = `
  <rect x="0" y="-10" width="74" height="20" rx="4" fill="#fff"/><rect x="26" y="-10" width="30" height="20" fill="${GREEN}"/>
  <path d="M74 0h16M90 -9v18M0 0h-28"/><path d="M12 -10v20M26 -10v20"/>`;
const HEART = `
  <g transform="scale(2.3)">
    <path d="M12 21s-7-4.6-9.5-9.2C.8 8.4 3 4.5 6.8 4.5c2 0 3.5 1 5.2 3 1.7-2 3.2-3 5.2-3 3.8 0 6 3.9 4.3 7.3C19 16.4 12 21 12 21z" fill="${GREEN}" stroke-width="1.1"/>
    <path d="M1.5 12.5h5l2-4 3.4 8 2.4-6 1.4 2h6.8" stroke-width="1.1"/>
  </g>`;
const MOLECULE = `
  <path d="M12 30L40 8 72 26 62 60 28 62Z"/><path d="M40 8L38 -10"/>
  <circle cx="12" cy="30" r="8" fill="#fff"/><circle cx="40" cy="8" r="8" fill="${GREEN}"/><circle cx="72" cy="26" r="8" fill="#fff"/>
  <circle cx="62" cy="60" r="8" fill="#fff"/><circle cx="28" cy="62" r="8" fill="${MINT}"/><circle cx="38" cy="-10" r="5" fill="${GREEN}"/>`;
const KIT = `
  <path d="M17 24v-9a5 5 0 0 1 5-5h18a5 5 0 0 1 5 5v9"/><rect x="0" y="24" width="62" height="46" rx="9" fill="#fff"/>
  <path d="M31 34v26M18 47h26" stroke-width="10"/><path d="M31 34v26M18 47h26" stroke="${GREEN}" stroke-width="5.5"/>`;
const CLIPBOARD = `
  <rect x="6" y="14" width="64" height="82" rx="7" fill="#fff"/><rect x="26" y="6" width="24" height="14" rx="4" fill="#d4d4d4"/>
  <path d="M18 42h40M18 56h40M18 70h22" stroke="#bdbdbd"/><path d="M44 80l7 7 13-15" stroke="${INK}" stroke-width="9"/><path d="M44 80l7 7 13-15" stroke="${GREEN}" stroke-width="4.5"/>`;
const MAGNIFIER = `
  <circle cx="34" cy="34" r="22" fill="#fff"/><path d="M50 50l24 24" stroke-width="7"/>
  <path d="M25 25l18 18M43 25L25 43" stroke="${INK}" stroke-width="9"/><path d="M25 25l18 18M43 25L25 43" stroke="${GREEN}" stroke-width="4.5"/>`;
const PLUS = `<path d="M0 -7v14M-7 0h14" stroke="${GREEN}" stroke-width="3.5"/>`;

/* ---------- personnages (coordonnées de l'illustration d'accueil) ---------- */
const DOCTOR = `
  <path d="M262 340l8-124q4-30 42-38h50q38 8 42 38l8 124z" fill="#fff"/>
  <path d="M310 190h60l-6 150h-48z" fill="${GREEN}"/>
  <path d="M318 186q-6 60 32 74 38-14 32-74" fill="none" stroke-width="3"/>
  <circle cx="350" cy="262" r="7" fill="#d9d9d9"/>
  <rect x="338" y="158" width="24" height="34" fill="#f1c7a3"/>
  <ellipse cx="350" cy="130" rx="31" ry="37" fill="#f1c7a3"/>
  <path d="M319 124q-3-38 33-38 34 0 29 38-7-20-29-20-22 0-33 20z" fill="#2b2b2b"/>
  <circle cx="338" cy="132" r="9"/><circle cx="362" cy="132" r="9"/><path d="M347 132h6"/>
  <circle cx="338" cy="132" r="2" fill="${INK}" stroke="none"/><circle cx="362" cy="132" r="2" fill="${INK}" stroke="none"/>
  <path d="M340 152q10 8 20 0"/>`;
const MAN = `
  <path d="M168 340l8-104q4-28 40-34h40q36 6 40 34l8 104z" fill="${GREEN}"/>
  <path d="M228 202l15 26 15-26z" fill="#8c5a3c"/>
  <path d="M182 266l108 30M296 266l-108 30" stroke-width="31"/>
  <path d="M182 266l108 30M296 266l-108 30" stroke="${GREEN}" stroke-width="26"/>
  <circle cx="292" cy="297" r="11" fill="#8c5a3c"/><circle cx="184" cy="297" r="11" fill="#8c5a3c"/>
  <rect x="231" y="176" width="24" height="28" fill="#8c5a3c"/>
  <ellipse cx="243" cy="152" rx="30" ry="36" fill="#8c5a3c"/>
  <ellipse cx="212" cy="156" rx="5" ry="8" fill="#8c5a3c"/><ellipse cx="274" cy="156" rx="5" ry="8" fill="#8c5a3c"/>
  <path d="M213 146q-1-35 31-35 31 0 30 35-7-18-30-18-23 0-31 18z" fill="#1d1d1d"/>
  <circle cx="233" cy="154" r="2.4" fill="${INK}" stroke="none"/><circle cx="255" cy="154" r="2.4" fill="${INK}" stroke="none"/>
  <path d="M233 171q10 8 20 0"/>`;
const NURSE = `
  <path d="M410 340l6-96q4-28 34-34h50q30 6 34 34l6 96z" fill="${GREEN}"/>
  <path d="M462 210l13 22 13-22z" fill="#e3ab83"/>
  <rect x="463" y="186" width="24" height="26" fill="#e3ab83"/>
  <ellipse cx="475" cy="162" rx="29" ry="34" fill="#e3ab83"/>
  <path d="M445 158q-2-36 31-36 34 0 30 36-8-18-30-18-22 0-31 18z" fill="#2b2b2b"/><circle cx="476" cy="110" r="14" fill="#2b2b2b"/>
  <path d="M447 166q28-9 56 0l-4 26q-24 10-48 0z" fill="${MINT}"/><path d="M447 168l-9-7M503 168l9-7"/>
  <circle cx="464" cy="152" r="2.4" fill="${INK}" stroke="none"/><circle cx="486" cy="152" r="2.4" fill="${INK}" stroke="none"/>
  <rect x="442" y="260" width="64" height="80" rx="6" fill="#fff"/><rect x="462" y="254" width="26" height="13" rx="3" fill="#d4d4d4"/>
  <path d="M452 286h44M452 299h44M452 312h30" stroke="#bdbdbd"/>
  <circle cx="446" cy="304" r="9" fill="#e3ab83"/><circle cx="502" cy="304" r="9" fill="#e3ab83"/>`;

const NS = 'xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" stroke-linejoin="round"';
const wrap = (viewBox, inner, label) =>
  `<svg viewBox="${viewBox}" role="img" aria-label="${label}" ${NS}><g stroke="${INK}" stroke-width="${SW}">${inner}</g></svg>`;

/* ---------- illustration d'accueil ---------- */
export const ILLUSTRATION = `
<svg viewBox="0 0 700 300" role="img" aria-label="Trois chercheurs en tenue de laboratoire entourés d'icônes médicales" ${NS}>
  <g stroke="${INK}" stroke-width="${SW}">
    <g transform="translate(68 84)">${TUBES}</g>
    <g transform="translate(88 232) rotate(-38)">${SYRINGE}</g>
    <g transform="translate(250 18)">${HEART}</g>
    <g transform="translate(404 6) scale(0.92)">${MOLECULE}</g>
    <g transform="translate(596 206)">${KIT}</g>
    <g transform="translate(168 65)">${PLUS}</g><g transform="translate(632 156)">${PLUS}</g>
    <circle cx="214" cy="40" r="3.5" fill="${GREEN}" stroke="none"/><circle cx="612" cy="210" r="4" fill="${MINT}" stroke="none"/>
    ${DOCTOR}${MAN}${NURSE}
  </g>
</svg>`;

/* ---------- petites illustrations de pages ---------- */
export const ART = {
  tubes: wrap("-6 -2 70 94", TUBES, "Tubes à essai"),
  syringe: wrap("-30 -70 112 100", `<g transform="rotate(-38)">${SYRINGE}</g>`, "Seringue"),
  heart: wrap("0 4 56 52", HEART, "Cœur et pouls"),
  molecule: wrap("0 -20 88 96", MOLECULE, "Molécule"),
  kit: wrap("-4 6 70 70", KIT, "Trousse de secours"),
  clipboard: wrap("0 0 76 100", CLIPBOARD, "Presse-papiers"),
  magnifier: wrap("0 0 84 84", MAGNIFIER, "Loupe"),
  doctor: wrap("255 80 192 220", DOCTOR, "Chercheur en blouse blanche"),
  man: wrap("160 105 180 195", MAN, "Chercheur en tenue verte"),
  nurse: wrap("405 92 140 208", NURSE, "Chercheuse avec masque et presse-papiers"),
  plus: `<svg viewBox="-9 -9 18 18" aria-hidden="true" ${NS}><g>${PLUS}</g></svg>`,
};
