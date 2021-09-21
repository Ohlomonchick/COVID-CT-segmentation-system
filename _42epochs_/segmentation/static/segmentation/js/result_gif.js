$(document).ready(function() {
    $( ".form_color" ).submit(function(event) {
        $(".wait-img").attr('style', 'display: inline-block;');
        setTimeout(function() {
            $(".wait-img").css('display', 'none')
        },2000);
    });
});