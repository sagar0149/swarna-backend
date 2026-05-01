from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. We define the URL for our database. 
# "sqlite:///./" means "create a file in this exact folder"
# We will name the file "swarna_lakshmi.db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./swarna_lakshmi.db"

# 2. The 'engine' is the core tool that actually connects to the file.
# (The 'check_same_thread' part is just a special requirement for SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. A 'Session' is like a single conversation with the database.
# We create a factory here to generate these conversations whenever we need them.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 'Base' is the master blueprint. 
# All of our database tables (like 'Products' or 'Users') will use this Base.
Base = declarative_base()
