    var pubbtn = document.getElementById("pub-btn");
    var privbtn = document.getElementById("priv-btn");

    var pub = document.getElementById("pub");
    var priv = document.getElementById("priv");

    pubbtn.onclick = function(){
        if (priv.style.display != "none"){
            priv.style.display = "none";
            pub.style.display = "block";

            privbtn.style.border= "none";
            pubbtn.style.borderStyle = "solid";
            pubbtn.style.bordeColor = "beige";

         
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

        
        }else{
            priv.style.display = "block"
        }
        
    }