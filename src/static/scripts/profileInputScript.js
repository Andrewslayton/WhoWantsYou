/*
This file stores the functions that are called on within the index.html file. 
**handles the placeholder card with the plus in the middle and allows it to accept a file.
** handles the zoom icon only after a file has been uploaded. Styling for this is in stylesheet.css
** Overlays the image to almost full screen(purposfully different than other fullscreen function to incentivise user to not look to long and finish craeting profile.)
*/
$(document).ready(function() {
$('.upload-placeholder').on('click', function() {
    const inputId = $(this).data('input');
    $('#' + inputId).trigger('click');
});
$('.image-input').on('change', function() {
  const input = $(this);
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        input.siblings('.image-preview').attr('src', e.target.result).show();
        input.siblings('.zoom-icon').show();
        input.siblings('.upload-placeholder').hide();
    }
    reader.readAsDataURL(file);
  }
});
$('.zoom-icon').on('click', function() {
  const src = $(this).siblings('.image-preview').attr('src');
  const overlay = $('<div>').css({
    background: `rgba(0,0,0,0.8) url(${src}) no-repeat center`,
    backgroundSize: 'contain',
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    zIndex: 1000,
    cursor: 'pointer'
  }).on('click', function() {
    $(this).remove();
  });

  $('body').append(overlay);
});
});