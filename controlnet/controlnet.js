AWS.config.region = 'eu-west-1'; // Region

AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'eu-west-1:daac3c5a-13e3-4c7d-80d8-869eacaa0f83',
});

var bucketName = 'visualneurons.com-logos'; // Enter your bucket name
var bucket = new AWS.S3({
    params: {
        Bucket: bucketName
    }
});

var fileChooser = document.getElementById('file-chooser');
var button = document.getElementById('upload-button');
var results = document.getElementById('results');

function validateEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

button.addEventListener('click', function() {
    email = document.getElementById('email').value.toLowerCase();

    if (validateEmail(email) == false) {
        results.textContent = "Please enter a valid email address and try again!"
        setTimeout(function() {
            results.textContent = ''
        }, 2000);
        return
    }

    var file = fileChooser.files[0];

    if (file) {
        this.disabled = true;
        button.style.backgroundColor = "#ffc477"
        button.textContent = "Uploaded"

        results.textContent = '';
        clean_email = email.replace('@', '_at_')
        var objKey = clean_email + '/' + file.name.replace(/[^a-zA-Z0-9.]/g, '_');
        var params = {
            Key: objKey,
            ContentType: file.type,
            Body: file,
            Metadata: {
                'email': email,
            },
        };

        bucket.putObject(params, function(err, data) {
            if (err) {
                results.textContent = 'ERROR: ' + err;
            } else {
                results.textContent = "Logo uploaded successfully!";
            }
        });
    } else {
        results.textContent = 'Nothing to upload.';
    }
}, false);