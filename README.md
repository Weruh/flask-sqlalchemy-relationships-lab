# Lab: Flask SQLAlchemy Relationships

## Scenario

You have just been hired as a junior backend engineer at a 
growing event management company called EventWise. Their 
current backend team built the database tables, but they 
haven't fully set up relationships between models. They need 
your help to define relationships between entities, populate 
the database, and expose the relational data through API 
endpoints.

In this lab, you’ll practice setting up one-to-one, one-to-many, 
and many-to-many relationships inside a Flask-SQLAlchemy app — 
and verify the relationships work by querying related records 
in different ways.

You'll follow the problem-solving steps you’ve learned:

* Define the problem clearly.
* Determine the design of models and relationships.
* Develop and test models and endpoints.
* Refine your code to ensure proper cascading and querying behaviors.


## Tools & Resources

- [GitHub Repo](https://github.com/learn-co-curriculum/flask-sqlalchemy-relationships-lab)
- [SQLAlchemy ORM Documentation: SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [Flask-SQLAlchemy Documentation: Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)

## Set Up

Fork and clone the lab repository.

Run the following commands:

```bash
$ pipenv install
$ pipenv shell
```

Navigate into the server/ directory and set environment variables:

```bash
$ cd server
$ export FLASK_APP=app.py
$ export FLASK_RUN_PORT=5555
```

You will find:
* `models.py` – already created but empty.
* `seed.py` – contains starter seed data (you will run this later after models are built).
* `testing/` – directory with test suites for models and endpoints to check your work.
* `app.py` – Flask app setup ready for you to add endpoints.

## Instructions

### Task 1: Define the Problem

You have been provided with the following Entity-Relationship Diagram (ERD):

![Entity-Relationship Diagram](/assets/erd.png)

* Event `has many` Sessions
* Session `belongs to` Event
* Speaker `has one` Bio
* Bio `belongs to` Speaker
* Speaker `has many` Sessions `through` session_speakers
* Session `has many` Speakers `through` session_speakers

Summary of Relationships:
* One-to-Many: Event ➡ Sessions
* One-to-One: Speaker ➡ Bio
* Many-to-Many: Session ↔ Speaker (through session_speakers association table)

You need to design and implement these relationships using Flask-SQLAlchemy models.

### Task 2: Determine the Design

Model Requirements:

| Model           | Attributes                                                             |
|-----------------|-------------------------------------------------------------------------|
| Event           | id (PK), name (String), location (String)                               |
| Session         | id (PK), title (String), start_time (DateTime), event_id (FK to Event)   |
| Speaker         | id (PK), name (String)                                                  |
| Bio             | id (PK), bio_text (String), speaker_id (FK to Speaker)                  |

Relationships:
* Event: sessions relationship
* Session: event relationship; speakers relationship (many-to-many)
* Speaker: bio relationship; sessions relationship (many-to-many)

Cascading:
* If an `Event` is deleted, its `Sessions` should also be deleted.
* If a `Speaker` is deleted, their `Bio` should be deleted.

### Task 3: Develop, Test, and Refine the Code

#### Step 1: Define Models and Relationships

Update models.py to:
* Define the association table.
* Set up the correct ForeignKey, relationship, and back_populates where needed.

__repr__ methods are included for each model that return readable summaries for each instance.

#### Step 2: Create Database and Tables

The initial migration is included. Apply it with:

```bash
$ flask db upgrade head
```

#### Step 3: Seed the Database

Run the seed file:

```bash
$ python seed.py
```

Confirm in the database (or use the Flask shell) that seed data is correctly inserted.

Run the test suite. You should be passing all models tests.

#### Step 4:  Check Relationships by Querying Relationship Data

Use the Flask shell to confirm relationships work:
* Fetch all Sessions for a given Event.
* Fetch the Bio for a given Speaker.
* Fetch all Speakers for a Session.

Example commands:

```bash
Event.query.first()

Speaker.query.first()

Session.query.first()
```

#### Step 5: Add Flask Endpoints

In app.py, build the following:

###### Event Endpoints:
* GET `/events`: Returns a list of all events. 
    * Events should be formatted as a dictionary with id, name, and location.
    * Include a `200` status.
* GET `/events/<int:id>/sessions`: Returns all sessions as a list for a given event.
    * Sessions should be formatted as a dictionary with id, title, and start_time (use `start_time.isoformat()`).
    * Include a `200` status if event exists.
    * If the event does not exist, return a message formatted as a dict `{"error": "Event not found"}` with status 404.

##### Speaker Endpoints
* GET `/speakers`: Returns a list of all speakers.
    * Speakers should be formatted as a dictionary with id and name.
    * Include a status of 200.
* GET `/speakers/<int:id>`: Return a speaker with their bio.
    * Speaker should be formatted as a dict with id, name, and bio_text.
    * If the speaker doesn't have a bio, bio_text should be assigned to `"No bio available"`.
    * Include a `200` status if speaker exists.
    * If the speaker does not exist, return a message formatted as a dict `{"error": "Speaker not found"}` with status 404.

##### Session Endpoints
* GET `/sessions/<int:id>/speakers`: Returns a list of `Speakers` for a `Session`.
    * Speakers should be formatted as a dictionary with id, name, and bio_text.
    * If the speaker doesn't have a bio, bio_text should be assigned to `"No bio available"`.
    * Include a `200` status if session exists.
    * If the session does not exist, return a message formatted as a dict `{"error": "Session not found"}` with status 404.

All responses should be JSON!

#### Step 6: Verify and Test your Code

Open your flask app and check the endpoints.

```bash
flask run
```

Run the test suite to verify all 4 suites are passing.

```bash
pytest
```

All tests should now be passing.

#### Step 7: Commit and Push Git History

Once all tests are passing, push your final code to GitHub.

If you used a feature branch, remember to merge your final code to main.

### Task 4: Document and Maintain

Best Practice documentation steps:
* Add comments to the code to explain purpose and logic, clarifying intent and functionality of your code to other developers.
* Update README text to reflect the functionality of the application following https://makeareadme.com. 
  * Add screenshot of completed work included in Markdown in README.
* Delete any stale branches on GitHub
* Remove unnecessary/commented out code
* If needed, update git ignore to remove sensitive data

## Summary

In this lab, you modeled and built one-to-one, one-to-many, and 
many-to-many relationships using Flask-SQLAlchemy. You seeded 
and queried relational data, added JSON-based endpoints, and 
solidified best practices for backend database modeling.

## Run the completed API

Use Python 3.12 and install the dependencies from the lock file:

```bash
pipenv sync
cd server
pipenv run flask --app app db upgrade
pipenv run python seed.py
pipenv run flask --app app run --port 5555
```

The seed command resets the sample records, so run it only when you want to replace local data. The SQLite database is stored in Flask's `server/instance/` directory and is ignored by Git.

| Method | Path | Response |
| --- | --- | --- |
| GET | `/events` | Events with `id`, `name`, and `location` |
| GET | `/events/<id>/sessions` | The event's sessions with ISO 8601 `start_time` |
| GET | `/speakers` | Speakers with `id` and `name` |
| GET | `/speakers/<id>` | Speaker details and `bio_text` |
| GET | `/sessions/<id>/speakers` | Speakers for the session, including `bio_text` |

Missing event, speaker, or session IDs return JSON with an `error` field and HTTP 404. Speakers without a bio return `"No bio available"`.

Run the test suite from the project root with `pipenv run pytest`.

![Seeded events API response](assets/events-api.png)

## Submission

Once all tests are passing and your finalized code is pushed 
to the main branch of your GitHub repo, submit your repo to
CodeGrade through Canvas.
