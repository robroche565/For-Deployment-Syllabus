$(document).ready(function () {
    // // Function to restrict input to one decimal place in the ones and tenths places
    // function restrictToDecimalPlace(inputElement) {
    //     inputElement.addEventListener('input', function () {
    //         // Get the input value
    //         var inputValue = this.value;

    //         // Check if the input exceeds 10
    //         if (parseFloat(inputValue) >= 10) {
    //             // Display an alert error
    //             alert('Value cannot exceed 10.');

    //             // Clear the input field
    //             this.value = '';
    //         }

    //         // Check if the input contains more than one decimal place in the tenths place
    //         if (/^\d+\.\d{2,}$/.test(inputValue)) {
    //             // Display an alert error
    //             alert('Please enter a value with only one decimal place in the tenths place.');

    //             // Remove extra decimal places in the tenths place
    //             this.value = parseFloat(inputValue).toFixed(1);
    //         }
    //     });
    // }
    // // Function to restrict input to two decimal places in the hundredths place
    // function restrictToHundredthsPlace(inputElement) {
    //     inputElement.addEventListener('input', function () {
    //         // Get the input value
    //         var inputValue = this.value;

    //         // Check if the input exceeds 10
    //         if (parseFloat(inputValue) >= 10) {
    //             // Display an alert error
    //             alert('Value cannot exceed 10.');

    //             // Clear the input field
    //             this.value = '';
    //         }

    //         // Check if the input contains more than two decimal places in the hundredths place
    //         if (/^\d+\.\d{3,}$/.test(inputValue)) {
    //             // Display an alert error
    //             alert('Please enter a value with only two decimal places in the hundredths place.');

    //             // Remove extra decimal places in the hundredths place
    //             this.value = parseFloat(inputValue).toFixed(2);
    //         }
    //     });
    // }

    // // Use event delegation to handle dynamically added "num_rating[]" inputs
    // document.addEventListener('input', function (event) {
    //     if (event.target && event.target.matches('[name="num_rating[]"]')) {
    //         restrictToHundredthsPlace(event.target);
    //     }
    // });

    // var maxSources = 5;

    // // Function to add a new source input field
    // function addSource() {
    //     if ($("#source-input-container .input-group").length < maxSources) {
    //         var $newSource = $("#source-input-container .input-group:first").clone();
    //         $newSource.find('input').val(''); // Clear input value in the cloned field
    //         $newSource.find('input').removeAttr('id'); // Remove the 'id' attribute
    //         $("#source-input-container").append($newSource);
    //     } else {
    //         alert('You can only add up to 5 sources.');
    //     }
    // }

    // // Event listener for "Add Source" button
    // $("#add-source").click(function () {
    //     addSource();
    // });

    // // Event delegation for "Remove" button
    // $("#source-input-container").on("click", ".remove-source", function () {
    //     if ($("#source-input-container .input-group").length > 1) {
    //         $(this).closest(".input-group").remove();
    //     }
    // });

    // var maxMidTermInputs = 5; // Maximum number of Mid-Term inputs allowed

    // // Function to add a new Mid-Term input field
    // function addMidTermInput() {
    //     if ($(".mid-term-inputs .input-group").length < maxMidTermInputs) {
    //         var $newMidTermInput = $(".mid-term-inputs .input-group:first").clone();
    //         $newMidTermInput.find('input').val(''); // Clear input values in the cloned field
    //         $(".mid-term-inputs").append($newMidTermInput);
    //     } else {
    //         alert('You can only add up to 5 Mid-Term entries.');
    //     }
    // }

    // // Event listener for "Add Mid-Term" button
    // $(document).on("click", ".add-mid-term", function () {
    //     addMidTermInput();
    // });

    // // Event delegation for "Remove" button for Mid-Term inputs
    // $(document).on("click", ".remove-mid-term", function () {
    //     if ($(".mid-term-inputs .input-group").length > 1) {
    //         $(this).closest(".input-group").remove();
    //     }
    // });

    // var maxFinalTermInputs = 5; // Maximum number of Final Term inputs allowed

    // // Function to add a new Final Term input field
    // function addFinalTermInput() {
    //     if ($(".final-term-inputs .input-group").length < maxFinalTermInputs) {
    //         var $newFinalTermInput = $(".final-term-inputs .input-group:first").clone();
    //         $newFinalTermInput.find('input').val(''); // Clear input values in the cloned field
    //         $(".final-term-inputs").append($newFinalTermInput);
    //     } else {
    //         alert('You can only add up to 5 Final Term entries.');
    //     }
    // }

    // // Event listener for "Add Final Term" button
    // $(document).on("click", ".add-final-term", function () {
    //     addFinalTermInput();
    // });

    // // Event delegation for "Remove" button for Final Term inputs
    // $(document).on("click", ".remove-final-term", function () {
    //     if ($(".final-term-inputs .input-group").length > 1) {
    //         $(this).closest(".input-group").remove();
    //     }
    // });

    // // Function to add a new percentage grade range input field
    // function addPercentageGradeRange() {
    //     var $newInput = $("#percentage-grade-ranges .input-group:first").clone();
    //     $newInput.find('input').val(''); // Clear input values in the cloned field
    //     $("#percentage-grade-ranges").append($newInput);
    // }

    // // Event listener for "Add Percentage Grade Range" button
    // $(document).on("click", ".add-percentage-grade-range", function () {
    //     addPercentageGradeRange();
    // });

    // // Event delegation for "Remove" button for percentage grade range inputs
    // $(document).on("click", ".remove-percentage-grade-range", function () {
    //     if ($("#percentage-grade-ranges .input-group").length > 1) {
    //         $(this).closest(".input-group").remove();
    //     }
    // });

    // // Function to add a new course requirement input field
    // function addCourseRequirement() {
    //     var $newCourseRequirement = $(".course-requirements .input-group:first").clone();
    //     $newCourseRequirement.find('input').val(''); // Clear input value in the cloned field
    //     $(".course-requirements").append($newCourseRequirement);
    // }

    // // Event listener for "Add Course Requirement" button
    // $(".add-course-requirement").click(function () {
    //     addCourseRequirement();
    // });

    // // Event delegation for "Remove" button for course requirements
    // $(".course-requirements").on("click", ".remove-course-requirement", function () {
    //     if ($(".course-requirements .input-group").length > 1) {
    //         $(this).closest(".input-group").remove();
    //     }
    // });

    // var maxPreparedBy = 3;

    // // Function to add a new prepared by input field
    // function addPreparedBy() {
    //     if ($(".prepared-by .input-group").length < maxPreparedBy) {
    //         var $newPreparedBy = $(".prepared-by .input-group:first").clone();
    //         $newPreparedBy.find('input').val(''); // Clear input value in the cloned field
    //         $(".prepared-by").append($newPreparedBy);
    //     } else {
    //         alert('You can only add up to 3 Prepared By entries.');
    //     }
    // }

    // // Event listener for "Add Prepared By" button
    // $(".add-prepared-by").click(function () {
    //     addPreparedBy();
    // });

    // // Event delegation for "Remove" button for prepared by
    // $(".prepared-by").on("click", ".remove-prepared-by", function () {
    //     if ($(".prepared-by .input-group").length > 1) {
    //         $(this).closest(".input-group").remove();
    //     }
    // });

    /* // Event listener for form submission
    let formTest = $(".formTest")
    console.log(formTest);

   // this is the id of the form
    $(".formTest").submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var actionUrl = form.attr('action');

        $.ajax({
            type: "POST",
            url: actionUrl,
            data: form.serialize(), // serializes the form's elements.
            success: function(data) {
                console.log(data);

                let dataJson = JSON.parse(data);
                if (dataJson.status === 1) {
                    // success handling
                    console.log("success")

                } else {
                    // error handling
                    console.log("error")
                }
            },
            error: function(error) {
                console.log(error)
            }
        });

    }); */




    // ---------- DAUD SETUP PAGE SYLLABUS TEMPLATE ----------
    // ---------- ADD INPUT CONTAINER GROUP ----------
    function addInputGroup(containerID) {
        var $container = $("#" + containerID);
        var $listInputCont = $container.find(".list-input-container");

        // Find the first .input-group element within $listInputCont and clone it
        var $inputGroup = $listInputCont.find(".input-group:first").clone();

        // To limit the number of inputs to be add
        var $counter = $listInputCont.find(".input-group");
        if ($counter.length < 6) {
            // Clear the value of the cloned input
            $inputGroup.find("input").val("");

            // Append the cloned element to $listInputCont or another container as needed
            $listInputCont.append($inputGroup.last());

            // Hide add input button
            if ($counter.length == 5) {
                $container.find(".add-input").hide();
            }
        } else {
            $container.find(".add-input").hide(); // Ensure the button is hidden if the limit is reached
        }
    }

    // ----- Syllabus -----
    $("#add-preriquisite").on("click", function () {
        addInputGroup("preriquisite-cont");
    });

    $("#add-requirements").on("click", function () {
        addInputGroup("requirements-cont");
    });

    $("#add-prepared").on("click", function () {
        addInputGroup("prepared-cont");
    })

    //--references---
    var maxSources = 5;
    // Function to toggle the source input container and "Add Source" button
    function toggleSourceInputContainer() {
        var radioValue = $("input[name='syllabus-source-type']:checked").val();
        if (radioValue === "specific") {
            $("#source-input-container").show();
            $("#add-source").show();
        } else {
            $("#source-input-container").hide();
            $("#add-source").hide();
        }
    }

    // Initialize the container's visibility based on the initial radio button state
    toggleSourceInputContainer();

    // Event listener for radio button change
    $("input[name='syllabus-source-type']").change(function () {
        toggleSourceInputContainer();
    });

    // Function to add a new source input field
    function addSource() {
        if ($("#source-input-container .input-group").length < maxSources) {
            var $newSource = $("#source-input-container .input-group:first").clone();
            $newSource.find('input').val(''); // Clear input value in the cloned field
            $newSource.find('input').removeAttr('id'); // Remove the 'id' attribute
            $("#source-input-container").append($newSource);
        } else {
            alert('You can only add up to 5 sources.');
        }
    }

    // Event listener for "Add Source" button
    $("#add-source").click(function () {
        addSource();
    });

    // Event delegation for "Remove" button
    $("#source-input-container").on("click", ".remove-source", function () {
        if ($("#source-input-container .input-group").length > 1) {
            $(this).closest(".input-group").remove();
        }
    });


    // ----- Syllabus Template -----
    // Event handler for adding new input group in vision
    $("#add-vision").on("click", function () {
        addInputGroup("vision-cont");
    });

    // Event handler for adding new input group in mission
    $("#add-mission").on("click", function () {
        addInputGroup("mission-cont");
    });

    // Event handler for adding new input group in goal
    $("#add-goal").on("click", function () {
        addInputGroup("goal-cont");
    });

    // Event handler for adding new input group in college course
    $("#add-college").on("click", function () {
        addInputGroup("college-cont");
    });

    // Event handler for adding new input group in midterm
    $("#add-midterm-lecture").on("click", function () {
        addInputGroup("midterm-lecture");
    });

    $("#add-midterm-laboratory").on("click", function () {
        addInputGroup("midterm-laboratory");
    });

    // Event handler for adding new input group in finalterm
    $("#add-finalterm-lecture").on("click", function () {
        addInputGroup("finalterm-lecture");
    });

    $("#add-finalterm-laboratory").on("click", function () {
        addInputGroup("finalterm-laboratory");
    })

    // Event handler for adding new input group in range
    $("#add-range").on("click", function () {
        addInputGroup("range-cont");
    });

    // Event handler for removing input group
    $(".row").on("click", ".remove-input", function () {
        var $inputGroup = $(this).closest(".input-group");
        var $container = $(this).closest(".list-input-container");
        var $inputGroups = $container.find(".input-group");

        if ($inputGroups.length > 1) { // check if there's more than one input group before removing
            $inputGroup.remove();

            console.log("Remove button clicked");
            $container.closest(".row").find(".mt-2 .btn").show(); // Show add input button
        }
    })


    // ---------- RADIO BUTTONS ----------
    // ----- Syllabus Template -----
    // ----- Grading System Type -----
    function gsTypeToggle() {
        const radioValue = $("input[name='grading_system_type']:checked").val();
        const termsContainer = $('.row.terms-cont');

        if (radioValue == 'lecture only') {
            termsContainer.addClass(radioValue);
            termsContainer.removeClass('laboratory only');
        }
        else if (radioValue == 'laboratory only') {
            termsContainer.addClass(radioValue);
            termsContainer.removeClass('lecture only');
        }
        else {
            termsContainer.removeClass('lecture only');
            termsContainer.removeClass('laboratory only');
        }
    }

    // ----- Syllabus -----
    // ----- Grading System Syllabus -----
    function gradingSystemSyllabus() {
        var grading_system_value = $(".create-syllabus input[name='grading_system_option']:checked").val();

        console.log(grading_system_value);

        if (grading_system_value === "create-new") {
            $("#additional_info_inputs").show();
        } else {
            $("#additional_info_inputs").hide();
        }
    }

    // ----- Information Syllabus Source (References) -----
    function sourceInputTypeToggle() {
        var source_type_value = $("input[name='syllabus-source-type']:checked").val();
        if (source_type_value === "specific") {
            $("#source-input-container").show();
            $("#add-resources").show();
        } else {
            $("#source-input-container").hide();
            $("#add-sources").hide();
        }
    }

    // Initialize the container's visibility based on the initial radio button state
    gsTypeToggle();
    gradingSystemSyllabus();
    sourceInputTypeToggle();

    // Event listener for radio button change
    $("input[name='grading_system_type']").change(function () {
        gsTypeToggle();
    });

    $("input[name='grading_system_option']").click(function () {
        gradingSystemSyllabus()
    });

    $("input[name='syllabus-source-type']").change(function () {
        sourceInputTypeToggle();
    });


    // ---------- CONFIRMATION MODAL ----------
    const $form = $("form");
    const $overlay = $("form .overlay");

    // ----- DELETE MODAL -----
    $(".top-content").on("click", ".delete-btn", function () {
        const $cancelButton = $("form .confirmation-modal-delete .btn-secondary");

        // shows the modal and overlay when delete button is pressed
        $form.addClass("active-delete");

        // hides overlay and modal when pressed
        $overlay.click(function () {
            $form.removeClass("active-delete");
        });

        $cancelButton.click(function () {
            $form.removeClass("active-delete");
        });
    });

    // ----- EDIT MODAL -----
    $("form").on("click", ".save-info", function () {
        const $cancelButton = $("form .confirmation-modal-edit .btn-secondary");
        const $saveButton = $("form .confirmation-modal-edit .btn-primary");

        $form.addClass("active-edit");

        $overlay.click(function () {
            $form.removeClass("active-edit");
        })

        $cancelButton.click(function () {
            $form.removeClass("active-edit");
        })

        $saveButton.click(function () {
            $form.removeClass("active-edit");
        })
    });
});