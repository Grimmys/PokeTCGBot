import random
import time

from src.utils import card_grade
from src.utils.card_grade import OBTAINABLE_GRADES, CardGrade

NUMBER_OF_GRADES = 10000000
card_grade.ASSETS_FOLDER_LOCATION = "../../assets"
card_grade.load_grades({"grade_star": ""})

grades: list[CardGrade] = []
simulation_start = time.time()
for _ in range(NUMBER_OF_GRADES):
    grade = random.choices(OBTAINABLE_GRADES,
                           weights=[grade.probability for grade in OBTAINABLE_GRADES])[0]
    grades.append(grade)
simulation_end = time.time()

number_of_grades_per_grade = {}
for grade in grades:
    if grade.in_application_name in number_of_grades_per_grade:
        number_of_grades_per_grade[grade.in_application_name] += 1
    else:
        number_of_grades_per_grade[grade.in_application_name] = 1

print(f"Number of cards for each grade: {number_of_grades_per_grade}")
grade_proportions = {grade: value / NUMBER_OF_GRADES for (grade, value) in number_of_grades_per_grade.items()}
print(f"Proportions of cards for each grade: {grade_proportions}")
print(f"Simulation duration: {(simulation_end - simulation_start):.2f} seconds")
