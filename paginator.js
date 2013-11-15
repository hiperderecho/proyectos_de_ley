$.getJSON( "html.json", function(data){
    var myarray = [];
    $.each( data, function( key, val) {
        myarray.push(val);
    });
    //console.log(myarray.sort().reverse());
    myarray.sort().reverse();
    $("#contenido").html(myarray.slice(0,20));

    // number of pages (20 items per page)
    var n_pages = parseInt(myarray.length / 20) + 1;
    //
    // init bootpag
    $('#page-selection').bootpag({
        total: n_pages,
        page: 1,
        maxVisible: 20
    }).on("page", function(event, /* page number here */ num){
        var start = 20;
        var end = start*num;
        console.log(myarray.slice(end - 20, end));
        $("#contenido").fadeOut("fast", function() {
            $("#contenido").fadeIn("slow", function(){}).html(myarray.slice(end - 20, end)); // some ajax content loading...
            $('html, body').animate({ scrollTop: 0 }, 0);
        });
    });
});
