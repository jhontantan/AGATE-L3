function myFunction() {
    var x = document.getElementById("hideImport");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

(function () {

    var $alertMsg = $("#alertMsg");

    // function configListeners() {
    //     $alertMsg.on("close.bs.alert", function () {
    //         $alertMsg.hide();
    //         return false;
    //     });
    // }
})();