document.addEventListener('DOMContentLoaded', () => {
  liff.init({ liffId: "2004358826-q4kZAA2J" })
      .then(() => {
          console.log('LIFF initialized');
      })
      .catch((error) => {
          console.log('LIFF initialization failed', error);
      });
});

// Qrcode scanner需要 login
document.getElementById('scanButton').addEventListener('click', () => {
  if (!liff.isLoggedIn()) {
      liff.login();
      return;
  }
  liff.scanCodeV2()
      .then(result => {
          // Handle the scan result
          const resultElement = document.getElementById('result');
          resultElement.textContent = `QR Code result: ${result.value}`;
      })
      .catch(error => {
          console.error('Scan failed', error);
      });
});