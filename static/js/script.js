const provincesData = {
  "Maputo Cidade": ["KaMpfumo", "Nlhamankulu", "KaMaxakeni", "KaMavota", "KaMubukwana", "KaTembe", "KaNyaka"],
  "Maputo Província": ["Boane", "Magude", "Manhiça", "Marracuene", "Matola", "Matutuíne", "Moamba", "Namaacha"],
  Gaza: ["Bilene", "Chibuto", "Chicualacuala", "Chigubo", "Chókwè", "Chongoene", "Guijá", "Limpopo", "Mabalane", "Manjacaze", "Mapai", "Massangena", "Massingir", "Xai-Xai"],
  Inhambane: ["Funhalouro", "Govuro", "Homoíne", "Inhambane", "Inharrime", "Inhassoro", "Jangamo", "Mabote", "Massinga", "Maxixe", "Morrumbene", "Panda", "Vilankulo", "Zavala"],
  Sofala: ["Beira", "Búzi", "Caia", "Chemba", "Cheringoma", "Chibabava", "Dondo", "Gorongosa", "Machanga", "Marínguè", "Marromeu", "Muanza", "Nhamatanda"],
  Manica: ["Bárue", "Gondola", "Guro", "Machaze", "Macossa", "Manica", "Mossurize", "Sussundenga", "Tambara", "Vanduzi"],
  Tete: ["Angónia", "Cahora-Bassa", "Changara", "Chifunde", "Chiúta", "Dôa", "Macanga", "Magoé", "Marara", "Moatize", "Mutarara", "Tsangano", "Zumbo"],
  "Zambézia": ["Alto Molócuè", "Chinde", "Derre", "Gilé", "Gurué", "Ile", "Inhassunge", "Luabo", "Maganja da Costa", "Milange", "Mocuba", "Mopeia", "Morrumbala", "Namacurra", "Namarrói", "Nicoadala", "Pebane", "Quelimane"],
  Nampula: ["Angoche", "Eráti", "Ilha de Moçambique", "Lalaua", "Larde", "Liúpo", "Malema", "Meconta", "Mecubúri", "Memba", "Mogincual", "Mogovolas", "Moma", "Monapo", "Mossuril", "Muecate", "Murrupula", "Nacala-a-Velha", "Nacala Porto", "Nacarôa", "Nampula", "Rapale", "Ribáuè"],
  "Cabo Delgado": ["Ancuabe", "Balama", "Chiúre", "Ibo", "Macomia", "Mecúfi", "Meluco", "Metuge", "Mocímboa da Praia", "Montepuez", "Mueda", "Muidumbe", "Namuno", "Nangade", "Palma", "Pemba", "Quissanga"],
  Niassa: ["Chimbonila", "Cuamba", "Lago", "Lichinga", "Majune", "Mandimba", "Marrupa", "Maúa", "Mavago", "Mecanhelas", "Mecula", "Metarica", "Muembe", "Ngauma", "Nipepe", "Sanga"]
};

const provinceSelect = document.getElementById('province');
const districtSelect = document.getElementById('district');
const reportForm = document.querySelector('.report-form');

if (provinceSelect && districtSelect) {
  Object.keys(provincesData).forEach(function (province) {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    provinceSelect.appendChild(option);
  });

  provinceSelect.addEventListener('change', function () {
    const selectedProvince = this.value;
    districtSelect.innerHTML = '<option value="">Selecione o Distrito</option>';

    if (!selectedProvince) {
      districtSelect.disabled = true;
      return;
    }

    provincesData[selectedProvince].forEach(function (district) {
      const option = document.createElement('option');
      option.value = district;
      option.textContent = district;
      districtSelect.appendChild(option);
    });

    districtSelect.disabled = false;
  });
}

if (reportForm) {
  reportForm.querySelectorAll('[required]').forEach(function (field) {
    field.addEventListener('input', function () {
      field.setCustomValidity('');
    });
    field.addEventListener('change', function () {
      field.setCustomValidity('');
    });
  });

  reportForm.addEventListener('submit', function (event) {
    const firstEmptyField = Array.from(reportForm.querySelectorAll('[required]')).find(function (field) {
      return !field.value.trim();
    });
    if (firstEmptyField) {
      firstEmptyField.setCustomValidity('Preencha este campo');
      firstEmptyField.reportValidity();
      event.preventDefault();
      return;
    }

    const invalidField = Array.from(reportForm.querySelectorAll('[required]')).find(function (field) {
      return !field.checkValidity();
    });
    if (invalidField) {
      invalidField.setCustomValidity('Introduza um valor válido');
      invalidField.reportValidity();
      event.preventDefault();
    }
  });
}
