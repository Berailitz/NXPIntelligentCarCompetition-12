'use strict;'

function showToast(messageText, timeout = 1000) {
  console.log(`Toast: ${messageText}`);
  $('#snackbar')[0].MaterialSnackbar.showSnackbar({
    'message': messageText,
    'timeout': timeout,
  });
}

export {showToast};
