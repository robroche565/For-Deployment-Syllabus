// ========== Error check or empty field check (first page) ==========
document.addEventListener('DOMContentLoaded', function () {
    const nextBtn = document.querySelector('#next_btn')

    const name = document.querySelector('input[name="name"]')
    const nameError = document.querySelector('#error_name')
    const courseLogo = document.querySelector('input[name="course_logo"')
    const courseLogoError = document.querySelector('#error_course_logo')
    const wmsuLogo = document.querySelector('input[name="wmsu_logo"]')
    const wmsuLogoError = document.querySelector('#error_wmsu_logo')
    const isoLogo = document.querySelector('input[name="iso_logo"]')
    const isoLogoError = document.querySelector('#error_iso_logo')
    const goal = document.querySelector('textarea[name="goal"]')
    const goalError = document.querySelector('#error_goal_desc')
    let itemizeGoals = document.querySelectorAll('input[name="goal_itemize"]')
    let itemizeGoalDeletes = document.querySelectorAll('#itemize_goal_delete')
    const itemizeGoalAdd = document.querySelector('#add-goal')
    const itemizeGoalsError = document.querySelector('#error_itemize_goal')

    // updates error either clearing out or displaying error and toggling next button
    const updateError = (errorContainer, message) => {
        errorContainer.querySelector('span').textContent = message
        errorContainer.style.display = message ? 'block' : 'none'
        nextBtn.classList.toggle('js-btn-next', !message)
    }

    // logo validates for image type, file size and if any file is present in the input file
    const validateLogo = (file, errorContainer, errorMessage) => {
        if (file) {
            if (!['image/jpg', 'image/jpeg', 'image/png'].includes(file.type)) {
                updateError(errorContainer, 'Please upload an image file (JPEG, JPG, PNG)')
            } else if (file.size > 4 * 1024 * 1024) {
                updateError(errorContainer, 'File size exceeds 4MB limit')
            } else {
                updateError(errorContainer, '')
            }
        } else {
            updateError(errorContainer, `Please upload a ${errorMessage} Logo`)
        }
    }

    // for inputs with limits on input
    const validateMaxInput = (errorContainer, value, limit, errorMessage) => {
        updateError(errorContainer, value.length > limit ? `${errorMessage} reached limit` : '')
    }

    // Goal validation
    const validateGoal = () => {
        if (!goal.value.trim()) {
            updateError(goalError, 'Please fill in the college goal description')
            return
        }

        validateMaxInput(goalError, goal.value, 300, 'Goal description')
    }

    const updateGlobalIG = () => {
        itemizeGoals = document.querySelectorAll('input[name="goal_itemize"]')
        itemizeGoalDeletes = document.querySelectorAll('#itemize_goal_delete')
    }

    // Itemized Goal validation
    const validateItemizeGoal = () => {
        updateGlobalIG()
        itemizeGoals.forEach(ig => { updateError(itemizeGoalsError, !ig.value.trim() ? 'Please fill in the itemized goal field' : '') })
    }

    // validation for all and scrolling to error field if there is. Returns boolean for proceeding to next page
    const validateAll = () => {
        validateMaxInput(nameError, name.value, 50, 'syllabus template name')
        validateLogo(courseLogo.files[0], courseLogoError, 'Course')
        validateLogo(wmsuLogo.files[0], wmsuLogoError, 'WMSU')
        validateLogo(isoLogo.files[0], isoLogoError, 'ISO')
        validateGoal()
        validateItemizeGoal()

        scrollToError(document.querySelector('input[name="goal_itemize"]'), itemizeGoalsError)
        scrollToError(goal, goalError)
        scrollToError(isoLogo, isoLogoError)
        scrollToError(wmsuLogo, wmsuLogoError)
        scrollToError(courseLogo, courseLogoError)
        scrollToError(name, nameError)

        return checkErrors()
    }

    // check for any errors
    const checkErrors = () => {
        return !!(nameError.textContent || courseLogoError.textContent || wmsuLogoError.textContent ||
            isoLogoError.textContent || goalError.textContent || itemizeGoalsError)
    }

    // scrolls into input fields that has an error
    const scrollToError = (input, errorContainer) => {
        if (errorContainer.textContent) { input.scrollIntoView({ behavior: 'smooth' }) }
    }

    // inputs and uploading event listener for realtime checking
    name.addEventListener('input', () => validateMaxInput(nameError, name.value, 50, 'syllabus template name'))
    courseLogo.addEventListener('change', () => validateLogo(courseLogo.files[0], courseLogoError, 'Course'))
    wmsuLogo.addEventListener('change', () => validateLogo(wmsuLogo.files[0], wmsuLogoError, 'WMSU'))
    isoLogo.addEventListener('change', () => validateLogo(isoLogo.files[0], isoLogoError, 'ISO'))
    goal.addEventListener('input', validateGoal)

    itemizeGoals.forEach(ig => { ig.addEventListener('input', validateItemizeGoal) })
    itemizeGoalDeletes.forEach(igd => { igd.addEventListener('click', () => { updateGlobalIG() }) })
    itemizeGoalAdd.addEventListener('click', () => { updateGlobalIG() })

    // finally before proceeding to next page, all the inputs that are needs for checking, gets check first.
    nextBtn.addEventListener('click', () => {
        validateAll()
    })


    // ========== Form page function (First page, basically for toggling the page to first and second) ==========
    //DOM elements
    const DOMstrings = {
        stepsBtnClass: 'multisteps-form__progress-btn',
        stepsBtns: document.querySelectorAll(`.multisteps-form__progress-btn`),
        stepsBar: document.querySelector('.multisteps-form__progress'),
        stepsForm: document.querySelector('.multisteps-form__form'),
        stepsFormTextareas: document.querySelectorAll('.multisteps-form__textarea'),
        stepFormPanelClass: 'multisteps-form__panel',
        stepFormPanels: document.querySelectorAll('.multisteps-form__panel'),
        stepPrevBtnClass: 'js-btn-prev',
        stepNextBtnClass: 'js-btn-next'
    };

    //remove class from a set of items
    const removeClasses = (elemSet, className) => {

        elemSet.forEach(elem => {

            elem.classList.remove(className);

        });

    };

    //return exect parent node of the element
    const findParent = (elem, parentClass) => {

        let currentNode = elem;

        while (!currentNode.classList.contains(parentClass)) {
            currentNode = currentNode.parentNode;
        }

        return currentNode;

    };

    //get active button step number
    const getActiveStep = elem => {
        return Array.from(DOMstrings.stepsBtns).indexOf(elem);
    };

    //set all steps before clicked (and clicked too) to active
    const setActiveStep = activeStepNum => {

        //remove active state from all the state
        removeClasses(DOMstrings.stepsBtns, 'js-active');

        //set picked items to active
        DOMstrings.stepsBtns.forEach((elem, index) => {

            if (index <= activeStepNum) {
                elem.classList.add('js-active');
            }

        });
    };

    //get active panel
    const getActivePanel = () => {

        let activePanel;

        DOMstrings.stepFormPanels.forEach(elem => {

            if (elem.classList.contains('js-active')) {

                activePanel = elem;

            }

        });

        return activePanel;

    };

    //open active panel (and close unactive panels)
    const setActivePanel = activePanelNum => {
        if (activePanelNum !== 2) {
            //remove active class from all the panels
            removeClasses(DOMstrings.stepFormPanels, 'js-active');

            //show active panel
            DOMstrings.stepFormPanels.forEach((elem, index) => {
                if (index === activePanelNum) {

                    elem.classList.add('js-active');

                    setFormHeight(elem);

                }
            });
        }
    };

    //set form height equal to current panel height
    const formHeight = activePanel => {

        const activePanelHeight = activePanel.offsetHeight;

        DOMstrings.stepsForm.style.height = `${activePanelHeight}px`;

    };

    const setFormHeight = () => {
        const activePanel = getActivePanel();

        formHeight(activePanel);
    };

    //STEPS BAR CLICK FUNCTION
    DOMstrings.stepsBar.addEventListener('click', e => {

        //check if click target is a step button
        const eventTarget = e.target;

        if (!eventTarget.classList.contains(`${DOMstrings.stepsBtnClass}`)) {
            return;
        }

        //get active button step number
        const activeStep = getActiveStep(eventTarget);

        //set all steps before clicked (and clicked too) to active
        `setActiveStep`(activeStep);

        //open active panel
        setActivePanel(activeStep);
    });

    //PREV/NEXT BTNS CLICK
    DOMstrings.stepsForm.addEventListener('click', e => {

        const eventTarget = e.target;

        //check if we clicked on `PREV` or NEXT` buttons
        if (!(eventTarget.classList.contains(`${DOMstrings.stepPrevBtnClass}`) || eventTarget.classList.contains(`${DOMstrings.stepNextBtnClass}`))) {
            return;
        }

        //find active panel
        const activePanel = findParent(eventTarget, `${DOMstrings.stepFormPanelClass}`);

        let activePanelNum = Array.from(DOMstrings.stepFormPanels).indexOf(activePanel);

        //set active step and active panel onclick
        if (eventTarget.classList.contains(`${DOMstrings.stepPrevBtnClass}`)) {
            activePanelNum--;
        } else {
            if (activePanelNum === 0) {
                if (validateAll) {
                    activePanelNum++;
                }
            } else if (activePanelNum === 1){
                if (!validateAll2) {
                    activePanelNum++;
                }
            } else {
                activePanelNum++;
            }
        }

        setActiveStep(activePanelNum);
        setActivePanel(activePanelNum);
    });

    //SETTING PROPER FORM HEIGHT ONLOAD
    window.addEventListener('load', setFormHeight, false);

    //SETTING PROPER FORM HEIGHT ONRESIZE
    window.addEventListener('resize', setFormHeight, false);

    //changing animation via animation select !!!YOU DON'T NEED THIS CODE (if you want to change animation type, just change form panels data-attr)
    const setAnimationType = newType => {
        DOMstrings.stepFormPanels.forEach(elem => {
            elem.dataset.animation = newType;
        });
    };

    //selector onchange - changing animation
    const animationSelect = document.querySelector('.pick-animation__select');


    // ========== Checks for required fields in Second Page (Preventing submitting form) ==========
    const submitBtn = document.querySelector('button[type="submit"]')

    let courseOutcomes = document.querySelectorAll('textarea[name="course_outcome"]')
    let courseOutcomeDelete = document.querySelectorAll('#course_outcome_delete')
    const courseOutcomeError = document.querySelector('#error_course_outcome')
    const courseOutcomeAdd = document.querySelector('#add-college')

    const updateGlobalCO = () => {
        courseOutcomes = document.querySelectorAll('textarea[name="course_outcome"]')
        courseOutcomeDelete = document.querySelectorAll('#course_outcome_delete')
    }

    const validateCourseOutcome = () => {
        updateGlobalCO()
        courseOutcomes.forEach(cou => {
            updateError(courseOutcomeError, !cou.value.trim() ? 'Please fill in the itemized goal field' : '')
        })
    }

    const validateAll2 = () => {
        validateCourseOutcome()

        if (courseOutcomeError.textContent) { document.querySelector('textarea[name="course_outcome"]').scrollIntoView({ behavior: 'smooth' }) }

        return !!courseOutcomeError.querySelector('span').textContent;
    }

    courseOutcomes.forEach(co => { co.addEventListener('input', validateCourseOutcome) })

    submitBtn.addEventListener('click', (e) => {
        if (validateAll2()) {
            e.preventDefault(); // Prevent form submission if there are errors
        }
    })
})