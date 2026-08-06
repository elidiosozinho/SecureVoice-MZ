const provincesData = {
  "Maputo Cidade": ["KaMpfumo", "Nlhamankulu", "KaMaxakeni", "KaMavota", "KaMubukwana", "KaTembe", "KaNyaka"],
  "Maputo Província": ["Boane", "Magude", "Manhiça", "Marracuene", "Matola", "Matutuíne", "Moamba", "Namaacha"],
  Gaza: ["Bilene", "Chibuto", "Chicualacuala", "Chigubo", "Chókwè", "Guijá", "Limpopo", "Mabalane", "Manjacaze", "Massangena", "Massingir", "Xai-Xai"],
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

if (provinceSelect && districtSelect) {
  Object.keys(provincesData).forEach(function (province) {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    provinceSelect.appendChild(option);
  });

  provinceSelect.addEventListener('change', function () {
    const selectedProvince = this.value;
    districtSelect.innerHTML = '<option value="">Select District</option>';

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
