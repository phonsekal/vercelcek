# Panduan: Tambah Fitur "Tidak Ditemukan" ke Google Apps Script

## Langkah 1: Buka Google Apps Script

1. Buka https://script.google.com
2. Klik project yang terhubung ke spreadsheet:
   `1CtWwWaMNW8lhkAHsCUhSNHBZxGAWlTrqDABzRM4_wkk`

## Langkah 2: Tambah 2 Fungsi Baru

Copy-paste kode di bawah ini ke **bawah** fungsi `doGet` / `doPost` yang sudah ada:

```javascript
// ============================================================
// FITUR: TIDAK DITEMUKAN (Checkbox → Kolom H)
// ============================================================

function handleCheckbox(e) {
  var data = JSON.parse(e.postData.contents);
  var nup = String(data.nup).trim();
  var checked = data.checked;
  var ss = SpreadsheetApp.openById('1CtWwWaMNW8lhkAHsCUhSNHBZxGAWlTrqDABzRM4_wkk');
  var sheet = ss.getSheets()[0];

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return ContentService.createTextOutput(JSON.stringify({status:'success'})).setMimeType(ContentService.MimeType.JSON);

  var nupData = sheet.getRange(2, 4, lastRow - 1, 1).getValues(); // Kolom D = NUP

  for (var i = 0; i < nupData.length; i++) {
    if (String(nupData[i][0]).trim() === nup) {
      sheet.getRange(i + 2, 8).setValue(checked ? 'YA' : ''); // Kolom H
      break;
    }
  }

  return ContentService.createTextOutput(JSON.stringify({status:'success'})).setMimeType(ContentService.MimeType.JSON);
}

function handleCheckCheckbox(e) {
  var nupParam = e.parameter.checkbox_nups || '';
  if (!nupParam) return ContentService.createTextOutput(JSON.stringify({status:'success',checked_nups:[]})).setMimeType(ContentService.MimeType.JSON);

  var nups = nupParam.split(',');
  var ss = SpreadsheetApp.openById('1CtWwWaMNW8lhkAHsCUhSNHBZxGAWlTrqDABzRM4_wkk');
  var sheet = ss.getSheets()[0];

  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return ContentService.createTextOutput(JSON.stringify({status:'success',checked_nups:[]})).setMimeType(ContentService.MimeType.JSON);

  var nupData = sheet.getRange(2, 4, lastRow - 1, 1).getValues(); // Kolom D
  var hData = sheet.getRange(2, 8, lastRow - 1, 1).getValues();   // Kolom H

  var checkedNups = [];
  var nupSet = {};
  nups.forEach(function(n) { nupSet[n.trim()] = true; });

  for (var i = 0; i < nupData.length; i++) {
    var cur = String(nupData[i][0]).trim();
    if (nupSet[cur] && String(hData[i][0]).trim() === 'YA') {
      checkedNups.push(cur);
    }
  }

  return ContentService.createTextOutput(JSON.stringify({status:'success',checked_nups:checkedNups})).setMimeType(ContentService.MimeType.JSON);
}
```

## Langkah 3: Edit Fungsi `doPost` yang Sudah Ada

Cari fungsi `doPost(e)` yang sudah ada, lalu **tambahkan** case ini di dalamnya:

```javascript
function doPost(e) {
  var data = JSON.parse(e.postData.contents);

  // ... case lain yang sudah ada ...

  // TAMBAHKAN INI:
  if (data.action === 'checkbox') {
    return handleCheckbox(e);
  }

  // ... sisa kode ...
}
```

## Langkah 4: Edit Fungsi `doGet` yang Sudah Ada

Cari fungsi `doGet(e)` yang sudah ada, lalu **tambahkan** di bagian awal:

```javascript
function doGet(e) {
  // TAMBAHKAN INI di paling atas:
  if (e.parameter.checkbox_nups) {
    return handleCheckCheckbox(e);
  }

  // ... kode lama yang sudah ada ...
}
```

## Langkah 5: Deploy Ulang

1. Klik **Deploy** → **New Deployment**
2. Pilih type: **Web app**
3. Execute as: **Me**
4. Who has access: **Anyone**
5. Klik **Deploy**
6. Copy URL baru (atau gunakan URL yang sama jika update deployment)

## Selesai!

Setelah deploy, fitur checkbox "Tidak Ditemukan" akan:
- ✅ Menyimpan centangan ke kolom H spreadsheet
- ✅ Menampilkan centangan saat user lain search
- ✅ Bertahan meskipun Vercel di-restart
