document.addEventListener("DOMContentLoaded", function () {
    const circles = document.querySelectorAll(".circle"),
        progressBar = document.querySelector(".indicator"),
        buttons = document.querySelectorAll("button"),
        formSections = document.querySelectorAll(".form-section");

    let currentStep = 1;

    const updateSteps = (e) => {
        currentStep = e.target.id === "next" ? ++currentStep : --currentStep;

        circles.forEach((circle, index) => {
            circle.classList[`${index < currentStep ? "add" : "remove"}`]("active");
        });

        progressBar.style.width = `${((currentStep - 1) / (circles.length - 1)) * 100}%`;

        formSections.forEach((section, index) => {
            section.classList[`${index + 1 === currentStep ? "add" : "remove"}`]("active");
        });

        buttons[0].disabled = currentStep === 1;
        buttons[1].disabled = currentStep === circles.length;

        if (currentStep === circles.length) {
            buttons[1].style.display = "none";
            document.getElementById("submitBtn").style.display = "block";
        } else {
            buttons[1].style.display = "inline-block";
            document.getElementById("submitBtn").style.display = "none";
        }
    };

    buttons.forEach((button) => {
        button.addEventListener("click", updateSteps);
    });

    document.getElementById('internetService').addEventListener('change', function() {
        var value = this.value;
        var fields = ['onlineSecurity', 'onlineBackup', 'deviceProtection', 'techSupport', 'streamingTV', 'streamingMovies'];

        if (value === 'Aucun') {
            fields.forEach(function(field) {
                var selectField = document.getElementById(field);
                selectField.value = 'Aucun service internet';
                selectField.disabled = true;
            });
        } else {
            fields.forEach(function(field) {
                var selectField = document.getElementById(field);
                selectField.disabled = false;
                selectField.value = 'Sélectionner';
            });
        }
    });

    document.getElementById('phoneService').addEventListener('change', function() {
        var value = this.value;
        var fields = ['multipleLines'];

        if (value === 'Non') {
            fields.forEach(function(field) {
                var selectField = document.getElementById(field);
                selectField.value = 'Aucun service téléphonique';
                selectField.disabled = true;
            });
        } else {
            fields.forEach(function(field) {
                var selectField = document.getElementById(field);
                selectField.disabled = false;
                selectField.value = 'Sélectionner';
            });
        }
    });
});
