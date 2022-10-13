    var pubbtn = document.getElementById("pub-btn");
    console.log(pubbtn);
    var privbtn = document.getElementById("priv-btn");
    console.log(privbtn);

    var pub = document.getElementById("pub");
    console.log(pub);
    var priv = document.getElementById("priv");
    console.log(priv);

    pubbtn.onclick = function(){
        if (priv.style.display != "none"){
            priv.style.display = "none";
            pub.style.display = "block";

            privbtn.style.border= "none";
            pubbtn.style.borderStyle = "solid";
            pubbtn.style.bordeColor = "beige";

            console.log("publico");
        }else{
            pub.style.display = "block"
        }
        
    }

    privbtn.onclick = function(){
        if (pub.style.display != "none"){
            pub.style.display = "none";
            priv.style.display = "block";

            pubbtn.style.border= "none";
            privbtn.style.borderStyle = "solid";
            privbtn.style.bordeColor = "beige";

            console.log("privado");
        }else{
            priv.style.display = "block"
        }
        
    }