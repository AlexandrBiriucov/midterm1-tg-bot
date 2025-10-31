import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.exercise import Base, Exercise
from src.utils.seed_exercises import seed_exercises, INITIAL_EXERCISES

@pytest.fixture
def test_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_seed_exercises(test_session):
    seed_exercises(test_session)
    exercises = test_session.query(Exercise).all()
    assert len(exercises) == len(INITIAL_EXERCISES)
    assert exercises[0].name == "Bench Press"
