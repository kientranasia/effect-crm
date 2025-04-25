from app import create_app, db
from app.models import Role, User

app = create_app()
with app.app_context():
    admin_roles = Role.query.filter(Role.name.ilike('admin')).all()
    print("Admin roles found:")
    for r in admin_roles:
        print(f"ID: {r.id}, Name: {r.name}, Description: {r.description}")

    # Ask user which ID to keep
    keep_id = int(input("Enter the ID of the admin role you want to keep: "))
    keep_role = Role.query.get(keep_id)
    delete_roles = [r for r in admin_roles if r.id != keep_id]

    for role in delete_roles:
        users = User.query.filter_by(role_id=role.id).all()
        for user in users:
            print(f"Reassigning user {user.email} from role {role.name} to {keep_role.name}")
            user.role_id = keep_role.id

    for role in delete_roles:
        print(f"Deleting role: {role.name} (ID: {role.id})")
        db.session.delete(role)

    db.session.commit()
    print("Cleanup complete.") 