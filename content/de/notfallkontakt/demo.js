const get = (id) => document.getElementById(`emergency-${id}`);

const contactForm = get("contact-form");
const codeForm = get("code-form");
const code = get("code");
const success = get("success");
const firstName = get("first-name");
const initial = get("initial");
const phone = get("phone");
const exampleNumber = "000 000 00 00";

get("contact-fields").disabled = false;

get("fill").addEventListener("click", () => {
  firstName.value = "Lina";
  initial.value = "M";
  phone.value = exampleNumber;
  phone.setCustomValidity("");
  firstName.focus();
});

phone.addEventListener("input", () => phone.setCustomValidity(""));
code.addEventListener("input", () => code.setCustomValidity(""));

contactForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (phone.value.replace(/\s/g, "") !== exampleNumber.replace(/\s/g, "")) {
    phone.setCustomValidity("Verwende für diese Vorschau die Nummer 000 000 00 00.");
    phone.reportValidity();
    return;
  }
  contactForm.hidden = true;
  codeForm.hidden = false;
  get("code-title").focus();
});

get("back").addEventListener("click", () => {
  codeForm.reset();
  code.setCustomValidity("");
  codeForm.hidden = true;
  contactForm.hidden = false;
  firstName.focus();
});

codeForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (code.value !== "246810") {
    code.setCustomValidity("Der Code stimmt nicht. Der Testcode lautet 246810.");
    code.reportValidity();
    return;
  }
  const duration = new FormData(contactForm).get("dauer");
  get("expiry").textContent = duration === "saison"
    ? `Die Nummer wird im Beispiel am ${get("season-end").textContent} bei Platzschluss gelöscht.`
    : "Die Nummer wird im Beispiel heute bei Platzschluss gelöscht.";
  contactForm.reset();
  codeForm.reset();
  codeForm.hidden = true;
  success.hidden = false;
  get("success-title").focus();
});

get("restart").addEventListener("click", () => {
  success.hidden = true;
  contactForm.hidden = false;
  firstName.focus();
});
