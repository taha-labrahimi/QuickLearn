from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from account.models import Account,Course,Quiz,Question,Answer


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Add a valid email address.')
    user_type = forms.ChoiceField(choices=(('student', 'Étudiant'), ('teacher', 'Professeur')))
    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2', 'user_type')

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('course_title', 'course_level', 'course_description', 'course_pdf', 'video_url', 'cover_image', 'duration_hours', 'duration_minutes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course_pdf'].required = True
        self.fields['video_url'].required = True
        self.fields['cover_image'].required = True
        


class CourseUpdateForm(forms.ModelForm):
     class Meta:
        model = Course
        fields = ('course_title', 'course_level', 'course_description', 'course_pdf', 'video_url', 'cover_image', 'duration_hours', 'duration_minutes')
     def __init__(self, *args, **kwargs):
        super(CourseUpdateForm, self).__init__(*args, **kwargs)
        self.fields['course_title'].required = False
        self.fields['course_level'].required = False
        self.fields['course_description'].required = False
        self.fields['course_pdf'].required = False
        self.fields['video_url'].required = False
        self.fields['cover_image'].required = False
        self.fields['duration_hours'].required = False
        self.fields['course_level'].required = False
        

class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid login")

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone', 'address', 'country']

class ProfilePictureUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['picture']

    

#Quiz 
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['course', 'quiz_name', 'quiz_duration']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['response_text', 'is_correct']    