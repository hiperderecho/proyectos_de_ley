$.getJSON( "html.json", function(data){
    var myarray = [];
    $.each( data, function( key, val) {
        myarray.push(val);
    });

    // init bootpag
    $('#page-selection').bootpag({
        total: 10,
        page: 1,
        maxVisible: 10
    }).on("page", function(event, /* page number here */ num){
        var start = 10;
        var end = start*num;
        console.log(myarray.slice(end - 10, end));
        $("#contenido").fadeOut("fast", function() {
            $("#contenido").fadeIn("slow", function(){}).html(myarray.slice(end - 10, end)); // some ajax content loading...
        });
    });
});
