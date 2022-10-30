from database import Database

def main(db):
    rel = {"tacos": 33, "networking":55}
    crawled = db.build_crawled_url("testurl", rel)
    db.add(crawled)
    print(db)

def cleanup(db):
    db.cleanup()

if __name__ == "__main__":
    # Actual script execution goes in here
    # Database uses input_file for output file when output_file doesn't
    # exist yet.
    db = Database(input_file="test_database.msgpack") # test_*.msgpack is in .gitignore
    try:
        main(db)
    finally:
        # Ensure we always save our state before closing the program.
        cleanup(db)