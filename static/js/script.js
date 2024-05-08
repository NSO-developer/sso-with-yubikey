// https://www.geeksforgeeks.org/create-otp-input-field-using-html-css-and-javascript/
const inputs = document.getElementById("otp_key");
const body = document.getElementById("body");
const form = document.getElementById("inputs");


window.addEventListener("keydown", function (e) {
    const val = e.key;
    const orig_val = inputs.value;
    if (val === 'Enter') {
        form.submit();
    } else if (val === 'Backspace') {
        inputs.setAttribute('value', "");
    }
    else {
        inputs.setAttribute('value', orig_val + val);
    }

});


function sendData(acs_form, status) {
    const fd = new FormData(acs_form);
    const Http_ACS = new XMLHttpRequest();
    const url_acs = "http://localhost:8080/sso/saml/acs/";
    Http_ACS.open("POST", url_acs);
    Http_ACS.send(fd);

    Http_ACS.onreadystatechange = (e) => {
        status.innerHTML = Http_ACS.responseText;
        console.log(Http_ACS.responseText);
    }
}

function register(acs_form, status) {
    const fd = new FormData(acs_form);
    const Http_ACS = new XMLHttpRequest();
    const url_acs = "http://localhost:8000/sso/saml/acs/";
    Http_ACS.open("POST", url_acs);
    Http_ACS.send(fd);

    Http_ACS.onreadystatechange = (e) => {
        status.innerHTML = Http_ACS.responseText;
        console.log(Http_ACS.responseText);
    }
}

function auth_next() {
    const Http = new XMLHttpRequest();
    const url = 'http://localhost:8000/saml/login/process/';
    Http.open("GET", url);
    Http.send();

    const status = document.getElementById("status");

    Http.onreadystatechange = (e) => {
        console.log(Http.responseText);
        const iframe=document.getElementById("dummyframe").contentWindow.document;
        //status.innerHTML = Http.responseText;
        //const acs_form = document.getElementById("logged_in_post_form");
        iframe.open();
        iframe.write(Http.responseText);
        iframe.close();

        // setTimeout(function(){
        //     location.replace("http://localhost:8080/")
        // }, 2000);


        //acs_form.submit()
        //sendData(acs_form, status)
        // acs_form.addEventListener("submit", (event) => {
        //     event.preventDefault();
        //     // sendData(acs_form, status)
        // });

        //acs_form.submit();



    }
    return Http.responseText;
}

function redirect() {
    setTimeout(function(){
        location.replace("http://localhost:8080/sso/saml/login/")
    }, 2000);
}


