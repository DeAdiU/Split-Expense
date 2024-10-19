from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from .serializers import UserSerializer, RepresentativeSerializer, ExpenseSerializer
from .models import User, Expense, ExpenseSplit
import datetime
import jwt  
from django.conf import settings
from rest_framework.decorators import api_view

# Create your views here.

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            return Response({'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            serializer = UserSerializer(user)
            if user.check_password(password):
                token = generate_jwt_token(user)
                return Response({'token': token, 'user':serializer.data}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_user_from_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        serializer = UserSerializer(user)
        return serializer.data
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Signature expired'}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.DecodeError:
        return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_jwt_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

@api_view(['GET'])
def user_expenses(request):
    user = get_user_from_token(request)

    if user is None:  # Check if the user is None, indicating an error occurred
        return Response({'error': 'Invalid token or user not found'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = RepresentativeSerializer(user) 
    return Response({
        'user': serializer.data,
    }, status=status.HTTP_200_OK)


class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class UserExpensesView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        return Expense.objects.filter(user=user)  