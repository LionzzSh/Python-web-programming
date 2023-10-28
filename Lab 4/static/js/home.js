$(function() {
  $(".typed").typed({
    strings: [
      "Lionzz<br/>" +
      "><span class='caret'>$</span> job: Student :) <br/> ^100" +
      "><span class='caret'>$</span> skills: Windows, c++, python, js, java, php.<br/> ^100" +
      "><span class='caret'>$</span> hobbies: Voiceover, video editing, dubbing, sound processing.<br/> ^300" 
    ],
    showCursor: true,
    cursorChar: '_',
    autoInsertCss: true,
    typeSpeed: 0.001,
    startDelay: 50,
    loop: false,
    showCursor: false,
    onStart: $('.message form').hide(),
    onStop: $('.message form').show(),
    onTypingResumed: $('.message form').hide(),
    onTypingPaused: $('.message form').show(),
    onComplete: $('.message form').show(),
    onStringTyped: function(pos, self) {$('.message form').show();},
  });
  $('.message form').hide()
});
