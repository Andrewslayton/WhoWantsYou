$(document).ready(function () {
  $(".match-form").submit(function (event) {
    event.preventDefault();
    const form = $(this);
    const profileCard = form.closest(".profile-card");
    $.post(form.attr("action"), function (data) {
      profileCard.hide();
    });
  });

  $(".zoom-trigger").click(function (event) {
    event.stopPropagation();
    openFullscreen($(this).prev()[0]);
  });
});

function openFullscreen(element) {
  if (element.requestFullscreen) {
    element.requestFullscreen();
  } else if (element.mozRequestFullScreen) {
    element.mozRequestFullScreen();
  } else if (element.webkitRequestFullscreen) {
    element.webkitRequestFullscreen();
  } else if (element.msRequestFullscreen) {
    element.msRequestFullscreen();
  }
}
