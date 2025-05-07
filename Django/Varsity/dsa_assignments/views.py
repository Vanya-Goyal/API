from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DSAAssignment, DSAStudentSubmission
from .forms import DSAAssignmentForm, DSAStudentSubmissionForm
from courses.models import Course
from django.http import Http404
from django.contrib import messages


@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    assignments = DSAAssignment.objects.filter(course=course)
    return render(request, 'dsa_assignments/assignment_list.html', {
        'assignments': assignments,
        'course': course
    })

@login_required
def add_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = DSAAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.instructor = request.user
            assignment.save()
            return redirect('dsa_assignments:assignment_list', course_id=course.id)

            # return redirect('instructors:manage_assignments', course_id=course.id)  # redirect after saving
    else:
        form = DSAAssignmentForm()

    return render(request, 'dsa_assignments/add_assignment.html', {
        'form': form,
        'course': course
    })
@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(DSAAssignment, pk=assignment_id, instructor=request.user)
    if request.method == 'POST':
        form = DSAAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('dsa_assignments:assignment_list', course_id=assignment.course.id)

            # return redirect('dsa_assignments:assignment_list')
    else:
        form = DSAAssignmentForm(instance=assignment)
    return render(request, 'dsa_assignments/edit_assignment.html', {'form': form, 'assignment': assignment})


@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(DSAAssignment, pk=assignment_id, instructor=request.user)
    if request.method == 'POST':
        assignment.delete()
        # return redirect('dsa_assignments:assignment_list')
        return redirect('dsa_assignments:assignment_list', course_id=assignment.course.id)

    return render(request, 'dsa_assignments/confirm_delete.html', {'assignment': assignment})

# student side
@login_required
def assignment_list_student(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = DSAAssignment.objects.filter(course=course)
    return render(request, 'dsa_assignments/assignment_list_student.html', {
        'course': course,
        'assignments': assignments
    })

@login_required
def assignment_detail_student(request, course_id, assignment_id):
    assignment = get_object_or_404(DSAAssignment, id=assignment_id, course__id=course_id)
    submissions = DSAStudentSubmission.objects.filter(assignment=assignment, student=request.user).order_by('-submitted_at')

    if request.method == 'POST':
        form = DSAStudentSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            return redirect('dsa_assignments:assignment_detail_student', course_id=course_id, assignment_id=assignment_id)
    else:
        form = DSAStudentSubmissionForm()

    return render(request, 'dsa_assignments/assignment_detail_student.html', {
        'assignment': assignment,
        'form': form,
        'submissions': submissions,
    })

@login_required
def create_submission(request, assignment_id):
    assignment = get_object_or_404(DSAAssignment, id=assignment_id)
    if request.method == 'POST':
        form = DSAStudentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            return redirect('dsa_assignments:student_submissions', course_id=assignment.course.id, assignment_id=assignment.id)
    else:
        form = DSAStudentSubmissionForm()
    return render(request, 'dsa_assignments/create_submission.html', {
        'form': form,
        'assignment': assignment
    })

# @login_required
# def edit_submission(request, submission_id):
#     submission = get_object_or_404(DSAStudentSubmission, id=submission_id, student=request.user)
#     if request.method == 'POST':
#         form = DSAStudentSubmissionForm(request.POST, request.FILES, instance=submission)
#         if form.is_valid():
#             form.save()
#             return redirect('dsa_assignments:assignment_detail_student', course_id=submission.assignment.course.id, assignment_id=submission.assignment.id)
#     else:
#         form = DSAStudentSubmissionForm(instance=submission)
#     return render(request, 'dsa_assignments/edit_submission.html', {'form': form, 'submission': submission})

from django.http import Http404

@login_required
def edit_submission(request, submission_id):
    submission = get_object_or_404(DSAStudentSubmission, id=submission_id)

    # Check if the current user is the owner of this submission
    if submission.student != request.user:
        raise Http404("You do not have permission to edit this submission.")

    form = DSAStudentSubmissionForm(instance=submission)

    if request.method == 'POST':
        form = DSAStudentSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, "Submission updated successfully!")
            return redirect('dsa_assignments:student_submissions', course_id=submission.assignment.course.id, assignment_id=submission.assignment.id)

    context = {
        'form': form,
        'submission': submission
    }
    return render(request, 'dsa_assignments/edit_submission.html', context)

# @login_required
# def delete_submission(request, submission_id):
#     submission = get_object_or_404(DSAStudentSubmission, id=submission_id, student=request.user)
#     if request.method == 'POST':
#         course_id = submission.assignment.course.id
#         assignment_id = submission.assignment.id
#         submission.delete()
#         return redirect('dsa_assignments:assignment_detail_student', course_id=course_id, assignment_id=assignment_id)
#     return render(request, 'dsa_assignments/delete_submission.html', {'submission': submission})

@login_required
def delete_submission(request, submission_id):
    submission = get_object_or_404(DSAStudentSubmission, id=submission_id)

    # Only the owner can delete
    if submission.student != request.user:
        raise Http404("You do not have permission to delete this submission.")

    if request.method == 'POST':
        submission.delete()
        messages.success(request, "Submission deleted.")
        return redirect('dsa_assignments:student_submissions', course_id=submission.assignment.course.id, assignment_id=submission.assignment.id)

    context = {
        'submission': submission
    }
    return render(request, 'dsa_assignments/delete_submission.html', context)

@login_required
def student_submissions(request, course_id, assignment_id):
    assignment = get_object_or_404(DSAAssignment, id=assignment_id, course__id=course_id)
    submissions = DSAStudentSubmission.objects.filter(assignment=assignment, student=request.user)

    if request.method == 'POST':
        form = DSAStudentSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            # ✅ Redirect to same page after submission
            return redirect('dsa_assignments:student_submissions', course_id=course_id, assignment_id=assignment.id)
    else:
        form = DSAStudentSubmissionForm()

    return render(request, 'dsa_assignments/student_submissions.html', {
        'assignment': assignment,
        'submissions': submissions,
        'form': form
    })