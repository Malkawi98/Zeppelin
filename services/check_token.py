import jwt


def get_token(request):
    token = request.cookies.get('fastapiusersauth')
    print(token)
    # token = request
    return validate_token(token)


def validate_token(token):
    try:
        decode_token = jwt.decode(token, 'SECRET', algorithms="HS256",
                                  audience='fastapi-users:auth')
        return {'valid': True, 'user_id': decode_token['user_id']}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'message': 'expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'message': 'invalid token'}
    except KeyError:
        return {'valid': False, 'message': 'Missing JWT key'}

# jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUI1NiJ9.eyJ1c2VyX2lkIjoiMWRlMTMxOGUtYzEwZi00OGE1LThjNzAtZWJiZmJlZDA0NDRhIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjIzOTQ2ODAzfQ.gYV9MxliMFf5Tjvqdh2jZmQ1j_TexjFDhMr8NHs9Ihs'
# print(get_token(jwt_token).get('message'))
