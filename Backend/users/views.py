from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User
from .serializers import UserRegistrationSerializer, UserProfileSerializer, UserLoginSerializer

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """تسجيل مستخدم جديد"""
    try:
        with transaction.atomic():
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'تم إنشاء الحساب بنجاح',
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'حدث خطأ أثناء إنشاء الحساب'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """تسجيل الدخول"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'تم تسجيل الدخول بنجاح',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response({'error': 'بيانات الدخول غير صحيحة أو الحساب غير مفعل'}, 
                       status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """الحصول على وتحديث الملف الشخصي"""
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(request.user, data=request.data, 
                                         partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'تم تحديث الملف الشخصي بنجاح', 
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """تسجيل الخروج"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'تم تسجيل الخروج بنجاح'})
    except Exception as e:
        return Response({'error': 'فشل في تسجيل الخروج'}, 
                       status=status.HTTP_400_BAD_REQUEST)

class UserListAPIView(generics.ListAPIView):
    """قائمة المستخدمين (للمشرفين فقط)"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_fields = ['role', 'is_active', 'is_verified']