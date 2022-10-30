from database import Database

def main(db):
    pass

def cleanup(db):
    db.cleanup()

if __name__ == "__main__":
    # Actual script execution goes in here
    db = Database()
    try:
        main(db)
    finally:
        # Ensure we always save our state before closing the program.
        cleanup(db)