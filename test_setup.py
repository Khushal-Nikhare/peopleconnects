"""
Test script to verify PeopleConnects setup
Run this before starting the application
"""

import sys
import importlib.util

def check_module(module_name):
    """Check if a Python module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def check_dependencies():
    """Check all required dependencies"""
    required = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'motor': 'Motor (MongoDB async driver)',
        'pydantic': 'Pydantic',
        'jinja2': 'Jinja2',
        'passlib': 'Passlib',
        'jose': 'Python-JOSE',
        'PIL': 'Pillow',
        'email_validator': 'Email Validator'
    }
    
    print("=" * 50)
    print("CHECKING PYTHON DEPENDENCIES")
    print("=" * 50)
    
    all_ok = True
    for module, name in required.items():
        if check_module(module):
            print(f"✅ {name:<30} INSTALLED")
        else:
            print(f"❌ {name:<30} MISSING")
            all_ok = False
    
    print("\n")
    return all_ok

def check_directories():
    """Check if required directories exist"""
    import os
    from pathlib import Path
    
    print("=" * 50)
    print("CHECKING DIRECTORY STRUCTURE")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    required_dirs = [
        base_dir / "backend",
        base_dir / "templates",
        base_dir / "static",
        base_dir / "static" / "uploads",
        base_dir / "static" / "uploads" / "profiles",
        base_dir / "static" / "uploads" / "posts"
    ]
    
    all_ok = True
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ {str(directory.relative_to(base_dir)):<30} EXISTS")
        else:
            print(f"❌ {str(directory.relative_to(base_dir)):<30} MISSING")
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"   ⚙️  Created directory")
            except Exception as e:
                print(f"   ⚠️  Error creating: {e}")
                all_ok = False
    
    print("\n")
    return all_ok

def check_mongodb():
    """Check MongoDB connection"""
    print("=" * 50)
    print("CHECKING MONGODB CONNECTION")
    print("=" * 50)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        
        print(f"✅ MongoDB connection successful")
        print(f"   Server: localhost:27017")
        
        # Check if database exists
        db_list = client.list_database_names()
        if "peopleconnects" in db_list:
            db = client.peopleconnects
            users_count = db.users.count_documents({})
            posts_count = db.posts.count_documents({})
            print(f"   Database: peopleconnects (exists)")
            print(f"   Users: {users_count}")
            print(f"   Posts: {posts_count}")
        else:
            print(f"   Database: peopleconnects (will be created on first run)")
        
        client.close()
        print("\n")
        return True
        
    except ServerSelectionTimeoutError:
        print(f"❌ MongoDB connection failed")
        print(f"   Error: Cannot connect to localhost:27017")
        print(f"   Please ensure MongoDB is running")
        print("\n")
        return False
    except Exception as e:
        print(f"❌ MongoDB check failed")
        print(f"   Error: {e}")
        print("\n")
        return False

def check_files():
    """Check if required files exist"""
    import os
    from pathlib import Path
    
    print("=" * 50)
    print("CHECKING REQUIRED FILES")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    required_files = {
        'backend/main.py': 'Main application',
        'backend/database.py': 'Database configuration',
        'backend/models.py': 'Data models',
        'backend/auth.py': 'Authentication',
        'backend/image_utils.py': 'Image utilities',
        'requirements.txt': 'Dependencies list',
        'start.bat': 'Startup script'
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path:<30} EXISTS")
        else:
            print(f"❌ {file_path:<30} MISSING")
            all_ok = False
    
    print("\n")
    return all_ok

def main():
    """Run all checks"""
    print("\n")
    print("🔍 PeopleConnects Setup Verification")
    print("=" * 50)
    print("\n")
    
    results = {
        'Files': check_files(),
        'Directories': check_directories(),
        'Dependencies': check_dependencies(),
        'MongoDB': check_mongodb()
    }
    
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for check, status in results.items():
        status_symbol = "✅" if status else "❌"
        print(f"{status_symbol} {check:<20} {'OK' if status else 'FAILED'}")
    
    print("\n")
    
    if all(results.values()):
        print("🎉 All checks passed! You're ready to run PeopleConnects.")
        print("\nTo start the application:")
        print("  1. Double-click start.bat")
        print("  2. Or run: cd backend && python -m uvicorn main:app --reload")
        print("  3. Open: http://localhost:8000")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        
        if not results['MongoDB']:
            print("\n📌 MongoDB Tips:")
            print("  - Windows: Run 'net start MongoDB' as administrator")
            print("  - Linux: Run 'sudo systemctl start mongod'")
            print("  - Mac: Run 'brew services start mongodb-community'")
        
        if not results['Dependencies']:
            print("\n📌 Dependency Tips:")
            print("  - Run: pip install -r requirements.txt")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
