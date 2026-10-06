def user_role_context(request):
    if request.user.is_authenticated:
        return {
            'is_clipper': request.user.role == 'clipper',
            'is_brand': request.user.role == 'brand',
            'is_admin': request.user.is_staff or request.user.role == 'admin',
            'user_role': request.user.role,
            'wallet_balance': request.user.wallet_balance,
        }
    return {
        'is_clipper': False,
        'is_brand': False,
        'is_admin': False,
        'user_role': None,
        'wallet_balance': 0.00,
    }
