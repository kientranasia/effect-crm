import os
import re

def update_imports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace 'from app import db' with 'from app.extensions import db'
    content = re.sub(r'from app import db', 'from app.extensions import db', content)
    
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    models_dir = 'app/models'
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            file_path = os.path.join(models_dir, filename)
            update_imports(file_path)
            print(f'Updated {filename}')

if __name__ == '__main__':
    main() 