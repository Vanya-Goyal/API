from django.shortcuts import render, get_object_or_404, redirect
from courses.models import Course  # from the correct app
from .models import  Assignment, Question, Option
from django.urls import reverse
from courses.models import Course
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})

def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = course.assignments.all()
    return render(request, 'assignment_list.html', {'course': course, 'assignments': assignments})

def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    questions = assignment.questions.prefetch_related('options')

    if request.method == 'POST':
        total_questions = questions.count()
        correct_answers = 0
        selected_answers = {}

        # Loop through each question and capture selected answer
        for question in questions:
            selected_option_id = request.POST.get(str(question.id))
            selected_answers[question.id] = int(selected_option_id) if selected_option_id else None

            if selected_option_id:
                option = Option.objects.filter(id=selected_option_id, question=question).first()
                if option and option.is_correct:
                    correct_answers += 1

        # Calculate score
        score = int((correct_answers / total_questions) * 100)

        # Save result data in session
        request.session['result_data'] = {
            'selected_answers': {str(k): v for k, v in selected_answers.items()},
            'score': score
        }

        # Redirect to results page
        return redirect(reverse('assignments:assignment_result', args=[assignment_id]))

    return render(request, 'assignment_details.html', {
        'assignment': assignment,
        'questions': questions
    })

def assignment_result(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    questions = assignment.questions.prefetch_related('options')

    result_data = request.session.get('result_data')

    if not result_data:
        return redirect('assignments:assignment_detail', assignment_id=assignment_id)


    selected_answers = result_data['selected_answers']
    score = result_data['score']

    # Clear the session result data after displaying results
    del request.session['result_data']

    return render(request, 'assignment_result.html', {
        'assignment': assignment,
        'questions': questions,
        'selected_answers': selected_answers,
        'score': score
    })


# Create your views here.
