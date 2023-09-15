from django.shortcuts import render,redirect,get_list_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from account.forms import RegistrationForm,AccountAuthenticationForm,ProfileUpdateForm,ProfilePictureUpdateForm,CourseForm,CourseUpdateForm,QuizForm,QuestionForm,AnswerForm
from account.models import DemandeAcces,Etudiant,Course,Professeur,Question,Answer,Quiz,Enrollment
from django.forms import formset_factory
from django.contrib import messages
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist




def index(request):
    logout(request)
    return render(request , 'pages/index.html')

@user_passes_test(lambda u: u.user_type == 'student', login_url='signin')
@login_required(login_url='signin')
def studentdashbord(request):
    user = request.user
    courses = Course.objects.all() 
    etudiant = Etudiant.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(student=user.etudiant, is_opened=True)
    opened_courses = [enrollment.course for enrollment in enrollments]
    context = {
        'courses' : courses,
        'etudiant' : etudiant,
        'opened_courses': opened_courses,
    }
    return render(request , 'users/Student/StudentHome.html',context)

#student edit : 
@login_required(login_url='signin')
def studentedit(request):
    if request.method == 'POST':
        if 'picture_update' in request.POST:
            picture_form = ProfilePictureUpdateForm(request.POST, request.FILES, instance=request.user)
            if picture_form.is_valid():
                picture_form.save()
                messages.success(request, 'Your profile picture has been updated successfully.')
        else:
            form = ProfileUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile information has been updated successfully.')
                return redirect('studentedit')
    else:
        form = ProfileUpdateForm(instance=request.user)
        picture_form = ProfilePictureUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'picture_form': picture_form
    }
    return render(request, 'users/Student/Profile/student-edit.html', context)
#professor edit 
def professoredit(request):
    return render(request,'users/Professor/profile/professor-edit.html')
@user_passes_test(lambda u: u.user_type == 'teacher', login_url='signin')
@login_required(login_url='signin')
def professordashbord(request):
    try:
        professor = Professeur.objects.get(user=request.user)
    except ObjectDoesNotExist:
        professor = None
    
    courses = Course.objects.filter(professor=professor)
    user = request.user
    demande_acces = DemandeAcces.objects.filter(user=user).first()
    
    context = {
        'username': request.user.username,
        'demande_acces': demande_acces,
        'courses' : courses,
    }

    return render(request, 'users/Professor/ProfessorHome.html', context)





def about(request):
    return render(request , 'pages/about.html')

def contact(request):
    return render(request , 'pages/contact.html')


def pricing(request):
    return render(request , 'pages/pricing.html')


def signin(request):
    logout(request)
    if request.method == 'POST':
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin:index')
                elif user.user_type == 'teacher':
                    return redirect('professordashbord')
                elif user.user_type == 'student':
                    return redirect('studentdashbord')
        else:
            context = {'login_form': form, 'message': 'Invalid email or password.'}
            return render(request, 'pages/signin.html', context)
    else:
        form = AccountAuthenticationForm()
    context = {'login_form': form}
    return render(request, 'pages/signin.html', context)



def signup(request):
    logout(request)
    context = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data['user_type']
            user.user_type = user_type
            user.save()
            if user.user_type == 'teacher':
                demande_acces = DemandeAcces.objects.create(user=user, accepte=False)
                demande_acces.save()
                messages.info(request, "Your access request has been submitted. Please wait for admin approval.")
            else:
                etudiant = Etudiant.objects.create(user=user)
                etudiant.username = user.username
                etudiant.email = user.email
                etudiant.save()

            user = authenticate(request, email=user.email, password=form.cleaned_data['password1'])
            login(request, user)

            
            default_image_url = 'default/defaultimage.png'
            user.picture = default_image_url
            user.save()


            if user.user_type == 'teacher':
                return redirect('professordashbord')
            else:
                return redirect('studentdashbord')

        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form

    return render(request, 'pages/signup.html', context)



def logout_view(request):
    logout(request)
    return redirect('index')


#delete course : 
def delete_course(request,course_id):
    course = Course.objects.get(pk=course_id)
    course.delete()
    return redirect('professordashbord')

#update course
@user_passes_test(lambda u: u.user_type == 'teacher', login_url='signin')
@login_required
def update_course(request,course_id):
    course = Course.objects.get(pk=course_id)
    if request.method == 'POST':
        form = CourseUpdateForm(request.POST,request.FILES,instance=course)
        if form.is_valid():
            form.save()
            return redirect('professordashbord')
    else:
        form = CourseUpdateForm(instance=course)
    context =  {'form' : form,'course' : course}
    return render(request,'users/Professor/course/Update-Course.html',context)

@user_passes_test(lambda u: u.user_type == 'teacher', login_url='signin')
@login_required
def addcourse(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)  
            course.professor = request.user.professeur  
            course.save() 
            return redirect('professordashbord')
        else:
            messages.error(request, 'Failed to create the course. Please fix the errors below.')
    else:
        form = CourseForm()
    
    context = {'form': form}
    return render(request, 'users/Professor/course/Add-Course.html', context)

@login_required
def coursepreview(request,course_id):
    course = Course.objects.get(pk=course_id)
    user = request.user
    if  request.user.user_type == 'student':
        enrollment, created = Enrollment.objects.get_or_create(student=user.etudiant, course=course)
        enrollment.is_opened = True
        enrollment.save()
    context = {'course' : course}
    return render(request,'users/Professor/course/course-preview.html',context)

@user_passes_test(lambda u: u.user_type == 'teacher', login_url='signin')
@login_required
def quizhome(request):
    professor = Professeur.objects.get(user=request.user)
    quizzes = Quiz.objects.filter(course__professor=professor)  # Filter based on the 'course' field
    context = {
        "quizzes": quizzes,
       

    }
    return render(request, 'users/Professor/Quiz/quiz-home.html', context)
@user_passes_test(lambda u: u.user_type == 'teacher', login_url='signin')
@login_required
def addquiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()  # Save the Quiz object first to get the quiz_id
            question_count = int(request.POST.get('question_count', 0))
            print("question count : ",question_count)
            if question_count < 1:
                form.add_error(None, 'At least one question is required.')  # Add form-level error
            else:
                for i in range(1, question_count + 1):
                    question_text = request.POST.get(f'questions-{i}')
                    question = Question(quiz=quiz, question_text=question_text)
                    question.save()
                    for j in range(1, 5):
                        answer_text = request.POST.get(f'answers-{i}-{j}')
                        is_correct_key = f'correct-{i}-{j}'
                        if is_correct_key in request.POST:
                            is_correct = True
                        else:
                            is_correct = False
                        answer = Answer(question=question, response_text=answer_text, is_correct=is_correct)
                        answer.save()
                return redirect('quizhome')
    else:
        form = QuizForm()
    professor = Professeur.objects.get(user=request.user)
    courses = Course.objects.filter(professor=professor)
    return render(request, 'users/Professor/Quiz/Add_Quiz.html', {'form': form, 'courses': courses})

def quizpreview(request,quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    context = {
        "quiz" : quiz
    }
    return render(request,'users/Professor/Quiz/quiz-preview.html',context)

#delete quiz : 
def delete_quiz(request,quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    quiz.delete()
    return redirect('quizhome')

#delete question
def delete_question(request,question_id):
    question = Question.objects.get(pk=question_id)
    quiz_id = question.quiz_id 
    question.delete()
    return redirect('quizpreview', quiz_id=quiz_id)
#delete profile 
def delete_profile_page(request):
    return render(request,'users/Professor/profile/delete-profile.html')

def delete_profile(request):
    user = request.user
    user.delete()
    return redirect('index')
        
       
def checkout(request):
    etudiant = Etudiant.objects.get(user=request.user)
    context = {
        "etudiant": etudiant
    }
    return render(request,'subscription/check-out.html',context)

def make_payment(request):
    etudiant = Etudiant.objects.get(user=request.user)
    etudiant.is_subscribed = True
    etudiant.save()
    return redirect('studentdashbord')
   

def studentcoursepreview(request):
    return render(request,'users/Student/course/student-course-preview.html')