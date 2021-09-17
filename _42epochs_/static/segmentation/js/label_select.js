$(document).ready(function(){
 $('#id_lung_other').change(function() {

  if(this.checked !== true){
        $('#lung_other_im').attr('style', 'display: none;')
        console.log("hHhjhhhhfff")
     }
  else {
      $('#lung_other_im').attr('style', 'display: inline-block;')
  }
});

 $('#id_consolidation').change(function() {

  if(this.checked !== true){
        $('#consolidation_im').css('display', 'none')
        console.log("hHhjhhhhfff")
     }
  else {
      $('#consolidation_im').css('display', 'inline-block;')
  }
});

 $('#id_ground_glass').change(function() {

  if(this.checked !== true){
        $('#ground_glass_im').attr('style', 'display: none;')
        console.log("hHhjhhhhfff")
     }
  else {
      $('#ground_glass_im').attr('style', 'display: inline-block;')
  }
});
});
