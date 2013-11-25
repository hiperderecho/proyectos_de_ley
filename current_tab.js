$(document).ready(function() {
    var pathname = window.location.pathname;
    //console.log(pathname);

    $(".nav a").each(function(index, value) {
        //console.log($(this).attr("href"));
        if (pathname.match("about") && $(this).attr('href').match("about")) {
            $(this).parent().addClass("active");
        }
        else if (pathname.match("contact") && $(this).attr('href').match("contact")) {
            $(this).parent().addClass("active");
        }
        else {
            $("#index").addClass("active");
        }
    });
});
