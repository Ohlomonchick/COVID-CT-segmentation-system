var counter = 0;

$(document).ready(function() {
    $( "#load_form" ).submit(function( event ) {
        if (counter < 1) {
      event.preventDefault();
      counter = counter + 1;

      var post_data = new FormData($("form")[0]);

      $.ajax({
          xhr: function() {
            var xhr = new window.XMLHttpRequest();
            var new_div = document.createElement('div');

            new_div.innerHTML = '<progress id="progressBar" value="0" max="100" style="width:300px;"></progress><h3 id="status"></h3><p id="loaded_n_total"></p>';
            document.getElementsByClassName('archive-form')[0].appendChild(new_div)

            xhr.upload.addEventListener("progress", progressHandler, false);
            xhr.addEventListener("load", completeHandler, false);
            xhr.addEventListener("error", errorHandler, false);
            xhr.addEventListener("abort", abortHandler, false);

            return xhr;
          },
            url: window.location.href,// to allow add and edit
            type: "POST",
            data: post_data,
            processData: false,
            contentType: false,
            success: function() {
                  $(".main").css('display', 'none');
                  $(".footer").css('display', 'none');
                  $( "#load_form" ).submit();

              // event.initEvent();
              // xhr.close();
          }
        });
      }
    });
});


function _(el) {
  return document.getElementById(el);
}

function progressHandler(event) {
  _("loaded_n_total").innerHTML = "Uploaded " + event.loaded + " bytes of " + event.total;
  var percent = (event.loaded / event.total) * 100;
  _("progressBar").value = Math.round(percent);
  _("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
  _("status").innerHTML = event.target.responseText;
  _("progressBar").value = 0; //wil clear progress bar after successful upload
}

function errorHandler(event) {
  _("status").innerHTML = "Upload Failed";

}

function abortHandler(event) {
  _("status").innerHTML = "Upload Aborted";
}