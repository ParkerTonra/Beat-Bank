from src.models import Track, Version
from src.database import SessionLocal

def initialize_versions():
    with SessionLocal() as session:
        # Retrieve all tracks
        tracks = session.query(Track).all()

        for track in tracks:
            # Create a new version for each track based on its details
            new_version = Version(
                track_id=track.id,
                title=track.title,
                length=track.length,
                key=track.key,
                date_created=track.date_created,
                date_added=track.date_added,
                notes=track.notes,
                path_to_file=track.file_path,
                path_to_ableton_project=track.path_to_ableton_project,
                original_artist=track.artist
                # Include other fields as needed
            )

            # Add the new version to the session
            session.add(new_version)
            session.flush()  # This will populate new_version.id

            # Update the track's current version
            track.current_version_id = new_version.id

        # Commit the changes to the database
        session.commit()

if __name__ == "__main__":
    initialize_versions()