from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Quiz, Question, Result
from .serializers import *

from django.contrib.auth.models import User



class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         # Authenticate using email and password
#         user = authenticate(request, email=email, password=password)

#         if user:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#             })
#         else:
#             return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Add token to the blacklist
            return Response({"message": "Successfully logged out."}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token."}, status=400)


class QuizListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)
    

class QuestionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            questions = quiz.questions.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=404)


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = Quiz.objects.filter(id=quiz_id).first()
        if not quiz:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        answers = request.data.get('answers', {})
        if not isinstance(answers, dict):
            return Response({"error": "Invalid answers format"}, status=status.HTTP_400_BAD_REQUEST)

        questions = Question.objects.filter(quiz=quiz)
        score, feedback = self.calculate_feedback(answers, questions)

        result = Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            feedback=feedback,
        )

        return Response({
            "score": score,
            "total_questions": questions.count(),
            "feedback": feedback
        })



    def calculate_feedback(self, answers, questions):
        feedback = []
        score = 0
        for question in questions:
            user_answer = answers.get(str(question.id))
            correct = user_answer == question.correct_option
            feedback.append({
                "question": question.text,
                "your_answer": user_answer,
                "correct_answer": question.correct_option,
                "correct": correct
            })
            if correct:
                score += 1
        return score, feedback


class UserResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        results = Result.objects.filter(user=request.user)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
    


class AdminQuizView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            serializer = QuizSerializer(quiz, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.delete()
            return Response({"message": "Quiz deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        


class AdminQuestionView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            questions = quiz.questions.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    # def post(self, request, quiz_id):
    #     try:
    #         Quiz.objects.get(id=quiz_id)
    #         serializer = QuestionSerializer(data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     except Quiz.DoesNotExist:
    #         return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
    def post(self, request, quiz_id):
        try:
            # Check if the quiz exists
            quiz = Quiz.objects.get(id=quiz_id)
            
            # Add the `quiz_id` to the request data
            data = request.data.copy()
            data['quiz_id'] = quiz.id  # Attach the quiz_id explicitly
            
            # Pass the modified data to the serializer
            serializer = QuestionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            serializer =  QuestionSerializer(question, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)


class AdminUserResultsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            results = Result.objects.filter(quiz=quiz)
            serializer =ResultSerializer(results, many=True)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
