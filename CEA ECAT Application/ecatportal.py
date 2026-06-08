

questions = [
    {"subject": "Math","question": "33 * 55 = ?","A": "3252","B": "1815","C": "5789","D": "2156","answer": "B"},
    {"subject": "GK","question": "Capital of Pakistan?","A": "Lahore","B": "Karachi","C": "Islamabad","D": "Peshawar","answer": "C"},
    {"subject": "GK","question" : "Total Pakistan Seasons are?","A": "2","B": "3","C": "4","D": "5","answer": "C"},
    {"subject": "Bio","question" : "kidney are used for","A": "cleaning","B": "digestion","C": "supplu","D": "none","answer": "A"},
    {"subject": "Phy","question" : "Total Newton Law","A": "109","B": "110","C": "111","D": "112","answer": "D"},
    {"subject": "Chem","question" : "Organic Bond are:","A": "C-H","B": "O-H","C": "-OH","D": "None","answer": "A"},
    {"subject": "Maths","question" : "cos 90","A": "1","B": "2","C": "0","D": "3","answer": "C"},
    {"subject": "Maths","question" : "sin90+cos1=","A": "1.97","B": "1.98","C": "1.99","D": "2.00","answer": "C"},
    {"subject": "Bio","question" : "Heart have how many chamber?","A": "2","B": "3","C": "4","D": "5","answer": "C"},
    {"subject": "Phy","question" : "G is equal to","A": "8","B": "9","C": "10","D": "11","answer": "C"}, 
    ]

all_results = []


def admin_login():

    attempts = 3

    while attempts > 0:

        username = input("Enter Username: ")
        password = input("Enter Password: ")

        if username == "ecat_admin" and password == "ecat@2024":

            print("Admin Login Successful")
            admin_menu()
            return

        else:

            attempts -= 1
            print("Invalid Login")

    print("Login Locked")


def student_login():

    attempts = 3

    while attempts > 0:

        username = input("Enter Username: ")
        password = input("Enter Password: ")

        if username == "student" and password == "student123":

            print("Student Login Successful")
            student_menu()
            return

        else:

            attempts -= 1
            print("Invalid Login")

    print("Login Locked")


def view_questions():

    for i in range(len(questions)):

        q = questions[i]

        print("\nQuestion", i + 1)
        print("Subject:", q["subject"])
        print(q["question"])

        print("A.", q["A"])
        print("B.", q["B"])
        print("C.", q["C"])
        print("D.", q["D"])

        print("Correct Answer:", q["answer"])


def add_question():

    subject = input("Enter Subject: ")
    question = input("Enter Question: ")

    option_a = input("Enter Option A: ")
    option_b = input("Enter Option B: ")
    option_c = input("Enter Option C: ")
    option_d = input("Enter Option D: ")

    answer = input("Enter Correct Answer: ").upper()


    questions.append({

        "subject": subject,
        "question": question,
        "A": option_a,
        "B": option_b,
        "C": option_c,
        "D": option_d,
        "answer": answer

    })

    print("Question Added Successfully")


def delete_question():

    view_questions()

    number = int(input("Enter Question Number: "))

    if number >= 1 and number <= len(questions):

        questions.pop(number - 1)

        print("Question Deleted")

    else:

        print("Invalid Number")


def question_statistics():

    print("\nTotal Questions =", len(questions))


def exam_rules():

    print("\n===== EXAM RULES =====")

    print("Correct Answer = +4 Marks")
    print("Wrong Answer = -1 Mark")
    print("Skip Question = 0 Marks")

    print("Press S to Skip")
    print("Type SUBMIT to End Exam")


def start_exam():

    student_name = input("Enter Name: ")
    roll_number = input("Enter Roll Number: ")

    answers = {}

    i = 0

    while i < len(questions):

        q = questions[i]

        print("\nQuestion", i + 1)
        print(q["question"])

        print("A.", q["A"])
        print("B.", q["B"])
        print("C.", q["C"])
        print("D.", q["D"])

        print("\nA/B/C/D = Answer")
        print("S = Skip")
        print("N = Next")
        print("BK = Back")
        print("SUBMIT = End Exam")

        answer = input("Enter Choice: ").upper()

        if answer == "SUBMIT":

            break

        elif answer == "N":

            i += 1

        elif answer == "BK":

            if i > 0:
                i -= 1

        elif answer == "S":

            answers[i] = "S"
            i += 1

        elif answer in ["A", "B", "C", "D"]:

            answers[i] = answer
            i += 1

        else:

            print("Invalid Input")

    score = 0
    review = []

    for i in range(len(questions)):

        q = questions[i]

        student_answer = answers.get(i, "S")

        if student_answer == q["answer"]:

            score += 4

        elif student_answer == "S":

            score += 0

        else:

            score -= 1

        review.append([
            q["question"],
            student_answer,
            q["answer"]
        ])

    total_marks = len(questions) * 4
    percentage = (score / total_marks) * 100

    if percentage >= 80:

        grade = "EXCELLENT"

    elif percentage >= 65:

        grade = "GOOD"

    elif percentage >= 50:

        grade = "AVERAGE"

    else:

        grade = "BELOW AVERAGE"

    result = {

        "name": student_name,
        "roll": roll_number,
        "score": score,
        "percentage": round(percentage, 2),
        "grade": grade,
        "review": review

    }

    all_results.append(result)

    print("\n===== RESULT =====")

    print("Name:", student_name)
    print("Roll Number:", roll_number)
    print("Score:", score)
    print("Percentage:", round(percentage, 2))
    print("Grade:", grade)

    print("\n===== REVIEW =====")

    for item in review:

        print(item)


def view_results():

    print("\n===== ALL RESULTS =====")

    for result in all_results:

        print("Name:", result["name"])
        print("Roll:", result["roll"])
        print("Score:", result["score"])
        print("Percentage:", result["percentage"])
        print("Grade:", result["grade"])
        print()


def detailed_result():

    roll = input("Enter Roll Number: ")

    for result in all_results:

        if result["roll"] == roll:

            print("\nName:", result["name"])
            print("Roll:", result["roll"])
            print("Score:", result["score"])
            print("Percentage:", result["percentage"])
            print("Grade:", result["grade"])

            print("\nReview:")

            for item in result["review"]:

                print(item)

            return

    print("Result Not Found")


def class_statistics():

    if len(all_results) == 0:

        print("No Results Available")
        return

    highest = all_results[0]["score"]
    lowest = all_results[0]["score"]

    total = 0

    for result in all_results:

        total += result["score"]

        if result["score"] > highest:

            highest = result["score"]

        if result["score"] < lowest:

            lowest = result["score"]

    average = total / len(all_results)

    print("\nHighest Score =", highest)
    print("Lowest Score =", lowest)
    print("Average Score =", round(average, 2))


def admin_menu():

    while True:

        print("\n===== ADMIN MENU =====")

        print("1. View Questions")
        print("2. Add Question")
        print("3. Delete Question")
        print("4. Question Statistics")
        print("5. View Results")
        print("6. Detailed Result")
        print("7. Class Statistics")
        print("8. Back")

        choice = input("Enter Choice: ")

        if choice == "1":

            view_questions()

        elif choice == "2":

            add_question()

        elif choice == "3":

            delete_question()

        elif choice == "4":

            question_statistics()

        elif choice == "5":

            view_results()

        elif choice == "6":

            detailed_result()

        elif choice == "7":

            class_statistics()

        elif choice == "8":

            break

        else:

            print("Invalid Choice")


def student_menu():

    while True:

        print("\n===== STUDENT MENU =====")

        print("1. Start Exam")
        print("2. View Rules")
        print("3. Back")

        choice = input("Enter Choice: ")

        if choice == "1":

            start_exam()

        elif choice == "2":

            exam_rules()

        elif choice == "3":

            break

        else:

            print("Invalid Choice")


while True:

    print("\n===== ECAT EXAM PORTAL =====")

    print("1. Admin Portal")
    print("2. Student Portal")
    print("3. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":

      admin_login()

    elif choice == "2":

        student_login()

    elif choice == "3":

        print("Program Closed")
        break

    else:

        print("Invalid Choice")