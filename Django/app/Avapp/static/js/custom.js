    // Get the "select all" checkbox element
var selectAllCheckbox = document.getElementById('select-all');

// Get all the checkboxes in the form
var checkboxes = document.querySelectorAll('input[type=checkbox]');

// Add an event listener to the "select all" checkbox
selectAllCheckbox.addEventListener('change', function() {
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = selectAllCheckbox.checked;
    });
});

/// for option 3 instudy to show only the weight
var studyField = document.getElementById('study_filter');
var weightFields = document.getElementById('weight-fields');

studyField.addEventListener('change', function() {
  if (studyField.value === '3') {
    weightFields.style.display = 'block';
  } else {
    weightFields.style.display = 'none';
  }
});
