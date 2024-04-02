document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var syllabusNameInput = document.getElementById("syllabus-name");

    // Add an event listener for input changes
    syllabusNameInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = syllabusNameInput.value;
        var inputLength = inputValue.length;

        // Get the error message element
        var errorMessage = document.querySelector("#syllabus-name-error");

        // Define the maximum length
        var maxLength = 21;

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the error message and prevent further typing
            errorMessage.style.display = "block";
            syllabusNameInput.value = inputValue.slice(0, maxLength);
        } else {
            // Hide the error message if within the limit
            errorMessage.style.display = "none";
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var timeFrameInput = document.getElementById("time-frame");

    // Add an event listener for input changes
    timeFrameInput.addEventListener("input", function() {
        // Get the current value
        var inputValue = parseInt(timeFrameInput.value);

        // Get the error message element
        var errorMessage = document.querySelector("#time-frame-error");

        // Define the valid range
        var minRange = 18;
        var maxRange = 21;

        // Check if the value is outside the valid range
        if (isNaN(inputValue) || inputValue < minRange || inputValue > maxRange) {
            // Display the error message
            errorMessage.style.display = "block";

            // Adjust the input value to be within the valid range
            if (inputValue < minRange) {
                timeFrameInput.value = minRange;
            } else if (inputValue > maxRange) {
                timeFrameInput.value = maxRange;
            }
        } else {
            // Hide the error message if within the valid range
            errorMessage.style.display = "none";
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var collegeInput = document.getElementById("college");

    // Get the error message elements
    var lengthErrorMessage = document.querySelector("#college-length-error");
    var formatErrorMessage = document.querySelector("#college-format-error");
    var spaceErrorMessage = document.querySelector("#college-space-error");
    var charactersErrorMessage = document.querySelector("#college-characters-error");

    // Add an event listener for input changes
    collegeInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = collegeInput.value;
        var inputLength = inputValue.length;

        // Define the maximum length
        var maxLength = 57;

        // Check if the input contains more than one space
        if (/\s{2,}/.test(inputValue)) {
            // Display the space error message
            spaceErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove consecutive spaces
            setTimeout(function () {
                inputValue = inputValue.replace(/\s{2,}/g, ' ');
                collegeInput.value = inputValue;
                spaceErrorMessage.style.display = "none"; // Hide the error after removing consecutive spaces
            }, 2000);
        } else {
            // Hide the space error message if there is only one space or none
            spaceErrorMessage.style.display = "none";
        }

        // Update the input value while considering the maximum length
        collegeInput.value = inputValue.slice(0, maxLength);

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the length error message
            lengthErrorMessage.style.display = "block";
        } else {
            // Hide the length error message if within the limit
            lengthErrorMessage.style.display = "none";
        }

        // Check if the input contains the words 'college of' (case-insensitive)
        var forbiddenPhrase = 'college of';
        if (inputValue.toLowerCase().includes(forbiddenPhrase)) {
            // Remove the forbidden phrase if pasted
            collegeInput.value = inputValue.replace(new RegExp(forbiddenPhrase, "i"), '').trim();

            // Display the format error message
            formatErrorMessage.style.display = "block";
        } else {
            // Hide the format error message if the format is correct
            formatErrorMessage.style.display = "none";
        }

        // Check if the input contains any special characters
        if (/[^a-zA-Z0-9 ]/.test(inputValue)) {
            // Display the characters error message
            charactersErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove special characters
            setTimeout(function () {
                inputValue = inputValue.replace(/[^a-zA-Z0-9- ]/g, '');
                collegeInput.value = inputValue;
                charactersErrorMessage.style.display = "none"; // Hide the error after removing special characters
            }, 2000);
        } else {
            // Hide the characters error message if there are no special characters
            charactersErrorMessage.style.display = "none";
        }
    });

    // Add an event listener for paste events
    collegeInput.addEventListener("paste", function(event) {
        // Get the pasted text
        var pastedText = (event.clipboardData || window.clipboardData).getData('text');

        // Remove special characters and extra spaces from the pasted text
        pastedText = pastedText.replace(/[^\w\d- ]/g, '').replace(/\s{2,}/g, ' ').trim();

        // Set the cleaned pasted text to the input
        collegeInput.value = pastedText;
        collegeInput.dispatchEvent(new Event('input'));

        // Prevent the default paste behavior
        event.preventDefault();
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var departmentInput = document.getElementById("department");

    // Get the error message elements
    var lengthErrorMessage = document.querySelector("#department-length-error");
    var formatErrorMessage = document.querySelector("#department-format-error");
    var spaceErrorMessage = document.querySelector("#department-space-error");
    var charactersErrorMessage = document.querySelector("#department-characters-error");

    // Add an event listener for input changes
    departmentInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = departmentInput.value;
        var inputLength = inputValue.length;

        // Define the maximum length
        var maxLength = 57;

        // Check if the input contains more than one space
        if (/\s{2,}/.test(inputValue)) {
            // Display the space error message
            spaceErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove consecutive spaces
            setTimeout(function () {
                inputValue = inputValue.replace(/\s{2,}/g, ' ');
                departmentInput.value = inputValue;
                spaceErrorMessage.style.display = "none"; // Hide the error after removing consecutive spaces
            }, 2000);
        } else {
            // Hide the space error message if there is only one space or none
            spaceErrorMessage.style.display = "none";
        }

        // Update the input value while considering the maximum length
        departmentInput.value = inputValue.slice(0, maxLength);

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the length error message
            lengthErrorMessage.style.display = "block";
        } else {
            // Hide the length error message if within the limit
            lengthErrorMessage.style.display = "none";
        }

        // Check if the input contains the words 'Department of' (case-insensitive)
        var forbiddenPhrase = 'department of';
        if (inputValue.toLowerCase().includes(forbiddenPhrase)) {
            // Remove the forbidden phrase if pasted
            departmentInput.value = inputValue.replace(new RegExp(forbiddenPhrase, "i"), '').trim();

            // Display the format error message
            formatErrorMessage.style.display = "block";
        } else {
            // Hide the format error message if the format is correct
            formatErrorMessage.style.display = "none";
        }

        // Check if the input contains any special characters
        if (/[^a-zA-Z0-9 ]/.test(inputValue)) {
            // Display the characters error message
            charactersErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove special characters
            setTimeout(function () {
                inputValue = inputValue.replace(/[^a-zA-Z0-9- ]/g, '');
                departmentInput.value = inputValue;
                charactersErrorMessage.style.display = "none"; // Hide the error after removing special characters
            }, 2000);
        } else {
            // Hide the characters error message if there are no special characters
            charactersErrorMessage.style.display = "none";
        }
    });

    // Add an event listener for paste events
    departmentInput.addEventListener("paste", function(event) {
        // Get the pasted text
        var pastedText = (event.clipboardData || window.clipboardData).getData('text');

        // Remove special characters and extra spaces from the pasted text
        pastedText = pastedText.replace(/[^\w\d- ]/g, '').replace(/\s{2,}/g, ' ').trim();

        // Set the cleaned pasted text to the input
        departmentInput.value = pastedText;
        departmentInput.dispatchEvent(new Event('input'));

        // Prevent the default paste behavior
        event.preventDefault();
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var bachelorInput = document.getElementById("bachelor");

    // Get the error message elements
    var lengthErrorMessage = document.querySelector("#bachelor-length-error");
    var formatErrorMessage = document.querySelector("#bachelor-format-error");
    var spaceErrorMessage = document.querySelector("#bachelor-space-error");
    var charactersErrorMessage = document.querySelector("#bachelor-characters-error");

    // Add an event listener for input changes
    bachelorInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = bachelorInput.value;
        var inputLength = inputValue.length;

        // Define the maximum length
        var maxLength = 57;

        // Check if the input contains more than one space
        if (/\s{2,}/.test(inputValue)) {
            // Display the space error message
            spaceErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove consecutive spaces
            setTimeout(function () {
                inputValue = inputValue.replace(/\s{2,}/g, ' ');
                bachelorInput.value = inputValue;
                spaceErrorMessage.style.display = "none"; // Hide the error after removing consecutive spaces
            }, 2000);
        } else {
            // Hide the space error message if there is only one space or none
            spaceErrorMessage.style.display = "none";
        }

        // Update the input value while considering the maximum length
        bachelorInput.value = inputValue.slice(0, maxLength);

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the length error message
            lengthErrorMessage.style.display = "block";
        } else {
            // Hide the length error message if within the limit
            lengthErrorMessage.style.display = "none";
        }

        // Check if the input contains the words 'bachelor of' (case-insensitive)
        var forbiddenPhrase = 'bachelor of';
        if (inputValue.toLowerCase().includes(forbiddenPhrase)) {
            // Remove the forbidden phrase if pasted
            bachelorInput.value = inputValue.replace(new RegExp(forbiddenPhrase, "i"), '').trim();

            // Display the format error message
            formatErrorMessage.style.display = "block";
        } else {
            // Hide the format error message if the format is correct
            formatErrorMessage.style.display = "none";
        }

        // Check if the input contains any special characters
        if (/[^a-zA-Z0-9 ]/.test(inputValue)) {
            // Display the characters error message
            charactersErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove special characters
            setTimeout(function () {
                inputValue = inputValue.replace(/[^a-zA-Z0-9- ]/g, '');
                bachelorInput.value = inputValue;
                charactersErrorMessage.style.display = "none"; // Hide the error after removing special characters
            }, 2000);
        } else {
            // Hide the characters error message if there are no special characters
            charactersErrorMessage.style.display = "none";
        }
    });

    // Add an event listener for paste events
    bachelorInput.addEventListener("paste", function(event) {
        // Get the pasted text
        var pastedText = (event.clipboardData || window.clipboardData).getData('text');

        // Remove special characters and extra spaces from the pasted text
        pastedText = pastedText.replace(/[^\w\d- ]/g, '').replace(/\s{2,}/g, ' ').trim();

        // Set the cleaned pasted text to the input
        bachelorInput.value = pastedText;
        bachelorInput.dispatchEvent(new Event('input'));

        // Prevent the default paste behavior
        event.preventDefault();
    });
});


document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var courseCodeInput = document.getElementById("course-code");

    // Get the error message elements
    var lengthErrorMessage = document.querySelector("#course-code-length-error");
    var formatErrorMessage = document.querySelector("#course-code-format-error");
    var spaceErrorMessage = document.querySelector("#course-code-space-error");

    // Add an event listener for input changes
    courseCodeInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = courseCodeInput.value;
        var inputLength = inputValue.length;

        // Define the maximum length
        var maxLength = 15;

        // Check if the input contains more than one space
        if (/\s{2,}/.test(inputValue)) {
            // Display the space error message
            spaceErrorMessage.style.display = "block";

            // Delay for 0.5 seconds and then remove consecutive spaces
            setTimeout(function () {
                inputValue = inputValue.replace(/\s{2,}/g, ' ');
                courseCodeInput.value = inputValue;
                spaceErrorMessage.style.display = "none"; // Hide the error after removing consecutive spaces
            }, 2000);
        } else {
            // Hide the space error message if there is only one space or none
            spaceErrorMessage.style.display = "none";
        }

        // Update the input value while considering the maximum length
        courseCodeInput.value = inputValue.slice(0, maxLength);

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the length error message
            lengthErrorMessage.style.display = "block";
        } else {
            // Hide the length error message if within the limit
            lengthErrorMessage.style.display = "none";
        }

        // Check if the input contains only acceptable characters (alphanumeric, dash, and one space)
        var acceptableCharacters = /^[a-zA-Z0-9- ]+$/;
        if (!acceptableCharacters.test(courseCodeInput.value)) {
            // Display the format error message
            formatErrorMessage.style.display = "block";

            // Delay for 0.5 seconds and then remove special characters
            setTimeout(function () {
                inputValue = inputValue.replace(/[^a-zA-Z0-9- ]/g, '');
                courseCodeInput.value = inputValue;
                formatErrorMessage.style.display = "none"; // Hide the error after removing special characters
            }, 2000);
        } else {
            // Hide the format error message if the format is correct
            formatErrorMessage.style.display = "none";
        }
    });

    // Add an event listener for paste events
    courseCodeInput.addEventListener("paste", function(event) {
        // Get the pasted text
        var pastedText = (event.clipboardData || window.clipboardData).getData('text');

        // Remove special characters and extra spaces from the pasted text
        pastedText = pastedText.replace(/[^\w\d- ]/g, '').replace(/\s{2,}/g, ' ').trim();

        // Set the cleaned pasted text to the input
        courseCodeInput.value = pastedText;
        courseCodeInput.dispatchEvent(new Event('input'));

        // Prevent the default paste behavior
        event.preventDefault();
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var courseNameInput = document.getElementById("course-name");

    // Get the error message elements
    var lengthErrorMessage = document.querySelector("#course-name-length-error");
    var formatErrorMessage = document.querySelector("#course-name-format-error");
    var spaceErrorMessage = document.querySelector("#course-name-space-error");

    // Add an event listener for input changes
    courseNameInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = courseNameInput.value;
        var inputLength = inputValue.length;

        // Define the maximum length
        var maxLength = 60;

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the length error message
            lengthErrorMessage.style.display = "block";
            courseNameInput.value = inputValue.slice(0, maxLength);
        } else {
            // Hide the length error message if within the limit
            lengthErrorMessage.style.display = "none";
        }

        // Check if the input contains only acceptable characters (alphabets and one space)
        var acceptableCharacters = /^[a-zA-Z ]+$/;
        if (!acceptableCharacters.test(courseNameInput.value)) {
            // Display the format error message
            formatErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove special characters
            setTimeout(function () {
                inputValue = inputValue.replace(/[^a-zA-Z ]/g, '');
                courseNameInput.value = inputValue;
                formatErrorMessage.style.display = "none"; // Hide the error after removing special characters
            }, 2000);
        } else {
            // Hide the format error message if the format is correct
            formatErrorMessage.style.display = "none";
        }

        // Check if the input contains more than one space
        if (/\s{2,}/.test(inputValue)) {
            // Display the space error message
            spaceErrorMessage.style.display = "block";

            // Delay for 2 seconds and then remove consecutive spaces
            setTimeout(function () {
                inputValue = inputValue.replace(/\s{2,}/g, ' ');
                courseNameInput.value = inputValue;
                spaceErrorMessage.style.display = "none"; // Hide the error after removing consecutive spaces
            }, 2000);
        } else {
            // Hide the space error message if there is only one space or none
            spaceErrorMessage.style.display = "none";
        }
    });

    // Add an event listener for paste events
    courseNameInput.addEventListener("paste", function(event) {
        // Get the pasted text
        var pastedText = (event.clipboardData || window.clipboardData).getData('text');

        // Remove special characters and extra spaces from the pasted text
        pastedText = pastedText.replace(/[^a-zA-Z ]/g, '').replace(/\s{2,}/g, ' ').trim();

        // Set the cleaned pasted text to the input
        courseNameInput.value = pastedText;
        courseNameInput.dispatchEvent(new Event('input'));

        // Prevent the default paste behavior
        event.preventDefault();
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var courseCreditInput = document.getElementById("course-credit");

    // Get the error message elements
    var creditError = document.querySelector("#course-credit-error");
    var formatError = document.querySelector("#course-credit-format-error");

    // Add an event listener for input changes
    courseCreditInput.addEventListener("input", function() {
        // Get the current value
        var inputValue = courseCreditInput.value;

        // Ensure the input is a valid number within the specified range (1.0 to 3.0)
        if (isNaN(inputValue) || inputValue < 1.0 || inputValue > 3.0) {
            // Display the range error message
            creditError.style.display = "block";
            formatError.style.display = "none"; // Hide the format error message
            courseCreditInput.value = ""; // Clear the input if the value is not valid
        } else {
            // Remove leading zeros
            inputValue = inputValue.replace(/^0+/, '');

            // Check if there is a decimal point in the input
            if (inputValue.indexOf('.') !== -1) {
                // Split the input into integer and decimal parts
                var parts = inputValue.split('.');
                var integerPart = parts[0];
                var decimalPart = parts[1];

                // Ensure that the decimal part has at most two decimal places
                if (decimalPart.length > 2) {
                    // Display the format error message
                    formatError.style.display = "block";
                    creditError.style.display = "none"; // Hide the range error message
                    courseCreditInput.value = integerPart + '.' + decimalPart.slice(0, 2); // Truncate to two decimal places
                } else {
                    // Hide both error messages if the value is valid
                    creditError.style.display = "none";
                    formatError.style.display = "none";
                }
            } else {
                // Hide the format error message if there is no decimal point
                formatError.style.display = "none";
                creditError.style.display = "none"; // Hide the range error message
            }
        }
    });

});

document.addEventListener("DOMContentLoaded", function() {
    // Get the input element
    var creditDescInput = document.getElementById("course_credit_description");

    // Get the error message element
    var descError = document.querySelector("#course-credit-desc-error");

    // Add an event listener for input changes
    creditDescInput.addEventListener("input", function() {
        // Get the current value and length
        var inputValue = creditDescInput.value;
        var inputLength = inputValue.length;

        // Define the maximum length
        var maxLength = 100;

        // Check if the length exceeds the maximum
        if (inputLength > maxLength) {
            // Display the length error message
            descError.style.display = "block";
            creditDescInput.value = inputValue.slice(0, maxLength);
        } else {
            // Hide the length error message if within the limit
            descError.style.display = "none";
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Get references to the input elements and the submit button
    var syllabusNameInput = document.getElementById("syllabus-name");
    var courseNameInput = document.getElementById("course-name");
    var courseDescriptionInput = document.getElementById("course-description");
    var submitButton = document.querySelector(".save-info");
    var tooltipElement = document.querySelector("[data-bs-toggle='tooltip']");

    // Initialize Bootstrap Tooltip
    var tooltip = new bootstrap.Tooltip(tooltipElement);

    // Add an event listener for input changes on all three inputs
    syllabusNameInput.addEventListener("input", checkInputs);
    courseNameInput.addEventListener("input", checkInputs);
    courseDescriptionInput.addEventListener("input", checkInputs);

    // Function to check if all inputs are filled and enable the submit button
    function checkInputs() {
        var syllabusNameValue = syllabusNameInput.value.trim();
        var courseNameValue = courseNameInput.value.trim();
        var courseDescriptionValue = courseDescriptionInput.value.trim();

        // Update tooltip content based on input status
        if (syllabusNameValue && courseNameValue && courseDescriptionValue) {
            tooltipElement.setAttribute("data-bs-original-title", "You are all set, the rest can be filled up later or you can come back to.");
            tooltip.update();
            tooltip.show();
        } else {
            tooltipElement.setAttribute("data-bs-original-title", "Missing Required Inputs: " + (syllabusNameValue ? "" : "Name of Syllabus, ") + (courseNameValue ? "" : "Course Name, ") + (courseDescriptionValue ? "" : "Course Description"));
            tooltip.hide();
        }

        // Enable the submit button if all inputs are filled
        submitButton.disabled = !(syllabusNameValue && courseNameValue && courseDescriptionValue);
    }
});



































