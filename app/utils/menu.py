from flask import current_app
from flask_login import current_user

def get_user_menu():
    """
    Returns a dictionary of menu items based on user's permissions.
    Each menu item contains:
    - title: Display name
    - icon: Font Awesome icon class
    - url: Route URL
    - permission: Required permission to view
    - children: Submenu items
    """
    print("DEBUG: Generating user menu")
    print(f"DEBUG: Current user: {current_user.email}")
    print(f"DEBUG: Is admin? {current_user.is_admin}")
    print(f"DEBUG: Role: {current_user.role.name if current_user.role else None}")
    
    menu_items = {
        'main': {
            'title': 'Main',
            'menu_items': [
                {
                    'title': 'Dashboard',
                    'icon': 'fas fa-tachometer-alt',
                    'url': 'main.dashboard',
                    'permission': None  # Always visible
                },
                {
                    'title': 'Contacts',
                    'icon': 'fas fa-address-book',
                    'url': 'contacts.index',
                    'permission': 'contact_view'
                },
                {
                    'title': 'Interactions',
                    'icon': 'fas fa-comments',
                    'url': 'interactions.index',
                    'permission': 'interaction_view'
                },
                {
                    'title': 'Organizations',
                    'icon': 'fas fa-building',
                    'url': 'organizations.index',
                    'permission': 'org_view'
                }
            ]
        },
        'user': {
            'title': 'User',
            'menu_items': [
                {
                    'title': 'Profile',
                    'icon': 'fas fa-user',
                    'url': 'admin.profile',
                    'permission': None  # Always visible
                },
                {
                    'title': 'Account Settings',
                    'icon': 'fas fa-user-cog',
                    'url': 'admin.update_account_settings',
                    'permission': None  # Always visible
                }
            ]
        },
        'admin': {
            'title': 'Administration',
            'menu_items': [
                {
                    'title': 'Users',
                    'icon': 'fas fa-users',
                    'url': 'admin.users',
                    'permission': 'user_view'
                },
                {
                    'title': 'Roles',
                    'icon': 'fas fa-user-shield',
                    'url': 'admin.roles',
                    'permission': 'role_view'
                },
                {
                    'title': 'Permissions',
                    'icon': 'fas fa-key',
                    'url': 'admin.permissions',
                    'permission': 'role_view'
                }
            ]
        }
    }
    
    # Filter menu items based on user permissions
    filtered_menu = {}
    for section, section_data in menu_items.items():
        filtered_items = []
        for item in section_data['menu_items']:
            print(f"DEBUG: Checking permission for {item['title']}: {item['permission']}")
            if item['permission'] is None or current_user.has_permission(item['permission']):
                print(f"DEBUG: Adding menu item: {item['title']}")
                filtered_items.append(item)
        
        if filtered_items:  # Only include sections that have visible items
            filtered_menu[section] = {
                'title': section_data['title'],
                'menu_items': filtered_items
            }
    
    print(f"DEBUG: Final menu sections: {list(filtered_menu.keys())}")
    return filtered_menu 