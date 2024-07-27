# require python(3.9 or 3.10 or 3.11)

import pandas as pd
from pycaret.classification import *

data = pd.read_csv('Student_performance_data _.csv')
clf = setup(data, target='GradeClass', session_id=123,
            numeric_features=['Age','StudyTimeWeekly','Absences'],
            categorical_features=['Gender','Ethnicity','ParentalEducation','Tutoring','ParentalSupport','Extracurricular','Sports','Music','Volunteering'],
            ignore_features=['StudentID','GPA']
            )

best_model = compare_models()
save_model(best_model, 'student_performance_model')
print('model has been saved successfuly!')
