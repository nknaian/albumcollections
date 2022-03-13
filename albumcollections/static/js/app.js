(function() {
  if('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
               .then(function(registration) {
               console.log('Service Worker Registered');
               return registration;
      })
      .catch(function(err) {
        console.error('Unable to register service worker.', err);
      });
      navigator.serviceWorker.ready.then(function(registration) {
        console.log('Service Worker Ready');
      });
    });
  }
})();

// This custom install button interface is a bit clunky.
// I'm disabling for now. I'd like to add it back in, but
// have the button be in the nav bar. Can't work out right
// now how I would 'hide' it after the app is already installed...
// let deferredPrompt;
// const btnAdd = document.querySelector('#btnAdd');

// window.addEventListener('beforeinstallprompt', (e) => {
//   console.log('beforeinstallprompt event fired');
//   e.preventDefault();
//   deferredPrompt = e;
//   btnAdd.style.visibility = 'visible';
// });

// btnAdd.addEventListener('click', (e) => {
//   btnAdd.style.visibility = 'hidden';
//   deferredPrompt.prompt();
//   deferredPrompt.userChoice
//     .then((choiceResult) => {
//       if (choiceResult.outcome === 'accepted') {
//         console.log('User accepted the A2HS prompt');
//       } else {
//         console.log('User dismissed the A2HS prompt');
//       }
//       deferredPrompt = null;
//     });
// });

// Not sure of the purpose of this? 
// window.addEventListener('appinstalled', (evt) => {
//   app.logEvent('app', 'installed');
// });
