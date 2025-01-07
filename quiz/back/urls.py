from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
   
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('quizzes/', QuizListView.as_view(), name='quiz_list'),
    path('quizzes/<int:quiz_id>/questions/', QuestionListView.as_view(), name='quiz_questions'),
    path('quizzes/<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('results/', UserResultsView.as_view(), name='user_results'),


    # admin endpoints
    path('admin/quizzes/', AdminQuizView.as_view(), name='admin_quiz_list'), # Fetch all quizzes, Create a new quiz.
    path('admin/quizzes/<int:quiz_id>/', AdminQuizView.as_view(), name='admin_quiz_detail'), #  Update an existing quiz, Delete a quiz
    path('admin/quizzes/<int:quiz_id>/questions/', AdminQuestionView.as_view(), name='admin_question_list'), # Fetch all questions for a quiz,  Add questions to a quiz.
    path('admin/questions/<int:question_id>/', AdminQuestionView.as_view(), name='admin_question_detail'), #  Update a question,  Delete a question.
    path('admin/quizzes/<int:quiz_id>/results/', AdminUserResultsView.as_view(), name='admin_quiz_results'), # Fetch all user results for a specific quiz.

]



