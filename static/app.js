var main = function() {
    $('.btn').click(function(){
        var post = $('.status-box').val();
        $('<li>').text(post).prependTo('.posts');
        //Clear value in the status box once posted
        $('.status-box').val('');
        //return .counter to 1000 when status posts
        $('.counter').text('1000');
        //make .btn disabled once status is posts
        $('.btn').addClass('disabled');
    });
  
/*  	//Remove post
  	$('.btn-danger').click(function(){
      	$('.selected').remove();
      
      	$('.posts li').addClass('selected');
    });*/
    
    //count down the 1000 characters
    $('.status-box').keyup(function(){
        var postLength = $(this).val().length;
        var charactersLeft = 1000 - postLength;
        $('.counter').text(charactersLeft);
        
        //check to see if characters in post are elidgible to post
        if(charactersLeft < 0) {
            //make button disabled if charcters are < 0
            $('.btn').addClass('disabled');
        }
        else if (charactersLeft === 1000) {
            //make button disabled if charcters are 140
            $('.btn').addClass('disabled');
        }
        else {
            //make button disabled if charcters anything else
            $('.btn').removeClass('disabled');
        }
    });
    
    $('.btn').addClass('disabled');
};

$(document).ready(main);